"""
Utilitaires pour l'archivage des fiches d'évaluation
Archive uniquement les PDFs générés dans un dossier d'archives
"""

import os
import shutil
from datetime import datetime


def archiver_fiche(fiche, raison, archive_par):
    """
    Archive le PDF d'une fiche d'évaluation avant modification ou réassignation

    L'archivage consiste à :
    1. Vérifier qu'un PDF a été généré (fiche.fichier_pdf existe)
    2. Copier le PDF vers le dossier d'archives avec un nom horodaté
    3. Le PDF archivé contient déjà toutes les informations de la fiche

    Args:
        fiche: Instance FicheEvaluation à archiver
        raison: Raison de l'archivage (ex: "modification_secretariat", "reassignation_avant_hierarchie", etc.)
        archive_par: Nom d'utilisateur de la personne qui déclenche l'archivage

    Returns:
        str: Chemin du fichier PDF archivé, ou None en cas d'erreur
    """
    if not fiche:
        print("⚠️ Aucune fiche fournie pour archivage")
        return None

    # Vérifier qu'un PDF a été généré
    if not fiche.fichier_pdf:
        print(f"⚠️ Aucun PDF généré pour la fiche du projet {fiche.project_id} - archivage ignoré")
        return None

    try:
        # Utiliser DATA_DIR si défini (Render), sinon chemin local
        data_dir = os.environ.get('DATA_DIR', None)

        if data_dir:
            # Sur Render: PDFs dans /data/pdfs/fiches_evaluation/
            pdf_source_dir = os.path.join(data_dir, 'pdfs', 'fiches_evaluation')
            archives_dir = os.path.join(data_dir, 'archives', 'fiches_evaluation')
        else:
            # En local: PDFs dans backend/routes/pdfs/fiches_evaluation/
            routes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'routes')
            pdf_source_dir = os.path.join(routes_dir, 'pdfs', 'fiches_evaluation')
            backend_dir = os.path.dirname(os.path.dirname(__file__))
            archives_dir = os.path.join(backend_dir, 'archives', 'fiches_evaluation')

        pdf_source_path = os.path.join(pdf_source_dir, fiche.fichier_pdf)

        # Vérifier que le fichier source existe
        if not os.path.exists(pdf_source_path):
            # Sur Render, essayer l'ancien emplacement (backend/routes/pdfs/) pour rétro-compatibilité
            if data_dir:
                # Chercher dans l'ancien emplacement (où les PDFs étaient générés avant la correction)
                old_pdf_dir = os.path.join('/opt/render/project/src/backend/routes/pdfs', 'fiches_evaluation')
                old_pdf_path = os.path.join(old_pdf_dir, fiche.fichier_pdf)
                print(f"[ARCHIVAGE] PDF non trouvé dans {pdf_source_path}, essai emplacement ancien: {old_pdf_path}", flush=True)
                if os.path.exists(old_pdf_path):
                    pdf_source_path = old_pdf_path
                    print(f"[ARCHIVAGE] ✓ PDF trouvé dans l'ancien emplacement", flush=True)
                else:
                    print(f"❌ Fichier PDF source non trouvé ni dans {pdf_source_dir} ni dans {old_pdf_dir}")
                    return None
            else:
                print(f"❌ Fichier PDF source non trouvé: {pdf_source_path}")
                return None

        # Créer le dossier d'archives s'il n'existe pas
        os.makedirs(archives_dir, exist_ok=True)

        # Construire le nom du fichier archivé avec métadonnées
        # Format: PROJET-XXX_v1_20250128_153045_reassignation_jean.pdf
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Compter les versions existantes pour ce projet
        import glob
        # Récupérer le numéro de projet depuis la relation project
        numero_projet = fiche.project.numero_projet if fiche.project else None
        pattern = f"*{numero_projet or f'ID{fiche.project_id}'}*"
        existing_archives = glob.glob(os.path.join(archives_dir, pattern))
        version = len(existing_archives) + 1

        # Nom du fichier archivé
        projet_ref = numero_projet or f'ID{fiche.project_id}'
        evaluateur = fiche.evaluateur_nom or 'inconnu'
        nom_archive = f"{projet_ref}_v{version}_{timestamp}_{raison}_{archive_par}.pdf"

        # Chemin complet du fichier archivé
        archive_path = os.path.join(archives_dir, nom_archive)

        # Copier le PDF vers le dossier d'archives
        shutil.copy2(pdf_source_path, archive_path)

        # Vérifier que la copie a réussi
        if os.path.exists(archive_path):
            file_size = os.path.getsize(archive_path)
            print(f"✅ PDF archivé avec succès:")
            print(f"   - Projet: {projet_ref}")
            print(f"   - Version: {version}")
            print(f"   - Raison: {raison}")
            print(f"   - Par: {archive_par}")
            print(f"   - Évaluateur: {evaluateur}")
            print(f"   - Fichier: {nom_archive}")
            print(f"   - Taille: {file_size / 1024:.1f} Ko")

            # Enregistrer l'archive dans la base de données
            try:
                print(f"[ARCHIVAGE] Tentative d'enregistrement dans la BDD...")
                from models import db, DocumentProjet
                print(f"[ARCHIVAGE] Imports réussis (db, DocumentProjet)")

                description = f"Fiche d'évaluation archivée (v{version}) - {raison}"
                if evaluateur != 'inconnu':
                    description += f" - Évaluée par {evaluateur}"

                print(f"[ARCHIVAGE] Création de l'objet DocumentProjet...")
                doc_archive = DocumentProjet(
                    project_id=fiche.project_id,
                    nom_fichier=nom_archive,
                    nom_original=f"Fiche_Evaluation_{projet_ref}_v{version}.pdf",
                    description=description,
                    type_document='fiche_evaluation_archivee',
                    auteur_nom=archive_par,
                    auteur_role='admin',  # L'archivage est fait par le système
                    taille_fichier=file_size,
                    visible_pour_roles='["admin", "secretariatsct", "presidencesct", "presidencecomite", "evaluateur"]'
                )

                print(f"[ARCHIVAGE] Ajout à la session...")
                db.session.add(doc_archive)

                print(f"[ARCHIVAGE] Commit...")
                db.session.commit()

                print(f"✅ Archive enregistrée dans la base de données (ID: {doc_archive.id})")

            except Exception as db_error:
                print(f"❌ Erreur lors de l'enregistrement dans la BDD: {db_error}")
                import traceback
                traceback.print_exc()
                # Le fichier est copié mais pas enregistré en BDD
                # On ne considère pas cela comme un échec critique

            return archive_path
        else:
            print(f"❌ Échec de la copie du fichier vers {archive_path}")
            return None

    except Exception as e:
        print(f"❌ Erreur lors de l'archivage de la fiche PDF: {e}")
        import traceback
        traceback.print_exc()
        return None
