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

# Lancer l'application
echo "[START] Démarrage de l'application..."
python app.py
