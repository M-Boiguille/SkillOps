# Changelog

All notable changes to SkillOps will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
