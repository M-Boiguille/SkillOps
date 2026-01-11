# Guide de Test - SkillOps LMS

Date: 11 janvier 2026
Sprint: 1 (Complet - 11/11 issues)

## 📊 État des Tests

### Tests Automatisés
```bash
# Résultats actuels
Total: 216 tests
✅ Passing: 205 (95%)
❌ Failing: 11 (5%)

# Couverture
Coverage: 98-100% sur les nouveaux modules
```

### Échecs Connus
- **reinforce_test.py** (8 tests) : Refactoring ProgressManager → JSON storage
- **review_test.py** (3 tests) : Type hints list vs dict

## 🧪 Tests Manuels - Comment Tester l'Application

### 1. Tester le CLI (Commandes de Base)

```bash
cd /home/mb/Documents/code/SkillOps

# Afficher l'aide
python skillops.py --help

# Afficher la version
python skillops.py version

# Démarrer le menu interactif
python skillops.py start
```

**Comportement attendu :**
- Help : Affiche 2 commandes (start, version)
- Version : "SkillOps LMS v0.1.0 (Sprint 1 MVP)"
- Start : Menu interactif avec 8 étapes + Quit

### 2. Tester le Menu Principal

```bash
python skillops.py start
```

**Vérifications :**
1. ✅ Header avec titre et date affichés
2. ✅ 9 options affichées :
   - 📊 Review (Yesterday's Metrics)
   - ⏱️ Formation (WakaTime Tracking)
   - 🧠 Analysis (AI Q&A)
   - 💪 Reinforce (Practice Exercises)
   - 📝 Zettelkasten (Note Taking)
   - 🎴 Learn Flashcards (Anki)
   - 🔄 Share (GitHub Portfolio)
   - 📱 Notify (Telegram Summary)
   - ❌ Quit
3. ✅ **Navigation avec :**
   - Flèches haut/bas (↑↓)
   - **Touches Vim : `j` (bas) / `k` (haut)**
4. ✅ Entrée pour sélectionner
5. ✅ Ctrl+C pour quitter

### 3. Tester l'Étape Review (sans données)

```bash
python skillops.py start
# Sélectionner "Review Metrics"
```

**Comportement attendu :**
```
📊 Review - Yesterday's Metrics

Date: 10 janvier 2026

No data found for [date]
Complete some steps today to see them tomorrow!
```

**Retour au menu** après affichage.

### 4. Tester l'Étape Formation (sans WakaTime API key)

```bash
python skillops.py start
# Sélectionner "Formation Tracking"
```

**Comportement attendu :**
```
⏱️ Formation - WakaTime Tracking

❌ Error: API Key Not Found

WAKATIME_API_KEY not found in environment.
Please set it in .env file or export it:
  export WAKATIME_API_KEY=waka_xxxxx

See .env.example for configuration template.
```

### 5. Tester l'Étape Formation (AVEC WakaTime API key)

```bash
# Créer un fichier .env
cat > .env << EOF
WAKATIME_API_KEY=waka_votre_clé_ici
EOF

python skillops.py start
# Sélectionner "Formation Tracking"
```

**Comportement attendu :**
1. ✅ Affichage des statistiques du jour :
   - Total Time Coded
   - Languages breakdown (top 5)
   - Category breakdown
2. ✅ Si < 2h avant 17h : alerte orange
3. ✅ Si >= 2h : message de félicitations

### 6. Tester l'Étape Reinforce

```bash
python skillops.py start
# Sélectionner "Reinforce Practice"
```

**Comportement attendu :**
1. ✅ Tableau avec 5 exercices :
   - docker-basics (Débutant, 15min)
   - k8s-pods (Intermédiaire, 30min)
   - terraform-aws (Intermédiaire, 45min)
   - ansible-playbook (Débutant, 20min)
   - cicd-pipeline (Avancé, 60min)
2. ✅ Prompt pour sélectionner un exercice (ID)
3. ✅ Affichage des détails de l'exercice
4. ✅ Chronomètre interactif (Start/Stop)
5. ✅ Validation de complétion
6. ✅ Sauvegarde de la progression

**Test complet :**
```
Enter exercise ID to start: docker-basics
[Affiche les détails]
Start the exercise? [y/N]: y
[Chronomètre démarre]
Have you completed this exercise? [y/N]: y
✅ Progress saved!
```

### 7. Tester les Étapes Placeholder

```bash
python skillops.py start
# Tester : Analysis, Zettelkasten, Learn, Share, Notify
```

**Comportement attendu pour chaque :**
```
[Icon] [Step Name]

This step is not yet implemented.
Coming soon in Sprint 2!
```

### 8. Tester Quit

```bash
python skillops.py start
# Sélectionner "Quit"
```

**Comportement attendu :**
- Message : "Goodbye! Keep learning! 🚀"
- Sortie propre du programme

## 🔧 Tests de Développement

### Lancer les Tests Unitaires

```bash
# Tous les tests
python -m pytest tests/

# Avec couverture
python -m pytest tests/ --cov=src/lms --cov-report=term-missing

# Tests spécifiques
python -m pytest tests/lms/cli_test.py -v
python -m pytest tests/lms/steps/ -v

# Tests e2e seulement
python -m pytest tests/lms/cli_e2e_test.py -v
python -m pytest tests/lms/integration/ -v
```

### Lancer les Pre-commit Hooks

```bash
# Installer pre-commit
pip install pre-commit
pre-commit install

# Tester manuellement
pre-commit run --all-files

# Résultats attendus :
# ✅ trim trailing whitespace
# ✅ fix end of files
# ✅ check yaml
# ✅ check toml
# ✅ black (formatting)
# ✅ flake8 (linting)
# ✅ mypy (type checking)
```

### Vérifier la CI/CD

```bash
# Voir les workflows GitHub Actions
gh workflow list

# Voir les runs récents
gh run list --limit 5

# Détails d'un run
gh run view [run-id]
```

## 🐛 Problèmes Connus & Solutions

### 1. ModuleNotFoundError: No module named 'src'

**Cause :** Imports relatifs dans main.py

**Solution :** Utiliser `python skillops.py` au lieu de `python src/lms/main.py`

### 2. WAKATIME_API_KEY not found

**Cause :** Fichier .env non configuré

**Solution :**
```bash
cp .env.example .env
# Éditer .env et ajouter votre clé WakaTime
```

### 3. Tests échouent (reinforce_test.py)

**Cause :** Refactoring de ProgressManager → JSON storage

**État :** En cours de résolution (Issue #22 - Sprint 2)

### 4. Import errors dans les tests

**Cause :** Mélange de `from lms.` et `from src.lms.`

**Solution :** Tous les tests utilisent maintenant `from src.lms.`

## ✅ Checklist de Test Complet

### Tests Automatisés
- [ ] `pytest tests/` : ≥95% des tests passent
- [ ] `pre-commit run --all-files` : Tous les hooks passent
- [ ] CI/CD pipeline : Build passe sur GitHub Actions

### Tests Manuels - CLI
- [ ] `python skillops.py --help` : Affiche l'aide
- [ ] `python skillops.py version` : Affiche v0.1.0
- [ ] `python skillops.py start` : Menu interactif fonctionne

### Tests Manuels - Étapes
- [ ] Review : Affiche "No data" quand aucune donnée
- [ ] Formation (sans API key) : Message d'erreur clair
- [ ] Formation (avec API key) : Affiche stats WakaTime
- [ ] Reinforce : Tableau d'exercices + chronomètre
- [ ] Autres étapes : Messages "Coming soon"

### Tests de Navigation
- [ ] Flèches haut/bas : Navigation dans le menu
- [ ] **Touches vim (j/k) : Navigation style vim** ⌨️
- [ ] Entrée : Sélection d'une étape
- [ ] Quit : Sortie propre avec message
- [ ] Ctrl+C : Interruption propre

## 📈 Métriques de Qualité

### Code Coverage
```
src/lms/cli.py                  98%
src/lms/display.py             100%
src/lms/api_clients/           100%
src/lms/steps/formation.py     100%
src/lms/steps/reinforce.py     100%
src/lms/steps/review.py         98%
```

### Tests
- **Unitaires :** 170+ tests
- **Intégration :** 13 tests (WakaTime)
- **End-to-End :** 19 tests (CLI)
- **Total :** 216 tests

### Code Quality
- **Black :** Formatting ✅
- **Flake8 :** No linting errors ✅
- **Mypy :** Type hints validated ✅
- **Pre-commit :** All hooks pass ✅

## 🎯 Prochaines Étapes (Sprint 2)

1. **Fixer les tests échouants** (11 tests)
2. **Implémenter Analysis step** (Gemini AI)
3. **Implémenter Zettelkasten step** (Obsidian)
4. **Implémenter Learn step** (Anki)
5. **Tests end-to-end complets** avec toutes les étapes

---

**Note :** Ce guide sera mis à jour à chaque sprint avec les nouvelles fonctionnalités.
