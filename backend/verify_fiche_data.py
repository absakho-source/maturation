#!/usr/bin/env python3
"""
Script pour vérifier EXACTEMENT ce qui est stocké dans la base de données
après une édition de fiche
"""
import sqlite3
import os
import sys
import json

# Déterminer le chemin de la base de données
DATA_DIR = os.environ.get('DATA_DIR', '/data')
db_path = os.path.join(DATA_DIR, 'maturation.db')

# Si la base n'existe pas dans /data, chercher dans le répertoire courant
if not os.path.exists(db_path):
    db_path = 'maturation.db'

print(f"[VERIFY] Base de données: {db_path}\n")

# ID du projet à vérifier (par défaut 18 - projet test 4)
project_id = int(sys.argv[1]) if len(sys.argv) > 1 else 18

try:
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # 1. Vérifier que les colonnes existent
    print("=" * 80)
    print("1. VÉRIFICATION DES COLONNES")
    print("=" * 80)
    cur.execute("PRAGMA table_info(fiche_evaluation)")
    cols = cur.fetchall()
    col_names = [col[1] for col in cols]

    required_cols = [
        'pertinence_recommandations',
        'alignement_recommandations',
        'activites_couts_recommandations',
        'equite_recommandations',
        'viabilite_recommandations',
        'rentabilite_recommandations',
        'benefices_strategiques_recommandations',
        'perennite_recommandations',
        'avantages_intangibles_recommandations',
        'faisabilite_recommandations',
        'ppp_recommandations',
        'impact_environnemental_recommandations'
    ]

    for col in required_cols:
        if col in col_names:
            print(f"  ✓ {col}")
        else:
            print(f"  ✗ MANQUANT: {col}")

    # 2. Récupérer TOUTES les données de la fiche
    print("\n" + "=" * 80)
    print(f"2. DONNÉES COMPLÈTES DE LA FICHE (projet {project_id})")
    print("=" * 80)

    cur.execute("""
        SELECT
            id, project_id, evaluateur_nom, proposition, recommandations,
            pertinence_score, pertinence_description, pertinence_recommandations,
            alignement_score, alignement_description, alignement_recommandations,
            activites_couts_score, activites_couts_description, activites_couts_recommandations,
            equite_score, equite_description, equite_recommandations,
            viabilite_score, viabilite_description, viabilite_recommandations,
            rentabilite_score, rentabilite_description, rentabilite_recommandations,
            benefices_strategiques_score, benefices_strategiques_description, benefices_strategiques_recommandations,
            perennite_score, perennite_description, perennite_recommandations,
            avantages_intangibles_score, avantages_intangibles_description, avantages_intangibles_recommandations,
            faisabilite_score, faisabilite_description, faisabilite_recommandations,
            ppp_score, ppp_description, ppp_recommandations,
            impact_environnemental_score, impact_environnemental_description, impact_environnemental_recommandations,
            fichier_pdf
        FROM fiche_evaluation
        WHERE project_id = ?
    """, (project_id,))

    fiche = cur.fetchone()

    if not fiche:
        print(f"❌ Aucune fiche trouvée pour le projet {project_id}")
        sys.exit(1)

    col_labels = [
        'id', 'project_id', 'evaluateur_nom', 'proposition', 'recommandations',
        'pertinence_score', 'pertinence_description', 'pertinence_recommandations',
        'alignement_score', 'alignement_description', 'alignement_recommandations',
        'activites_couts_score', 'activites_couts_description', 'activites_couts_recommandations',
        'equite_score', 'equite_description', 'equite_recommandations',
        'viabilite_score', 'viabilite_description', 'viabilite_recommandations',
        'rentabilite_score', 'rentabilite_description', 'rentabilite_recommandations',
        'benefices_strategiques_score', 'benefices_strategiques_description', 'benefices_strategiques_recommandations',
        'perennite_score', 'perennite_description', 'perennite_recommandations',
        'avantages_intangibles_score', 'avantages_intangibles_description', 'avantages_intangibles_recommandations',
        'faisabilite_score', 'faisabilite_description', 'faisabilite_recommandations',
        'ppp_score', 'ppp_description', 'ppp_recommandations',
        'impact_environnemental_score', 'impact_environnemental_description', 'impact_environnemental_recommandations',
        'fichier_pdf'
    ]

    print(f"\n✓ Fiche ID: {fiche[0]}")
    print(f"✓ Évaluateur: {fiche[2]}")
    print(f"✓ Proposition: {fiche[3]}")
    print(f"✓ Recommandations générales: {fiche[4][:100] if fiche[4] else 'VIDE'}...")
    print(f"✓ PDF: {fiche[-1]}")

    # 3. Vérifier chaque critère
    print("\n" + "=" * 80)
    print("3. DÉTAIL PAR CRITÈRE")
    print("=" * 80)

    criteria = [
        ('PERTINENCE', 5, 7),
        ('ALIGNEMENT', 8, 10),
        ('ACTIVITES_COUTS', 11, 13),
        ('EQUITE', 14, 16),
        ('VIABILITE', 17, 19),
        ('RENTABILITE', 20, 22),
        ('BENEFICES_STRATEGIQUES', 23, 25),
        ('PERENNITE', 26, 28),
        ('AVANTAGES_INTANGIBLES', 29, 31),
        ('FAISABILITE', 32, 34),
        ('PPP', 35, 37),
        ('IMPACT_ENVIRONNEMENTAL', 38, 40)
    ]

    total_score = 0
    for name, score_idx, desc_idx, reco_idx in [(c[0], c[1], c[1]+1, c[1]+2) for c in criteria]:
        score = fiche[score_idx]
        description = fiche[desc_idx]
        recommandations = fiche[reco_idx]

        total_score += score or 0

        print(f"\n{name}:")
        print(f"  Score: {score}")
        print(f"  Description: {description[:80] if description else '❌ VIDE'}...")
        print(f"  Recommandations: {recommandations[:80] if recommandations else '❌ VIDE'}...")

    print("\n" + "=" * 80)
    print(f"SCORE TOTAL: {total_score} / 100")
    print("=" * 80)

    # 4. Vérifier les anciennes versions
    print("\n" + "=" * 80)
    print("4. HISTORIQUE DES MODIFICATIONS")
    print("=" * 80)

    cur.execute("""
        SELECT id, evaluateur_nom, fichier_pdf
        FROM fiche_evaluation_archive
        WHERE project_id = ?
        ORDER BY id DESC
    """, (project_id,))

    archives = cur.fetchall()
    if archives:
        print(f"✓ {len(archives)} version(s) archivée(s):")
        for arch in archives:
            print(f"  - ID {arch[0]}, par {arch[1]}, PDF: {arch[2]}")
    else:
        print("⚠️ Aucune version archivée")

    con.close()

    print("\n" + "=" * 80)
    print("[VERIFY] Diagnostic terminé!")
    print("=" * 80)

except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
