#!/usr/bin/env python3
"""
Script de migration: Ajouter les champs de la section I à la table fiche_evaluation
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app
from db import db
import sqlite3

def add_fiche_section_i_fields():
    """Ajoute les champs de présentation du projet (Section I) à fiche_evaluation"""

    with app.app_context():
        print("=" * 60)
        print("MIGRATION: Ajout des champs Section I à fiche_evaluation")
        print("=" * 60)
        print()

        # Récupérer le chemin de la base de données
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        print(f"📂 Base de données: {db_path}")
        print()

        # Liste des colonnes à ajouter
        columns_to_add = [
            # Champs de base
            ("intitule_projet", "TEXT"),
            ("cout_projet", "VARCHAR(100)"),
            ("origine_projet", "TEXT"),

            # Dimensions transversales
            ("cc_adaptation", "BOOLEAN DEFAULT 0"),
            ("cc_attenuation", "BOOLEAN DEFAULT 0"),
            ("genre", "BOOLEAN DEFAULT 0"),

            # Nouveaux champs - Tableau de présentation
            ("articulation", "TEXT"),
            ("axes", "TEXT"),
            ("objectifs_strategiques", "TEXT"),
            ("odd", "TEXT"),

            # Durées
            ("duree_analyse", "VARCHAR(50)"),
            ("realisation", "VARCHAR(50)"),
            ("exploitation", "VARCHAR(50)"),

            # Autres informations projet
            ("localisation", "TEXT"),
            ("parties_prenantes", "TEXT"),
            ("autres_projets_connexes", "TEXT"),
            ("objectif_projet", "TEXT"),
            ("activites_principales", "TEXT"),
            ("resultats_attendus", "TEXT"),

            # Anciens champs (pour compatibilité)
            ("sous_secteur", "TEXT"),
            ("organisme_tutelle", "TEXT"),
            ("snd_2025_2029", "TEXT"),
        ]

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Récupérer les colonnes existantes
        cursor.execute("PRAGMA table_info(fiche_evaluation)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        print(f"📋 Colonnes existantes: {len(existing_columns)}")
        print()

        added_count = 0
        skipped_count = 0

        for column_name, column_type in columns_to_add:
            if column_name in existing_columns:
                print(f"  ⏭️  '{column_name}' existe déjà")
                skipped_count += 1
                continue

            try:
                sql = f"ALTER TABLE fiche_evaluation ADD COLUMN {column_name} {column_type}"
                cursor.execute(sql)
                print(f"  ✅ '{column_name}' ajoutée ({column_type})")
                added_count += 1
            except Exception as e:
                print(f"  ❌ Erreur lors de l'ajout de '{column_name}': {e}")

        conn.commit()
        conn.close()

        print()
        print("=" * 60)
        print(f"✅ Migration terminée!")
        print(f"   - {added_count} colonnes ajoutées")
        print(f"   - {skipped_count} colonnes déjà existantes")
        print("=" * 60)

if __name__ == '__main__':
    add_fiche_section_i_fields()
