# Project Structure

## Root
```
SkillOps/
├── README.md
├── LICENSE
├── pyproject.toml
├── docs/
└── src/
```

## src/
```
src/lms/
├── commands/            # train, code, review, quiz
├── chaos_templates/     # YAML templates
├── chaos_templates.py   # template logic
├── database.py          # SQLite schema + migrations
├── persistence.py       # data access helpers
├── passive_tracking.py  # Phase 3: WakaTime + git consolidation
├── git_hooks.py         # Phase 3: post-commit hook integration
├── steps/
│   ├── anki.py           # quiz due counts
│   ├── notify.py         # Telegram summary
│   ├── share.py          # GitHub automation (legacy but optional)
│   └── migrate.py        # legacy data importer
└── main.py              # CLI entrypoint
```

## tests/
```
tests/
├── lms/commands/           # command tests
├── lms/steps/              # active step tests
├── lms/test_passive_tracking.py  # Phase 3 tests
└── smoke/                  # CLI smoke tests
```
