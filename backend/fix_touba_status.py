#!/usr/bin/env python3
"""
Script pour corriger le statut du projet Touba
Change 'rejeté par présidence SCT' vers 'en réexamen par le Secrétariat SCT'
"""

import sqlite3
import os

DATA_DIR = os.environ.get("DATA_DIR", os.path.abspath(os.path.dirname(__file__)))
DB_PATH = os.path.join(DATA_DIR, "maturation.db")

def fix_status():
    """Corrige les statuts des projets rejetés"""

    if not os.path.exists(DB_PATH):
        print(f"❌ Base de données non trouvée: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Trouver les projets avec anciens statuts
    old_statuts = ['rejeté', 'rejeté par présidence SCT', 'rejeté par presidencesct']
    placeholders = ','.join(['?' for _ in old_statuts])

    cursor.execute(f"SELECT id, numero_projet, titre, statut FROM projects WHERE statut IN ({placeholders})", old_statuts)
    projects = cursor.fetchall()

    if not projects:
        print("✅ Aucun projet avec ancien statut de rejet trouvé")
        conn.close()
        return

    print(f"🔍 {len(projects)} projet(s) à corriger:\n")

    for p in projects:
        print(f"  - ID={p[0]} | {p[1]} | {p[2][:40]}...")
        print(f"    Ancien: '{p[3]}' → Nouveau: 'en réexamen par le Secrétariat SCT'")

    # Corriger
    cursor.execute(f"""
        UPDATE projects
        SET statut = 'en réexamen par le Secrétariat SCT'
        WHERE statut IN ({placeholders})
    """, old_statuts)

    conn.commit()
    print(f"\n✅ {cursor.rowcount} projet(s) corrigé(s)")

    conn.close()

if __name__ == "__main__":
    fix_status()
