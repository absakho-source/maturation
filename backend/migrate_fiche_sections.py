#!/usr/bin/env python3
"""
Script de migration pour remplir les champs Section I & II des fiches d'évaluation existantes
avec les données des projets correspondants, puis régénérer les PDFs complets.
"""

import sqlite3
import os
import sys

# Utiliser le même chemin que app.py (compatible Render et local)
DATA_DIR = os.environ.get("DATA_DIR", os.path.abspath(os.path.dirname(__file__)))
DB_PATH = os.path.join(DATA_DIR, "maturation.db")

def migrate_fiche_sections():
    """
    Migre les données des projets vers les fiches d'évaluation existantes
    pour remplir les champs Section I & II qui étaient vides
    """

    if not os.path.exists(DB_PATH):
        print(f"❌ Base de données non trouvée: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 80)
    print("MIGRATION: Remplissage Sections I & II des fiches existantes")
    print("=" * 80)
    print()

    try:
        # 1. Vérifier que les tables existent
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fiche_evaluation'")
        if not cursor.fetchone():
            print("⚠️  Table fiche_evaluation non trouvée - migration non nécessaire")
            return

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project'")
        if not cursor.fetchone():
            print("⚠️  Table project non trouvée - migration impossible")
            return

        print("✓ Tables trouvées")

        # 2. Récupérer toutes les fiches d'évaluation
        print("\n1️⃣  Récupération des fiches d'évaluation...")
        cursor.execute("SELECT id, project_id FROM fiche_evaluation")
        fiches = cursor.fetchall()

        if not fiches:
            print("   ⚠️  Aucune fiche d'évaluation trouvée")
            return

        print(f"   ✓ {len(fiches)} fiche(s) trouvée(s)")

        # 3. Pour chaque fiche, copier les données du projet
        print("\n2️⃣  Migration des données projet → fiche...")
        updated_count = 0

        for fiche_id, project_id in fiches:
            # Récupérer les données du projet
            cursor.execute("""
                SELECT titre, secteur, poles_territoriaux, cout_estimatif, organisme_tutelle, description
                FROM project WHERE id = ?
            """, (project_id,))

            project = cursor.fetchone()

            if not project:
                print(f"   ⚠️  Projet {project_id} non trouvé pour fiche {fiche_id}")
                continue

            titre, secteur, poles, cout, organisme, description = project

            # Mettre à jour la fiche avec les données du projet
            cursor.execute("""
                UPDATE fiche_evaluation
                SET
                    intitule_projet = ?,
                    sous_secteur = ?,
                    cout_projet = ?,
                    organisme_tutelle = COALESCE(organisme_tutelle, ?)
                WHERE id = ?
            """, (
                titre or '',
                secteur or '',
                str(cout) if cout else '',
                organisme or "MINISTÈRE DE L'ÉCONOMIE, DU PLAN ET DE LA COOPÉRATION",
                fiche_id
            ))

            updated_count += 1
            print(f"   ✓ Fiche {fiche_id} (Projet {project_id}): {titre[:50]}...")

        # 4. Commit des changements
        conn.commit()

        print()
        print("=" * 80)
        print("✅ MIGRATION RÉUSSIE!")
        print("=" * 80)
        print()
        print(f"Résumé:")
        print(f"  • {updated_count} fiche(s) mise(s) à jour")
        print()
        print("Champs migrés:")
        print("  • intitule_projet ← project.titre")
        print("  • sous_secteur ← project.secteur")
        print("  • cout_projet ← project.cout_estimatif")
        print("  • organisme_tutelle ← project.organisme_tutelle (si vide)")
        print()
        print("⚠️  IMPORTANT: Les PDFs doivent être régénérés")
        print("Pour régénérer les PDFs, éditez chaque fiche et sauvegardez-la,")
        print("ou utilisez le script de régénération des PDFs.")
        print()

    except Exception as e:
        conn.rollback()
        print()
        print("=" * 80)
        print("❌ ERREUR LORS DE LA MIGRATION")
        print("=" * 80)
        print(f"\n{e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        conn.close()

if __name__ == "__main__":
    migrate_fiche_sections()
