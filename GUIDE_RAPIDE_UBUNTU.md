# Guide Rapide - Installation Ubuntu Server
## Plateforme de Maturation DGPPE - Installation en 30 minutes

---

## ⚡ Installation Rapide

### 📋 Prérequis

**Serveur :**
- Ubuntu Server 22.04 LTS (64-bit)
- 4 vCPUs, 8 GB RAM, 100 GB SSD
- IP fixe publique
- Accès SSH avec clé (recommandé)

---

## 🚀 Installation en 8 étapes

### 1️⃣ MISE À JOUR SYSTÈME (2 min)

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git build-essential
```

---

### 2️⃣ INSTALLER PYTHON 3.10+ (3 min)

```bash
# Installer Python 3.10
sudo apt install -y python3.10 python3.10-venv python3-pip

# Vérifier
python3 --version  # Python 3.10.x

# Installer pip et virtualenv
sudo apt install -y python3-pip python3-venv
pip3 install --upgrade pip
```

---

### 3️⃣ INSTALLER POSTGRESQL 14+ (5 min)

```bash
# Installer PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Démarrer le service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Créer la base de données et l'utilisateur
sudo -u postgres psql <<EOF
CREATE DATABASE maturation_db;
CREATE USER maturation_user WITH PASSWORD 'VotreMotDePasseSecurise123!@#';
ALTER ROLE maturation_user SET client_encoding TO 'utf8';
ALTER ROLE maturation_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE maturation_user SET timezone TO 'Africa/Dakar';
GRANT ALL PRIVILEGES ON DATABASE maturation_db TO maturation_user;
\q
EOF

echo "✓ PostgreSQL configuré"
```

---

### 4️⃣ INSTALLER NODE.JS 18 LTS (3 min)

```bash
# Installer Node.js 18 LTS via NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Vérifier
node --version  # v18.x.x
npm --version   # 9.x.x
```

---

### 5️⃣ INSTALLER NGINX (2 min)

```bash
sudo apt install -y nginx

# Démarrer Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Vérifier
curl http://localhost  # Devrait afficher la page par défaut Nginx
```

---

### 6️⃣ CLONER ET CONFIGURER L'APPLICATION (7 min)

```bash
# Créer répertoire et cloner
sudo mkdir -p /opt/maturation
sudo chown $USER:$USER /opt/maturation
cd /opt/maturation
git clone https://github.com/absakho-source/maturation.git .

# ========== BACKEND ==========
cd backend

# Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Créer fichier .env
cat > .env <<'EOF'
DATABASE_TYPE=postgresql
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=maturation_db
DATABASE_USER=maturation_user
DATABASE_PASSWORD=VotreMotDePasseSecurise123!@#

FLASK_ENV=production
SECRET_KEY=generer_cle_aleatoire_32_caracteres_minimum_ici

UPLOAD_FOLDER=/opt/maturation/backend/uploads
MAX_CONTENT_LENGTH=52428800

CORS_ORIGINS=https://www.dgppe.sn
EOF

# Créer dossier uploads
mkdir -p uploads

# Initialiser la base de données
python3 <<'PYEOF'
from app import db, app
with app.app_context():
    db.create_all()
    print("✓ Base de données initialisée")
PYEOF

deactivate

# ========== FRONTEND ==========
cd ../frontend

# Installer dépendances
npm install

# Créer .env.production
cat > .env.production <<'EOF'
VITE_API_BASE_URL=/api
EOF

# Compiler le frontend
npm run build

echo "✓ Application configurée"
```

---

### 7️⃣ CRÉER SERVICE SYSTEMD POUR FLASK (3 min)

```bash
sudo tee /etc/systemd/system/maturation-backend.service > /dev/null <<'EOF'
[Unit]
Description=Maturation Backend Flask
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/maturation/backend
Environment="PATH=/opt/maturation/backend/venv/bin"
ExecStart=/opt/maturation/backend/venv/bin/python /opt/maturation/backend/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Ajuster permissions
sudo chown -R www-data:www-data /opt/maturation

# Démarrer le service
sudo systemctl daemon-reload
sudo systemctl start maturation-backend
sudo systemctl enable maturation-backend

# Vérifier
sudo systemctl status maturation-backend
```

---

### 8️⃣ CONFIGURER NGINX (5 min)

```bash
# Créer configuration Nginx
sudo tee /etc/nginx/sites-available/maturation <<'EOF'
server {
    listen 80;
    server_name _;

    # Logs
    access_log /var/log/nginx/maturation_access.log;
    error_log /var/log/nginx/maturation_error.log;

    # Frontend (Vue.js static files)
    root /opt/maturation/frontend/dist;
    index index.html;

    # Compression
    gzip on;
    gzip_types text/css application/javascript application/json;

    # Backend API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Vue.js SPA routing (must be last)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Activer le site
sudo ln -sf /etc/nginx/sites-available/maturation /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Tester et recharger Nginx
sudo nginx -t
sudo systemctl reload nginx

echo "✓ Nginx configuré"
```

---

### 9️⃣ CONFIGURER LE PARE-FEU UFW (2 min)

```bash
# Installer et configurer UFW
sudo apt install -y ufw

# Autoriser SSH, HTTP, HTTPS
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS

# Activer UFW
sudo ufw --force enable

# Vérifier
sudo ufw status
```

---

### 🔟 TESTER L'APPLICATION (2 min)

```bash
# Test backend Flask
curl http://localhost:5000/api/health
# Devrait retourner : {"status":"ok"}

# Test frontend Nginx
curl http://localhost/
# Devrait retourner le HTML de Vue.js

# Test depuis l'extérieur
curl http://<IP_PUBLIQUE_SERVEUR>/
# Devrait afficher la page de login
```

**Dans un navigateur :**
- Aller sur `http://<IP_PUBLIQUE_SERVEUR>/`
- La page de connexion devrait s'afficher ✅

---

## 🔐 CONFIGURER LES BACKUPS POSTGRESQL (5 min)

```bash
# Créer script de backup
sudo mkdir -p /opt/backups
sudo tee /opt/backups/backup_postgres.sh > /dev/null <<'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/postgres"
DATE=$(date +%Y-%m-%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/maturation_db_$DATE.sql"

mkdir -p $BACKUP_DIR

export PGPASSWORD='VotreMotDePasseSecurise123!@#'
pg_dump -U maturation_user -h localhost -d maturation_db -F c -f "$BACKUP_FILE"

# Supprimer backups de plus de 30 jours
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete

echo "✓ Backup créé: $BACKUP_FILE"
EOF

# Rendre exécutable
sudo chmod +x /opt/backups/backup_postgres.sh

# Ajouter à crontab (2:00 AM tous les jours)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/backups/backup_postgres.sh >> /var/log/postgres_backup.log 2>&1") | crontab -

# Test manuel
sudo /opt/backups/backup_postgres.sh
```

---

## 📞 COORDONNER AVEC LA SONATEL

Une fois l'installation terminée, contacter la SONATEL pour configurer le reverse proxy.

**Informations à fournir :**
- **IP publique du serveur ANSD :** `<IP_À_FOURNIR>`
- **URL cible :** `https://www.dgppe.sn/maturation`

**Configuration à demander (Nginx sur serveur SONATEL) :**

```nginx
# À ajouter dans /etc/nginx/sites-available/dgppe.sn
location /maturation/ {
    proxy_pass http://<IP_SERVEUR_ANSD>/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Une fois configuré, l'application sera accessible via : **`https://www.dgppe.sn/maturation`**

---

## ✅ CHECKLIST FINALE

```
□ Ubuntu 22.04 LTS installé et à jour
□ Python 3.10+ installé
□ PostgreSQL 14 installé et base créée
□ Node.js 18 LTS installé
□ Nginx installé et configuré
□ Application clonée dans /opt/maturation
□ Backend : venv créé + dépendances installées
□ Backend : .env configuré avec credentials PostgreSQL
□ Backend : Base de données initialisée (tables créées)
□ Frontend : npm install + npm run build réussi
□ Service systemd maturation-backend démarré
□ Nginx configuration activée (/etc/nginx/sites-enabled/maturation)
□ UFW activé (ports 22, 80, 443 ouverts)
□ PostgreSQL accessible uniquement en localhost
□ Backup script créé et planifié (cron 2:00 AM)
□ Test : http://<IP>/api/health retourne {"status":"ok"}
□ Test : http://<IP>/ affiche la page de login
□ Coordonné avec SONATEL pour reverse proxy
```

---

## 🔧 COMMANDES UTILES

### Redémarrer les services

```bash
sudo systemctl restart maturation-backend  # Flask
sudo systemctl restart nginx               # Nginx
sudo systemctl restart postgresql          # PostgreSQL
```

### Voir les logs

```bash
# Logs backend Flask
sudo journalctl -u maturation-backend -f

# Logs Nginx
sudo tail -f /var/log/nginx/maturation_error.log
sudo tail -f /var/log/nginx/maturation_access.log

# Logs PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### Vérifier statut des services

```bash
sudo systemctl status maturation-backend
sudo systemctl status nginx
sudo systemctl status postgresql
```

### Mettre à jour l'application

```bash
cd /opt/maturation

# Backend
git pull origin main
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart maturation-backend

# Frontend
cd ../frontend
npm install
npm run build
sudo systemctl reload nginx
```

---

## 🆘 DÉPANNAGE

### Problème : Backend Flask ne démarre pas

```bash
# Vérifier les logs
sudo journalctl -u maturation-backend -n 50

# Tester manuellement
cd /opt/maturation/backend
source venv/bin/activate
python app.py
# Regarder les erreurs dans la console
```

### Problème : Nginx erreur 502 Bad Gateway

```bash
# Vérifier que Flask tourne
curl http://localhost:5000/api/health

# Si ne répond pas, redémarrer Flask
sudo systemctl restart maturation-backend
```

### Problème : PostgreSQL connection refused

```bash
# Vérifier que PostgreSQL écoute
sudo ss -tlnp | grep 5432

# Tester connexion
psql -U maturation_user -d maturation_db -h localhost
```

### Problème : Page blanche ou 404

```bash
# Vérifier que les fichiers frontend sont compilés
ls -la /opt/maturation/frontend/dist/

# Si vide, recompiler
cd /opt/maturation/frontend
npm run build
```

---

## 📚 DOCUMENTS COMPLÉMENTAIRES

- **SPECS_TECHNIQUES_ANSD.md** : Spécifications techniques complètes
- **CONFIG_REVERSE_PROXY_SONATEL.md** : Configuration détaillée du reverse proxy

---

## 📞 CONTACTS

**Support technique :** [À compléter]
**ANSD :** [À compléter]
**SONATEL (reverse proxy) :** [À compléter]

---

**Version :** 1.0 - Ubuntu Server 22.04 LTS
**Date :** 2025-01-19
**Durée d'installation :** ~30 minutes
