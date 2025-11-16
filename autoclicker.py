#!/usr/bin/env python3
"""
Autoclicker/Website Pinger
Automatically pings configured websites at regular intervals
"""

import json
import logging
import time
from datetime import datetime
from typing import List, Dict
import requests
from pathlib import Path

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

        return results

    def run(self):
        """Run the pinger continuously"""
        logger.info("Starting autoclicker service...")
        logger.info(f"Will ping {len(self.urls)} URLs every {self.interval} seconds")

        try:
            while True:
                self.ping_all()
                logger.info(f"Waiting {self.interval} seconds until next cycle...")
                time.sleep(self.interval)
        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise


def main():
    """Main entry point"""
    pinger = WebsitePinger()
    pinger.run()


if __name__ == '__main__':
    main()
