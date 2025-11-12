#!/bin/bash
# Script de démarrage pour Render.com

# Créer les dossiers nécessaires
mkdir -p uploads static/uploads

# Initialiser la base de données si elle n'existe pas
python -c "from db import db; from app import app;
with app.app_context():
    db.create_all();
    print('Base de données initialisée')"

# Initialiser les ministères
echo "[INIT] Initialisation des ministères..."
python create_ministeres_table.py

# Initialiser les données de démonstration
echo "[INIT] Initialisation des données de démonstration..."
python init_demo_data.py

# Lancer l'application
python app.py
