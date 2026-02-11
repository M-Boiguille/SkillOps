# Cron Setup Guide for SkillOps

This guide explains how to set up SkillOps to run automatically using cron jobs (traditional Linux job scheduler).

## Why Cron?

Cron is the traditional Unix/Linux job scheduler. Use cron if:

- You're on an older Linux system without systemd
- You prefer cron over systemd timers
- Your system is a container or WSL without full systemd support
- You like simple, straightforward scheduling

**Note:** If your system supports systemd, [SETUP_SYSTEMD.md](SETUP_SYSTEMD.md) is recommended for better logging and integration.

## Quick Start

### Automated Setup

Run the interactive installation script:

```bash
bash setup/cron/install.sh
```

This script will:
1. Check requirements (crontab availability)
2. Ask for execution time
3. Configure environment variables
4. Install the cron job
5. Verify installation

### Manual Setup

If you prefer manual configuration, follow the steps below.

## Installation

### 1. Install SkillOps

```bash
pip install skillops
```

### 2. Create Configuration Directory

```bash
mkdir -p ~/.config/skillops
mkdir -p ~/.local/share/skillops
```

### 3. Create Environment File

Create `~/.config/skillops/skillops.env`:

```bash
cat > ~/.config/skillops/skillops.env << 'EOF'
# API Keys
WAKATIME_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here
GITHUB_USERNAME=your_username
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id

# Optional
LABS_PATH=~/labs
OBSIDIAN_VAULT_PATH=~/Vault
STORAGE_PATH=~/.local/share/skillops
VERBOSE=false
EOF

chmod 600 ~/.config/skillops/skillops.env
```

### 4. Add to Crontab

Open your crontab editor:

```bash
crontab -e
```

Add one of these lines (choose based on your preference):

#### Basic (no environment file)
```
0 8 * * * /home/username/.local/bin/skillops start >> ~/.local/share/skillops/cron.log 2>&1
```

#### With environment file (recommended)
```
0 8 * * * source ~/.config/skillops/skillops.env && /home/username/.local/bin/skillops start >> ~/.local/share/skillops/cron.log 2>&1
```

#### Daily backup (recommended)
```
30 1 * * * source ~/.config/skillops/skillops.env && /home/username/SkillOps/setup/backup/backup.sh >> ~/.local/share/skillops/backup.log 2>&1
```

#### With error email notifications
```
0 8 * * * source ~/.config/skillops/skillops.env && /home/username/.local/bin/skillops start >> ~/.local/share/skillops/cron.log 2>&1 || echo "SkillOps failed" | mail -s "SkillOps Error" your-email@example.com
```

Replace:
- `8` with your preferred hour (0-23, 24-hour format)
- `/home/username/.local/bin` with output of `which skillops`
- `your-email@example.com` with your email address

### 5. Verify Installation

```bash
crontab -l | grep skillops
```

You should see your cron job listed.

## Cron Schedule Format

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6, 0=Sunday)
│ │ │ │ │
│ │ │ │ │
0 8 * * * command
```

### Common Schedules

| Time | Cron |
|------|------|
| Every day at 8:00 AM | `0 8 * * *` |
| Every day at 9:30 PM | `30 21 * * *` |
| Every weekday at 8:00 AM | `0 8 * * 1-5` |
| Every Monday at 8:00 AM | `0 8 * * 1` |
| Every hour | `0 * * * *` |
| Every 30 minutes | `*/30 * * * *` |
| Every day at 2:00 AM | `0 2 * * *` |

## Usage

### View Your Cron Jobs

```bash
crontab -l
```

### Edit Your Cron Jobs

```bash
crontab -e
```

### View Cron Logs

```bash
# Last 50 lines
tail -50 ~/.local/share/skillops/cron.log

# Follow logs in real-time
tail -f ~/.local/share/skillops/cron.log

# View logs from past 24 hours (macOS/BSD)
tail -f "$(date -d '24 hours ago' +'%Y-%m-%d')" ~/.local/share/skillops/cron.log
```

### Manually Run SkillOps

```bash
# Load environment and run
source ~/.config/skillops/skillops.env && skillops start

# Or with verbose logging
source ~/.config/skillops/skillops.env && skillops start --verbose
```

## Rollback Procedure

1. Restore a backup:
   - `bash setup/backup/restore.sh ~/.local/share/skillops/backups/skillops_YYYYmmdd_HHMMSS.db`
2. Run a quick check:
   - `skillops doctor`

## Troubleshooting

### "command not found: skillops"

The absolute path to `skillops` might be different. Find it:

```bash
which skillops
# Output: /home/username/.local/bin/skillops

# Use full path in crontab:
0 8 * * * /home/username/.local/bin/skillops start >> ~/.local/share/skillops/cron.log 2>&1
```

### "Environment variable not found"

Cron doesn't load your shell configuration (`.bashrc`, `.zshrc`). Always source the environment file:

```bash
0 8 * * * source ~/.config/skillops/skillops.env && skillops start >> ~/.local/share/skillops/cron.log 2>&1
```

### Cron job doesn't run

1. **Verify installation:**
   ```bash
   crontab -l | grep skillops
   ```

2. **Check if cron daemon is running:**
   ```bash
   # macOS/BSD
   launchctl list | grep cron

   # Linux
   systemctl status cron  # or crond
   ```

3. **Test manually:**
   ```bash
   source ~/.config/skillops/skillops.env
   skillops start --verbose
   ```

4. **Check system logs:**
   ```bash
   # macOS
   log stream --predicate 'eventMessage contains "cron"'

   # Linux
   grep CRON /var/log/syslog
   # or
   journalctl -u cron
   ```

### No logs are being written

1. **Check permissions:**
   ```bash
   ls -la ~/.local/share/skillops/
   ```

2. **Create log directory:**
   ```bash
   mkdir -p ~/.local/share/skillops
   touch ~/.local/share/skillops/cron.log
   ```

3. **Check cron syntax:**
   ```bash
   # Make sure you're using >>  (append) not > (overwrite)
   0 8 * * * ... >> ~/.local/share/skillops/cron.log 2>&1
   ```

### Cron job runs but fails silently

Add `--verbose` flag to see debug output:

```bash
0 8 * * * source ~/.config/skillops/skillops.env && skillops start --verbose >> ~/.local/share/skillops/cron.log 2>&1
```

## Advanced Configuration

### Multiple Schedules

Run SkillOps at different times:

```bash
# Morning check
0 8 * * * source ~/.config/skillops/skillops.env && skillops start >> ~/.local/share/skillops/cron.log 2>&1

# Evening reflection
0 20 * * * source ~/.config/skillops/skillops.env && skillops reflect >> ~/.local/share/skillops/cron.log 2>&1
```

### Run Specific Commands

```bash
# Only share (GitHub)
0 8 * * * source ~/.config/skillops/skillops.env && skillops share

# Only notify (Telegram)
30 20 * * * source ~/.config/skillops/skillops.env && skillops notify

# Only create flashcards
0 18 * * * source ~/.config/skillops/skillops.env && skillops create
```

### Email Notifications on Failure

```bash
0 8 * * * source ~/.config/skillops/skillops.env && skillops start >> ~/.local/share/skillops/cron.log 2>&1 || echo "SkillOps failed on $(date)" | mail -s "SkillOps Cron Error" your-email@example.com
```

### Redirect to Syslog (Linux)

```bash
0 8 * * * source ~/.config/skillops/skillops.env && skillops start 2>&1 | logger -t skillops
```

Then view logs:
```bash
tail -f /var/log/syslog | grep skillops
# or
journalctl -t skillops -f
```

## Cron Best Practices

1. **Always use absolute paths:**
   ```bash
   # Bad
   skillops start

   # Good
   /home/username/.local/bin/skillops start
   ```

2. **Source environment files:**
   ```bash
   # Bad
   0 8 * * * skillops start

   # Good
   0 8 * * * source ~/.config/skillops/skillops.env && skillops start
   ```

3. **Log all output:**
   ```bash
   # Bad
   0 8 * * * skillops start

   # Good
   0 8 * * * skillops start >> ~/.local/share/skillops/cron.log 2>&1
   ```

4. **Use >> (append) not > (overwrite):**
   ```bash
   # Bad (overwrites log each time)
   0 8 * * * skillops start > ~/.local/share/skillops/cron.log 2>&1

   # Good (appends to log)
   0 8 * * * skillops start >> ~/.local/share/skillops/cron.log 2>&1
   ```

5. **Redirect stderr to stdout:**
   ```bash
   # Logs both stdout and stderr
   skillops start >> log.txt 2>&1
   ```

## Uninstall

Remove SkillOps from cron:

```bash
crontab -e
# Find and delete the SkillOps line(s)
# Save and exit

# Verify it's removed
crontab -l | grep skillops  # Should show nothing
```

## See Also

- [SETUP_SYSTEMD.md](SETUP_SYSTEMD.md) – Recommended: systemd timers (better logging)
- [QUICKSTART.md](QUICKSTART.md) – Getting started with SkillOps
- [Cron Manual](https://man7.org/linux/man-pages/man5/crontab.5.html)
