#!/usr/bin/env python3
"""
Script de migration pour ajouter les colonnes fichier_joint à la table messages_projet
"""
import sys
import os
import sqlite3

# Chemin vers la base de données
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
db_path = os.path.join(backend_path, 'maturation.db')

def migrate():
    """Ajoute les colonnes fichier_joint si elles n'existent pas"""
    print("🔄 Démarrage de la migration pour les fichiers joints dans la discussion...")

    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Vérifier si la table existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages_projet'")
        if not cursor.fetchone():
            print("❌ La table messages_projet n'existe pas. Exécutez d'abord migrate_discussion.py")
            return False

        # Vérifier les colonnes existantes
        cursor.execute("PRAGMA table_info(messages_projet)")
        columns = {row[1] for row in cursor.fetchall()}

        # Ajouter les nouvelles colonnes si elles n'existent pas
        new_columns = {
            'fichier_joint': 'VARCHAR(500)',
            'fichier_joint_original': 'VARCHAR(500)',
            'fichier_joint_taille': 'INTEGER'
        }

        for col_name, col_type in new_columns.items():
            if col_name not in columns:
                print(f"   Ajout de la colonne {col_name}...")
                cursor.execute(f"ALTER TABLE messages_projet ADD COLUMN {col_name} {col_type}")
                print(f"   ✅ Colonne {col_name} ajoutée")
            else:
                print(f"   ℹ️  Colonne {col_name} déjà existante")

        conn.commit()

        # Afficher les colonnes finales
        cursor.execute("PRAGMA table_info(messages_projet)")
        print("\n📋 Colonnes de la table messages_projet:")
        for row in cursor.fetchall():
            print(f"  - {row[1]}: {row[2]}")

        conn.close()

        print("\n✅ Migration terminée avec succès!")
        print("   Les messages peuvent maintenant inclure des fichiers joints.")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
