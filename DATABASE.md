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
Stores all configured website URLs:
- `id` - Unique identifier (UUID)
- `url` - The website URL to ping
- `name` - Display name for the URL
- `enabled` - Whether the URL is active (boolean)
- `created_at` - Timestamp when URL was added
- `updated_at` - Timestamp of last update

### Settings Table
Stores configuration settings:
- `key` - Setting name (e.g., 'interval_seconds')
- `value` - Setting value
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

## Technical Details

### Database Operations

All CRUD operations are handled through the `Database` class:

```python
from database import Database

db = Database('autoclicker.db')

# Add URL
url = db.add_url('https://example.com', 'Example', enabled=True)

# Get all URLs
urls = db.get_all_urls()

# Update URL
db.update_url(url_id, name='New Name', enabled=False)

# Delete URL
db.delete_url(url_id)

# Settings
db.set_setting('interval_seconds', 300)
interval = db.get_setting('interval_seconds')
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
