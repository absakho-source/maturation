#!/usr/bin/env python3
"""
Script de migration pour ajouter la colonne visible_pour_roles à la table documents_projet
"""

import sys
import os

# Ajouter le chemin du backend au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import db
from app import app
from sqlalchemy import text

def add_visibility_column():
    """Ajoute la colonne visible_pour_roles si elle n'existe pas"""
    with app.app_context():
        try:
            # Vérifier si la colonne existe déjà
            result = db.session.execute(text("PRAGMA table_info(documents_projet)"))
            columns = [row[1] for row in result.fetchall()]

            if 'visible_pour_roles' in columns:
                print("✓ La colonne 'visible_pour_roles' existe déjà.")
                return True

            # Ajouter la colonne
            print("Ajout de la colonne 'visible_pour_roles'...")
            db.session.execute(text(
                "ALTER TABLE documents_projet ADD COLUMN visible_pour_roles TEXT"
            ))
            db.session.commit()
            print("✓ Colonne 'visible_pour_roles' ajoutée avec succès!")
            return True

        except Exception as e:
            print(f"✗ Erreur lors de l'ajout de la colonne: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Ajout de la colonne visible_pour_roles")
    print("=" * 60)

    success = add_visibility_column()

    if success:
        print("\n✓ Migration terminée avec succès!")
        sys.exit(0)
    else:
        print("\n✗ La migration a échoué.")
        sys.exit(1)
