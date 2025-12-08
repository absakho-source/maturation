#!/usr/bin/env python3
"""
Script complet pour corriger les données de production:
1. Mettre à jour fiche_evaluation_visible pour les projets entérinés
2. Supprimer les projets de test
"""

import os
import sqlite3

DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(__file__))
DB_PATH = os.path.join(DATA_DIR, 'maturation.db')

def fix_production_data():
    """
    Corrige les données de production
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=== CORRECTION DES DONNÉES DE PRODUCTION ===\n")

    # Étape 1: Mettre à jour fiche_evaluation_visible pour les projets entérinés
    print("1. Mise à jour de fiche_evaluation_visible pour les projets entérinés...")

    cursor.execute("""
        UPDATE project
        SET fiche_evaluation_visible = 1
        WHERE decision_finale = 'confirme'
        AND (fiche_evaluation_visible = 0 OR fiche_evaluation_visible IS NULL)
    """)
    count_updated = cursor.rowcount
    print(f"   ✅ {count_updated} projet(s) mis à jour avec fiche_evaluation_visible = True")

    # Étape 2: Supprimer les projets de test
    print("\n2. Suppression des projets de test...")

    # IDs des projets de test à supprimer
    test_project_ids = [1, 2, 4, 9, 13, 14, 15, 16, 18, 19]

    # Afficher les projets avant suppression
    cursor.execute("""
        SELECT id, numero_projet, titre, auteur_nom
        FROM project
        WHERE id IN ({})
        ORDER BY id
    """.format(','.join('?' * len(test_project_ids))), test_project_ids)

    projects_to_delete = cursor.fetchall()

    if projects_to_delete:
        print(f"   Projets à supprimer ({len(projects_to_delete)}):")
        for project_id, numero, titre, auteur in projects_to_delete:
            print(f"   - ID {project_id:3}: {numero or 'N/A':15} | {titre[:40]:40} | {auteur or 'N/A'}")

        # Supprimer les projets
        cursor.execute("""
            DELETE FROM project
            WHERE id IN ({})
        """.format(','.join('?' * len(test_project_ids))), test_project_ids)

        print(f"   ✅ {cursor.rowcount} projet(s) de test supprimé(s)")
    else:
        print("   ℹ️  Aucun projet de test trouvé avec ces IDs")

    # Étape 3: Afficher les projets restants
    print("\n3. Projets restants dans la base de données:")

    cursor.execute("""
        SELECT id, numero_projet, titre, auteur_nom, statut, fiche_evaluation_visible
        FROM project
        ORDER BY id
    """)
    remaining = cursor.fetchall()

    if remaining:
        print(f"   📋 {len(remaining)} projet(s) restant(s):")
        for project_id, numero, titre, auteur, statut, fiche_visible in remaining:
            fiche_icon = "🔓" if fiche_visible else "🔒"
            print(f"   {fiche_icon} ID {project_id:3}: {numero or 'N/A':15} | {titre[:30]:30} | {statut:20} | {auteur or 'N/A'}")
    else:
        print("   ⚠️  Aucun projet restant dans la base de données")

    conn.commit()
    conn.close()

    print("\n✅ Correction des données de production terminée!\n")

if __name__ == '__main__':
    try:
        fix_production_data()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
