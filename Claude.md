# Claude.md - Autoclicker Project Tracker

## Project Summary

**Autoclicker** is a production-ready Python-based website pinger service that automatically pings configured websites at regular intervals to keep them alive and monitor uptime.

**Tech Stack**: Python 3.11.9, Flask, Gunicorn, SQLite3/PostgreSQL, Docker
**Key Features**:
- Professional Notion-style admin dashboard for URL management
- SQLite/PostgreSQL database for persistent, crash-resistant data storage
- REST API for configuration and monitoring
- Multi-deployment support (Koyeb, Docker, systemd, Heroku, VPS)
- Independent timers for each URL with customizable ping intervals
- Per-website interval configuration with global default fallback
- **Time-based scheduling: Set active hours for each URL (e.g., 9 AM - 10 PM)**
- **Automatic pause/resume outside active hours**
- **Retry logic with 3 attempts to handle cold starts (60s timeout)**
- Health check endpoints for cloud platform integration
- Real-time interval and schedule editing via admin interface

**Architecture**: Hybrid Flask web server with independent background timers for each URL. Each website pings on its own schedule using threading.Timer, respecting configured active hours. Uses SQLite for ACID-compliant data persistence with automatic schema migrations.

---

## Progress

(Currently no tasks in progress)

**Latest Session Summary (2026-01-04):**
- Fixed websites not waking up from cold starts
- Increased default timeout from 10s to 60s (cloud cold starts take 30-60s)
- Added retry logic: 3 attempts with 5-second delay between retries
- Websites now reliably wake up even with long cold start times

**Previous Session (2026-01-04):**
- Added PostgreSQL support for persistent data storage on Koyeb
- Data now persists across server restarts and redeployments
- Uses Neon PostgreSQL (free tier) as external database
- Falls back to SQLite for local development
- Updated KOYEB_DEPLOY.md with Neon setup instructions
- Optimized database performance (connection pooling, batched queries)
- Fixed 30-second delay when adding/removing URLs

**Previous Session (2026-01-01):**
- Implemented complete per-website interval and active hours scheduling system
- Added timezone support for accurate active hours across different server locations
- Updated all documentation (README.md, DATABASE.md, KOYEB_DEPLOY.md)
- Cleaned up project files and verified all code
- All features tested and verified working correctly

---

## Done

- Initial repository scan and project analysis (2026-01-01)
- Created Claude.md project tracker
- Implemented per-website ping intervals with independent timers (2026-01-01)
  - Added `interval_seconds` column to database URLs table with automatic migration
  - Refactored ping system from batch processing to independent timers per URL
  - Each URL now pings on its own schedule (custom interval or global default)
  - Added interval editing to admin UI - can set per-URL intervals inline
  - URLs without custom intervals automatically use global default setting
  - Admin page allows editing intervals for both individual URLs and global default
- **Implemented time-based scheduling with active hours (2026-01-01)**
  - Added `start_time` and `end_time` columns to database URLs table with automatic migration
  - Implemented active hours logic: URLs only ping during configured time windows
  - Supports time ranges that cross midnight (e.g., 22:00 - 06:00)
  - Outside active hours, pinging pauses and resumes automatically when active period starts
  - URLs without time configuration ping 24/7 (backward compatible)
  - Added time picker UI in admin panel for setting active hours per URL
  - Real-time active hours editing with instant timer restart
  - Example: Set abc.com to ping from 9 AM - 10 PM with 300 second intervals
- **Added timezone support (2026-01-01)**
  - Added global `timezone` setting in database (default: Asia/Bangkok)
  - All active hours use configured timezone instead of server local time
  - Works correctly regardless of server deployment location (cloud vs local)
  - Timezone selector in admin panel with 12 common timezones
  - Uses Python's built-in zoneinfo for timezone handling (no extra dependencies)
  - Changing timezone automatically restarts all timers
  - Example: Deploy to UTC server but keep active hours in SE Asia timezone
- **Added PostgreSQL support for persistent cloud storage (2026-01-04)**
  - Data now persists across Koyeb server restarts and redeployments
  - Uses Neon PostgreSQL (free tier) as external database
  - Automatically detects DATABASE_URL environment variable
  - Falls back to SQLite for local development (no changes needed)
  - Updated KOYEB_DEPLOY.md with Neon setup instructions
  - Added psycopg2-binary to requirements.txt
- **Optimized database performance for PostgreSQL (2026-01-04)**
  - Added connection pooling (reuses connections instead of opening new ones)
  - Batched settings queries (1 query instead of 4 separate calls)
  - Skip JSON backup when using PostgreSQL (not needed with persistent DB)
  - Fixed 30-second delay when adding/removing URLs
- **Fixed cold start wake-up issue (2026-01-04)**
  - Increased default timeout from 10s to 60s (cloud platforms need 30-60s to cold start)
  - Added retry logic with 3 attempts and 5-second delay between retries
  - First request triggers wake-up, retries catch the now-warm service
  - Websites now reliably wake up even on free tier cloud platforms (Koyeb, Render, etc.)
