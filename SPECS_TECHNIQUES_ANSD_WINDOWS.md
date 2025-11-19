# Spécifications Techniques - Windows Server
## Plateforme de Soumission de Projets de Maturation - Configuration Windows

---

## 1. RÉSUMÉ EXÉCUTIF

**Application :** Plateforme de Soumission et Évaluation de Projets de Maturation
**Organisation :** Direction Générale de la Planification et des Politiques Économiques (DGPPE)
**Type de déploiement :** Windows Server avec IIS
**Niveau de criticité :** Production (données sensibles gouvernementales)

---

## 2. SPÉCIFICATIONS SERVEUR

### 2.1 Système d'exploitation

**REQUIS : Windows Server 2019 ou Windows Server 2022**

**Configuration recommandée :**
- Windows Server 2022 Standard (64-bit)
- Interface Desktop Experience (GUI recommandée pour administration)
- Langue : Français
- Timezone : (UTC+00:00) Africa/Dakar

**Rôles Windows Server requis :**
- Web Server (IIS)
- Remote Desktop Services (pour administration à distance)
- Windows Defender Antivirus

---

### 2.2 Ressources matérielles

#### **Configuration PRODUCTION (recommandée)**

```
┌─────────────────────────────────────────────────────────┐
│ COMPOSANT        │ SPÉCIFICATION                        │
├─────────────────────────────────────────────────────────┤
│ CPU              │ 4 cœurs (vCPUs) minimum              │
│                  │ 6-8 cœurs recommandé                 │
│                  │ Processeur x86_64                     │
│                  │ Intel Xeon / AMD EPYC                │
│                  │ Fréquence : ≥ 2.5 GHz                │
├─────────────────────────────────────────────────────────┤
│ RAM              │ 12 GB minimum (Windows + apps)       │
│                  │ 16 GB recommandé                     │
│                  │ DDR4 ECC recommandé                  │
├─────────────────────────────────────────────────────────┤
│ DISQUE C:\       │ 150 GB SSD (système Windows)         │
│                  │ NTFS, défragmentation automatique    │
├─────────────────────────────────────────────────────────┤
│ DISQUE D:\       │ 100-200 GB SSD (données + backups)   │
│ (optionnel)      │ Pour PostgreSQL et sauvegardes       │
├─────────────────────────────────────────────────────────┤
│ RÉSEAU           │ 500 Mbps minimum                     │
│                  │ 1 Gbps recommandé                    │
│                  │ IP fixe publique (obligatoire)       │
│                  │ Nom de domaine : À définir           │
└─────────────────────────────────────────────────────────┘
```

**Note :** Windows Server nécessite plus de RAM que Linux (3-4 GB supplémentaires pour l'OS).

---

### 2.3 Partitionnement disque recommandé

**Si disque unique de 200 GB :**
```
C:\ (Système)          150 GB  (Windows + applications)
D:\ (Données)          50 GB   (PostgreSQL + backups)
```

**Si 2 disques physiques :**
```
Disque 1 (SSD) :
  C:\                  150 GB  (Windows Server + IIS + Python)

Disque 2 (SSD) :
  D:\PostgreSQL        80 GB   (Base de données)
  D:\Backups           120 GB  (Sauvegardes automatiques)
```

---

## 3. LOGICIELS REQUIS

### 3.1 Composants Windows

**IIS (Internet Information Services) 10.0+**
```
Rôles et fonctionnalités à installer :
☑ Web Server (IIS)
  ☑ Web Server
    ☑ Common HTTP Features
      ☑ Default Document
      ☑ Directory Browsing
      ☑ HTTP Errors
      ☑ Static Content
    ☑ Health and Diagnostics
      ☑ HTTP Logging
      ☑ Request Monitor
    ☑ Performance
      ☑ Static Content Compression
      ☑ Dynamic Content Compression
    ☑ Security
      ☑ Request Filtering
      ☑ URL Authorization
  ☑ Management Tools
    ☑ IIS Management Console
```

**Installation PowerShell :**
```powershell
Install-WindowsFeature -name Web-Server -IncludeManagementTools
Install-WindowsFeature -name Web-Static-Content
Install-WindowsFeature -name Web-Default-Doc
Install-WindowsFeature -name Web-Http-Errors
Install-WindowsFeature -name Web-Http-Logging
Install-WindowsFeature -name Web-Request-Monitor
Install-WindowsFeature -name Web-Filtering
Install-WindowsFeature -name Web-Stat-Compression
Install-WindowsFeature -name Web-Dyn-Compression
```

---

### 3.2 Python 3.10+

**Installation :**

1. Télécharger Python 3.10.11 (64-bit) depuis https://www.python.org/downloads/windows/
2. Installer avec les options suivantes :
   - ☑ Install for all users
   - ☑ Add Python to PATH
   - ☑ Install pip
   - Destination : `C:\Python310`

3. Vérifier l'installation :
```powershell
python --version
# Python 3.10.11

pip --version
# pip 23.x.x
```

4. Installer les dépendances système Python :
```powershell
pip install --upgrade pip
pip install virtualenv
```

---

### 3.3 PostgreSQL 14+

**Installation :**

1. Télécharger PostgreSQL 14.x ou 15.x (Windows x86-64) depuis :
   https://www.postgresql.org/download/windows/

2. Installer avec :
   - Installation Directory : `C:\Program Files\PostgreSQL\14`
   - Data Directory : `D:\PostgreSQL\data` (si disque D:\ disponible) ou `C:\PostgreSQL\data`
   - Port : **5432** (par défaut)
   - Locale : **French, France**
   - **Mot de passe superuser `postgres` :** Noter le mot de passe (≥ 20 caractères)

3. Ajouter PostgreSQL au PATH système :
```powershell
$env:Path += ";C:\Program Files\PostgreSQL\14\bin"
[Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::Machine)
```

4. Vérifier l'installation :
```powershell
psql --version
# psql (PostgreSQL) 14.x
```

5. Créer la base de données :
```powershell
psql -U postgres
```
```sql
CREATE DATABASE maturation_db;
CREATE USER maturation_user WITH PASSWORD 'VotreMotDePasseTresSecurise123!@#';
GRANT ALL PRIVILEGES ON DATABASE maturation_db TO maturation_user;
\q
```

---

### 3.4 Node.js 18+ et npm

**Installation :**

1. Télécharger Node.js 18 LTS (64-bit) depuis https://nodejs.org/
2. Installer avec les options par défaut
   - Destination : `C:\Program Files\nodejs`
   - ☑ Automatically install necessary tools

3. Vérifier :
```powershell
node --version
# v18.x.x

npm --version
# 9.x.x
```

---

### 3.5 Git for Windows

**Installation :**

1. Télécharger depuis https://git-scm.com/download/win
2. Installer avec :
   - ☑ Git Bash
   - ☑ Git GUI
   - Default editor : Notepad++ ou Vim

3. Vérifier :
```powershell
git --version
# git version 2.x.x
```

---

### 3.6 URL Rewrite Module pour IIS

**Obligatoire pour router les requêtes correctement**

1. Télécharger depuis :
   https://www.iis.net/downloads/microsoft/url-rewrite

2. Installer `rewrite_amd64_en-US.msi`

3. Vérifier dans IIS Manager : URL Rewrite devrait apparaître dans les modules

---

### 3.7 Application Request Routing (ARR) pour IIS

**Pour le reverse proxy vers le backend Flask**

1. Télécharger depuis :
   https://www.iis.net/downloads/microsoft/application-request-routing

2. Installer `ARRv3_setup_amd64_en-us.exe`

3. Activer le proxy dans IIS :
```powershell
# Dans IIS Manager :
# Server → Application Request Routing Cache → Server Proxy Settings
# ☑ Enable proxy
# HTTP timeout : 60 seconds
```

---

## 4. CONFIGURATION RÉSEAU ET SÉCURITÉ

### 4.1 Pare-feu Windows (Windows Defender Firewall)

**Règles à créer :**

```powershell
# Autoriser HTTP (port 80)
New-NetFirewallRule -DisplayName "HTTP Inbound" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow

# Autoriser HTTPS (port 443)
New-NetFirewallRule -DisplayName "HTTPS Inbound" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# Autoriser Remote Desktop (si nécessaire)
New-NetFirewallRule -DisplayName "RDP" -Direction Inbound -Protocol TCP -LocalPort 3389 -Action Allow

# BLOQUER PostgreSQL de l'extérieur (sécurité)
New-NetFirewallRule -DisplayName "Block PostgreSQL External" -Direction Inbound -Protocol TCP -LocalPort 5432 -Action Block -RemoteAddress Internet
```

**⚠️ IMPORTANT :** PostgreSQL doit être accessible uniquement en local (localhost), PAS depuis Internet.

---

### 4.2 Nom de domaine et SSL

**URL de la plateforme :** `https://www.dgppe.sn/maturation`

#### **Option A : Reverse Proxy depuis www.dgppe.sn (RECOMMANDÉ)**

Le serveur principal `www.dgppe.sn` (géré par SONATEL) fait un reverse proxy vers le serveur Windows ANSD :

**Configuration Nginx sur serveur SONATEL :**
```nginx
# Sur le serveur SONATEL www.dgppe.sn
location /maturation/ {
    proxy_pass http://<IP_SERVEUR_WINDOWS_ANSD>/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Avantages :**
- ✅ URL propre : `www.dgppe.sn/maturation`
- ✅ Certificat SSL géré par SONATEL
- ✅ Serveur Windows peut rester en HTTP interne
- ✅ Pas de configuration SSL Windows compliquée

**Coordination requise avec SONATEL :**
- Communiquer l'IP publique du serveur Windows
- Demander l'ajout de la règle reverse proxy ci-dessus

---

#### **Option B : Certificat SSL sur Windows Server (Alternative)**

Si vous voulez gérer SSL directement sur Windows :

**Étapes :**
1. Obtenir un certificat SSL :
   - **Let's Encrypt** via **win-acme** (gratuit) : https://www.win-acme.com/
   - Ou certificat commercial (DigiCert, GlobalSign, etc.)

2. Installer le certificat dans IIS :
   - Ouvrir IIS Manager
   - Server Certificates → Import Certificate
   - Bind le certificat au site sur port 443

3. Configurer HTTPS Binding :
   - Site → Bindings → Add
   - Type: https
   - Port: 443
   - SSL Certificate: Sélectionner le certificat installé

---

## 5. ARCHITECTURE APPLICATIVE

### 5.1 Stack technique

```
┌──────────────────────────────────────────────────────┐
│                   INTERNET                            │
│            https://www.dgppe.sn/maturation           │
└─────────────────────┬────────────────────────────────┘
                      │
            ┌─────────▼──────────┐
            │  Serveur SONATEL   │
            │  www.dgppe.sn      │
            │  (Reverse Proxy)   │
            └─────────┬──────────┘
                      │ HTTP/HTTPS
                      │
┌─────────────────────▼────────────────────────────────┐
│              Serveur Windows ANSD                     │
│              Windows Server 2022                      │
│              IP: <IP_PUBLIQUE>                        │
├───────────────────────────────────────────────────────┤
│            [Windows Defender Firewall]                │
│                       │                               │
│           ┌───────────▼──────────┐                    │
│           │   IIS 10.0 :80/443   │                    │
│           │   Reverse Proxy      │                    │
│           │   + Static Files     │                    │
│           └───────────┬──────────┘                    │
│                       │                               │
│         ┌─────────────┴──────────────┐                │
│         ▼                            ▼                │
│ ┌──────────────────┐        ┌──────────────────┐     │
│ │ Backend Flask    │        │ Frontend Vue.js  │     │
│ │ Python 3.10      │        │ (dist/ static)   │     │
│ │ Port: 5000       │        │ Servi par IIS    │     │
│ │ (localhost)      │        │ C:\inetpub\www\  │     │
│ └────────┬─────────┘        └──────────────────┘     │
│          │                                            │
│          ▼                                            │
│ ┌──────────────────┐                                 │
│ │ PostgreSQL 14    │                                 │
│ │ Port: 5432       │                                 │
│ │ (localhost)      │                                 │
│ │ D:\PostgreSQL\   │                                 │
│ └──────────────────┘                                 │
└───────────────────────────────────────────────────────┘
```

---

### 5.2 Répertoires d'installation

```
C:\
├── inetpub\
│   └── wwwroot\
│       └── maturation\             # Racine application
│           ├── frontend\           # Frontend Vue.js compilé (dist/)
│           │   ├── index.html
│           │   ├── assets\
│           │   └── ...
│           └── backend\            # Backend Flask
│               ├── venv\           # Environnement virtuel Python
│               ├── app.py
│               ├── models.py
│               ├── routes\
│               └── ...

D:\
├── PostgreSQL\
│   ├── data\                       # Données PostgreSQL
│   └── backups\                    # Sauvegardes automatiques
└── Logs\
    ├── backend\                    # Logs Flask
    └── iis\                        # Logs IIS
```

---

## 6. INSTALLATION DE L'APPLICATION

### 6.1 Cloner le dépôt

```powershell
cd C:\inetpub\wwwroot
git clone https://github.com/absakho-source/maturation.git
cd maturation
```

---

### 6.2 Configuration Backend Flask

```powershell
cd C:\inetpub\wwwroot\maturation\backend

# Créer environnement virtuel
python -m venv venv

# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt
```

**Créer le fichier `.env` :**
```powershell
notepad .env
```

**Contenu de `.env` :**
```env
# Base de données PostgreSQL
DATABASE_TYPE=postgresql
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=maturation_db
DATABASE_USER=maturation_user
DATABASE_PASSWORD=VotreMotDePasseTresSecurise123!@#

# Configuration Flask
FLASK_ENV=production
SECRET_KEY=generer_une_cle_secrete_aleatoire_de_32_caracteres_minimum
UPLOAD_FOLDER=C:\inetpub\wwwroot\maturation\backend\uploads
MAX_CONTENT_LENGTH=52428800

# CORS (pour le frontend)
CORS_ORIGINS=https://www.dgppe.sn
```

**Initialiser la base de données :**
```powershell
python
```
```python
from app import db, app
with app.app_context():
    db.create_all()
    print("✓ Base de données initialisée")
exit()
```

---

### 6.3 Configuration Frontend Vue.js

```powershell
cd C:\inetpub\wwwroot\maturation\frontend

# Installer les dépendances
npm install

# Configurer l'URL de l'API backend
notepad .env.production
```

**Contenu de `.env.production` :**
```env
VITE_API_BASE_URL=/api
```

**Compiler le frontend :**
```powershell
npm run build
```

Les fichiers compilés se trouveront dans `frontend\dist\`.

---

### 6.4 Configuration IIS

#### **Étape 1 : Créer le site IIS**

```powershell
# Créer un nouveau site IIS
Import-Module WebAdministration

# Arrêter le site par défaut
Stop-Website -Name "Default Web Site"

# Créer le site maturation
New-Website -Name "Maturation" `
  -PhysicalPath "C:\inetpub\wwwroot\maturation\frontend\dist" `
  -Port 80 `
  -Force

# Démarrer le site
Start-Website -Name "Maturation"
```

---

#### **Étape 2 : Configurer le reverse proxy vers Flask**

Créer `C:\inetpub\wwwroot\maturation\frontend\dist\web.config` :

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <!-- Reverse proxy pour /api vers Flask backend -->
    <rewrite>
      <rules>
        <!-- Proxy API requests vers Flask :5000 -->
        <rule name="Proxy API to Flask" stopProcessing="true">
          <match url="^api/(.*)" />
          <action type="Rewrite" url="http://localhost:5000/api/{R:1}" />
        </rule>

        <!-- Vue.js SPA routing -->
        <rule name="Vue.js SPA" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
            <add input="{REQUEST_URI}" pattern="^/api/" negate="true" />
          </conditions>
          <action type="Rewrite" url="/" />
        </rule>
      </rules>
    </rewrite>

    <!-- Compression -->
    <urlCompression doStaticCompression="true" doDynamicCompression="true" />

    <!-- Cache statique (CSS, JS, images) -->
    <staticContent>
      <clientCache cacheControlMode="UseMaxAge" cacheControlMaxAge="7.00:00:00" />
    </staticContent>

    <!-- Sécurité -->
    <httpProtocol>
      <customHeaders>
        <add name="X-Content-Type-Options" value="nosniff" />
        <add name="X-Frame-Options" value="SAMEORIGIN" />
        <add name="X-XSS-Protection" value="1; mode=block" />
      </customHeaders>
    </httpProtocol>
  </system.webServer>
</configuration>
```

---

#### **Étape 3 : Démarrer Flask en tant que service Windows**

**Option A : Utiliser NSSM (Non-Sucking Service Manager) - RECOMMANDÉ**

1. Télécharger NSSM : https://nssm.cc/download
2. Extraire dans `C:\nssm\`

```powershell
# Installer Flask comme service
C:\nssm\nssm.exe install FlaskBackend "C:\inetpub\wwwroot\maturation\backend\venv\Scripts\python.exe" "C:\inetpub\wwwroot\maturation\backend\app.py"

# Configurer le service
C:\nssm\nssm.exe set FlaskBackend AppDirectory "C:\inetpub\wwwroot\maturation\backend"
C:\nssm\nssm.exe set FlaskBackend AppStdout "D:\Logs\backend\output.log"
C:\nssm\nssm.exe set FlaskBackend AppStderr "D:\Logs\backend\error.log"

# Démarrer le service
Start-Service FlaskBackend

# Vérifier
Get-Service FlaskBackend
```

**Option B : Utiliser Task Scheduler (alternative)**

Créer une tâche planifiée qui démarre au démarrage Windows.

---

## 7. SAUVEGARDES

### 7.1 Sauvegarde PostgreSQL automatique

**Créer le script de backup** `D:\Backups\backup_postgres.ps1` :

```powershell
# backup_postgres.ps1
$date = Get-Date -Format "yyyy-MM-dd_HHmmss"
$backupFile = "D:\PostgreSQL\backups\maturation_db_$date.sql"

# Variables
$env:PGPASSWORD = "VotreMotDePasseTresSecurise123!@#"
$pgDumpPath = "C:\Program Files\PostgreSQL\14\bin\pg_dump.exe"

# Créer le backup
& $pgDumpPath -U maturation_user -h localhost -d maturation_db -F c -f $backupFile

# Supprimer les backups de plus de 30 jours
Get-ChildItem "D:\PostgreSQL\backups\*.sql" | Where-Object { $_.CreationTime -lt (Get-Date).AddDays(-30) } | Remove-Item

Write-Host "✓ Backup créé : $backupFile"
```

**Planifier l'exécution quotidienne :**

```powershell
# Créer une tâche planifiée
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File D:\Backups\backup_postgres.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName "PostgreSQL Daily Backup" -Action $action -Trigger $trigger -Principal $principal
```

---

### 7.2 Sauvegarde des fichiers uploadés

Sauvegarder régulièrement :
- `C:\inetpub\wwwroot\maturation\backend\uploads\`

Vers :
- `D:\Backups\uploads\`

---

## 8. MONITORING ET LOGS

### 8.1 Logs IIS

**Emplacement :** `C:\inetpub\logs\LogFiles\`

**Analyser les logs :**
```powershell
Get-Content "C:\inetpub\logs\LogFiles\W3SVC1\u_ex$(Get-Date -Format 'yyMMdd').log" -Tail 50
```

---

### 8.2 Logs Flask

**Emplacement :** `D:\Logs\backend\`

**Analyser :**
```powershell
Get-Content "D:\Logs\backend\error.log" -Tail 50
```

---

### 8.3 Monitoring Performance

**Outils Windows :**
- **Performance Monitor (perfmon)** : Surveiller CPU, RAM, disque, réseau
- **Event Viewer** : Logs système et applicatifs
- **Task Manager** : Utilisation en temps réel

---

## 9. MAINTENANCE

### 9.1 Mises à jour

**Windows Server :**
```powershell
# Vérifier les mises à jour
Install-Module PSWindowsUpdate
Get-WindowsUpdate

# Installer les mises à jour critiques
Install-WindowsUpdate -MicrosoftUpdate -AcceptAll -AutoReboot
```

**Python/Flask :**
```powershell
cd C:\inetpub\wwwroot\maturation\backend
.\venv\Scripts\Activate.ps1
pip list --outdated
pip install --upgrade <package>
```

---

### 9.2 Redémarrage services

**Redémarrer IIS :**
```powershell
iisreset
```

**Redémarrer Flask backend :**
```powershell
Restart-Service FlaskBackend
```

**Redémarrer PostgreSQL :**
```powershell
Restart-Service postgresql-x64-14
```

---

## 10. CHECKLIST DE DÉPLOIEMENT

```
SYSTÈME
□ Windows Server 2022 installé et à jour
□ Pare-feu Windows configuré (ports 80, 443 ouverts)
□ IP fixe configurée
□ Nom de domaine/reverse proxy configuré avec SONATEL

LOGICIELS
□ IIS 10 installé avec URL Rewrite et ARR
□ Python 3.10 installé + pip + virtualenv
□ PostgreSQL 14 installé et sécurisé
□ Node.js 18 LTS installé
□ Git for Windows installé
□ NSSM installé (pour service Flask)

APPLICATION
□ Dépôt GitHub cloné dans C:\inetpub\wwwroot\maturation
□ Backend : venv créé + dépendances installées
□ Backend : .env configuré avec bonnes credentials
□ Backend : Base de données initialisée
□ Frontend : npm install + npm run build réussi
□ IIS : Site "Maturation" créé et démarré
□ IIS : web.config configuré avec reverse proxy
□ Flask : Service Windows créé avec NSSM et démarré

SÉCURITÉ
□ Mot de passe PostgreSQL fort (20+ caractères)
□ SECRET_KEY Flask généré et unique
□ PostgreSQL accessible uniquement en localhost
□ Pare-feu bloque accès externe à PostgreSQL
□ Certificat SSL installé (si option B)

BACKUPS
□ Script backup PostgreSQL créé
□ Tâche planifiée backup configurée (2:00 AM quotidien)
□ Test de restauration backup effectué

TESTS
□ Accès frontend : https://www.dgppe.sn/maturation fonctionne
□ Login utilisateur fonctionne
□ Soumission projet fonctionne
□ Upload PDF fonctionne
□ API backend répond : https://www.dgppe.sn/maturation/api/health
□ Logs IIS et Flask fonctionnent
□ Service Flask redémarre automatiquement après reboot

DOCUMENTATION
□ Credentials documentés en lieu sûr
□ Contact SONATEL pour reverse proxy
□ Procédures de maintenance documentées
```

---

## 11. CONTACTS ET SUPPORT

### DGPPE
**Responsable technique :**
- Email : [À compléter]
- Téléphone : [À compléter]

### ANSD
**Administrateur serveur Windows :**
- Email : [À compléter]
- Téléphone : [À compléter]

### SONATEL
**Administrateur www.dgppe.sn :**
- Email : [À compléter]
- Téléphone : [À compléter]

---

**Date :** 2025-01-19
**Version :** 1.0 - Configuration Windows Server
**Statut :** Prêt pour déploiement
