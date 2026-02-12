# SkillOps 🚀

> Minimal CLI for DevOps learning: train, code, review, quiz + chaos/oncall.

## Overview
SkillOps helps you keep a lightweight daily learning loop with local SQLite tracking, optional AI assistance, and targeted chaos drills.

## Core Commands
- `skillops train <topic>` — quick learning + quiz
- `skillops code` — coding session (passive tracking in Phase 3)
- `skillops review` / `skillops stats` — streak + daily metrics
- `skillops quiz <topic>` — local flashcards (SQLite)
- `skillops chaos` — adaptive chaos templates
- `skillops oncall` — incident simulator
- `skillops post-mortem` — incident write-up
- `skillops notify` — daily Telegram summary

## Quickstart
```bash
git clone https://github.com/M-Boiguille/SkillOps.git
cd SkillOps
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

skillops train kubernetes
skillops code
skillops review
skillops quiz kubernetes
```

## Configuration (optional)
```bash
# AI
GEMINI_API_KEY=your_key

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC
TELEGRAM_CHAT_ID=987654321
TELEGRAM_SCHEDULE_TIME=20:00

# WakaTime (Phase 3)
WAKATIME_API_KEY=waka_xxxxxxxxxxxxx
```

## Documentation
- [docs/CHAOS.md](docs/CHAOS.md)
- [docs/ONCALL_AI.md](docs/ONCALL_AI.md)
- [docs/GOVERNANCE.md](docs/GOVERNANCE.md)
- [docs/GEMINI_API_2026.md](docs/GEMINI_API_2026.md)
