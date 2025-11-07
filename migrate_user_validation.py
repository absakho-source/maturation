#!/usr/bin/env python3
"""
Script de migration pour ajouter les champs de validation des comptes
"""
import sqlite3
import os

# Chemin vers la base de données
DB_PATH = os.path.join(os.path.dirname(__file__), 'backend', 'maturation.db')

def run_migration():
    """Exécute la migration"""
    print("🔄 Démarrage de la migration...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Lire le fichier SQL de migration
        migration_file = os.path.join(os.path.dirname(__file__), 'migrations', 'add_user_validation_fields.sql')

        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Exécuter chaque commande SQL
        commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip() and not cmd.strip().startswith('--')]

        for command in commands:
            if command:
                print(f"  Exécution: {command[:50]}...")
                cursor.execute(command)

        conn.commit()
        print("✅ Migration réussie !")

        # Afficher les colonnes de la table users
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\n📋 Colonnes de la table 'users' après migration:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de la migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    run_migration()
