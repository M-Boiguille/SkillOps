# Testing Best Practices

## Test Pyramid

```
        /\
       /E2E\      <- 10% (Slow, Brittle)
      /------\
     /  INT   \   <- 20% (Medium Speed)
    /----------\
   /   UNIT     \ <- 70% (Fast, Focused)
  /--------------\
```

### ✅ Do
- **70% unit tests** : Rapides, isolés
- **20% integration tests** : Modules ensemble
- **10% E2E tests** : User flows critiques
- **Tests rapides** : Suite complète < 5 min

### ❌ Don't
- Inverse pyramid (90% E2E = lent)
- Tests qui prennent 1h
- Tester uniquement happy path

## Unit Tests

### ✅ Do
- **AAA Pattern** : Arrange, Act, Assert
- **1 test = 1 comportement**
- **Noms descriptifs** : `test_calculate_average_returns_zero_for_empty_list`
- **Mocks** : Isoler le code testé
- **Coverage > 70%** : Viser 80%+

```python
def test_calculate_average_returns_zero_for_empty_list():
    # Arrange
    numbers = []
    
    # Act
    result = calculate_average(numbers)
    
    # Assert
    assert result == 0
```

### ❌ Don't
- Tests sans assertions
- Tests qui dépendent d'ordre d'exécution
- Tests qui modifient state global

## Integration Tests

### ✅ Do
- **Tester interactions** : API + DB, Service A + Service B
- **Fixtures** : Données de test reproductibles
- **Teardown** : Nettoyer après chaque test
- **Isolation** : DB de test séparée

### ❌ Don't
- Tests qui partagent state
- Utiliser prod DB
- Tests qui nécessitent internet

## E2E Tests

### ✅ Do
- **User flows critiques** : Login, checkout, paiement
- **Headless browser** : Playwright, Selenium
- **Attentes explicites** : `wait_for_element()` pas `sleep(5)`
- **Screenshots on failure** : Debug plus facile

### ❌ Don't
- Tester chaque edge case en E2E
- Tests avec timeouts hardcodés
- 500 E2E tests (trop lent)

## TDD (Test-Driven Development)

### ✅ Do
1. **Red** : Écrire test qui échoue
2. **Green** : Code minimal pour passer test
3. **Refactor** : Améliorer code sans casser tests

**Exemple Concret (MetricsManager):**
```python
# Step 1 - RED: Write failing test first
def test_calculate_streak_consecutive_days(tmp_path):
    """Test consecutive days streak calculation."""
    progress_data = [
        {"date": "2026-01-10", "steps": 8},
        {"date": "2026-01-09", "steps": 7},
        {"date": "2026-01-08", "steps": 8}
    ]
    manager = MetricsManager(tmp_path / "metrics.json")
    streak = manager.calculate_streak(progress_data)
    assert streak == 3  # FAILS - method not implemented

# Step 2 - GREEN: Minimal implementation
def calculate_streak(self, progress_data: list) -> int:
    if not progress_data:
        return 0
    return len(progress_data)  # Simple but works

# Step 3 - REFACTOR: Better implementation
def calculate_streak(self, progress_data: list) -> int:
    """Calculate consecutive days from today/yesterday backward."""
    if not progress_data:
        return 0
    
    # Sort by date descending
    sorted_data = sorted(
        progress_data,
        key=lambda x: x["date"],
        reverse=True
    )
    
    # Count consecutive days
    streak = 0
    today = date.today()
    expected_date = today
    
    for entry in sorted_data:
        entry_date = date.fromisoformat(entry["date"])
        if entry_date == expected_date:
            streak += 1
            expected_date -= timedelta(days=1)
        elif entry_date == expected_date + timedelta(days=1):
            # Allow starting from yesterday if no activity today
            streak += 1
            expected_date = entry_date - timedelta(days=1)
        else:
            break  # Gap found, stop counting
    
    return streak
```

**Résultat:** 99.4% coverage (165/166 lignes) avec 41 tests

### ❌ Don't
- Écrire tous les tests d'un coup
- Skipper refactor step
- Tests écrits après code (= pas TDD)

## Mocking

### ✅ Do
```python
def test_fetch_user_data(mocker):
    # Mock external API
    mock_response = {"id": 1, "name": "Alice"}
    mocker.patch('requests.get', return_value=mock_response)
    
    result = fetch_user_data(user_id=1)
    
    assert result["name"] == "Alice"
```

### ❌ Don't
- Appels API réels dans tests
- Over-mocking (tout mocker = test inutile)
- Mocks qui divergent de réalité

## Test Data

### ✅ Do
- **Fixtures** : Données réutilisables
- **Factories** : Générer données de test
- **Anonymisation** : Pas de vraies données users
- **Seed data** : Reproductible

### ❌ Don't
- Données de test hardcodées partout
- Copier prod DB (RGPD!)
- Données qui expirent (dates fixes)

## Coverage

### ✅ Do
- **Objectif 80%+** : Balance entre effort et valeur
- **Branch coverage** : Pas juste line coverage
- **Critical paths 100%** : Paiement, auth, sécurité
- **Ignorer code trivial** : Getters/setters

### ❌ Don't
- Viser 100% sans réfléchir
- Tests inutiles juste pour coverage
- Ignorer warnings de coverage

## Flaky Tests

### ✅ Do
- **Identifier** : Tests qui passent 90% du temps
- **Fixer immédiatement** : Ou supprimer
- **Cause commune** : Race conditions, timeouts, state partagé
- **Retry limité** : Max 3 retries, puis fail

### ❌ Don't
- "Ça passe si je relance" = flaky test
- Ignorer flaky tests
- Augmenter timeout sans comprendre pourquoi

## Performance Testing

### ✅ Do
- **Load tests** : 1000 users simultanés
- **Stress tests** : Jusqu'à breaking point
- **Soak tests** : Performance sur 24h
- **Benchmarks** : Comparer versions

### ❌ Don't
- Tester perf uniquement en dev
- Assumer "ça scale"
- Ignorer memory leaks

---

**Outils Recommandés :**
- **Pytest** : Framework Python
- **Playwright** : E2E testing
- **Locust** : Load testing
- **Coverage.py** : Code coverage
- **pytest-mock** : Mocking

**Ressources :**
- [Test Driven Development](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530)
- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://testingjavascript.com/)
