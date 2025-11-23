#!/usr/bin/env python3
"""
Script de migration pour ajouter toutes les colonnes manquantes à la table users
"""

import sys
import os

# Ajouter le chemin du backend au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import db
from app import app
from sqlalchemy import text

def add_missing_columns():
    """Ajoute toutes les colonnes manquantes à la table users"""
    with app.app_context():
        try:
            # Vérifier les colonnes existantes
            result = db.session.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]

            # Liste des colonnes à ajouter avec leurs définitions
            columns_to_add = [
                ('email', 'VARCHAR(150)'),
                ('nom_complet', 'VARCHAR(255)'),
                ('fonction', 'VARCHAR(255)'),
                ('telephone', 'VARCHAR(20)'),
                ('type_structure', 'VARCHAR(50)'),
                ('type_institution', 'VARCHAR(50)'),
                ('nom_structure', 'VARCHAR(255)'),
                ('direction_service', 'VARCHAR(255)'),
                ('nom_ministere', 'VARCHAR(300)'),
                ('tutelle_agence', 'VARCHAR(300)'),
                ('justificatif_path', 'VARCHAR(500)'),
                ('statut_compte', "VARCHAR(50) DEFAULT 'non_verifie'"),
                ('date_verification', 'DATETIME'),
                ('verifie_par', 'VARCHAR(100)'),
                ('date_creation', 'DATETIME'),
                ('is_point_focal', 'BOOLEAN DEFAULT 0'),
                ('point_focal_organisme', 'VARCHAR(300)'),
            ]

            added_count = 0
            for col_name, col_type in columns_to_add:
                if col_name not in columns:
                    print(f"Ajout de la colonne '{col_name}'...")
                    db.session.execute(text(
                        f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"
                    ))
                    db.session.commit()
                    print(f"✓ Colonne '{col_name}' ajoutée")
                    added_count += 1
                else:
                    print(f"• Colonne '{col_name}' existe déjà")

            if added_count > 0:
                print(f"\n✓ {added_count} colonne(s) ajoutée(s)")
            else:
                print("\n• Toutes les colonnes existent déjà")

            return True

        except Exception as e:
            print(f"✗ Erreur lors de la migration: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Ajout des colonnes manquantes à users")
    print("=" * 60)

    success = add_missing_columns()

    if success:
        print("\n✅ Migration terminée avec succès!")
    else:
        print("\n❌ Migration échouée!")
        sys.exit(1)
