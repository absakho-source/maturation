#!/bin/bash
# Script de démarrage pour Render.com

# Créer les dossiers nécessaires
mkdir -p uploads static/uploads

# Initialiser la base de données si elle n'existe pas
python -c "from db import db; from app import app;
with app.app_context():
    db.create_all();
    print('Base de données initialisée')"

# IMPORTANT: Exécuter les migrations AVANT l'initialisation des données
echo "[MIGRATION] Exécution des migrations de schéma..."
[ -f migrations/add_must_change_password_column.py ] && python migrations/add_must_change_password_column.py || echo "[SKIP] add_must_change_password_column.py non trouvé"
[ -f migrations/add_project_versions_table.py ] && python migrations/add_project_versions_table.py || echo "[SKIP] add_project_versions_table.py non trouvé"

# Initialiser les ministères
echo "[INIT] Initialisation des ministères..."
[ -f migrations/create_ministeres_table.py ] && python migrations/create_ministeres_table.py || echo "[SKIP] create_ministeres_table.py non trouvé"

# Initialiser les données de démonstration (après les migrations)
echo "[INIT] Initialisation des données de démonstration..."
[ -f migrations/init_demo_data.py ] && python migrations/init_demo_data.py || echo "[SKIP] init_demo_data.py non trouvé"

# Lancer l'application
python app.py
