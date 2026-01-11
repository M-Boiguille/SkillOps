# Sprint 3 Planning
## SkillOps Learning Management System - Polish & DevOps

**Sprint:** Sprint 3 - User Experience & DevOps Integration
**Duration:** 7 days (12-18 janvier 2026)
**Story Points:** 18 points across 3 user stories
**Status:** 📋 Planning Phase

---

## Sprint Overview

After successfully implementing core features in Sprint 2 (Telegram, Flashcards, GitHub), Sprint 3 focuses on:
1. **User Experience**: Better feedback, error handling, documentation
2. **DevOps Integration**: Cron/systemd automation, monitoring
3. **Reliability**: Integration tests, rollback strategies

### Sprint Objectives
- ✅ All new features have integration tests
- ✅ Users get clear feedback for all operations
- ✅ Errors are informative and actionable
- ✅ Features can run unattended (cron, systemd)
- ✅ Documentation complete and current

---

## User Stories

### US-007: User Experience Polish
**Epic:** Make the tool feel professional and reliable
**Story Points:** 8
**Priority:** HIGH

#### Description
Improve user feedback and error handling across all operations. Users should understand what's happening, why operations fail, and how to fix them.

#### Acceptance Criteria
- ✅ All long operations (share_step) show progress bars
- ✅ All errors have actionable messages
- ✅ --verbose flag provides detailed logging
- ✅ Exit codes reflect success/failure (0 = success, 1+ = error)
- ✅ README updated with all features documented
- ✅ Example .env file provided with comments

#### Tasks

**T007-1: Add Progress Bars & Feedback (2h)**
```python
# Current (bad):
✓ project1: https://github.com/user/project1
✓ project2: https://github.com/user/project2

# Desired (good):
Processing project1...
  [████████████░░] 80% - Pushing to GitHub...
✓ project1: https://github.com/user/project1

Processing project2...
  [██████░░░░░░░░] 40% - Creating GitHub repo...
```

**Files:**
- Modify: `src/lms/steps/share.py`
- Update: Long operations add `rich.Progress`
- Tests: 3 new tests for progress tracking

**Subtasks:**
- Add progress bar during git operations
- Show current operation (git init, git push, etc.)
- Estimate time remaining (if available)

---

**T007-2: Better Error Messages (2h)**
```python
# Current (bad):
[red]Error: {e}[/red]

# Desired (good):
[red]Error: GitHub API returned 401[/red]
[yellow]Hint: Your GITHUB_TOKEN might be expired[/yellow]
[cyan]Solution: Get a new token from https://github.com/settings/tokens[/cyan]
```

**Files:**
- Create: `src/lms/exceptions.py` (custom exceptions)
- Modify: `src/lms/integrations/github_automation.py`
- Modify: `src/lms/integrations/github_detector.py`
- Modify: `src/lms/steps/share.py`
- Tests: 4 new tests for error scenarios

**Implementation:**
```python
# exceptions.py
class GitHubAuthError(Exception):
    """Raised when GitHub authentication fails."""
    def __init__(self, token_type="personal"):
        super().__init__(
            f"GitHub authentication failed\n"
            f"Hint: Your {token_type} token may be invalid\n"
            f"Solution: Get a new token from "
            f"https://github.com/settings/tokens"
        )

class GitHubRepositoryError(Exception):
    """Raised when repository operation fails."""
    pass
```

---

**T007-3: Verbose Logging Support (1.5h)**
```bash
# Normal mode (minimal output):
$ skillops share
Found 3 projects
✓ project1: https://github.com/user/project1
✓ project2: https://github.com/user/project2

# Verbose mode (detailed):
$ skillops share --verbose
[DEBUG] Loading detector...
[DEBUG] Scanned /home/user/labs directory
[DEBUG] Found 3 projects
[DEBUG] Processing: project1
[DEBUG] Generating README...
[DEBUG] [git] Initializing repository at /home/user/labs/project1
[DEBUG] [git] Creating commit: "Initial commit"
[DEBUG] [GitHub API] POST /user/repos (201 Created)
[DEBUG] [git] Adding remote: origin
[DEBUG] [git] Pushing main branch...
✓ project1: https://github.com/user/project1 (12.3s)
```

**Files:**
- Modify: `src/lms/main.py` (add --verbose flag)
- Modify: `src/lms/steps/share.py`
- Modify: All integrations (add logging)
- Tests: 2 new tests

---

**T007-4: Documentation & README Update (1.5h)**
```markdown
# SkillOps - Your Daily Learning Management System

## Features
- 📊 Track daily learning metrics (via WakaTime)
- 📝 Review progress and analytics
- 📚 Create flashcards from Obsidian notes
- 🚀 Share lab projects to GitHub automatically
- 📱 Get daily Telegram notifications

## Installation
```bash
git clone https://github.com/M-Boiguille/SkillOps
cd SkillOps
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Quick Start
```bash
# Copy example environment
cp .env.example .env

# Edit with your tokens
nano .env

# Start the daily routine
skillops start
```

## Features Guide
### 1. Share Lab Projects to GitHub
```bash
export GITHUB_TOKEN=ghp_xxx
export GITHUB_USERNAME=your_username
skillops share
```
...
```

**Files:**
- Modify: `README.md` (complete rewrite with all features)
- Create: `.env.example` with detailed comments
- Create: `docs/QUICKSTART.md` (beginners guide)
- Create: `docs/FEATURES.md` (detailed feature guide)

---

**Estimated Effort:** 8 hours
**Definition of Done:**
- ✅ Progress bars show during share_step
- ✅ All errors have helpful messages
- ✅ --verbose flag works end-to-end
- ✅ README covers all features with examples
- ✅ .env.example has detailed comments
- ✅ All 9 new tests passing
- ✅ 285+ total tests passing

---

### US-008: Integration Tests & Reliability
**Epic:** Verify features work with real APIs
**Story Points:** 6
**Priority:** HIGH

#### Description
Add integration tests that call real APIs (not mocks) to verify behavior. Add rollback/idempotent logic for state changes.

#### Acceptance Criteria
- ✅ Integration tests for GitHub automation (with test token)
- ✅ Integration tests for Telegram notifications (with test bot)
- ✅ All operations are idempotent (safe to retry)
- ✅ Tests run in CI/CD (marked as integration, skip by default)
- ✅ Coverage remains > 90%

#### Tasks

**T008-1: GitHub Integration Tests (2h)**
```python
# tests/integration/test_github_integration.py

@pytest.mark.integration
def test_create_github_repo_real(github_token, tmp_path):
    """Test creating repository with real GitHub API."""
    automation = GitHubAutomation(github_token, "test-user")

    # Create test project
    project_dir = tmp_path / "test_integration_project"
    project_dir.mkdir()

    # Initialize and push
    automation.init_repository(project_dir)
    automation.create_commit(project_dir, "Initial commit")

    repo_info = automation.create_remote_repository(
        f"skillops-test-{uuid4()}",  # Unique name
        "Integration test repo"
    )

    assert repo_info is not None
    assert "html_url" in repo_info

    # Cleanup: Delete repository via API
    # (would need admin token, or skip cleanup for testing)
```

**Files:**
- Create: `tests/integration/test_github_integration.py` (5 tests)
- Create: `tests/integration/conftest.py` (fixtures)
- Modify: `pytest.ini` (mark integration tests)

---

**T008-2: Telegram Integration Tests (1h)**
```python
# tests/integration/test_telegram_integration.py

@pytest.mark.integration
def test_send_telegram_message_real(telegram_token, telegram_chat_id):
    """Test sending message with real Telegram API."""
    client = TelegramClient(telegram_token, telegram_chat_id)

    success = client.send_message("Integration test message ✓")

    assert success is True
```

**Files:**
- Create: `tests/integration/test_telegram_integration.py` (2 tests)

---

**T008-3: Idempotent Operations (2h)**
```python
# Make share_step idempotent (safe to run multiple times)

# Current problem:
# If share_step fails at step 5, running it again fails at step 1
# because README already exists, git already initialized, etc.

# Solution:
# share_step should check state and skip already-done steps
def share_step(...):
    for project_path in projects:
        # Check if already has remote
        if detector.is_new_project(project_path):
            # Only process new projects
            ...

        # Check if README already exists
        if (project_path / "README.md").exists():
            console.print("README already exists, skipping generation")
            continue

        # Check if git already initialized
        if (project_path / ".git").exists():
            console.print("Git already initialized, skipping init")
        else:
            automation.init_repository(project_path)

        # ... rest of steps with similar checks
```

**Files:**
- Modify: `src/lms/integrations/github_automation.py`
- Modify: `src/lms/integrations/github_detector.py`
- Modify: `src/lms/steps/share.py`
- Tests: 3 new tests for idempotent operations

---

**T008-4: CI/CD Integration Tests Job (1h)**
```yaml
# .github/workflows/ci.yml

jobs:
  test:
    # ... existing unit tests

  integration:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    needs: test  # Only run after unit tests pass
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - run: pip install -e .

      - run: |
          pytest tests/integration \
            -v \
            --tb=short \
            -m integration
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TEST_TOKEN }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_TEST_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_TEST_CHAT_ID }}
```

**Files:**
- Modify: `.github/workflows/ci.yml`
- Create: `tests/integration/__init__.py`
- Modify: `pytest.ini` (add integration marker)

---

**Estimated Effort:** 6 hours
**Definition of Done:**
- ✅ 7 integration tests for real APIs
- ✅ All integration tests passing
- ✅ share_step is fully idempotent
- ✅ CI/CD runs integration tests on main branch
- ✅ Coverage remains > 90% (295+ tests)

---

### US-009: DevOps Automation & Monitoring
**Epic:** Run SkillOps unattended
**Story Points:** 4
**Priority:** MEDIUM

#### Description
Enable SkillOps to run automatically via cron or systemd, with monitoring and alerting.

#### Acceptance Criteria
- ✅ Create systemd service file
- ✅ Create cron job templates
- ✅ Logging to syslog for monitoring
- ✅ Health check command (verify all API credentials work)
- ✅ Documentation for setup

#### Tasks

**T009-1: Systemd Service (1h)**
```ini
# /etc/systemd/system/skillops-daily.service

[Unit]
Description=SkillOps Daily Learning Routine
Documentation=https://github.com/M-Boiguille/SkillOps
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=skillops
Environment="PATH=/home/skillops/.venv/bin:/usr/local/bin:/usr/bin"
ExecStart=/home/skillops/.venv/bin/python -m src.lms.main start
StandardOutput=journal
StandardError=journal
SyslogIdentifier=skillops

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/skillops-daily.timer

[Unit]
Description=SkillOps Daily Routine Timer
Requires=skillops-daily.service

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 09:00:00  # Run at 9 AM every day
Unit=skillops-daily.service

[Install]
WantedBy=timers.target
```

**Files:**
- Create: `setup/systemd/skillops-daily.service`
- Create: `setup/systemd/skillops-daily.timer`
- Create: `docs/SETUP_SYSTEMD.md` (installation guide)

---

**T009-2: Cron Job Templates (0.5h)**
```bash
# Cron: Run daily routine at 9 AM
0 9 * * * /home/user/.venv/bin/python -m src.lms.main start >> /var/log/skillops.log 2>&1

# Cron: Send Telegram notification at 8 PM
0 20 * * * /home/user/.venv/bin/python -m src.lms.main notify --respect-schedule >> /var/log/skillops.log 2>&1

# Cron: Share lab projects every Sunday
0 10 * * 0 /home/user/.venv/bin/python -m src.lms.main share >> /var/log/skillops.log 2>&1
```

**Files:**
- Create: `setup/cron/install.sh` (cron setup script)
- Create: `docs/SETUP_CRON.md`

---

**T009-3: Health Check Command (1.5h)**
```bash
$ skillops health

Checking SkillOps configuration...

✓ GITHUB_TOKEN: Valid (expires 2027-01-15)
✓ TELEGRAM_BOT_TOKEN: Valid (bot @SkillOpsBot)
✓ WAKATIME_API_KEY: Valid (user: user123)
✓ Storage directory: /home/user/.skillops (123 MB)
✓ Obsidian vault: /home/user/Obsidian (456 MB)

All checks passed! ✓
```

**Files:**
- Create: `src/lms/commands/health.py` (new command)
- Modify: `src/lms/main.py` (add health command)
- Tests: 3 new tests

**Implementation:**
```python
# health.py
def health_check() -> bool:
    """Verify all API credentials and setup."""
    issues = []

    # Check GitHub token
    if github_token := os.getenv("GITHUB_TOKEN"):
        try:
            headers = {"Authorization": f"token {github_token}"}
            r = requests.get("https://api.github.com/user", headers=headers)
            if r.status_code == 200:
                console.print("✓ GITHUB_TOKEN: Valid")
            else:
                issues.append("GITHUB_TOKEN: Invalid (401 Unauthorized)")
        except Exception as e:
            issues.append(f"GITHUB_TOKEN: {e}")
    else:
        issues.append("GITHUB_TOKEN: Not set")

    # Similar checks for Telegram, WakaTime, storage paths...

    if issues:
        console.print("[red]Issues found:[/red]")
        for issue in issues:
            console.print(f"[red]✗ {issue}[/red]")
        return False

    console.print("[green]All checks passed![/green]")
    return True
```

---

**T009-4: Monitoring & Alerts (1h)**
```bash
# Log to syslog for centralized monitoring
python -m src.lms.main share 2>&1 | logger -t skillops

# View logs
journalctl -u skillops-daily.service -f

# Get alerts if service fails
# (via systemd email notifications or integration with Telegram)
```

**Files:**
- Modify: `src/lms/steps/share.py` (add logging)
- Modify: `src/lms/steps/notify.py` (add logging)
- Create: `docs/MONITORING.md`

---

**Estimated Effort:** 4 hours
**Definition of Done:**
- ✅ Systemd service files created
- ✅ Cron templates provided
- ✅ Health check command works
- ✅ Logging to syslog enabled
- ✅ Documentation complete
- ✅ 3 new tests for health check

---

## Sprint Summary

| Story | Points | Priority | Status |
|-------|--------|----------|--------|
| US-007: UX Polish | 8 | HIGH | 📋 Planning |
| US-008: Integration Tests | 6 | HIGH | 📋 Planning |
| US-009: DevOps Automation | 4 | MEDIUM | 📋 Planning |
| **TOTAL** | **18** | | **📋 Planning** |

---

## Timeline

```
Day 1-2 (Jan 12-13):  US-007 Progress bars & error handling
Day 3-4 (Jan 14-15):  US-007 Documentation & verbose logging
Day 5-6 (Jan 16-17):  US-008 Integration tests & CI/CD
Day 7 (Jan 18):       US-009 Systemd/Cron + health check
                      Testing & documentation
```

---

## Success Criteria

✅ **All user stories completed**
- US-007: 100% (9 new tests, full documentation)
- US-008: 100% (integration tests passing, idempotent operations)
- US-009: 100% (systemd/cron working, health check functional)

✅ **Code Quality**
- Coverage: > 90% (300+ tests)
- Linting: 0 issues
- Type errors: 0

✅ **Documentation**
- README: Complete with all features
- Quick start guide: For new users
- DevOps guide: For automation setup
- API documentation: For integrations

✅ **User Experience**
- Progress bars for long operations
- Clear error messages with solutions
- Health check to verify configuration
- Verbose mode for debugging

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| GitHub API rate limits | Low | Medium | Use test token, batch requests |
| Systemd not on all platforms | Medium | Low | Document cron alternative |
| Integration tests slow | Low | Low | Mark as optional, run on main only |

---

## Post-Sprint Review

After Sprint 3, we'll review:
- User feedback from real usage
- Performance metrics (CLI start time, API response times)
- Coverage metrics (test coverage, code quality)
- Feature completeness vs. user needs

---

## Next Sprint Planning (Sprint 4)

Potential features for future consideration:
- **Web Dashboard** (FastAPI + React for metrics visualization)
- **Multi-user Support** (PostgreSQL migration)
- **Advanced Analytics** (ML-based learning patterns)
- **Mobile App** (React Native)
- **GitHub Copilot Integration** (code review automation)

---

**Document Info:**
- **Created:** 11 janvier 2026
- **Status:** 📋 Planning (Ready to Start)
- **Next:** Sprint 3 Implementation (Jan 12-18)
