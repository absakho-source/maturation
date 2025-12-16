#!/bin/bash

# Script de vérification et redémarrage des services sur Render
# Serveur: 164.92.255.58

echo "=========================================="
echo "Vérification et redémarrage production"
echo "=========================================="
echo ""

echo "1️⃣  Connexion au serveur de production..."
ssh -o ConnectTimeout=30 root@164.92.255.58 << 'ENDSSH'

cd /root/maturation

echo ""
echo "2️⃣  Vérification de la base de données..."
cd backend
source venv/bin/activate

# Vérifier le nombre de templates dans la base
echo "📊 Nombre de templates dans la base:"
sqlite3 /data/maturation.db "SELECT COUNT(*) FROM email_templates;"

echo ""
echo "📋 Liste des templates:"
sqlite3 /data/maturation.db "SELECT id, template_key, sujet, actif FROM email_templates;" -header -column

echo ""
echo "3️⃣  Vérification du chemin de la base de données dans app.py..."
grep -n "SQLALCHEMY_DATABASE_URI" app.py

echo ""
echo "4️⃣  Arrêt des services en cours..."
pkill -f "python.*app.py"
pkill -f "npm.*dev"
sleep 3

echo ""
echo "5️⃣  Redémarrage du backend..."
cd /root/maturation/backend
source venv/bin/activate
nohup python3 app.py > backend.log 2>&1 &
sleep 5

echo ""
echo "6️⃣  Redémarrage du frontend..."
cd /root/maturation/frontend
nohup npm run dev > frontend.log 2>&1 &
sleep 3

echo ""
echo "7️⃣  Vérification des processus..."
ps aux | grep -E "python.*app.py|npm.*dev" | grep -v grep

echo ""
echo "8️⃣  Test de l'API templates après redémarrage..."
sleep 5
curl -s "http://localhost:5000/api/admin/email-templates" -H "X-Role: admin" -H "X-Username: admin" | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'Nombre de templates retournés: {len(data.get(\"templates\", []))}')"

echo ""
echo "=========================================="
echo "✅ Vérification et redémarrage terminés"
echo "=========================================="

ENDSSH

echo ""
echo "=========================================="
echo "✅ Script terminé"
echo "=========================================="
