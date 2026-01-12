# Ansible Automation

#ansible #automation #infrastructure #configuration-management

## Architecture Ansible

```
Control Node (Ansible installed)
    ↓ SSH / WinRM
Managed Nodes (No agent needed!)
    - Server 1
    - Server 2
    - Server N
```

**Concepts clés** :
- **Control Node** : Machine où Ansible est installé
- **Managed Nodes** : Serveurs gérés (inventaire)
- **Inventory** : Liste des serveurs
- **Playbook** : Script YAML décrivant l'état désiré
- **Module** : Unité de code exécutée (apt, yum, copy, service...)
- **Task** : Appel à un module
- **Role** : Regroupement réutilisable (tasks, vars, handlers...)
- **Handler** : Task exécuté sur notification (ex: restart service)

## Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ansible -y

# macOS
brew install ansible

# Python pip
pip install ansible

# Vérifier
ansible --version
```

## Inventory

Fichier définissant les serveurs à gérer.

### Inventory basique (INI)

```ini
# inventory.ini

# Serveur individuel
web1 ansible_host=192.168.1.10 ansible_user=admin

# Groupe de serveurs
[webservers]
web1 ansible_host=192.168.1.10
web2 ansible_host=192.168.1.11
web3 ansible_host=192.168.1.12

[databases]
db1 ansible_host=192.168.1.20 ansible_user=dbadmin
db2 ansible_host=192.168.1.21

# Groupe de groupes
[production:children]
webservers
databases

# Variables de groupe
[webservers:vars]
ansible_user=deploy
ansible_port=2222
http_port=80

[databases:vars]
ansible_user=dbadmin
db_engine=postgresql
```

### Inventory YAML

```yaml
# inventory.yml
all:
  children:
    webservers:
      hosts:
        web1:
          ansible_host: 192.168.1.10
        web2:
          ansible_host: 192.168.1.11
      vars:
        ansible_user: deploy
        http_port: 80

    databases:
      hosts:
        db1:
          ansible_host: 192.168.1.20
          db_type: primary
        db2:
          ansible_host: 192.168.1.21
          db_type: replica
      vars:
        ansible_user: dbadmin
```

### Inventory dynamique

```python
#!/usr/bin/env python3
# inventory.py - Génère inventory depuis API/DB

import json

inventory = {
    "webservers": {
        "hosts": ["web1", "web2"],
        "vars": {"http_port": 80}
    },
    "_meta": {
        "hostvars": {
            "web1": {"ansible_host": "192.168.1.10"},
            "web2": {"ansible_host": "192.168.1.11"}
        }
    }
}

print(json.dumps(inventory))
```

```bash
# Utiliser
ansible-playbook -i inventory.py playbook.yml
```

## Ad-hoc Commands

Commandes rapides sans playbook.

```bash
# Ping tous les serveurs
ansible all -m ping -i inventory.ini

# Commande shell sur un groupe
ansible webservers -m shell -a "uptime" -i inventory.ini

# Installer package
ansible webservers -m apt -a "name=nginx state=present" -b

# Copier fichier
ansible all -m copy -a "src=/local/file dest=/remote/file mode=0644"

# Restart service
ansible webservers -m service -a "name=nginx state=restarted" -b

# Gather facts
ansible all -m setup
ansible all -m setup -a "filter=ansible_distribution*"
```

**Options** :
- `-m` : Module à utiliser
- `-a` : Arguments du module
- `-b` : Devenir sudo (become)
- `-i` : Inventory file
- `--limit` : Limiter à certains hosts
- `--check` : Dry-run
- `-v`, `-vv`, `-vvv` : Verbosité

## Playbooks

Scripts YAML définissant l'état désiré.

### Playbook basique

```yaml
# playbook.yml
---
- name: Configure web servers
  hosts: webservers
  become: yes  # Sudo

  vars:
    http_port: 80
    app_user: webapp

  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
        cache_valid_time: 3600

    - name: Install Nginx
      apt:
        name: nginx
        state: present

    - name: Create app user
      user:
        name: "{{ app_user }}"
        state: present
        shell: /bin/bash

    - name: Copy Nginx config
      template:
        src: templates/nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        owner: root
        group: root
        mode: '0644'
      notify: Restart Nginx

    - name: Ensure Nginx is running
      service:
        name: nginx
        state: started
        enabled: yes

  handlers:
    - name: Restart Nginx
      service:
        name: nginx
        state: restarted
```

### Exécuter playbook

```bash
# Basique
ansible-playbook playbook.yml -i inventory.ini

# Check mode (dry-run)
ansible-playbook playbook.yml --check

# Verbeux
ansible-playbook playbook.yml -vvv

# Limiter à certains hosts
ansible-playbook playbook.yml --limit web1,web2

# Demander sudo password
ansible-playbook playbook.yml --ask-become-pass

# Tags
ansible-playbook playbook.yml --tags "install,config"
```

## Modules essentiels

### Gestion de packages

```yaml
# APT (Debian/Ubuntu)
- name: Install packages
  apt:
    name:
      - nginx
      - postgresql
      - python3-pip
    state: present
    update_cache: yes

# YUM (RedHat/CentOS)
- name: Install package
  yum:
    name: httpd
    state: present

# DNF (Fedora)
- name: Install package
  dnf:
    name: nginx
    state: latest
```

### Fichiers et templates

```yaml
# Copier fichier
- name: Copy file
  copy:
    src: files/config.txt
    dest: /etc/app/config.txt
    owner: root
    group: root
    mode: '0644'
    backup: yes  # Backup si existe

# Template Jinja2
- name: Deploy config from template
  template:
    src: templates/app.conf.j2
    dest: /etc/app/app.conf
  notify: Restart app

# Télécharger fichier
- name: Download file
  get_url:
    url: https://example.com/file.tar.gz
    dest: /tmp/file.tar.gz
    checksum: sha256:abc123...

# Créer dossier
- name: Create directory
  file:
    path: /opt/app
    state: directory
    owner: app
    group: app
    mode: '0755'

# Symlink
- name: Create symlink
  file:
    src: /opt/app/current
    dest: /opt/app/live
    state: link
```

### Services

```yaml
# Systemd
- name: Start and enable service
  service:
    name: nginx
    state: started
    enabled: yes

# Reload systemd
- name: Reload systemd
  systemd:
    daemon_reload: yes

# Restart service
- name: Restart Apache
  service:
    name: apache2
    state: restarted
```

### Commandes shell

```yaml
# Shell command
- name: Run command
  shell: |
    echo "Hello" > /tmp/hello.txt
    cat /tmp/hello.txt
  args:
    creates: /tmp/hello.txt  # Skip si existe

# Command (plus sûr que shell)
- name: Run ls
  command: ls -la /opt
  register: ls_output

- name: Display output
  debug:
    var: ls_output.stdout_lines

# Script
- name: Run script
  script: scripts/setup.sh
  args:
    creates: /opt/app/installed.flag
```

### Utilisateurs et groupes

```yaml
- name: Create group
  group:
    name: webadmin
    state: present
    gid: 5000

- name: Create user
  user:
    name: deploy
    groups: webadmin,sudo
    shell: /bin/bash
    create_home: yes
    password: "{{ 'mypassword' | password_hash('sha512') }}"

- name: Add SSH key
  authorized_key:
    user: deploy
    key: "{{ lookup('file', '~/.ssh/id_rsa.pub') }}"
    state: present
```

### Git

```yaml
- name: Clone repository
  git:
    repo: https://github.com/user/repo.git
    dest: /opt/app
    version: main
    force: yes
  notify: Restart app

- name: Pull latest changes
  git:
    repo: https://github.com/user/repo.git
    dest: /opt/app
    update: yes
```

### Docker

```yaml
- name: Install Docker
  apt:
    name: docker.io
    state: present

- name: Start Docker container
  docker_container:
    name: webapp
    image: nginx:latest
    state: started
    ports:
      - "80:80"
    volumes:
      - /opt/app:/usr/share/nginx/html
    env:
      ENV: production
    restart_policy: always
```

## Variables et Facts

### Définir variables

```yaml
# Dans playbook
vars:
  http_port: 80
  app_name: myapp

# Fichier externe
vars_files:
  - vars/common.yml
  - vars/{{ ansible_distribution }}.yml

# Prompt utilisateur
vars_prompt:
  - name: db_password
    prompt: "Enter DB password"
    private: yes
```

### Facts (variables automatiques)

```yaml
tasks:
  - name: Display hostname
    debug:
      msg: "Hostname is {{ ansible_hostname }}"

  - name: Install package based on OS
    apt:
      name: apache2
      state: present
    when: ansible_os_family == "Debian"

  - name: Show all facts
    debug:
      var: ansible_facts
```

**Facts utiles** :
- `ansible_hostname` : Nom de la machine
- `ansible_distribution` : OS (Ubuntu, CentOS...)
- `ansible_os_family` : Famille OS (Debian, RedHat...)
- `ansible_default_ipv4.address` : IP principale
- `ansible_processor_cores` : Nombre de cores CPU
- `ansible_memtotal_mb` : RAM totale

### Register et debug

```yaml
- name: Get disk usage
  shell: df -h /
  register: disk_info

- name: Show disk usage
  debug:
    var: disk_info.stdout_lines

- name: Fail if disk > 80%
  fail:
    msg: "Disk usage too high!"
  when: disk_info.stdout is search("8[0-9]%|9[0-9]%|100%")
```

## Conditionals et Loops

### When (conditions)

```yaml
- name: Install Apache (Debian)
  apt:
    name: apache2
    state: present
  when: ansible_os_family == "Debian"

- name: Install Apache (RedHat)
  yum:
    name: httpd
    state: present
  when: ansible_os_family == "RedHat"

- name: Skip task on production
  debug:
    msg: "Running debug task"
  when: env != "production"

- name: Multiple conditions (AND)
  debug:
    msg: "Ubuntu 20.04"
  when:
    - ansible_distribution == "Ubuntu"
    - ansible_distribution_version == "20.04"

- name: OR condition
  debug:
    msg: "Debian or Ubuntu"
  when: ansible_os_family == "Debian" or ansible_os_family == "Ubuntu"
```

### Loops

```yaml
# Liste simple
- name: Install packages
  apt:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - postgresql
    - redis-server

# Liste de dictionnaires
- name: Create users
  user:
    name: "{{ item.name }}"
    groups: "{{ item.groups }}"
    state: present
  loop:
    - { name: alice, groups: "sudo,webadmin" }
    - { name: bob, groups: "webadmin" }
    - { name: charlie, groups: "users" }

# Avec register
- name: Check service status
  service:
    name: "{{ item }}"
    state: started
  loop:
    - nginx
    - postgresql
  register: service_status

- name: Show results
  debug:
    msg: "{{ item.name }} is {{ item.state }}"
  loop: "{{ service_status.results }}"
```

## Templates Jinja2

```jinja2
{# templates/nginx.conf.j2 #}
user {{ nginx_user }};
worker_processes {{ ansible_processor_cores }};

events {
    worker_connections 1024;
}

http {
    server {
        listen {{ http_port }};
        server_name {{ server_name }};

        location / {
            proxy_pass http://{{ app_host }}:{{ app_port }};
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}

{# Conditional #}
{% if enable_ssl %}
server {
    listen 443 ssl;
    ssl_certificate {{ ssl_cert_path }};
    ssl_certificate_key {{ ssl_key_path }};
}
{% endif %}

{# Loop #}
{% for upstream in upstreams %}
upstream {{ upstream.name }} {
    server {{ upstream.host }}:{{ upstream.port }};
}
{% endfor %}
```

## Roles

Structure réutilisable pour organiser playbooks.

### Structure d'un role

```
roles/
└── webserver/
    ├── tasks/
    │   └── main.yml          # Tâches principales
    ├── handlers/
    │   └── main.yml          # Handlers
    ├── templates/
    │   └── nginx.conf.j2     # Templates
    ├── files/
    │   └── index.html        # Fichiers statiques
    ├── vars/
    │   └── main.yml          # Variables du role
    ├── defaults/
    │   └── main.yml          # Variables par défaut
    ├── meta/
    │   └── main.yml          # Métadonnées et dépendances
    └── README.md
```

### Exemple de role

**roles/webserver/tasks/main.yml** :
```yaml
---
- name: Install Nginx
  apt:
    name: nginx
    state: present
  notify: Restart Nginx

- name: Deploy config
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  notify: Restart Nginx

- name: Start Nginx
  service:
    name: nginx
    state: started
    enabled: yes
```

**roles/webserver/handlers/main.yml** :
```yaml
---
- name: Restart Nginx
  service:
    name: nginx
    state: restarted
```

**roles/webserver/defaults/main.yml** :
```yaml
---
nginx_user: www-data
http_port: 80
server_name: localhost
```

**Utiliser le role** :
```yaml
---
- name: Setup web servers
  hosts: webservers
  become: yes
  roles:
    - webserver
    - { role: database, db_name: myapp }
```

### Ansible Galaxy (roles publics)

```bash
# Installer role depuis Galaxy
ansible-galaxy install geerlingguy.nginx

# Chercher roles
ansible-galaxy search nginx

# Créer structure de role
ansible-galaxy init my-role

# requirements.yml
---
- name: geerlingguy.nginx
- src: https://github.com/user/role.git
  version: v1.0.0
  name: custom-role

# Installer depuis requirements
ansible-galaxy install -r requirements.yml
```

## Vault (secrets)

Chiffrer données sensibles.

```bash
# Créer fichier vault
ansible-vault create secrets.yml

# Éditer
ansible-vault edit secrets.yml

# Voir contenu
ansible-vault view secrets.yml

# Chiffrer fichier existant
ansible-vault encrypt vars.yml

# Déchiffrer
ansible-vault decrypt vars.yml

# Changer password
ansible-vault rekey secrets.yml
```

**secrets.yml** :
```yaml
---
db_password: supersecret123
api_key: abc123xyz
```

**Utiliser dans playbook** :
```yaml
---
- name: Deploy app
  hosts: all
  vars_files:
    - secrets.yml
  tasks:
    - name: Configure database
      template:
        src: db.conf.j2
        dest: /etc/app/db.conf
```

**Exécuter avec vault** :
```bash
# Prompt password
ansible-playbook playbook.yml --ask-vault-pass

# Fichier password
ansible-playbook playbook.yml --vault-password-file ~/.vault_pass

# Variable d'environnement
export ANSIBLE_VAULT_PASSWORD_FILE=~/.vault_pass
ansible-playbook playbook.yml
```

## Best Practices

- ✅ **Idempotence** : Playbooks réexécutables sans effet de bord
- ✅ **Check mode** : Toujours tester avec --check d'abord
- ✅ **Version control** : Git pour playbooks et inventory
- ✅ **Roles** : Organiser code réutilisable en roles
- ✅ **Variables** : group_vars et host_vars pour organisation
- ✅ **Vault** : Chiffrer tous les secrets
- ✅ **Tags** : Tagger tasks pour exécution partielle
- ✅ **Handlers** : Éviter redémarrages inutiles
- ✅ **Facts caching** : Accélérer playbooks avec cache
- ✅ **Linting** : ansible-lint pour valider syntaxe

```bash
# Installer linter
pip install ansible-lint

# Valider playbook
ansible-lint playbook.yml
```

## Liens

- [[Ansible Roles Development]]
- [[Terraform and Ansible]]
- [[CI/CD with Ansible]]
- [[AWX/Ansible Tower]]

## Notes perso

Date: 2026-01-12
- Automatisation complète de l'infrastructure
- Utilisation de roles pour réutilisabilité
- TODO: Intégrer avec Terraform pour provisioning
- TODO: Setup AWX pour interface web
