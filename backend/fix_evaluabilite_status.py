#!/usr/bin/env python3
"""
Script pour corriger le statut des projets qui sont 'en évaluation'
mais dont l'évaluabilité n'a pas encore été confirmée.
Ces projets doivent revenir au statut 'assigné'.
"""

import sqlite3
import os

DATA_DIR = os.environ.get("DATA_DIR", os.path.abspath(os.path.dirname(__file__)))
DB_PATH = os.path.join(DATA_DIR, "maturation.db")


def fix_evaluabilite_status():
    if not os.path.exists(DB_PATH):
        print(f"❌ Base de données non trouvée: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Trouver les projets "en évaluation" sans évaluabilité confirmée
    cursor.execute("""
        SELECT id, numero_projet, titre, statut, evaluabilite
        FROM project
        WHERE statut = 'en évaluation'
          AND (evaluabilite IS NULL OR evaluabilite != 'evaluable')
    """)
    projects = cursor.fetchall()

    if not projects:
        print("✅ Aucun projet à corriger")
        conn.close()
        return

    print(f"🔍 {len(projects)} projet(s) à corriger:\n")

    for p in projects:
        print(f"  - ID={p[0]} | {p[1]} | {p[2][:50]}")
        print(f"    Statut: '{p[3]}' → 'assigné' (évaluabilité non confirmée)")

    # Corriger le statut
    cursor.execute("""
        UPDATE project
        SET statut = 'assigné'
        WHERE statut = 'en évaluation'
          AND (evaluabilite IS NULL OR evaluabilite != 'evaluable')
    """)

    conn.commit()
    print(f"\n✅ {cursor.rowcount} projet(s) corrigé(s) → statut remis à 'assigné'")

    conn.close()


if __name__ == "__main__":
    try:
        fix_evaluabilite_status()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
