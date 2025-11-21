#!/usr/bin/env python3
"""
Script de migration pour ajouter la colonne email à la table users
"""

import sqlite3
import os

# Chemin vers la base de données
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'maturation.db')

def migrate():
    """Ajoute la colonne email à la table users"""

    if not os.path.exists(DB_PATH):
        print(f"Base de données non trouvée: {DB_PATH}")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Vérifier les colonnes existantes
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        # Ajouter email si elle n'existe pas
        if 'email' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(150)")
            print("✓ Colonne 'email' ajoutée")
        else:
            print("• Colonne 'email' existe déjà")

        conn.commit()
        print("\n✅ Migration email terminée avec succès!")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
