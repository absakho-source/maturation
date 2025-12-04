#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier les colonnes recommandations
"""
import sqlite3
import os
import sys

# Déterminer le chemin de la base de données
DATA_DIR = os.environ.get('DATA_DIR', '/data')
db_path = os.path.join(DATA_DIR, 'maturation.db')

# Si la base n'existe pas dans /data, chercher dans le répertoire courant
if not os.path.exists(db_path):
    db_path = 'maturation.db'

print(f"[DIAGNOSTIC] Base de données: {db_path}\n")

try:
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # 1. Vérifier les colonnes recommandations
    print("=" * 80)
    print("1. COLONNES RECOMMANDATIONS DANS fiche_evaluation")
    print("=" * 80)
    cur.execute("PRAGMA table_info(fiche_evaluation)")
    cols = cur.fetchall()
    recommandations_cols = [col for col in cols if 'recommandations' in col[1]]

    for col in recommandations_cols:
        print(f"  ✓ {col[1]} (type: {col[2]})")

    # 2. Vérifier les données existantes
    print("\n" + "=" * 80)
    print("2. DONNÉES DE RECOMMANDATIONS DANS LA BASE")
    print("=" * 80)

    cur.execute("""
        SELECT id, project_id,
               pertinence_recommandations,
               alignement_recommandations,
               activites_couts_recommandations,
               equite_recommandations,
               viabilite_recommandations,
               rentabilite_recommandations
        FROM fiche_evaluation
        WHERE id IS NOT NULL
    """)

    fiches = cur.fetchall()
    if not fiches:
        print("  ⚠️ Aucune fiche d'évaluation dans la base")
    else:
        for fiche in fiches:
            print(f"\n  Fiche ID={fiche[0]}, Project ID={fiche[1]}")
            has_data = False
            for i, col_name in enumerate(['pertinence', 'alignement', 'activites_couts', 'equite', 'viabilite', 'rentabilite']):
                value = fiche[i+2]
                if value:
                    print(f"    ✓ {col_name}_recommandations: '{value[:50]}...'")
                    has_data = True
                else:
                    print(f"    ✗ {col_name}_recommandations: VIDE")

            if not has_data:
                print(f"    ⚠️ Aucune recommandation pour cette fiche")

    # 3. Vérifier les PDFs générés
    print("\n" + "=" * 80)
    print("3. PDFs GÉNÉRÉS")
    print("=" * 80)

    cur.execute("SELECT id, project_id, fichier_pdf FROM fiche_evaluation WHERE fichier_pdf IS NOT NULL")
    pdfs = cur.fetchall()

    if not pdfs:
        print("  ⚠️ Aucun PDF généré")
    else:
        for pdf in pdfs:
            print(f"  ✓ Fiche ID={pdf[0]}, Project ID={pdf[1]}, PDF={pdf[2]}")

    con.close()
    print("\n" + "=" * 80)
    print("[DIAGNOSTIC] Terminé!")
    print("=" * 80)

except Exception as e:
    print(f"[DIAGNOSTIC] ✗ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
