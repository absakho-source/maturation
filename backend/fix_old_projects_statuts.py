#!/usr/bin/env python3
"""
Script pour corriger les statuts des anciens projets exemples
Selon le workflow actuel de la plateforme
"""

import os
import sys
import sqlite3

DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(__file__))
DB_PATH = os.path.join(DATA_DIR, 'maturation.db')

def fix_old_projects():
    """
    Corrige les statuts des projets selon le workflow actuel:

    Workflow correct:
    1. soumis
    2. assigné
    3. en évaluation
    4. évalué
    5. compléments demandés (optionnel)
    6. compléments fournis (optionnel)
    7. en attente validation presidencesct
    8. validé par presidencesct
    9. validé par presidencecomite
    10. favorable / favorable sous conditions / défavorable (avis final)

    Problèmes identifiés:
    - Projets "en évaluation" avec un avis → doivent être "évalué"
    - Projets "évalué" sans validation_secretariat → doivent être "en attente validation presidencesct"
    - Projets "validé par presidencesct" sans avis_presidencesct → corriger
    - Projets "validé par presidencecomite" sans statut final → mettre l'avis comme statut
    - Projet "rejeté" avec avis favorable → incohérent
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=== CORRECTION DES STATUTS DES PROJETS ===\n")

    # Problème 1: Projets "en évaluation" qui ont un avis → doivent être "évalué"
    cursor.execute("""
        SELECT id, numero_projet, titre, statut, avis
        FROM project
        WHERE statut = 'en évaluation' AND avis IS NOT NULL AND avis != ''
    """)
    projects = cursor.fetchall()

    if projects:
        print(f"1. Correction de {len(projects)} projet(s) 'en évaluation' avec avis → 'évalué'")
        for project_id, numero, titre, statut, avis in projects:
            cursor.execute("""
                UPDATE project
                SET statut = 'évalué'
                WHERE id = ?
            """, (project_id,))
            print(f"   ✅ {numero or 'ID-'+str(project_id)}: {titre[:50]} → évalué")

    # Problème 2: Projets "évalué" avec validation_secretariat='valide' → "en attente validation presidencesct"
    cursor.execute("""
        SELECT id, numero_projet, titre, statut, validation_secretariat
        FROM project
        WHERE statut = 'évalué' AND validation_secretariat = 'valide'
    """)
    projects = cursor.fetchall()

    if projects:
        print(f"\n2. Correction de {len(projects)} projet(s) 'évalué' validé → 'en attente validation presidencesct'")
        for project_id, numero, titre, statut, validation in projects:
            cursor.execute("""
                UPDATE project
                SET statut = 'en attente validation presidencesct'
                WHERE id = ?
            """, (project_id,))
            print(f"   ✅ {numero or 'ID-'+str(project_id)}: {titre[:50]} → en attente validation presidencesct")

    # Problème 3: Projets "validé par presidencesct" qui devraient avoir avis_presidencesct
    cursor.execute("""
        SELECT id, numero_projet, titre
        FROM project
        WHERE statut = 'validé par presidencesct'
        AND (avis_presidencesct IS NULL OR avis_presidencesct = '')
    """)
    projects = cursor.fetchall()

    if projects:
        print(f"\n3. Ajout de avis_presidencesct='valide' pour {len(projects)} projet(s)")
        for project_id, numero, titre in projects:
            cursor.execute("""
                UPDATE project
                SET avis_presidencesct = 'valide'
                WHERE id = ?
            """, (project_id,))
            print(f"   ✅ {numero or 'ID-'+str(project_id)}: {titre[:50]} → avis_presidencesct='valide'")

    # Problème 4: Projets "validé par presidencecomite" avec decision_finale='confirme' → statut = avis
    cursor.execute("""
        SELECT id, numero_projet, titre, avis
        FROM project
        WHERE statut = 'validé par presidencecomite'
        AND decision_finale = 'confirme'
        AND avis IS NOT NULL AND avis != ''
    """)
    projects = cursor.fetchall()

    if projects:
        print(f"\n4. Correction de {len(projects)} projet(s) 'validé par presidencecomite' → avis final")
        for project_id, numero, titre, avis in projects:
            cursor.execute("""
                UPDATE project
                SET statut = ?
                WHERE id = ?
            """, (avis, project_id))
            print(f"   ✅ {numero or 'ID-'+str(project_id)}: {titre[:50]} → {avis}")

    # Problème 5: Projet "rejeté" incohérent
    cursor.execute("""
        SELECT id, numero_projet, titre, avis
        FROM project
        WHERE statut = 'rejeté' AND avis != 'défavorable'
    """)
    projects = cursor.fetchall()

    if projects:
        print(f"\n5. Correction de {len(projects)} projet(s) 'rejeté' incohérent")
        for project_id, numero, titre, avis in projects:
            # Si le projet a un avis favorable mais est rejeté, c'est incohérent
            # On suppose qu'il a été rejeté pour raisons administratives
            cursor.execute("""
                UPDATE project
                SET statut = 'rejeté',
                    avis = 'défavorable',
                    commentaires = 'Rejeté pour non-conformité administrative'
                WHERE id = ?
            """, (project_id,))
            print(f"   ✅ {numero or 'ID-'+str(project_id)}: {titre[:50]} → rejeté + avis défavorable")

    # Ajout de numéros de projets manquants
    cursor.execute("""
        SELECT id, titre
        FROM project
        WHERE numero_projet IS NULL OR numero_projet = ''
        ORDER BY id
    """)
    projects = cursor.fetchall()

    if projects:
        print(f"\n6. Ajout de numéros de projets pour {len(projects)} projet(s)")
        for idx, (project_id, titre) in enumerate(projects, 1):
            numero = f"DGPPE-25-{str(project_id).zfill(3)}"
            cursor.execute("""
                UPDATE project
                SET numero_projet = ?
                WHERE id = ?
            """, (numero, project_id))
            print(f"   ✅ ID-{project_id}: {titre[:50]} → {numero}")

    conn.commit()
    conn.close()

    print("\n✅ Correction des statuts terminée!\n")

if __name__ == '__main__':
    try:
        fix_old_projects()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
