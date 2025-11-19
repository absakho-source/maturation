#!/usr/bin/env python3
"""
Script de migration rapide pour Render Shell
Ajoute les colonnes organisme_tutelle_data et structure_soumissionnaire
"""
import sqlite3
import os

def migrate_database(db_path=None):
    """Exécute la migration de la base de données"""
    # Trouver le chemin de la base de données
    if db_path is None:
        db_path = os.environ.get('DATABASE_PATH', 'maturation.db')
        if not os.path.exists(db_path) and os.path.exists('projects.db'):
            db_path = 'projects.db'

    print(f"[MIGRATION] Base de données: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Vérifier les colonnes existantes
        cursor.execute("PRAGMA table_info(project)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"[MIGRATION] Colonnes actuelles: {len(columns)}")

        # Ajouter organisme_tutelle_data
        if 'organisme_tutelle_data' not in columns:
            cursor.execute("ALTER TABLE project ADD COLUMN organisme_tutelle_data TEXT")
            print("✓ Colonne organisme_tutelle_data ajoutée")
        else:
            print("- organisme_tutelle_data existe déjà")

        # Ajouter structure_soumissionnaire
        if 'structure_soumissionnaire' not in columns:
            cursor.execute("ALTER TABLE project ADD COLUMN structure_soumissionnaire TEXT")
            print("✓ Colonne structure_soumissionnaire ajoutée")
        else:
            print("- structure_soumissionnaire existe déjà")

        conn.commit()
        conn.close()

        print("\n✓ Migration terminée avec succès")
        return True

    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("\nVous pouvez maintenant redémarrer le service backend sur Render.")
    else:
        print("\n✗ La migration a échoué")
        exit(1)
