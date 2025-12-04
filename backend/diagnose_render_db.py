#!/usr/bin/env python3
"""
Script de diagnostic à exécuter sur Render via SSH
Pour vérifier les données de la base de production
"""
import sqlite3
import os
import sys

# Sur Render, DATA_DIR = /data
DATA_DIR = os.environ.get('DATA_DIR', '/data')
db_path = os.path.join(DATA_DIR, 'maturation.db')

print(f"[DIAGNOSE RENDER] Base de données: {db_path}\n")

if not os.path.exists(db_path):
    print(f"❌ ERREUR: Base de données introuvable à {db_path}")
    sys.exit(1)

try:
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # 1. Vérifier les colonnes recommandations
    print("=" * 80)
    print("1. COLONNES RECOMMANDATIONS")
    print("=" * 80)
    cur.execute("PRAGMA table_info(fiche_evaluation)")
    cols = cur.fetchall()
    col_names = [col[1] for col in cols]

    required_cols = [
        'pertinence_recommandations',
        'alignement_recommandations',
        'activites_couts_recommandations'
    ]

    for col in required_cols:
        if col in col_names:
            print(f"  ✓ {col}")
        else:
            print(f"  ✗ MANQUANT: {col}")

    # 2. Lister les fiches existantes
    print("\n" + "=" * 80)
    print("2. FICHES D'ÉVALUATION EXISTANTES")
    print("=" * 80)

    cur.execute("""
        SELECT f.id, f.project_id, p.numero_projet, p.titre, f.evaluateur_nom, f.fichier_pdf
        FROM fiche_evaluation f
        JOIN project p ON f.project_id = p.id
        ORDER BY f.id DESC
        LIMIT 10
    """)

    fiches = cur.fetchall()
    if not fiches:
        print("  ⚠️ Aucune fiche d'évaluation")
    else:
        for fiche in fiches:
            print(f"\n  Fiche ID={fiche[0]}, Projet={fiche[2] or f'ID{fiche[1]}'}")
            print(f"    Titre: {fiche[3][:50]}...")
            print(f"    Évaluateur: {fiche[4]}")
            print(f"    PDF: {fiche[5]}")

    # 3. Vérifier le projet 18 spécifiquement
    print("\n" + "=" * 80)
    print("3. DÉTAILS PROJET 18 (Test 4)")
    print("=" * 80)

    cur.execute("""
        SELECT
            f.id, f.evaluateur_nom,
            f.pertinence_score, f.pertinence_description, f.pertinence_recommandations,
            f.alignement_score, f.alignement_description, f.alignement_recommandations,
            f.fichier_pdf
        FROM fiche_evaluation f
        WHERE f.project_id = 18
    """)

    fiche18 = cur.fetchone()
    if not fiche18:
        print("  ⚠️ Aucune fiche pour le projet 18")
    else:
        print(f"  ✓ Fiche ID: {fiche18[0]}")
        print(f"  ✓ Évaluateur: {fiche18[1]}")
        print(f"\n  PERTINENCE:")
        print(f"    Score: {fiche18[2]}")
        print(f"    Description: {fiche18[3][:80] if fiche18[3] else '❌ VIDE'}...")
        print(f"    Recommandations: {fiche18[4][:80] if fiche18[4] else '❌ VIDE'}...")
        print(f"\n  ALIGNEMENT:")
        print(f"    Score: {fiche18[5]}")
        print(f"    Description: {fiche18[6][:80] if fiche18[6] else '❌ VIDE'}...")
        print(f"    Recommandations: {fiche18[7][:80] if fiche18[7] else '❌ VIDE'}...")
        print(f"\n  PDF: {fiche18[8]}")

    con.close()

    print("\n" + "=" * 80)
    print("[DIAGNOSE RENDER] Terminé!")
    print("=" * 80)

except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
