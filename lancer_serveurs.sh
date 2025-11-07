#!/bin/bash

# Script pour lancer les serveurs backend et frontend
echo "🚀 Démarrage de la plateforme de soumission DGPPE"

# Nettoyer les processus existants
echo "🧹 Nettoyage des processus existants..."
pkill -f "python.*app.py" 2>/dev/null
pkill -f "vite" 2>/dev/null
sleep 3

# Tuer les processus sur les ports si nécessaire
echo "🔌 Libération des ports..."
lsof -ti:5002 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null
sleep 2

# Changer vers le répertoire racine
cd "/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation"

# Activer l'environnement virtuel
echo "🐍 Activation de l'environnement Python..."
source venv/bin/activate

# Démarrer le backend Flask
echo "⚙️ Démarrage du backend Flask (port 5002)..."
cd backend
python app.py &
BACKEND_PID=$!
sleep 5

# Vérifier que le backend fonctionne
if lsof -i :5002 > /dev/null; then
    echo "✅ Backend démarré avec succès (PID: $BACKEND_PID)"
    
    # Test de l'API
    if curl -s "http://127.0.0.1:5002/api/users" > /dev/null; then
        echo "✅ API backend répond correctement"
    else
        echo "⚠️ API backend ne répond pas encore"
    fi
else
    echo "❌ Échec du démarrage du backend"
    exit 1
fi

# Démarrer le frontend Vite
echo "� Démarrage du frontend Vite (port 5173)..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
sleep 5

# Vérifier que le frontend fonctionne
if lsof -i :5173 > /dev/null; then
    echo "✅ Frontend démarré avec succès (PID: $FRONTEND_PID)"
else
    echo "❌ Échec du démarrage du frontend"
fi

echo ""
echo "🎉 SERVEURS LANCÉS !"
echo "� Frontend: http://127.0.0.1:5173"
echo "🔧 Backend API: http://127.0.0.1:5002"
echo ""
echo "� Pour arrêter les serveurs :"
echo "   pkill -f 'python.*app.py' && pkill -f 'vite'"
echo ""
echo "� États des processus :"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"