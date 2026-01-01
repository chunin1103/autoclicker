# Feature Overview

This document provides a quick reference to all features in the Autoclicker service.

## Core Features

### 1. Professional Admin Interface
- Clean, Notion-style web dashboard
- Real-time status monitoring
- Toast notifications for all actions
- Mobile-responsive design
- Access at `/admin` endpoint

### 2. Per-Website Ping Intervals
Set custom ping intervals for each URL independently.

**Examples:**
- Critical production site: 60 seconds
- Regular monitoring: 300 seconds (5 minutes)
- Low-priority site: 600 seconds (10 minutes)
- Use global default: Leave empty

**How to use:**
1. Go to admin interface
2. Find the URL in the list
3. Edit the "Interval" field (in seconds)
4. Leave empty to use global default
5. Changes apply immediately

### 3. Active Hours Scheduling
Configure specific time windows when each URL should be pinged.

**Examples:**
- Business hours: 09:00 - 17:00
- Extended hours: 09:00 - 22:00
- Night shift: 22:00 - 06:00 (crosses midnight)
- 24/7 operation: Leave both fields empty

**How to use:**
1. Go to admin interface
2. Find the URL in the list
3. Set "Active Hours" start and end times
4. Use HH:MM format (24-hour)
5. Leave empty for 24/7 operation

**Behavior:**
- Inside active hours: Pings normally at configured interval
- Outside active hours: Pinging pauses automatically
- Resumes automatically when active period starts

### 4. Timezone Configuration
All active hours use your configured timezone, not the server's timezone.

**Supported Timezones:**
- Asia/Bangkok (GMT+7)
- UTC (GMT+0)
- America/New_York (EST/EDT)
- America/Los_Angeles (PST/PDT)
- America/Chicago (CST/CDT)
- Europe/London (GMT/BST)
- Europe/Paris (CET/CEST)
- Asia/Tokyo (JST)
- Asia/Shanghai (CST)
- Asia/Singapore (SGT)
- Asia/Hong_Kong (HKT)
- Australia/Sydney (AEDT/AEST)

**How to use:**
1. Go to admin interface
2. Scroll to "Settings" section
3. Select your timezone from dropdown
4. Click "Save Settings"
5. All timers restart automatically

**Why this matters:**
- Deploy to Koyeb (UTC server) but use Bangkok timezone
- Active hours 09:00-22:00 means 9 AM - 10 PM in YOUR timezone
- Works correctly regardless of server location

### 5. SQLite Database Persistence
All configuration stored in reliable SQLite database.

**Benefits:**
- Data survives server crashes
- Automatic recovery from errors
- Fast queries with indexing
- ACID-compliant transactions
- Automatic schema migrations

**Files:**
- `autoclicker.db` - Primary database (gitignored)
- `config.json` - JSON backup (auto-updated)

### 6. REST API
Programmatic access to all features.

**Endpoints:**
- `GET /api/config` - Get full configuration
- `GET /api/urls` - Get all URLs
- `POST /api/urls` - Add new URL
- `PUT /api/urls/:id` - Update URL
- `DELETE /api/urls/:id` - Delete URL
- `PUT /api/settings` - Update global settings
- `GET /status` - Service status
- `GET /health` - Health check

## Usage Examples

### Example 1: Basic Setup
```
Website: https://mysite.com
Interval: 300 seconds (use global default)
Active Hours: (empty = 24/7)
Result: Pings every 5 minutes, 24/7
```

### Example 2: Business Hours Only
```
Website: https://businessapp.com
Interval: 60 seconds
Active Hours: 09:00 - 17:00
Timezone: Asia/Bangkok
Result: Pings every minute from 9 AM to 5 PM Bangkok time
```

### Example 3: Different Intervals
```
Critical site: 60 seconds
Regular site: 300 seconds
Low priority: 600 seconds
All: Active Hours 09:00 - 22:00
Result: Each pings at its own interval, only during 9 AM - 10 PM
```

### Example 4: Night Monitoring
```
Website: https://nightshift.com
Interval: 120 seconds
Active Hours: 22:00 - 06:00
Result: Pings every 2 minutes from 10 PM to 6 AM (crosses midnight)
```

### Example 5: Global Deployment
```
Server: Deployed on Koyeb (UTC timezone)
Configured Timezone: Asia/Bangkok (GMT+7)
Active Hours: 09:00 - 22:00
Result: Pings from 9 AM to 10 PM Bangkok time, even though server is in UTC
```

## Best Practices

### 1. Choosing Intervals
- **Critical services**: 60-120 seconds
- **Regular monitoring**: 300 seconds (5 minutes)
- **Low-priority**: 600 seconds (10 minutes)
- **Resource-constrained**: 900 seconds (15 minutes)

### 2. Using Active Hours
- **Production sites**: Keep 24/7 for maximum uptime
- **Development sites**: Use business hours to save resources
- **Scheduled tasks**: Match your task schedules
- **Cost optimization**: Reduce pinging during off-hours

### 3. Timezone Setup
- **Always set timezone** when using active hours
- **Use your local timezone** for easier management
- **Test after deployment** to verify timing is correct
- **Check logs** to confirm pings happen at expected times

### 4. Performance
- **Free tier**: Keep under 20 URLs
- **Paid tier**: Can handle hundreds of URLs
- **Lower intervals** = higher resource usage
- **Active hours** = reduced resource usage

## Troubleshooting

### URLs not pinging
1. Check if URL is enabled (toggle switch)
2. Verify active hours match current time in your timezone
3. Check timezone setting is correct
4. View logs for errors

### Active hours not working
1. Verify timezone is set correctly
2. Check start/end times are in HH:MM format
3. Confirm current time is within active window
4. Check server logs for timing information

### Changes not taking effect
1. Wait for current interval to complete
2. Check for errors in toast notifications
3. Reload admin page to verify changes saved
4. Check logs for confirmation messages

## Advanced Configuration

### Using config.json (Backup)
While the admin interface is recommended, you can also edit `config.json`:

```json
{
  "urls": [
    {
      "id": "1",
      "url": "https://example.com",
      "name": "Example Site",
      "enabled": true,
      "interval_seconds": 60,
      "start_time": "09:00",
      "end_time": "22:00"
    }
  ],
  "interval_seconds": 300,
  "timeout_seconds": 10,
  "user_agent": "AutoClicker/1.0",
  "timezone": "Asia/Bangkok"
}
```

**Note:** Changes to `config.json` are automatically migrated to the database on startup.

## Summary

The Autoclicker service now offers enterprise-grade scheduling features:
- ✅ Per-URL intervals for granular control
- ✅ Active hours for time-based scheduling
- ✅ Timezone support for global deployments
- ✅ SQLite persistence for reliability
- ✅ Easy-to-use admin interface
- ✅ REST API for automation

All features work seamlessly together and can be configured in real-time through the admin interface!
