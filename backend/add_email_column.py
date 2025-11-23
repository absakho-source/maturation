#!/usr/bin/env python3
"""
Script de migration pour ajouter la colonne email à la table users
"""

import sys
import os

# Ajouter le chemin du backend au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import db
from app import app
from sqlalchemy import text

def add_email_column():
    """Ajoute la colonne email à la table users si elle n'existe pas"""
    with app.app_context():
        try:
            # Vérifier si la colonne existe déjà
            result = db.session.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]

            if 'email' in columns:
                print("✓ La colonne 'email' existe déjà.")
                return True

            # Ajouter la colonne
            print("Ajout de la colonne 'email'...")
            db.session.execute(text(
                "ALTER TABLE users ADD COLUMN email VARCHAR(150)"
            ))
            db.session.commit()
            print("✓ Colonne 'email' ajoutée avec succès!")
            return True

        except Exception as e:
            print(f"✗ Erreur lors de l'ajout de la colonne: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Ajout de la colonne email")
    print("=" * 60)

    success = add_email_column()

    if success:
        print("\n✓ Migration terminée avec succès!")
    else:
        print("\n✗ Migration échouée!")
        sys.exit(1)
