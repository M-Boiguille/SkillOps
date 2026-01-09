# Architecture Decision Records (ADR)

## 📝 Définition

Un **Architecture Decision Record (ADR)** est un document court qui capture une **décision architecturale importante**, le **contexte** dans lequel elle a été prise, les **alternatives considérées**, et les **conséquences** de ce choix. 

**Objectif :** Tracer les décisions techniques majeures pour comprendre **pourquoi** le système est construit ainsi, même des mois/années plus tard.

**En une phrase :** "On a choisi X plutôt que Y car Z, et voici les impacts."

---

## 🎯 Concepts Clés

### 1. Format ADR Standard (Michael Nygard)

```markdown
# ADR-XXX: [Titre de la Décision]

## Statut
[Proposé | Accepté | Déprécié | Remplacé par ADR-YYY]

## Contexte
Quel problème devons-nous résoudre ?
Quelles sont les contraintes ?

## Décision
Quelle solution avons-nous choisie ?

## Conséquences
Quels sont les impacts (positifs et négatifs) ?
```

### 2. Quand Créer un ADR ?

**Créer un ADR pour :**
- ✅ Choix de langage (Python vs Go vs Rust)
- ✅ Choix d'architecture (Monolithe vs Microservices)
- ✅ Choix de base de données (PostgreSQL vs MongoDB vs JSON)
- ✅ Pattern d'architecture (State Machine vs Event-Driven)
- ✅ Stratégie de déploiement (Docker vs Kubernetes vs Bare Metal)
- ✅ Gestion des secrets (Vault vs .env vs Cloud Secrets)

**Ne PAS créer d'ADR pour :**
- ❌ Choix trivial (quelle librairie de parsing JSON)
- ❌ Décisions réversibles facilement (format de log)
- ❌ Préférences personnelles sans impact (tabs vs spaces)

### 3. Statuts d'un ADR

| Statut | Signification | Quand ? |
|--------|---------------|---------|
| **Proposé** | En discussion, pas encore validé | Phase de review |
| **Accepté** | Validé et appliqué | Après consensus équipe |
| **Déprécié** | N'est plus recommandé mais existe encore | Migration en cours |
| **Remplacé** | Obsolète, remplacé par ADR-YYY | Après pivot technique |

### 4. Options Considérées

Toujours documenter **au moins 2-3 alternatives** :
- L'option choisie
- Les options rejetées avec justification

**Pourquoi ?** Éviter que quelqu'un demande "Pourquoi pas X ?" dans 6 mois.

---

## 💡 Exemple Concret (SkillOps)

### ADR-001: Choix du Langage (Python vs Go)

```markdown
# ADR-001: Choix du Langage de Programmation

**Date:** 2026-01-09
**Statut:** ✅ Accepté

## Contexte
Nous devons choisir un langage pour développer SkillOps CLI.
Critères: rapidité dev (MVP 2 semaines), écosystème APIs, portabilité.

## Options Considérées

### Option A: Python 3.11+
Pour:
- ✅ Écosystème riche (requests, typer, rich)
- ✅ Prototypage rapide
- ✅ Je connais déjà Python

Contre:
- ❌ Performance moindre
- ❌ Pas de binaire statique

### Option B: Go
Pour:
- ✅ Binaire statique
- ✅ Performance excellente

Contre:
- ❌ Courbe d'apprentissage
- ❌ Écosystème moins riche pour IA/ML

## Décision
**Choix: Python 3.11+**

Justification: Le projet est d'abord un outil d'apprentissage.
Python permet de se concentrer sur DevOps (CI/CD, infra) plutôt 
que sur la syntaxe du langage.

## Conséquences

Positives:
- Développement MVP rapide (2 semaines tenable)
- Nombreux exemples pour APIs tierces

Négatives:
- Nécessite Python installé (pas de binaire standalone)
- Performance moindre (acceptable pour CLI quotidien)

Mitigations:
- Poetry pour gestion dépendances
- Typage strict avec mypy
```

---

## ✅ Bonnes Pratiques

### Do ✅

- **Écrire l'ADR dès la décision prise** : Pas 3 mois après quand on a oublié le contexte
- **Être factuel** : "Python a 200k+ packages sur PyPI" plutôt que "Python c'est mieux"
- **Documenter les alternatives** : Montrer qu'on a réfléchi aux options
- **Expliquer le contexte** : Contraintes, deadlines, compétences équipe
- **Numéroter séquentiellement** : ADR-001, ADR-002... (historique clair)
- **Committer dans le repo** : Les ADRs vivent avec le code (docs/ ou adr/)
- **Mettre à jour le statut** : Si une décision est remplacée, marquer "Déprécié"

### Don't ❌

- **Ne pas réécrire l'histoire** : Si on change d'avis, créer ADR-YYY qui remplace ADR-XXX
- **Ne pas être vague** : "Microservices parce que c'est moderne" ❌
- **Ne pas oublier les conséquences négatives** : Toute décision a des trade-offs
- **Ne pas faire des ADRs de 50 pages** : 1-2 pages max, synthétique
- **Ne pas documenter des non-décisions** : "On va sûrement faire X un jour" ❌

---

## 📚 Ressources pour Approfondir

### Articles Fondateurs 📝

1. **"Documenting Architecture Decisions"** - Michael Nygard (2011)  
   → Article original qui a lancé le concept  
   → [cognitect.com](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)

2. **"ADR GitHub Organization"**  
   → Templates et exemples d'ADRs  
   → [adr.github.io](https://adr.github.io/)

3. **"Lightweight Architecture Decision Records"** - ThoughtWorks  
   → [thoughtworks.com](https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records)

### Templates & Outils 🛠️

- **adr-tools** : CLI pour créer/gérer ADRs  
  ```bash
  brew install adr-tools
  adr init docs/architecture/decisions
  adr new "Use PostgreSQL for persistence"
  ```

- **MADR (Markdown ADR)** : Format Markdown enrichi  
  → [github.com/adr/madr](https://github.com/adr/madr)

- **ADR Tools VSCode Extension**  
  → Snippets pour créer ADRs rapidement

### Exemples Réels 🌍

- **Spotify Engineering** : ADRs publics sur GitHub
- **GOV.UK** : Architecture decisions du site gouvernemental UK
- **Architecture Decision Records - AWS**

### Livres 📖

- **"Software Architecture for Developers"** - Simon Brown  
  → Intègre les ADRs dans le C4 Model

---

## 🔗 Voir Aussi

- [KB-08: Software Architecture Patterns](KB-08-software-architecture-patterns.md) - Patterns à documenter via ADRs
- [KB-09: C4 Model](KB-09-c4-model.md) - Diagrammes d'architecture complémentaires
- [KB-10: Technical Documentation](KB-10-technical-documentation.md) - Autres types de docs

---

## 🎯 Application dans SkillOps

### ADRs Documentés

Dans [03-adr-architecture-decision-records.md](../project-lifecycle/03-adr-architecture-decision-records.md), 8 ADRs :

| ADR | Décision | Justification Clé |
|-----|----------|-------------------|
| **001** | Python 3.11+ | Écosystème riche, apprentissage |
| **002** | CLI (pas web) | MVP rapide, focus logique |
| **003** | Typer + Rich | UX moderne, menus interactifs |
| **004** | JSON local | Simplicité, volume faible |
| **005** | .env + GitHub Secrets | Simple, gratuit, suffisant |
| **006** | State Machine | Workflow linéaire clair |
| **007** | Pytest | Standard industrie, fixtures |
| **008** | GitHub Actions | Intégré, gratuit |

### Exemple Complet : ADR-006 State Machine

**Contexte :** Orchestrer 8 étapes séquentielles (Review → Formation → ... → Reflection)

**Options :**
- State Machine (états explicites, transitions claires)
- Event-Driven (flexible mais complexe)

**Décision :** State Machine

**Raison :** Workflow simple et linéaire, pas besoin de la complexité event-driven

**Conséquences :**
- ✅ Code simple et debuggable
- ❌ Si workflow devient complexe (branches), refactoring nécessaire

---

## 📊 Template ADR Simplifié

```markdown
# ADR-XXX: [Titre Court]

**Date:** YYYY-MM-DD  
**Statut:** [Proposé | Accepté | Déprécié]

## Problème
[Quel problème résolvons-nous ?]

## Options
1. **Option A:** [Description] (✅ Pros | ❌ Cons)
2. **Option B:** [Description] (✅ Pros | ❌ Cons)
3. **Option C:** [Description] (✅ Pros | ❌ Cons)

## Décision
**Choix: [Option X]**

[Justification en 2-3 phrases]

## Conséquences
**Positives:**
- [Impact positif 1]
- [Impact positif 2]

**Négatives:**
- [Trade-off 1]
- [Trade-off 2]

**Mitigations:**
- [Comment gérer les impacts négatifs]
```

---

## 🧪 Exercice : Transformer une Discussion en ADR

**Slack Conversation (fictive) :**
```
Dev1: On devrait utiliser MongoDB pour stocker les données
Dev2: Pourquoi pas PostgreSQL ?
Dev1: Parce que MongoDB c'est NoSQL, c'est plus flexible
Dev2: Mais on a des relations entre entities...
Tech Lead: Ok, je décide PostgreSQL
```

**ADR Manquant :**
```markdown
# ADR-042: Choix Base de Données (PostgreSQL)

## Contexte
Besoin de stocker users, sessions, progress (relations claires).
Volume estimé: 10k users, 1M events/mois.

## Options
1. **PostgreSQL** (✅ Relations, ACID | ❌ Scaling horizontal)
2. **MongoDB** (✅ Flexible schema | ❌ Pas de JOIN, consistency)

## Décision
**PostgreSQL** car relations bien définies, ACID critique pour progress.

## Conséquences
✅ Intégrité données garantie
❌ Scaling vertical uniquement (acceptable pour 10k users)
```

**Valeur :** Dans 6 mois, tout le monde comprend POURQUOI PostgreSQL.

---

**Dernière mise à jour :** 9 janvier 2026  
**Statut :** ✅ Concept appliqué dans SkillOps (8 ADRs documentés)
