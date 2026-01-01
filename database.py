#!/usr/bin/env python3
"""
Database module for persistent storage of website configurations
Uses SQLite for reliable, crash-resistant data persistence
"""

import sqlite3
import logging
import uuid
from typing import List, Dict, Optional
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)


class Database:
    """Handles all database operations for the website pinger"""

    def __init__(self, db_path: str = 'autoclicker.db'):
        """
        Initialize database connection and create tables if needed

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
        logger.info(f"Database initialized: {db_path}")

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _init_database(self):
        """Create database tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Create URLs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS urls (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    name TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    interval_seconds INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')

            # Create settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')

            # Create statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    key TEXT PRIMARY KEY,
                    value INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL
                )
            ''')

            # Create indices for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_urls_enabled
                ON urls(enabled)
            ''')

            conn.commit()
            logger.info("Database tables created/verified")

            # Run migrations
            self._run_migrations()

    def _run_migrations(self):
        """Run database migrations for schema updates"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Migration: Add interval_seconds column to urls table if it doesn't exist
            cursor.execute("PRAGMA table_info(urls)")
            columns = [row[1] for row in cursor.fetchall()]

            if 'interval_seconds' not in columns:
                logger.info("Running migration: Adding interval_seconds column to urls table")
                cursor.execute('ALTER TABLE urls ADD COLUMN interval_seconds INTEGER')
                conn.commit()
                logger.info("Migration completed: interval_seconds column added")

    # URL Management Methods

    def add_url(self, url: str, name: str, enabled: bool = True, interval_seconds: int = None) -> Dict:
        """
        Add a new URL to the database

        Args:
            url: The URL to ping
            name: Display name for the URL
            enabled: Whether the URL is enabled
            interval_seconds: Custom ping interval for this URL (None = use global default)

        Returns:
            Dictionary containing the created URL data
        """
        url_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO urls (id, url, name, enabled, interval_seconds, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (url_id, url, name, 1 if enabled else 0, interval_seconds, now, now))

        logger.info(f"Added URL to database: {name} ({url})")

        return {
            'id': url_id,
            'url': url,
            'name': name,
            'enabled': enabled,
            'interval_seconds': interval_seconds,
            'created_at': now,
            'updated_at': now
        }

    def get_url(self, url_id: str) -> Optional[Dict]:
        """
        Get a specific URL by ID

        Args:
            url_id: The URL ID

        Returns:
            Dictionary containing URL data or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM urls WHERE id = ?', (url_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_url_dict(row)
            return None

    def get_all_urls(self) -> List[Dict]:
        """
        Get all URLs from the database

        Returns:
            List of dictionaries containing URL data
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM urls ORDER BY created_at')
            rows = cursor.fetchall()

            return [self._row_to_url_dict(row) for row in rows]

    def get_enabled_urls(self) -> List[Dict]:
        """
        Get only enabled URLs

        Returns:
            List of dictionaries containing enabled URL data
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM urls WHERE enabled = 1 ORDER BY created_at')
            rows = cursor.fetchall()

            return [self._row_to_url_dict(row) for row in rows]

    def update_url(self, url_id: str, **kwargs) -> bool:
        """
        Update a URL's properties

        Args:
            url_id: The URL ID
            **kwargs: Fields to update (url, name, enabled, interval_seconds)

        Returns:
            True if updated, False if URL not found
        """
        allowed_fields = {'url', 'name', 'enabled', 'interval_seconds'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return False

        # Convert boolean to integer for SQLite
        if 'enabled' in updates:
            updates['enabled'] = 1 if updates['enabled'] else 0

        updates['updated_at'] = datetime.now().isoformat()

        set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
        values = list(updates.values()) + [url_id]

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE urls SET {set_clause} WHERE id = ?
            ''', values)

            if cursor.rowcount > 0:
                logger.info(f"Updated URL {url_id}")
                return True
            return False

    def delete_url(self, url_id: str) -> bool:
        """
        Delete a URL from the database

        Args:
            url_id: The URL ID

        Returns:
            True if deleted, False if URL not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM urls WHERE id = ?', (url_id,))

            if cursor.rowcount > 0:
                logger.info(f"Deleted URL {url_id}")
                return True
            return False

    def delete_all_urls(self):
        """Delete all URLs from the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM urls')
            logger.info("Deleted all URLs from database")

    # Settings Management Methods

    def get_setting(self, key: str, default: any = None) -> any:
        """
        Get a setting value

        Args:
            key: Setting key
            default: Default value if setting not found

        Returns:
            Setting value or default
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()

            if row:
                return self._parse_setting_value(row['value'])
            return default

    def set_setting(self, key: str, value: any):
        """
        Set a setting value

        Args:
            key: Setting key
            value: Setting value
        """
        now = datetime.now().isoformat()
        value_str = str(value)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, value_str, now))

        logger.info(f"Setting updated: {key} = {value}")

    def get_all_settings(self) -> Dict:
        """
        Get all settings

        Returns:
            Dictionary of all settings
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT key, value FROM settings')
            rows = cursor.fetchall()

            return {row['key']: self._parse_setting_value(row['value']) for row in rows}

    # Helper Methods

    def _row_to_url_dict(self, row) -> Dict:
        """Convert SQLite row to URL dictionary"""
        return {
            'id': row['id'],
            'url': row['url'],
            'name': row['name'],
            'enabled': bool(row['enabled']),
            'interval_seconds': row['interval_seconds'] if row['interval_seconds'] is not None else None,
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }

    def _parse_setting_value(self, value: str) -> any:
        """Parse setting value from string"""
        # Try to parse as integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try to parse as float
        try:
            return float(value)
        except ValueError:
            pass

        # Try to parse as boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'

        # Return as string
        return value

    # Statistics Management Methods

    def get_statistic(self, key: str) -> int:
        """
        Get a statistic value

        Args:
            key: Statistic key (e.g., 'total_pings')

        Returns:
            Statistic value (defaults to 0 if not found)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM statistics WHERE key = ?', (key,))
            row = cursor.fetchone()

            if row:
                return int(row['value'])
            return 0

    def increment_statistic(self, key: str, amount: int = 1) -> int:
        """
        Increment a statistic value atomically

        Args:
            key: Statistic key
            amount: Amount to increment by (default: 1)

        Returns:
            New value after increment
        """
        now = datetime.now().isoformat()

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get current value
            cursor.execute('SELECT value FROM statistics WHERE key = ?', (key,))
            row = cursor.fetchone()

            if row:
                new_value = int(row['value']) + amount
                cursor.execute('''
                    UPDATE statistics SET value = ?, updated_at = ? WHERE key = ?
                ''', (new_value, now, key))
            else:
                new_value = amount
                cursor.execute('''
                    INSERT INTO statistics (key, value, updated_at)
                    VALUES (?, ?, ?)
                ''', (key, new_value, now))

        logger.debug(f"Statistic incremented: {key} = {new_value}")
        return new_value

    def set_statistic(self, key: str, value: int):
        """
        Set a statistic value

        Args:
            key: Statistic key
            value: Statistic value
        """
        now = datetime.now().isoformat()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO statistics (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, value, now))

        logger.info(f"Statistic set: {key} = {value}")

    # Migration and Backup Methods

    def import_from_config(self, config: Dict):
        """
        Import data from config.json format

        Args:
            config: Configuration dictionary from JSON
        """
        logger.info("Importing data from config...")

        # Import URLs
        urls = config.get('urls', [])
        for url_data in urls:
            # Check if URL already exists
            existing = self.get_url(url_data.get('id', ''))
            if not existing:
                url_id = url_data.get('id', str(uuid.uuid4()))
                now = datetime.now().isoformat()

                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO urls (id, url, name, enabled, interval_seconds, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        url_id,
                        url_data.get('url'),
                        url_data.get('name', 'Imported URL'),
                        1 if url_data.get('enabled', True) else 0,
                        url_data.get('interval_seconds'),
                        now,
                        now
                    ))

        # Import settings
        settings_to_import = {
            'interval_seconds': config.get('interval_seconds'),
            'timeout_seconds': config.get('timeout_seconds'),
            'user_agent': config.get('user_agent')
        }

        for key, value in settings_to_import.items():
            if value is not None:
                self.set_setting(key, value)

        logger.info(f"Imported {len(urls)} URLs and {len(settings_to_import)} settings")

    def export_to_config(self) -> Dict:
        """
        Export database data to config.json format

        Returns:
            Configuration dictionary suitable for JSON export
        """
        urls = self.get_all_urls()
        settings = self.get_all_settings()

        # Convert to config.json format
        config = {
            'urls': [
                {
                    'id': url['id'],
                    'url': url['url'],
                    'name': url['name'],
                    'enabled': url['enabled'],
                    'interval_seconds': url.get('interval_seconds')
                }
                for url in urls
            ],
            'interval_seconds': settings.get('interval_seconds', 300),
            'timeout_seconds': settings.get('timeout_seconds', 10),
            'user_agent': settings.get('user_agent', 'AutoClicker/1.0')
        }

        return config
