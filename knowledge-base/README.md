# Knowledge Base - Concepts DevOps & Product Management

> **Fiches théoriques synthétiques couvrant les concepts utilisés dans SkillOps**

---

## 🎯 Objectif

Ce dossier contient des fiches pédagogiques sur les **méthodologies, frameworks et bonnes pratiques** appliquées dans le développement de SkillOps. Chaque fiche est structurée pour un apprentissage rapide et efficace.

**Public cible :** 
- Apprenants DevOps souhaitant comprendre les concepts au-delà des outils
- Développeurs curieux de la méthodologie produit
- Recruteurs voulant valider ma compréhension théorique

---

## 📚 Liste des Fiches

### 🔵 Product Management & Méthodologies Agiles

| Fiche | Sujet | Concepts Clés |
|-------|-------|---------------|
| [KB-01](KB-01-product-discovery.md) | **Product Discovery** | Discovery process, PM/PO roles, problem validation |
| [KB-02](KB-02-user-stories.md) | **User Stories & Acceptance Criteria** | Format As a/I want/So that, INVEST, AC |
| [KB-03](KB-03-moscow-prioritization.md) | **Priorisation MoSCoW** | Must/Should/Could/Won't Have |
| [KB-04](KB-04-sprint-planning.md) | **Sprint Planning** | Story points, vélocité, planning poker |
| [KB-05](KB-05-definition-of-done.md) | **Definition of Done** | Critères qualité, checklist |
| [KB-06](KB-06-retrospective.md) | **Rétrospective Agile** | Start/Stop/Continue, amélioration continue |

### 🟢 Architecture & Documentation Technique

| Fiche | Sujet | Concepts Clés |
|-------|-------|---------------|
| [KB-07](KB-07-architecture-decision-records.md) | **ADR (Architecture Decision Records)** | Format ADR, traçabilité décisions |
| [KB-08](KB-08-software-architecture-patterns.md) | **Patterns d'Architecture** | State Machine, Event-Driven, MVC |
| [KB-09](KB-09-c4-model.md) | **C4 Model** | Context, Containers, Components, Code |
| [KB-10](KB-10-technical-documentation.md) | **Documentation Technique** | README, API docs, docstrings |

### 🟡 DevOps & CI/CD

| Fiche | Sujet | Concepts Clés |
|-------|-------|---------------|
| [KB-11](KB-11-cicd-fundamentals.md) | **CI/CD Fundamentals** | Continuous Integration, Continuous Deployment |
| [KB-12](KB-12-testing-strategies.md) | **Stratégies de Tests** | Unit, Integration, E2E, TDD |
| [KB-13](KB-13-code-quality.md) | **Qualité de Code** | Linting, formatting, coverage |
| [KB-14](KB-14-secrets-management.md) | **Gestion des Secrets** | .env, Vault, cloud secrets |
| [KB-15](KB-15-observability.md) | **Observabilité** | Logs, métriques, traces (3 piliers) |

### 🟠 Git & Versioning

| Fiche | Sujet | Concepts Clés |
|-------|-------|---------------|
| [KB-16](KB-16-conventional-commits.md) | **Conventional Commits** | Format, types (feat/fix/docs), changelog |
| [KB-17](KB-17-gitflow-vs-trunk.md) | **GitFlow vs Trunk-Based** | Branching strategies |
| [KB-18](KB-18-semantic-versioning.md) | **Semantic Versioning (SemVer)** | MAJOR.MINOR.PATCH |

### 🔴 Concepts Transverses

| Fiche | Sujet | Concepts Clés |
|-------|-------|---------------|
| [KB-19](KB-19-shift-left-testing.md) | **Shift-Left Testing** | Tests précoces, prévention |
| [KB-20](KB-20-infrastructure-as-code.md) | **Infrastructure as Code** | Declarative vs Imperative |
| [KB-21](KB-21-devops-culture.md) | **Culture DevOps** | CALMS, collaboration, automation |

---

## 🎓 Comment Utiliser ces Fiches ?

### Pour l'Apprentissage
1. **Lecture séquentielle** : Commencer par KB-01 et progresser
2. **Lecture thématique** : Choisir un domaine (Product, DevOps, etc.)
3. **Révision espacée** : Relire les fiches à J+1, J+7, J+30

### Pour les Révisions
- Chaque fiche = 5-10 minutes de lecture
- Format synthétique pour révision rapide avant entretien
- Exemples concrets tirés du projet SkillOps

### Pour les Recruteurs
- Valider ma compréhension théorique des concepts
- Voir comment je les applique dans le projet
- Liens entre théorie (knowledge-base) et pratique (project-lifecycle)

---

## 📖 Structure d'une Fiche Type

Chaque fiche suit ce format :

```markdown
# [Titre du Concept]

## 📝 Définition

Explication concise en 2-3 phrases.

## 🎯 Concepts Clés

- Point clé 1
- Point clé 2
- Point clé 3

## 💡 Exemple Concret (SkillOps)

Illustration avec le projet réel.

## ✅ Bonnes Pratiques

- Do ✅
- Don't ❌

## 📚 Ressources pour Approfondir

- Livre de référence
- Article/blog
- Documentation officielle
- Cours en ligne

## 🔗 Voir Aussi

Liens vers autres fiches connexes.
```

---

## 🔗 Liens avec le Projet

| Concept (Knowledge Base) | Application (Project Lifecycle) |
|-------------------------|--------------------------------|
| **KB-01 Product Discovery** | [01-product-discovery-session.md](../project-lifecycle/01-product-discovery-session.md) |
| **KB-02 User Stories** | [02-urd-user-requirements-document.md](../project-lifecycle/02-urd-user-requirements-document.md) |
| **KB-07 ADR** | [03-adr-architecture-decision-records.md](../project-lifecycle/03-adr-architecture-decision-records.md) |
| **KB-04 Sprint Planning** | [04-sprint-planning-sprint-1.md](../project-lifecycle/04-sprint-planning-sprint-1.md) |

---

## 🎯 Progression d'Apprentissage Suggérée

### Semaine 1 : Product Management
- [ ] KB-01: Product Discovery
- [ ] KB-02: User Stories
- [ ] KB-03: MoSCoW Prioritization
- [ ] KB-04: Sprint Planning

### Semaine 2 : Architecture & DevOps
- [ ] KB-07: ADR
- [ ] KB-08: Architecture Patterns
- [ ] KB-11: CI/CD Fundamentals
- [ ] KB-12: Testing Strategies

### Semaine 3 : Qualité & Culture
- [ ] KB-13: Code Quality
- [ ] KB-15: Observability
- [ ] KB-21: DevOps Culture
- [ ] KB-16: Conventional Commits

---

## 📊 Métriques d'Apprentissage

Pour chaque fiche, je peux tracker :
- [ ] Lue (première fois)
- [ ] Comprise (capable d'expliquer)
- [ ] Appliquée (utilisée dans SkillOps)
- [ ] Maîtrisée (capable de former quelqu'un)

---

## 🔄 Mise à Jour

Ce dossier évolue avec mon apprentissage :
- Ajout de nouvelles fiches si découverte de concepts
- Enrichissement avec exemples réels du projet
- Correction suite à feedback ou approfondissement

**Dernière mise à jour :** 9 janvier 2026

---

## 📞 Feedback

Si certaines fiches manquent de clarté ou de profondeur, n'hésitez pas à me le signaler. C'est aussi un exercice d'amélioration continue !

---

*Ce dossier démontre ma volonté de comprendre les concepts théoriques au-delà de l'implémentation technique pure.*
