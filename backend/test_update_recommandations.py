#!/usr/bin/env python3
"""
Script de test pour vérifier la mise à jour des recommandations
Simule ce que fait l'API PUT /api/projects/{id}/fiche-evaluation
"""
import sqlite3
import os
import sys
import json

# Sur Render, DATA_DIR = /data
DATA_DIR = os.environ.get('DATA_DIR', '/data')
db_path = os.path.join(DATA_DIR, 'maturation.db')

if not os.path.exists(db_path):
    db_path = 'maturation.db'

print(f"[TEST UPDATE] Base de données: {db_path}\n")

project_id = 18

try:
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # 1. Vérifier l'état initial
    print("=" * 80)
    print("1. ÉTAT INITIAL")
    print("=" * 80)

    cur.execute("""
        SELECT id, pertinence_recommandations, alignement_recommandations
        FROM fiche_evaluation
        WHERE project_id = ?
    """, (project_id,))

    fiche = cur.fetchone()
    if not fiche:
        print(f"❌ Aucune fiche pour projet {project_id}")
        sys.exit(1)

    fiche_id = fiche[0]
    print(f"  Fiche ID: {fiche_id}")
    print(f"  pertinence_recommandations: '{fiche[1] or 'VIDE'}'")
    print(f"  alignement_recommandations: '{fiche[2] or 'VIDE'}'")

    # 2. Mettre à jour les recommandations (comme le fait l'API)
    print("\n" + "=" * 80)
    print("2. MISE À JOUR DES RECOMMANDATIONS")
    print("=" * 80)

    test_data = {
        'pertinence_recommandations': 'TEST RECO PERTINENCE - Script direct',
        'alignement_recommandations': 'TEST RECO ALIGNEMENT - Script direct'
    }

    print(f"  Mise à jour avec:")
    print(f"    pertinence_recommandations: '{test_data['pertinence_recommandations']}'")
    print(f"    alignement_recommandations: '{test_data['alignement_recommandations']}'")

    cur.execute("""
        UPDATE fiche_evaluation
        SET pertinence_recommandations = ?,
            alignement_recommandations = ?
        WHERE id = ?
    """, (
        test_data['pertinence_recommandations'],
        test_data['alignement_recommandations'],
        fiche_id
    ))

    con.commit()
    print("  ✓ UPDATE executé et commit effectué")

    # 3. Vérifier immédiatement après la mise à jour
    print("\n" + "=" * 80)
    print("3. VÉRIFICATION IMMÉDIATE APRÈS UPDATE")
    print("=" * 80)

    cur.execute("""
        SELECT pertinence_recommandations, alignement_recommandations
        FROM fiche_evaluation
        WHERE id = ?
    """, (fiche_id,))

    result = cur.fetchone()
    print(f"  pertinence_recommandations: '{result[0] or 'VIDE'}'")
    print(f"  alignement_recommandations: '{result[1] or 'VIDE'}'")

    # 4. Verdict
    print("\n" + "=" * 80)
    print("4. VERDICT")
    print("=" * 80)

    if result[0] == test_data['pertinence_recommandations'] and \
       result[1] == test_data['alignement_recommandations']:
        print("  ✅ SUCCESS: Les recommandations sont bien sauvegardées!")
        print("  → Le problème n'est PAS dans la base de données")
        print("  → Le problème est dans le code de l'API qui ne fait pas l'UPDATE")
    else:
        print("  ❌ ÉCHEC: Les recommandations ne sont pas sauvegardées")
        print("  → Problème au niveau de SQLite ou des permissions")

    con.close()

    print("\n" + "=" * 80)
    print("[TEST UPDATE] Terminé!")
    print("=" * 80)

except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
