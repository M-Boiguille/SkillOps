# SkillOps 🚀

> **Un Learning Management System (LMS) CLI intelligent pour orchestrer mon apprentissage DevOps avec IA, tracking automatique et notifications.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![DevOps](https://img.shields.io/badge/Focus-DevOps%20Learning-orange.svg)]()
[![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)]()

---

## 📖 Vue d'Ensemble

**SkillOps** est un système d'apprentissage automatisé conçu pour optimiser ma routine quotidienne de formation DevOps. Plutôt que de gérer manuellement mon tracking, mes notes et mes révisions, j'ai construit un outil CLI qui orchestre intelligemment mes 8 étapes d'apprentissage quotidiennes.

### 🎯 Le Problème Résolu

En tant qu'apprenant DevOps autodidacte, je faisais face à :
- ❌ **Manque de discipline** : oublier certaines étapes de ma routine
- ❌ **Tracking manuel chronophage** : copier-coller des métriques entre outils
- ❌ **Absence de feedback** : difficile de mesurer ma progression
- ❌ **Perte de contexte** : notes dispersées, pas de vision d'ensemble

### ✅ La Solution

Un **outil CLI Python** qui :
- 🤖 Automatise le tracking de mon temps de code (WakaTime)
- 🧠 Génère des questions/réponses contextuelles via IA (Gemini)
- 📝 Synchronise mes notes Obsidian et flashcards Anki
- 🔔 M'envoie des rappels et bilans quotidiens (Telegram)
- 📊 Visualise ma progression avec des métriques claires
- 🔄 Gère mon portfolio GitHub automatiquement

---

## 🏗️ Architecture Système

```
┌──────────────────────────────────────────────────────────────┐
│                    SkillOps CLI Engine                       │
│                   State Machine (8 Steps)                    │
└────────────┬─────────────────────────────────┬───────────────┘
             │                                 │
    ┌────────▼─────────┐              ┌───────▼────────┐
    │  User Interface  │              │ Data Tracking  │
    │  ├─ Typer (CLI)  │              │ ├─ .state.yaml │
    │  ├─ Rich (UI)    │              │ ├─ .progress   │
    │  └─ Inquirer     │              │ └─ .metrics    │
    └──────────────────┘              └────────────────┘
             │
    ┌────────┴────────────────────────────────────────┐
    │                                                  │
┌───▼──────────┐  ┌──────────┐  ┌─────────┐  ┌──────▼──────┐
│ API Clients  │  │ Workflows│  │ Storage │  │ Integration │
│              │  │          │  │         │  │             │
│ ├─ Gemini AI│  │ ├─ Steps │  │ ├─ JSON │  │ ├─ Obsidian │
│ ├─ WakaTime │  │ ├─ State │  │ ├─ YAML │  │ ├─ GitHub   │
│ ├─ GitHub   │  │ └─ Events│  │ └─ CSV  │  │ └─ Telegram │
│ └─ Telegram │  │          │  │         │  │             │
└──────────────┘  └──────────┘  └─────────┘  └─────────────┘
```

---

## 🎨 Fonctionnalités Principales

### 1️⃣ **Review Metrics** 📊
- Affiche les métriques de la veille (temps codé, étapes complétées)
- Compare avec les objectifs quotidiens
- Calcule le "streak" de jours consécutifs

### 2️⃣ **Formation Tracking** ⏱️
- Intégration WakaTime pour tracking automatique du code
- Suivi des sessions KodeKloud
- Alertes si quota quotidien non atteint

### 3️⃣ **Analysis with AI** 🧠
- Pose des questions sur les concepts étudiés
- Gemini génère des réponses contextuelles
- Stocke les Q&A pour révisions futures

### 4️⃣ **Reinforcement** 💪
- Génère des exercices pratiques personnalisés
- Labs hands-on basés sur la progression
- Validation des acquis

### 5️⃣ **Zettelkasten Notes** 📝
- Prise de notes atomiques (méthode Zettelkasten)
- Synchronisation avec Obsidian
- Liens entre concepts

### 6️⃣ **Flashcards Generation** 🃏
- Création automatique de cartes Anki depuis les notes
- Export compatible avec Obsidian Spaced Repetition
- Tags intelligents par sujet

### 7️⃣ **Portfolio Automation** 🔧
- Commits automatiques des projets sur GitHub
- Génération de README pour chaque lab
- Tracking des contributions

### 8️⃣ **Daily Reflection** 🌅
- Synthèse quotidienne avec IA
- Export vers journal Obsidian
- Identification des points d'amélioration

---

## 🛠️ Stack Technique (Provisoire)

| Catégorie | Technologies |
|-----------|-------------|
| **Langage** | Python 3.11+ |
| **CLI Framework** | Typer, Rich, Inquirer |
| **APIs** | Google Gemini, WakaTime, GitHub REST API, Telegram Bot API |
| **Persistence** | JSON, YAML, CSV |
| **Testing** | Pytest, Coverage, Mock |
| **CI/CD** | GitHub Actions |
| **Containerisation** | Docker (prévu) |
| **Documentation** | Markdown, Mermaid diagrams |

---

## 🚀 Installation (Prévu)

```bash
# Cloner le repository
git clone https://github.com/votre-username/SkillOps.git
cd SkillOps

# Installer les dépendances
pip install -r requirements.txt

# Configuration
cp config.yaml.example config.yaml
# Éditer config.yaml avec vos API keys

# Lancer le CLI
python main.py start
```

---

## 📋 Workflow Quotidien

```bash
# Démarrer la routine du matin (7h00)
skillops start

# Commande affiche :
┌─────────────────────────────────────────┐
│  SkillOps - Routine du 9 janvier 2026  │
├─────────────────────────────────────────┤
│ 📊 Métriques d'hier :                   │
│   ✅ 8/8 étapes complétées              │
│   ⏱️  3h42 codé (WakaTime)              │
│   🔥 Streak : 18 jours                  │
├─────────────────────────────────────────┤
│ 🎯 Programme aujourd'hui :              │
│   1. [●○○○○○○○] Review Metrics          │
│   2. [○○○○○○○○] Formation               │
│   ...                                   │
└─────────────────────────────────────────┘

# Navigation interactive
> Appuyez sur Entrée pour Step 1: Review Metrics

# Notification Telegram automatique en fin de journée
📱 "✅ Bilan : 8/8 étapes | 4h12 codé | 15 cartes créées"
```

---

## 🎓 Apprentissage DevOps Démontré

Ce projet illustre ma maîtrise des concepts DevOps suivants :

### 🔹 Product Management
- ✅ Product Discovery (voir [Product-Discovery-Session.md](Product-Discovery-Session.md))
- ✅ Priorisation MoSCoW (MVP vs Nice-to-have)
- ✅ User Stories avec Acceptance Criteria
- ✅ OKRs et métriques de succès

### 🔹 Architecture & Design
- ✅ State Machine Pattern
- ✅ API Client abstraction
- ✅ Event-driven architecture
- ✅ Separation of Concerns

### 🔹 DevOps Practices
- ✅ Configuration as Code (YAML)
- ✅ Secrets Management (environment variables)
- ✅ Logging structuré (JSON)
- ✅ CI/CD Pipeline (GitHub Actions - prévu)
- ✅ Containerisation (Docker - prévu)

### 🔹 Observabilité
- ✅ Logs structurés
- ✅ Métriques personnalisées
- ✅ Alerting (Telegram)
- ✅ Dashboard de progression

### 🔹 Automatisation
- ✅ Cron jobs pour exécution planifiée
- ✅ Webhooks GitHub
- ✅ Bot Telegram
- ✅ Génération automatique de contenu (flashcards, README)

---

## 📊 Roadmap

### ✅ Phase 1 : Conception (En cours)
- [ ] Product Discovery Session
- [ ] Documentation technique
- [ ] Définition des besoins et priorisation

### 🚧 Phase 2 : MVP Core (En attente)
- [ ] Machine à états pour orchestration
- [ ] Interface CLI interactive
- [ ] Système de persistence des données
- [ ] Tests de base

### 📅 Phase 3 : Intégrations Externes (En attente)
- [ ] API de tracking de code
- [ ] Intelligence artificielle pour Q&A
- [ ] Automatisation portfolio
- [ ] Notifications temps réel
- [ ] Tests d'intégration

### 📅 Phase 4 : DevOps Pipeline (En attente)
- [ ] Automatisation CI/CD
- [ ] Containerisation
- [ ] Observabilité (logs, métriques, alertes)
- [ ] Documentation complète

### 🔮 Phase 5 : Optimisations (En attente)
- [ ] Interface web de visualisation
- [ ] Synchronisation multi-device
- [ ] Extensions et plugins
- [ ] Ouverture communautaire

---

## 🤝 Contribution

Ce projet est actuellement un outil d'apprentissage personnel, mais les suggestions sont les bienvenues !

Si vous souhaitez :
- 💡 Proposer une amélioration
- 🐛 Signaler un bug
- 📖 Améliorer la documentation
- 🔀 Soumettre une Pull Request

N'hésitez pas à ouvrir une **Issue** sur GitHub.

---

## 📚 Ressources & Inspirations

### Méthodologies Appliquées
- **Product Discovery** : "Inspired" - Marty Cagan
- **DevOps** : "The Phoenix Project", "Accelerate"
- **Learning** : "Make It Stick", méthode Zettelkasten, Deep Work
- **Architecture** : C4 Model, Event Storming

---

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE) pour plus de détails.

---

## ⭐ Pourquoi ce Projet ?

> *"La meilleure façon d'apprendre DevOps, c'est de l'appliquer à un problème réel. SkillOps est né de ma frustration à gérer manuellement ma routine d'apprentissage. Plutôt que d'utiliser 10 outils différents, j'ai construit un système qui les orchestre tous."*

Ce projet démontre que je ne me contente pas d'apprendre des outils en isolation, mais que je comprends :
- 🎯 **Le cycle de vie produit** (discovery, MVP, itération)
- 🏗️ **L'architecture distribuée** (APIs, état, persistence)
- 🔒 **La sécurité** (secrets, encryption, least privilege)
- 📊 **L'observabilité** (logs, métriques, alerting)
- ♻️ **L'automatisation** (CI/CD, cron, webhooks)

**SkillOps n'est pas juste un projet d'apprentissage, c'est un outil que j'utilise quotidiennement pour devenir DevOps Engineer.**

---

<div align="center">

**⭐ Si ce projet vous inspire, n'hésitez pas à le star !**

</div>
