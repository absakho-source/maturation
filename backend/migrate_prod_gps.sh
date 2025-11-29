#!/bin/bash
# Script de migration pour ajouter les colonnes GPS en production (Render)

echo "[MIGRATION] Démarrage de la migration GPS en production..."

# Le chemin DATA_DIR est défini par Render
if [ -z "$DATA_DIR" ]; then
    export DATA_DIR="/data"
fi

export DB_PATH="$DATA_DIR/maturation.db"

echo "[MIGRATION] Base de données: $DB_PATH"

python3 migrate_prod_gps.py

echo "[MIGRATION] Migration terminée."
