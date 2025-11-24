#!/bin/bash

# =============================================================================
# Script d'installation automatique PLASMAP
# Usage: sudo bash install.sh [IP_DU_SERVEUR]
# =============================================================================

set -e  # Arrêter si une commande échoue

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Vérifier si root
if [ "$EUID" -ne 0 ]; then
    error "Ce script doit être exécuté en tant que root (sudo bash install.sh)"
fi

# Récupérer l'IP du serveur
if [ -z "$1" ]; then
    SERVER_IP=$(hostname -I | awk '{print $1}')
    echo ""
    info "Adresse IP détectée: $SERVER_IP"
    read -p "Appuyez sur Entrée pour confirmer ou tapez une autre IP: " INPUT_IP
    if [ -n "$INPUT_IP" ]; then
        SERVER_IP=$INPUT_IP
    fi
else
    SERVER_IP=$1
fi

info "Installation de PLASMAP pour l'IP: $SERVER_IP"
echo ""

# =============================================================================
# ÉTAPE 1: Mise à jour du système
# =============================================================================
info "Étape 1/8: Mise à jour du système..."
apt update -qq
apt upgrade -y -qq

# =============================================================================
# ÉTAPE 2: Installation des dépendances
# =============================================================================
info "Étape 2/8: Installation des dépendances..."
apt install -y -qq python3 python3-pip python3-venv nodejs npm git nginx curl

# Vérifier les versions
info "Versions installées:"
echo "  - Python: $(python3 --version)"
echo "  - Node: $(node --version)"
echo "  - NPM: $(npm --version)"
echo "  - Nginx: $(nginx -v 2>&1)"

# =============================================================================
# ÉTAPE 3: Création des dossiers
# =============================================================================
info "Étape 3/8: Création des dossiers..."
mkdir -p /var/www/plasmap
cd /var/www/plasmap

# =============================================================================
# ÉTAPE 4: Téléchargement du code
# =============================================================================
info "Étape 4/8: Téléchargement du code..."

if [ -d ".git" ]; then
    info "Mise à jour du code existant..."
    git pull origin main
else
    # Essayer Git d'abord
    if git clone https://github.com/absakho-source/maturation.git . 2>/dev/null; then
        info "Code téléchargé via Git"
    else
        error "Impossible de cloner le repo. Copiez manuellement les fichiers dans /var/www/plasmap"
    fi
fi

# =============================================================================
# ÉTAPE 5: Configuration du Backend
# =============================================================================
info "Étape 5/8: Configuration du Backend..."
cd /var/www/plasmap/backend

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -q -r requirements.txt

# Créer les dossiers
mkdir -p uploads static/uploads

# Initialiser la base de données
python -c "from db import db; from app import app;
with app.app_context():
    db.create_all()
    print('Base de données créée')"

# Exécuter les migrations
[ -f add_missing_user_columns.py ] && python add_missing_user_columns.py
[ -f add_visibility_column.py ] && python add_visibility_column.py
[ -f create_ministeres_table.py ] && python create_ministeres_table.py
[ -f init_demo_data.py ] && python init_demo_data.py

deactivate

# =============================================================================
# ÉTAPE 6: Configuration du Frontend
# =============================================================================
info "Étape 6/8: Configuration du Frontend..."
cd /var/www/plasmap/frontend

npm install --silent
npm run build

# =============================================================================
# ÉTAPE 7: Configuration des services
# =============================================================================
info "Étape 7/8: Configuration des services..."

# Créer le service systemd pour le backend
cat > /etc/systemd/system/plasmap-backend.service << 'EOF'
[Unit]
Description=PLASMAP Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/plasmap/backend
Environment="PATH=/var/www/plasmap/backend/venv/bin"
ExecStart=/var/www/plasmap/backend/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Créer la configuration Nginx
cat > /etc/nginx/sites-available/plasmap << EOF
server {
    listen 80;
    server_name $SERVER_IP;

    client_max_body_size 100M;

    location / {
        root /var/www/plasmap/frontend/dist;
        try_files \$uri \$uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /uploads {
        alias /var/www/plasmap/backend/uploads;
    }
}
EOF

# Activer le site
ln -sf /etc/nginx/sites-available/plasmap /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Tester Nginx
nginx -t

# =============================================================================
# ÉTAPE 8: Permissions et démarrage
# =============================================================================
info "Étape 8/8: Configuration des permissions et démarrage..."

# Permissions
chown -R www-data:www-data /var/www/plasmap
chmod -R 755 /var/www/plasmap
chmod -R 775 /var/www/plasmap/backend/uploads

# Recharger et démarrer les services
systemctl daemon-reload
systemctl enable plasmap-backend
systemctl start plasmap-backend
systemctl restart nginx

# Configurer le pare-feu
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 22/tcp
    ufw --force enable
fi

# =============================================================================
# VÉRIFICATION
# =============================================================================
echo ""
echo "=============================================="
info "Installation terminée!"
echo "=============================================="
echo ""

# Vérifier les services
if systemctl is-active --quiet plasmap-backend; then
    echo -e "${GREEN}[OK]${NC} Backend: actif"
else
    echo -e "${RED}[ERREUR]${NC} Backend: inactif"
fi

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}[OK]${NC} Nginx: actif"
else
    echo -e "${RED}[ERREUR]${NC} Nginx: inactif"
fi

# Test API
sleep 2
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}[OK]${NC} API: accessible"
else
    echo -e "${YELLOW}[WARN]${NC} API: en cours de démarrage..."
fi

echo ""
echo "=============================================="
echo "ACCÈS À L'APPLICATION"
echo "=============================================="
echo ""
echo "URL: http://$SERVER_IP"
echo ""
echo "Identifiants par défaut:"
echo "  Admin:          admin / admin123"
echo "  Secrétariat:    secretariat / secret123"
echo "  Évaluateur:     evaluateur1 / eval123"
echo "  Soumissionnaire: soumissionnaire / soum123"
echo ""
echo "=============================================="
echo "COMMANDES UTILES"
echo "=============================================="
echo ""
echo "Voir les logs:     sudo journalctl -u plasmap-backend -f"
echo "Redémarrer:        sudo systemctl restart plasmap-backend"
echo "État du service:   sudo systemctl status plasmap-backend"
echo ""
