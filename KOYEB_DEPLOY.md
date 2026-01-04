# Quick Deployment Guide for Koyeb

This guide will help you deploy the Autoclicker service on Koyeb in just a few minutes.

## Prerequisites

- A GitHub account
- A Koyeb account (sign up free at [app.koyeb.com](https://app.koyeb.com))
- A Neon PostgreSQL account (sign up free at [neon.tech](https://neon.tech)) - **Required for data persistence!**
- Your code pushed to a GitHub repository

## Important: Data Persistence

**Without a database, your URLs and settings will be lost when Koyeb restarts!**

Koyeb uses ephemeral storage - files are deleted when the container restarts. To keep your data, you need an external PostgreSQL database.

### Set Up Neon PostgreSQL (Free)

1. Go to [neon.tech](https://neon.tech) and sign up (free tier available)
2. Create a new project (e.g., "autoclicker")
3. Copy your connection string from the dashboard. It looks like:
   ```
   postgresql://username:password@ep-xxx-xxx-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. Save this connection string - you'll need it when configuring Koyeb

## Step-by-Step Deployment

### 1. Push Code to GitHub

```bash
# Make sure your code is committed
git add .
git commit -m "Ready for Koyeb deployment"

# Push to GitHub
git push origin main
```

### 2. Create App on Koyeb

1. Go to [app.koyeb.com](https://app.koyeb.com)
2. Click **"Create App"** button
3. Choose **"GitHub"** as your deployment method

### 3. Connect GitHub Repository

1. Click **"Authorize GitHub"**
2. Select your **autoclicker** repository
3. Choose the branch: **main** (or your default branch)

### 4. Configure Build Settings

**Basic Settings:**
- **App name**: autoclicker (or your preferred name)
- **Region**: Choose closest to you (e.g., Washington D.C. - was)

**Build Configuration:**
- **Builder**: Buildpack (auto-detected Python)
- **Build command**: (leave empty - auto-detected)
- **Run command**:
  ```
  gunicorn autoclicker:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
  ```

**Port Configuration:**
- **Port**: 8000
- **Protocol**: HTTP

### 5. Configure Health Checks

- **Health check path**: `/health`
- **Port**: 8000
- **Initial delay**: 30 seconds
- **Period**: 30 seconds
- **Timeout**: 10 seconds

### 6. Set Instance Type

- **Instance type**: Nano (Free tier)
- **Scaling**: Min 1, Max 1

### 7. Configure Environment Variables (Important!)

Add the following environment variable:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | Your Neon PostgreSQL connection string |

Example:
```
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**This is required for your data to persist across restarts!**

### 8. Deploy!

Click the **"Deploy"** button and wait 2-3 minutes for deployment to complete.

## Post-Deployment

### Access Your Service

Koyeb will provide a public URL like:
```
https://your-app-name-yourorg.koyeb.app
```

### Check Endpoints

- **Admin Interface**: `https://your-app-name.koyeb.app/admin` ⭐ **Start here!**
- **Home**: `https://your-app-name.koyeb.app/`
- **Health**: `https://your-app-name.koyeb.app/health`
- **Status**: `https://your-app-name.koyeb.app/status`

### Use the Admin Interface

1. Visit `https://your-app-name.koyeb.app/admin`
2. You'll see a clean, Notion-style interface
3. Add your URLs by:
   - Entering a name (e.g., "My Website")
   - Entering the URL (e.g., "https://mysite.com")
   - (Optional) Set custom ping interval in seconds
   - (Optional) Set active hours (e.g., 09:00 - 22:00)
   - Clicking "Add URL"
4. Manage URLs:
   - Toggle URLs on/off with the switch
   - Edit intervals inline (leave empty for global default)
   - Edit active hours inline (leave empty for 24/7)
   - Delete URLs with the Delete button
   - View real-time status (Online/Offline/Pending)
5. Update global settings:
   - Scroll to "Settings" section
   - Change global ping interval or timeout
   - **Select your timezone** (important for active hours!)
   - Click "Save Settings"

**New Features:**
- **Per-URL Intervals**: Set different ping intervals for each URL
- **Active Hours**: Configure time windows when each URL should ping
- **Timezone Support**: Active hours work correctly in your timezone even if server is in UTC

### View Logs

1. Go to your Koyeb dashboard
2. Click on your app
3. Click on **"Logs"** tab
4. You'll see your ping activity in real-time!

## Managing URLs

### Method 1: Use the Admin Interface (Recommended) ⭐

The easiest way to manage URLs is through the admin interface:

1. Visit `https://your-app.koyeb.app/admin`
2. Add, delete, or toggle URLs directly in the browser
3. Changes are saved immediately - no need to redeploy!
4. The pinger will pick up changes on the next cycle

**Benefits:**
- No need to edit code or redeploy
- Real-time status updates
- Easy to use, no technical knowledge required
- Changes take effect within minutes

### Method 2: Update config.json via GitHub

1. Edit `config.json` in your repository
2. Commit and push changes
3. Koyeb will auto-deploy (if auto-deploy is enabled)

**Note:** Using the admin interface is much faster and doesn't require redeployment!

### Method 3: Environment Variables (Advanced)

You can override config via environment variables in Koyeb:
1. Go to your app → **Settings** → **Environment**
2. Add variables as needed
3. Redeploy

## Troubleshooting

### Build Fails

**Issue**: Python version not detected
- **Solution**: Make sure `runtime.txt` exists with `python-3.11.9`

**Issue**: Dependencies not installed
- **Solution**: Check `requirements.txt` is in the root directory

### Health Check Fails

**Issue**: `/health` endpoint not responding
- **Solution**: Check logs to see if Flask server started correctly
- **Solution**: Verify PORT is 8000 in your configuration

### Service Not Pinging

**Issue**: Pinger not running
- **Solution**: Check logs for errors
- **Solution**: Verify `config.json` has valid URLs
- **Solution**: Check the background thread started (look for "Starting autoclicker service..." in logs)

### Data Not Persisting

**Issue**: URLs and settings lost after restart
- **Solution**: Make sure `DATABASE_URL` environment variable is set in Koyeb
- **Solution**: Verify the Neon connection string is correct
- **Solution**: Check logs for "Using PostgreSQL database" on startup (if you see "Using SQLite database", DATABASE_URL is not set)

## Configuration Tips

### Optimal Ping Interval

For free tier, recommended settings in `config.json`:
```json
{
  "interval_seconds": 300,  // 5 minutes - good balance
  "timeout_seconds": 10
}
```

### Resource Usage

- Nano instance (free tier) is sufficient for up to 10-20 URLs
- Ping every 5 minutes uses minimal resources
- Keep URL list under 20 for best performance on free tier

## Free Tier Limitations

Koyeb free tier includes:
- ✓ 2 web services
- ✓ 512 MB RAM per service
- ✓ Shared CPU
- ✓ Unlimited bandwidth
- ✓ Auto-sleep after inactivity (wakes on request)
- ✓ HTTPS included

**Note**: Free tier may sleep after prolonged inactivity, but will wake up on any HTTP request to the service.

## Need Help?

- Koyeb Docs: https://www.koyeb.com/docs
- Koyeb Community: https://community.koyeb.com
- Check logs in Koyeb dashboard
- Verify health check is passing

## Success Checklist

- [ ] Neon PostgreSQL database created
- [ ] Code pushed to GitHub
- [ ] Koyeb app created and deployed
- [ ] `DATABASE_URL` environment variable set in Koyeb
- [ ] Logs show "Using PostgreSQL database" on startup
- [ ] Health check passing (green status)
- [ ] Can access `/health` endpoint
- [ ] Can access `/status` endpoint and see ping statistics
- [ ] Logs show "Starting autoclicker service..."
- [ ] Logs show ping cycles completing
- [ ] **Data persists after Koyeb restarts!**

If all checkboxes are checked, your service is running 24/7 on Koyeb with persistent data! 🎉
