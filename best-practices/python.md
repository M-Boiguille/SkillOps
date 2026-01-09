# Python Best Practices

## Code Style

### ✅ Do
- **PEP 8** : Style guide officiel Python
- **Black formatter** : Formatage automatique (pas de débat)
- **Type hints** : `def func(name: str) -> int:`
- **Docstrings** : Google style ou NumPy style
- **Noms explicites** : `calculate_average()` pas `calc()`

### ❌ Don't
- Mélanger snake_case et camelCase
- Lignes > 88 caractères (Black default)
- Variables d'1 lettre (sauf i, j dans boucles courtes)
- Commentaires inutiles : `# increment i`

## Structure Projet

### ✅ Do
```
project/
├── src/
│   └── package/
│       ├── __init__.py
│       └── module.py
├── tests/
│   └── test_module.py
├── requirements.txt
├── setup.py
└── README.md
```

### ❌ Don't
- Tout dans un seul fichier de 2000 lignes
- Import circulaires
- Pas de tests

## Imports

### ✅ Do
```python
# Standard library
import os
import sys

# Third party
import requests
import pytest

# Local
from lms.persistence import StateManager
```

### ❌ Don't
```python
from module import *  # Pollue namespace
import sys, os  # Imports sur même ligne
```

## Error Handling

### ✅ Do
```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
```

### ❌ Don't
```python
try:
    result = risky_operation()
except:  # Catch trop large
    pass  # Silence les erreurs
```

## Tests

### ✅ Do
- **Coverage > 70%** : Viser 80%+
- **Tests unitaires** : 1 test = 1 comportement
- **Mocks** : Pas d'appels API réels dans tests
- **Nommage clair** : `test_calculate_average_with_empty_list`
- **AAA pattern** : Arrange, Act, Assert

### ❌ Don't
- Tests qui dépendent de l'ordre d'exécution
- Tests sans assertions
- Tests qui nécessitent internet

## Performance

### ✅ Do
- **List comprehensions** : `[x*2 for x in range(10)]`
- **Generators** : Pour grandes données
- **`with` statement** : Gestion automatique des ressources
- **f-strings** : Plus rapide que `%` ou `.format()`

### ❌ Don't
- Boucles inutiles : `for i in range(len(list))`
- Concaténation strings en boucle : `s += word`
- Charger 10GB en RAM quand tu peux stream

## Dependencies

### ✅ Do
- **requirements.txt** : Versions fixées `requests==2.31.0`
- **Virtual env** : venv ou conda
- **Audit régulier** : `pip audit` pour vulnérabilités
- **Minimal** : Seulement ce dont tu as besoin

### ❌ Don't
- Installer packages en global
- requirements.txt sans versions
- 50 dépendances pour un projet simple

---

**Outils Recommandés :**
- **Black** : Formatage auto
- **Pylint / Flake8** : Linting
- **Mypy** : Type checking
- **Pytest** : Testing
- **isort** : Tri des imports

**Ressources :**
- [PEP 8](https://peps.python.org/pep-0008/)
- [Real Python](https://realpython.com/)
- [Python Anti-Patterns](https://docs.quantifiedcode.com/python-anti-patterns/)
