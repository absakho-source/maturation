#!/usr/bin/env python3
"""
Script pour régénérer le PDF d'une fiche d'évaluation spécifique.
Usage: python regenerer_pdf_projet.py <project_id>
"""

import sqlite3
import os
import sys

# Utiliser le même chemin que app.py (compatible Render et local)
DATA_DIR = os.environ.get("DATA_DIR", os.path.abspath(os.path.dirname(__file__)))
DB_PATH = os.path.join(DATA_DIR, "maturation.db")
UPLOAD_FOLDER = os.path.join(DATA_DIR, "uploads")

# Importer le générateur PDF
from pdf_generator_dgppe import generer_fiche_evaluation_dgppe_pdf

def regenerer_pdf_projet(project_id):
    """
    Régénère le PDF de la fiche d'évaluation d'un projet spécifique
    """

    if not os.path.exists(DB_PATH):
        print(f"❌ Base de données non trouvée: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=" * 80)
    print(f"RÉGÉNÉRATION PDF: Projet {project_id}")
    print("=" * 80)
    print()

    try:
        # 1. Récupérer la fiche
        print("1️⃣  Récupération de la fiche d'évaluation...")
        cursor.execute("""
            SELECT
                f.*,
                p.titre as projet_titre,
                p.secteur as projet_secteur,
                p.poles_territoriaux as projet_poles,
                p.cout_estimatif as projet_cout,
                p.organisme_tutelle as projet_organisme,
                p.description as projet_description,
                p.numero_projet as projet_numero
            FROM fiche_evaluation f
            JOIN project p ON f.project_id = p.id
            WHERE f.project_id = ?
        """, (project_id,))

        fiche = cursor.fetchone()

        if not fiche:
            print(f"   ❌ Aucune fiche d'évaluation trouvée pour le projet {project_id}")
            return

        print(f"   ✓ Fiche trouvée (ID: {fiche['id']}, Évaluateur: {fiche['evaluateur_nom']})")

        # 2. Préparer les données
        print("\n2️⃣  Préparation des données...")

        numero_projet = fiche['projet_numero'] or f"PROJ-{project_id}"

        fiche_data = {
            'id': fiche['id'],
            'evaluateur_nom': fiche['evaluateur_nom'] or '',
            'criteres': {
                'pertinence': {
                    'score': fiche['pertinence_score'] or 0,
                    'description': fiche['pertinence_description'] or '',
                    'recommandations': fiche['pertinence_recommandations'] or ''
                },
                'alignement': {
                    'score': fiche['alignement_score'] or 0,
                    'description': fiche['alignement_description'] or '',
                    'recommandations': fiche['alignement_recommandations'] or ''
                },
                'coherence': {
                    'score': fiche['coherence_score'] or 0,
                    'description': fiche['coherence_description'] or '',
                    'recommandations': fiche['coherence_recommandations'] or ''
                },
                'faisabilite': {
                    'score': fiche['faisabilite_score'] or 0,
                    'description': fiche['faisabilite_description'] or '',
                    'recommandations': fiche['faisabilite_recommandations'] or ''
                },
                'viabilite': {
                    'score': fiche['viabilite_score'] or 0,
                    'description': fiche['viabilite_description'] or '',
                    'recommandations': fiche['viabilite_recommandations'] or ''
                },
                'durabilite': {
                    'score': fiche['durabilite_score'] or 0,
                    'description': fiche['durabilite_description'] or '',
                    'recommandations': fiche['durabilite_recommandations'] or ''
                },
                'sensibilite_genre': {
                    'score': fiche['sensibilite_genre_score'] or 0,
                    'description': fiche['sensibilite_genre_description'] or '',
                    'recommandations': fiche['sensibilite_genre_recommandations'] or ''
                },
                'changement_climatique': {
                    'score': fiche['changement_climatique_score'] or 0,
                    'description': fiche['changement_climatique_description'] or '',
                    'recommandations': fiche['changement_climatique_recommandations'] or ''
                },
                'risques_hypotheses': {
                    'score': fiche['risques_hypotheses_score'] or 0,
                    'description': fiche['risques_hypotheses_description'] or '',
                    'recommandations': fiche['risques_hypotheses_recommandations'] or ''
                },
                'parties_prenantes': {
                    'score': fiche['parties_prenantes_score'] or 0,
                    'description': fiche['parties_prenantes_description'] or '',
                    'recommandations': fiche['parties_prenantes_recommandations'] or ''
                },
                'cadrage': {
                    'score': fiche['cadrage_score'] or 0,
                    'description': fiche['cadrage_description'] or '',
                    'recommandations': fiche['cadrage_recommandations'] or ''
                },
                'impact_environnemental': {
                    'score': fiche['impact_environnemental_score'] or 0,
                    'description': fiche['impact_environnemental_description'] or '',
                    'recommandations': fiche['impact_environnemental_recommandations'] or ''
                }
            },
            'proposition': fiche['proposition'] or '',
            'recommandations_generales': fiche['recommandations_generales'] or '',
            'articulation': fiche['articulation'] or '',
            'axes': fiche['axes'] or '',
            'objectifs_strategiques': fiche['objectifs_strategiques'] or '',
            'odd': fiche['odd'] or '',
            'duree_analyse': fiche['duree_analyse'] or '',
            'realisation': fiche['realisation'] or '',
            'exploitation': fiche['exploitation'] or '',
            'localisation': fiche['localisation'] or '',
            'parties_prenantes': fiche['parties_prenantes'] or '',
            'autres_projets_connexes': fiche['autres_projets_connexes'] or '',
            'objectif_projet': fiche['objectif_projet'] or '',
            'activites_principales': fiche['activites_principales'] or '',
            'resultats_attendus': fiche['resultats_attendus'] or ''
        }

        project_data = {
            'id': project_id,
            'numero_projet': numero_projet,
            'titre': fiche['intitule_projet'] or fiche['projet_titre'] or '',
            'organisme_tutelle': fiche['organisme_tutelle'] or fiche['projet_organisme'] or '',
            'cout_estimatif': fiche['cout_projet'] or fiche['projet_cout'] or '',
            'secteur': fiche['sous_secteur'] or fiche['projet_secteur'] or '',
            'poles': fiche['projet_poles'] or '',
            'description': fiche['projet_description'] or '',
            'origine_projet': {
                'maturation': fiche['origine_projet'] == 'maturation',
                'offre_spontanee': fiche['origine_projet'] == 'offre_spontanee',
                'autres': fiche['origine_projet'] == 'autres'
            },
            'cc_adaptation': fiche['changement_climatique_adaptation'] or False,
            'cc_attenuation': fiche['changement_climatique_attenuation'] or False,
            'genre': fiche['genre'] or False,
            'articulation': fiche['articulation'] or '',
            'axes': fiche['axes'] or '',
            'objectifs_strategiques': fiche['objectifs_strategiques'] or '',
            'odd': fiche['odd'] or '',
            'duree_analyse': fiche['duree_analyse'] or '',
            'realisation': fiche['realisation'] or '',
            'exploitation': fiche['exploitation'] or '',
            'localisation': fiche['localisation'] or '',
            'parties_prenantes': fiche['parties_prenantes'] or '',
            'autres_projets_connexes': fiche['autres_projets_connexes'] or '',
            'objectif_projet': fiche['objectif_projet'] or '',
            'activites_principales': fiche['activites_principales'] or '',
            'resultats_attendus': fiche['resultats_attendus'] or ''
        }

        print(f"   ✓ Données préparées")

        # 3. Générer le PDF
        print("\n3️⃣  Génération du PDF...")

        # Répertoire de sortie
        data_dir = os.environ.get('DATA_DIR', None)
        if data_dir:
            pdf_directory = os.path.join(data_dir, 'pdfs', 'fiches_evaluation')
        else:
            pdf_directory = os.path.join(os.path.dirname(__file__), 'routes', 'pdfs', 'fiches_evaluation')

        os.makedirs(pdf_directory, exist_ok=True)

        pdf_filename = f"fiche_evaluation_{numero_projet}.pdf"
        pdf_path = generer_fiche_evaluation_dgppe_pdf(
            fiche_data=fiche_data,
            project_data=project_data,
            filename=pdf_filename,
            upload_folder=pdf_directory
        )

        print(f"   ✓ PDF généré: {pdf_path}")

        # 4. Mettre à jour la base de données
        print("\n4️⃣  Mise à jour de la base de données...")
        cursor.execute("""
            UPDATE fiche_evaluation
            SET fichier_pdf = ?
            WHERE id = ?
        """, (pdf_filename, fiche['id']))

        conn.commit()
        print(f"   ✓ Base de données mise à jour")

        print()
        print("=" * 80)
        print("✅ RÉGÉNÉRATION TERMINÉE!")
        print("=" * 80)
        print()
        print(f"PDF: {pdf_filename}")
        print(f"Emplacement: {pdf_directory}")
        print()

    except Exception as e:
        conn.rollback()
        print()
        print("=" * 80)
        print("❌ ERREUR LORS DE LA RÉGÉNÉRATION")
        print("=" * 80)
        print(f"\n{e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        project_id = int(sys.argv[1])
    else:
        project_id = 7  # Par défaut, projet "Plateforme industrielle de Touba Typ"

    regenerer_pdf_projet(project_id)
