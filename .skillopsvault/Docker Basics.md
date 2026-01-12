# Docker Basics

#docker #containers #devops

## Concepts clés

**Docker** est une plateforme de containerisation qui permet d'empaqueter des applications avec toutes leurs dépendances.

### Conteneurs vs VMs

- **Conteneur**: Partage le kernel de l'OS hôte, léger et rapide
- **VM**: Système d'exploitation complet, plus lourd mais isolation totale

## Commandes essentielles

```bash
# Lancer un conteneur
docker run -d -p 8080:80 nginx

# Lister les conteneurs
docker ps
docker ps -a  # Inclure les conteneurs arrêtés

# Arrêter un conteneur
docker stop <container_id>

# Supprimer un conteneur
docker rm <container_id>

# Images
docker images
docker pull ubuntu:20.04
docker rmi <image_id>
```

## Dockerfile

Structure de base:

```dockerfile
FROM ubuntu:20.04
RUN apt-get update && apt-get install -y nginx
COPY ./app /var/www/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Best practices

- ✅ Utiliser des images officielles
- ✅ Minimiser les layers (combiner RUN)
- ✅ Utiliser .dockerignore
- ✅ Ne pas stocker de secrets dans l'image
- ✅ Scanner les vulnérabilités

## Liens

- [[Docker Compose]]
- [[Docker Networks]]
- [[Kubernetes Basics]]

## Notes perso

Date: 2026-01-12
- Exercice complété: création d'un Dockerfile multi-stage
- Prochaine étape: Docker Compose pour orchestrer plusieurs services
