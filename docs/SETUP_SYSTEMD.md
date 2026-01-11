# Systemd Setup Guide for SkillOps

This guide explains how to set up SkillOps to run automatically every day using systemd timers.

## Why Systemd Timers?

Systemd timers are the modern replacement for cron jobs on Linux systems. They provide:

- **Better logging**: All output goes to the system journal (queryable with `journalctl`)
- **Integration**: Works seamlessly with other system services
- **Reliability**: Automatic restart on failure, configurable retry behavior
- **Flexibility**: Run on specific times, calendar dates, boot, or based on unit state changes
- **User-level support**: Can run user services without root privileges (recommended)

## Installation

### 1. Install SkillOps

```bash
pip install skillops==0.2.0
```

Verify installation:
```bash
skillops --version
skillops start --help
```

### 2. Create Configuration Directory

```bash
mkdir -p ~/.config/skillops
```

### 3. Create Environment File

Create `~/.config/skillops/skillops.env` with your API tokens:

```bash
cat > ~/.config/skillops/skillops.env << 'EOF'
# API Keys (obtain from respective services)
WAKATIME_API_KEY=your_wakatime_key_here
GEMINI_API_KEY=your_gemini_key_here
GITHUB_TOKEN=your_github_token_here
GITHUB_USERNAME=your_github_username
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Optional paths
LABS_PATH=~/labs
OBSIDIAN_VAULT_PATH=~/Vault
ANKI_SYNC_PATH=~/Anki2/User\ 1/collection.media
STORAGE_PATH=~/.local/share/skillops

# Telegram schedule (24-hour format)
TELEGRAM_SCHEDULE_TIME=20:00

# Verbose mode (optional)
VERBOSE=false
EOF

chmod 600 ~/.config/skillops/skillops.env
```

**Important:** Keep `skillops.env` private (`600` permissions) as it contains sensitive API keys.

### 4. Copy Systemd Files

```bash
mkdir -p ~/.config/systemd/user/
cp setup/systemd/skillops.service ~/.config/systemd/user/
cp setup/systemd/skillops.timer ~/.config/systemd/user/

# If using per-user username (recommended for security):
cp setup/systemd/skillops.service ~/.config/systemd/user/skillops@.service
cp setup/systemd/skillops.timer ~/.config/systemd/user/skillops@.timer
```

### 5. Customize Files (Optional)

Edit `~/.config/systemd/user/skillops.service` to:
- Change the execution time in `skillops.timer` (default: 8:00 AM daily)
- Modify resource limits (memory, CPU) as needed
- Update the `ExecStart` command to use different SkillOps commands

Common customizations:

```ini
# Run only 'review' step
ExecStart=/usr/bin/skillops review

# Run with verbose output
ExecStart=/usr/bin/skillops start --verbose

# Run at specific time (e.g., 9:30 PM)
OnCalendar=*-*-* 21:30:00
```

### 6. Enable and Start the Timer

```bash
# Reload systemd configuration
systemctl --user daemon-reload

# Enable timer to run on boot
systemctl --user enable skillops.timer

# Start the timer immediately
systemctl --user start skillops.timer

# Verify it's running
systemctl --user status skillops.timer
```

## Usage

### Check Timer Status

```bash
systemctl --user status skillops.timer
systemctl --user list-timers
```

### View Recent Runs

```bash
# View last 50 lines of SkillOps logs
journalctl --user-unit=skillops.service -n 50

# Follow logs in real-time
journalctl --user-unit=skillops.service -f

# View last 24 hours of logs
journalctl --user-unit=skillops.service --since "24 hours ago"

# View errors only
journalctl --user-unit=skillops.service -p err
```

### Manually Run Service

```bash
# Run the service once immediately
systemctl --user start skillops.service

# Check if it ran successfully
systemctl --user status skillops.service
journalctl --user-unit=skillops.service -n 20
```

### Disable/Stop Service

```bash
# Stop the timer
systemctl --user stop skillops.timer

# Disable timer from running at boot
systemctl --user disable skillops.timer

# Stop current execution
systemctl --user stop skillops.service
```

## Troubleshooting

### "systemctl: command not found"

You're likely on a system without systemd (some minimal containers, older systems). Use [cron jobs](SETUP_CRON.md) instead.

### Timer doesn't run at scheduled time

1. Check if timer is enabled and active:
   ```bash
   systemctl --user status skillops.timer
   ```

2. Verify the timer schedule syntax:
   ```bash
   systemd-analyze calendar "daily"
   systemd-analyze calendar "*-*-* 08:00:00"
   ```

3. Check for execution errors:
   ```bash
   journalctl --user-unit=skillops.service -p err
   ```

### Service fails immediately

1. Check for errors:
   ```bash
   journalctl --user-unit=skillops.service -n 50
   ```

2. Verify configuration file:
   ```bash
   cat ~/.config/skillops/skillops.env
   ```

3. Test manually:
   ```bash
   skillops start --verbose
   ```

### Cannot find Python/SkillOps executable

1. Verify installation:
   ```bash
   which skillops
   ~/.local/bin/skillops --version
   ```

2. Update service file to use absolute path:
   ```bash
   ExecStart=/home/username/.local/bin/skillops start
   ```

3. Verify PATH in environment file:
   ```bash
   echo $PATH
   # Should include /home/username/.local/bin
   ```

### Logs not appearing in journalctl

1. Enable per-user journal:
   ```bash
   mkdir -p ~/.local/share/systemd/journal/
   systemctl --user restart systemd-journald
   ```

2. Verify standard output is set to journal:
   ```bash
   grep StandardOutput ~/.config/systemd/user/skillops.service
   # Should be: StandardOutput=journal
   ```

## Advanced Configuration

### Run Multiple Schedules

Create multiple timer instances:

```bash
cp ~/.config/systemd/user/skillops.timer ~/.config/systemd/user/skillops-morning.timer
cp ~/.config/systemd/user/skillops.timer ~/.config/systemd/user/skillops-evening.timer

# Edit skillops-morning.timer
systemctl --user enable skillops-morning.timer

# Edit skillops-evening.timer
systemctl --user enable skillops-evening.timer
```

### Run Different Commands

```bash
# Service for morning review only
ExecStart=/usr/bin/skillops review

# Service for evening reflection only
ExecStart=/usr/bin/skillops reflect
```

### Resource Limits

Adjust memory and CPU usage:

```ini
# Limit memory to 256MB
MemoryLimit=256M

# Limit CPU to 20%
CPUQuota=20%

# Limit tasks to 10 per service unit
TasksMax=10
```

### Notifications on Failure

Add email or notification on failure:

```ini
[Service]
OnFailure=send-email@%n.service
```

## Monitoring

### Check Timer Execution History

```bash
# Show when timers will next run
systemctl --user list-timers skillops.timer --all

# Show execution statistics
systemctl --user show skillops.timer
```

### Health Check

After setup, verify everything works:

```bash
# 1. Check environment file exists and is readable
cat ~/.config/skillops/skillops.env

# 2. Run skillops health check
skillops health

# 3. Manually trigger service
systemctl --user start skillops.service

# 4. Check logs
journalctl --user-unit=skillops.service -n 30

# 5. Verify next scheduled run
systemctl --user list-timers skillops.timer
```

## Uninstall

To remove SkillOps from systemd:

```bash
# Stop the timer
systemctl --user stop skillops.timer

# Disable it
systemctl --user disable skillops.timer

# Remove service files
rm ~/.config/systemd/user/skillops.service
rm ~/.config/systemd/user/skillops.timer

# Reload systemd
systemctl --user daemon-reload

# Keep config if you might reinstall
# rm -rf ~/.config/skillops
```

## See Also

- [SETUP_CRON.md](SETUP_CRON.md) – Alternative: cron jobs for scheduling
- [QUICKSTART.md](QUICKSTART.md) – Getting started with SkillOps
- [Systemd Documentation](https://www.freedesktop.org/software/systemd/man/systemd.timer.html)
