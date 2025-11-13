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

# Exécuter les migrations de base de données
echo "[MIGRATION] Exécution des migrations..."
python add_visibility_column.py
python add_motivation_column.py

# Exécuter les migrations de données
echo "[DATA MIGRATION] Correction des données existantes..."
echo "oui" | python fix_stale_decision_finale.py || echo "[WARNING] fix_stale_decision_finale.py n'a pas corrigé de données (normal si aucune donnée à corriger)"

# Lancer l'application
python app.py
