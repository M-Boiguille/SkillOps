# URD - User Requirements Document
## SkillOps Learning Management System

**Version:** 1.0
**Date:** 9 janvier 2026
**Product Owner:** MB
**Product Manager:** PM Team
**Status:** Draft for Review

---

## 1. Executive Summary

SkillOps est un système d'apprentissage automatisé conçu pour optimiser la routine quotidienne de formation DevOps. Le système orchestre 8 étapes d'apprentissage via une interface CLI, en intégrant des APIs externes (WakaTime, Gemini, GitHub, Telegram, Obsidian) pour le tracking automatique, la génération de contenu assistée par IA, et les notifications.

**Objectif principal:** Réduire la friction dans l'apprentissage DevOps en automatisant le tracking, la révision espacée, et la progression.

---

## 2. Personas

### Persona 1: L'Apprenant DevOps Autodidacte

**Nom:** MB (Product Owner)
**Âge:** 35-45 ans
**Situation:** En reconversion professionnelle, apprend le DevOps sans mentor
**Environnement:** Ubuntu 22.04 LTS, travaille depuis un laptop

**Pain Points:**
- Éparpillement entre trop de ressources (Kubernetes, Docker, Terraform...)
- Difficulté à maintenir une discipline quotidienne
- Absence de feedback sur la progression réelle
- Tracking manuel chronophage

**Objectifs:**
- Suivre une routine structurée de 8 étapes par jour
- Mesurer sa progression avec des métriques claires
- Automatiser au maximum le suivi et la révision
- Construire un portfolio GitHub automatiquement => Utiliser l'apprentissage dans des projets portfolio le plus fidele a la realite

**Comportement:**
- Travaille 3-4h par jour sur le DevOps
- Utilise déjà WakaTime pour tracker son code
- Prend des notes dans Obsidian
- Révise avec des flashcards (Anki + plugin Obsidian)

---

## 3. User Stories (Priorisées MoSCoW)

### 🔴 MUST HAVE (MVP - Sprint 1)

#### US-001: Tracking de Formation
**En tant qu'** apprenant DevOps
**Je veux** voir mon temps de code quotidien via WakaTime
**Afin de** valider que j'atteins mon quota de Xh minimum

**Acceptance Criteria:**
- [ ] Connexion à l'API WakaTime avec token personnel
- [ ] Affichage du temps codé aujourd'hui (format: 2h 45min)
- [ ] Affichage du temps codé hier
- [ ] Alerte si temps < 2h avant 17h
- [ ] Gestion erreur API (rate limit, token invalide)

**Priorité:** P0 (Critical)
**Estimation:** 5 points
**Dépendances:** Aucune

---

#### US-002: Review des Métriques Quotidiennes
**En tant qu'** apprenant DevOps
**Je veux** voir un résumé de ma journée d'hier
**Afin de** mesurer ma progression et ajuster ma routine

**Acceptance Criteria:**
- [ ] Affichage des 8 étapes complétées/totales (ex: 7/8)
- [ ] Temps total passé hier
- [ ] Nombre de cartes Anki créées
- [ ] Streak de jours consécutifs
- [ ] Comparaison avec objectifs (vert si atteint, rouge sinon)

**Priorité:** P0 (Critical)
**Estimation:** 3 points
**Dépendances:** Système de persistence (US-010)

---

#### US-003: Exercices de Renforcement
**En tant qu'** apprenant DevOps
**Je veux** accéder à des exercices pratiques sur le concept du jour
**Afin de** consolider mes connaissances par la pratique

**Acceptance Criteria:**
- [ ] Liste d'exercices suggérés (manuellement au MVP) => prevoir des listes aleatoires (sans repetition) des meilleurs exercices de rentention + interleaving
- [ ] Marquage exercice comme "Terminé"
- [ ] Timer pour suivre le temps passé par exercice
- [ ] Historique des exercices complétés

**Priorité:** P0 (Critical)
**Estimation:** 3 points
**Dépendances:** Aucune

---

#### US-010: Persistence des Données
**En tant que** système
**Je dois** sauvegarder l'état et les métriques
**Afin de** permettre la continuité entre les sessions

**Acceptance Criteria:**
- [ ] Fichier SQLite `skillops.db` pour l'état et les métriques
- [ ] Tables pour sessions, étapes complétées, contexte, journaux et métriques
- [ ] Création automatique de la base si elle n'existe pas
- [ ] Lecture au démarrage
- [ ] Écriture après chaque étape complétée

**Priorité:** P0 (Critical)
**Estimation:** 3 points
**Dépendances:** Aucune

---

#### US-011: Interface CLI Interactive
**En tant qu'** utilisateur
**Je veux** naviguer dans l'outil avec des menus interactifs
**Afin de** ne pas avoir à mémoriser des commandes

**Acceptance Criteria:**
- [ ] Menu principal avec les 8 étapes (navigation flèches clavier) =>  + commande vim
- [ ] Sélection par Entrée
- [ ] Indicateur visuel de l'étape en cours (●) vs à faire (○)
- [ ] Option "Quitter" dans chaque menu
- [ ] Affichage coloré (Rich library) pour meilleure UX

**Priorité:** P0 (Critical)
**Estimation:** 5 points
**Dépendances:** Aucune

---

### 🟡 SHOULD HAVE (Sprint 2)

#### US-004: Génération Automatique de Flashcards
**En tant qu'** apprenant DevOps
**Je veux** que le système génère des flashcards depuis mes notes
**Afin de** gagner du temps sur la création manuelle

**Acceptance Criteria:**
- [ ] Scan du vault Obsidian (chemin configurable)
- [ ] Détection des balises #flashcard ou format Q:/A:
- [ ] Génération fichier Markdown compatible Anki
- [ ] Export vers dossier Anki (sync automatique)
- [ ] Affichage nombre de cartes générées

**Priorité:** P1 (High)
**Estimation:** 8 points
**Dépendances:** Configuration path Obsidian

---

#### US-005: Automatisation Portfolio GitHub => Exercices sur un projet capstone. Ces exercices ajoute des fonctionnalites ou de l'amelioration en fonction du niveau d'apprentissage pour finir avec un projet complet qui peut toucher tout ce que j'ai appris (nouvel US ou feature de celle ci ?)
**En tant qu'** apprenant DevOps
**Je veux** que mes labs soient automatiquement commités sur GitHub
**Afin de** construire mon portfolio sans friction

**Acceptance Criteria:**
- [ ] Détection automatique de nouveaux projets dans ~/labs/
- [ ] Génération README.md avec template (titre, description, tech stack)
- [ ] Commit automatique avec message conventionnel
- [ ] Push vers GitHub avec token personnel
- [ ] Confirmation visuelle du commit (hash + URL)

**Priorité:** P1 (High)
**Estimation:** 8 points
**Dépendances:** Configuration GitHub token

---

#### US-006: Notifications Telegram
**En tant qu'** apprenant DevOps
**Je veux** recevoir un bilan quotidien sur Telegram
**Afin de** suivre ma progression sans ouvrir l'outil

**Acceptance Criteria:**
- [ ] Envoi automatique à 20h (configurable)
- [ ] Message formaté: étapes complétées, temps codé, streak
- [ ] Bouton "Détails" pour voir plus d'infos
- [ ] Alerte si journée incomplète (<6 étapes)
- [ ] Alerte si temps effectif/log est trop faible
- [ ] Possibilité de désactiver les notifications

**Priorité:** P1 (High)
**Estimation:** 5 points
**Dépendances:** Configuration Telegram Bot

---

### 🟢 COULD HAVE (Backlog)

#### US-007: Q&A Assistée par IA
**En tant qu'** apprenant DevOps
**Je veux** expliquer un concept à l'IA et recevoir un feedback
**Afin de** valider ma compréhension profonde (Technique Feynman)

**Acceptance Criteria:**
 - [ ] Gemini pose une question ou demande une explication sur le sujet
 - [ ] Utilisateur saisit son explication (vulgarisation)
 - [ ] Gemini analyse l'explication (Clarté, Exactitude, Analogies)
 - [ ] Feedback immédiat avec correction des idées fausses
- [ ] Sauvegarde Q&A dans fichier dédié
- [ ] Historique des questions posées

**Priorité:** P2 (Medium)
**Estimation:** 8 points
**Dépendances:** Gemini API key

---

#### US-008: Méthode Zettelkasten
**En tant qu'** apprenant DevOps
**Je veux** créer des notes atomiques liées entre elles
**Afin de** construire un graphe de connaissances

**Acceptance Criteria:**
- [ ] Création note avec ID unique (timestamp)
- [ ] Détection automatique des liens [[concept]]
- [ ] Export vers Obsidian (format compatible)
- [ ] Suggestion de liens basés sur mots-clés
- [ ] Visualisation du graphe (futur)

**Priorité:** P2 (Medium)
**Estimation:** 13 points
**Dépendances:** Obsidian sync

---

#### US-009: Synthèse Quotidienne avec IA
**En tant qu'** apprenant DevOps
**Je veux** qu'une IA génère un résumé de ma journée
**Afin de** consolider mes apprentissages

**Acceptance Criteria:**
- [ ] Appel Gemini avec métriques du jour
- [ ] Génération bullet points (3-5 max)
- [ ] Identification points à améliorer
- [ ] Export vers journal Obsidian (format YAML frontmatter)
- [ ] Temps génération < 5s

**Priorité:** P2 (Medium)
**Estimation:** 5 points
**Dépendances:** Gemini API, Obsidian path

---

#### US-012: Auto-évaluation vs IA
**En tant qu'** apprenant DevOps
**Je veux** comparer ma note quotidienne avec l'évaluation de l'IA
**Afin de** identifier mes biais (trop dur/clément avec moi-même)

**Acceptance Criteria:**
- [ ] Demande de note utilisateur (1-5) dans Review
- [ ] Calcul note IA basé sur métriques (temps, étapes, qualité)
- [ ] Affichage comparaison: "Vous: 3/5 | IA: 4/5"
- [ ] Explication du delta si > 1 point
- [ ] Historique des écarts sur 30 jours
- [ ] Questionnaire "Daily though en fin de session, puis conseils pour se sentir mieux/progresser etc"

**Priorité:** P2 (Medium)
**Estimation:** 8 points
**Dépendances:** Gemini API

---

## 4. Non-Functional Requirements

### Performance
- **NFR-001:** Les commandes CLI doivent répondre en < 2 secondes (hors appels API externes)
- **NFR-002:** Les appels API doivent avoir un timeout de 10 secondes
- **NFR-003:** Le démarrage de l'application doit prendre < 1 seconde

### Sécurité
- **NFR-004:** Les API keys doivent être stockées dans GitHub Secrets (CI/CD) ou `.env` local (jamais commités)
- **NFR-005:** Le fichier `.env` doit être dans `.gitignore`
- **NFR-006:** Les tokens GitHub doivent avoir les permissions minimales (principe du moindre privilège)

### Fiabilité
- **NFR-007:** Les erreurs API doivent être gérées gracieusement (retry 3× avec backoff exponentiel)
- **NFR-008:** Backup automatique quotidien des données vers cloud storage
- **NFR-009:** Les données critiques (SQLite `skillops.db`) doivent être sauvegardées après chaque modification

### Maintenabilité
- **NFR-010:** Le code doit avoir une couverture de tests > 80%
- **NFR-011:** Le code doit passer les linters (black, pylint, mypy)
- **NFR-012:** Chaque module doit avoir une documentation (docstrings)

### Portabilité
- **NFR-013:** L'application doit fonctionner sur Linux (Ubuntu 22.04 LTS minimum)
- **NFR-014:** Support Python 3.11+
- **NFR-015:** Les dépendances doivent être fixées (requirements.txt avec versions)

### Observabilité
- **NFR-016:** Logs structurés en JSON pour parsing facile
- **NFR-017:** Un log par action importante (API call, file write, error)
- **NFR-018:** Métriques exportables (format Prometheus)

---

## 5. Out of Scope (Won't Have v1.0)

- Dashboard web temps réel
- Support multi-utilisateurs
- Synchronisation temps réel entre devices
- Intégration KodeKloud API (tracking manuel pour MVP)
- Système de gamification (badges, achievements)
- Export PDF des rapports
- Intégration Slack
- Mobile app (iOS/Android)
- Support Windows natif (WSL uniquement)

---

## 6. Success Metrics

### Métriques Utilisateur (HEART Framework)

| Métrique | Définition | Target | Mesure |
|----------|-----------|--------|--------|
| **Happiness** | Note auto-évaluation quotidienne | ≥ 4.0/5 | Moyenne sur 30 jours |
| **Engagement** | Taux de complétion des 8 étapes | ≥ 85% | (Étapes complétées / 8) × 100 |
| **Adoption** | Jours d'utilisation par mois | ≥ 25/30 | Count jours avec au moins 1 étape |
| **Retention** | Utilisation continue sur 3 mois | ≥ 90% | Jours actifs / jours totaux |
| **Task Success** | Temps moyen par session | ≤ 3h30 | Moyenne temps quotidien |

### Métriques Techniques

| Métrique | Définition | Target |
|----------|-----------|--------|
| **Availability** | Uptime de l'application | > 99% |
| **Latency** | Temps de réponse commande CLI | < 2s |
| **Error Rate** | Taux d'échec des appels API | < 1% |
| **Test Coverage** | Couverture des tests unitaires | > 80% |

---

## 7. Acceptance Criteria Globaux

Pour que le MVP soit considéré comme "DONE" :

- [ ] Les 5 user stories Must Have sont implémentées et testées
- [ ] La couverture de tests est > 80%
- [ ] Le code passe tous les linters (black, pylint, mypy)
- [ ] La documentation utilisateur est complète (README, exemples)
- [ ] Les secrets sont gérés de manière sécurisée
- [ ] Un pipeline CI/CD minimal est en place (tests automatiques)
- [ ] Les logs sont structurés et exploitables
- [ ] L'application a été testée sur Ubuntu 22.04 LTS
- [ ] Au moins 1 backup automatique fonctionne (Git ou cloud)
- [ ] Le projet est déployable en < 5 minutes (clone + install + config)

---

## 8. Risks & Mitigation

| Risk | Impact | Probabilité | Mitigation |
|------|--------|-------------|------------|
| **API Rate Limits** (WakaTime, Gemini) | High | Medium | Caching des résultats, retry avec backoff |
| **Breaking API Changes** | High | Low | Tests d'intégration, monitoring des versions |
| **Loss of Local Data** | High | Medium | Backup automatique quotidien vers cloud |
| **Obsidian Path Changes** | Medium | Medium | Configuration flexible, validation au démarrage |
| **Python Version Incompatibility** | Low | Low | CI/CD avec matrice de versions (3.11, 3.12) |

---

## 9. Dependencies & Assumptions

### Dependencies Externes
- **WakaTime API** : disponible et stable
- **GitHub API** : rate limit 5000 req/h authentifié
- **Gemini API** : accès via Google AI Studio
- **Telegram Bot API** : création bot via BotFather

### Assumptions
- L'utilisateur a déjà un compte WakaTime configuré
- L'utilisateur utilise Obsidian pour ses notes
- L'utilisateur a un compte GitHub actif
- L'environnement est Ubuntu 22.04 LTS ou supérieur
- L'utilisateur a deja un bot sur BotFather
- Python 3.11+ est installé

---

## 10. Timeline & Milestones ===> tracking par nombre d'heures, pas de jours ou de semaines

### Sprint 1 (2 semaines) - MVP Core
**Objectif:** Outil CLI fonctionnel avec tracking de base

**Deliverables:**
- US-001, US-002, US-003, US-010, US-011 complètes
- Tests unitaires (coverage > 70%)
- Documentation README de base

**Demo:** Lancement CLI → Navigation menu → Review metrics → Tracking WakaTime

---

### Sprint 2 (2 semaines) - Automatisations
**Objectif:** Intégrations API principales

**Deliverables:**
- US-004, US-005, US-006 complètes
- Tests d'intégration API
- Pipeline CI/CD basique

**Demo:** Génération flashcards → Commit GitHub auto → Notification Telegram

---

### Sprint 3 (1 semaine) - Polish & DevOps
**Objectif:** Production-ready

**Deliverables:**
- NFRs validés (sécurité, performance, observabilité)
- Documentation complète
- Monitoring en place

**Demo:** Déploiement complet sur environnement propre en < 5 min

---

## 11. Review & Approval

| Rôle | Nom | Date | Signature |
|------|-----|------|-----------|
| **Product Owner** | MB | 2026-01-09 | ✅ |
| **Product Manager** | PM Team | _Pending_ | ⏳ |
| **Tech Lead** | DevOps Engineer | _Pending_ | ⏳ |
| **QA Lead** | QA Team | _Pending_ | ⏳ |

---

## 12. Glossary

- **CLI** : Command Line Interface
- **MoSCoW** : Must have, Should have, Could have, Won't have
- **MVP** : Minimum Viable Product
- **NFR** : Non-Functional Requirement
- **Zettelkasten** : Méthode de prise de notes atomiques et liées
- **Streak** : Nombre de jours consécutifs d'utilisation
- **Flashcard** : Carte de révision espacée (Anki)

---

**Document Status:** Draft - Awaiting Review
**Next Steps:** Review by Tech Lead → Architecture Decision Records → Sprint Planning

---

*Ce document est un livrable de la phase Product Discovery et servira de référence pour le développement du MVP SkillOps.*
