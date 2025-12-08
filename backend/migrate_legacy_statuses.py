#!/usr/bin/env python3
"""
Migration script pour nettoyer les statuts legacy (Catégorie 9)

Ce script migre les anciens formats de statuts vers les nouveaux:
- "en_evaluation" → "en évaluation"
- "approuvé" → "validé par presidencecomite"
- "valide_sct" → "validé par presidencesct"
- "compléments soumis" → "compléments fournis"
"""

import os
import sys
import sqlite3
from datetime import datetime

# Déterminer le chemin de la base de données
DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(__file__))
DB_PATH = os.path.join(DATA_DIR, 'maturation.db')

def migrate_legacy_statuses():
    """Migrer les statuts legacy vers les nouveaux formats"""

    print(f"📊 Migration des statuts legacy dans: {DB_PATH}")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Mapping des migrations
    migrations = {
        'en_evaluation': 'en évaluation',
        'approuvé': 'validé par presidencecomite',
        'valide_sct': 'validé par presidencesct',
        'compléments soumis': 'compléments fournis'
    }

    total_migrated = 0

    for old_status, new_status in migrations.items():
        # Compter les projets à migrer
        cursor.execute("SELECT COUNT(*) FROM project WHERE statut = ?", (old_status,))
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"\n🔄 Migration: '{old_status}' → '{new_status}'")

            # Afficher les projets concernés
            cursor.execute(
                "SELECT id, numero_projet, titre FROM project WHERE statut = ?",
                (old_status,)
            )
            projects = cursor.fetchall()

            for project_id, numero, titre in projects:
                print(f"  - [{numero}] {titre[:50]}...")

            # Effectuer la migration
            cursor.execute(
                "UPDATE project SET statut = ? WHERE statut = ?",
                (new_status, old_status)
            )

            print(f"  ✅ {count} projet(s) migré(s)")
            total_migrated += count
        else:
            print(f"✓ Aucun projet avec le statut '{old_status}'")

    # Commit les changements
    conn.commit()

    print("\n" + "=" * 60)
    print(f"✅ Migration terminée: {total_migrated} projet(s) migré(s) au total")

    # Afficher les statuts restants
    print("\n📋 Statuts actuels dans la base de données:")
    cursor.execute("SELECT DISTINCT statut, COUNT(*) FROM project GROUP BY statut ORDER BY statut")
    statuses = cursor.fetchall()

    for statut, count in statuses:
        print(f"  - {statut}: {count} projet(s)")

    conn.close()

if __name__ == '__main__':
    try:
        migrate_legacy_statuses()
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
