#!/usr/bin/env python3
"""
Script pour ajouter la colonne fiche_evaluation_visible à la table project
"""

import os
import sqlite3

DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(__file__))
DB_PATH = os.path.join(DATA_DIR, 'maturation.db')

def add_fiche_visible_column():
    """
    Ajoute la colonne fiche_evaluation_visible (BOOLEAN, default FALSE)

    La fiche d'évaluation devient visible pour le soumissionnaire dans ces cas:
    1. Quand le Comité entérine (decision_comite='enterine')
    2. Quand l'avis défavorable est validé par presidencecomite (decision_finale='confirme' ET avis='défavorable')
    3. PAS de fiche si rejet à l'évaluation préalable (evaluation_prealable='dossier_rejete')
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=== AJOUT COLONNE fiche_evaluation_visible ===\n")

    # Vérifier si la colonne existe déjà
    cursor.execute("PRAGMA table_info(project)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'fiche_evaluation_visible' in columns:
        print("✅ La colonne 'fiche_evaluation_visible' existe déjà")
    else:
        print("Ajout de la colonne 'fiche_evaluation_visible'...")
        cursor.execute("""
            ALTER TABLE project
            ADD COLUMN fiche_evaluation_visible BOOLEAN DEFAULT 0
        """)
        print("✅ Colonne 'fiche_evaluation_visible' ajoutée avec succès")

    conn.commit()
    conn.close()

    print("\n✅ Migration terminée!\n")

if __name__ == '__main__':
    try:
        add_fiche_visible_column()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
