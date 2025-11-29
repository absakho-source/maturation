#!/usr/bin/env python3
"""
Migration : Créer la table project_versions pour l'historique des modifications de projets

Cette table conserve une copie de chaque version d'un projet lors de modifications,
permettant de voir l'évolution d'un projet au fil du temps.
"""

import sqlite3
import os
import sys

# Chemin de la base de données
db_path = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "maturation.db"))
print(f"[MIGRATION] Utilisation de la base de données: {db_path}")

# Vérifier que la base existe
if not os.path.exists(db_path):
    print(f"❌ ERREUR: Base de données introuvable: {db_path}")
    sys.exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Vérifier si la table existe déjà
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project_version'")
    if cursor.fetchone():
        print("✅ La table 'project_version' existe déjà. Aucune migration nécessaire.")
        conn.close()
        sys.exit(0)

    # Créer la table project_version
    print("[MIGRATION] Création de la table project_version...")

    sql = """
    CREATE TABLE project_version (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        version_number INTEGER NOT NULL,

        -- Informations de versioning
        modified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        modified_by VARCHAR(100),
        modification_type VARCHAR(50),  -- 'creation', 'update', 'status_change', etc.
        change_summary TEXT,

        -- Snapshot complet du projet (JSON)
        project_data TEXT NOT NULL,  -- Tous les champs du projet en JSON

        -- Métadonnées
        statut_before VARCHAR(100),
        statut_after VARCHAR(100),

        FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE
    )
    """

    cursor.execute(sql)

    # Créer des index pour améliorer les performances
    print("[MIGRATION] Création des index...")
    cursor.execute("CREATE INDEX idx_project_version_project_id ON project_version(project_id)")
    cursor.execute("CREATE INDEX idx_project_version_modified_at ON project_version(modified_at)")

    conn.commit()
    print("✅ Table 'project_version' créée avec succès !")
    print("✅ Index créés avec succès !")

except Exception as e:
    print(f"❌ Erreur lors de la migration: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

finally:
    if conn:
        conn.close()
        print("[MIGRATION] Connexion fermée.")
