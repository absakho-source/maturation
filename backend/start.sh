#!/bin/bash
# Script de démarrage pour Render.com

# Créer les dossiers nécessaires
mkdir -p uploads static/uploads

# Lancer l'application
# Les migrations sont gérées automatiquement par ensure_sqlite_columns() dans app.py
python app.py
