# Claude.md - Autoclicker Project Tracker

## Project Summary

**Autoclicker** is a production-ready Python-based website pinger service that automatically pings configured websites at regular intervals to keep them alive and monitor uptime.

**Tech Stack**: Python 3.11.9, Flask, Gunicorn, SQLite3, Docker
**Key Features**:
- Professional Notion-style admin dashboard for URL management
- SQLite database for persistent, crash-resistant data storage
- REST API for configuration and monitoring
- Multi-deployment support (Koyeb, Docker, systemd, Heroku, VPS)
- Independent timers for each URL with customizable ping intervals
- Per-website interval configuration with global default fallback
- **Time-based scheduling: Set active hours for each URL (e.g., 9 AM - 10 PM)**
- **Automatic pause/resume outside active hours**
- Health check endpoints for cloud platform integration
- Real-time interval and schedule editing via admin interface

**Architecture**: Hybrid Flask web server with independent background timers for each URL. Each website pings on its own schedule using threading.Timer, respecting configured active hours. Uses SQLite for ACID-compliant data persistence with automatic schema migrations.

---

## Progress

(Currently no tasks in progress)

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
