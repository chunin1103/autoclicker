# Quick Deployment Guide for Koyeb

This guide will help you deploy the Autoclicker service on Koyeb in just a few minutes.

## Prerequisites

- A GitHub account
- A Koyeb account (sign up free at [app.koyeb.com](https://app.koyeb.com))
- Your code pushed to a GitHub repository

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

### 7. Deploy!

Click the **"Deploy"** button and wait 2-3 minutes for deployment to complete.

## Post-Deployment

### Access Your Service

Koyeb will provide a public URL like:
```
https://your-app-name-yourorg.koyeb.app
```

### Check Endpoints

- **Home**: `https://your-app-name.koyeb.app/`
- **Health**: `https://your-app-name.koyeb.app/health`
- **Status**: `https://your-app-name.koyeb.app/status`

### View Logs

1. Go to your Koyeb dashboard
2. Click on your app
3. Click on **"Logs"** tab
4. You'll see your ping activity in real-time!

## Updating Configuration

### Method 1: Update config.json via GitHub

1. Edit `config.json` in your repository
2. Commit and push changes
3. Koyeb will auto-deploy (if auto-deploy is enabled)

### Method 2: Environment Variables (Advanced)

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

- [ ] Code pushed to GitHub
- [ ] Koyeb app created and deployed
- [ ] Health check passing (green status)
- [ ] Can access `/health` endpoint
- [ ] Can access `/status` endpoint and see ping statistics
- [ ] Logs show "Starting autoclicker service..."
- [ ] Logs show ping cycles completing

If all checkboxes are checked, your service is running 24/7 on Koyeb! 🎉
