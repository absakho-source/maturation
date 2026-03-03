#!/bin/bash
# Script de démarrage pour Render.com

# Créer les dossiers nécessaires
mkdir -p uploads static/uploads

# Exécuter les migrations critiques AVANT le démarrage de l'app
echo "[START] Exécution des migrations pré-démarrage..."
python pre_start_migration.py
if [ $? -ne 0 ]; then
    echo "[START] ✗ Échec des migrations pré-démarrage"
    exit 1
fi

# Exécuter les migrations de données
echo "[START] Exécution des migrations de données..."
python -c "from migrate_render import migrate_database; migrate_database()" || echo "[START] ⚠️ Migrations de données ignorées"

# Lancer l'application avec gunicorn (production)
echo "[START] Démarrage de l'application avec gunicorn..."
gunicorn app:app --workers 4 --threads 2 --bind 0.0.0.0:$PORT --timeout 120
