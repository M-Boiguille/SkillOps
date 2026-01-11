# Sprint Planning - Sprint 2 (Automatisations)
## SkillOps Learning Management System

**Sprint:** 2
**Date:** 11 janvier 2026
**Durée:** 2 semaines (11 jan - 25 jan 2026)
**Scrum Master:** MB
**Product Owner:** MB
**Équipe Dev:** MB (DevOps Engineer)

---

## 🎯 Objectif du Sprint

**Sprint Goal:**
> Intégrer les APIs principales pour automatiser la génération de flashcards depuis Obsidian, l'envoi automatique des projets vers GitHub, et les notifications quotidiennes via Telegram. L'objectif est de réduire la friction dans le workflow d'apprentissage.

**Critères de succès :**
- ✅ Génération de flashcards depuis notes Obsidian vers Anki
- ✅ Commit et push automatique des projets labs vers GitHub
- ✅ Notifications Telegram quotidiennes avec métriques
- ✅ Tests d'intégration pour chaque API
- ✅ Documentation des configurations nécessaires
- ✅ Au moins 75% de couverture de tests
- ✅ Pipeline CI/CD étendu avec nouveaux tests

---

## 📋 User Stories du Sprint

D'après l'[URD](02-urd-user-requirements-document.md), les stories Should Have pour Sprint 2 :

### 🟡 Should Have (Sprint 2)

| ID | User Story | Story Points | Priorité | Dépendances |
|----|-----------|--------------|----------|-------------|
| **US-004** | Génération Automatique de Flashcards | 8 | P1 | Config Obsidian path |
| **US-005** | Automatisation Portfolio GitHub | 8 | P1 | GitHub token |
| **US-006** | Notifications Telegram | 5 | P1 | Telegram Bot token |

**Total Sprint 2 :** 21 story points

---

## 🔧 Découpage en Tasks Techniques

### US-004: Génération Automatique de Flashcards (8 points)

**Description:** Scanner le vault Obsidian, détecter les balises #flashcard ou format Q:/A:, générer un fichier Markdown compatible Anki, et l'exporter vers le dossier de synchronisation Anki.

#### Tasks :
- [ ] **T004-1:** Configuration Obsidian (1h)
  - Ajouter `OBSIDIAN_VAULT_PATH` dans `.env.example`
  - Ajouter validation du path dans configuration
  - Tests de configuration

- [ ] **T004-2:** Scanner de notes Obsidian (3h)
  ```python
  # lms/integrations/obsidian.py
  class ObsidianScanner:
      def scan_vault() -> list[Path]
      def extract_flashcards(file_path: Path) -> list[Flashcard]
      def parse_flashcard_syntax(content: str) -> list[dict]
  ```
  - Scan récursif du vault
  - Détection balises #flashcard
  - Parsing format `Q: question` / `A: answer`
  - Support du format inline `Q::A`
  - Tests unitaires avec fixtures

- [ ] **T004-3:** Générateur Anki Markdown (2h)
  ```python
  class AnkiMarkdownGenerator:
      def generate_anki_deck(flashcards: list) -> str
      def format_flashcard(q: str, a: str) -> str
  ```
  - Format compatible avec Anki import
  - Gestion des tags
  - Gestion du deck name
  - Tests unitaires

- [ ] **T004-4:** Export vers Anki (2h)
  - Configuration `ANKI_SYNC_PATH` dans `.env`
  - Écriture fichier dans dossier Anki
  - Gestion des doublons (vérification hash)
  - Confirmation visuelle nombre de cartes
  - Tests d'intégration

- [ ] **T004-5:** Intégration CLI Step "Create" (1h)
  - Ajouter appel à `generate_flashcards()` dans step 4
  - Affichage progrès avec Rich
  - Gestion erreurs (vault non trouvé, etc.)
  - Tests end-to-end

**Total US-004 :** 9h

---

### US-005: Automatisation Portfolio GitHub (8 points)

**Description:** Détecter automatiquement les nouveaux projets dans ~/labs/, générer un README.md avec template, commit et push vers GitHub avec un message conventionnel.

#### Tasks :
- [ ] **T005-1:** Configuration GitHub (1h)
  - Ajouter `GITHUB_TOKEN` et `GITHUB_USERNAME` dans `.env.example`
  - Validation token avec GitHub API
  - Tests de configuration

- [ ] **T005-2:** Détecteur de projets labs (2h)
  ```python
  # lms/integrations/github_auto.py
  class LabProjectDetector:
      def scan_labs_directory() -> list[Path]
      def is_new_project(project_path: Path) -> bool
      def get_project_metadata(path: Path) -> dict
  ```
  - Scan de `~/labs/` (configurable via `LABS_PATH`)
  - Détection projets sans remote Git
  - Extraction metadata (nom, tech stack auto-détectée)
  - Tests unitaires

- [ ] **T005-3:** Générateur README template (2h)
  ```python
  class ReadmeGenerator:
      def generate_readme(metadata: dict) -> str
      def detect_tech_stack(project_path: Path) -> list[str]
  ```
  - Template Markdown (titre, description, tech stack, usage)
  - Auto-détection tech stack (package.json, requirements.txt, etc.)
  - Badges automatiques (Python, Node, etc.)
  - Tests unitaires

- [ ] **T005-4:** Git automation (3h)
  ```python
  class GitHubAutomation:
      def init_repository(path: Path)
      def create_commit(message: str)
      def create_remote_repository(name: str) -> str
      def push_to_github()
  ```
  - `git init` si nécessaire
  - Commit avec message conventionnel
  - Création repo GitHub via API
  - Push avec token
  - Tests d'intégration (mock GitHub API)

- [ ] **T005-5:** Intégration CLI Step "Share" (1h)
  - Ajouter appel dans step 7 "Share"
  - Affichage URL du repo créé
  - Gestion erreurs (token invalide, repo existe, etc.)
  - Tests end-to-end

**Total US-005 :** 9h

---

### US-006: Notifications Telegram (5 points)

**Description:** Envoyer un bilan quotidien automatique à 20h via Telegram avec les métriques du jour (étapes complétées, temps codé, streak) et des alertes si la journée est incomplète.

#### Tasks :
- [ ] **T006-1:** Configuration Telegram Bot (1h)
  - Créer bot via @BotFather
  - Ajouter `TELEGRAM_BOT_TOKEN` et `TELEGRAM_CHAT_ID` dans `.env.example`
  - Guide dans README pour récupérer chat_id
  - Tests de configuration

- [ ] **T006-2:** Client Telegram (2h)
  ```python
  # lms/integrations/telegram_client.py
  class TelegramClient:
      def send_message(text: str)
      def send_formatted_message(metrics: dict)
      def test_connection() -> bool
  ```
  - Utilisation de `python-telegram-bot`
  - Formatage messages avec Markdown
  - Support des boutons inline (optionnel)
  - Tests unitaires avec mock

- [ ] **T006-3:** Générateur de rapports quotidiens (2h)
  ```python
  class DailyReportGenerator:
      def generate_report(progress: dict) -> str
      def format_metrics(metrics: dict) -> str
      def check_completion_alerts(progress: dict) -> list[str]
  ```
  - Format Telegram avec emojis
  - Alertes si <6 étapes complétées
  - Alerte si temps effectif/log faible
  - Message motivationnel basé sur streak
  - Tests unitaires

- [ ] **T006-4:** Scheduler notifications (2h)
  - Option CLI pour envoyer notification manuelle
  - Documentation pour setup cron/systemd timer
  - Script `send_daily_notification.py`
  - Tests d'intégration

- [ ] **T006-5:** Intégration CLI Step "Notify" (1h)
  - Nouveau step optionnel ou automatique en fin de session
  - Affichage confirmation envoi
  - Gestion erreurs (token invalide, réseau, etc.)
  - Tests end-to-end

**Total US-006 :** 8h

---

## 📦 Issues Techniques Additionnelles

### Issue #22: Documentation API Configurations
- [ ] Documenter setup pour chaque API (Obsidian, GitHub, Telegram)
- [ ] Ajouter troubleshooting section
- [ ] Screenshots/exemples de configuration
- [ ] Vidéo démo optionnelle
**Estimation:** 2h

### Issue #23: Tests d'intégration multi-API
- [ ] Tests end-to-end avec toutes les APIs
- [ ] Tests de rollback si une API échoue
- [ ] Tests de performance (scan Obsidian sur gros vault)
**Estimation:** 3h

### Issue #24: Gestion des secrets sécurisée
- [ ] Validation tokens au démarrage
- [ ] Messages d'erreur clairs pour configs manquantes
- [ ] Documentation sécurité (ne pas commit tokens)
**Estimation:** 2h

---

## 📊 Capacity Planning

**Développeur:** MB
**Disponibilité:** 2-3h/jour pendant 14 jours = **28-42h max**

**Story Points:**
- US-004: 8 pts = 9h
- US-005: 8 pts = 9h
- US-006: 5 pts = 8h
- Issues techniques: 7h

**Total estimé:** 33h
**Buffer:** 15% (5h) pour imprévus = **38h total**

✅ **Capacité suffisante** pour compléter le sprint

---

## 🎬 Ordre d'Exécution Recommandé

1. **US-006 (Telegram)** - Le plus simple, validation rapide de l'intégration API
2. **US-004 (Flashcards)** - Complexité moyenne, grande valeur utilisateur
3. **US-005 (GitHub)** - Le plus complexe, nécessite interaction avec GitHub API

Alternative : Commencer par US-004 si la génération de flashcards est la priorité.

---

## 📝 Definition of Done

Une story est considérée "Done" quand :
- ✅ Code implémenté selon les acceptance criteria
- ✅ Tests unitaires écrits et passent (>75% coverage)
- ✅ Tests d'intégration pour les APIs
- ✅ Documentation mise à jour (README, .env.example)
- ✅ Pre-commit hooks passent (black, flake8, mypy)
- ✅ CI/CD passe sur GitHub Actions
- ✅ Code review effectué (self-review ou pair)
- ✅ Demo fonctionnelle réalisable

---

## 🚀 Sprint Demo

**Date de demo:** 25 janvier 2026

**Scénario de demo:**
1. Ouvrir notes Obsidian avec balises #flashcard
2. Lancer `skillops start` → Step 4 "Create"
3. Voir génération de 12 flashcards vers Anki
4. Créer un nouveau projet dans `~/labs/sample-devops-project`
5. Lancer Step 7 "Share"
6. Voir commit automatique + création repo GitHub
7. Lancer Step 8 "Notify"
8. Recevoir notification Telegram avec bilan du jour

**Durée demo:** 10-15 minutes

---

## 📌 Risques et Mitigation

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| GitHub API rate limits | Moyenne | Moyen | Implémenter cache + retry logic |
| Format Obsidian incompatible | Faible | Moyen | Support multiple formats (Q:/A:, Q::A, #flashcard) |
| Telegram bloqué en entreprise | Faible | Faible | Rendre optionnel, skip si config manquante |
| Temps de scan Obsidian long | Moyenne | Faible | Implémenter cache + scan incrémental |

---

## 📚 Références

- [URD - User Requirements Document](02-urd-user-requirements-document.md)
- [Sprint 1 Planning](04-sprint-planning-sprint-1.md)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Anki Manual - Importing](https://docs.ankiweb.net/importing.html)

---

## ✅ Sprint Checklist

### Avant le Sprint
- [x] Sprint planning complété
- [ ] Issues GitHub créées avec labels
- [ ] Milestone "Sprint 2" créé sur GitHub
- [ ] `.env.example` vérifié

### Pendant le Sprint
- [ ] Daily standups (auto-log)
- [ ] Tests écrits avant/pendant le code (TDD)
- [ ] Documentation mise à jour au fur et à mesure
- [ ] Code reviews régulières

### Fin de Sprint
- [ ] Demo préparée
- [ ] Rétrospective écrite
- [ ] Backlog raffiné pour Sprint 3
- [ ] Métriques collectées (velocity, bugs, etc.)

---

**Document Status:** ✅ Ready for Execution
**Next Steps:** Créer issues GitHub → Commencer US-006 (Telegram)

---

*Document créé le 11 janvier 2026 - Sprint 2 commence aujourd'hui !*
