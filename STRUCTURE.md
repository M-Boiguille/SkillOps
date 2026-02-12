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
├── commands/          # train, code, review, quiz
├── chaos_templates/   # YAML templates
├── chaos_templates.py # template logic
├── database.py        # SQLite schema + migrations
├── persistence.py     # data access helpers
├── steps/
│   ├── anki.py         # quiz due counts
│   ├── notify.py       # Telegram summary
│   ├── share.py        # GitHub automation (legacy but optional)
│   └── migrate.py      # legacy data importer
└── main.py            # CLI entrypoint
```

## tests/
```
tests/
├── lms/commands/      # command tests
├── lms/steps/         # active step tests
└── smoke/             # CLI smoke tests
```
