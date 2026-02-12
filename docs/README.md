# Documentation Index

> **SkillOps is production-ready for local single-user DevOps learning.** Use this index to find the right documentation for your needs.

---

## Quick Navigation

### 🚀 Just Getting Started?

**Start here:**
1. [LOCAL_SETUP.md](LOCAL_SETUP.md) — Complete local installation guide (30 mins)
2. [QUICKSTART.md](QUICKSTART.md) — Run your first workflow (5 mins)
3. [README.md](../README.md) — Project overview

---

### 👤 I Want to...

#### Run SkillOps Locally
- [LOCAL_SETUP.md](LOCAL_SETUP.md) — Full installation & configuration
- [DEPLOYMENT.md](DEPLOYMENT.md) — Setup backups & automation

#### Learn About Features
- [FEATURES.md](FEATURES.md) — Detailed feature descriptions
- [README.md](../README.md#-workflow-9-steps) — 9-step workflow overview

#### Use Advanced Features
- [OPERATIONS.md](OPERATIONS.md) — Metrics, retention, chaos operations
- [OBSERVABILITY.md](OBSERVABILITY.md) — Monitoring & logging
- [CHAOS.md](CHAOS.md) — Chaos Monkey testing

#### Secure My Setup
- [SECURITY.md](SECURITY.md) — Secrets, API keys, rotation
- [DEPLOYMENT.md](DEPLOYMENT.md#secrets--configuration-management) — Config management

#### Troubleshoot Issues
- [RUNBOOKS.md](RUNBOOKS.md) — Common problems & solutions
- [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting-deployments) — Deployment issues
- [OPERATIONS.md](OPERATIONS.md#troubleshooting) — Operations issues

#### Backup & Restore Data
- [DEPLOYMENT.md](DEPLOYMENT.md#backup--recovery) — Backup procedures
- [OPERATIONS.md](OPERATIONS.md#backups--recovery) — Daily operations

#### Schedule Automation
- [OPERATIONS.md](OPERATIONS.md#automation) — Cron jobs & systemd timers
- [DEPLOYMENT.md](DEPLOYMENT.md#local-deployment-checklist) — Deployment automation

---

## Documentation Map

### Foundation Documents

| Document | Purpose | Time | Audience |
|----------|---------|------|----------|
| [README.md](../README.md) | Project overview, features, tech stack | 10 min | Everyone |
| [LOCAL_SETUP.md](LOCAL_SETUP.md) | Complete installation & first run | 30 min | New users |
| [QUICKSTART.md](QUICKSTART.md) | 5-minute quick start | 5 min | Impatient users |

### Operations Documents

| Document | Purpose | Time | Audience |
|----------|---------|------|----------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | Local deployment, backups, rollback | 20 min | Operators |
| [OPERATIONS.md](OPERATIONS.md) | Daily operations, metrics, retention | 25 min | Daily users |
| [SECURITY.md](SECURITY.md) | Secrets, API keys, incident response | 20 min | Security-conscious |

### Feature & Advanced Documents

| Document | Purpose | Time | Audience |
|----------|---------|------|----------|
| [FEATURES.md](FEATURES.md) | Detailed feature descriptions | 15 min | Feature users |
| [OBSERVABILITY.md](OBSERVABILITY.md) | Monitoring, logging, metrics | 15 min | Operators |
| [CHAOS.md](CHAOS.md) | Chaos Monkey testing | 10 min | Testers |
| [RUNBOOKS.md](RUNBOOKS.md) | Troubleshooting procedures | 15 min | Troubleshooters |

### Governance & Meta

| Document | Purpose | Time | Audience |
|----------|---------|------|----------|
| [GOVERNANCE.md](GOVERNANCE.md) | Contribution guidelines | 10 min | Contributors |

---

## Common Scenarios

### Scenario 1: "I just cloned the repo"
→ Read: [LOCAL_SETUP.md](LOCAL_SETUP.md) (30 min)

### Scenario 2: "I want to run the workflow now"
→ Read: [QUICKSTART.md](QUICKSTART.md) (5 min)

### Scenario 3: "I want daily backups"
→ Read: [DEPLOYMENT.md](DEPLOYMENT.md#backup--recovery) (5 min)

### Scenario 4: "I lost my data"
→ Read: [DEPLOYMENT.md](DEPLOYMENT.md#disaster-recovery-data-loss) (5 min)

### Scenario 5: "How do I schedule daily reminders?"
→ Read: [OPERATIONS.md](OPERATIONS.md#automation) (5 min)

### Scenario 6: "I forgot my API key"
→ Read: [SECURITY.md](SECURITY.md#retrieve-secrets) (2 min)

### Scenario 7: "Something's broken"
→ Read: [RUNBOOKS.md](RUNBOOKS.md) (varies)

### Scenario 8: "I want to see my metrics"
→ Read: [OBSERVABILITY.md](OBSERVABILITY.md#quick-start) (2 min)

---

## Document Dependency Graph

```
README.md (start here)
    ↓
LOCAL_SETUP.md (installation)
    ↓
┌─────────────────┬──────────────────┬─────────────────┐
│                 │                  │                 │
QUICKSTART.md  DEPLOYMENT.md    OPERATIONS.md    SECURITY.md
                 ↓                   ↓                  ↓
              Backups/Rollback   Metrics/Retention  API Keys
                 ↓                   ↓
            OBSERVABILITY.md     CHAOS.md

FEATURES.md ← QUICKSTART.md
RUNBOOKS.md ← (all docs)
GOVERNANCE.md ← (contributors)
```

---

## Reading Order (Recommended)

### For New Users (1-2 hours)
1. [README.md](../README.md) (10 min) — What is SkillOps?
2. [LOCAL_SETUP.md](LOCAL_SETUP.md) (30 min) — Install it
3. [QUICKSTART.md](QUICKSTART.md) (5 min) — Run it
4. [FEATURES.md](FEATURES.md) (15 min) — Understand features

### For Daily Users (30 min)
1. [OPERATIONS.md](OPERATIONS.md) (25 min) — Daily operations
2. [OBSERVABILITY.md](OBSERVABILITY.md) (5 min) — View metrics

### For Operators (1 hour)
1. [DEPLOYMENT.md](DEPLOYMENT.md) (20 min) — Setup
2. [OPERATIONS.md](OPERATIONS.md) (25 min) — Daily ops
3. [SECURITY.md](SECURITY.md) (15 min) — Secrets

### For Production-Like Setup (2 hours)
1. [LOCAL_SETUP.md](LOCAL_SETUP.md) (30 min)
2. [DEPLOYMENT.md](DEPLOYMENT.md) (20 min)
3. [OPERATIONS.md](OPERATIONS.md) (25 min)
4. [SECURITY.md](SECURITY.md) (20 min)
5. [OBSERVABILITY.md](OBSERVABILITY.md) (15 min)

---

## Feature-Specific Guides

### AI Tutor & On-Call
- [FEATURES.md](FEATURES.md) → "Tutor" and "On-Call" sections
- [SECURITY.md](SECURITY.md) → "Store secrets" (GEMINI_API_KEY)
- [OPERATIONS.md](OPERATIONS.md) → "Incident & Post-Mortem Workflow"

### Metrics & Observability
- [OBSERVABILITY.md](OBSERVABILITY.md) → "Quick Start" and "Metrics Command"
- [OPERATIONS.md](OPERATIONS.md) → "View Daily Metrics"
- [FEATURES.md](FEATURES.md) → "Daily Stand-up"

### Backups & Disaster Recovery
- [DEPLOYMENT.md](DEPLOYMENT.md) → "Backup & Recovery"
- [OPERATIONS.md](OPERATIONS.md) → "Backups & Recovery"
- [DEPLOYMENT.md](DEPLOYMENT.md#disaster-recovery-data-loss) → Data loss scenario

### Automation & Scheduling
- [OPERATIONS.md](OPERATIONS.md) → "Automation" section
- [DEPLOYMENT.md](DEPLOYMENT.md#local-deployment-checklist) → Setup automation

### Secrets & Security
- [SECURITY.md](SECURITY.md) → Complete security guide
- [LOCAL_SETUP.md](LOCAL_SETUP.md) → "Getting API Keys"
- [DEPLOYMENT.md](DEPLOYMENT.md) → "Secrets & Configuration Management"

### Chaos Testing
- [CHAOS.md](CHAOS.md) → Complete chaos guide
- [OPERATIONS.md](OPERATIONS.md) → "Chaos Operations (Local Only)"

---

## API Reference (By Feature)

### Commands

#### Data & Export
- `skillops export --format json|csv`
- `skillops import-data <file>`
- `skillops metrics --hours <N>`
- `skillops retention --days <N> [--vacuum]`

#### Secrets Management
- `skillops secret-set KEY`
- `skillops secret-unset KEY`
- `skillops secret-list`

#### Workflows
- `skillops start [--mode learning|engineering] [--verbose]`
- `skillops oncall [--dry-run]`
- `skillops post-mortem`
- `skillops chaos --level 1|2|3 [--execute] [--allow-dangerous]`

#### System
- `skillops doctor` — Health check
- `skillops health` — Legacy health check
- `skillops version` — Show version
- `skillops notify [--respect-schedule]`
- `skillops migrate` — Migrate from legacy JSON

See [OPERATIONS.md](OPERATIONS.md#daily-operations) and [FEATURES.md](FEATURES.md) for full command reference.

---

## Environment Variables Reference

| Variable | Default | Guide | Purpose |
|----------|---------|-------|---------|
| `SKILLOPS_USE_KEYRING` | `false` | [SECURITY.md](SECURITY.md) | Enable OS keyring |
| `SKILLOPS_STORAGE_PATH` | `~/.local/share/skillops` | [OPERATIONS.md](OPERATIONS.md) | Database location |
| `SKILLOPS_LOG_FORMAT` | `text` | [OBSERVABILITY.md](OBSERVABILITY.md) | Log format (text/json) |
| `SKILLOPS_DAY_START_HOUR` | `4` | [OPERATIONS.md](OPERATIONS.md) | Streak reset hour |
| `SKILLOPS_BACKUP_RETENTION_DAYS` | `14` | [DEPLOYMENT.md](DEPLOYMENT.md) | Backup retention |
| `SKILLOPS_RETENTION_DAYS` | `90` | [OPERATIONS.md](OPERATIONS.md) | Data cleanup window |
| `GEMINI_API_KEY` | - | [LOCAL_SETUP.md](LOCAL_SETUP.md) | Google AI key |
| `WAKATIME_API_KEY` | - | [LOCAL_SETUP.md](LOCAL_SETUP.md) | WakaTime key |
| `GITHUB_TOKEN` | - | [LOCAL_SETUP.md](LOCAL_SETUP.md) | GitHub token |
| `TELEGRAM_BOT_TOKEN` | - | [LOCAL_SETUP.md](LOCAL_SETUP.md) | Telegram bot token |

---

## Troubleshooting by Error

| Error | Guide | Solution |
|-------|-------|----------|
| "ModuleNotFoundError" | [LOCAL_SETUP.md](LOCAL_SETUP.md#troubleshooting) | Reinstall dependencies |
| "Database locked" | [OPERATIONS.md](OPERATIONS.md#troubleshooting) | Kill lingering processes |
| "API key not found" | [SECURITY.md](SECURITY.md) | Set via `secret-set` |
| "Backup failed" | [DEPLOYMENT.md](DEPLOYMENT.md#backup-issues) | Check permissions |
| "Tests failing" | [RUNBOOKS.md](RUNBOOKS.md) | See troubleshooting guide |

---

## Additional Resources

### Project Structure
- [../STRUCTURE.md](../STRUCTURE.md) — Directory structure
- [../IMPLEMENTATION.md](../IMPLEMENTATION.md) — Implementation notes

### Project Lifecycle
- [../project-lifecycle/](../project-lifecycle/) — Product discovery, sprint planning, retrospectives

### Knowledge Base
- [../knowledge-base/](../knowledge-base/) — DevOps concepts, CI/CD, architecture

### Best Practices
- [../best-practices/](../best-practices/) — DevOps, Git, Python, testing

---

## Contact & Support

- 💬 **Questions?** Review the relevant guide above
- 🐛 **Bug report?** [GitHub Issues](https://github.com/M-Boiguille/SkillOps/issues)
- 🔒 **Security issue?** Email maintainer privately (do NOT open public issue)
- 💡 **Feature request?** [GitHub Discussions](https://github.com/M-Boiguille/SkillOps/discussions)

---

## Document Maintenance

**Last Updated:** February 2025

All guides reflect:
- ✅ google-genai==1.62.0 (latest SDK)
- ✅ Database schema v4
- ✅ Production-ready local deployment
- ✅ Keyring-based secrets management
- ✅ AI validation + retry patterns
- ✅ Automated backups + retention
- ✅ Reproducible installs with lockfile

---

**Happy learning! 🚀**
