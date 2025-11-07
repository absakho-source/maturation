#!/bin/bash
# Script de redémarrage propre des serveurs

echo "🧹 NETTOYAGE COMPLET..."

# Tuer tous les processus Python et Node.js liés au projet
echo "🔧 Arrêt de tous les processus..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "python.*start_backend" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
pkill -f "node.*vite" 2>/dev/null || true

# Libérer les ports
echo "🔌 Libération des ports..."
lsof -ti:5002 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

# Attendre que tout se termine
sleep 5

echo "✅ Nettoyage terminé"
echo ""
echo "🚀 REDÉMARRAGE PROPRE..."

# Aller dans le bon répertoire
cd "/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation"

# Activer l'environnement virtuel
source venv/bin/activate

echo "📦 Environnement virtuel activé"

# Démarrer le backend
echo "🔧 Démarrage du backend..."
cd backend
nohup python app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "📡 Backend démarré (PID: $BACKEND_PID)"

# Attendre que le backend soit prêt
sleep 5

# Vérifier que le backend répond
echo "🔍 Test du backend..."
curl -s "http://127.0.0.1:5002/api/projects?role=admin&username=admin" > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Backend OK"
else
    echo "❌ Backend ne répond pas"
fi

# Démarrer le frontend
echo "🎨 Démarrage du frontend..."
cd frontend
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "📱 Frontend démarré (PID: $FRONTEND_PID)"

# Attendre que le frontend soit prêt
sleep 8

echo ""
echo "🎉 SERVEURS PRÊTS !"
echo "📡 Backend: http://127.0.0.1:5002"
echo "🎨 Frontend: http://127.0.0.1:5173"
echo ""
echo "📋 Pour tester la fiche d'évaluation:"
echo "   1. Aller sur http://127.0.0.1:5173"
echo "   2. Se connecter en tant qu'évaluateur"
echo "   3. Cliquer sur 'Évaluer' pour un projet"
echo ""
echo "📝 Logs:"
echo "   Backend: tail -f backend.log"
echo "   Frontend: tail -f frontend.log"