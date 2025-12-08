#!/usr/bin/env python3
"""
Migration pour remplacer "approuvé définitivement par le Comité" par l'avis réel
"""

import os
import sys
import sqlite3

# Déterminer le chemin de la base de données
DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(__file__))
DB_PATH = os.path.join(DATA_DIR, 'maturation.db')

def migrate_approuve_definitif():
    """
    Remplace le statut "approuvé définitivement par le Comité" par l'avis réel du projet
    """

    print(f"📊 Migration des projets 'approuvé définitivement' dans: {DB_PATH}")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Trouver les projets avec "approuvé définitivement par le Comité"
    cursor.execute("""
        SELECT id, numero_projet, titre, avis
        FROM project
        WHERE statut = 'approuvé définitivement par le Comité'
    """)
    projects = cursor.fetchall()

    if not projects:
        print("✓ Aucun projet avec le statut 'approuvé définitivement par le Comité'")
        conn.close()
        return

    print(f"\n🔄 {len(projects)} projet(s) à migrer:\n")

    migrated = 0
    for project_id, numero, titre, avis in projects:
        print(f"  [{numero or 'N/A'}] {titre[:50]}...")
        print(f"    Avis actuel: {avis or 'NON DÉFINI'}")

        if avis:
            # Mettre à jour avec l'avis réel
            cursor.execute("""
                UPDATE project
                SET statut = ?
                WHERE id = ?
            """, (avis, project_id))
            print(f"    ✅ Statut mis à jour: {avis}\n")
            migrated += 1
        else:
            # Si pas d'avis, utiliser un fallback
            cursor.execute("""
                UPDATE project
                SET statut = 'validé par presidencecomite'
                WHERE id = ?
            """, (project_id,))
            print(f"    ⚠️ Pas d'avis défini - Fallback: 'validé par presidencecomite'\n")
            migrated += 1

    # Commit les changements
    conn.commit()

    print("=" * 60)
    print(f"✅ Migration terminée: {migrated} projet(s) migré(s)")

    # Afficher les statuts après migration
    print("\n📋 Vérification - Projets avec statut_comite='approuve_definitif':")
    cursor.execute("""
        SELECT numero_projet, titre, statut, avis
        FROM project
        WHERE statut_comite = 'approuve_definitif'
        ORDER BY id DESC
        LIMIT 5
    """)
    projects_after = cursor.fetchall()

    if projects_after:
        for numero, titre, statut, avis in projects_after:
            print(f"  [{numero or 'N/A'}] {titre[:40]}... → Statut: {statut}")
    else:
        print("  (Aucun projet)")

    conn.close()

if __name__ == '__main__':
    try:
        migrate_approuve_definitif()
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
