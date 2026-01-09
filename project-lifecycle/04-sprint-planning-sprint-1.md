# Sprint Planning - Sprint 1 (MVP Core)
## SkillOps Learning Management System

**Sprint:** 1  
**Date:** 9 janvier 2026  
**Durée:** 2 semaines (9 jan - 23 jan 2026)  
**Scrum Master:** MB  
**Product Owner:** MB  
**Équipe Dev:** MB (DevOps Engineer)

---

## 🎯 Objectif du Sprint

**Sprint Goal:**  
> Développer un CLI fonctionnel permettant de lancer la routine d'apprentissage quotidienne, de tracker le temps via WakaTime, de visualiser les métriques de progression, et de marquer les exercices comme complétés. L'outil doit persister l'état entre les sessions.

**Critères de succès :**
- ✅ L'utilisateur peut lancer `skillops start` et voir un menu interactif
- ✅ Les 8 étapes sont navigables avec les flèches du clavier
- ✅ L'intégration WakaTime fonctionne (affichage temps codé)
- ✅ Les métriques d'hier sont affichées dans Review
- ✅ L'état est sauvegardé entre les sessions (`.state.yaml`, `.progress.json`)
- ✅ Au moins 70% de couverture de tests
- ✅ Le pipeline CI/CD fonctionne (tests + linting)

---

## 📋 User Stories du Sprint

D'après l'[URD](02-urd-user-requirements-document.md), les stories Must Have pour le MVP :

### 🔴 Must Have (Sprint 1)

| ID | User Story | Story Points | Priorité |
|----|-----------|--------------|----------|
| **US-001** | Tracking de Formation (WakaTime) | 5 | P0 |
| **US-002** | Review des Métriques Quotidiennes | 3 | P0 |
| **US-003** | Exercices de Renforcement | 3 | P0 |
| **US-010** | Persistence des Données | 3 | P0 |
| **US-011** | Interface CLI Interactive | 5 | P0 |

**Total Sprint 1 :** 19 story points

---

## 🔧 Découpage en Tasks Techniques

### US-010: Persistence des Données (3 points)
**Pourquoi en premier ?** Toutes les autres US en dépendent

#### Tasks :
- [ ] **T010-1:** Créer structure `storage/` avec `.gitignore` (1h)
  - Créer dossiers `storage/`
  - Ajouter `storage/*` dans `.gitignore` (sauf `.gitkeep`)
  
- [ ] **T010-2:** Implémenter `persistence.py` - Gestion YAML (2h)
  ```python
  # lms/persistence.py
  class StateManager:
      def load_state() -> dict
      def save_state(state: dict)
  ```
  - Lecture/écriture `.state.yaml`
  - Gestion cas fichier inexistant (création auto)
  - Tests unitaires

- [ ] **T010-3:** Implémenter gestion JSON (2h)
  ```python
  class ProgressManager:
      def load_progress() -> list
      def save_daily_progress(date, data)
      def get_yesterday_progress() -> dict
  ```
  - Lecture/écriture `.progress.json`
  - Format : `[{date, steps, time, cards, streak}, ...]`
  - Tests unitaires

- [ ] **T010-4:** Implémenter métriques agrégées (1h)
  ```python
  class MetricsManager:
      def calculate_streak() -> int
      def get_average_time() -> float
      def update_metrics()
  ```
  - Tests unitaires

**Total US-010 :** 6h

---

### US-011: Interface CLI Interactive (5 points)

#### Tasks :
- [ ] **T011-1:** Setup projet Python (2h)
  - `pip install typer rich inquirer pytest pytest-cov`
  - Créer `requirements.txt`
  - Structure `src/lms/` avec `__init__.py`
  - Créer `main.py` entry point

- [ ] **T011-2:** Implémenter menu principal (3h)
  ```python
  # lms/cli.py
  def main_menu() -> Step:
      """Affiche menu interactif des 8 étapes"""
      choices = [
          "1. 📊 Review Metrics",
          "2. ⏱️  Formation (WakaTime)",
          # ...
          "8. 🌅 Reflection",
          "Exit"
      ]
      # Inquirer pour navigation
  ```
  - Menu avec Inquirer (navigation flèches)
  - Indicateur visuel étape courante (● vs ○)
  - Option Exit

- [ ] **T011-3:** Implémenter affichage Rich (2h)
  - Tableaux formatés (métriques)
  - Progress bars
  - Couleurs (vert = OK, rouge = warning)
  - Layout responsive

- [ ] **T011-4:** Tests CLI (2h)
  - Tester inputs/outputs
  - Mock user input
  - Vérifier rendering

**Total US-011 :** 9h

---

### US-002: Review des Métriques (3 points)

#### Tasks :
- [ ] **T002-1:** Implémenter step Review (2h)
  ```python
  # lms/steps/review.py
  def review_metrics():
      yesterday = ProgressManager.get_yesterday_progress()
      display_summary(yesterday)
  ```
  - Récupérer données d'hier
  - Calculer streak
  - Afficher dans tableau Rich

- [ ] **T002-2:** Affichage formaté (2h)
  ```
  ┌─────────────────────────────────┐
  │  Métriques du 8 janvier 2026    │
  ├─────────────────────────────────┤
  │ ✅ Étapes complétées : 7/8      │
  │ ⏱️  Temps codé : 3h42           │
  │ 📝 Cartes créées : 12           │
  │ 🔥 Streak : 18 jours            │
  └─────────────────────────────────┘
  ```
  - Table Rich avec émojis
  - Couleurs conditionnelles (vert si objectif atteint)

- [ ] **T002-3:** Tests (1h)

**Total US-002 :** 5h

---

### US-001: Tracking WakaTime (5 points)

#### Tasks :
- [ ] **T001-1:** Setup WakaTime API client (2h)
  ```python
  # lms/api_clients/wakatime_client.py
  class WakaTimeClient:
      def __init__(self, api_key: str)
      def get_today_stats() -> dict
      def get_date_stats(date: str) -> dict
  ```
  - Authentification via token
  - Requête API `/users/current/summaries`
  - Parsing JSON response
  - Gestion erreurs (rate limit, network)

- [ ] **T001-2:** Intégration dans step Formation (2h)
  ```python
  # lms/steps/formation.py
  def formation_step():
      client = WakaTimeClient(os.getenv('WAKATIME_API_KEY'))
      today_stats = client.get_today_stats()
      display_time(today_stats['grand_total']['text'])
  ```
  - Afficher temps codé aujourd'hui
  - Afficher langages utilisés
  - Alerte si < 2h avant 17h

- [ ] **T001-3:** Configuration secrets (1h)
  - Créer `.env.example`
  - Documentation dans README
  - Load avec `python-dotenv`

- [ ] **T001-4:** Tests avec mocks (3h)
  - Mock API responses
  - Test cas erreur (401, 429, network)
  - Test parsing données

**Total US-001 :** 8h

---

### US-003: Exercices de Renforcement (3 points)

#### Tasks :
- [ ] **T003-1:** Implémenter step Reinforce (2h)
  ```python
  # lms/steps/reinforce.py
  def reinforce_step():
      exercises = [
          "Déployer une app Flask avec Docker",
          "Configurer un pipeline CI/CD basique",
          "Créer un playbook Ansible"
      ]
      # Afficher liste
      # Marquer comme done
      # Timer par exercice
  ```
  - Liste hardcodée pour MVP
  - Checkbox pour marquer done
  - Timer simple

- [ ] **T003-2:** Sauvegarde progression (1h)
  - Persister exercices complétés
  - Historique dans `.progress.json`

- [ ] **T003-3:** Tests (1h)

**Total US-003 :** 4h

---

### 🔨 Tasks Infrastructure & DevOps

#### CI/CD Setup (non user story, mais critique)

- [ ] **T-CI-1:** Créer `.github/workflows/ci.yml` (2h)
  ```yaml
  name: CI
  
  on: [push, pull_request]
  
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - uses: actions/setup-python@v4
          with:
            python-version: '3.11'
        - run: pip install -r requirements.txt
        - run: pytest --cov=lms --cov-report=xml
        - run: coverage report --fail-under=70
    
    lint:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - run: pip install black pylint mypy
        - run: black --check .
        - run: pylint lms/
        - run: mypy lms/
  ```

- [ ] **T-CI-2:** Pre-commit hooks (1h)
  - `.pre-commit-config.yaml`
  - Black, isort, trailing-whitespace

- [ ] **T-CI-3:** Badge README (30min)
  - Ajouter badge CI status
  - Badge coverage

**Total Infra :** 3.5h

---

## 📊 Estimation Totale

| Catégorie | Temps Estimé |
|-----------|--------------|
| **US-010** (Persistence) | 6h |
| **US-011** (CLI) | 9h |
| **US-002** (Review) | 5h |
| **US-001** (WakaTime) | 8h |
| **US-003** (Reinforce) | 4h |
| **Infra** (CI/CD) | 3.5h |
| **Total** | **35.5h** |

**Répartition sur 2 semaines :**
- ~18h semaine 1
- ~17.5h semaine 2
- Moyenne : **~3.5h par jour** (sur 10 jours ouvrés)

**Vélocité :** 19 story points / 2 semaines = **9.5 points/semaine**

---

## 🗓️ Planning Détaillé

### Semaine 1 (9-13 janvier)

**Jour 1 (Jeudi 9 jan) - Setup & Persistence**
- ✅ T010-1: Structure storage (1h)
- ✅ T010-2: StateManager YAML (2h)
- ✅ T010-3: ProgressManager JSON (2h)
- **Total jour 1 :** 5h

**Jour 2 (Vendredi 10 jan) - CLI Foundation**
- [ ] T011-1: Setup projet Python (2h)
- [ ] T011-2: Menu principal (3h)
- **Total jour 2 :** 5h

**Weekend - Pause**

**Jour 3 (Lundi 13 jan) - CLI Polish**
- [ ] T011-3: Affichage Rich (2h)
- [ ] T011-4: Tests CLI (2h)
- [ ] T010-4: Métriques agrégées (1h)
- **Total jour 3 :** 5h

### Semaine 2 (14-17 janvier)

**Jour 4 (Mardi 14 jan) - Review Step**
- [ ] T002-1: Implémenter Review (2h)
- [ ] T002-2: Affichage formaté (2h)
- [ ] T002-3: Tests Review (1h)
- **Total jour 4 :** 5h

**Jour 5 (Mercredi 15 jan) - WakaTime Integration**
- [ ] T001-1: WakaTime API client (2h)
- [ ] T001-2: Intégration Formation step (2h)
- [ ] T001-3: Configuration secrets (1h)
- **Total jour 5 :** 5h

**Jour 6 (Jeudi 16 jan) - Reinforce & Tests**
- [ ] T001-4: Tests WakaTime (3h)
- [ ] T003-1: Reinforce step (2h)
- **Total jour 6 :** 5h

**Jour 7 (Vendredi 17 jan) - CI/CD & Polish**
- [ ] T003-2: Sauvegarde progression (1h)
- [ ] T003-3: Tests Reinforce (1h)
- [ ] T-CI-1: GitHub Actions (2h)
- [ ] T-CI-2: Pre-commit hooks (1h)
- **Total jour 7 :** 5h

**Weekend - Buffer & documentation**
- [ ] T-CI-3: Badge README (30min)
- [ ] Documentation README (installation, usage)
- [ ] Tests end-to-end
- [ ] Bug fixes

---

## 📦 Definition of Done

Une user story est considérée "Done" quand :

### Code
- [ ] Code implémenté selon acceptance criteria
- [ ] Code respecte PEP 8 (vérifié par black)
- [ ] Pas de warnings pylint critiques
- [ ] Type hints ajoutés (vérifié par mypy)

### Tests
- [ ] Tests unitaires écrits (pytest)
- [ ] Coverage > 70% pour le module
- [ ] Tests passent en local
- [ ] Tests passent en CI/CD

### Documentation
- [ ] Docstrings ajoutées (format Google)
- [ ] README mis à jour si nécessaire
- [ ] Exemples d'usage si nouvelle feature

### CI/CD
- [ ] Pipeline CI passe (tests + linting)
- [ ] Pas de secrets committés (check gitleaks)
- [ ] Branch mergée dans main

### Review
- [ ] Code review par... moi-même 😅 (simulation : relecture 24h après)
- [ ] Acceptance criteria validés par PO (moi)

---

## 🎭 Daily Stand-up Format

Chaque matin, je documente dans un fichier `daily-log.md` :

**Format :**
```
## Jour X - [Date]

### Hier
- [Task complétée]
- [Task complétée]

### Aujourd'hui
- [Task planifiée]
- [Task planifiée]

### Blocages
- [Blocker si existe]
```

---

## 🚧 Risques Identifiés

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| **WakaTime API rate limit** | Medium | Low | Caching des résultats, retry avec backoff |
| **Temps sous-estimé** | High | Medium | Buffer weekend, prioriser US-001/002/010 |
| **Complexité CLI navigation** | Medium | Medium | Utiliser exemples Inquirer, tests manuels |
| **Tests flaky** | Low | Low | Mocks propres, pas de dépendances réseau |

---

## 📈 Métriques de Sprint

À tracker quotidiennement :

- **Story points completed** (target: 19)
- **Bugs trouvés** (target: < 5)
- **Coverage** (target: > 70%)
- **Commits par jour** (indicateur activité)

---

## 🎯 Sprint Review (23 janvier)

**Demo checklist :**

1. **Lancement de l'outil**
   ```bash
   python main.py
   ```
   → Menu interactif s'affiche

2. **Navigation menu**
   → Flèches haut/bas fonctionnent
   → Indicateur étape courante visible

3. **Step 1: Review Metrics**
   → Affiche métriques d'hier (simulées si premier jour)
   → Streak calculé correctement

4. **Step 2: Formation**
   → Appel WakaTime API réussi
   → Temps codé affiché
   → Message si quota non atteint

5. **Step 4: Reinforce**
   → Liste d'exercices affichée
   → Possibilité de marquer done
   → Sauvegarde persiste

6. **Persistence**
   → Quitter et relancer l'outil
   → État restauré correctement

7. **CI/CD**
   → Montrer pipeline GitHub Actions (vert ✅)
   → Badge dans README

**Questions pour le PO (moi) :**
- Est-ce que l'UX réduit la friction ?
- Est-ce que je l'utiliserais quotidiennement ?
- Qu'est-ce qui manque pour Sprint 2 ?

---

## 🔄 Sprint Retrospective (23 janvier)

**Format Start/Stop/Continue :**

À remplir après le sprint :

### Continue (ce qui a bien marché)
- _À remplir_

### Stop (ce qui a mal marché)
- _À remplir_

### Start (à essayer au prochain sprint)
- _À remplir_

**Actions d'amélioration :**
- _À définir après retro_

---

## 🔗 Ressources

- [Product Discovery Session](01-product-discovery-session.md)
- [URD - User Requirements](02-urd-user-requirements-document.md)
- [ADR - Architecture Decisions](03-adr-architecture-decision-records.md)
- [WakaTime API Documentation](https://wakatime.com/developers)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)

---

## ✅ Sprint Commitment

**En tant qu'équipe** (moi-même 😄), nous nous engageons à :
- Livrer les 5 user stories Must Have
- Maintenir une couverture de tests > 70%
- Respecter les standards de code (black, pylint)
- Documenter les décisions importantes
- Faire une vraie démo à la fin du sprint

**Signature :**
- Product Owner: MB ✅
- Scrum Master: MB ✅
- DevOps Engineer: MB ✅

---

**Status:** Committed - Sprint Started 🚀  
**Next Review:** 23 janvier 2026  
**Next Document:** [05-development-logs.md](05-development-logs.md) (à créer pendant le sprint)
