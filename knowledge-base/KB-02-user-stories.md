# User Stories & Acceptance Criteria

## 📝 Définition

Une **User Story** est une description courte et simple d'une fonctionnalité, racontée du point de vue de l'utilisateur. Elle capture **qui** veut **quoi** et **pourquoi**, sans décrire le **comment** (laissé aux développeurs).

**Format standard :**
```
En tant que [type d'utilisateur]
Je veux [action/fonctionnalité]
Afin de [bénéfice/valeur]
```

Les **Acceptance Criteria** (critères d'acceptation) définissent **quand** la story est considérée comme terminée. Ce sont des conditions testables qui valident que la fonctionnalité répond au besoin.

---

## 🎯 Concepts Clés

### 1. Format User Story

**Composants :**
- **Who** (Qui) : Le persona/rôle utilisateur
- **What** (Quoi) : L'action ou la fonctionnalité désirée
- **Why** (Pourquoi) : Le bénéfice ou la valeur métier

**Exemple :**
```
En tant qu'apprenant DevOps
Je veux voir mon temps de code quotidien via WakaTime
Afin de valider que j'atteins mon quota de 3h minimum
```

### 2. Critères INVEST

Une bonne user story doit être **INVEST** :

| Lettre | Critère | Signification | Exemple |
|--------|---------|---------------|---------|
| **I** | **Independent** | Indépendante des autres stories | "Afficher métriques" ne dépend pas de "Intégration Telegram" |
| **N** | **Negotiable** | Détails à discuter avec l'équipe | "Affichage temps" : format exact à définir ensemble |
| **V** | **Valuable** | Apporte de la valeur à l'utilisateur | Tracking WakaTime = mesure progression |
| **E** | **Estimable** | L'équipe peut estimer l'effort | "Intégration API" = 5 points (faisable) |
| **S** | **Small** | Livrable en 1 sprint | Pas "Construire LMS complet" mais "Afficher métriques" |
| **T** | **Testable** | On peut vérifier que c'est fait | "Temps affiché" → Critère clair |

### 3. Acceptance Criteria (AC)

**Format :** Liste de conditions sous forme de checklist.

**Exemple :**
```
Acceptance Criteria:
- [ ] Connexion à l'API WakaTime avec token personnel
- [ ] Affichage du temps codé aujourd'hui (format: 2h 45min)
- [ ] Affichage du temps codé hier
- [ ] Alerte si temps < 2h avant 17h
- [ ] Gestion erreur API (rate limit, token invalide)
```

**Caractéristiques d'un bon AC :**
- **Testable** : On peut vérifier facilement (automatiquement ou manuellement)
- **Clair** : Pas d'ambiguïté sur ce qui est attendu
- **Mesurable** : "Affiche le temps" ✅ vs "Affiche joliment" ❌

---

## 💡 Exemple Concret (SkillOps)

### User Story Complète

**US-001: Tracking de Formation**

```markdown
En tant qu'apprenant DevOps
Je veux voir mon temps de code quotidien via WakaTime
Afin de valider que j'atteins mon quota de 3h minimum

**Acceptance Criteria:**
- [ ] Connexion à l'API WakaTime avec token personnel
- [ ] Affichage du temps codé aujourd'hui (format: 2h 45min)
- [ ] Affichage du temps codé hier
- [ ] Alerte si temps < 2h avant 17h
- [ ] Gestion erreur API (rate limit, token invalide)

**Priorité:** P0 (Critical)
**Estimation:** 5 points
**Dépendances:** Aucune
```

### Validation INVEST

- ✅ **Independent** : Peut être développée sans autre story
- ✅ **Negotiable** : Format d'affichage discutable (table vs texte simple)
- ✅ **Valuable** : Mesure la discipline quotidienne
- ✅ **Estimable** : 5 points = ~8h de travail
- ✅ **Small** : Livrable en quelques jours
- ✅ **Testable** : Chaque AC est vérifiable

---

## ✅ Bonnes Pratiques

### Do ✅

**User Stories :**
- **Focus sur la valeur utilisateur** : Toujours expliquer le "pourquoi"
- **Utiliser le langage métier** : Pas de jargon technique dans la story
- **Impliquer l'utilisateur** : Valider que la story répond au besoin réel
- **Décomposer les epics** : "Système de notifications" → 5 stories plus petites
- **Prioriser** : Utiliser MoSCoW (Must/Should/Could/Won't Have)

**Acceptance Criteria :**
- **Être spécifique** : "Temps affiché en format Xh Ymin" plutôt que "Affiche le temps"
- **Couvrir les cas d'erreur** : Pas que le happy path
- **Inclure les NFRs** : Performance, sécurité si pertinent
- **Format checklist** : Facile à valider pendant le dev

### Don't ❌

**User Stories :**
- **Pas de détails d'implémentation** : "Je veux une API REST en Python" ❌ → C'est le comment, pas le quoi
- **Pas trop grandes** : "Je veux un LMS complet" ❌ → Découper en plus petites stories
- **Pas de stories techniques pures** : "Refactorer le code" ❌ → Si vraiment nécessaire, justifier la valeur

**Acceptance Criteria :**
- **Pas vagues** : "Ça doit marcher bien" ❌
- **Pas trop nombreux** : > 10 AC = story trop grosse, découper
- **Pas subjectifs** : "Interface jolie" ❌ → Définir des critères mesurables

---

## 📚 Ressources pour Approfondir

### Livres 📖

1. **"User Stories Applied"** - Mike Cohn  
   → Référence sur les user stories, INVEST, sizing  
   → [Amazon](https://www.amazon.com/User-Stories-Applied-Software-Development/dp/0321205685)

2. **"User Story Mapping"** - Jeff Patton  
   → Organiser les stories en map pour vision d'ensemble  
   → [Amazon](https://www.amazon.com/User-Story-Mapping-Discover-Product/dp/1491904909)

3. **"Specification by Example"** - Gojko Adzic  
   → Acceptance Criteria sous forme d'exemples exécutables  
   → [Amazon](https://www.amazon.com/Specification-Example-Successful-Deliver-Software/dp/1617290084)

### Articles & Templates 📝

- [User Stories - Mike Cohn (Mountain Goat Software)](https://www.mountaingoatsoftware.com/agile/user-stories)
- [INVEST in Good Stories (Bill Wake)](https://xp123.com/articles/invest-in-good-stories-and-smart-tasks/)
- [Acceptance Criteria Template (Atlassian)](https://www.atlassian.com/agile/project-management/user-stories)

### Formats Alternatifs 🎯

**Given/When/Then (Gherkin - BDD)**
```gherkin
Given je suis sur l'étape Formation
When je lance la commande
Then le temps WakaTime s'affiche en format "Xh Ymin"
And une alerte apparaît si < 2h
```

**Job Story (Jobs To Be Done)**
```
When [situation]
I want to [motivation]
So I can [expected outcome]
```

Exemple :
```
When je commence ma session d'apprentissage le matin
I want to voir combien de temps j'ai codé hier
So I can évaluer si j'ai atteint mon objectif quotidien
```

---

## 🔗 Voir Aussi

- [KB-01: Product Discovery](KB-01-product-discovery.md) - D'où viennent les user stories
- [KB-03: MoSCoW Prioritization](KB-03-moscow-prioritization.md) - Comment prioriser les stories
- [KB-04: Sprint Planning](KB-04-sprint-planning.md) - Comment estimer et planifier les stories
- [KB-12: Testing Strategies](KB-12-testing-strategies.md) - Transformer AC en tests automatisés

---

## 🎯 Application dans SkillOps

### Stories du MVP (Must Have)

Dans [02-urd-user-requirements-document.md](../project-lifecycle/02-urd-user-requirements-document.md), 5 stories Must Have :

1. **US-001** : Tracking WakaTime (5 points)
2. **US-002** : Review Métriques (3 points)
3. **US-003** : Exercices Renforcement (3 points)
4. **US-010** : Persistence Données (3 points)
5. **US-011** : Interface CLI (5 points)

**Total :** 19 points = Sprint 1

### Exemple d'AC Testables

**US-002: Review Metrics**
```
AC transformés en tests:
- test_display_yesterday_steps() → Vérifie affichage 7/8
- test_display_time_coded() → Vérifie format "3h42"
- test_calculate_streak() → Vérifie calcul 18 jours
- test_green_color_when_goal_met() → Vérifie couleur conditionnelle
```

---

## 📊 Template User Story

```markdown
## US-XXX: [Titre Court]

**En tant que** [persona]
**Je veux** [action]
**Afin de** [bénéfice]

### Acceptance Criteria
- [ ] Critère 1 (testable)
- [ ] Critère 2 (testable)
- [ ] Critère 3 (testable)

### Priorité
[P0: Critical | P1: High | P2: Medium | P3: Low]

### Estimation
[Story points ou heures]

### Dépendances
[US-XXX, US-YYY ou Aucune]

### Notes Techniques (optionnel)
[Contraintes, risques, suggestions d'implémentation]
```

---

## 🧪 Exercice Pratique

**Mauvaise User Story :**
```
En tant que développeur
Je veux créer une API REST en Python avec FastAPI
Afin d'avoir une architecture moderne
```

**Problèmes :**
- ❌ Persona technique (dev) au lieu d'utilisateur final
- ❌ Détails d'implémentation (FastAPI)
- ❌ Pas de vraie valeur utilisateur

**Bonne Version :**
```
En tant qu'apprenant DevOps
Je veux synchroniser mes données entre mon laptop et desktop
Afin de continuer ma routine d'apprentissage sur n'importe quelle machine

Acceptance Criteria:
- [ ] Modifications sur laptop visibles sur desktop en < 5 minutes
- [ ] Pas de perte de données en cas de conflit
- [ ] Fonctionnement hors ligne (sync au retour de connexion)
```

---

**Dernière mise à jour :** 9 janvier 2026  
**Statut :** ✅ Concept appliqué dans SkillOps (19 stories définies)
