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
from datetime import datetime
from typing import List, Dict
import requests
from pathlib import Path
from flask import Flask, jsonify

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
        self.config = self.load_config(config_path)
        self.urls = self.config.get('urls', [])
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
        Ping all configured URLs

        Returns:
            Dictionary mapping URLs to their success status
        """
        results = {}
        logger.info(f"Starting ping cycle at {datetime.now()}")

        for url in self.urls:
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
            '/health': 'Health check endpoint',
            '/status': 'Detailed status information',
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
