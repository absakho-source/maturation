#!/usr/bin/env python3
"""
Script de migration pré-démarrage
Exécuté AVANT app.py pour s'assurer que toutes les colonnes/tables existent
"""
import sqlite3
import os
import sys

# Déterminer le chemin de la base de données
DATA_DIR = os.environ.get('DATA_DIR', '/data')
db_path = os.path.join(DATA_DIR, 'maturation.db')

# Si la base n'existe pas dans /data, chercher dans le répertoire courant
if not os.path.exists(db_path):
    db_path = 'maturation.db'

print(f"[PRE-MIGRATION] Base de données: {db_path}")

try:
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # Migration 1: Colonne must_change_password dans users
    cur.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in cur.fetchall()]

    if 'must_change_password' not in cols:
        print("[PRE-MIGRATION] Ajout de la colonne must_change_password...")
        cur.execute("ALTER TABLE users ADD COLUMN must_change_password BOOLEAN DEFAULT 0")
        con.commit()
        print("[PRE-MIGRATION] ✓ Colonne must_change_password ajoutée")
    else:
        print("[PRE-MIGRATION] ✓ Colonne must_change_password existe déjà")

    # Migration 2: Colonnes GPS dans project
    cur.execute("PRAGMA table_info(project)")
    project_cols = [row[1] for row in cur.fetchall()]

    if 'gps_latitude' not in project_cols:
        print("[PRE-MIGRATION] Ajout des colonnes GPS au projet...")
        cur.execute("ALTER TABLE project ADD COLUMN gps_latitude REAL")
        cur.execute("ALTER TABLE project ADD COLUMN gps_longitude REAL")
        cur.execute("ALTER TABLE project ADD COLUMN gps_accuracy INTEGER")
        con.commit()
        print("[PRE-MIGRATION] ✓ Colonnes GPS ajoutées")
    else:
        print("[PRE-MIGRATION] ✓ Colonnes GPS existent déjà")

    # Migration 3: Activer must_change_password pour les comptes admin existants
    print("[PRE-MIGRATION] Activation du changement de mot de passe obligatoire pour les comptes admin...")
    roles_admin = ('admin', 'secretariatsct', 'presidencesct', 'presidencecomite')
    cur.execute("""
        UPDATE users
        SET must_change_password = 1
        WHERE role IN (?, ?, ?, ?)
        AND (must_change_password IS NULL OR must_change_password = 0)
    """, roles_admin)
    affected = cur.rowcount
    con.commit()
    print(f"[PRE-MIGRATION] ✓ {affected} compte(s) admin mis à jour pour forcer le changement de mot de passe")

    # Migration 4: Table project_version
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project_version'")
    if not cur.fetchone():
        print("[PRE-MIGRATION] Création de la table project_version...")
        cur.execute("""
            CREATE TABLE project_version (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                version_number INTEGER NOT NULL,
                modified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                modified_by VARCHAR(100),
                modification_type VARCHAR(50),
                change_summary TEXT,
                project_data TEXT NOT NULL,
                statut_before VARCHAR(100),
                statut_after VARCHAR(100),
                FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE
            )
        """)
        cur.execute("CREATE INDEX idx_project_version_project_id ON project_version(project_id)")
        cur.execute("CREATE INDEX idx_project_version_modified_at ON project_version(modified_at)")
        con.commit()
        print("[PRE-MIGRATION] ✓ Table project_version créée")
    else:
        print("[PRE-MIGRATION] ✓ Table project_version existe déjà")

    con.close()
    print("[PRE-MIGRATION] ✓ Migrations terminées avec succès!")
    sys.exit(0)

except Exception as e:
    print(f"[PRE-MIGRATION] ✗ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
