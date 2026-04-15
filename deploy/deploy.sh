#!/bin/bash
# Script de déploiement PLASMAP sur serveur partagé (coexistence avec e-Présence)
# Serveur : 41.82.253.109
# Domaine  : maturation.economie.gouv.sn
#
# Usage : bash deploy.sh
# Lancer depuis le serveur après avoir copié le projet dans /var/www/plasmap

set -e

APP_DIR="/var/www/plasmap"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"

echo "======================================"
echo "  DÉPLOIEMENT PLASMAP"
echo "======================================"

# ── 1. Permissions ─────────────────────────────────────────────
echo "[1/7] Permissions..."
sudo chown -R $USER:$USER $APP_DIR

# ── 2. Backend Python ───────────────────────────────────────────
echo "[2/7] Backend - environnement Python..."
cd $BACKEND_DIR
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt --quiet
mkdir -p uploads static/uploads

echo "[2/7] Backend - initialisation base de données..."
python -c "
from db import db
from app import app
with app.app_context():
    db.create_all()
    print('  Base de données OK')
"

# Migrations si nécessaires
for script in add_missing_user_columns.py add_visibility_column.py create_ministeres_table.py; do
    if [ -f "$script" ]; then
        echo "  Migration: $script"
        python $script
    fi
done

deactivate

# ── 3. Frontend Vue.js ──────────────────────────────────────────
echo "[3/7] Frontend - installation dépendances..."
cd $FRONTEND_DIR
npm install --silent

echo "[3/7] Frontend - build production..."
npm run build

# ── 4. Certificat SSL auto-signé (temporaire) ──────────────────
echo "[4/7] Certificat SSL auto-signé (temporaire)..."
if [ ! -f /etc/ssl/certs/plasmap-selfsigned.crt ]; then
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/ssl/private/plasmap-selfsigned.key \
        -out /etc/ssl/certs/plasmap-selfsigned.crt \
        -subj "/C=SN/ST=Dakar/L=Dakar/O=DGPPE/CN=maturation.economie.gouv.sn"
    echo "  Certificat créé"
else
    echo "  Certificat déjà existant, conservé"
fi

# ── 5. Nginx ────────────────────────────────────────────────────
echo "[5/7] Configuration nginx..."
sudo cp $APP_DIR/deploy/nginx-plasmap.conf /etc/nginx/sites-available/plasmap

if [ ! -L /etc/nginx/sites-enabled/plasmap ]; then
    sudo ln -s /etc/nginx/sites-available/plasmap /etc/nginx/sites-enabled/
fi

sudo nginx -t && sudo systemctl reload nginx
echo "  Nginx rechargé"

# ── 6. Service systemd ──────────────────────────────────────────
echo "[6/7] Service systemd..."
sudo cp $APP_DIR/deploy/plasmap-backend.service /etc/systemd/system/
sudo chown -R www-data:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR
sudo chmod -R 775 $BACKEND_DIR/uploads
sudo systemctl daemon-reload
sudo systemctl enable plasmap-backend
sudo systemctl restart plasmap-backend

sleep 2
sudo systemctl status plasmap-backend --no-pager | head -10

# ── 7. Test ─────────────────────────────────────────────────────
echo "[7/7] Test de l'API..."
sleep 2
if curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
    echo "  ✓ Backend répond sur le port 5001"
else
    echo "  ⚠ Backend ne répond pas encore - vérifier : sudo journalctl -u plasmap-backend -n 30"
fi

echo ""
echo "======================================"
echo "  DÉPLOIEMENT TERMINÉ"
echo "  → https://maturation.economie.gouv.sn"
echo "======================================"
