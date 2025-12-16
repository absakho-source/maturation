#!/bin/bash

# Script de déploiement de la configuration Gmail sur le serveur de production
# Serveur: 164.92.255.58

echo "=========================================="
echo "Déploiement de la configuration Gmail"
echo "=========================================="
echo ""

# Variables de configuration Gmail
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USERNAME="maturation.dgppe@gmail.com"
SMTP_PASSWORD="pfjwdshjptitxypl"
FROM_EMAIL="maturation.dgppe@gmail.com"
FROM_NAME="Maturation DGPPE"
PLATFORM_URL="https://maturation-dgppe.onrender.com"
EMAIL_ENABLED="true"
EMAIL_DEBUG_MODE="false"  # false en production

echo "1️⃣  Connexion au serveur de production..."
ssh -o ConnectTimeout=30 root@164.92.255.58 << 'ENDSSH'

cd /root/maturation

echo ""
echo "2️⃣  Mise à jour du code depuis GitHub..."
git pull origin main

echo ""
echo "3️⃣  Configuration des variables d'environnement..."

# Créer/Mettre à jour le fichier .env
cat > backend/.env << 'EOF'
# Configuration Email - Gmail
# IMPORTANT: Utilise un App Password Gmail pour l'authentification

# Configuration SMTP Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=maturation.dgppe@gmail.com
SMTP_PASSWORD=pfjwdshjptitxypl

# Email d'envoi
FROM_EMAIL=maturation.dgppe@gmail.com
FROM_NAME=Maturation DGPPE

# URL de la plateforme
PLATFORM_URL=https://maturation-dgppe.onrender.com

# Activer les emails en production
EMAIL_ENABLED=true
EMAIL_DEBUG_MODE=false
EOF

echo "✅ Fichier .env configuré"

echo ""
echo "4️⃣  Initialisation des templates d'emails..."
cd backend
source venv/bin/activate
python3 init_email_templates.py
cd ..

echo ""
echo "5️⃣  Arrêt des services en cours..."
pkill -f "python.*app.py"
pkill -f "npm.*dev"
sleep 2

echo ""
echo "6️⃣  Démarrage du backend..."
cd backend
source venv/bin/activate
nohup python3 app.py > backend.log 2>&1 &
sleep 3

echo ""
echo "7️⃣  Démarrage du frontend..."
cd ../frontend
nohup npm run dev > frontend.log 2>&1 &
sleep 3

echo ""
echo "8️⃣  Vérification des processus..."
ps aux | grep -E "python.*app.py|npm.*dev" | grep -v grep

echo ""
echo "=========================================="
echo "✅ Déploiement terminé avec succès!"
echo "=========================================="
echo ""
echo "Configuration appliquée:"
echo "  📧 SMTP: smtp.gmail.com:587"
echo "  👤 Compte: maturation.dgppe@gmail.com"
echo "  📨 From: maturation.dgppe@gmail.com"
echo "  🌐 URL: https://maturation-dgppe.onrender.com"
echo "  ✉️  Emails activés: OUI"
echo "  🐛 Debug mode: NON (production)"
echo ""

ENDSSH

echo ""
echo "=========================================="
echo "✅ Script de déploiement terminé"
echo "=========================================="
