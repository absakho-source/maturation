#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier l'état d'une fiche d'évaluation
"""

import sqlite3
import os
import sys

# Utiliser le même chemin que app.py (compatible Render et local)
DATA_DIR = os.environ.get("DATA_DIR", os.path.abspath(os.path.dirname(__file__)))
DB_PATH = os.path.join(DATA_DIR, "maturation.db")

def check_fiche(project_id):
    """Vérifier l'état de la fiche d'évaluation pour un projet"""

    if not os.path.exists(DB_PATH):
        print(f"❌ Base de données non trouvée: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=" * 80)
    print(f"DIAGNOSTIC: Fiche d'évaluation du projet {project_id}")
    print("=" * 80)
    print()

    try:
        # 1. Vérifier le projet
        cursor.execute("SELECT id, numero_projet, titre FROM project WHERE id = ?", (project_id,))
        project = cursor.fetchone()

        if not project:
            print(f"❌ Projet {project_id} non trouvé")
            return

        print(f"✅ Projet trouvé:")
        print(f"   ID: {project['id']}")
        print(f"   Numéro: {project['numero_projet']}")
        print(f"   Titre: {project['titre']}")
        print()

        # 2. Vérifier la fiche d'évaluation
        cursor.execute("""
            SELECT id, evaluateur_nom, fichier_pdf, score_total, proposition,
                   date_evaluation
            FROM fiche_evaluation
            WHERE project_id = ?
        """, (project_id,))

        fiche = cursor.fetchone()

        if not fiche:
            print(f"❌ Aucune fiche d'évaluation trouvée pour ce projet")
            return

        print(f"✅ Fiche d'évaluation trouvée:")
        print(f"   ID: {fiche['id']}")
        print(f"   Évaluateur: {fiche['evaluateur_nom']}")
        print(f"   Score total: {fiche['score_total']}")
        print(f"   Proposition: {fiche['proposition']}")
        print(f"   Date: {fiche['date_evaluation']}")
        print(f"   Fichier PDF: {fiche['fichier_pdf']}")
        print()

        # 3. Vérifier l'existence du fichier PDF
        if fiche['fichier_pdf']:
            # Essayer différents emplacements
            pdf_locations = []

            # Emplacement Render (/data/pdfs/fiches_evaluation/)
            if os.environ.get('DATA_DIR'):
                pdf_locations.append(os.path.join(DATA_DIR, 'pdfs', 'fiches_evaluation', fiche['fichier_pdf']))

            # Emplacement local (backend/routes/pdfs/fiches_evaluation/)
            pdf_locations.append(os.path.join(os.path.dirname(__file__), 'routes', 'pdfs', 'fiches_evaluation', fiche['fichier_pdf']))

            # Ancien emplacement Render (backend/routes/pdfs/)
            pdf_locations.append(os.path.join('/opt/render/project/src/backend/routes/pdfs', 'fiches_evaluation', fiche['fichier_pdf']))

            found = False
            for location in pdf_locations:
                if os.path.exists(location):
                    size = os.path.getsize(location)
                    print(f"✅ PDF trouvé: {location}")
                    print(f"   Taille: {size / 1024:.1f} Ko")
                    found = True
                    break
                else:
                    print(f"❌ PDF non trouvé: {location}")

            if not found:
                print()
                print(f"⚠️  Le PDF '{fiche['fichier_pdf']}' est référencé en base mais n'existe pas sur le disque")
        else:
            print("⚠️  Aucun fichier PDF associé à cette fiche")

        print()

        # 4. Vérifier les documents archivés
        cursor.execute("""
            SELECT nom_fichier, type_document, description, taille_fichier
            FROM documents_projet
            WHERE project_id = ? AND type_document LIKE '%fiche%'
            ORDER BY date_ajout DESC
        """, (project_id,))

        docs = cursor.fetchall()
        if docs:
            print(f"📚 Documents liés à la fiche ({len(docs)}):")
            for doc in docs:
                print(f"   - {doc['nom_fichier']} ({doc['type_document']}) - {doc['taille_fichier']/1024:.1f} Ko")
                print(f"     {doc['description']}")
        else:
            print("ℹ️  Aucun document archivé lié à la fiche")

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        project_id = int(sys.argv[1])
    else:
        project_id = 7  # Par défaut, projet "Plateforme industrielle de Touba Typ"

    check_fiche(project_id)
