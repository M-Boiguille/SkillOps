#!/bin/bash
# Script to create all Sprint 1 issues in GitHub (without milestone for now)

REPO="M-Boiguille/SkillOps"

echo "Creating Sprint 1 issues..."

# US-010: Persistence (6h)
echo "Creating US-010 issues..."

gh issue create \
  --title "[US-010] T010-1: Créer structure storage/ avec .gitignore" \
  --body "**User Story:** US-010 - Persistence des Données (3 points)

**Description:**
Créer la structure de base pour la persistence des données.

**Tasks:**
- [ ] Créer dossier \`storage/\`
- [ ] Ajouter \`storage/*\` dans \`.gitignore\`
- [ ] Ajouter \`.gitkeep\` pour tracker le dossier

**Estimation:** 1h

**Definition of Done:**
- Structure créée
- Gitignore configuré
- Commit pushed" \
  --label "us-persistence,sprint-1"

gh issue create \
  --title "[US-010] T010-2: Implémenter StateManager pour gestion YAML" \
  --body "**User Story:** US-010 - Persistence des Données (3 points)

**Description:**
Implémenter la classe \`StateManager\` pour gérer l'état de l'application en YAML.

**Tasks:**
- [ ] Créer \`lms/persistence.py\`
- [ ] Implémenter \`StateManager.load_state() -> dict\`
- [ ] Implémenter \`StateManager.save_state(state: dict)\`
- [ ] Gérer cas fichier inexistant (création auto)
- [ ] Tests unitaires (pytest)

**Estimation:** 2h

**Definition of Done:**
- Code implémenté
- Tests unitaires > 80% coverage
- Type hints ajoutés" \
  --label "us-persistence,sprint-1"

gh issue create \
  --title "[US-010] T010-3: Implémenter ProgressManager pour gestion JSON" \
  --body "**User Story:** US-010 - Persistence des Données (3 points)

**Description:**
Implémenter la classe \`ProgressManager\` pour gérer l'historique de progression en JSON.

**Tasks:**
- [ ] Implémenter \`ProgressManager.load_progress() -> list\`
- [ ] Implémenter \`ProgressManager.save_daily_progress(date, data)\`
- [ ] Implémenter \`ProgressManager.get_yesterday_progress() -> dict\`
- [ ] Format JSON: \`[{date, steps, time, cards, streak}, ...]\`
- [ ] Tests unitaires

**Estimation:** 2h

**Definition of Done:**
- Code implémenté
- Tests unitaires > 80% coverage
- Format JSON validé" \
  --label "us-persistence,sprint-1"

gh issue create \
  --title "[US-010] T010-4: Implémenter MetricsManager pour calculs agrégés" \
  --body "**User Story:** US-010 - Persistence des Données (3 points)

**Description:**
Implémenter la classe \`MetricsManager\` pour calculer les métriques agrégées (streak, moyennes).

**Tasks:**
- [ ] Implémenter \`MetricsManager.calculate_streak() -> int\`
- [ ] Implémenter \`MetricsManager.get_average_time() -> float\`
- [ ] Implémenter \`MetricsManager.update_metrics()\`
- [ ] Tests unitaires

**Estimation:** 1h

**Definition of Done:**
- Code implémenté
- Tests unitaires passent
- Métriques calculées correctement" \
  --label "us-persistence,sprint-1"

# US-011: CLI (9h)
echo "Creating US-011 issues..."

gh issue create \
  --title "[US-011] T011-1: Setup projet Python avec dépendances" \
  --body "**User Story:** US-011 - Interface CLI Interactive (5 points)

**Description:**
Initialiser le projet Python avec toutes les dépendances nécessaires.

**Tasks:**
- [ ] \`pip install typer rich inquirer pytest pytest-cov\`
- [ ] Créer \`requirements.txt\`
- [ ] Créer structure \`src/lms/\` avec \`__init__.py\`
- [ ] Créer \`main.py\` entry point
- [ ] Documenter installation dans README

**Estimation:** 2h

**Definition of Done:**
- Requirements.txt créé
- Structure projet fonctionnelle
- \`python main.py\` exécutable" \
  --label "us-cli,sprint-1"

gh issue create \
  --title "[US-011] T011-2: Implémenter menu principal interactif" \
  --body "**User Story:** US-011 - Interface CLI Interactive (5 points)

**Description:**
Créer le menu principal avec navigation au clavier (Inquirer).

**Tasks:**
- [ ] Créer \`lms/cli.py\`
- [ ] Implémenter \`main_menu() -> Step\`
- [ ] Liste des 8 étapes + Exit
- [ ] Navigation avec flèches haut/bas
- [ ] Indicateur étape courante (● vs ○)

**Estimation:** 3h

**Definition of Done:**
- Menu affiché
- Navigation fonctionnelle
- Tests manuel OK" \
  --label "us-cli,sprint-1"

gh issue create \
  --title "[US-011] T011-3: Implémenter affichage Rich (tableaux, couleurs)" \
  --body "**User Story:** US-011 - Interface CLI Interactive (5 points)

**Description:**
Améliorer l'affichage avec Rich (tableaux, progress bars, couleurs).

**Tasks:**
- [ ] Tableaux formatés pour métriques
- [ ] Progress bars
- [ ] Couleurs conditionnelles (vert = OK, rouge = warning)
- [ ] Layout responsive

**Estimation:** 2h

**Definition of Done:**
- Affichage Rich fonctionnel
- Tableaux bien formatés
- Couleurs appropriées" \
  --label "us-cli,sprint-1"

gh issue create \
  --title "[US-011] T011-4: Tests CLI (inputs/outputs)" \
  --body "**User Story:** US-011 - Interface CLI Interactive (5 points)

**Description:**
Écrire les tests pour le CLI (inputs, outputs, rendering).

**Tasks:**
- [ ] Tests inputs/outputs
- [ ] Mock user input
- [ ] Vérifier rendering
- [ ] Coverage > 70%

**Estimation:** 2h

**Definition of Done:**
- Tests unitaires passent
- Coverage > 70%
- CI passe" \
  --label "us-cli,sprint-1"

# US-002: Review (5h)
echo "Creating US-002 issues..."

gh issue create \
  --title "[US-002] T002-1: Implémenter step Review (récupération données)" \
  --body "**User Story:** US-002 - Review des Métriques Quotidiennes (3 points)

**Description:**
Implémenter l'étape Review qui récupère les métriques d'hier.

**Tasks:**
- [ ] Créer \`lms/steps/review.py\`
- [ ] Implémenter \`review_metrics()\`
- [ ] Récupérer données d'hier via ProgressManager
- [ ] Calculer streak
- [ ] Afficher dans console

**Estimation:** 2h

**Definition of Done:**
- Code implémenté
- Données récupérées correctement
- Tests unitaires" \
  --label "us-review,sprint-1"

gh issue create \
  --title "[US-002] T002-2: Affichage formaté Rich pour métriques" \
  --body "**User Story:** US-002 - Review des Métriques Quotidiennes (3 points)

**Description:**
Créer un affichage Rich formaté avec tableaux et émojis.

**Tasks:**
- [ ] Table Rich avec colonnes: Métrique | Valeur
- [ ] Émojis pour chaque métrique
- [ ] Couleurs conditionnelles (objectif atteint = vert)
- [ ] Layout responsive

**Estimation:** 2h

**Definition of Done:**
- Tableau affiché correctement
- Couleurs appropriées
- Émojis visibles" \
  --label "us-review,sprint-1"

gh issue create \
  --title "[US-002] T002-3: Tests step Review" \
  --body "**User Story:** US-002 - Review des Métriques Quotidiennes (3 points)

**Description:**
Écrire les tests unitaires pour le step Review.

**Tasks:**
- [ ] Test récupération données
- [ ] Test calcul streak
- [ ] Test affichage (mock Rich)
- [ ] Coverage > 70%

**Estimation:** 1h

**Definition of Done:**
- Tests passent
- Coverage > 70%" \
  --label "us-review,sprint-1"

# US-001: WakaTime (8h)
echo "Creating US-001 issues..."

gh issue create \
  --title "[US-001] T001-1: Setup WakaTime API client" \
  --body "**User Story:** US-001 - Tracking de Formation WakaTime (5 points)

**Description:**
Créer le client API WakaTime pour récupérer les stats de temps codé.

**Tasks:**
- [ ] Créer \`lms/api_clients/wakatime_client.py\`
- [ ] Classe \`WakaTimeClient\`
- [ ] \`__init__(api_key: str)\`
- [ ] \`get_today_stats() -> dict\`
- [ ] \`get_date_stats(date: str) -> dict\`
- [ ] Authentification via token
- [ ] Requête API \`/users/current/summaries\`
- [ ] Parsing JSON response
- [ ] Gestion erreurs (rate limit 429, network, 401)

**Estimation:** 2h

**Definition of Done:**
- Client implémenté
- Gestion erreurs robuste
- Type hints ajoutés" \
  --label "us-wakatime,sprint-1"

gh issue create \
  --title "[US-001] T001-2: Intégration WakaTime dans step Formation" \
  --body "**User Story:** US-001 - Tracking de Formation WakaTime (5 points)

**Description:**
Intégrer le client WakaTime dans l'étape Formation.

**Tasks:**
- [ ] Créer \`lms/steps/formation.py\`
- [ ] Implémenter \`formation_step()\`
- [ ] Appeler \`WakaTimeClient.get_today_stats()\`
- [ ] Afficher temps codé aujourd'hui
- [ ] Afficher langages utilisés
- [ ] Alerte si < 2h avant 17h

**Estimation:** 2h

**Definition of Done:**
- Intégration fonctionnelle
- Affichage correct
- Alerte visible" \
  --label "us-wakatime,sprint-1"

gh issue create \
  --title "[US-001] T001-3: Configuration secrets (.env)" \
  --body "**User Story:** US-001 - Tracking de Formation WakaTime (5 points)

**Description:**
Configurer la gestion des secrets avec .env.

**Tasks:**
- [ ] Créer \`.env.example\`
- [ ] Documenter dans README (comment obtenir API key)
- [ ] Load avec \`python-dotenv\`
- [ ] Ajouter \`.env\` dans \`.gitignore\`

**Estimation:** 1h

**Definition of Done:**
- .env.example créé
- Documentation claire
- .env ignoré par git" \
  --label "us-wakatime,sprint-1"

gh issue create \
  --title "[US-001] T001-4: Tests WakaTime avec mocks" \
  --body "**User Story:** US-001 - Tracking de Formation WakaTime (5 points)

**Description:**
Écrire les tests avec mocks pour éviter appels API réels.

**Tasks:**
- [ ] Mock API responses (200, 401, 429, network error)
- [ ] Test parsing données
- [ ] Test gestion erreurs
- [ ] Test retry logic
- [ ] Coverage > 80%

**Estimation:** 3h

**Definition of Done:**
- Tests passent
- Coverage > 80%
- Pas d'appels API réels" \
  --label "us-wakatime,sprint-1"

# US-003: Reinforce (4h)
echo "Creating US-003 issues..."

gh issue create \
  --title "[US-003] T003-1: Implémenter step Reinforce (exercices)" \
  --body "**User Story:** US-003 - Exercices de Renforcement (3 points)

**Description:**
Implémenter l'étape Reinforce avec liste d'exercices hardcodée.

**Tasks:**
- [ ] Créer \`lms/steps/reinforce.py\`
- [ ] Implémenter \`reinforce_step()\`
- [ ] Liste hardcodée d'exercices DevOps (3-5 exercices)
- [ ] Checkbox pour marquer done (Inquirer)
- [ ] Timer simple par exercice (optional)

**Estimation:** 2h

**Definition of Done:**
- Liste affichée
- Checkbox fonctionnelle
- Exercices marquables done" \
  --label "us-reinforce,sprint-1"

gh issue create \
  --title "[US-003] T003-2: Sauvegarde progression exercices" \
  --body "**User Story:** US-003 - Exercices de Renforcement (3 points)

**Description:**
Persister les exercices complétés dans .progress.json.

**Tasks:**
- [ ] Sauvegarder exercices complétés dans progress.json
- [ ] Format: \`{date, exercises_done: [id1, id2]}\`
- [ ] Restaurer état au prochain lancement

**Estimation:** 1h

**Definition of Done:**
- Persistence fonctionnelle
- État restauré correctement" \
  --label "us-reinforce,sprint-1"

gh issue create \
  --title "[US-003] T003-3: Tests step Reinforce" \
  --body "**User Story:** US-003 - Exercices de Renforcement (3 points)

**Description:**
Écrire les tests unitaires pour Reinforce.

**Tasks:**
- [ ] Test affichage exercices
- [ ] Test marquage done
- [ ] Test persistence
- [ ] Coverage > 70%

**Estimation:** 1h

**Definition of Done:**
- Tests passent
- Coverage > 70%" \
  --label "us-reinforce,sprint-1"

# Infrastructure & CI/CD (3.5h)
echo "Creating Infrastructure issues..."

gh issue create \
  --title "[INFRA] T-CI-1: Créer GitHub Actions CI pipeline" \
  --body "**Catégorie:** Infrastructure & CI/CD

**Description:**
Configurer le pipeline CI avec GitHub Actions (tests + linting).

**Tasks:**
- [ ] Créer \`.github/workflows/ci.yml\`
- [ ] Job \`test\`: pytest + coverage
- [ ] Job \`lint\`: black, pylint, mypy
- [ ] Fail si coverage < 70%
- [ ] Trigger sur push + pull_request

**Estimation:** 2h

**Definition of Done:**
- Pipeline fonctionne
- Tests passent
- Badge vert" \
  --label "infrastructure,sprint-1"

gh issue create \
  --title "[INFRA] T-CI-2: Configurer pre-commit hooks" \
  --body "**Catégorie:** Infrastructure & CI/CD

**Description:**
Ajouter pre-commit hooks pour vérifications locales avant commit.

**Tasks:**
- [ ] Créer \`.pre-commit-config.yaml\`
- [ ] Hook black (format)
- [ ] Hook isort (imports)
- [ ] Hook trailing-whitespace
- [ ] Documenter dans README

**Estimation:** 1h

**Definition of Done:**
- Pre-commit installé
- Hooks fonctionnent
- Documentation OK" \
  --label "infrastructure,sprint-1"

gh issue create \
  --title "[INFRA] T-CI-3: Ajouter badges CI/CD au README" \
  --body "**Catégorie:** Infrastructure & CI/CD

**Description:**
Ajouter les badges de statut CI et coverage dans le README.

**Tasks:**
- [ ] Badge CI status (GitHub Actions)
- [ ] Badge coverage (codecov ou shields.io)
- [ ] Badge Python version
- [ ] Badge License

**Estimation:** 30min

**Definition of Done:**
- Badges visibles dans README
- Liens fonctionnels" \
  --label "infrastructure,sprint-1"

echo ""
echo "✓ All Sprint 1 issues created!"
echo "✓ Total: 23 issues organized by User Story"
echo ""
echo "Issues breakdown:"
echo "  - US-010 (Persistence): 4 issues (6h)"
echo "  - US-011 (CLI): 4 issues (9h)"
echo "  - US-002 (Review): 3 issues (5h)"
echo "  - US-001 (WakaTime): 4 issues (8h)"
echo "  - US-003 (Reinforce): 3 issues (4h)"
echo "  - Infrastructure: 3 issues (3.5h)"
echo ""
echo "Next: Create GitHub Project Board with gh project"
