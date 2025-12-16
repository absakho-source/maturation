#!/bin/bash

# Script de déploiement des nouveaux tableaux de fiche d'évaluation sur Render
# Serveur: 164.92.255.58

echo "=========================================="
echo "Déploiement tableaux Fiche Évaluation"
echo "=========================================="
echo ""

echo "1️⃣  Push des modifications vers GitHub..."
git push origin main
if [ $? -ne 0 ]; then
    echo "❌ Erreur lors du push vers GitHub"
    exit 1
fi
echo "✅ Push réussi"
echo ""

echo "2️⃣  Connexion au serveur de production..."
ssh -o ConnectTimeout=30 root@164.92.255.58 << 'ENDSSH'

cd /root/maturation

echo ""
echo "3️⃣  Pull des modifications depuis GitHub..."
git pull origin main

echo ""
echo "4️⃣  Exécution de la migration de la base de données..."
cd backend
source venv/bin/activate
python3 add_fiche_section_i_fields.py

echo ""
echo "5️⃣  Redémarrage des services..."
pkill -f "python.*app.py"
pkill -f "npm.*dev"
sleep 3

echo ""
echo "6️⃣  Démarrage du backend..."
nohup python3 app.py > backend.log 2>&1 &
sleep 5

echo ""
echo "7️⃣  Démarrage du frontend..."
cd /root/maturation/frontend
nohup npm run dev > frontend.log 2>&1 &
sleep 3

echo ""
echo "8️⃣  Vérification des processus..."
ps aux | grep -E "python.*app.py|npm.*dev" | grep -v grep

echo ""
echo "9️⃣  Vérification de la migration..."
cd /root/maturation/backend
sqlite3 /data/maturation.db "PRAGMA table_info(fiche_evaluation);" | grep -E "articulation|axes|odd"

echo ""
echo "=========================================="
echo "✅ Déploiement terminé"
echo "=========================================="

ENDSSH

echo ""
echo "=========================================="
echo "✅ Script terminé"
echo "=========================================="
echo ""
echo "📋 Vérification:"
echo "   1. Connectez-vous à l'interface admin: https://maturation-dgppe.onrender.com"
echo "   2. Créez ou modifiez une fiche d'évaluation"
echo "   3. Vérifiez que les 4 tableaux apparaissent correctement"
echo ""
