# DevOps Best Practices

## CI/CD

### ✅ Do
- **Pipeline rapide** : < 10 minutes
- **Tests automatisés** : Unit + Integration + E2E
- **Fail fast** : Arrêter pipeline si étape critique échoue
- **Artifacts** : Sauvegarder logs, coverage reports
- **Notifications** : Slack/Email si build cassé

### ❌ Don't
- Pipeline de 2h (personne n'attendra)
- Tests flaky (qui passent aléatoirement)
- Ignorer warnings
- Merger si CI rouge

## Infrastructure as Code

### ✅ Do
- **Déclaratif** : Terraform, Ansible (état désiré)
- **Versionné** : IaC dans Git
- **Modules réutilisables** : DRY principle
- **State management** : Terraform state en remote (S3)
- **Documentation** : README par module

### ❌ Don't
- Configuration manuelle (clicks in UI)
- IaC sans versionning
- Secrets en clair dans code

## Secrets Management

### ✅ Do
- **Vault dédié** : HashiCorp Vault, AWS Secrets Manager
- **.env local** : Jamais commité
- **Rotation** : Changer secrets régulièrement
- **Least privilege** : Permissions minimales

### ❌ Don't
- Secrets en dur dans code
- .env dans Git
- Même mot de passe partout
- Secrets dans logs

## Monitoring & Observability

### ✅ Do
- **3 Pillars** : Logs, Metrics, Traces
- **Logs structurés** : JSON avec contexte
- **Alerting** : SLO-based (business impact)
- **Dashboards** : Métriques clés visibles
- **Runbooks** : Documentation pour incidents

### ❌ Don't
- Logs non structurés ("error happened")
- Alertes bruyantes (fatigue)
- Pas de monitoring = blind deployment

## Containers (Docker)

### ✅ Do
- **Multi-stage builds** : Image finale légère
- **Non-root user** : Sécurité
- **.dockerignore** : Comme .gitignore
- **Tags explicites** : `app:v1.2.3` pas `latest`
- **Health checks** : HEALTHCHECK dans Dockerfile

### ❌ Don't
- Images > 1GB (Alpine base recommended)
- Root user dans container
- `latest` tag en production
- Secrets dans ENV vars du Dockerfile

## Deployment Strategies

### ✅ Do
- **Blue/Green** : 2 environnements, switch instantané
- **Canary** : Déploiement progressif (1% → 10% → 100%)
- **Rollback automatique** : Si health check fail
- **Zero-downtime** : Users ne doivent rien voir

### ❌ Don't
- Déployer le vendredi soir 😅
- Pas de stratégie de rollback
- Downtime de 1h pour un deploy

## Documentation

### ✅ Do
- **README.md** : Installation, usage, architecture
- **ADRs** : Décisions architecture documentées
- **Runbooks** : Procédures incidents
- **Architecture diagrams** : C4 model

### ❌ Don't
- Documentation outdated (pire que pas de doc)
- Tout dans la tête de 1 personne
- Jargon sans explications

## Testing in Production

### ✅ Do
- **Feature flags** : Tester en prod avec 1% users
- **A/B testing** : Valider hypothèses
- **Chaos engineering** : Tester résilience (Netflix Simian Army)
- **Synthetic monitoring** : Tests automatiques en prod

### ❌ Don't
- Tester uniquement en dev/staging
- Assumer prod = staging (spoiler: jamais le cas)

---

**Métriques DORA à Suivre :**
- **Deployment Frequency** : Combien de fois/jour
- **Lead Time** : Commit → Production
- **MTTR** : Mean Time To Restore (< 1h objectif)
- **Change Failure Rate** : % deploys qui échouent (< 15%)

**Ressources :**
- [The Phoenix Project](https://www.amazon.com/Phoenix-Project-DevOps-Helping-Business/dp/0988262592)
- [The DevOps Handbook](https://www.amazon.com/DevOps-Handbook-World-Class-Reliability-Organizations/dp/1942788002)
- [12 Factor App](https://12factor.net/)
- [DORA Metrics](https://dora.dev/)
