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
- Health check endpoints for cloud platform integration
- Real-time interval editing via admin interface

**Architecture**: Hybrid Flask web server with independent background timers for each URL. Each website pings on its own schedule using threading.Timer. Uses SQLite for ACID-compliant data persistence with automatic schema migrations.

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
