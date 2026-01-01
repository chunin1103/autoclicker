# Database Persistence

## Overview

The autoclicker now uses SQLite database for persistent storage of website configurations. This ensures that your configured websites and settings are **never lost**, even if the server crashes, times out, or encounters problems.

## Key Features

### 🛡️ Crash-Resistant Storage
- **SQLite Database**: All data is stored in a reliable, ACID-compliant SQLite database
- **Automatic Recovery**: Database automatically recovers from server crashes
- **No Data Loss**: Configured websites persist across restarts and failures

### 🔄 Automatic Migration
- **Seamless Upgrade**: Existing `config.json` data is automatically migrated to the database on first run
- **Backup Created**: Original config.json is backed up as `config.json.backup`
- **Zero Downtime**: Migration happens transparently during initialization

### 💾 Dual Storage System
- **Primary Storage**: SQLite database (`autoclicker.db`)
- **JSON Backup**: config.json is maintained as a human-readable backup
- **Automatic Export**: Database changes are exported to config.json for backup purposes

## Database Schema

### URLs Table
Stores all configured website URLs with per-URL settings:
- `id` - Unique identifier (UUID)
- `url` - The website URL to ping
- `name` - Display name for the URL
- `enabled` - Whether the URL is active (boolean)
- `interval_seconds` - Custom ping interval for this URL (NULL = use global default)
- `start_time` - Active hours start time in HH:MM format (NULL = 24/7)
- `end_time` - Active hours end time in HH:MM format (NULL = 24/7)
- `created_at` - Timestamp when URL was added
- `updated_at` - Timestamp of last update

### Settings Table
Stores global configuration settings:
- `key` - Setting name (e.g., 'interval_seconds', 'timezone')
- `value` - Setting value
- `updated_at` - Timestamp of last update

**Default Settings:**
- `interval_seconds` - Global default ping interval (default: 300)
- `timeout_seconds` - Request timeout in seconds (default: 10)
- `user_agent` - User agent string for HTTP requests
- `timezone` - Timezone for active hours (default: 'Asia/Bangkok')

### Statistics Table
Stores service statistics:
- `key` - Statistic name (e.g., 'total_pings')
- `value` - Statistic value (integer)
- `updated_at` - Timestamp of last update

## Files

- **`database.py`**: Database module handling all SQLite operations
- **`autoclicker.db`**: SQLite database file (auto-created, git-ignored)
- **`config.json`**: JSON backup of database contents
- **`config.json.backup`**: Backup of original config.json after migration

## Benefits

1. **Reliability**: Data survives crashes, timeouts, and errors
2. **Performance**: Fast database queries with indexed lookups
3. **Integrity**: ACID transactions ensure data consistency
4. **Scalability**: Can handle large numbers of URLs efficiently
5. **Backup**: Automatic JSON export for human readability
6. **Flexibility**: Per-URL intervals and active hours scheduling
7. **Automatic Migrations**: Schema updates happen automatically when starting the service

## Technical Details

### Database Operations

All CRUD operations are handled through the `Database` class:

```python
from database import Database

db = Database('autoclicker.db')

# Add URL with per-URL settings
url = db.add_url(
    url='https://example.com',
    name='Example',
    enabled=True,
    interval_seconds=60,          # Custom interval (optional)
    start_time='09:00',            # Active hours start (optional)
    end_time='22:00'               # Active hours end (optional)
)

# Add URL with 24/7 operation (default)
url = db.add_url('https://example.com', 'Example', enabled=True)

# Get all URLs
urls = db.get_all_urls()

# Update URL settings
db.update_url(url_id,
    name='New Name',
    enabled=False,
    interval_seconds=120,
    start_time='10:00',
    end_time='23:00'
)

# Delete URL
db.delete_url(url_id)

# Global settings
db.set_setting('interval_seconds', 300)
db.set_setting('timezone', 'Asia/Bangkok')
interval = db.get_setting('interval_seconds')
timezone = db.get_setting('timezone', 'Asia/Bangkok')  # With default

# Statistics
total = db.get_statistic('total_pings')
db.increment_statistic('total_pings')  # Atomic increment
```

### Thread Safety

The database uses context managers and proper connection handling to ensure thread-safe operations in the multi-threaded Flask environment.

### Error Handling

All database operations include proper error handling with automatic rollback on failures, ensuring data integrity is maintained even during errors.

## Upgrade Notes

When upgrading from the JSON-only version:
1. Start the application normally
2. Database will be created automatically
3. Existing config.json data will be migrated
4. A backup will be created at config.json.backup
5. Application continues with no downtime

No manual steps required!
