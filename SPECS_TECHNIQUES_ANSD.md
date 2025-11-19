# Spécifications Techniques - Plateforme de Soumission de Projets
## Document destiné à l'ANSD pour provisionnement serveur

---

## 1. RÉSUMÉ EXÉCUTIF

**Application :** Plateforme de Soumission et Évaluation de Projets de Maturation
**Organisation :** Direction Générale de la Planification et des Politiques Économiques (DGPPE)
**Type de déploiement :** Serveur dédié ou VM avec accès complet
**Niveau de criticité :** Production (données sensibles gouvernementales)

---

## 2. SPÉCIFICATIONS SERVEUR

### 2.1 Système d'exploitation

**REQUIS : Ubuntu Server 22.04 LTS (64-bit)**

**Alternatives acceptables :**
- Ubuntu Server 24.04 LTS
- Debian 12 (Bookworm)

**Configuration d'installation :**
- Installation minimale (sans interface graphique)
- OpenSSH Server activé
- Langue : Français ou Anglais
- Timezone : Africa/Dakar

**⚠️ IMPORTANT :** Ne PAS utiliser Windows Server (incompatibilités critiques)

---

### 2.2 Ressources matérielles

#### **Configuration PRODUCTION (recommandée)**

```
┌─────────────────────────────────────────────────────────┐
│ COMPOSANT        │ SPÉCIFICATION                        │
├─────────────────────────────────────────────────────────┤
│ CPU              │ 4 cœurs (vCPUs) minimum              │
│                  │ Processeur x86_64                     │
│                  │ Intel Xeon / AMD EPYC recommandé      │
│                  │ Fréquence : ≥ 2.5 GHz                │
├─────────────────────────────────────────────────────────┤
│ RAM              │ 8 GB DDR4                            │
│                  │ ECC recommandé (non obligatoire)      │
├─────────────────────────────────────────────────────────┤
│ DISQUE SYSTÈME   │ 100 GB SSD                           │
│                  │ NVMe préféré (lecture ≥ 3000 MB/s)   │
│                  │ Partition : / (root) = 100 GB        │
├─────────────────────────────────────────────────────────┤
│ DISQUE DONNÉES   │ 100-200 GB SSD (ou même disque)      │
│ (optionnel)      │ Pour /var/lib/postgresql et backups  │
├─────────────────────────────────────────────────────────┤
│ RÉSEAU           │ 500 Mbps minimum                     │
│                  │ 1 Gbps recommandé                    │
│                  │ IP fixe publique (obligatoire)       │
│                  │ Nom de domaine : À définir           │
└─────────────────────────────────────────────────────────┘
```

#### **Estimation de charge**

- **Utilisateurs simultanés attendus :** 50-200
- **Nombre total d'utilisateurs :** 300-500
- **Projets par an :** 200-500
- **Taille moyenne par projet :** 2-5 MB (formulaire + PDF)
- **Croissance annuelle données :** 5-10 GB/an

---

### 2.3 Partitionnement disque recommandé

```bash
# Si disque unique de 100 GB
/boot          1 GB    (EFI ou legacy)
/              80 GB   (système + application)
/var           15 GB   (logs + base de données)
swap           4 GB    (mémoire swap)

# Si 2 disques (système 100 GB + données 100 GB)
Disque 1:
  /boot        1 GB
  /            95 GB
  swap         4 GB

Disque 2:
  /var/lib/postgresql    50 GB  (base de données)
  /var/backups           50 GB  (sauvegardes)
```

---

## 3. LOGICIELS REQUIS

### 3.1 Dépendances système

**À installer par l'ANSD avant déploiement :**

```bash
# Système de base
apt update && apt upgrade -y
apt install -y build-essential curl wget git unzip

# Python 3.10 ou 3.11
apt install -y python3.10 python3-pip python3-venv python3-dev

# Node.js 20.x LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Base de données PostgreSQL 14+
apt install -y postgresql postgresql-contrib postgresql-client

# Serveur web Nginx
apt install -y nginx

# Certificat SSL
apt install -y certbot python3-certbot-nginx

# Outils système
apt install -y ufw fail2ban logrotate htop net-tools
```

### 3.2 Versions minimales requises

| Logiciel | Version minimale | Commande de vérification |
|----------|------------------|--------------------------|
| Ubuntu | 22.04 LTS | `lsb_release -a` |
| Python | 3.10 | `python3 --version` |
| pip | 22.0 | `pip3 --version` |
| Node.js | 20.0 | `node --version` |
| npm | 10.0 | `npm --version` |
| PostgreSQL | 14.0 | `psql --version` |
| Nginx | 1.18 | `nginx -v` |

---

## 4. CONFIGURATION RÉSEAU

### 4.1 Ports réseau

**Ports à ouvrir sur le firewall :**

| Port | Protocole | Service | Accès | Obligatoire |
|------|-----------|---------|-------|-------------|
| 22 | TCP | SSH | IP admin uniquement | ✅ Oui |
| 80 | TCP | HTTP | Public (redirection HTTPS) | ✅ Oui |
| 443 | TCP | HTTPS | Public | ✅ Oui |
| 5432 | TCP | PostgreSQL | **LOCALHOST UNIQUEMENT** | ⚠️ Ne JAMAIS exposer |

**Configuration UFW (firewall) :**

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow from <IP_ADMIN_ANSD> to any port 22 proto tcp  # SSH restreint
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

### 4.2 Nom de domaine et URL

**URL de la plateforme :** `https://www.dgppe.sn/maturation`

**Configuration requise :**

Le domaine principal `www.dgppe.sn` est géré par la SONATEL. Deux options pour héberger la plateforme :

#### **Option A : Reverse Proxy depuis www.dgppe.sn (RECOMMANDÉ)**

Le serveur principal `www.dgppe.sn` (géré par SONATEL) fait un reverse proxy vers le serveur ANSD :

```nginx
# Sur le serveur SONATEL www.dgppe.sn
location /maturation/ {
    proxy_pass http://<IP_SERVEUR_ANSD>/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Avantages :**
- ✅ URL propre : `www.dgppe.sn/maturation`
- ✅ Certificat SSL géré par SONATEL
- ✅ Serveur ANSD peut rester en HTTP interne
- ✅ Pas de configuration DNS supplémentaire

**Coordination requise avec SONATEL :**
- Ajouter la règle reverse proxy ci-dessus
- Communiquer l'IP publique du serveur ANSD

---

#### **Option B : Sous-domaine dédié (Alternative)**

Créer un sous-domaine `maturation.dgppe.sn` pointant vers le serveur ANSD :

**Configuration DNS (par SONATEL) :**
```
Type: A
Nom: maturation
Zone: dgppe.sn
Valeur: <IP_PUBLIQUE_SERVEUR_ANSD>
TTL: 3600
```

**Certificat SSL :**
- Let's Encrypt (gratuit, renouvellement automatique tous les 90 jours)
- Configuration automatique via Certbot sur serveur ANSD

**Avantages :**
- ✅ Indépendance totale du serveur SONATEL
- ✅ Gestion SSL autonome

**Inconvénients :**
- ❌ URL différente : `maturation.dgppe.sn` au lieu de `www.dgppe.sn/maturation`
- ❌ Nécessite intervention SONATEL pour DNS

---

**🎯 RECOMMANDATION :** Option A (Reverse Proxy) pour conserver l'URL `www.dgppe.sn/maturation`

---

## 5. SÉCURITÉ

### 5.1 Pare-feu (UFW)

✅ **Obligatoire :**
- Activer UFW
- Bloquer tout trafic entrant par défaut
- Autoriser uniquement ports 22 (SSH admin), 80 (HTTP), 443 (HTTPS)
- SSH accessible uniquement depuis IP ANSD (whitelist)

### 5.2 SSH

✅ **Configuration SSH sécurisée :**

```bash
# /etc/ssh/sshd_config
PermitRootLogin no                    # Interdire connexion root directe
PasswordAuthentication no             # Authentification par clé uniquement
PubkeyAuthentication yes              # Autoriser clés SSH
Port 22                               # Port standard (ou personnalisé)
AllowUsers dgppe_admin                # Utilisateur autorisé
```

**Clés SSH :**
- L'ANSD doit créer un utilisateur `dgppe_admin` (non-root)
- La DGPPE fournira sa clé publique SSH pour accès

### 5.3 Fail2ban

✅ **Obligatoire :** Protection contre brute-force SSH/HTTP

```bash
apt install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

Configuration : Bannir IP après 5 tentatives échouées pendant 10 minutes

### 5.4 Mises à jour automatiques

✅ **Recommandé :** Activer mises à jour de sécurité automatiques

```bash
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

### 5.5 Base de données

⚠️ **CRITIQUE :**
- PostgreSQL doit écouter **UNIQUEMENT sur localhost (127.0.0.1)**
- Ne JAMAIS exposer le port 5432 publiquement
- Mot de passe PostgreSQL fort (≥ 20 caractères aléatoires)

---

## 6. ARCHITECTURE APPLICATIVE

### 6.1 Stack technique

**Architecture avec reverse proxy SONATEL (Option A) :**

```
┌──────────────────────────────────────────────────┐
│                   INTERNET                        │
│            https://www.dgppe.sn/maturation       │
└─────────────────────┬────────────────────────────┘
                      │
            ┌─────────▼──────────┐
            │  Serveur SONATEL   │
            │  www.dgppe.sn      │
            │  (Reverse Proxy)   │
            └─────────┬──────────┘
                      │ HTTP/HTTPS
                      │
┌─────────────────────▼────────────────────────────┐
│              Serveur ANSD                         │
│              IP: <IP_PUBLIQUE>                    │
├───────────────────────────────────────────────────┤
│                  [Firewall UFW]                   │
│                       │                           │
│           ┌───────────▼──────────┐                │
│           │   Nginx :80          │                │
│           │   Reverse Proxy      │                │
│           └───────────┬──────────┘                │
│                       │                           │
│         ┌─────────────┴──────────────┐            │
│         ▼                            ▼            │
│ ┌──────────────────┐        ┌──────────────────┐ │
│ │ Backend Flask    │        │ Frontend Vue.js  │ │
│ │ Python 3.10      │        │ (fichiers static)│ │
│ │ Port: 5000       │        │ Servi par Nginx  │ │
│ │ (localhost)      │        └──────────────────┘ │
│ └────────┬─────────┘                             │
│          │                                        │
│          ▼                                        │
│ ┌──────────────────┐                             │
│ │ PostgreSQL 14+   │                             │
│ │ Port: 5432       │                             │
│ │ (localhost)      │                             │
│ └──────────────────┘                             │
└───────────────────────────────────────────────────┘
```

**Architecture standalone (Option B) :**

```
┌──────────────────────────────────────────────────┐
│                   INTERNET                        │
│         https://maturation.dgppe.sn              │
└─────────────────────┬────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────┐
│              Serveur ANSD                         │
│              maturation.dgppe.sn                  │
├───────────────────────────────────────────────────┤
│                  [Firewall UFW]                   │
│                       │                           │
│           ┌───────────▼──────────┐                │
│           │   Nginx :443 (TLS)   │ ← Let's Encrypt│
│           │   Reverse Proxy      │                │
│           └───────────┬──────────┘                │
│                       │                           │
│         ┌─────────────┴──────────────┐            │
│         ▼                            ▼            │
│ ┌──────────────────┐        ┌──────────────────┐ │
│ │ Backend Flask    │        │ Frontend Vue.js  │ │
│ │ Python 3.10      │        │ (fichiers static)│ │
│ │ Port: 5000       │        │ Servi par Nginx  │ │
│ │ (localhost)      │        └──────────────────┘ │
│ └────────┬─────────┘                             │
│          │                                        │
│          ▼                                        │
│ ┌──────────────────┐                             │
│ │ PostgreSQL 14+   │                             │
│ │ Port: 5432       │                             │
│ │ (localhost)      │                             │
│ └──────────────────┘                             │
└───────────────────────────────────────────────────┘
```

### 6.2 Répertoires d'installation

```bash
/opt/maturation/                    # Racine application
├── backend/                        # Backend Flask
│   ├── venv/                       # Environnement virtuel Python
│   ├── app.py                      # Point d'entrée Flask
│   ├── maturation.db               # Base SQLite (dev) ou config PostgreSQL
│   └── requirements.txt            # Dépendances Python
├── frontend/                       # Frontend Vue.js
│   ├── dist/                       # Fichiers compilés (production)
│   └── node_modules/               # Dépendances Node.js
└── logs/                           # Logs applicatifs
    ├── backend.log
    ├── nginx-access.log
    └── nginx-error.log

/var/lib/postgresql/14/main/        # Données PostgreSQL
/var/backups/maturation/            # Sauvegardes automatiques
/etc/nginx/sites-available/         # Configuration Nginx
/etc/systemd/system/                # Services systemd
```

### 6.3 Services systemd

**Backend Flask :**
```ini
# /etc/systemd/system/maturation-backend.service
[Unit]
Description=Maturation Platform Backend
After=network.target postgresql.service

[Service]
Type=simple
User=dgppe_admin
WorkingDirectory=/opt/maturation/backend
Environment="PATH=/opt/maturation/backend/venv/bin"
ExecStart=/opt/maturation/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 7. SAUVEGARDES

### 7.1 Stratégie de sauvegarde

**Fréquence :**
- Base de données : Dump SQL quotidien (3h du matin)
- Fichiers uploadés : Rsync quotidien
- Configuration : Backup hebdomadaire

**Rétention :**
```
Quotidien     : 7 jours
Hebdomadaire  : 4 semaines
Mensuel       : 12 mois
```

**Emplacement :**
```
/var/backups/maturation/daily/
/var/backups/maturation/weekly/
/var/backups/maturation/monthly/
```

### 7.2 Script de sauvegarde (fourni)

Un script bash automatique sera fourni pour :
- Dump PostgreSQL compressé (gzip)
- Sauvegarde fichiers uploadés
- Rotation automatique selon politique de rétention
- Logs de sauvegarde
- Notification par email en cas d'échec

**Commande cron :**
```bash
0 3 * * * /opt/maturation/scripts/backup.sh >> /var/log/maturation-backup.log 2>&1
```

### 7.3 Stockage externe (recommandé)

⚠️ **Recommandation ANSD :**
- Copier les sauvegardes sur un stockage externe (NAS, serveur de fichiers, cloud)
- Fréquence : Quotidienne ou hebdomadaire
- Protocole : rsync, sftp, ou S3-compatible

---

## 8. MONITORING ET LOGS

### 8.1 Logs à surveiller

```bash
# Logs applicatifs
/opt/maturation/logs/backend.log        # Backend Flask
/var/log/nginx/access.log               # Accès HTTP
/var/log/nginx/error.log                # Erreurs HTTP
/var/log/postgresql/postgresql-14-main.log  # PostgreSQL

# Logs système
/var/log/auth.log                       # Authentifications SSH
/var/log/syslog                         # Système général
/var/log/fail2ban.log                   # Tentatives d'intrusion
```

### 8.2 Rotation des logs

Configuration logrotate automatique :
```
Rotation quotidienne
Conservation : 30 jours
Compression : gzip après 1 jour
```

### 8.3 Monitoring (optionnel)

**Recommandé :**
- **htop** : Monitoring CPU/RAM en temps réel
- **netdata** : Dashboard monitoring complet (CPU, RAM, disque, réseau)
- **PostgreSQL logs** : Requêtes lentes (> 1 seconde)

**Alertes à configurer :**
- CPU > 80% pendant 5 minutes
- RAM > 90%
- Disque > 85%
- PostgreSQL connexions > 80% du max
- Certificat SSL expiration < 30 jours

---

## 9. ACCÈS ET COMPTES

### 9.1 Accès SSH

**Utilisateur système :**
```
Nom d'utilisateur : dgppe_admin
Groupe : dgppe_admin, sudo
Shell : /bin/bash
Home : /home/dgppe_admin
Accès : Clé SSH uniquement (fournie par DGPPE)
```

**⚠️ IMPORTANT :**
- Ne PAS utiliser le compte `root` directement
- Utiliser `sudo` pour les opérations admin
- Clé SSH privée conservée par DGPPE uniquement

### 9.2 Accès base de données

**PostgreSQL :**
```
Utilisateur : maturation_user
Mot de passe : <généré aléatoirement 32 caractères>
Base de données : maturation_db
Privilèges : ALL sur maturation_db uniquement
```

**Accès :**
- Local uniquement (localhost)
- Connexion via socket Unix ou 127.0.0.1:5432

---

## 10. BANDE PASSANTE ET PERFORMANCE

### 10.1 Estimation trafic réseau

**Par utilisateur actif :**
- Chargement page : 2-5 MB (première visite)
- Navigation : 100-500 KB/page
- Upload projet (PDF) : 2-5 MB
- Download rapport : 1-3 MB

**Trafic mensuel estimé :**
```
200 utilisateurs actifs/mois × 50 MB = 10 GB/mois
Pics d'activité : 50-100 utilisateurs simultanés
Bande passante requise : 500 Mbps - 1 Gbps
```

### 10.2 Temps de réponse attendus

```
Page d'accueil : < 1 seconde
Liste projets : < 2 secondes
Formulaire soumission : < 1 seconde
Upload fichier PDF : < 10 secondes (pour 5 MB)
Génération rapport : < 5 secondes
```

---

## 11. CONFORMITÉ ET LÉGISLATION

### 11.1 Protection des données

⚠️ **Données sensibles stockées :**
- Informations personnelles des utilisateurs (nom, email, téléphone)
- Projets soumis (descriptions, budgets, localisation)
- Documents PDF (potentiellement confidentiels)
- Historique des évaluations

**Mesures de protection :**
- Chiffrement HTTPS obligatoire (TLS 1.2+)
- Accès base de données restreint (localhost)
- Sauvegardes chiffrées recommandées
- Logs d'accès conservés 90 jours minimum

### 11.2 Disponibilité

**SLA attendu :**
- Disponibilité : 99% (7h de maintenance/mois autorisées)
- Fenêtre de maintenance : Dimanche 2h-6h du matin
- Temps de récupération (RTO) : < 4 heures
- Perte de données maximale (RPO) : < 24 heures

---

## 12. TIMELINE D'INSTALLATION

### Phase 1 : Provisionnement serveur (ANSD)
**Durée : 1-2 jours**
- ✅ Allocation serveur/VM
- ✅ Installation Ubuntu 22.04 LTS
- ✅ Configuration réseau + IP fixe
- ✅ Création utilisateur `dgppe_admin`
- ✅ Installation dépendances (Python, Node.js, PostgreSQL, Nginx)
- ✅ Configuration firewall UFW
- ✅ Activation Fail2ban

### Phase 2 : Configuration DNS et SSL (ANSD + DGPPE)
**Durée : 1 jour**
- ✅ Configuration DNS (A record)
- ✅ Génération certificat SSL Let's Encrypt
- ✅ Configuration Nginx

### Phase 3 : Déploiement application (DGPPE)
**Durée : 1 jour**
- ✅ Clone dépôt Git
- ✅ Installation dépendances backend/frontend
- ✅ Configuration PostgreSQL
- ✅ Migration base de données
- ✅ Compilation frontend Vue.js
- ✅ Configuration services systemd
- ✅ Tests fonctionnels

### Phase 4 : Tests et validation (DGPPE + ANSD)
**Durée : 2-3 jours**
- ✅ Tests de charge
- ✅ Tests de sécurité
- ✅ Validation sauvegardes
- ✅ Documentation administrateur
- ✅ Formation équipe ANSD

**TOTAL : 5-7 jours ouvrés**

---

## 13. LIVRABLES DGPPE → ANSD

Une fois le serveur provisionné, la DGPPE fournira :

1. ✅ **Code source de l'application** (dépôt Git privé ou archive)
2. ✅ **Script d'installation automatique** (1 commande)
3. ✅ **Documentation d'installation** (guide pas-à-pas)
4. ✅ **Script de sauvegarde automatique**
5. ✅ **Configuration Nginx optimisée**
6. ✅ **Services systemd (backend Flask)**
7. ✅ **Documentation administrateur** (maintenance, dépannage)
8. ✅ **Procédures de mise à jour**
9. ✅ **Clé SSH publique DGPPE** (accès serveur)

---

## 14. CONTACTS ET SUPPORT

### DGPPE
**Responsable technique :**
- Nom : [À compléter]
- Email : [À compléter]
- Téléphone : [À compléter]

### ANSD
**Responsable infrastructure :**
- Nom : [À compléter par ANSD]
- Email : [À compléter par ANSD]
- Téléphone : [À compléter par ANSD]

---

## 15. CHECKLIST DE VALIDATION

**À vérifier par l'ANSD avant livraison à la DGPPE :**

```
□ Serveur Ubuntu 22.04 LTS installé
□ Python 3.10+ installé et fonctionnel
□ Node.js 20.x installé et fonctionnel
□ PostgreSQL 14+ installé et démarré
□ Nginx installé et démarré
□ UFW activé avec règles correctes
□ Fail2ban installé et actif
□ IP publique fixe allouée
□ DNS configuré et propagé (maturation.dgppe.gouv.sn)
□ Utilisateur dgppe_admin créé avec accès sudo
□ Clé SSH DGPPE ajoutée
□ Répertoire /opt/maturation créé
□ Répertoire /var/backups/maturation créé
□ Accès SSH fonctionnel depuis DGPPE
□ Port 80/443 accessibles publiquement
□ PostgreSQL accessible localement uniquement
□ Certificat SSL Let's Encrypt configuré (si DNS prêt)
```

---

## ANNEXE A : COMMANDES DE VÉRIFICATION

**À exécuter par l'ANSD pour valider l'installation :**

```bash
# Vérification système
lsb_release -a                    # Ubuntu 22.04 LTS
uname -m                          # x86_64
nproc                             # Nombre de CPU (≥ 4)
free -h                           # RAM (≥ 8 GB)
df -h                             # Disque (≥ 100 GB disponible)

# Vérification logiciels
python3 --version                 # Python 3.10+
pip3 --version                    # pip 22+
node --version                    # Node.js 20.x
npm --version                     # npm 10.x
psql --version                    # PostgreSQL 14+
nginx -v                          # Nginx 1.18+

# Vérification services
systemctl status postgresql       # Active (running)
systemctl status nginx            # Active (running)
systemctl status ufw              # Active
systemctl status fail2ban         # Active (running)

# Vérification réseau
ip addr show                      # IP publique visible
ufw status                        # Status: active
ss -tlnp | grep 80                # Nginx écoute :80
ss -tlnp | grep 443               # Nginx écoute :443
ss -tlnp | grep 5432              # PostgreSQL écoute 127.0.0.1:5432 UNIQUEMENT

# Vérification accès PostgreSQL
sudo -u postgres psql -c "SELECT version();"  # Version PostgreSQL
```

---

## ANNEXE B : ESTIMATION COÛTS (si hébergement payant)

**Si l'ANSD facture l'hébergement à la DGPPE :**

| Composant | Spécification | Coût estimé |
|-----------|---------------|-------------|
| VM/Serveur | 4 vCPU, 8GB, 100GB SSD | 30-50 €/mois |
| Bande passante | 1 TB/mois | Inclus |
| IP publique | Fixe | Inclus |
| Certificat SSL | Let's Encrypt | Gratuit |
| Sauvegardes | 100 GB stockage externe | 5-10 €/mois |
| Support ANSD | Maintenance infrastructure | À définir |
| **TOTAL estimé** | | **35-60 €/mois** |

---

**Date du document :** 2025-01-19
**Version :** 1.0
**Statut :** Prêt pour transmission à l'ANSD

---

## RÉSUMÉ EN 1 PAGE (à transmettre à l'ANSD)

```
╔════════════════════════════════════════════════════════════════╗
║   PLATEFORME DE SOUMISSION DE PROJETS - SPÉCIFICATIONS ANSD   ║
╚════════════════════════════════════════════════════════════════╝

📋 SYSTÈME D'EXPLOITATION
   • Ubuntu Server 22.04 LTS (minimal, sans GUI)
   • Architecture : x86_64
   • Timezone : Africa/Dakar

💻 RESSOURCES MATÉRIELLES
   • CPU : 4 cœurs (vCPUs)
   • RAM : 8 GB
   • Disque : 100 GB SSD (NVMe préféré)
   • Réseau : 500 Mbps - 1 Gbps + IP fixe publique

📦 LOGICIELS À INSTALLER
   • Python 3.10+
   • Node.js 20.x LTS
   • PostgreSQL 14+
   • Nginx 1.18+
   • Certbot (SSL Let's Encrypt)
   • UFW (firewall)
   • Fail2ban

🌐 RÉSEAU
   • Ports ouverts : 22 (SSH admin), 80 (HTTP), 443 (HTTPS)
   • Port 5432 (PostgreSQL) : LOCALHOST UNIQUEMENT
   • URL finale : https://www.dgppe.sn/maturation
   • Configuration : Reverse proxy depuis serveur SONATEL

🔒 SÉCURITÉ
   • Certificat SSL Let's Encrypt (gratuit)
   • Firewall UFW actif
   • SSH par clé uniquement (pas de mot de passe)
   • Fail2ban contre brute-force
   • Utilisateur non-root : dgppe_admin

💾 SAUVEGARDES
   • Base de données : Dump quotidien (3h du matin)
   • Rétention : 7 jours quotidien, 4 semaines hebdo, 12 mois mensuel
   • Emplacement : /var/backups/maturation/

📊 CHARGE ATTENDUE
   • Utilisateurs simultanés : 50-200
   • Projets par an : 200-500
   • Trafic mensuel : 10-20 GB

⏱️ TIMELINE
   • Provisionnement : 1-2 jours (ANSD)
   • Déploiement : 1 jour (DGPPE)
   • Tests : 2-3 jours
   • TOTAL : 5-7 jours ouvrés

✅ LIVRABLES DGPPE
   • Code source + script d'installation automatique
   • Documentation complète
   • Scripts de sauvegarde
   • Support pendant phase de déploiement

📧 CONTACT DGPPE
   [À compléter]
```

---

**Ce document est prêt à être transmis à l'ANSD.**
