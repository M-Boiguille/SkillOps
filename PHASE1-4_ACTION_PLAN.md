# Plan d'Action: Transformation SkillOps (9 Étapes → 3 Commandes)

**Date:** 12 février 2026
**Objectif:** Transformer SkillOps d'une app complexe (9 étapes) à une app lean (3 commandes)
**Horizon:** 4-6 semaines
**Status:** 🟢 Architecture validée, prêt pour Phase 1

---

## 📋 Vue d'ensemble des Phases

| Phase | Objectif | Durée | Dépendances | Status |
|-------|----------|-------|-------------|--------|
| **1** | 3 commandes simplifiées (train, code, review) | 1-2 sem | Aucune | ❌ TODO |
| **2a** | Tuer AnkiConnect, quiz SQLite | 3-4 jours | Phase 1 | ❌ TODO |
| **2b** | Chaos templates + bug injection | 1 sem | Phase 1 + 2a | ❌ TODO |
| **3** | Tracking passif (git hooks + WakaTime) | 1 sem | Phase 1-2 | ❌ TODO |
| **4** | TUI stats (Textual dashboard) | 2-3 sem | Phase 1-3 | ❌ TODO |

---

## PHASE 1: Les 3 Commandes Simplifiées

### Objectif
Remplacer 9 étapes séquentielles par 3 commandes autonomes:
- `skillops train <topic>` → Mode apprentissage avec quiz
- `skillops code` → Mode coding avec tracking passif
- `skillops review` / `skillops stats` → Mode consultation des métriques

### Tâches

#### 1.1 Refactoriser `src/lms/cli.py` → `src/lms/commands/`
```
Créer structure:
  src/lms/commands/
    ├── __init__.py
    ├── train.py        # Quiz + apprentissage
    ├── code.py         # Tracking coding
    └── review.py       # Consultation stats
```
- **Fichier:** [src/lms/cli.py](src/lms/cli.py)
- **Changement:** Garder menu principal simple, déplacer logique dans modules
- **Tests:** Créer [tests/lms/test_commands.py](tests/lms/test_commands.py)

#### 1.2 Implémenter `train <topic>`
```python
# src/lms/commands/train.py
@app.command("train")
def train(topic: str = typer.Argument(...)):
    """Apprentissage interactif avec quiz Gemini"""
    # 1. Load/create learning_profile for topic
    # 2. Generate 3-5 questions via Gemini
    # 3. Interactive Q&A loop
    # 4. Track correct answers → update streak
```
- **Dépendances:** Gemini API (déjà présent), database.learning_profile
- **Tests:**
  - Mock Gemini responses
  - Verify streak increments on correct answers
  - Check learning_profile updated

#### 1.3 Implémenter `code`
```python
# src/lms/commands/code.py
@app.command("code")
def code():
    """Tracking passif du coding (git hooks + WakaTime manual)"""
    # Phase 1: Just display current session
    # Message: "Git hooks will auto-track commits"
    # Show: today's hours (manual for now)
```
- **Phase 1 Scope:** Minimal (placeholder)
- **Phase 3 Scope:** Git hooks + WakaTime integration (ajouter plus tard)
- **Tests:** Verify command runs without error

#### 1.4 Implémenter `review` / `stats`
```python
# src/lms/commands/review.py
@app.command("review")
@app.command("stats")
def review_stats():
    """Consultation: Streak, hours, concepts, chaos tests"""
    # 1. Query sessions → calculate current streak
    # 2. Query performance_metrics → coding hours today
    # 3. Query user_learning_profile → topics learned
    # 4. Display via Rich table
```
- **Dépendances:** persistence.py (calculate_streak déjà prêt ✅)
- **Tests:** Mock database, verify output formatting

#### 1.5 Mettre à jour `src/lms/main.py`
```python
# Replace current 9-step menu with simple dispatch:
# @app.callback() → welcome message
# Then import and include: train, code, review commands
```
- **Changement:** Typer multi-command structure (on a déjà typer v0.9.8)
- **Tests:** CLI smoke tests doivent passer

### Critères de Succès Phase 1
- ✅ `skillops train kubernetes` génère 3 questions et enregistre réponses
- ✅ `skillops code` affiche message "tracking passif activé"
- ✅ `skillops review` affiche streak actuel + stats du jour
- ✅ Tous les tests Phase 1 passent
- ✅ Tous les pre-commit hooks passent (black, flake8, mypy)
- ✅ Commité sur main avec message "feat: Implement 3-command architecture (Phase 1)"

### Timeline Phase 1
- **Jour 1-2:** Créer structure commands/, écrire tests d'intégration
- **Jour 3:** Implémenter train command + Gemini integration
- **Jour 4:** Implémenter code + review commands
- **Jour 5:** Tester, débugger, commit

---

## PHASE 2a: Tuer AnkiConnect

### Objectif
Supprimer AnkiConnect, créer SQLite quiz natif

### Tâches

#### 2a.1 Créer table SQLite quiz
```sql
-- Dans src/lms/database.py (v5 schema)
CREATE TABLE quiz_cards (
    id INTEGER PRIMARY KEY,
    topic TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    difficulty INTEGER,  -- 1-5
    last_reviewed DATE,
    review_count INTEGER DEFAULT 0
);
```
- **Fichier:** [src/lms/database.py](src/lms/database.py)
- **Changement:** Incrémenter version schema de 4 → 5
- **Migration:** Créer migration script pour existing DBs

#### 2a.2 Créer `src/lms/commands/quiz.py`
```python
@app.command("quiz")
def quiz(topic: str = typer.Argument(...)):
    """Mode quiz SQLite (remote to local)"""
    # 1. Load cards for topic from DB
    # 2. Or generate new cards via Gemini + store
    # 3. Interactive Q&A loop
    # 4. Score + difficulty adjustment
```
- **Dépendances:** quiz_cards table, Gemini API
- **Tests:** Mock card loading, verify scoring

#### 2a.3 Supprimer AnkiConnect
- **Fichiers à modifier:**
  - [requirements.txt](requirements.txt) → remove anki-connect
  - [src/lms/cli.py](src/lms/cli.py) → remove AnkiConnect imports/calls
  - [src/lms/persistence.py](src/lms/persistence.py) → remove Anki sync logic (si existe)
- **Tests:** Verify no imports of anki

#### 2a.4 Créer `skillops import-anki` (optionnel)
- Permettre aux users d'exporter leurs Anki decks
- CSV → SQLite quiz_cards
- Pour migration légère

### Critères de Succès Phase 2a
- ✅ AnkiConnect complètement supprimé (pas de dépendance)
- ✅ `skillops quiz kubernetes` charge cards depuis SQLite
- ✅ Gemini génère cards si table vide
- ✅ Tous tests passent, pre-commit OK
- ✅ Commité: "feat: Kill AnkiConnect, implement SQLite quiz (Phase 2a)"

### Timeline Phase 2a
- **Jour 1:** Schema v5, migration script
- **Jour 2:** Implémenter quiz command
- **Jour 3:** Supprimer AnkiConnect, tester migration
- **Jour 4:** Cleanup, commit

---

## PHASE 2b: Chaos Templates + Bug Injection

### Objectif
Implémenter adaptive chaos testing avec templates + bug injection adaptatif

### Tâches

#### 2b.1 Créer `user_learning_profile` table
```sql
CREATE TABLE user_learning_profile (
    id INTEGER PRIMARY KEY,
    user_id TEXT UNIQUE,
    current_topics TEXT,  -- JSON: ["kubernetes", "docker"]
    recent_achievements TEXT,
    learning_difficulty TEXT  -- "beginner", "intermediate", "advanced"
);
```
- **Fichier:** [src/lms/database.py](src/lms/database.py)
- **Intégration:** Remplir lors du `train` command

#### 2b.2 Créer templates YAML
```
src/lms/chaos_templates/
├── README.md
├── k8s_healthchecks.yaml
├── k8s_resource_limits.yaml
├── docker_network_isolation.yaml
├── systemd_timeout.yaml
└── container_oom.yaml
```

**Exemple template:**
```yaml
# k8s_healthchecks.yaml
name: "Kubernetes Healthchecks"
learning_topics: ["kubernetes", "deployment", "reliability"]
difficulty: "intermediate"

bug_inject: |
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: broken-app
  spec:
    containers:
    - name: app
      livenessProbe: null  # BUG: Missing healthcheck
      readinessProbe: null

description: "App crashes repeatedly. Why? Fix the deployment."
expected_solution: "Add liveness/readiness probes"
```

- **Fichier:** Créer [src/lms/chaos_templates/](src/lms/chaos_templates/)
- **Format:** YAML simple, pas de code Python

#### 2b.3 Créer `src/lms/chaos.py`
```python
def pick_chaos_template(user_id: str) -> dict:
    """Pick template matching user's learning topics"""
    profile = get_learning_profile(user_id)
    compatible_templates = filter_by_topics(profile.current_topics)
    return random.choice(compatible_templates)

def apply_chaos(template: dict) -> str:
    """Render YAML bug, return manifests"""
    return template["bug_inject"]

def get_ai_feedback(user_answer: str, template: dict) -> str:
    """Gemini analyze user's fix attempt"""
    prompt = f"""
    User is learning: {template['learning_topics']}
    Expected fix: {template['expected_solution']}
    User suggested: {user_answer}

    Provide constructive feedback.
    """
    return gemini.generate(prompt)
```

- **Dépendances:** Gemini API, user_learning_profile table
- **Tests:** Mock Gemini, verify template picking

#### 2b.4 Créer `chaos_history` table
```sql
CREATE TABLE chaos_history (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    template_name TEXT,
    attempt_date DATE,
    user_answer TEXT,
    ai_feedback TEXT,
    success BOOLEAN
);
```

#### 2b.5 Créer `@app.command("chaos")`
```python
@app.command("chaos")
def chaos(user_id: str = "default"):
    """Launch adaptive chaos test"""
    # 1. Pick template based on learning profile
    # 2. Display bug-injected manifest
    # 3. Ask user to identify/fix bug
    # 4. Get Gemini feedback
    # 5. Store result in chaos_history
```

### Critères de Succès Phase 2b
- ✅ 5-6 chaos templates dans YAML
- ✅ `skillops chaos` picks template matching user's topics
- ✅ Gemini provides contextual feedback on fix attempt
- ✅ Results stored in chaos_history
- ✅ Tous tests passent
- ✅ Commité: "feat: Implement adaptive chaos templates + bug injection (Phase 2b)"

### Timeline Phase 2b
- **Jour 1:** Table schema, user_learning_profile integration
- **Jour 2-3:** Créer 5-6 templates YAML
- **Jour 4:** Implémenter chaos.py + chaos command
- **Jour 5:** Gemini integration + feedback loop
- **Jour 6:** Tests, cleanup, commit

---

## PHASE 3: Tracking Passif

### Objectif
Auto-validate "code" step via git hooks + WakaTime (zero manual interaction)

### Tâches

#### 3.1 Git Hooks Installation
```
src/setup/hooks/
├── post-commit
└── install_hooks.sh
```

**post-commit script:**
```bash
#!/bin/bash
# Auto-log commit to SkillOps
python3 -c "from src.lms.persistence import log_commit; log_commit()"
```

- **Fichier:** Créer [src/setup/hooks/post-commit](src/setup/hooks/post-commit)
- **Installation:** `skillops setup-hooks` → symlink to .git/hooks/
- **Tests:** Verify hook fires on commit

#### 3.2 Implémenter `log_commit()`
```python
# src/lms/persistence.py
def log_commit(repo_path: str = "."):
    """
    Auto-called by git post-commit hook
    1. Parse git diff
    2. Extract language/topic
    3. Auto-validate "code" session
    """
    # Get last commit
    # Parse files changed
    # Infer language/topic
    # Create session with auto_validated=True
```

- **Dépendances:** GitPython library (add to requirements.txt)
- **Tests:** Mock git operations

#### 3.3 WakaTime Passive Integration
```python
# src/lms/persistence.py
def sync_wakatime_metrics(user_id: str):
    """
    Called from `skillops code` or via cron
    1. Query WakaTime API
    2. Sum today's coding hours
    3. If 2+ hours → auto-validate "code" session
    """
    wakatime_data = wakatime.get_today()
    if wakatime_data['total_seconds'] / 3600 >= 2:
        auto_validate_session("code")
```

- **Dépendances:** WakaTime API (déjà intégré)
- **Tests:** Mock WakaTime API response

#### 3.4 Créer `@app.command("setup-hooks")`
```python
@app.command("setup-hooks")
def setup_hooks():
    """Install git hooks for passive tracking"""
    hook_src = Path(__file__).parent / "setup" / "hooks" / "post-commit"
    hook_dst = Path(".git") / "hooks" / "post-commit"
    shutil.copy(hook_src, hook_dst)
    os.chmod(hook_dst, 0o755)
    typer.echo("✅ Git hooks installed")
```

### Critères de Succès Phase 3
- ✅ `skillops setup-hooks` installe git hooks
- ✅ Chaque commit trigger `log_commit()` → crée session auto
- ✅ `skillops code` syncs WakaTime, auto-validate si 2+ heures
- ✅ No manual "validate code step" needed
- ✅ Tous tests passent
- ✅ Commité: "feat: Implement passive tracking via git hooks + WakaTime (Phase 3)"

### Timeline Phase 3
- **Jour 1:** Git hooks script + installation
- **Jour 2:** Implement log_commit() parsing
- **Jour 3:** WakaTime sync integration
- **Jour 4:** Tests, debugging
- **Jour 5:** Commit

---

## PHASE 4: TUI Stats Dashboard

### Objectif
Créer Textual-based interactive stats dashboard (not persistent daemon)

### Tâches

#### 4.1 Ajouter Textual à requirements.txt
```
textual==0.42.0
rich==13.7.0  # Already present
```

#### 4.2 Créer `src/lms/tui/dashboard.py`
```python
from textual.app import ComposeResult
from textual.widgets import Static, DataTable

class Dashboard(StaticScreen):
    """Main stats dashboard"""
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            StatsPanel(),    # Streak, hours, concepts
            ChaosPanel(),    # Recent chaos tests
            Footer()
        )

    def on_key(self, event) -> None:
        """Keyboard shortcuts"""
        if event.key == "t":
            self.app.push_screen("train")  # Launch train command
        elif event.key == "c":
            self.app.push_screen("code")
        elif event.key == "q":
            self.app.exit()
```

#### 4.3 Créer `@app.command("dashboard")`
```python
@app.command("dashboard")
def dashboard():
    """Launch interactive stats TUI"""
    from src.lms.tui.dashboard import Dashboard
    app = Dashboard()
    app.run()
```

#### 4.4 Panels
- **StatsPanel:** Streak, total hours, concepts learned, chaos tests passed
- **ChaosPanel:** Last 5 chaos attempts, success rate
- **Footer:** Shortcuts (t=train, c=code, r=review, q=quit)

### Critères de Succès Phase 4
- ✅ `skillops dashboard` launches interactive TUI
- ✅ Shows real-time stats from DB
- ✅ Keyboard navigation works
- ✅ Can launch train/code from within TUI
- ✅ Tous tests passent
- ✅ Commité: "feat: Add Textual TUI dashboard (Phase 4)"

### Timeline Phase 4
- **Jour 1-2:** Set up Textual structure
- **Jour 3-4:** Implement panels + data queries
- **Jour 5-6:** Keyboard shortcuts, polish UI
- **Jour 7:** Tests, commit

---

## 📊 Timeline Global

```
Semaine 1:  Phase 1 (3 commands architecture)
Semaine 2:  Phase 2a (kill AnkiConnect) + début Phase 2b
Semaine 3:  Phase 2b (chaos templates)
Semaine 4:  Phase 3 (passive tracking)
Semaine 5-6: Phase 4 (TUI dashboard) + polish
```

---

## 🎯 Prochaines Étapes Immédiatement

### Sprint 0 (Aujourd'hui - Jour 1 Phase 1)

1. **Créer structure commands:**
   ```bash
   mkdir -p src/lms/commands
   touch src/lms/commands/__init__.py
   touch src/lms/commands/train.py
   touch src/lms/commands/code.py
   touch src/lms/commands/review.py
   ```

2. **Créer tests intégration:**
   ```
   tests/lms/test_commands.py
   tests/lms/test_train_command.py
   tests/lms/test_code_command.py
   tests/lms/test_review_command.py
   ```

3. **Refactoriser main.py:**
   - Import les 3 commands
   - Typer multi-command dispatch
   - Remove 9-step menu

4. **Commit:**
   ```
   git commit -m "refactor: Restructure CLI to 3-command architecture (Phase 1 setup)"
   ```

---

## 📝 Tracking Progress

Après chaque phase:
```bash
# Update this document with Status → ✅ DONE
# Create commit with phase summary
# Update MODIFICATION.md with summary

git commit -m "feat: Complete Phase X - [description]"
```

---

## ⚠️ Risques & Mitigations

| Risque | Mitigation |
|--------|-----------|
| Gemini API quota exceeded | Implement retry logic, mock for tests |
| WakaTime API downtime | Graceful fallback, manual sync option |
| Git hooks not firing | Test with actual commits, document setup |
| TUI complexity | Start simple, iterate on UX |
| DB migration issues | Create reversible migration script, backup |

---

## 🚀 Success Criteria (Global)

- ✅ All 4 phases complete
- ✅ 100+ integration tests passing
- ✅ All pre-commit hooks passing
- ✅ No AnkiConnect dependency
- ✅ Git hooks auto-logging commits
- ✅ Chaos templates working adaptively
- ✅ TUI dashboard functional
- ✅ All features documented in README
- ✅ Production-ready on main branch

---

**Last Updated:** 12 février 2026
**Owner:** MB
**Status:** 🟢 Ready to Execute
