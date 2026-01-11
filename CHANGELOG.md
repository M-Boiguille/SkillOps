# Changelog

All notable changes to SkillOps will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.3.0] - 2026-01-12

### Added

#### Operational Enhancements (US-009)
- **Systemd Integration** (US-009-1):
  - `setup/systemd/skillops.service`: systemd service unit with resource limits
    - User-level installation support (%i variable for username)
    - Automatic restart on failure (300s delay)
    - Memory limit (512MB) and CPU quota (50%)
  - `setup/systemd/skillops.timer`: systemd timer unit for daily scheduling
    - Daily execution at 8:00 AM (customizable)
    - Automatic execution on boot if missed
    - Random delay (0-5 min) to prevent thundering herd
  - `docs/SETUP_SYSTEMD.md`: 348-line comprehensive guide
    - Installation (6 steps with example commands)
    - Configuration (environment variables, custom schedules)
    - Usage (status, logs, manual runs via systemctl)
    - Troubleshooting (10+ common issues)
    - Advanced options (multiple timers, resource limits, notifications)

- **Cron Job Integration** (US-009-2):
  - `setup/cron/install.sh`: Interactive bash installer (300+ lines)
    - Color-coded output and menu interface
    - Automatic requirement checking (crontab, skillops command)
    - Interactive schedule configuration (time/frequency)
    - Email notification setup (success/failure)
    - Environment file handling (.env sourcing)
    - Crontab manipulation (add, verify, uninstall)
    - Manual configuration help and documentation
  - `docs/SETUP_CRON.md`: 661-line comprehensive guide
    - Quick start (automated installer, 4-step setup)
    - Manual setup (copy-paste commands)
    - Cron schedule format with table of examples
    - Troubleshooting (command not found, env vars, permissions, logs)
    - Advanced options (multiple jobs, syslog integration)
    - Best practices (logging, email notifications)

- **Health Check Command** (US-009-3):
  - `skillops health`: New CLI command to validate configuration
  - `src/lms/commands/health.py`: Comprehensive health check module
    - `check_api_token()`: Verifies required API tokens (WakaTime, Gemini, GitHub, Telegram)
    - `check_github_token()`: Authenticates with GitHub API, displays authenticated user
    - `check_telegram_token()`: Validates Telegram bot token, displays bot name
    - `check_directory()`: Verifies storage/labs directories exist (with defaults)
    - `health_check()`: Orchestrates all checks with rich formatted output
    - Graceful error handling for network issues
  - Rich formatted output with green/yellow/red status indicators
  - Detailed error messages for quick troubleshooting

### Changed
- Updated CLI version string to "v0.2.0 (Sprint 2 Complete)"
- Integrated health check into main.py as new CLI command

### Testing
- Added `tests/lms/commands/health_test.py`: 19 comprehensive tests
  - Valid configuration scenarios (all checks pass)
  - Missing credentials handling (graceful fallback)
  - Missing directories handling (fallback to defaults)
  - Network error handling (requests.RequestException)
  - Mocked API calls (GitHub, Telegram)
  - File system operations (pathlib mocking)
- All 353 tests passing (334 previous + 19 new health tests)
- Pre-commit hooks validated (black, flake8, mypy)

---

## [0.2.0] - 2026-01-11

### Added

#### UX & Error Handling (US-007)
- **Progress Bars**: `share_step()` now displays rich progress bars for git operations (init, commit, push)
- **Custom Exceptions**: 8 custom exception classes with helpful error messages and hints:
  - `SkillOpsError` (base)
  - `GitHubAuthError`, `GitHubRepositoryError`, `GitHubPushError`
  - `TelegramError`, `ObsidianError`, `AnkiError`, `WakaTimeError`, `GeminiError`
- **Verbose Logging**: `--verbose` flag added to `start`, `notify`, and `share` commands with debug logs throughout integrations
- **Documentation Overhaul**:
  - Complete README rewrite
  - New QUICKSTART.md guide
  - New FEATURES.md listing all capabilities
  - Enhanced .env.example with detailed comments

#### Testing & Integration (US-008)
- **GitHub Integration Tests**: 5 live integration tests hitting real GitHub API
  - Repository creation and URL handling
  - Duplicate repository handling
  - Private repository flag
  - Authenticated user matching
  - Invalid token rejection
- **Telegram Integration Tests**: 2 live integration tests hitting real Telegram API
  - `getMe()` endpoint verification
  - `sendMessage()` delivery confirmation
- **Idempotent Operations**: All core steps now safe to run multiple times
  - `share_step()`: Checks if remote repository exists before creation
  - `create_step()`: Skips deck generation if content unchanged (hash-based)
  - `notify_step()`: Only sends one notification per calendar day (marker file)
- **CI/CD Integration**: GitHub Actions workflow updated to run integration tests
  - Only on main branch pushes (not PRs)
  - Optional step with continue-on-error (doesn't block CI)
  - Credentials passed via GitHub Secrets

### Changed
- Enhanced `GitHubAutomation` class with `repository_exists()` method
- Improved `create_step()` hash checking logic (pre-loads existing hashes)
- `notify_step()` now uses `.notify_sent` marker for daily deduplication
- CI pipeline now includes integration test job after unit tests

### Fixed
- Mock in `test_share_step_with_new_project` now includes `repository_exists.return_value = False`

### Test Coverage
- **Total Tests**: 334 passing, 7 skipped
- **New Tests**: +4 new tests for idempotent operations
- **Integration Tests**: 7 live API tests (skip gracefully when creds unavailable)

---

## [0.1.0] - 2026-01-09

### Added

#### Core Features
- **8-Step Learning Workflow**:
  1. REVIEW_METRICS - Review coding metrics from WakaTime
  2. FORMATION - Study AI-generated learning materials
  3. ANALYSIS - Analyze patterns and gaps
  4. REINFORCE - Reinforce learning with spaced repetition
  5. ZETTELKASTEN - Create Zettelkasten notes
  6. FLASHCARDS - Generate flashcards from Obsidian vault
  7. PORTFOLIO - Share projects to GitHub
  8. REFLECTION - Daily reflection and planning

#### API Integrations
- **WakaTime**: Fetch coding metrics (language, time, projects)
- **Gemini**: AI-powered learning content generation
- **GitHub**: Repository creation and management
- **Telegram**: Daily progress notifications
- **Obsidian**: Vault scanning for flashcard extraction
- **Anki**: Flashcard deck generation

#### CLI & UX
- Typer-based CLI with rich formatting
- Rich console output (colors, tables, progress bars)
- Interactive menus with Inquirer
- Comprehensive help documentation

#### Data Persistence
- JSON/YAML local storage
- Session-based state management
- Progress history tracking
- Deduplication via hash comparison

#### Testing
- 327 passing unit tests
- Mock-based integration tests
- Full test coverage reporting
- Pre-commit hooks (black, flake8, mypy)

#### CI/CD
- GitHub Actions pipeline
- Automated testing on push/PR
- Code formatting enforcement
- Type checking (mypy)
- Security scanning (bandit, safety)

#### Documentation
- Comprehensive README
- Architecture Decision Records (ADRs)
- Sprint planning documents
- Setup and configuration guides

---

## How to Upgrade

### From 0.1.0 to 0.2.0

```bash
pip install --upgrade skillops
```

No breaking changes. All new features are additive.

**Key Improvements:**
- Better error messages (read error messages carefully—they provide solutions)
- Use `--verbose` flag for debugging: `skillops start --verbose`
- Integration tests now run in CI (watch GitHub Actions for live test results)
- Idempotent operations: safe to run tasks multiple times without issues

---

## Known Limitations

- Integration tests require API credentials (configured as GitHub Secrets for CI)
- Telegram notifications limited by bot rate limits
- GitHub API has standard rate limits (5000 req/hour for authenticated requests)

---

## Roadmap

### v0.3.0 (Operational)
- Systemd service files for scheduled daily runs
- Cron job templates and installation script
- Health check command (`skillops health`)
- Monitoring and alerting integration

### v0.4.0 (Enhanced)
- Dashboard web interface (FastAPI + React)
- Database backend (PostgreSQL migration path)
- Multi-user support
- Advanced analytics and reporting

### v1.0.0 (Production)
- Stable API
- Comprehensive documentation
- Performance optimization
- Docker containerization

---

## Support

For issues, feature requests, or questions:
- Check [QUICKSTART.md](docs/QUICKSTART.md) for common issues
- Review error messages (they include helpful hints)
- Use `--verbose` flag to enable debug logging
- Check [FEATURES.md](docs/FEATURES.md) for capability overview

---

**SkillOps v0.2.0**: Robust, tested, and ready for daily use.
