# KB-09: Python Project Structure Best Practices

**Date:** 11 janvier 2026
**Catégorie:** Python Development
**Tags:** #python #project-structure #packaging #best-practices

---

## Vue d'Ensemble

Guide complet sur la structure d'un projet Python moderne et professionnel, basé sur l'expérience SkillOps.

---

## Structure Recommandée

### Layout Standard (src/ pattern)

```
project-root/
├── src/                         # Source code (importable)
│   ├── __init__.py
│   └── package_name/
│       ├── __init__.py
│       ├── main.py             # Entry point
│       ├── module1.py
│       └── module2.py
├── tests/                       # Tests (mirror src structure)
│   ├── __init__.py
│   └── package_name/
│       ├── test_module1.py
│       └── test_module2.py
├── docs/                        # Documentation
├── .github/                     # CI/CD workflows
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml              # Project metadata (PEP 518)
└── requirements.txt            # Dependencies
```

**Pourquoi src/ ?**
- ✅ Évite imports accidentels depuis root
- ✅ Force utilisation de package installé
- ✅ Meilleure isolation dev/prod
- ✅ Standard moderne (PEP 420)

### Alternative: Flat Layout

```
project-root/
├── package_name/               # Source directly at root
│   ├── __init__.py
│   └── main.py
├── tests/
├── setup.py
└── README.md
```

**Quand utiliser:**
- Projets simples/scripts
- Applications (pas bibliothèques)
- Prototypes rapides

---

## Fichiers de Configuration

### pyproject.toml (Modern Standard)

```toml
[project]
name = "skillops"
version = "0.1.0"
description = "Learning Management System CLI"
authors = [{name = "MB", email = "m.boiguille@example.com"}]
dependencies = [
    "typer>=0.21.1",
    "rich>=14.2.0",
    "PyYAML>=6.0.3"
]
requires-python = ">=3.11"

[project.optional-dependencies]
dev = [
    "pytest>=9.0.2",
    "pytest-cov>=7.0.0",
    "black>=25.0.0",
    "mypy>=1.0.0"
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]

[tool.black]
line-length = 88
target-version = ['py311']

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
```

**Avantages pyproject.toml:**
- ✅ Standard PEP 518 (officiel)
- ✅ Centralise toute la config
- ✅ Remplace setup.py, setup.cfg, pytest.ini
- ✅ Supporté par pip, poetry, hatch

### requirements.txt (Dependency Pinning)

```txt
# Production dependencies
typer==0.21.1
rich==14.2.0
PyYAML==6.0.3

# Dev dependencies (optional)
pytest==9.0.2
pytest-cov==7.0.0
black==25.12.0
```

**Best Practices:**
- Pin versions exactes en prod (`==`)
- Utiliser `>=` pour libraries (flexibilité)
- Séparer dev deps (requirements-dev.txt)
- Générer avec `pip freeze > requirements.txt`

### .gitignore (Python Standard)

```gitignore
# Byte-compiled / optimized
__pycache__/
*.py[cod]
*$py.class

# Testing
.pytest_cache/
.coverage
htmlcov/

# Virtual environments
.venv/
venv/
env/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Project specific
storage/
*.log
.env
```

---

## Virtual Environments

### Création et Activation

```bash
# Créer venv
python -m venv .venv

# Activer (Linux/macOS)
source .venv/bin/activate

# Activer (Windows)
.venv\Scripts\activate

# Vérifier
which python  # Should point to .venv/bin/python
python --version
```

### Best Practices

**✅ Do:**
- Toujours utiliser venv pour projets
- Nom `.venv` (standard moderne)
- Ajouter `.venv/` dans .gitignore
- Requirements.txt pour reproduire

**❌ Don't:**
- Installer globalement (`sudo pip install`)
- Commit venv/ dans Git
- Mélanger plusieurs projets dans 1 venv
- Oublier d'activer venv

---

## Entry Points

### main.py Pattern

```python
# src/lms/main.py
import typer
from pathlib import Path

app = typer.Typer()

@app.command()
def start():
    """Start the LMS routine."""
    typer.echo("Starting SkillOps...")

def main():
    """Entry point for CLI."""
    app()

if __name__ == "__main__":
    main()
```

**Exécution:**
```bash
# Direct
python src/lms/main.py

# Module
python -m src.lms.main

# Installé (via setup.py)
skillops start
```

### setup.py (Entry Points)

```python
from setuptools import setup, find_packages

setup(
    name="skillops",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "skillops=lms.main:main",
        ],
    },
)
```

**Avantages:**
- `skillops` devient commande globale
- Gère automatiquement PYTHONPATH
- Installation: `pip install -e .`

---

## Import Patterns

### Absolute Imports (Recommended)

```python
# ✅ Bon: Clear and explicit
from src.lms.persistence import MetricsManager
from src.lms.state import StateMachine

# ✅ Bon: From package root (if installed)
from lms.persistence import MetricsManager
from lms.state import StateMachine
```

### Relative Imports (Within Package)

```python
# src/lms/cli.py
from . import persistence  # Same level
from .persistence import MetricsManager
from ..utils import helper  # Parent level
```

**Quand utiliser:**
- ✅ À l'intérieur d'un package
- ✅ Code réutilisable (bibliotèque)
- ❌ Scripts standalone
- ❌ Entry points (main.py)

---

## Testing Structure

### Mirror Source Structure

```
src/
└── lms/
    ├── __init__.py
    ├── persistence.py
    └── state.py

tests/
└── lms/
    ├── __init__.py
    ├── test_persistence.py    # Tests for persistence.py
    └── test_state.py          # Tests for state.py
```

### Conftest Pattern

```python
# tests/conftest.py (shared fixtures)
import pytest
from pathlib import Path

@pytest.fixture
def tmp_storage(tmp_path):
    """Create temporary storage directory."""
    storage = tmp_path / "storage"
    storage.mkdir()
    return storage

# tests/lms/test_persistence.py (use fixture)
def test_metrics_manager(tmp_storage):
    metrics_file = tmp_storage / "metrics.json"
    # ...
```

---

## Documentation

### README.md Structure

```markdown
# Project Name

Brief description (1-2 sentences)

## Installation

\`\`\`bash
# Quick start commands
\`\`\`

## Usage

\`\`\`python
# Example code
\`\`\`

## Development

\`\`\`bash
# Setup dev environment
\`\`\`

## Testing

\`\`\`bash
# Run tests
\`\`\`

## License
```

### Docstrings (Google Style)

```python
def calculate_streak(self, progress_data: list) -> int:
    """Calculate consecutive days streak from progress history.

    Counts consecutive days of activity ending today or yesterday.
    Stops at first gap (missing day).

    Args:
        progress_data: List of progress dicts with 'date' field.
                      Format: [{"date": "2026-01-10", ...}, ...]

    Returns:
        Number of consecutive days (int). Returns 0 if no progress.

    Example:
        >>> data = [{"date": "2026-01-10"}, {"date": "2026-01-09"}]
        >>> manager.calculate_streak(data)
        2
    """
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: pytest tests/ --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Migration: Flat → src/

### Étapes

1. **Créer structure src/**
```bash
mkdir -p src
mv package_name src/
```

2. **Mettre à jour imports**
```python
# Avant
from package_name.module import func

# Après
from src.package_name.module import func
```

3. **Mettre à jour pyproject.toml**
```toml
[tool.pytest.ini_options]
pythonpath = ["."]  # Permet pytest de trouver src/
```

4. **Vérifier tests**
```bash
pytest tests/ -v
```

---

## Checklist Projet

**Structure:**
- [ ] src/ ou flat layout choisi consciemment
- [ ] tests/ mirror src/ structure
- [ ] .gitignore complet
- [ ] README.md avec installation guide

**Configuration:**
- [ ] pyproject.toml avec dependencies
- [ ] requirements.txt pinned versions
- [ ] .venv/ créé et activé

**Quality:**
- [ ] Tests coverage > 80%
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Linting (black, mypy)

**Documentation:**
- [ ] Docstrings Google style
- [ ] README avec exemples
- [ ] CHANGELOG pour versions

---

## Ressources

- [Python Packaging Guide](https://packaging.python.org/)
- [PEP 518 - pyproject.toml](https://peps.python.org/pep-0518/)
- [SkillOps README](../README.md)

---

**Status:** Production Ready
**Maintenu par:** MB
**Dernière mise à jour:** 11 janvier 2026
