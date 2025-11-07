#!/usr/bin/env python3
"""
Script de migration pour ajouter les champs d'évaluation préalable
"""
import sys
import os
import sqlite3

# Chemin vers la base de données
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
db_path = os.path.join(backend_path, 'maturation.db')

def migrate():
    """Ajoute les colonnes d'évaluation préalable si elles n'existent pas"""
    print("🔄 Démarrage de la migration pour l'évaluation préalable...")

    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Vérifier si la table existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project'")
        if not cursor.fetchone():
            print("❌ La table project n'existe pas")
            return False

        # Vérifier les colonnes existantes
        cursor.execute("PRAGMA table_info(project)")
        columns = {row[1] for row in cursor.fetchall()}

        # Ajouter les nouvelles colonnes si elles n'existent pas
        new_columns = {
            'evaluation_prealable': 'VARCHAR(50)',
            'evaluation_prealable_date': 'DATETIME',
            'evaluation_prealable_commentaire': 'TEXT'
        }

        for col_name, col_type in new_columns.items():
            if col_name not in columns:
                print(f"   Ajout de la colonne {col_name}...")
                cursor.execute(f"ALTER TABLE project ADD COLUMN {col_name} {col_type}")
                print(f"   ✅ Colonne {col_name} ajoutée")
            else:
                print(f"   ℹ️  Colonne {col_name} déjà existante")

        conn.commit()

        # Afficher les colonnes finales
        cursor.execute("PRAGMA table_info(project)")
        print("\n📋 Colonnes de la table project (nouvelles colonnes):")
        for row in cursor.fetchall():
            if row[1] in new_columns:
                print(f"  - {row[1]}: {row[2]}")

        conn.close()

        print("\n✅ Migration terminée avec succès!")
        print("   Les projets peuvent maintenant avoir une évaluation préalable.")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
