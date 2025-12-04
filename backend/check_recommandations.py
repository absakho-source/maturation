#!/usr/bin/env python3
"""
Script pour vérifier les recommandations d'une fiche spécifique
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

print(f"[CHECK] Base de données: {db_path}\n")

# ID du projet à vérifier (par défaut 18)
project_id = int(sys.argv[1]) if len(sys.argv) > 1 else 18

try:
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # Récupérer la fiche
    cur.execute("""
        SELECT
            id,
            project_id,
            evaluateur_nom,
            pertinence_score,
            pertinence_description,
            pertinence_recommandations,
            alignement_score,
            alignement_description,
            alignement_recommandations,
            fichier_pdf
        FROM fiche_evaluation
        WHERE project_id = ?
    """, (project_id,))

    fiche = cur.fetchone()

    if not fiche:
        print(f"❌ Aucune fiche trouvée pour le projet {project_id}")
        sys.exit(1)

    print(f"✓ Fiche trouvée pour le projet {project_id}")
    print(f"  - ID fiche: {fiche[0]}")
    print(f"  - Évaluateur: {fiche[2]}")
    print(f"  - PDF: {fiche[9]}")
    print()
    print("=" * 80)
    print("PERTINENCE")
    print("=" * 80)
    print(f"  Score: {fiche[3]}")
    print(f"  Description: {fiche[4][:100] if fiche[4] else 'VIDE'}...")
    print(f"  Recommandations: {fiche[5] if fiche[5] else 'VIDE'}")
    print()
    print("=" * 80)
    print("ALIGNEMENT")
    print("=" * 80)
    print(f"  Score: {fiche[6]}")
    print(f"  Description: {fiche[7][:100] if fiche[7] else 'VIDE'}...")
    print(f"  Recommandations: {fiche[8] if fiche[8] else 'VIDE'}")

    con.close()

except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
