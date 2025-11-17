#!/usr/bin/env python3
"""
Autoclicker/Website Pinger
Automatically pings configured websites at regular intervals
"""

import json
import logging
import time
import os
import threading
import uuid
from datetime import datetime
from typing import List, Dict
import requests
from pathlib import Path
from flask import Flask, jsonify, render_template, request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autoclicker.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class WebsitePinger:
    """Handles pinging of configured websites"""

    def __init__(self, config_path: str = 'config.json'):
        """Initialize the pinger with configuration"""
        self.config_path = config_path
        self.config_lock = threading.Lock()
        self.config = self.load_config(config_path)
        self.urls = self.config.get('urls', [])

        # Normalize URLs to new format if needed
        self._normalize_urls()

        self.interval = self.config.get('interval_seconds', 300)
        self.timeout = self.config.get('timeout_seconds', 10)
        self.user_agent = self.config.get('user_agent', 'AutoClicker/1.0')

        # Track statistics
        self.last_ping_time = None
        self.last_results = {}
        self.total_pings = 0
        self.is_running = False

        logger.info(f"Initialized pinger with {len(self.urls)} URLs")
        logger.info(f"Ping interval: {self.interval} seconds")

    def _normalize_urls(self):
        """Convert old URL format (strings) to new format (objects)"""
        normalized = []
        for i, url in enumerate(self.urls):
            if isinstance(url, str):
                # Old format - convert to new format
                normalized.append({
                    'id': str(i + 1),
                    'url': url,
                    'enabled': True,
                    'name': f'URL {i + 1}'
                })
            else:
                # Already in new format
                if 'id' not in url:
                    url['id'] = str(uuid.uuid4())
                if 'enabled' not in url:
                    url['enabled'] = True
                if 'name' not in url:
                    url['name'] = f'URL {i + 1}'
                normalized.append(url)

        if normalized != self.urls:
            self.urls = normalized
            self.config['urls'] = normalized
            self.save_config()

    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return {}

    def save_config(self):
        """Save configuration to JSON file"""
        with self.config_lock:
            try:
                with open(self.config_path, 'w') as f:
                    json.dump(self.config, f, indent=2)
                logger.info("Configuration saved successfully")
            except Exception as e:
                logger.error(f"Error saving config: {e}")

    def reload_config(self):
        """Reload configuration from file"""
        with self.config_lock:
            self.config = self.load_config(self.config_path)
            self.urls = self.config.get('urls', [])
            self.interval = self.config.get('interval_seconds', 300)
            self.timeout = self.config.get('timeout_seconds', 10)
            logger.info("Configuration reloaded")

    def ping_url(self, url: str) -> bool:
        """
        Ping a single URL and return success status

        Args:
            url: The URL to ping

        Returns:
            True if successful (status code 2xx), False otherwise
        """
        try:
            headers = {'User-Agent': self.user_agent}
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True
            )

            success = 200 <= response.status_code < 300

            if success:
                logger.info(f"✓ {url} - Status: {response.status_code}")
            else:
                logger.warning(f"✗ {url} - Status: {response.status_code}")

            return success

        except requests.exceptions.Timeout:
            logger.error(f"✗ {url} - Timeout after {self.timeout}s")
            return False
        except requests.exceptions.ConnectionError:
            logger.error(f"✗ {url} - Connection error")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ {url} - Error: {str(e)}")
            return False

    def ping_all(self) -> Dict[str, bool]:
        """
        Ping all enabled URLs

        Returns:
            Dictionary mapping URLs to their success status
        """
        results = {}

        # Reload config to pick up any changes
        self.reload_config()

        # Filter only enabled URLs
        enabled_urls = [u for u in self.urls if u.get('enabled', True)]

        logger.info(f"Starting ping cycle at {datetime.now()}")
        logger.info(f"Pinging {len(enabled_urls)} enabled URLs out of {len(self.urls)} total")

        for url_obj in enabled_urls:
            url = url_obj.get('url') if isinstance(url_obj, dict) else url_obj
            results[url] = self.ping_url(url)
            time.sleep(1)  # Small delay between requests

        successful = sum(1 for v in results.values() if v)
        logger.info(f"Ping cycle complete: {successful}/{len(results)} successful")

        # Update statistics
        self.last_ping_time = datetime.now()
        self.last_results = results
        self.total_pings += 1

        return results

    def run(self):
        """Run the pinger continuously"""
        logger.info("Starting autoclicker service...")
        logger.info(f"Will ping {len(self.urls)} URLs every {self.interval} seconds")

        self.is_running = True

        try:
            while self.is_running:
                self.ping_all()
                logger.info(f"Waiting {self.interval} seconds until next cycle...")
                time.sleep(self.interval)
        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")
            self.is_running = False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.is_running = False
            raise

    def get_status(self) -> Dict:
        """Get current status of the pinger"""
        return {
            'is_running': self.is_running,
            'urls_count': len(self.urls),
            'interval_seconds': self.interval,
            'last_ping_time': self.last_ping_time.isoformat() if self.last_ping_time else None,
            'total_pings': self.total_pings,
            'last_results': self.last_results
        }


# Create Flask app
app = Flask(__name__)

# Global pinger instance
pinger = None


@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'service': 'Autoclicker Website Pinger',
        'status': 'running',
        'endpoints': {
            '/admin': 'Admin interface for URL management',
            '/health': 'Health check endpoint',
            '/status': 'Detailed status information',
            '/api/config': 'Get configuration',
            '/api/urls': 'Manage URLs (GET, POST)',
            '/': 'This endpoint'
        }
    })


@app.route('/health')
def health():
    """Health check endpoint for Koyeb"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/status')
def status():
    """Detailed status endpoint"""
    if pinger:
        return jsonify(pinger.get_status())
    return jsonify({'error': 'Pinger not initialized'}), 500


@app.route('/admin')
def admin():
    """Admin interface for managing URLs"""
    return render_template('admin.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    if pinger:
        return jsonify(pinger.config)
    return jsonify({'error': 'Pinger not initialized'}), 500


@app.route('/api/urls', methods=['GET'])
def get_urls():
    """Get all URLs"""
    if pinger:
        return jsonify(pinger.urls)
    return jsonify({'error': 'Pinger not initialized'}), 500


@app.route('/api/urls', methods=['POST'])
def add_url():
    """Add a new URL"""
    if not pinger:
        return jsonify({'error': 'Pinger not initialized'}), 500

    data = request.json
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400

    # Create new URL object
    new_url = {
        'id': str(uuid.uuid4()),
        'url': data['url'],
        'name': data.get('name', 'New URL'),
        'enabled': data.get('enabled', True)
    }

    # Add to config
    pinger.urls.append(new_url)
    pinger.config['urls'] = pinger.urls
    pinger.save_config()

    logger.info(f"Added new URL: {new_url['name']} ({new_url['url']})")

    return jsonify(new_url), 201


@app.route('/api/urls/<url_id>', methods=['PUT'])
def update_url(url_id):
    """Update an existing URL"""
    if not pinger:
        return jsonify({'error': 'Pinger not initialized'}), 500

    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Find the URL
    url_obj = next((u for u in pinger.urls if u['id'] == url_id), None)
    if not url_obj:
        return jsonify({'error': 'URL not found'}), 404

    # Update fields
    if 'url' in data:
        url_obj['url'] = data['url']
    if 'name' in data:
        url_obj['name'] = data['name']
    if 'enabled' in data:
        url_obj['enabled'] = data['enabled']
        logger.info(f"URL {url_obj['name']} {'enabled' if data['enabled'] else 'disabled'}")

    pinger.config['urls'] = pinger.urls
    pinger.save_config()

    return jsonify(url_obj)


@app.route('/api/urls/<url_id>', methods=['DELETE'])
def delete_url(url_id):
    """Delete a URL"""
    if not pinger:
        return jsonify({'error': 'Pinger not initialized'}), 500

    # Find and remove the URL
    url_obj = next((u for u in pinger.urls if u['id'] == url_id), None)
    if not url_obj:
        return jsonify({'error': 'URL not found'}), 404

    pinger.urls = [u for u in pinger.urls if u['id'] != url_id]
    pinger.config['urls'] = pinger.urls
    pinger.save_config()

    logger.info(f"Deleted URL: {url_obj['name']} ({url_obj['url']})")

    return jsonify({'message': 'URL deleted successfully'})


@app.route('/api/settings', methods=['PUT'])
def update_settings():
    """Update settings"""
    if not pinger:
        return jsonify({'error': 'Pinger not initialized'}), 500

    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Update settings
    if 'interval_seconds' in data:
        pinger.config['interval_seconds'] = int(data['interval_seconds'])
    if 'timeout_seconds' in data:
        pinger.config['timeout_seconds'] = int(data['timeout_seconds'])
    if 'user_agent' in data:
        pinger.config['user_agent'] = data['user_agent']

    pinger.save_config()

    logger.info("Settings updated")

    return jsonify({'message': 'Settings updated successfully'})


def run_pinger():
    """Run the pinger in a background thread"""
    global pinger
    pinger = WebsitePinger()
    pinger.run()


def main():
    """Main entry point"""
    # Start pinger in background thread
    pinger_thread = threading.Thread(target=run_pinger, daemon=True)
    pinger_thread.start()

    logger.info("Starting web server...")

    # Get port from environment variable (Koyeb provides PORT)
    port = int(os.environ.get('PORT', 8000))

    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    main()
