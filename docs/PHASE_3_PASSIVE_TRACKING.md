# Phase 3: Passive Code Tracking

**Status:** ✅ **IMPLEMENTED**
**Date:** 12 février 2026

## Overview

Phase 3 introduces passive, automated tracking of coding activity through two complementary mechanisms:

1. **Git Hooks** - Automatically records commit metadata on every git commit
2. **WakaTime Integration** - Passive time tracking when WAKATIME_API_KEY is configured

This phase requires **no explicit user interaction** beyond normal development workflow.

## Features Implemented

### 1. Git Hooks for Commit Tracking

Automatically installs a post-commit hook that records:
- Commit hash and timestamp
- Commit message
- Files changed
- Lines added/deleted

```bash
# Hook installed automatically on first `skillops code` run
# Stored in: .git/hooks/post-commit

# Data recorded to SQLite table: code_sessions
```

### 2. WakaTime API Integration

When `WAKATIME_API_KEY` is set, collects:
- Total coding time for the day
- Language breakdown
- Top projects worked on
- Editor/IDE breakdown

```python
# Set in .env:
WAKATIME_API_KEY=waka_xxxxx

# Data source: https://wakatime.com/api/v1/users/current/summaries
```

### 3. Consolidated Daily Metrics

Combines git + WakaTime data into a unified view:

```bash
$ skillops code

Code - Passive Tracking (Phase 3)

     Today's Coding Activity
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Metric          ┃ Value     ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ 💻 WakaTime     │ 2h 15m    │
│ 🔤 Languages    │ Python 80%│
│ 📦 Commits      │ 5         │
│ 📝 Files        │ 12        │
│ ➕ Lines Added  │ 245       │
│ ➖ Lines Deleted│ 67        │
│ ⚡ Activity     │ High      │
└─────────────────┴───────────┘
```

### 4. Activity Level Assessment

Automatically categorizes daily activity as:
- **inactive** - No commits or time tracked
- **low** - <30 min or <3 commits
- **moderate** - <1 hour or <10 commits
- **high** - ≥1 hour and ≥10 commits

## Database Schema (v7)

### `code_sessions` Table
Stores individual commit records:

```sql
CREATE TABLE code_sessions (
    id INTEGER PRIMARY KEY,
    commit_hash TEXT UNIQUE NOT NULL,
    commit_time TEXT NOT NULL,
    commit_msg TEXT,
    files_changed INTEGER,
    lines_added INTEGER,
    lines_deleted INTEGER,
    recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
    date TEXT NOT NULL
);
```

### `tracking_summary` Table
Stores daily consolidated metrics:

```sql
CREATE TABLE tracking_summary (
    id INTEGER PRIMARY KEY,
    date TEXT UNIQUE NOT NULL,
    wakatime_seconds INTEGER DEFAULT 0,
    git_commits INTEGER DEFAULT 0,
    git_files_changed INTEGER DEFAULT 0,
    git_lines_added INTEGER DEFAULT 0,
    git_lines_deleted INTEGER DEFAULT 0,
    activity_level TEXT,
    recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## Usage

### Run Daily Metrics Command

```bash
skillops code
```

Shows consolidated activity metrics for today.

### Review Historical Tracking

```python
from src.lms.passive_tracking import get_tracking_summary

# Get summary for specific date
summary = get_tracking_summary(date_str="2026-02-12")
print(summary)
# {
#   'date': '2026-02-12',
#   'wakatime_seconds': 8100,
#   'git_commits': 5,
#   'git_files_changed': 12,
#   'git_lines_added': 245,
#   'git_lines_deleted': 67,
#   'activity_level': 'high'
# }
```

### Manual Commit Recording

```python
from src.lms.git_hooks import record_commit_to_db

# Record a commit programmatically
record_commit_to_db(
    commit_hash="abc123def456",
    commit_time="2026-02-12T10:30:00Z",
    commit_msg="Implement feature X",
    files_changed=3,
    lines_added=45,
    lines_deleted=12,
    storage_path=None  # Optional: custom storage dir
)
```

## Configuration

### .env Settings

```bash
# Optional: WakaTime API key for time tracking
WAKATIME_API_KEY=waka_xxxxxxxxxxxxxxxxxxxxx

# Storage directory (default: storage/)
STORAGE_PATH=storage

# Logical day start hour (default: 4 = 4 AM)
SKILLOPS_DAY_START_HOUR=4
```

### Getting WakaTime API Key

1. Sign up at https://wakatime.com
2. Go to Settings → Account
3. Copy your API Key
4. Add to `.env`: `WAKATIME_API_KEY=waka_xxx`

## Implementation Details

### Git Hook Installation

The hook is installed automatically when `skillops code` is first run:

```bash
# Hook path: .git/hooks/post-commit
# Language: Bash + Python integration
# Execution: After every git commit (non-blocking)
# Fallback: Silent fail if Python/sqlite unavailable
```

### Data Flow

```
git commit
    ↓
post-commit hook
    ↓
Extract commit metadata (hash, timestamp, msg, stats)
    ↓
Python: src.lms.git_hooks.record_commit_to_db()
    ↓
SQLite: code_sessions table
    ↓
Daily consolidation → tracking_summary table
```

### WakaTime Integration

```
skillops code
    ↓
collect_daily_tracking_data()
    ↓
Try: WakaTimeClient().get_today_stats()
    ↓
If available:
  - Query: /users/current/summaries?range=Today
  - Parse: languages, projects, editors, total_seconds
    ↓
If not available:
  - Continue with git data only
    ↓
Merge data + store in tracking_summary
```

## Testing

All Phase 3 features include comprehensive tests:

```bash
pytest tests/lms/test_passive_tracking.py -v

# Test coverage includes:
# - Git hook installation
# - Commit recording
# - Metrics calculation
# - WakaTime data merging
# - Activity level estimation
# - Database schema migration
```

**15 tests, all passing ✅**

## Privacy & Security

### Data Stored Locally

All code tracking data is stored in local SQLite database (`storage/skillops.db`):
- Commits are only recorded in your local repository
- No data sent anywhere except (optionally) to WakaTime for time tracking
- WakaTime integration is optional (can be disabled by not setting WAKATIME_API_KEY)

### No External Dependencies

Git hook runs entirely locally:
- No API calls required
- No network requests
- No third-party services (except optional WakaTime)

## Roadmap: Phase 4

Phase 4 will add:
- **TUI Dashboard** - Rich terminal UI for viewing metrics
- **Historical Analytics** - Trends over time
- **Adaptive Learning** - Suggest focus areas based on activity patterns
- **Integration Metrics** - Combine with training/quiz completion

## Troubleshooting

### Git Hook Not Recording Commits

**Problem:** Commits recorded but appear in SQLite

```bash
# Check hook exists and is executable
ls -la .git/hooks/post-commit

# Should show:
# -rwxr-xr-x  1 user  group  500 Feb 12 10:30 post-commit
```

**Solution:** Reinstall hook

```bash
python -c "from src.lms.git_hooks import install_post_commit_hook; install_post_commit_hook()"
```

### WakaTime Data Not Showing

**Problem:** Only git commits shown, no WakaTime stats

```bash
# Check API key set
grep WAKATIME_API_KEY .env

# Test WakaTime API
python -c "
from src.lms.api_clients.wakatime_client import WakaTimeClient
c = WakaTimeClient()
print(c.get_today_stats())
"
```

**Solution:** Verify API key is valid at https://wakatime.com/settings/account

## Summary

Phase 3 completes passive code tracking, enabling SkillOps to automatically measure daily coding activity through:

✅ Git commit tracking (local)
✅ WakaTime time tracking (optional)
✅ Consolidated daily metrics
✅ Activity level assessment
✅ 15 comprehensive tests
✅ Zero-config git hook installation
✅ Privacy-first data storage

**Next:** Phase 4 - TUI Dashboard & Analytics
