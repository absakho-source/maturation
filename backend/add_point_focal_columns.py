#!/usr/bin/env python3
"""
Script de migration pour ajouter les colonnes Point Focal à la table users
"""

import sys
import os

# Ajouter le chemin du backend au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import db
from app import app
from sqlalchemy import text

def add_point_focal_columns():
    """Ajoute les colonnes Point Focal à la table users si elles n'existent pas"""
    with app.app_context():
        try:
            # Vérifier les colonnes existantes
            result = db.session.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]

            # Ajouter is_point_focal si elle n'existe pas
            if 'is_point_focal' not in columns:
                print("Ajout de la colonne 'is_point_focal'...")
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN is_point_focal BOOLEAN DEFAULT 0"
                ))
                db.session.commit()
                print("✓ Colonne 'is_point_focal' ajoutée")
            else:
                print("• Colonne 'is_point_focal' existe déjà")

            # Ajouter point_focal_organisme si elle n'existe pas
            if 'point_focal_organisme' not in columns:
                print("Ajout de la colonne 'point_focal_organisme'...")
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN point_focal_organisme VARCHAR(300)"
                ))
                db.session.commit()
                print("✓ Colonne 'point_focal_organisme' ajoutée")
            else:
                print("• Colonne 'point_focal_organisme' existe déjà")

            return True

        except Exception as e:
            print(f"✗ Erreur lors de la migration: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Ajout des colonnes Point Focal")
    print("=" * 60)

    success = add_point_focal_columns()

    if success:
        print("\n✅ Migration Point Focal terminée avec succès!")
    else:
        print("\n❌ Migration échouée!")
        sys.exit(1)
