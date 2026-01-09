# Project Lifecycle - SkillOps

> **Documentation du cycle de vie complet du projet suivant les méthodologies d'entreprise**

---

## 🎯 Objectif de ce Dossier

Ce dossier documente **chaque phase du développement de SkillOps** en suivant les processus standards utilisés dans l'industrie tech. Il démontre ma capacité à :

- ✅ Suivre une méthodologie structurée (Product Management → Architecture → Développement)
- ✅ Produire des livrables professionnels à chaque étape
- ✅ Collaborer efficacement avec différents rôles (PM, PO, QA, DevOps)
- ✅ Documenter les décisions techniques de manière traçable

**Pour les recruteurs** : Ce n'est pas juste "un projet perso", c'est une **simulation complète d'un environnement professionnel** où je joue tous les rôles pour comprendre le cycle complet.

---

## 📋 Workflow Standard en Entreprise Tech

Voici le processus typique dans une entreprise utilisant Agile/Scrum avec une culture DevOps :

```
┌─────────────────────────────────────────────────────────────────┐
│                    IDEATION & DISCOVERY                         │
│  Rôles: Product Manager + Product Owner + Tech Lead            │
│  Durée: 1-2 semaines                                            │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│               01 - PRODUCT DISCOVERY SESSION                    │
│                                                                 │
│  Objectif: Comprendre le problème et valider la solution       │
│  Livrables:                                                     │
│    - Questions/Réponses entre PM et PO                          │
│    - Clarification de la vision produit                         │
│    - Priorisation initiale (MoSCoW)                             │
│                                                                 │
│  Participants:                                                  │
│    ✅ Product Manager (anime la session)                        │
│    ✅ Product Owner (définit les besoins business)              │
│    🟡 Tech Lead (consultatif - faisabilité technique)           │
│    ❌ Développeurs (pas encore impliqués)                       │
│    ❌ QA (pas encore impliqués)                                 │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 02 - URD (USER REQUIREMENTS)                    │
│                                                                 │
│  Objectif: Formaliser les besoins en user stories              │
│  Livrables:                                                     │
│    - User stories avec acceptance criteria                      │
│    - Personas détaillés                                         │
│    - Non-functional requirements (NFRs)                         │
│    - Success metrics (KPIs)                                     │
│                                                                 │
│  Processus:                                                     │
│    1. PM/PO rédigent l'URD (2-3 jours)                         │
│    2. Review Meeting avec toute l'équipe                        │
│    3. Tech Lead valide la faisabilité technique                 │
│    4. Développeurs estiment les story points                    │
│    5. QA valide la testabilité                                  │
│    6. Approbation finale et signature                           │
│                                                                 │
│  Participants à la Review:                                      │
│    ✅ Product Owner (valide alignement business)                │
│    ✅ Product Manager (présente le document)                    │
│    ✅✅ Tech Lead / DevOps Engineer (critique technique)         │
│    ✅ Développeurs (estimation, faisabilité)                    │
│    ✅ QA Lead (stratégie de test)                               │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│             03 - ADR (ARCHITECTURE DECISION RECORDS)            │
│                                                                 │
│  Objectif: Documenter les choix techniques avec justifications │
│  Livrables:                                                     │
│    - Un ADR par décision majeure                                │
│    - Format: Contexte → Options → Décision → Conséquences      │
│    - Exemples: choix du langage, framework, base de données    │
│                                                                 │
│  Processus:                                                     │
│    1. Tech Lead rédige les ADRs                                 │
│    2. Discussion technique avec l'équipe dev                    │
│    3. Validation par l'architecte (si présent)                  │
│    4. Commit dans le repo (versionnés avec le code)             │
│                                                                 │
│  Rôle du DevOps Engineer:                                       │
│    ✅✅✅ C'EST VOUS QUI PILOTEZ CETTE PHASE                     │
│    - Vous rédigez les ADRs techniques                           │
│    - Vous justifiez vos choix (Python vs Go, CLI vs Web, etc.) │
│    - Le PM valide juste la cohérence avec l'URD                 │
│                                                                 │
│  Participants:                                                  │
│    ✅✅✅ Tech Lead / DevOps Engineer (rédacteur principal)      │
│    ✅ Développeurs seniors (review & feedback)                  │
│    🟡 Product Manager (validation cohérence URD)                │
│    ❌ Product Owner (n'a pas besoin de comprendre les détails)  │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    04 - SPRINT PLANNING                         │
│                                                                 │
│  Objectif: Découper le travail en sprints et tasks             │
│  Livrables:                                                     │
│    - Backlog priorisé (user stories triées)                     │
│    - Sprint 1 défini avec objectif clair                        │
│    - Tasks techniques créées (sous-tâches des user stories)     │
│    - Definition of Done validée                                 │
│                                                                 │
│  Processus (réunion 2-4h):                                      │
│    1. PO présente les user stories prioritaires                 │
│    2. Équipe dev estime chaque story (Planning Poker)           │
│    3. Identification des dépendances techniques                 │
│    4. Validation de la vélocité (combien de points par sprint)  │
│    5. Sélection des stories pour Sprint 1                       │
│    6. Découpage en tasks dans Jira/GitHub Projects              │
│                                                                 │
│  Participants:                                                  │
│    ✅✅ Product Owner (priorise les stories)                    │
│    ✅✅ Scrum Master (facilite la réunion)                      │
│    ✅✅✅ TOUTE L'ÉQUIPE DEV (estimation obligatoire)            │
│    ✅✅✅ DevOps Engineer (estime l'infra, CI/CD)                │
│    ✅ QA (valide la testabilité dans le sprint)                 │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    05 - DEVELOPMENT (Sprint)                    │
│                                                                 │
│  Objectif: Implémenter les user stories du sprint              │
│  Durée: 1-3 semaines (typiquement 2 semaines)                   │
│                                                                 │
│  Workflow quotidien:                                            │
│    - Daily Stand-up (15 min) : "Hier / Aujourd'hui / Blocages" │
│    - Développement avec TDD (Test-Driven Development)           │
│    - Pull Requests + Code Review (pair minimum)                 │
│    - CI/CD automatique (tests, linting, build)                  │
│    - Merge après approbation                                    │
│                                                                 │
│  Rôle du DevOps Engineer:                                       │
│    ✅ Développer le code (évidemment)                           │
│    ✅ Setup de l'infrastructure (Docker, K8s si besoin)         │
│    ✅ Configuration du pipeline CI/CD                           │
│    ✅ Monitoring & Observabilité (logs, métriques)              │
│    ✅ Sécurité (secrets management, scanning)                   │
│    ✅ Documentation technique                                   │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    06 - SPRINT REVIEW & DEMO                    │
│                                                                 │
│  Objectif: Démontrer le travail accompli aux stakeholders      │
│  Durée: 1-2h à la fin du sprint                                 │
│                                                                 │
│  Contenu:                                                       │
│    - Demo des user stories complétées (environnement réel)      │
│    - Métriques du sprint (vélocité, bugs, couverture tests)     │
│    - Feedback des stakeholders                                  │
│    - Ajustement du backlog si besoin                            │
│                                                                 │
│  Participants:                                                  │
│    ✅ Product Owner (valide que c'est conforme aux attentes)    │
│    ✅ Équipe dev (présente le travail)                          │
│    ✅ Stakeholders (donnent du feedback)                        │
│    🟡 Utilisateurs finaux (si possible)                         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    07 - SPRINT RETROSPECTIVE                    │
│                                                                 │
│  Objectif: S'améliorer continuellement (processus, outils)     │
│  Durée: 1-2h après la Sprint Review                             │
│                                                                 │
│  Format (Start/Stop/Continue):                                  │
│    - Qu'est-ce qui a bien marché ? (Continue)                   │
│    - Qu'est-ce qui a mal marché ? (Stop)                        │
│    - Qu'est-ce qu'on devrait essayer ? (Start)                  │
│                                                                 │
│  Exemples de sujets:                                            │
│    - "Les PRs prennent trop de temps" → Action: limit 24h       │
│    - "Les tests flaky ralentissent la CI" → Action: fix tests   │
│    - "Manque de pair programming" → Action: 2h/jour en binôme   │
│                                                                 │
│  Participants:                                                  │
│    ✅✅ TOUTE L'ÉQUIPE (dev, QA, DevOps)                        │
│    ✅ Scrum Master (facilite)                                   │
│    ❌ Product Owner (optionnel, souvent absent)                 │
│    ❌ Management (jamais présent - safe space)                  │
└─────────────────────────────────────────────────────────────────┘

       │
       └──────┐
              │  Retour au Sprint Planning pour Sprint 2
              ▼  (cycle continu jusqu'au release)
```

---

## 📁 Structure de ce Dossier

Chaque fichier correspond à une phase du workflow ci-dessus :

```
project-lifecycle/
├── README.md                                    # Ce fichier
├── 01-product-discovery-session.md             # Phase Discovery (Q&A PM/PO)
├── 02-urd-user-requirements-document.md         # User stories, NFRs, KPIs
├── 03-adr-architecture-decision-records.md      # Choix techniques justifiés
├── 04-sprint-planning-sprint-1.md               # Backlog, estimation, tasks
├── 05-development-logs.md                       # Journal de développement
├── 06-sprint-review-demo.md                     # Démo et feedback
└── 07-retrospective-sprint-1.md                 # Amélioration continue
```

---

## 🎭 Mon Rôle dans ce Projet (Multi-Casquettes)

Dans une vraie entreprise, chaque phase implique des rôles différents. Pour SkillOps, **je joue tous les rôles** pour comprendre le cycle complet :

| Phase | Rôle Principal | Ce que je fais |
|-------|---------------|----------------|
| **01 - Discovery** | Product Owner | Je définis mes besoins d'apprenant DevOps |
| **02 - URD** | Product Manager | Je formalise en user stories professionnelles |
| **03 - ADR** | Tech Lead / DevOps Engineer | Je documente mes choix techniques (Python, CLI, APIs) |
| **04 - Sprint Planning** | Scrum Master + Dev | J'estime et je planifie le sprint |
| **05 - Development** | DevOps Engineer | Je code + setup infra + CI/CD |
| **06 - Sprint Review** | Product Owner | Je valide que ça répond à mes besoins |
| **07 - Retrospective** | Toute l'équipe | J'identifie les améliorations |

**Pourquoi c'est important pour un recruteur ?**

✅ **Démontre une vision 360°** : Je ne suis pas "juste un dev", je comprends le business, le produit, et l'infra  
✅ **Culture DevOps** : Je casse les silos entre dev, ops, et produit  
✅ **Autonomie** : Je sais structurer un projet de A à Z  
✅ **Rigueur méthodologique** : Je ne code pas "au feeling", je suis un processus  
✅ **Documentation** : Chaque décision est traçable et justifiée

---

## 🚀 Comment Lire ce Dossier (Pour les Recruteurs)

### Si vous avez 5 minutes :
1. Lisez [01-product-discovery-session.md](01-product-discovery-session.md) → Vous verrez ma capacité à clarifier les besoins
2. Parcourez [02-urd-user-requirements-document.md](02-urd-user-requirements-document.md) → User stories professionnelles
3. Regardez [03-adr-architecture-decision-records.md](03-adr-architecture-decision-records.md) → Mes choix techniques justifiés

### Si vous avez 15 minutes :
- Lisez tout le dossier dans l'ordre chronologique (01 → 07)
- Vous comprendrez exactement comment je travaille et pourquoi je prends chaque décision

### Si vous avez 30 minutes :
- Lisez le dossier + consultez le code dans `/src`
- Vérifiez la cohérence entre les specs (URD) et l'implémentation
- Regardez le pipeline CI/CD dans `.github/workflows`

---

## 📚 Références & Standards Appliqués

Ce projet suit les méthodologies et standards suivants :

**Product Management :**
- Product Discovery (Marty Cagan - "Inspired")
- User Stories (format As a... I want... So that...)
- MoSCoW Prioritization

**Architecture :**
- ADR (Architecture Decision Records) - Michael Nygard
- C4 Model pour les diagrammes d'architecture

**Agile/Scrum :**
- Sprints de 2 semaines
- Daily Stand-ups
- Sprint Review & Retrospective

**DevOps :**
- GitFlow / Trunk-Based Development
- Conventional Commits
- CI/CD automatique
- Infrastructure as Code
- Observabilité (Logs, Metrics, Traces)

**Qualité :**
- Test-Driven Development (TDD)
- Code Review obligatoire
- Coverage > 80%
- Definition of Done

---

## 🎓 Apprentissage Démontré

Ce dossier prouve que je comprends :

1. **Le cycle de vie produit** (Ideation → Discovery → Development → Release)
2. **La collaboration inter-équipes** (PM, PO, Dev, QA, DevOps)
3. **La documentation technique** (ADRs, user stories, specs)
4. **La priorisation** (MoSCoW, story points, vélocité)
5. **Les méthodologies Agile** (Scrum, sprints, retrospectives)
6. **La culture DevOps** (automation, CI/CD, observabilité)

**Ce n'est pas un simple projet GitHub**, c'est une **simulation complète d'un environnement professionnel** avec toute la rigueur méthodologique d'une entreprise tech.

---

## 📞 Contact

Si vous avez des questions sur ma méthodologie ou sur les choix effectués à chaque phase, n'hésitez pas à me contacter.

**MB** - Apprenant DevOps  
📧 [votre-email]  
💼 [LinkedIn]  
🐙 [GitHub]

---

*Document créé le 9 janvier 2026 dans le cadre du développement de SkillOps LMS*
