# Linux Command Line Essentials

#linux #bash #cli #terminal

## Navigation et fichiers

```bash
# Navigation
pwd                  # Print working directory
cd /path/to/dir     # Change directory
cd ~                # Home directory
cd -                # Previous directory
cd ..               # Parent directory

# Lister fichiers
ls                  # Liste basique
ls -la              # Détails + fichiers cachés
ls -lh              # Tailles lisibles (human)
ls -lt              # Trié par date
tree                # Arborescence

# Créer/Supprimer
mkdir dir_name      # Créer dossier
mkdir -p a/b/c      # Créer récursivement
touch file.txt      # Créer fichier vide
rm file.txt         # Supprimer fichier
rm -rf dir/         # Supprimer dossier récursivement (ATTENTION!)

# Copier/Déplacer
cp source dest      # Copier fichier
cp -r dir1/ dir2/   # Copier dossier
mv old new          # Renommer/Déplacer
```

## Permissions

```bash
# Format: rwxrwxrwx (user/group/others)
# r=4, w=2, x=1

chmod 755 script.sh    # rwxr-xr-x
chmod +x script.sh     # Ajouter exécution
chmod -R 644 dir/      # Récursif

chown user:group file  # Changer propriétaire
chown -R user dir/     # Récursif

# Voir permissions
ls -l file.txt
stat file.txt
```

## Recherche

```bash
# Find
find /path -name "*.txt"           # Par nom
find . -type f -mtime -7           # Modifié < 7 jours
find . -size +100M                 # Taille > 100MB
find . -name "*.log" -delete       # Supprimer

# Grep
grep "pattern" file.txt            # Chercher dans fichier
grep -r "pattern" dir/             # Récursif
grep -i "pattern" file             # Case insensitive
grep -v "pattern" file             # Inverser (NOT)
grep -n "pattern" file             # Avec numéros de ligne
grep -c "pattern" file             # Compter occurrences
grep -E "regex" file               # Regex étendu

# Which/Whereis
which python                       # Chemin de la commande
whereis python                     # Tous les emplacements
```

## Manipulation de texte

```bash
# Cat/Head/Tail
cat file.txt                       # Afficher tout
head -n 10 file.txt               # 10 premières lignes
tail -n 10 file.txt               # 10 dernières lignes
tail -f /var/log/app.log          # Suivre en temps réel

# Wc (word count)
wc file.txt                        # Lignes, mots, caractères
wc -l file.txt                     # Nombre de lignes
wc -w file.txt                     # Nombre de mots

# Sort/Uniq
sort file.txt                      # Trier
sort -r file.txt                   # Ordre inverse
sort -n file.txt                   # Tri numérique
uniq file.txt                      # Supprimer doublons
sort file.txt | uniq -c            # Compter occurrences

# Cut
cut -d',' -f1,3 data.csv          # Colonnes 1 et 3 (CSV)
cut -c1-10 file.txt               # Caractères 1 à 10

# Awk
awk '{print $1}' file.txt         # 1ère colonne
awk -F',' '{print $2}' data.csv   # 2ème colonne CSV
awk '/pattern/ {print $0}' file   # Lignes matchant pattern

# Sed
sed 's/old/new/' file.txt         # Remplacer 1ère occurrence
sed 's/old/new/g' file.txt        # Remplacer toutes
sed -i 's/old/new/g' file.txt     # Modifier le fichier
sed '1,10d' file.txt              # Supprimer lignes 1-10
```

## Processus

```bash
# Voir processus
ps aux                             # Tous les processus
ps aux | grep nginx               # Filtrer
top                                # Monitoring temps réel
htop                               # Version améliorée (à installer)

# Kill
kill PID                           # Terminer processus
kill -9 PID                        # Forcer (SIGKILL)
killall process_name              # Tous les processus du nom
pkill -f pattern                  # Par pattern

# Background/Foreground
command &                          # Lancer en background
Ctrl+Z                            # Suspendre processus
bg                                # Reprendre en background
fg                                # Reprendre en foreground
jobs                              # Lister jobs
```

## Réseau

```bash
# Connexions
ping google.com                    # Test connectivité
traceroute google.com             # Route réseau
curl https://api.com              # Requête HTTP
wget https://file.com/file.zip    # Télécharger fichier

# Ports et connexions
netstat -tuln                     # Ports ouverts
ss -tuln                          # Alternative moderne
lsof -i :8080                     # Processus sur port 8080

# DNS
nslookup google.com               # Résolution DNS
dig google.com                    # DNS détaillé
host google.com                   # Simple lookup
```

## Système

```bash
# Info système
uname -a                          # Info kernel
hostname                          # Nom machine
uptime                            # Uptime
df -h                             # Espace disque
du -sh dir/                       # Taille dossier
free -h                           # Mémoire RAM

# Utilisateurs
whoami                            # Utilisateur actuel
who                               # Qui est connecté
id                                # UID/GID
sudo command                      # Exécuter en root
su - user                         # Changer d'utilisateur
```

## Redirections et Pipes

```bash
# Redirections
command > file.txt                # Rediriger stdout (écrase)
command >> file.txt               # Append
command 2> error.log              # Rediriger stderr
command &> all.log                # stdout + stderr
command < input.txt               # Input depuis fichier

# Pipes
command1 | command2               # Sortie 1 → Entrée 2
ls -la | grep ".txt"
cat file.txt | wc -l
ps aux | grep nginx | awk '{print $2}'
```

## Archives

```bash
# Tar
tar -czf archive.tar.gz dir/      # Créer (compress)
tar -xzf archive.tar.gz           # Extraire
tar -tzf archive.tar.gz           # Lister contenu

# Zip/Unzip
zip -r archive.zip dir/           # Créer
unzip archive.zip                 # Extraire
unzip -l archive.zip              # Lister
```

## Variables d'environnement

```bash
# Voir variables
env                               # Toutes les variables
echo $PATH                        # Variable spécifique
printenv PATH

# Définir
export VAR="value"                # Session actuelle
export PATH=$PATH:/new/path       # Ajouter au PATH

# Fichiers de config
~/.bashrc                         # Bash config
~/.bash_profile                   # Login shell
source ~/.bashrc                  # Recharger config
```

## Scripting Bash

```bash
#!/bin/bash

# Variables
NAME="World"
echo "Hello $NAME"

# Conditions
if [ -f "file.txt" ]; then
    echo "File exists"
fi

# Boucles
for i in {1..5}; do
    echo "Iteration $i"
done

while read line; do
    echo "$line"
done < file.txt

# Fonctions
function greet() {
    echo "Hello $1"
}
greet "Alice"
```

## Best Practices

- ✅ Utiliser tab pour l'autocomplétion
- ✅ Utiliser Ctrl+R pour chercher dans l'historique
- ✅ Créer des alias pour commandes fréquentes
- ✅ Toujours tester avec -n avant rm -rf
- ✅ Utiliser && et || pour chaîner commandes
- ✅ Documenter les scripts avec des commentaires

## Alias utiles

```bash
# Dans ~/.bashrc
alias ll='ls -la'
alias grep='grep --color=auto'
alias ..='cd ..'
alias ...='cd ../..'
alias gs='git status'
alias gp='git pull'
alias dc='docker-compose'
```

## Liens

- [[Bash Scripting]]
- [[Linux System Administration]]
- [[SSH and Remote Access]]
- [[Vim Editor]]

## Notes perso

Date: 2026-01-12
- Maîtrise des pipes et redirections
- Création de scripts d'automatisation
- TODO: Approfondir sed et awk
