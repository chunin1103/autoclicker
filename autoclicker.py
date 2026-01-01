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
from datetime import datetime, timedelta
from typing import List, Dict
from zoneinfo import ZoneInfo
import requests
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from database import Database

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

    def __init__(self, config_path: str = 'config.json', db_path: str = 'autoclicker.db'):
        """Initialize the pinger with configuration"""
        self.config_path = config_path
        self.db_path = db_path
        self.config_lock = threading.Lock()

        # Initialize database
        self.db = Database(db_path)

        # Migrate data from config.json if database is empty
        self._migrate_from_json_if_needed()

        # Load configuration from database
        self.urls = self.db.get_all_urls()
        self.interval = self.db.get_setting('interval_seconds', 300)
        self.timeout = self.db.get_setting('timeout_seconds', 10)
        self.user_agent = self.db.get_setting('user_agent', 'AutoClicker/1.0')
        self.timezone = self.db.get_setting('timezone', 'Asia/Bangkok')

        # Track statistics (total_pings now stored in database)
        self.last_ping_time = None
        self.last_results = {}
        self.is_running = False
        self.timers = {}  # url_id -> Timer instance

        logger.info(f"Initialized pinger with {len(self.urls)} URLs from database")
        logger.info(f"Global ping interval: {self.interval} seconds")

    def _migrate_from_json_if_needed(self):
        """Migrate data from config.json to database if database is empty"""
        # Check if database has any URLs
        existing_urls = self.db.get_all_urls()

        if not existing_urls and os.path.exists(self.config_path):
            logger.info("Database is empty. Migrating data from config.json...")
            try:
                config = self.load_config(self.config_path)
                if config:
                    self.db.import_from_config(config)
                    logger.info("Migration from config.json completed successfully")

                    # Backup the config.json file
                    backup_path = f"{self.config_path}.backup"
                    import shutil
                    shutil.copy(self.config_path, backup_path)
                    logger.info(f"Created backup: {backup_path}")
            except Exception as e:
                logger.error(f"Error during migration: {e}")

    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file (used for migration only)"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return {}

    def save_config(self):
        """
        Export database to config.json as backup
        Note: Primary storage is now the database
        """
        with self.config_lock:
            try:
                config = self.db.export_to_config()
                with open(self.config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                logger.info("Configuration exported to JSON backup")
            except Exception as e:
                logger.error(f"Error exporting config: {e}")

    def reload_config(self):
        """Reload configuration from database and restart timers"""
        with self.config_lock:
            self.urls = self.db.get_all_urls()
            self.interval = self.db.get_setting('interval_seconds', 300)
            self.timeout = self.db.get_setting('timeout_seconds', 10)
            self.user_agent = self.db.get_setting('user_agent', 'AutoClicker/1.0')
            self.timezone = self.db.get_setting('timezone', 'Asia/Bangkok')
            logger.info(f"Configuration reloaded from database (timezone: {self.timezone})")

            # Restart all timers if pinger is running
            if self.is_running:
                self._restart_all_timers()

    def _is_in_active_hours(self, start_time: str, end_time: str) -> bool:
        """
        Check if current time is within active hours (in configured timezone)

        Args:
            start_time: Start time in HH:MM format (e.g., "09:00")
            end_time: End time in HH:MM format (e.g., "22:00")

        Returns:
            True if current time is within active hours, False otherwise
        """
        if not start_time or not end_time:
            # No time restrictions, always active
            return True

        try:
            # Get current time in configured timezone
            tz = ZoneInfo(self.timezone)
            now = datetime.now(tz)
            current_time = now.time()

            start = datetime.strptime(start_time, "%H:%M").time()
            end = datetime.strptime(end_time, "%H:%M").time()

            if start <= end:
                # Same day range (e.g., 09:00 to 22:00)
                return start <= current_time <= end
            else:
                # Crosses midnight (e.g., 22:00 to 06:00)
                return current_time >= start or current_time <= end
        except Exception as e:
            logger.error(f"Error checking active hours: {e}")
            return True  # Default to active if error occurs

    def _seconds_until_next_active_period(self, start_time: str) -> int:
        """
        Calculate seconds until the next active period starts (in configured timezone)

        Args:
            start_time: Start time in HH:MM format

        Returns:
            Number of seconds until next active period
        """
        if not start_time:
            return 0

        try:
            # Get current time in configured timezone
            tz = ZoneInfo(self.timezone)
            now = datetime.now(tz)
            start = datetime.strptime(start_time, "%H:%M").time()

            # Create timezone-aware datetime for next start
            next_start = datetime.combine(now.date(), start, tzinfo=tz)

            # If start time has passed today, schedule for tomorrow
            if next_start <= now:
                next_start = datetime.combine(now.date(), start, tzinfo=tz) + timedelta(days=1)

            seconds_until = (next_start - now).total_seconds()
            return int(seconds_until)
        except Exception as e:
            logger.error(f"Error calculating next active period: {e}")
            return 60  # Default to 1 minute if error occurs

    def _schedule_url_ping(self, url_obj: Dict):
        """
        Schedule a ping for a specific URL, respecting active hours

        Args:
            url_obj: URL object containing id, url, interval_seconds, start_time, end_time, etc.
        """
        url_id = url_obj['id']
        url = url_obj.get('url')
        interval = url_obj.get('interval_seconds') or self.interval
        start_time = url_obj.get('start_time')
        end_time = url_obj.get('end_time')

        def ping_and_reschedule():
            """Check active hours, ping if active, and reschedule"""
            # Check if URL is still enabled
            url_obj_current = self.db.get_url(url_id)
            if not url_obj_current or not url_obj_current.get('enabled', True):
                # URL was disabled or deleted, remove from timers
                if url_id in self.timers:
                    del self.timers[url_id]
                logger.info(f"URL {url_obj.get('name')} disabled or deleted, stopping timer")
                return

            # Update start_time and end_time from current URL object
            current_start_time = url_obj_current.get('start_time')
            current_end_time = url_obj_current.get('end_time')

            # Check if we're in active hours
            if self._is_in_active_hours(current_start_time, current_end_time):
                # We're in active hours, ping the URL
                logger.info(f"Pinging {url_obj_current.get('name')} (within active hours)")
                success = self.ping_url(url)

                # Update last results
                self.last_results[url] = success
                self.last_ping_time = datetime.now()

                # Increment ping counter
                self.db.increment_statistic('total_pings')

                # Reschedule based on interval
                self._schedule_url_ping(url_obj_current)
            else:
                # We're outside active hours, schedule check for next active period
                if current_start_time:
                    seconds_until = self._seconds_until_next_active_period(current_start_time)
                    logger.info(f"{url_obj_current.get('name')} outside active hours. Next check in {seconds_until} seconds")

                    # Schedule a check when active period starts
                    timer = threading.Timer(seconds_until, lambda: self._schedule_url_ping(url_obj_current))
                    timer.daemon = True
                    timer.start()
                    self.timers[url_id] = timer
                else:
                    # No start time, treat as always active and reschedule normally
                    self._schedule_url_ping(url_obj_current)

        # Cancel existing timer for this URL if it exists
        if url_id in self.timers:
            self.timers[url_id].cancel()

        # Check if we're in active hours before scheduling
        if self._is_in_active_hours(start_time, end_time):
            # We're in active hours, schedule the next ping
            timer = threading.Timer(interval, ping_and_reschedule)
            timer.daemon = True
            timer.start()
            self.timers[url_id] = timer
            logger.info(f"Scheduled {url_obj.get('name')} to ping in {interval} seconds (active hours: {start_time or 'always'} - {end_time or 'always'})")
        else:
            # We're outside active hours, schedule check for when active period starts
            if start_time:
                seconds_until = self._seconds_until_next_active_period(start_time)
                logger.info(f"{url_obj.get('name')} outside active hours ({start_time} - {end_time}). Next check in {seconds_until} seconds")

                timer = threading.Timer(seconds_until, ping_and_reschedule)
                timer.daemon = True
                timer.start()
                self.timers[url_id] = timer
            else:
                # No time restriction, schedule normally
                timer = threading.Timer(interval, ping_and_reschedule)
                timer.daemon = True
                timer.start()
                self.timers[url_id] = timer
                logger.info(f"Scheduled {url_obj.get('name')} to ping in {interval} seconds (24/7 active)")

    def _cancel_all_timers(self):
        """Cancel all active timers"""
        for timer in self.timers.values():
            timer.cancel()
        self.timers.clear()
        logger.info("Cancelled all timers")

    def _restart_all_timers(self):
        """Restart all timers based on current configuration"""
        # Cancel all existing timers
        self._cancel_all_timers()

        # Schedule enabled URLs
        enabled_urls = [u for u in self.urls if u.get('enabled', True)]
        for url_obj in enabled_urls:
            self._schedule_url_ping(url_obj)

        logger.info(f"Restarted timers for {len(enabled_urls)} enabled URLs")

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

        # Update statistics in database for persistence across workers
        self.last_ping_time = datetime.now()
        self.last_results = results
        total_pings = self.db.increment_statistic('total_pings')
        logger.info(f"Total ping cycles completed: {total_pings}")

        return results

    def run(self):
        """Run the pinger continuously with independent timers per URL"""
        logger.info("Starting autoclicker service...")

        self.is_running = True

        # Schedule all enabled URLs
        enabled_urls = [u for u in self.urls if u.get('enabled', True)]
        for url_obj in enabled_urls:
            interval = url_obj.get('interval_seconds') or self.interval
            logger.info(f"URL: {url_obj.get('name')} - Interval: {interval} seconds")
            self._schedule_url_ping(url_obj)

        logger.info(f"Started independent timers for {len(enabled_urls)} URLs")

        # Keep main thread alive
        try:
            while self.is_running:
                time.sleep(60)  # Sleep for a minute, just to keep thread alive
        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")
            self.is_running = False
            self._cancel_all_timers()
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.is_running = False
            self._cancel_all_timers()
            raise

    def get_status(self) -> Dict:
        """Get current status of the pinger"""
        return {
            'is_running': self.is_running,
            'urls_count': len(self.urls),
            'interval_seconds': self.interval,
            'last_ping_time': self.last_ping_time.isoformat() if self.last_ping_time else None,
            'total_pings': self.db.get_statistic('total_pings'),
            'last_results': self.last_results
        }


# Create Flask app
app = Flask(__name__)

# Global pinger instance
pinger = None


def initialize_pinger():
    """Initialize the pinger and start background thread"""
    global pinger
    if pinger is None:
        logger.info("Initializing pinger...")
        pinger = WebsitePinger()
        pinger_thread = threading.Thread(target=pinger.run, daemon=True)
        pinger_thread.start()
        logger.info("Pinger initialized and background thread started")


# Initialize pinger when module is imported (for WSGI servers like Gunicorn)
initialize_pinger()


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
        config = pinger.db.export_to_config()
        return jsonify(config)
    return jsonify({'error': 'Pinger not initialized'}), 500


@app.route('/api/urls', methods=['GET'])
def get_urls():
    """Get all URLs"""
    if pinger:
        urls = pinger.db.get_all_urls()
        return jsonify(urls)
    return jsonify({'error': 'Pinger not initialized'}), 500


@app.route('/api/urls', methods=['POST'])
def add_url():
    """Add a new URL"""
    if not pinger:
        return jsonify({'error': 'Pinger not initialized'}), 500

    data = request.json
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400

    # Add URL to database
    new_url = pinger.db.add_url(
        url=data['url'],
        name=data.get('name', 'New URL'),
        enabled=data.get('enabled', True),
        interval_seconds=data.get('interval_seconds'),
        start_time=data.get('start_time'),
        end_time=data.get('end_time')
    )

    # Reload configuration (this will restart timers)
    pinger.reload_config()

    # Export to JSON backup
    pinger.save_config()

    logger.info(f"Added new URL: {new_url['name']} ({new_url['url']}) - Interval: {new_url.get('interval_seconds', 'global default')}, Active: {new_url.get('start_time', 'always')} - {new_url.get('end_time', 'always')}")

    return jsonify(new_url), 201


@app.route('/api/urls/<url_id>', methods=['PUT'])
def update_url(url_id):
    """Update an existing URL"""
    if not pinger:
        return jsonify({'error': 'Pinger not initialized'}), 500

    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Update in database
    success = pinger.db.update_url(url_id, **data)
    if not success:
        return jsonify({'error': 'URL not found'}), 404

    # Get updated URL
    url_obj = pinger.db.get_url(url_id)

    # Reload configuration
    pinger.reload_config()

    # Export to JSON backup
    pinger.save_config()

    if 'enabled' in data:
        logger.info(f"URL {url_obj['name']} {'enabled' if data['enabled'] else 'disabled'}")

    return jsonify(url_obj)


@app.route('/api/urls/<url_id>', methods=['DELETE'])
def delete_url(url_id):
    """Delete a URL"""
    if not pinger:
        return jsonify({'error': 'Pinger not initialized'}), 500

    # Get URL info before deleting
    url_obj = pinger.db.get_url(url_id)
    if not url_obj:
        return jsonify({'error': 'URL not found'}), 404

    # Delete from database
    pinger.db.delete_url(url_id)

    # Reload configuration
    pinger.reload_config()

    # Export to JSON backup
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

    # Update settings in database
    if 'interval_seconds' in data:
        pinger.db.set_setting('interval_seconds', int(data['interval_seconds']))
    if 'timeout_seconds' in data:
        pinger.db.set_setting('timeout_seconds', int(data['timeout_seconds']))
    if 'user_agent' in data:
        pinger.db.set_setting('user_agent', data['user_agent'])
    if 'timezone' in data:
        pinger.db.set_setting('timezone', data['timezone'])

    # Reload configuration
    pinger.reload_config()

    # Export to JSON backup
    pinger.save_config()

    logger.info("Settings updated in database")

    return jsonify({'message': 'Settings updated successfully'})


def main():
    """Main entry point"""
    # Pinger is already initialized at module level
    # This is just for running locally with Flask's development server

    logger.info("Starting web server...")

    # Get port from environment variable (Koyeb provides PORT)
    port = int(os.environ.get('PORT', 8000))

    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    main()
