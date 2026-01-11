# Product Discovery

## 📝 Définition

Le **Product Discovery** est la phase initiale du cycle de développement produit où l'on cherche à **comprendre le problème à résoudre avant de construire la solution**. C'est un processus itératif de validation des hypothèses avec les utilisateurs pour s'assurer qu'on construit le bon produit, pas juste qu'on construit le produit correctement.

**En une phrase :** Répondre à "Est-ce que ce problème vaut la peine d'être résolu ?" avant de coder.

---

## 🎯 Concepts Clés

### 1. Les 4 Risques Produit (Marty Cagan)

| Risque | Question | Validation |
|--------|----------|-----------|
| **Value Risk** | Les utilisateurs vont-ils acheter/utiliser ? | Interviews, prototypes |
| **Usability Risk** | Les utilisateurs vont-ils comprendre comment l'utiliser ? | Tests d'utilisabilité |
| **Feasibility Risk** | Pouvons-nous le construire ? | Tech spikes, POC |
| **Business Viability Risk** | Est-ce viable pour le business ? | Modèle économique |

### 2. Rôles dans la Discovery

- **Product Manager (PM)** : Anime la session, pose les questions, challenge les hypothèses
- **Product Owner (PO)** : Représente les besoins business/utilisateurs, priorise
- **Tech Lead** : Consultatif sur la faisabilité technique
- **Designers UX** : Validation de l'utilisabilité
- **Développeurs** : Pas présents (pour éviter de démarrer le dev trop tôt)

### 3. Outputs de la Discovery

- **Problem Statement** : Définition claire du problème
- **User Personas** : Qui sont les utilisateurs ?
- **Pain Points** : Quels sont leurs frustrations ?
- **Success Metrics** : Comment mesurer le succès ?
- **Priorisation MoSCoW** : Quelles features sont critiques ?

---

## 💡 Exemple Concret (SkillOps)

### Problem Statement
> "En tant qu'apprenant DevOps autodidacte, je m'éparpille entre trop de ressources sans système pour mesurer ma progression, ce qui réduit mon efficacité d'apprentissage."

### Discovery Questions Posées

**Q: Quel est ton problème principal ?**
R: Éparpillement (Kubernetes, Docker, Terraform...) sans fil conducteur

**Q: À qui s'adresse l'outil ?**
R: Personnel pour l'instant, mais architecture évolutive

**Q: Qu'est-ce qui définit le succès dans 3 mois ?**
R: Routine quotidienne sans friction (lancer → faire → review → terminé)

**Q: Quelles features sont critiques pour le MVP ?**
R: Formation (tracking temps), Reinforce (exercices), Review (métriques)

**Résultat :** MVP clair avec 5 user stories Must Have au lieu de partir dans 15 directions.

---

## ✅ Bonnes Pratiques

### Do ✅

- **Poser des questions ouvertes** : "Raconte-moi ta dernière session d'apprentissage" plutôt que "Tu aimes Docker ?"
- **Valider les hypothèses** : "Je pense que les utilisateurs veulent X" → Tester avec de vrais utilisateurs
- **Documenter tout** : Les réponses, les insights, les décisions prises
- **Itérer rapidement** : Discovery → Prototype → Test → Pivot ou Persévère
- **Impliquer le Tech Lead tôt** : Éviter de découvrir que c'est infaisable après 2 mois de design

### Don't ❌

- **Ne pas sauter directement au code** : "J'ai une idée cool" ≠ "Il y a un problème à résoudre"
- **Ne pas écouter que les early adopters** : Ils ne représentent pas tous les utilisateurs
- **Ne pas confondre features et problème** : "Je veux un bouton rouge" ≠ "J'ai du mal à identifier les actions critiques"
- **Ne pas faire de Discovery seul dans sa tête** : Parler à de vrais utilisateurs, même 5
- **Ne pas rendre la Discovery trop longue** : 1-2 semaines max, sinon paralysie d'analyse

---

## 📚 Ressources pour Approfondir

### Livres 📖

1. **"Inspired: How to Create Tech Products Customers Love"** - Marty Cagan
   → Bible du Product Management, chapitres 10-15 sur Discovery
   → [Amazon](https://www.amazon.com/INSPIRED-Create-Tech-Products-Customers/dp/1119387507)

2. **"The Mom Test"** - Rob Fitzpatrick
   → Comment poser les bonnes questions aux utilisateurs
   → Éviter les biais de validation
   → [Amazon](https://www.amazon.com/Mom-Test-customers-business-everyone/dp/1492180742)

3. **"Continuous Discovery Habits"** - Teresa Torres
   → Discovery hebdomadaire intégrée au processus
   → [Amazon](https://www.amazon.com/Continuous-Discovery-Habits-Discover-Products/dp/1736633309)

### Articles & Blogs 📝

- [Product Discovery de Silicon Valley Product Group](https://www.svpg.com/product-discovery/)
- [Discovery vs Delivery (Jeff Patton)](https://www.jpattonassociates.com/dual-track-development/)
- [How to Run a Product Discovery Sprint (Google Ventures)](https://www.gv.com/sprint/)

### Frameworks & Outils 🛠️

- **Design Sprint (Google)** : 5 jours pour valider une idée
- **Lean Startup** : Build → Measure → Learn
- **Jobs To Be Done (JTBD)** : Comprendre le "job" que l'utilisateur veut accomplir
- **Opportunity Solution Tree** : Mapper problèmes → opportunités → solutions

### Cours 🎓

- [Product Management Specialization - Coursera (University of Virginia)](https://www.coursera.org/specializations/product-management)
- [Reforge - Product Strategy](https://www.reforge.com/product-strategy)

---

## 🔗 Voir Aussi

- [KB-02: User Stories](KB-02-user-stories.md) - Comment transformer les insights de Discovery en stories
- [KB-03: MoSCoW Prioritization](KB-03-moscow-prioritization.md) - Prioriser les features découvertes
- [KB-21: DevOps Culture](KB-21-devops-culture.md) - Parallèle avec la culture d'expérimentation

---

## 🎯 Application dans SkillOps

Dans le projet SkillOps, la Product Discovery est documentée dans :
- [01-product-discovery-session.md](../project-lifecycle/01-product-discovery-session.md)

**Ce qui a été validé :**
- ✅ Le problème existe (éparpillement confirmé)
- ✅ La solution est faisable (CLI Python, APIs disponibles)
- ✅ Les features prioritaires sont claires (MoSCoW défini)
- ✅ Les métriques de succès sont mesurables (taux complétion, temps gagné)

**Impact :**
- Évité de construire un dashboard web complexe (pas le besoin principal)
- Focus sur friction minimale (menus interactifs vs commandes à mémoriser)
- Architecture évolutive sans over-engineering initial

---

## 📊 Checklist Discovery

Avant de passer au développement, valider :

- [ ] Le problème est clairement défini (Problem Statement)
- [ ] Les utilisateurs cibles sont identifiés (Personas)
- [ ] Les pain points sont documentés
- [ ] Les métriques de succès sont définies (KPIs)
- [ ] La faisabilité technique est validée (Tech Lead consulté)
- [ ] Les features sont priorisées (MoSCoW)
- [ ] Les hypothèses risquées sont testées (prototypes, interviews)
- [ ] Le PO et le PM sont alignés sur la vision

---

**Dernière mise à jour :** 9 janvier 2026
**Statut :** ✅ Concept appliqué dans SkillOps
