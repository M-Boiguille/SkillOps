# Product Discovery Session - SkillOps LMS

> **Démarche de découverte produit appliquée au développement d'un Learning Management System personnel**  
> *Exercice de Product Management dans un contexte DevOps réel*

---

## 🎯 Contexte & Objectif de cet Exercice

Dans le cadre de mon apprentissage DevOps, j'ai voulu **aller au-delà des aspects purement techniques** en m'appropriant les méthodologies de gestion de produit utilisées dans l'industrie. Avant de coder un outil, il est crucial de **clarifier les besoins, définir le scope, et valider les hypothèses**.

Cet exercice simule une **session de découverte produit** entre un Product Manager et un Product Owner, appliquée à mon projet SkillOps. Il démontre ma capacité à :

- ✅ Structurer une réflexion produit avant le développement
- ✅ Poser les bonnes questions pour éviter le "scope creep"
- ✅ Prioriser les fonctionnalités selon la valeur métier
- ✅ Anticiper les contraintes techniques et opérationnelles
- ✅ Penser "production-ready" dès la conception

---

## 📋 Questionnaire de Découverte Produit

### **BLOC 1 : Vision & Objectifs Stratégiques**

#### **Q1. Problématique Principale**
> *Quel est votre problème principal aujourd'hui avec votre routine d'apprentissage DevOps ?*

**Pourquoi cette question ?**  
Identifier le "pain point" réel permet de construire une solution centrée sur l'utilisateur plutôt qu'une sur-ingénierie technique. En DevOps, on optimise ce qui apporte de la valeur métier.

**Exemples de réponses attendues :**
- Manque de discipline / difficulté à maintenir la régularité
- Oublis fréquents de certaines étapes
- Tracking manuel chronophage
- Absence de feedback sur la progression

---

#### **Q2. Cible Utilisateur**
> *À qui ce LMS s'adresse-t-il au-delà de vous ?*
> - Est-ce un outil personnel uniquement ?
> - Envisagez-vous de le partager avec la communauté DevOps ?
> - Cible : étudiants ? professionnels en reconversion ?

**Pourquoi cette question ?**  
La scalabilité et l'architecture dépendent du nombre d'utilisateurs. Un outil personnel peut utiliser SQLite local, tandis qu'une plateforme communautaire nécessite PostgreSQL + Redis + containerisation.

**Impact technique :**
- **Personnel** → CLI local, config YAML, données non chiffrées
- **Communautaire** → API REST, auth JWT, base de données centralisée, Docker Compose

---

#### **Q3. Définition du Succès**
> *Quel est le succès pour ce projet dans 3 mois ?*

**Pourquoi cette question ?**  
Les OKRs (Objectives & Key Results) guident les sprints de développement. Sans critères mesurables, impossible de valider le MVP.

**Exemples de métriques :**
- ✅ Taux de complétion des 8 étapes quotidiennes > 85%
- ✅ Temps gagné vs routine manuelle : 30 min/jour
- ✅ Nombre de cartes Anki générées automatiquement : 150+
- ✅ Taux d'adoption de l'outil : utilisé 6 jours/7

---

### **BLOC 2 : Priorisation Fonctionnelle (MoSCoW)**

#### **Q4. Features Essentielles vs Nice-to-Have**
> *Parmi les 8 étapes, lesquelles sont absolument essentielles pour le MVP ?*

```
1. REVIEW_METRICS       (Revue des métriques de la veille)
2. FORMATION            (KodeKloud + WakaTime tracking)
3. ANALYSIS             (Q&A assistée par IA)
4. REINFORCE            (Exercices pratiques)
5. ZETTELKASTEN         (Prise de notes atomiques)
6. FLASHCARDS           (Génération automatique de cartes)
7. PORTFOLIO            (Automatisation GitHub)
8. REFLECTION           (Synthèse quotidienne)
```

**Méthode MoSCoW appliquée :**
- **Must Have** (MVP) : Features sans lesquelles l'outil n'a pas de valeur
- **Should Have** (Sprint 2) : Fonctionnalités importantes mais non bloquantes
- **Could Have** (Backlog) : Nice-to-have pour améliorer l'UX
- **Won't Have** (Hors scope) : Idées reportées à une future version

**Exemple de priorisation :**
- 🔴 **Must** : FORMATION, REVIEW_METRICS (tracking de base)
- 🟡 **Should** : ANALYSIS (Gemini), PORTFOLIO (GitHub)
- 🟢 **Could** : FLASHCARDS (automatisation Anki)
- ⚪ **Won't** : Dashboard web temps réel (trop complexe pour MVP)

---

#### **Q5. Priorisation des Intégrations API**
> *Classez de 1 (critique) à 5 (optionnel) :*
> - [ ] Gemini (IA Q&A)
> - [ ] WakaTime (code tracking)
> - [ ] GitHub (portfolio)
> - [ ] Telegram (notifications)
> - [ ] Obsidian (notes)

**Pourquoi cette question ?**  
Chaque intégration API ajoute :
- Complexité technique (auth, rate limits, error handling)
- Coût opérationnel (monitoring, maintenance)
- Surface d'attaque sécurité (gestion des secrets)

**Approche DevOps :**  
Intégrer progressivement les API en suivant le cycle "Build → Measure → Learn". Commencer par une intégration critique, valider le pattern, puis répliquer.

---

#### **Q6. Expérience Utilisateur CLI**
> *Quel niveau d'interactivité voulez-vous ?*
> - CLI minimaliste (commandes simples)
> - CLI riche avec menus interactifs (inquirer)
> - TUI (Text User Interface) type `htop`
> - Dashboard web (futur) ?

**Impact sur le développement :**
- **CLI simple** → Typer, Click (1-2 jours)
- **CLI interactif** → Rich, Inquirer, menus complexes (3-5 jours)
- **TUI** → Textual, architecture événementielle (1-2 semaines)
- **Web** → FastAPI + React + Docker (4-6 semaines)

---

### **BLOC 3 : Contraintes Techniques & DevOps**

#### **Q7. Environnement de Déploiement**
> *Où s'exécutera le LMS ?*
> - Machine locale uniquement ?
> - Serveur distant (VPS, cloud) ?
> - Docker container ?

**Questions complémentaires :**
- Besoin d'un **scheduler** pour tâches automatiques (cron, systemd timer) ?
- Exécution manuelle ou déclenchement automatique à heures fixes ?

**Choix d'architecture selon réponse :**

| Environnement | Architecture | Outils |
|--------------|--------------|---------|
| **Local uniquement** | CLI Python + JSON local | Cron (7h00, 18h00) |
| **VPS** | Docker + PostgreSQL + Nginx | Systemd timer + Watchtower |
| **Cloud** | Kubernetes + RDS + S3 | CronJob + ArgoCD |

---

#### **Q8. Pipeline CI/CD**
> *Quelles attentes sur l'automatisation ?*
> - Tests automatisés à chaque commit ?
> - Déploiement automatique ?
> - Versioning sémantique (semver) ?

**Workflow DevOps idéal :**

```yaml
# .github/workflows/ci-cd.yml

on: [push, pull_request]

jobs:
  test:
    - pytest (unit tests)
    - black (formatting)
    - pylint (linting)
    - mypy (type checking)
  
  build:
    - Docker image build
    - Tag semver (v1.2.3)
  
  deploy:
    - Push to registry
    - Auto-deploy to production (main branch only)
```

**Apprentissage DevOps démontré :**
- ✅ Shift-left testing (tests avant merge)
- ✅ Immutable infrastructure (Docker)
- ✅ GitOps (déploiement déclaratif)
- ✅ Versioning sémantique

---

#### **Q9. Gestion des Secrets & Sécurité**
> *Comment gérer les API keys ?*
> - `.env` local ? Vault ? GitHub Secrets ?

**Bonnes pratiques DevOps :**

| Environnement | Solution | Justification |
|--------------|----------|---------------|
| **Dev local** | `.env` + `python-dotenv` | Simple, rapide, non committé |
| **CI/CD** | GitHub Secrets | Chiffrement natif, injection sécurisée |
| **Production** | HashiCorp Vault / AWS Secrets Manager | Rotation automatique, audit trail |

**Questions de sécurité additionnelles :**
- Besoin d'encryption des données locales (.progress.json) ?
- Authentification pour l'API Telegram (éviter les MITM) ?
- Principe du moindre privilège pour les tokens GitHub (read-only vs write) ?

---

#### **Q10. Observabilité & Monitoring**
> *Comment superviser l'outil en production ?*

**Les 3 piliers de l'observabilité :**

1. **Logs**
   ```python
   import structlog
   
   logger = structlog.get_logger()
   logger.info("step_completed", step="FORMATION", duration_sec=120)
   ```
   - Format structuré (JSON) pour parsing Elasticsearch/Loki
   - Rotation automatique (logrotate)

2. **Métriques**
   ```python
   from prometheus_client import Counter, Histogram
   
   steps_completed = Counter('lms_steps_completed_total', 'Total steps')
   step_duration = Histogram('lms_step_duration_seconds', 'Step duration')
   ```
   - Export Prometheus
   - Grafana dashboard

3. **Traces**
   - OpenTelemetry pour tracking des appels API (Gemini, GitHub)
   - Identifier les bottlenecks (rate limits, latence réseau)

**Alerting :**
- Telegram si étape échoue 3 fois
- Email si WakaTime tracking absent > 2 jours
- Slack pour les anomalies critiques

---

### **BLOC 4 : Persistence & Résilience**

#### **Q11. Stratégie de Backup**
> *Les données (.progress.json, .state.yaml) doivent être sauvegardées où ?*

**Options :**

| Stratégie | Implémentation | RPO/RTO |
|-----------|----------------|---------|
| **Git privé** | Auto-commit quotidien | RPO: 24h, RTO: 5 min |
| **Cloud storage** | Sync S3/GCS via rclone | RPO: 1h, RTO: 10 min |
| **Local + NAS** | rsync + cron | RPO: 12h, RTO: 30 min |

**Best practice DevOps :**
```bash
# Backup automatique quotidien
0 23 * * * cd /home/user/lms && git add . && git commit -m "Daily backup $(date)" && git push
```

**Test de disaster recovery :**
- Scénario : perte complète du disque dur
- Objectif : restaurer l'état complet en < 15 minutes
- Validation : tester la procédure 1×/mois

---

#### **Q12. Synchronisation Multi-Device**
> *Utilisez-vous le LMS sur plusieurs machines ?*

**Cas d'usage :**
- Laptop perso + Desktop travail
- WSL + Linux natif

**Solutions techniques :**

| Solution | Pros | Cons |
|----------|------|------|
| **Git** | Historique complet, merge conflicts | Commiter/pull manuel |
| **Syncthing** | Sync temps réel, P2P | Conflits si modifs simultanées |
| **Dropbox/Google Drive** | UX simple | Vendor lock-in |
| **API centralisée** | Source unique de vérité | Complexité infra (backend) |

---

### **BLOC 5 : Mesure de Succès & KPIs**

#### **Q13. Métriques de Performance**
> *Comment mesurer que le LMS fonctionne ?*

**Framework HEART (Google) :**

| Métrique | Définition | Cible |
|----------|-----------|-------|
| **Happiness** | User satisfaction score (1-5) | ≥ 4.2/5 |
| **Engagement** | Taux complétion 8 étapes | ≥ 85% |
| **Adoption** | Jours utilisés / mois | ≥ 25/30 |
| **Retention** | Utilisation continue sur 3 mois | ≥ 90% |
| **Task Success** | Temps moyen par étape | ≤ budget temps |

**Métriques techniques DevOps :**
- **Availability** : Uptime > 99.5% (si hosted)
- **Latency** : Commande LMS répond en < 2s
- **Error rate** : Taux erreur API < 1%

---

#### **Q14. Dashboards & Reporting**
> *Quels rapports voulez-vous automatiser ?*

**Hiérarchie de reporting :**

1. **Daily Briefing** (Telegram - 7h00)
   ```
   📊 Bilan d'hier :
   ✅ 8/8 étapes complétées
   ⏱️ 3h42 codé (WakaTime)
   📝 12 cartes Anki créées
   🔥 Streak : 18 jours
   
   🎯 Aujourd'hui :
   - Module Kubernetes (KodeKloud)
   - Lab : Déployer app multi-tiers
   ```

2. **Weekly Review** (Email - Dimanche 20h)
   ```
   📈 Semaine 2 - Janvier 2026
   
   Progression :
   - Formation : 18h (target: 15h) ✅
   - Portfolio : 23 commits
   - Quiz : 89% réussite
   
   Top skills acquis :
   1. Kubernetes (Deployments, Services)
   2. Terraform (AWS provider)
   3. CI/CD (GitHub Actions)
   
   Next week focus : Monitoring (Prometheus)
   ```

3. **Monthly Checkpoint** (Dashboard web)
   - Graphiques de progression (WakaTime style)
   - Heatmap des jours actifs
   - Skills rating (auto-évaluation vs quiz)
   - Comparaison avec roadmap

---

## 🚀 Livrables Post-Session

Après avoir répondu à ces questions, les documents suivants seront produits :

### 1. **URD (User Requirements Document)**

```markdown
# SkillOps LMS - User Requirements

## User Stories (Priorisées MoSCoW)

### Must Have (Sprint 1 - MVP)
- [ ] US-001: En tant qu'apprenant, je veux voir mes métriques d'hier
      pour évaluer ma progression
      **Acceptance Criteria:**
      - Affichage temps codé (WakaTime)
      - Nombre étapes complétées (8/8)
      - Streak actif
      
- [ ] US-002: En tant qu'apprenant, je veux tracker mon temps de formation
      pour valider mon quota quotidien
      **Acceptance Criteria:**
      - Intégration WakaTime API
      - Alert si < 2h codé avant 17h
```

### 2. **Cahier des Charges Technique**

```markdown
# Architecture Système

## Stack Technique Retenue
- **Langage**: Python 3.11+
- **CLI Framework**: Typer + Rich
- **Persistence**: JSON local + Git backup
- **APIs**: Gemini, WakaTime, GitHub, Telegram
- **Tests**: Pytest + Coverage > 80%
- **CI/CD**: GitHub Actions

## Diagramme C4 (Context)
[Diagramme montrant LMS, APIs externes, utilisateur]

## Plan de Tests
- Unit tests (pytest)
- Integration tests (mock API)
- E2E tests (smoke tests quotidiens)
```

### 3. **Roadmap de Développement**

```
Sprint 1 (2 semaines) - MVP Core
├─ Setup projet (poetry, pre-commit)
├─ State machine (8 steps)
├─ Persistence (JSON)
└─ CLI basique (typer)

Sprint 2 (2 semaines) - Intégrations
├─ WakaTime API
├─ Gemini API
├─ Telegram notifications
└─ Tests unitaires

Sprint 3 (1 semaine) - DevOps
├─ CI/CD pipeline
├─ Docker image
├─ Monitoring (logs structurés)
└─ Documentation
```

---

## 💡 Compétences DevOps Démontrées

Ce questionnaire illustre ma maîtrise des concepts suivants :

| Domaine | Compétences |
|---------|-------------|
| **Product Management** | Discovery, priorisation MoSCoW, OKRs, user stories |
| **Architecture** | Patterns API, persistence, state machines, observability |
| **Sécurité** | Gestion secrets, encryption, least privilege |
| **CI/CD** | Pipelines GitLab/GitHub Actions, testing automation |
| **Monitoring** | Logs structurés, métriques Prometheus, alerting |
| **Résilience** | Backup strategies, disaster recovery, multi-device sync |
| **Documentation** | ADR (Architecture Decision Records), C4 diagrams |

---

## 📚 Ressources & Méthodologies Utilisées

- **Product Discovery** : "Inspired" (Marty Cagan)
- **Priorisation** : MoSCoW Method, RICE Framework
- **Architecture** : C4 Model, Event Storming
- **DevOps** : The Phoenix Project, Accelerate (DORA metrics)
- **Observability** : The 3 Pillars (logs, metrics, traces)

---

## ✅ Conclusion

Cette démarche démontre qu'avant toute implémentation, j'applique une **méthodologie rigoureuse de découverte produit** intégrant :
- Les contraintes techniques réelles (APIs, infra, sécurité)
- La priorisation business (MVP vs nice-to-have)
- Les principes DevOps (automatisation, monitoring, résilience)

**Ce n'est pas qu'un exercice théorique** : chaque question trouvera une réponse concrète dans le code, l'architecture, et les pipelines CI/CD du projet SkillOps.

---

*Créé le 9 janvier 2026 dans le cadre de ma formation DevOps autodidacte*  
*Méthode : Simulation Product Manager ↔️ Product Owner*
