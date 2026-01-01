# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-01-01

### Added
- **Per-Website Intervals**: Each URL can now have its own custom ping interval
  - Set different intervals for critical vs low-priority sites
  - Leave empty to use global default interval
  - Changes apply immediately without restart

- **Active Hours Scheduling**: Configure time windows for each URL
  - Set start and end times in HH:MM format
  - Supports time ranges that cross midnight (e.g., 22:00 - 06:00)
  - Leave empty for 24/7 operation
  - Automatic pause/resume based on schedule

- **Timezone Support**: All active hours use configured timezone
  - Works correctly regardless of server deployment location
  - 12 common timezones supported (Asia, Americas, Europe, Pacific)
  - Default: Asia/Bangkok (GMT+7)
  - Configurable via admin interface

- **Independent Timers**: Each URL now runs on its own timer
  - True independent scheduling per URL
  - No more batch processing delays
  - More accurate timing

- **Enhanced Admin Interface**:
  - Inline editing for intervals
  - Time picker inputs for active hours
  - Timezone selector in settings
  - Real-time configuration updates

- **Database Enhancements**:
  - Added `interval_seconds` column to urls table
  - Added `start_time` and `end_time` columns to urls table
  - Added `timezone` setting to settings table
  - Automatic schema migrations

- **Documentation**:
  - Added FEATURES.md with comprehensive feature guide
  - Updated README.md with new features and examples
  - Updated DATABASE.md with new schema
  - Updated KOYEB_DEPLOY.md with timezone instructions

### Changed
- **Ping Architecture**: Refactored from batch processing to independent timers
  - Each URL has its own threading.Timer
  - Timers automatically restart after each ping
  - Better resource utilization

- **Time Logic**: All time operations now timezone-aware
  - Uses Python's zoneinfo module (Python 3.9+)
  - No additional dependencies required

### Fixed
- N/A (new features, no bug fixes in this release)

### Technical Details
- Python 3.9+ required (for zoneinfo support)
- Automatic database migrations on startup
- Backward compatible (existing URLs continue working)
- All existing features maintained

## [1.0.0] - Previous Version

### Features
- Basic website pinging
- Admin interface
- SQLite database persistence
- Global interval configuration
- Enable/disable URLs
- REST API
- Multi-platform deployment support

