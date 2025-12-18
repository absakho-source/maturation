#!/usr/bin/env python3
"""
Script pour régénérer tous les PDFs des fiches d'évaluation existantes.
Utile après une mise à jour du générateur PDF ou de la structure de la fiche.
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

def regenerer_tous_pdfs():
    """
    Régénère tous les PDFs des fiches d'évaluation existantes
    """

    if not os.path.exists(DB_PATH):
        print(f"❌ Base de données non trouvée: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
    cursor = conn.cursor()

    print("=" * 80)
    print("RÉGÉNÉRATION: PDFs de toutes les fiches d'évaluation")
    print("=" * 80)
    print()

    try:
        # 1. Vérifier que les tables existent
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fiche_evaluation'")
        if not cursor.fetchone():
            print("⚠️  Table fiche_evaluation non trouvée")
            return

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project'")
        if not cursor.fetchone():
            print("⚠️  Table project non trouvée")
            return

        print("✓ Tables trouvées")

        # 2. Récupérer toutes les fiches avec leurs projets
        print("\n1️⃣  Récupération des fiches d'évaluation...")
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
        """)

        fiches = cursor.fetchall()

        if not fiches:
            print("   ⚠️  Aucune fiche d'évaluation trouvée")
            return

        print(f"   ✓ {len(fiches)} fiche(s) trouvée(s)")

        # 3. Régénérer chaque PDF
        print("\n2️⃣  Régénération des PDFs...")
        regenerated_count = 0
        error_count = 0

        for fiche in fiches:
            try:
                project_id = fiche['project_id']
                fiche_id = fiche['id']
                numero_projet = fiche['projet_numero'] or f"PROJ-{project_id}"

                # Préparer les données de la fiche
                fiche_data = {
                    'id': fiche_id,
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

                    # Section II - Tableaux détaillés
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

                # Préparer les données du projet
                project_data = {
                    'id': project_id,
                    'numero_projet': numero_projet,
                    'titre': fiche['intitule_projet'] or fiche['projet_titre'] or '',
                    'organisme_tutelle': fiche['organisme_tutelle'] or fiche['projet_organisme'] or '',
                    'cout_estimatif': fiche['cout_projet'] or fiche['projet_cout'] or '',

                    # Section I
                    'secteur': fiche['sous_secteur'] or fiche['projet_secteur'] or '',
                    'poles': fiche['projet_poles'] or '',
                    'description': fiche['projet_description'] or '',

                    # Section II - Classification
                    'origine_projet': {
                        'maturation': fiche['origine_projet'] == 'maturation',
                        'offre_spontanee': fiche['origine_projet'] == 'offre_spontanee',
                        'autres': fiche['origine_projet'] == 'autres'
                    },
                    'cc_adaptation': fiche['changement_climatique_adaptation'] or False,
                    'cc_attenuation': fiche['changement_climatique_attenuation'] or False,
                    'genre': fiche['genre'] or False,

                    # Tableaux détaillés (reprise depuis fiche_data)
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

                # Générer le PDF
                pdf_filename = f"fiche_evaluation_{numero_projet}.pdf"
                pdf_path = generer_fiche_evaluation_dgppe_pdf(
                    fiche_data=fiche_data,
                    project_data=project_data,
                    filename=pdf_filename,
                    upload_folder=UPLOAD_FOLDER
                )

                # Mettre à jour le champ fichier_pdf dans la base
                cursor.execute("""
                    UPDATE fiche_evaluation
                    SET fichier_pdf = ?
                    WHERE id = ?
                """, (pdf_filename, fiche_id))

                regenerated_count += 1
                print(f"   ✓ Fiche {fiche_id} (Projet {numero_projet}): PDF régénéré")

            except Exception as e:
                error_count += 1
                print(f"   ❌ Fiche {fiche_id}: Erreur - {str(e)}")
                continue

        # 4. Commit des changements
        conn.commit()

        print()
        print("=" * 80)
        print("✅ RÉGÉNÉRATION TERMINÉE!")
        print("=" * 80)
        print()
        print(f"Résumé:")
        print(f"  • {regenerated_count} PDF(s) régénéré(s) avec succès")
        if error_count > 0:
            print(f"  • {error_count} erreur(s)")
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
    regenerer_tous_pdfs()
