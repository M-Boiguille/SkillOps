# KB-08: Testing avec Pytest - Guide Complet

**Date:** 11 janvier 2026
**Catégorie:** Testing & Quality Assurance
**Tags:** #pytest #testing #python #tdd #coverage

---

## Vue d'Ensemble

Pytest est le framework de test Python standard industrie. Ce guide couvre les patterns avancés appris lors de l'implémentation de MetricsManager (99.4% coverage).

---

## Table des Matières

1. [Structure des Tests](#structure-des-tests)
2. [Fixtures et Setup](#fixtures-et-setup)
3. [Patterns de Test](#patterns-de-test)
4. [Coverage et Qualité](#coverage-et-qualité)
5. [Cas Pratique: MetricsManager](#cas-pratique-metricsmanager)

---

## Structure des Tests

### Organisation par Responsabilité

```
tests/
├── lms/
│   ├── __init__.py
│   ├── metrics_manager_test.py    # Tests par classe
│   ├── state_manager_test.py
│   └── progress_manager_test.py
├── integration/
│   ├── test_persistence_flow.py   # Tests end-to-end
│   └── test_api_integrations.py
└── conftest.py                     # Fixtures partagées
```

**Principe:** 1 fichier de test par classe testée, organisé en classes de test par fonctionnalité.

### Nomenclature des Classes de Test

```python
# ✅ Bon: Organisation claire par feature
class TestMetricsManagerInit:
    """Test initialization and configuration."""

class TestLoadMetrics:
    """Test loading metrics from JSON file."""

class TestCalculateStreak:
    """Test streak calculation logic."""
```

**Pattern:** `Test{ClassName}{Feature}` permet de regrouper les tests liés.

---

## Fixtures et Setup

### Fixtures tmp_path

```python
def test_init_with_valid_path(tmp_path):
    """GIVEN a valid file path
    WHEN MetricsManager is initialized
    THEN it should create instance with correct file_path
    """
    metrics_file = tmp_path / "test_metrics.json"
    manager = MetricsManager(metrics_file)

    assert manager.file_path == metrics_file
```

**Avantages:**
- Isolation complète entre tests
- Nettoyage automatique (pytest gère le cleanup)
- Pas de pollution du filesystem

### Fixtures Custom

```python
# conftest.py
import pytest

@pytest.fixture
def sample_progress_data():
    """Fixture providing sample progress data for tests."""
    return [
        {"date": "2026-01-10", "steps": 8, "time": 3.5, "cards": 10},
        {"date": "2026-01-09", "steps": 7, "time": 4.0, "cards": 12},
        {"date": "2026-01-08", "steps": 8, "time": 3.2, "cards": 8}
    ]

# Usage dans test
def test_calculate_streak_consecutive_days(tmp_path, sample_progress_data):
    manager = MetricsManager(tmp_path / "metrics.json")
    streak = manager.calculate_streak(sample_progress_data)
    assert streak == 3
```

---

## Patterns de Test

### Pattern 1: Given-When-Then (Gherkin)

```python
def test_calculate_streak_broken_by_gap(tmp_path):
    """GIVEN progress with a gap in dates (missing day)
    WHEN calculate_streak is called
    THEN streak should stop at the gap (not count before)
    """
    # GIVEN
    today = date.today()
    progress_data = [
        {"date": today.strftime("%Y-%m-%d"), "steps": 8},
        {"date": (today - timedelta(days=1)).strftime("%Y-%m-%d"), "steps": 8},
        # GAP: day-2 missing
        {"date": (today - timedelta(days=3)).strftime("%Y-%m-%d"), "steps": 8}
    ]

    # WHEN
    manager = MetricsManager(tmp_path / "metrics.json")
    streak = manager.calculate_streak(progress_data)

    # THEN
    assert streak == 2  # Stops at gap
```

**Avantages:**
- Documentation du comportement attendu
- Tests lisibles par non-dev
- Trace la spécification (URD/User Stories)

### Pattern 2: Arrange-Act-Assert (AAA)

```python
def test_load_existing_metrics(tmp_path):
    # Arrange
    metrics_file = tmp_path / "metrics.json"
    test_data = {"streak": 15, "avg_time": 3.5, "total_cards": 120}
    metrics_file.write_text(json.dumps(test_data))

    # Act
    manager = MetricsManager(metrics_file)
    loaded = manager.load_metrics()

    # Assert
    assert loaded == test_data
    assert loaded["streak"] == 15
```

**Avantages:**
- Structure claire et prévisible
- Facile à débugger
- Séparation logique du test

### Pattern 3: Parameterized Tests

```python
@pytest.mark.parametrize("input_data,expected", [
    ([], 0.0),                          # Empty list
    ([{"time": 5.0}], 5.0),            # Single entry
    ([{"time": 2.0}, {"time": 4.0}], 3.0),  # Average
])
def test_get_average_time(tmp_path, input_data, expected):
    manager = MetricsManager(tmp_path / "metrics.json")
    result = manager.get_average_time(input_data)
    assert result == expected
```

**Avantages:**
- Teste multiple scenarios en 1 test
- Réduit duplication de code
- Facile d'ajouter cas additionnels

---

## Coverage et Qualité

### Target: >80% Coverage

```bash
# Exécuter tests avec coverage
pytest tests/ --cov=src/lms --cov-report=term-missing

# Voir lignes manquantes
pytest tests/ --cov=src/lms --cov-report=html
open htmlcov/index.html
```

### Calculer Coverage Spécifique

```python
# Script: calculate_coverage.py
import subprocess
import re

result = subprocess.run(
    ["pytest", "--cov=src/lms", "--cov-report=term-missing"],
    capture_output=True, text=True
)

# Parser output pour extraire coverage par classe
# MetricsManager (lines 332-497): 99.4% coverage
```

### Branches Critiques à Tester

1. **Error Handling:**
```python
def test_save_metrics_with_readonly_file(tmp_path):
    """Test IOError raised when file is read-only."""
    metrics_file = tmp_path / "readonly.json"
    metrics_file.write_text('{}')
    metrics_file.chmod(0o444)  # Read-only

    manager = MetricsManager(metrics_file)
    with pytest.raises(IOError, match="Error writing metrics"):
        manager.save_metrics()
```

2. **Edge Cases:**
```python
def test_get_average_time_with_empty_data_explicit(tmp_path):
    """Test count == 0 branch explicitly."""
    manager = MetricsManager(tmp_path / "metrics.json")
    avg = manager.get_average_time([])
    assert avg == 0.0
```

3. **Default Values:**
```python
def test_load_nonexistent_file_returns_default(tmp_path):
    """Test graceful degradation when file missing."""
    metrics_file = tmp_path / "nonexistent.json"
    manager = MetricsManager(metrics_file)
    loaded = manager.load_metrics()
    assert loaded == {"streak": 0, "avg_time": 0.0, "total_cards": 0}
```

---

## Cas Pratique: MetricsManager

### Contexte

Implémentation de MetricsManager avec TDD:
- **Objectif:** 80% coverage minimum (ADR-007)
- **Résultat:** 99.4% coverage (165/166 lignes)
- **Tests:** 41 tests en 11 classes

### Structure des Tests

```python
# 11 classes de test, 41 tests total
TestMetricsManagerInit (3 tests)           # Initialization
TestLoadMetrics (5 tests)                  # Loading logic
TestSaveMetrics (3 tests)                  # Persistence
TestCalculateStreak (6 tests)              # Streak algorithm
TestGetAverageTime (5 tests)               # Averaging
TestGetTotalCards (4 tests)                # Aggregation
TestUpdateMetrics (4 tests)                # Update workflow
TestGetMetricsSummary (2 tests)            # Formatting
TestEdgeCases (5 tests)                    # Edge cases
TestIntegrationWithProgressManager (2)     # Integration
TestErrorHandling (3 tests)                # Exceptions
```

### Tests par Catégorie

**1. Happy Path (70%):**
```python
def test_calculate_streak_consecutive_days(tmp_path):
    """Test normal consecutive days scenario."""
    # Most common usage
```

**2. Edge Cases (20%):**
```python
def test_calculate_streak_unsorted_data(tmp_path):
    """Test algorithm handles unsorted input."""
    # Defensive programming
```

**3. Error Handling (10%):**
```python
def test_save_metrics_with_readonly_file(tmp_path):
    """Test IOError when cannot write."""
    # Robustness
```

### Leçons Apprises

**✅ Ce qui a bien fonctionné:**
1. **TDD strict:** Tests écrits avant implémentation
2. **Given-When-Then:** Docstrings claires et traçabilité
3. **tmp_path:** Isolation complète des tests
4. **Classes par feature:** Organisation claire
5. **Coverage analysis:** Script custom pour coverage par classe

**❌ Pièges évités:**
1. **Pas de shared state:** Chaque test indépendant
2. **Pas de sleep/timeouts:** Tests rapides (0.43s pour 41 tests)
3. **Pas de hardcoded paths:** Utilisation tmp_path
4. **Pas de tests qui modifient files system:** Cleanup auto

### Métriques Finales

```
================================ tests coverage ================================
Name                         Stmts   Miss  Cover
-----------------------------------------------
src/lms/persistence.py         204     80    61%   # Global
  └─ MetricsManager (L332-497)  166      1   99.4% # Target
-----------------------------------------------
TOTAL                          204     80    61%

========================================== 41 passed in 0.43s ==================
```

---

## Configuration Projet

### pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

### Requirements

```txt
pytest==9.0.2
pytest-cov==7.0.0
```

### CI/CD Integration

```yaml
# .github/workflows/ci.yml
- name: Run tests with coverage
  run: |
    pytest tests/ --cov=src/lms --cov-report=xml
    coverage report --fail-under=80
```

---

## Ressources

- [Pytest Documentation](https://docs.pytest.org/)
- [ADR-007: Testing Strategy](../project-lifecycle/03-adr-architecture-decision-records.md#adr-007)
- [Best Practices: Testing](../best-practices/testing.md)

---

**Status:** Production Ready
**Maintenu par:** MB
**Dernière mise à jour:** 11 janvier 2026
