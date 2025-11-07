#!/usr/bin/env python3
"""
Serveur de démarrage pour l'API backend
"""
import os
import sys

# Ajouter le répertoire backend au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurer le port
os.environ['FLASK_PORT'] = '5002'

# Importer et démarrer l'app
from app import app

if __name__ == '__main__':
    print("🚀 Démarrage du serveur backend sur le port 5002...")
    app.run(
        debug=True, 
        host="127.0.0.1", 
        port=5002, 
        use_reloader=False
    )