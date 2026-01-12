# Kubernetes Basics

#kubernetes #k8s #orchestration #containers

## Vue d'ensemble

**Kubernetes** (K8s) est un système d'orchestration de conteneurs qui automatise le déploiement, la mise à l'échelle et la gestion d'applications conteneurisées.

## Architecture

### Control Plane
- **API Server**: Point d'entrée de tous les appels
- **etcd**: Base de données clé-valeur distribuée
- **Scheduler**: Assigne les Pods aux nodes
- **Controller Manager**: Gère les contrôleurs

### Worker Nodes
- **Kubelet**: Agent qui exécute sur chaque node
- **Kube-proxy**: Gère les règles réseau
- **Container Runtime**: Docker, containerd, CRI-O

## Objets principaux

### Pod
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
```

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
```

### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: LoadBalancer
```

## Commandes kubectl

```bash
# Cluster info
kubectl cluster-info
kubectl get nodes

# Pods
kubectl get pods
kubectl get pods -n kube-system
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl exec -it <pod-name> -- /bin/bash

# Deployments
kubectl get deployments
kubectl create deployment nginx --image=nginx
kubectl scale deployment nginx --replicas=5
kubectl rollout status deployment/nginx
kubectl rollout undo deployment/nginx

# Services
kubectl get services
kubectl expose deployment nginx --port=80 --type=LoadBalancer

# Configuration
kubectl apply -f deployment.yaml
kubectl delete -f deployment.yaml
```

## Concepts avancés

### ConfigMaps et Secrets
- **ConfigMap**: Configuration non-sensible
- **Secret**: Données sensibles (base64 encodé)

### Volumes
- **emptyDir**: Volume éphémère
- **hostPath**: Monte un chemin de l'hôte
- **PersistentVolume**: Stockage persistant

### Namespaces
Isolation logique des ressources

```bash
kubectl create namespace dev
kubectl get pods -n dev
```

## Best practices

- ✅ Utiliser les labels et sélecteurs
- ✅ Définir des limits et requests de ressources
- ✅ Implémenter liveness et readiness probes
- ✅ Utiliser des Secrets pour les données sensibles
- ✅ Versionner les manifests YAML
- ✅ Utiliser Helm pour les déploiements complexes

## Liens

- [[Docker Basics]]
- [[Helm Charts]]
- [[Kubernetes Security]]
- [[Prometheus Monitoring]]

## Notes perso

Date: 2026-01-12
- Cluster minikube installé et testé
- Déployé une app 3-tiers avec LoadBalancer
- TODO: Apprendre Helm et les StatefulSets
