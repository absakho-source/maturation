# Guide Rapide - Installation Windows Server
## Plateforme de Maturation DGPPE

---

## ⚡ Installation Rapide (30-45 minutes)

### 1️⃣ PRÉREQUIS

**Serveur :**
- Windows Server 2019/2022
- 4 CPU, 12 GB RAM, 150 GB disque
- IP fixe publique
- Accès administrateur

---

### 2️⃣ INSTALLER LES LOGICIELS (15 min)

**Exécuter en PowerShell (Admin) :**

```powershell
# IIS + modules
Install-WindowsFeature -name Web-Server -IncludeManagementTools
Install-WindowsFeature Web-Static-Content, Web-Default-Doc, Web-Http-Errors, Web-Http-Logging

# Télécharger et installer :
# 1. Python 3.10 : https://www.python.org/downloads/windows/ (64-bit, Add to PATH)
# 2. PostgreSQL 14 : https://www.postgresql.org/download/windows/ (Port 5432)
# 3. Node.js 18 LTS : https://nodejs.org/ (64-bit)
# 4. Git for Windows : https://git-scm.com/download/win
# 5. URL Rewrite : https://www.iis.net/downloads/microsoft/url-rewrite
# 6. ARR : https://www.iis.net/downloads/microsoft/application-request-routing
# 7. NSSM : https://nssm.cc/download → Extraire dans C:\nssm\
```

---

### 3️⃣ CONFIGURER POSTGRESQL (5 min)

```powershell
# Ouvrir psql
psql -U postgres

# Créer base et utilisateur
CREATE DATABASE maturation_db;
CREATE USER maturation_user WITH PASSWORD 'VotreMotDePasse123!@#';
GRANT ALL PRIVILEGES ON DATABASE maturation_db TO maturation_user;
\q
```

---

### 4️⃣ CLONER ET CONFIGURER L'APPLICATION (10 min)

```powershell
# Cloner le dépôt
cd C:\inetpub\wwwroot
git clone https://github.com/absakho-source/maturation.git
cd maturation

# Backend
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Créer .env
notepad .env
```

**Contenu .env :**
```env
DATABASE_TYPE=postgresql
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=maturation_db
DATABASE_USER=maturation_user
DATABASE_PASSWORD=VotreMotDePasse123!@#
FLASK_ENV=production
SECRET_KEY=generer_cle_aleatoire_32_caracteres_minimum
UPLOAD_FOLDER=C:\inetpub\wwwroot\maturation\backend\uploads
CORS_ORIGINS=https://www.dgppe.sn
```

**Initialiser la BD :**
```powershell
python
```
```python
from app import db, app
with app.app_context():
    db.create_all()
exit()
```

**Frontend :**
```powershell
cd ..\frontend
npm install

# Créer .env.production
notepad .env.production
```
**Contenu :**
```env
VITE_API_BASE_URL=/api
```

```powershell
# Compiler
npm run build
```

---

### 5️⃣ CONFIGURER IIS (10 min)

**Créer le site :**
```powershell
Import-Module WebAdministration
Stop-Website -Name "Default Web Site"

New-Website -Name "Maturation" `
  -PhysicalPath "C:\inetpub\wwwroot\maturation\frontend\dist" `
  -Port 80 -Force

Start-Website -Name "Maturation"
```

**Créer web.config dans `C:\inetpub\wwwroot\maturation\frontend\dist\web.config` :**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="Proxy API" stopProcessing="true">
          <match url="^api/(.*)" />
          <action type="Rewrite" url="http://localhost:5000/api/{R:1}" />
        </rule>
        <rule name="Vue SPA" stopProcessing="true">
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
    <staticContent>
      <clientCache cacheControlMode="UseMaxAge" cacheControlMaxAge="7.00:00:00" />
    </staticContent>
  </system.webServer>
</configuration>
```

---

### 6️⃣ DÉMARRER FLASK COMME SERVICE (5 min)

```powershell
# Installer Flask comme service Windows
C:\nssm\nssm.exe install FlaskBackend `
  "C:\inetpub\wwwroot\maturation\backend\venv\Scripts\python.exe" `
  "C:\inetpub\wwwroot\maturation\backend\app.py"

C:\nssm\nssm.exe set FlaskBackend AppDirectory "C:\inetpub\wwwroot\maturation\backend"

# Démarrer
Start-Service FlaskBackend

# Vérifier
Get-Service FlaskBackend
# Status doit être "Running"
```

---

### 7️⃣ CONFIGURER LE PARE-FEU (2 min)

```powershell
# Autoriser HTTP/HTTPS
New-NetFirewallRule -DisplayName "HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# BLOQUER PostgreSQL externe
New-NetFirewallRule -DisplayName "Block PostgreSQL" -Direction Inbound -Protocol TCP -LocalPort 5432 -Action Block -RemoteAddress Internet
```

---

### 8️⃣ TESTER L'APPLICATION (3 min)

**Depuis le serveur :**
```powershell
# Tester backend Flask
curl http://localhost:5000/api/health

# Tester frontend
curl http://localhost/
```

**Depuis un navigateur externe :**
- Ouvrir : `http://<IP_SERVEUR>`
- La page de login devrait s'afficher

---

### 9️⃣ CONFIGURER REVERSE PROXY SONATEL

**Contacter SONATEL pour ajouter cette configuration sur leur serveur `www.dgppe.sn` :**

```nginx
# À ajouter dans la config Nginx de www.dgppe.sn
location /maturation/ {
    proxy_pass http://<IP_SERVEUR_WINDOWS_ANSD>/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Informations à transmettre à SONATEL :**
- IP publique du serveur Windows ANSD : `<IP_À_FOURNIR>`
- URL cible : `https://www.dgppe.sn/maturation`

Une fois configuré, l'application sera accessible via : **`https://www.dgppe.sn/maturation`**

---

### 🔟 CONFIGURER LES SAUVEGARDES (5 min)

**Créer `D:\Backups\backup_postgres.ps1` :**

```powershell
$date = Get-Date -Format "yyyy-MM-dd_HHmmss"
$backupFile = "D:\PostgreSQL\backups\maturation_db_$date.sql"
$env:PGPASSWORD = "VotreMotDePasse123!@#"
& "C:\Program Files\PostgreSQL\14\bin\pg_dump.exe" -U maturation_user -h localhost -d maturation_db -F c -f $backupFile
Get-ChildItem "D:\PostgreSQL\backups\*.sql" | Where-Object { $_.CreationTime -lt (Get-Date).AddDays(-30) } | Remove-Item
Write-Host "✓ Backup : $backupFile"
```

**Planifier :**
```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File D:\Backups\backup_postgres.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName "PostgreSQL Backup" -Action $action -Trigger $trigger -Principal $principal
```

---

## ✅ CHECKLIST FINALE

```
□ IIS site "Maturation" démarré (port 80)
□ Service FlaskBackend démarré
□ PostgreSQL démarré
□ Frontend accessible : http://<IP_SERVEUR>/
□ Backend API répond : http://<IP_SERVEUR>/api/health
□ Pare-feu configuré (80, 443 ouverts / 5432 bloqué)
□ Backup PostgreSQL planifié (2:00 AM quotidien)
□ Coordonné avec SONATEL pour reverse proxy
□ Test complet : login, soumission projet, upload PDF
```

---

## 🔧 COMMANDES UTILES

**Redémarrer les services :**
```powershell
iisreset                          # IIS
Restart-Service FlaskBackend      # Flask
Restart-Service postgresql-x64-14 # PostgreSQL
```

**Voir les logs :**
```powershell
# Logs IIS
Get-Content "C:\inetpub\logs\LogFiles\W3SVC1\*.log" -Tail 50

# Logs Flask (si NSSM configuré avec logs)
Get-Content "D:\Logs\backend\error.log" -Tail 50

# Event Viewer système
eventvwr.msc
```

**Mettre à jour l'application :**
```powershell
cd C:\inetpub\wwwroot\maturation
git pull origin main

# Backend
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
deactivate
Restart-Service FlaskBackend

# Frontend
cd ..\frontend
npm install
npm run build
iisreset
```

---

## 🆘 DÉPANNAGE

**Problème : Site IIS ne démarre pas**
```powershell
# Vérifier les logs
Get-EventLog -LogName Application -Source "IIS*" -Newest 10

# Vérifier web.config
notepad C:\inetpub\wwwroot\maturation\frontend\dist\web.config
```

**Problème : Backend Flask ne répond pas**
```powershell
# Vérifier le service
Get-Service FlaskBackend

# Tester manuellement
cd C:\inetpub\wwwroot\maturation\backend
.\venv\Scripts\Activate.ps1
python app.py
# Regarder les erreurs dans la console
```

**Problème : PostgreSQL connection refused**
```powershell
# Vérifier que PostgreSQL écoute
netstat -an | findstr "5432"

# Tester connexion
psql -U maturation_user -d maturation_db -h localhost
```

**Problème : Erreur 502 Bad Gateway**
- Le backend Flask n'est pas démarré
- Le port 5000 est utilisé par autre chose
- Le `web.config` reverse proxy est mal configuré

---

## 📞 CONTACTS

**Support technique :** [À compléter]
**ANSD :** [À compléter]
**SONATEL (reverse proxy) :** [À compléter]

---

**Version :** 1.0 - Windows Server
**Date :** 2025-01-19
