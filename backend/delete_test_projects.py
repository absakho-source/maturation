#!/usr/bin/env python3
"""
Script pour supprimer les projets de test de la base de données
"""

import os
import sqlite3

DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(__file__))
DB_PATH = os.path.join(DATA_DIR, 'maturation.db')

def delete_test_projects():
    """
    Supprime les projets de test identifiés
    IDs à supprimer: 1, 2, 4, 9, 13, 14, 15, 16, 18, 19
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=== SUPPRESSION DES PROJETS DE TEST ===\n")

    # IDs des projets à supprimer
    test_project_ids = [1, 2, 4, 9, 13, 14, 15, 16, 18, 19]

    # Afficher les projets avant suppression
    cursor.execute("""
        SELECT id, numero_projet, titre, auteur_nom
        FROM project
        WHERE id IN ({})
        ORDER BY id
    """.format(','.join('?' * len(test_project_ids))), test_project_ids)

    projects = cursor.fetchall()

    if projects:
        print(f"Projets à supprimer ({len(projects)}):")
        for project_id, numero, titre, auteur in projects:
            print(f"  - ID {project_id}: {numero or 'N/A':15} | {titre[:40]:40} | {auteur or 'N/A'}")

        print("\nSuppression en cours...")

        # Supprimer les projets
        cursor.execute("""
            DELETE FROM project
            WHERE id IN ({})
        """.format(','.join('?' * len(test_project_ids))), test_project_ids)

        conn.commit()
        print(f"\n✅ {cursor.rowcount} projet(s) de test supprimé(s) avec succès!")
    else:
        print("Aucun projet de test trouvé avec ces IDs.")

    # Afficher les projets restants
    cursor.execute("""
        SELECT id, numero_projet, titre, auteur_nom
        FROM project
        ORDER BY id
    """)
    remaining = cursor.fetchall()

    if remaining:
        print(f"\n📋 Projets restants ({len(remaining)}):")
        for project_id, numero, titre, auteur in remaining:
            print(f"  - ID {project_id}: {numero or 'N/A':15} | {titre[:40]:40} | {auteur or 'N/A'}")
    else:
        print("\n⚠️  Aucun projet restant dans la base de données.")

    conn.close()
    print("\n✅ Opération terminée!\n")

if __name__ == '__main__':
    try:
        delete_test_projects()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
