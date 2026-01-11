# Best Practices Index

> Guide de référence rapide pour les bonnes pratiques de développement et DevOps.

## 📚 Fiches Disponibles

### [Git](git.md)
Commits, branches, .gitignore, pull requests, historique propre

**Topics :**
- Conventional Commits
- Trunk-based development
- Branch naming
- .gitignore patterns

### [Python](python.md)
Code style, structure projet, tests, performance, dependencies

**Topics :**
- PEP 8 & Black
- Type hints
- Error handling
- Virtual environments

### [DevOps](devops.md)
CI/CD, IaC, secrets, monitoring, containers, deployment

**Topics :**
- Pipeline design
- Infrastructure as Code
- DORA metrics
- Zero-downtime deployments

### [Testing](testing.md)
Test pyramid, unit/integration/E2E, TDD, mocking, coverage

**Topics :**
- AAA pattern
- Test-Driven Development
- Mocking strategies
- Performance testing

---

## 🎯 Quick Reference

### Commit Message
```
<type>(<scope>): <description>

feat(api): add WakaTime client with retry logic
fix(cli): resolve menu navigation bug
docs(readme): update installation instructions
```

### Test Structure (AAA)
```python
def test_function_behavior():
    # Arrange
    input_data = setup_test_data()

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_value
```

### Docker Best Practice
```dockerfile
# Multi-stage build
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY . .
USER 1000
CMD ["python", "main.py"]
```

---

## 📊 Key Metrics to Track

| Metric | Target | Category |
|--------|--------|----------|
| **Test Coverage** | > 70% | Quality |
| **Build Time** | < 10 min | CI/CD |
| **Deployment Frequency** | Daily | DevOps |
| **MTTR** | < 1h | Reliability |
| **Change Failure Rate** | < 15% | Quality |

---

## 🔗 External Resources

- [12 Factor App](https://12factor.net/)
- [DORA Metrics](https://dora.dev/)
- [Python PEP 8](https://peps.python.org/pep-0008/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)

---

**Dernière mise à jour :** 9 janvier 2026
**Projet :** SkillOps LMS
