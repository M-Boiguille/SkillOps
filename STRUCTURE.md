# Project Structure and Maintenance Guide

## Overview

SkillOps is a Learning Management System for DevOps training with a full automated test suite and YAML exercise/mission catalogs.

## Directory Organization

### Root Level
```
SkillOps/
├── README.md                      # Main project documentation
├── LICENSE                        # MIT License
├── pyproject.toml                 # Python project configuration
├── IMPLEMENTATION.md              # Implementation notes (Mission Control & Reinforce)
├── CHANGELOG.md                   # Version history and changes
├── docs/                          # User-facing guides (Quickstart, Features, Ops)
└── STRUCTURE.md                   # This file - navigation guide
```

### src/ - Production Code
```
src/lms/                          # Main application
├── data/
│   └── exercises_catalog.yaml     # 105 exercises in YAML format
├── steps/
│   ├── __init__.py
│   ├── anki.py                   # Anki review (AnkiConnect)
│   ├── create.py                 # Flashcard generation
│   ├── missions.py               # Mission Control
│   ├── read.py                   # Reading & notes
│   ├── reflection.py             # Daily reflection
│   ├── reinforce.py              # Practice exercises
│   ├── review.py                 # Daily stand-up metrics
│   ├── share.py                  # Portfolio automation
│   ├── tutor.py                  # AI Q&A
│   └── ...
├── classes/
├── utils/
└── cli.py                        # CLI entry point
```

### tests/ - Automated Tests
```
tests/
├── lms/
│   ├── steps/
│   ├── integrations/
│   ├── monitoring/
│   └── ...
└── integration/
```

### .skillopsvault/ - Obsidian Vault Content
Learning resources in Markdown format for Obsidian integration.
```
.skillopsvault/
├── Docker Basics.md              # Docker fundamentals
├── Kubernetes Basics.md           # K8s architecture & YAML
├── Terraform Infrastructure as Code.md
├── Git Version Control.md         # Git workflows
├── Linux Command Line Essentials.md
├── AWS Cloud Fundamentals.md      # EC2, S3, RDS, VPC, Lambda
├── CI-CD with GitLab.md          # Pipelines, runners, security
└── Ansible Automation.md          # Playbooks, roles, vaults
```

### .personal-notes/ - Development Notes (Internal Use)
Temporary documentation, research, and development notes.

```
.personal-notes/
├── _template.md                  # Template for new notes
├── devops_katas_250_complete.md  # Full kata source (250 exercises)
├── katas_96_145_instructions.md  # Integration instructions for katas 96-145
├── issue-us-*/                   # Issue tracking notes
├── session-*/                    # Development session summaries
├── release-v*.md                 # Release planning notes
└── python/                       # Python-specific learnings
    ├── exception-handling-*.md
    ├── tests-*.md
    └── ...
```

**Note**: `.personal-notes/` is NOT part of production deployment. It's for development reference only.

## Key Files Explained

### exercises_catalog.yaml
**Purpose**: Central repository of all 105 exercises
**Size**: 1,985 lines
**Format**: YAML with structured metadata per exercise
**Content**:
- IDs 1-10: Original exercises (Docker, Kubernetes, Terraform, AWS, GitLab CI)
- IDs 11-105: 95 katas integrated from DevOps training collection

**Structure per exercise**:
```yaml
- id: 11
  key: kata-001
  title: List files and navigate
  primary_domain: Linux
  description: Learning objective description
  secondary_domains: [CLI, System Administration]
  difficulty: Débutant
  estimated_time: 15min
  prerequisites: [Terminal/CLI knowledge]
  learning_objectives: [Objective 1, Objective 2]
  tags: [linux, devops, kata]
```

### reinforce.py
**Purpose**: Main exercise selection and execution module
**Size**: 552 lines
**Key Functions**:
- `get_available_domains()` - Returns 6 primary domains
- `_load_exercises_catalog()` - Loads YAML catalog
- `reinforce_step()` - Interactive menu with smart sorting
- `get_exercise_completion_count()` - Progress tracking

**Recent Changes** (v1.0.0):
- Removed hardcoded exercises system
- Implemented `inquirer.List()` for interactive menu
- Added tri-level sorting: completion → difficulty → ID
- Added visual completion indicators `[✓×N]`

### reinforcetest.py
**Purpose**: Unit tests for reinforce module
**Size**: 523 lines
**Tests**: 21 tests, all passing (100%)
**Coverage**: ~92% of reinforce.py
**Key Areas**:
- Menu rendering and sorting
- Completion indicator display
- ESC/exit handling
- Empty catalog graceful failure

## Development Workflow

### Running Tests
```bash
# All tests
pytest -v
# Result: 539/539 PASSED ✅

# Just reinforce tests
pytest tests/lms/steps/reinforce_test.py -v
# Result: 21/21 PASSED ✅

# With coverage
pytest --cov=src/lms/steps/reinforce tests/lms/steps/reinforce_test.py
# Coverage: ~92%
```

### Adding New Exercises
1. Edit `src/lms/data/exercises_catalog.yaml`
2. Add entry with all required fields (id, key, title, etc.)
3. Increment ID (next would be 106 after kata-095)
4. Run tests to verify parsing: `pytest -v`

### Creating Development Notes
1. Use `.personal-notes/_template.md` as template
2. Save with clear naming: `issue-us-NNN-desc.md` or `session-YYYY-MM-DD.md`
3. These are for reference only, not deployed

## Git Workflow

### Committing Changes
```bash
# Stage all changes
git add .

# Commit with clear message
git commit -m "feat: improve reinforce menu

- Replace hardcoded exercises with catalog system
- Add inquirer.List() for vim-style navigation
- Implement tri-level sorting (completion/difficulty/ID)
- Add visual [✓×N] indicators
- All tests passing"

# Push to remote
git push origin main
```

### Branching Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: New features
- `fix/*`: Bug fixes
- `docs/*`: Documentation updates

## Storage
- Progress tracking: SQLite (skillops.db)
- Optional exports: JSON/CSV via `skillops export`
- Exercise cache: Versioned per completion level
- Storage path: `./storage/` (default, configurable via STORAGE_PATH)

## Testing Strategy

### Test Categories
1. **Unit Tests** (see `pytest -v` for current totals)
   - Individual function tests
   - Mocked dependencies
   - Fast execution (<5s)

2. **Integration Tests**
   - End-to-end menu flows
   - Progress tracking
   - Catalog loading



## Dependencies

### Core
- Python 3.12.3
- inquirer >= 9.0.0
- PyYAML >= 6.0
- rich >= 13.0

### Testing
- pytest >= 9.0.2
- pytest-cov >= 4.0

### Optional
- Obsidian (for vault viewing)
- Docker (for container-based testing)

## Common Tasks

### Debug Menu Sorting
```bash
python -c "
from src.lms.steps.reinforce import _load_exercises_catalog
exercises = _load_exercises_catalog()
for ex in exercises[:5]:
    print(f'{ex[\"id\"]}: {ex[\"title\"]} ({ex.get(\"difficulty\", \"?\")})' )
"
```

### Add New Domain
1. Update `exercises_catalog.yaml` entries with new domain
2. Update `get_available_domains()` return list
3. Update tests to verify domain appears in list
4. Add vault note if learning resource needed

### Fix Failing Test
1. Identify test: `pytest -v tests/lms/steps/reinforce_test.py::test_name`
2. Run with verbose: `pytest -vvv test_name`
3. Check mock format matches actual menu display
4. Verify all mock fields present (or update test expectations)

## Documentation Map

| Document | Purpose | Audience |
|----------|---------|----------|
| README.md | Project overview, quick start | Everyone |
| IMPLEMENTATION.md | Technical architecture, API docs | Developers |
| CHANGELOG.md | Version history, migration guides | Developers, Users |
| STRUCTURE.md | This file - directory navigation | Developers |
| .skillopsvault/*.md | Learning resources | Users |
| .personal-notes/ | Dev notes (not deployed) | Team |

---

**Last Updated**: 10 février 2026
**Maintained By**: Project maintainers
**Next Review**: After next release
