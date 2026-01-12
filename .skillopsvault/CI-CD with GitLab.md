# CI/CD with GitLab

#cicd #gitlab #devops #automation

## GitLab CI/CD Architecture

```
Code Push → GitLab Repository → .gitlab-ci.yml → GitLab Runner → Pipeline Execution
```

**Composants** :
- **Pipeline** : Ensemble de stages et jobs
- **Stage** : Phase du pipeline (build, test, deploy)
- **Job** : Tâche spécifique dans un stage
- **Runner** : Agent qui exécute les jobs
- **Artifact** : Fichier produit par un job (binaire, rapport)

## .gitlab-ci.yml Structure

Fichier de configuration à la racine du projet.

### Pipeline de base

```yaml
# Définir les stages
stages:
  - build
  - test
  - deploy

# Variables globales
variables:
  DOCKER_IMAGE: myapp:$CI_COMMIT_SHORT_SHA
  APP_ENV: production

# Job de build
build-job:
  stage: build
  image: node:18
  script:
    - npm install
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 hour
  only:
    - main
    - develop

# Job de test
test-unit:
  stage: test
  image: node:18
  script:
    - npm install
    - npm run test:unit
  coverage: '/Coverage: \d+\.\d+%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

test-integration:
  stage: test
  image: node:18
  services:
    - postgres:14
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: test_user
    POSTGRES_PASSWORD: test_pass
  script:
    - npm install
    - npm run test:integration
  dependencies:
    - build-job

# Job de déploiement
deploy-prod:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache openssh
    - ssh user@server "cd /app && ./deploy.sh"
  environment:
    name: production
    url: https://myapp.com
  only:
    - main
  when: manual  # Déploiement manuel
```

### Pipeline Docker

```yaml
stages:
  - build
  - test
  - push
  - deploy

variables:
  DOCKER_REGISTRY: registry.gitlab.com
  DOCKER_IMAGE: $DOCKER_REGISTRY/$CI_PROJECT_PATH
  DOCKER_TAG: $CI_COMMIT_SHORT_SHA

before_script:
  - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $DOCKER_REGISTRY

build-docker:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker build -t $DOCKER_IMAGE:$DOCKER_TAG .
    - docker tag $DOCKER_IMAGE:$DOCKER_TAG $DOCKER_IMAGE:latest
    - docker push $DOCKER_IMAGE:$DOCKER_TAG
    - docker push $DOCKER_IMAGE:latest
  only:
    - main

test-docker:
  stage: test
  image: $DOCKER_IMAGE:$DOCKER_TAG
  script:
    - python -m pytest tests/

security-scan:
  stage: test
  image: aquasec/trivy:latest
  script:
    - trivy image --severity HIGH,CRITICAL $DOCKER_IMAGE:$DOCKER_TAG
  allow_failure: true

deploy-k8s:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config set-cluster k8s --server=$K8S_SERVER
    - kubectl config set-credentials gitlab --token=$K8S_TOKEN
    - kubectl set image deployment/myapp myapp=$DOCKER_IMAGE:$DOCKER_TAG
    - kubectl rollout status deployment/myapp
  environment:
    name: production
    kubernetes:
      namespace: production
  only:
    - main
```

## Variables CI/CD

### Variables prédéfinies

```yaml
script:
  - echo "Pipeline ID: $CI_PIPELINE_ID"
  - echo "Commit SHA: $CI_COMMIT_SHA"
  - echo "Commit Short SHA: $CI_COMMIT_SHORT_SHA"
  - echo "Branch: $CI_COMMIT_REF_NAME"
  - echo "Project: $CI_PROJECT_NAME"
  - echo "Job Stage: $CI_JOB_STAGE"
  - echo "Runner: $CI_RUNNER_DESCRIPTION"
```

**Variables utiles** :
- `$CI_COMMIT_SHA` : Hash complet du commit
- `$CI_COMMIT_SHORT_SHA` : Hash court (8 chars)
- `$CI_COMMIT_REF_NAME` : Nom de la branche/tag
- `$CI_COMMIT_MESSAGE` : Message du commit
- `$CI_PROJECT_NAME` : Nom du projet
- `$CI_PROJECT_PATH` : Chemin complet (group/project)
- `$CI_REGISTRY` : URL du registry GitLab
- `$CI_REGISTRY_USER` : Username registry
- `$CI_REGISTRY_PASSWORD` : Token registry

### Variables personnalisées

Dans GitLab UI : **Settings → CI/CD → Variables**

```yaml
# Utilisation
deploy:
  script:
    - echo "API Key: $API_KEY"
    - echo "DB Password: $DB_PASSWORD"
```

**Types de variables** :
- **Variable** : Texte simple
- **File** : Contenu écrit dans un fichier temporaire
- **Protected** : Uniquement sur branches protégées
- **Masked** : Masquée dans les logs

## Runners

### Types de runners

1. **Shared Runners** : Partagés entre tous les projets
2. **Group Runners** : Partagés dans un groupe
3. **Specific Runners** : Dédiés à un projet

### Installation d'un runner (Linux)

```bash
# Télécharger
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash
sudo apt-get install gitlab-runner

# Enregistrer
sudo gitlab-runner register
# URL: https://gitlab.com/
# Token: (depuis Settings → CI/CD → Runners)
# Executor: docker, shell, kubernetes, etc.

# Vérifier
sudo gitlab-runner list
sudo gitlab-runner status

# Démarrer/Arrêter
sudo gitlab-runner start
sudo gitlab-runner stop
```

### Configuration runner (config.toml)

```toml
concurrent = 4  # Jobs parallèles

[[runners]]
  name = "my-runner"
  url = "https://gitlab.com/"
  token = "YOUR_TOKEN"
  executor = "docker"

  [runners.docker]
    image = "alpine:latest"
    privileged = true  # Pour Docker-in-Docker
    volumes = ["/cache", "/var/run/docker.sock:/var/run/docker.sock"]

  [runners.cache]
    Type = "s3"
    Path = "gitlab-runner-cache"
    Shared = true
```

## Cache et Artifacts

### Cache

Accélère les builds en sauvegardant dépendances entre pipelines.

```yaml
variables:
  npm_config_cache: "$CI_PROJECT_DIR/.npm"

cache:
  key: $CI_COMMIT_REF_SLUG  # Par branche
  paths:
    - .npm/
    - node_modules/

build:
  script:
    - npm ci --cache .npm --prefer-offline
    - npm run build
```

**Cache policy** :
- `pull` : Télécharger uniquement
- `push` : Upload uniquement
- `pull-push` : Les deux (défaut)

### Artifacts

Fichiers produits par un job, passés aux jobs suivants.

```yaml
build:
  script:
    - make build
  artifacts:
    paths:
      - build/
      - dist/
    exclude:
      - build/tmp/
    expire_in: 1 week
    reports:
      junit: test-results.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

test:
  dependencies:
    - build  # Télécharge artifacts de build
  script:
    - ./dist/run-tests
```

## Conditions et rules

### Rules (moderne)

```yaml
deploy-prod:
  script: echo "Deploying to production"
  rules:
    # Seulement sur main
    - if: $CI_COMMIT_BRANCH == "main"
    # Seulement si tag
    - if: $CI_COMMIT_TAG
    # Seulement si fichier modifié
    - changes:
        - src/**/*
        - Dockerfile
    # Seulement si variable définie
    - if: $DEPLOY_ENABLED == "true"
    # Job manuel si develop
    - if: $CI_COMMIT_BRANCH == "develop"
      when: manual
```

### Only/Except (legacy)

```yaml
deploy:
  script: echo "Deploy"
  only:
    - main
    - tags
  except:
    - develop

deploy-feature:
  script: echo "Deploy feature"
  only:
    refs:
      - /^feature-.*$/  # Branches feature-*
    changes:
      - src/**/*
```

## Parallel et Matrix

### Jobs parallèles

```yaml
test:
  stage: test
  parallel: 5  # 5 instances
  script:
    - bundle exec rspec --tag ~slow
```

### Matrix builds

```yaml
test:
  stage: test
  parallel:
    matrix:
      - RUBY_VERSION: ['2.7', '3.0', '3.1']
        DB: ['mysql', 'postgres']
  image: ruby:${RUBY_VERSION}
  services:
    - name: ${DB}:latest
  script:
    - bundle exec rspec
```

## Environments et Deployments

```yaml
deploy-staging:
  stage: deploy
  script:
    - ./deploy.sh staging
  environment:
    name: staging
    url: https://staging.example.com
    on_stop: stop-staging
    auto_stop_in: 1 week
  only:
    - develop

stop-staging:
  stage: deploy
  script:
    - ./cleanup.sh staging
  environment:
    name: staging
    action: stop
  when: manual

deploy-prod:
  stage: deploy
  script:
    - ./deploy.sh production
  environment:
    name: production
    url: https://example.com
    deployment_tier: production
  only:
    - main
  when: manual
```

## Triggers et Pipelines multi-projets

### Trigger child pipeline

```yaml
# .gitlab-ci.yml
trigger-child:
  trigger:
    include: .gitlab-ci-child.yml
    strategy: depend  # Attend que le child finisse
```

### Trigger autre projet

```yaml
trigger-deploy:
  stage: deploy
  trigger:
    project: group/deploy-project
    branch: main
    strategy: depend
  only:
    - main
```

### Pipeline schedules

Dans GitLab UI : **CI/CD → Schedules**

Cron pour exécuter pipelines périodiquement.

```yaml
# Job exécuté uniquement par schedule
nightly-build:
  script: make build
  only:
    - schedules
```

## Templates et extends

### DRY avec extends

```yaml
.deploy-template:
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | ssh-add -
  script:
    - ssh user@$SERVER "cd /app && ./deploy.sh"

deploy-staging:
  extends: .deploy-template
  variables:
    SERVER: staging.example.com
  environment:
    name: staging

deploy-prod:
  extends: .deploy-template
  variables:
    SERVER: example.com
  environment:
    name: production
  when: manual
```

### Include external files

```yaml
include:
  - local: '.gitlab-ci-build.yml'
  - remote: 'https://example.com/ci-template.yml'
  - template: 'Security/SAST.gitlab-ci.yml'
  - project: 'group/templates'
    file: '/templates/.gitlab-ci.yml'
```

## Security Scanning

### SAST (Static Application Security Testing)

```yaml
include:
  - template: Security/SAST.gitlab-ci.yml

variables:
  SAST_EXCLUDED_PATHS: "spec, test, tests, tmp"
```

### Container Scanning

```yaml
include:
  - template: Security/Container-Scanning.gitlab-ci.yml

container_scanning:
  variables:
    CS_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

### Dependency Scanning

```yaml
include:
  - template: Security/Dependency-Scanning.gitlab-ci.yml
```

## Best Practices

- ✅ **Idempotence** : Jobs réexécutables sans effet de bord
- ✅ **Fail fast** : Tester rapidement, déployer après
- ✅ **Cache intelligemment** : node_modules, .m2, pip cache
- ✅ **Artifacts minimum** : Expiration courte, taille limitée
- ✅ **Secrets sécurisés** : Variables protected + masked
- ✅ **Docker layers** : Optimiser Dockerfile pour cache
- ✅ **Parallel jobs** : Accélérer tests longs
- ✅ **Manual gates** : Prod deployment manual
- ✅ **Monitoring** : Intégrer avec Prometheus/Grafana

## Exemple complet : Application Node.js

```yaml
image: node:18

stages:
  - install
  - lint
  - test
  - build
  - deploy

variables:
  npm_config_cache: "$CI_PROJECT_DIR/.npm"

cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .npm/
    - node_modules/

install:
  stage: install
  script:
    - npm ci --cache .npm --prefer-offline
  artifacts:
    paths:
      - node_modules/
    expire_in: 1 day

lint:
  stage: lint
  script:
    - npm run lint
  dependencies:
    - install

test:unit:
  stage: test
  script:
    - npm run test:unit
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'
  artifacts:
    reports:
      junit: junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
  dependencies:
    - install

test:e2e:
  stage: test
  services:
    - postgres:14
  variables:
    POSTGRES_DB: test_db
    DATABASE_URL: postgresql://postgres:postgres@postgres:5432/test_db
  script:
    - npm run test:e2e
  dependencies:
    - install

build:
  stage: build
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
  dependencies:
    - install
  only:
    - main
    - develop

deploy:staging:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache rsync openssh
    - rsync -avz --delete dist/ user@staging:/var/www/app/
  environment:
    name: staging
    url: https://staging.myapp.com
  dependencies:
    - build
  only:
    - develop

deploy:production:
  stage: deploy
  image: alpine:latest
  script:
    - apk add --no-cache rsync openssh
    - rsync -avz --delete dist/ user@prod:/var/www/app/
  environment:
    name: production
    url: https://myapp.com
  dependencies:
    - build
  only:
    - main
  when: manual
```

## Liens

- [[GitLab Runner Configuration]]
- [[Docker CI/CD]]
- [[Kubernetes Deployments]]
- [[Security Scanning]]

## Notes perso

Date: 2026-01-12
- Pipeline multi-stages avec cache optimisé
- Utilisation de matrix pour tests multi-versions
- TODO: Intégrer ArgoCD pour GitOps
- TODO: Ajouter performance testing avec k6
