# Autoclicker - Website Pinger Service

A Python-based service that automatically pings configured websites at regular intervals. Perfect for keeping websites alive, monitoring uptime, or preventing services from sleeping.

## Features

- ✓ Configurable URL list
- ✓ Customizable ping intervals
- ✓ Comprehensive logging
- ✓ Multiple deployment options for 24/7 operation
- ✓ Docker support
- ✓ Systemd service support
- ✓ Graceful error handling

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd autoclicker

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Edit `config.json` to add your URLs:

```json
{
  "urls": [
    "https://your-website.com",
    "https://another-site.com"
  ],
  "interval_seconds": 300,
  "timeout_seconds": 10,
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
```

**Configuration options:**
- `urls`: List of URLs to ping
- `interval_seconds`: Time between ping cycles (default: 300 = 5 minutes)
- `timeout_seconds`: Request timeout (default: 10)
- `user_agent`: User agent string for requests

### 3. Run Manually

```bash
python3 autoclicker.py
```

Press `Ctrl+C` to stop.

## 24/7 Deployment Options

### Option 1: Docker (Recommended)

**Advantages:**
- Easy to deploy anywhere
- Isolated environment
- Automatic restarts
- Works on any OS

**Steps:**

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart
```

**Or using Docker directly:**

```bash
# Build
docker build -t autoclicker .

# Run
docker run -d \
  --name autoclicker \
  --restart unless-stopped \
  -v $(pwd)/config.json:/app/config.json \
  -v $(pwd)/logs:/app/logs \
  autoclicker
```

### Option 2: Systemd Service (Linux)

**Advantages:**
- Native Linux integration
- Starts on boot
- System-level process management
- Journald logging integration

**Steps:**

1. Edit `autoclicker.service` and update paths:
   ```bash
   # Change these lines:
   User=youruser                                    # Your username
   WorkingDirectory=/path/to/autoclicker           # Full path to project
   ExecStart=/usr/bin/python3 /path/to/autoclicker/autoclicker.py
   ```

2. Install the service:
   ```bash
   # Copy service file
   sudo cp autoclicker.service /etc/systemd/system/

   # Create log directory
   sudo mkdir -p /var/log/autoclicker
   sudo chown youruser:youruser /var/log/autoclicker

   # Reload systemd
   sudo systemctl daemon-reload

   # Enable and start service
   sudo systemctl enable autoclicker
   sudo systemctl start autoclicker
   ```

3. Manage the service:
   ```bash
   # Check status
   sudo systemctl status autoclicker

   # View logs
   sudo journalctl -u autoclicker -f

   # Restart
   sudo systemctl restart autoclicker

   # Stop
   sudo systemctl stop autoclicker
   ```

### Option 3: Screen/Tmux (Simple)

**Advantages:**
- Very simple
- No installation needed
- Easy to attach and check

**Disadvantages:**
- Manual restart after reboot
- Process can be killed

**Using Screen:**

```bash
# Start a new screen session
screen -S autoclicker

# Run the script
python3 autoclicker.py

# Detach: Press Ctrl+A, then D

# Reattach later
screen -r autoclicker

# List sessions
screen -ls
```

**Using Tmux:**

```bash
# Start new tmux session
tmux new -s autoclicker

# Run the script
python3 autoclicker.py

# Detach: Press Ctrl+B, then D

# Reattach later
tmux attach -t autoclicker

# List sessions
tmux ls
```

### Option 4: Cron Job (Periodic Execution)

**Advantages:**
- Built into Linux
- Very simple

**Disadvantages:**
- Not truly 24/7 (runs periodically)
- No persistent process

**Steps:**

```bash
# Edit crontab
crontab -e

# Add this line to run every 5 minutes:
*/5 * * * * cd /path/to/autoclicker && /usr/bin/python3 autoclicker.py --once

# Or run every hour:
0 * * * * cd /path/to/autoclicker && /usr/bin/python3 autoclicker.py --once
```

Note: You'll need to modify `autoclicker.py` to support `--once` flag for single execution.

### Option 5: Cloud Hosting

**A. Free Tier Cloud Options:**

1. **Google Cloud Run** (Free tier available)
   - Deploy as container
   - Automatic scaling
   - Free 2M requests/month

2. **AWS EC2 Free Tier**
   - t2.micro instance free for 12 months
   - Use systemd or Docker

3. **Oracle Cloud (Always Free)**
   - 2 AMD-based VMs
   - Use systemd or Docker

4. **Heroku** (Limited free tier)
   - Deploy via Git
   - Automatically restarts

**B. VPS Providers (Low Cost):**

- DigitalOcean ($4-6/month)
- Linode ($5/month)
- Vultr ($2.50-6/month)
- Hetzner ($3-5/month)

### Option 6: Raspberry Pi / Home Server

**Advantages:**
- One-time cost
- Full control
- Can run other services

**Steps:**
1. Install Raspberry Pi OS
2. Follow systemd service setup above
3. Ensure stable internet connection

## Monitoring & Logs

### View Logs

**Docker:**
```bash
docker-compose logs -f
# or
docker logs -f autoclicker
```

**Systemd:**
```bash
sudo journalctl -u autoclicker -f
```

**File logs:**
```bash
tail -f autoclicker.log
```

### Log Files

- `autoclicker.log` - Main log file with ping results
- Contains timestamps, status codes, and errors

## Troubleshooting

### Service won't start

```bash
# Check Python is installed
python3 --version

# Check dependencies
pip install -r requirements.txt

# Check config file
python3 -m json.tool config.json
```

### URLs not being pinged

- Check internet connection
- Verify URLs in config.json are valid
- Check firewall settings
- Review logs for errors

### High CPU usage

- Increase `interval_seconds` in config.json
- Reduce number of URLs

## Security Considerations

- Don't ping websites you don't own without permission
- Some websites may block or rate-limit automated requests
- Consider using this only for your own services
- Respect robots.txt and terms of service

## Customization

### Add Custom Headers

Edit `autoclicker.py` line 57:

```python
headers = {
    'User-Agent': self.user_agent,
    'Custom-Header': 'value'
}
```

### Add POST Requests

Modify the `ping_url` method to use `requests.post()` instead of `requests.get()`.

### Send Notifications on Failure

Add email/Slack/Discord notifications in the `ping_url` method when `success == False`.

## License

MIT License - Feel free to use and modify as needed.

## Contributing

Pull requests welcome! Please ensure code follows PEP 8 style guidelines.
