"""
Routes pour les fiches d'évaluation conformes au format réel DGPPE
"""

from flask import Blueprint, request, jsonify, send_file
import os
import sys
import json
from datetime import datetime
from models import db, Project, FicheEvaluation, FicheEvaluationArchive, DocumentProjet
from utils.archivage import archiver_fiche

# Import pdf_generator DGPPE depuis le dossier parent
try:
    from pdf_generator_dgppe import generer_fiche_evaluation_dgppe_pdf
except ImportError:
    # Si l'import échoue, essayer avec le chemin absolu
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    from pdf_generator_dgppe import generer_fiche_evaluation_dgppe_pdf

evaluation_bp = Blueprint('evaluation', __name__)

@evaluation_bp.route('/api/projects/<int:project_id>/presentation', methods=['GET'])
def get_project_presentation(project_id):
    """Récupération des données de présentation du projet (Section I)"""
    try:
        project = Project.query.get_or_404(project_id)

        # Récupérer la fiche d'évaluation si elle existe pour récupérer les champs de présentation détaillée
        fiche = FicheEvaluation.query.filter_by(project_id=project_id).first()

        # Données automatiquement pré-remplies de la section I - PRESENTATION DU PROJET
        presentation_data = {
            'intitule': project.titre,
            'cout_projet': project.cout_estimatif,
            'cout_estimatif': project.cout_estimatif,  # Ajout pour compatibilité
            'origine_projet': {
                'maturation': False,
                'offre_spontanee': False,
                'autres': False
            },
            'typologie_projet': {
                'productif': False,
                'appui_production': False,
                'social': False,
                'environnemental': False
            },
            'changement_climatique': {
                'adaptation': False,
                'attenuation': False,
                'genre': project.secteur and 'famille' in project.secteur.lower()
            },
            'sous_secteur': project.secteur or '',
            'secteur': project.secteur or '',  # Ajout pour compatibilité
            'secteur_planification': project.secteur or '',
            'organisme_tutelle': project.organisme_tutelle or '',
            'poles': project.poles or '',  # Ajout explicite des pôles
            'description': project.description or '',  # Ajout de la description
            # Dimensions transversales
            'changement_climatique_adaptation': fiche.changement_climatique_adaptation if fiche else False,
            'changement_climatique_attenuation': fiche.changement_climatique_attenuation if fiche else False,
            'genre': fiche.genre if fiche else False,

            # Tableau 1: ARTICULATION / AXES / OBJECTIFS STRATÉGIQUES / ODD
            'articulation': fiche.articulation if fiche else '',
            'axes': fiche.axes if fiche else '',
            'objectifs_strategiques': fiche.objectifs_strategiques if fiche else '',
            'odd': fiche.odd if fiche else '',

            # Tableau 2: DURÉES
            'duree_analyse': fiche.duree_analyse if fiche else '',
            'realisation': fiche.realisation if fiche else '',
            'exploitation': fiche.exploitation if fiche else '',

            # Tableau 3: LOCALISATION / PARTIES PRENANTES / AUTRES PROJETS CONNEXES
            'localisation': fiche.localisation if fiche else '',
            'parties_prenantes': fiche.parties_prenantes if fiche else '',
            'autres_projets_connexes': fiche.autres_projets_connexes if fiche else '',

            # Tableau 4: OBJECTIF / ACTIVITÉS / RÉSULTATS
            'objectif_projet': fiche.objectif_projet if fiche else '',
            'activites_principales': fiche.activites_principales if fiche else '',
            'resultats_attendus': fiche.resultats_attendus if fiche else '',
            'evaluateur_nom': getattr(project, 'evaluateur_nom', '')
        }
        return jsonify(presentation_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération: {str(e)}'}), 500

@evaluation_bp.route('/api/projects/<int:project_id>/fiche-evaluation', methods=['GET'])
def get_fiche_evaluation(project_id):
    """Récupération de la fiche d'évaluation d'un projet"""
    try:
        # Vérifier que le projet existe
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Projet non trouvé'}), 404

        # Vérifier si l'utilisateur est un soumissionnaire et si la fiche est visible
        user_role = request.headers.get('X-Role', request.args.get('role', ''))
        if user_role == 'soumissionnaire':
            # Vérifier si la fiche est visible pour le soumissionnaire
            fiche_visible = getattr(project, 'fiche_evaluation_visible', False)
            if not fiche_visible:
                return jsonify({'error': 'La fiche d\'évaluation n\'est pas encore disponible'}), 403

        fiche = FicheEvaluation.query.filter_by(project_id=project_id).first()

        if not fiche:
            # Chercher une fiche archivée dans les documents du projet
            fiche_archivee = DocumentProjet.query.filter_by(
                project_id=project_id,
                type_document='fiche_evaluation_archivee'
            ).order_by(DocumentProjet.date_ajout.desc()).first()

            if fiche_archivee:
                # Retourner les infos de la fiche archivée (PDF uniquement)
                return jsonify({
                    'archived': True,
                    'document_id': fiche_archivee.id,
                    'nom_fichier': fiche_archivee.nom_fichier,
                    'description': fiche_archivee.description,
                    'date_archivage': fiche_archivee.date_ajout.isoformat(),
                    'evaluateur_nom': fiche_archivee.description.split('(')[0].replace('Fiche d\'évaluation archivée lors de la réassignation', '').strip() if fiche_archivee.description else 'Inconnu'
                }), 200

            # Si aucune fiche, retourner une structure par défaut avec l'évaluateur affecté au projet
            project = Project.query.get_or_404(project_id)
            evaluateur_nom = project.evaluateur_nom or ''
            return jsonify({
                'id': None,
                'project_id': project_id,
                'evaluateur_nom': evaluateur_nom,
                'date_evaluation': None,
                'reference_fiche': None,
                'criteres': {
                    'pertinence': {'score': 0, 'max_score': 5, 'description': ''},
                    'alignement': {'score': 0, 'max_score': 10, 'description': ''},
                    'activites_couts': {'score': 0, 'max_score': 15, 'description': ''},
                    'equite': {'score': 0, 'max_score': 15, 'description': ''},
                    'viabilite': {'score': 0, 'max_score': 5, 'description': ''},
                    'rentabilite': {'score': 0, 'max_score': 5, 'description': ''},
                    'benefices_strategiques': {'score': 0, 'max_score': 10, 'description': ''},
                    'perennite': {'score': 0, 'max_score': 5, 'description': ''},
                    'avantages_intangibles': {'score': 0, 'max_score': 10, 'description': ''},
                    'faisabilite': {'score': 0, 'max_score': 5, 'description': ''},
                    'ppp': {'score': 0, 'max_score': 5, 'description': ''},
                    'impact_environnemental': {'score': 0, 'max_score': 5, 'description': ''}
                },
                'impact_emploi_description': '',
                'score_total': 0,
                'proposition': '',
                'recommandations': '',
                'fichier_pdf': None
            }), 200

        # Utiliser to_dict() pour garantir la cohérence avec tous les champs (notamment recommandations)
        fiche_data = fiche.to_dict()

        return jsonify(fiche_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération: {str(e)}'}), 500

@evaluation_bp.route('/api/projects/<int:project_id>/fiche-evaluation', methods=['POST', 'PUT', 'OPTIONS'])
def create_or_update_fiche_evaluation(project_id):
    """Création ou mise à jour d'une fiche d'évaluation avec le nouveau format"""
    # Handler pour les requêtes preflight CORS
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        data = request.get_json()

        # Vérifier que le projet existe
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Projet non trouvé'}), 404

        # Récupérer ou créer la fiche d'évaluation
        fiche = FicheEvaluation.query.filter_by(project_id=project_id).first()

        is_update = fiche is not None

        # ARCHIVAGE AUTOMATIQUE lors de modification par SecretariatSCT
        if is_update and fiche:
            # Détermine qui modifie (username depuis le header ou depuis les données)
            modificateur = request.headers.get('X-Username', data.get('evaluateur_nom', 'secretariatsct'))

            # Si c'est une modification (pas une création initiale), archiver l'ancienne version
            # On archive uniquement si le projet a déjà été évalué
            if fiche.fichier_pdf:
                try:
                    # Compter les versions existantes
                    versions_existantes = FicheEvaluationArchive.query.filter_by(project_id=project_id).count()

                    # Créer l'archive
                    archive = FicheEvaluationArchive(
                        fiche_id_originale=fiche.id,
                        project_id=fiche.project_id,
                        raison_archivage='modification_secretariat',
                        archive_par=modificateur,
                        version=versions_existantes + 1,
                        evaluateur_nom=fiche.evaluateur_nom,
                        date_evaluation_originale=fiche.date_evaluation,
                        reference_fiche=fiche.reference_fiche,
                        pertinence_score=fiche.pertinence_score,
                        pertinence_description=fiche.pertinence_description,
                        alignement_score=fiche.alignement_score,
                        alignement_description=fiche.alignement_description,
                        activites_couts_score=fiche.activites_couts_score,
                        activites_couts_description=fiche.activites_couts_description,
                        equite_score=fiche.equite_score,
                        equite_description=fiche.equite_description,
                        viabilite_score=fiche.viabilite_score,
                        viabilite_description=fiche.viabilite_description,
                        rentabilite_score=fiche.rentabilite_score,
                        rentabilite_description=fiche.rentabilite_description,
                        benefices_strategiques_score=fiche.benefices_strategiques_score,
                        benefices_strategiques_description=fiche.benefices_strategiques_description,
                        perennite_score=fiche.perennite_score,
                        perennite_description=fiche.perennite_description,
                        avantages_intangibles_score=fiche.avantages_intangibles_score,
                        avantages_intangibles_description=fiche.avantages_intangibles_description,
                        faisabilite_score=fiche.faisabilite_score,
                        faisabilite_description=fiche.faisabilite_description,
                        ppp_score=fiche.ppp_score,
                        ppp_description=fiche.ppp_description,
                        impact_environnemental_score=fiche.impact_environnemental_score,
                        impact_environnemental_description=fiche.impact_environnemental_description,
                        score_total=fiche.score_total,
                        proposition=fiche.proposition,
                        recommandations=fiche.recommandations
                    )
                    db.session.add(archive)
                    db.session.flush()
                    print(f"✅ PDF archivé avec succès avant modification")
                except Exception as e:
                    print(f"⚠️ Erreur archivage fiche: {e}")
                    # Continue quand même pour ne pas bloquer la modification

        if not fiche:
            # Générer une référence automatique si absente
            ref = data.get('reference_fiche')
            if not ref:
                date_str = datetime.now().strftime('%Y%m%d')
                ref = f"EVAL-{project.numero_projet or project.id}-{date_str}"
            fiche = FicheEvaluation(
                project_id=project_id,
                evaluateur_nom=data.get('evaluateur_nom', 'evaluateur'),
                reference_fiche=ref
            )
            db.session.add(fiche)
        else:
            # Pour une mise à jour, mettre à jour l'évaluateur si fourni
            if data.get('evaluateur_nom'):
                fiche.evaluateur_nom = data.get('evaluateur_nom')
        
        # Mise à jour des critères d'évaluation selon le nouveau format
        criteres = data.get('criteres', {})
        
        # PERTINENCE (/10)
        if 'pertinence' in criteres:
            fiche.pertinence_score = min(criteres['pertinence'].get('score', 0), 10)
            fiche.pertinence_description = criteres['pertinence'].get('description', '')
            fiche.pertinence_recommandations = criteres['pertinence'].get('recommandations', '')
        
        # ALIGNEMENT (/10)
        if 'alignement' in criteres:
            fiche.alignement_score = min(criteres['alignement'].get('score', 0), 10)
            fiche.alignement_description = criteres['alignement'].get('description', '')
            fiche.alignement_recommandations = criteres['alignement'].get('recommandations', '')

        # ACTIVITES ET COUTS (/15)
        if 'activites_couts' in criteres:
            fiche.activites_couts_score = min(criteres['activites_couts'].get('score', 0), 15)
            fiche.activites_couts_description = criteres['activites_couts'].get('description', '')
            fiche.activites_couts_recommandations = criteres['activites_couts'].get('recommandations', '')

        # EQUITE (/15)
        if 'equite' in criteres:
            fiche.equite_score = min(criteres['equite'].get('score', 0), 15)
            fiche.equite_description = criteres['equite'].get('description', '')
            fiche.equite_recommandations = criteres['equite'].get('recommandations', '')

        # VIABILITE (/5)
        if 'viabilite' in criteres:
            fiche.viabilite_score = min(criteres['viabilite'].get('score', 0), 5)
            fiche.viabilite_description = criteres['viabilite'].get('description', '')
            fiche.viabilite_recommandations = criteres['viabilite'].get('recommandations', '')

        # RENTABILITE (/5)
        if 'rentabilite' in criteres:
            fiche.rentabilite_score = min(criteres['rentabilite'].get('score', 0), 5)
            fiche.rentabilite_description = criteres['rentabilite'].get('description', '')
            fiche.rentabilite_recommandations = criteres['rentabilite'].get('recommandations', '')

        # BENEFICES STRATEGIQUES (/10)
        if 'benefices_strategiques' in criteres:
            fiche.benefices_strategiques_score = min(criteres['benefices_strategiques'].get('score', 0), 10)
            fiche.benefices_strategiques_description = criteres['benefices_strategiques'].get('description', '')
            fiche.benefices_strategiques_recommandations = criteres['benefices_strategiques'].get('recommandations', '')

        # PERENNITE (/5)
        if 'perennite' in criteres:
            fiche.perennite_score = min(criteres['perennite'].get('score', 0), 5)
            fiche.perennite_description = criteres['perennite'].get('description', '')
            fiche.perennite_recommandations = criteres['perennite'].get('recommandations', '')

        # AVANTAGES INTANGIBLES (/10)
        if 'avantages_intangibles' in criteres:
            fiche.avantages_intangibles_score = min(criteres['avantages_intangibles'].get('score', 0), 10)
            fiche.avantages_intangibles_description = criteres['avantages_intangibles'].get('description', '')
            fiche.avantages_intangibles_recommandations = criteres['avantages_intangibles'].get('recommandations', '')

        # FAISABILITE (/5)
        if 'faisabilite' in criteres:
            fiche.faisabilite_score = min(criteres['faisabilite'].get('score', 0), 5)
            fiche.faisabilite_description = criteres['faisabilite'].get('description', '')
            fiche.faisabilite_recommandations = criteres['faisabilite'].get('recommandations', '')
        
        # PPP (/5)
        if 'ppp' in criteres:
            fiche.ppp_score = min(criteres['ppp'].get('score', 0), 5)
            fiche.ppp_description = criteres['ppp'].get('description', '')
            fiche.ppp_recommandations = criteres['ppp'].get('recommandations', '')

        # IMPACT ENVIRONNEMENTAL (/5)
        if 'impact_environnemental' in criteres:
            fiche.impact_environnemental_score = min(criteres['impact_environnemental'].get('score', 0), 5)
            fiche.impact_environnemental_description = criteres['impact_environnemental'].get('description', '')
            fiche.impact_environnemental_recommandations = criteres['impact_environnemental'].get('recommandations', '')
        
        # IMPACT SUR L'EMPLOI (/5)
        if 'impact_emploi' in criteres:
            fiche.impact_emploi_score = min(criteres['impact_emploi'].get('score', 0), 5)
            fiche.impact_emploi_description = criteres['impact_emploi'].get('description', '')
            fiche.impact_emploi_recommandations = criteres['impact_emploi'].get('recommandations', '')
        
        # Conclusion
        fiche.proposition = data.get('proposition', '')
        fiche.recommandations = data.get('recommandations', '')

        # Sauvegarder origine_projet et typologie_projet depuis le frontend
        import json

        # Convertir origine_projet_choix en format objet
        origine_choix = data.get('origine_projet_choix', '')
        if origine_choix:
            origine_obj = {
                'maturation': origine_choix == 'maturation',
                'offre_spontanee': origine_choix == 'offre_spontanee',
                'autres': origine_choix == 'autres'
            }
            project.origine_projet = json.dumps(origine_obj)

        # Convertir typologie_projet_choix en format objet
        typologie_choix = data.get('typologie_projet_choix', '')
        if typologie_choix:
            typologie_obj = {
                'productif': typologie_choix == 'productif',
                'appui_production': typologie_choix == 'appui_production',
                'social': typologie_choix == 'social',
                'environnemental': typologie_choix == 'environnemental'
            }
            project.typologie_projet = json.dumps(typologie_obj)

        # Sauvegarder les dimensions transversales
        fiche.changement_climatique_adaptation = data.get('changement_climatique_adaptation', False)
        fiche.changement_climatique_attenuation = data.get('changement_climatique_attenuation', False)
        fiche.genre = data.get('genre', False)

        # Sauvegarder les champs de présentation détaillée (Section I - 4 tableaux)
        # Tableau 1: ARTICULATION / AXES / OBJECTIFS STRATÉGIQUES / ODD
        fiche.articulation = data.get('articulation', '')
        fiche.axes = data.get('axes', '')
        fiche.objectifs_strategiques = data.get('objectifs_strategiques', '')
        fiche.odd = data.get('odd', '')

        # Tableau 2: DURÉES
        fiche.duree_analyse = data.get('duree_analyse', '')
        fiche.realisation = data.get('realisation', '')
        fiche.exploitation = data.get('exploitation', '')

        # Tableau 3: LOCALISATION / PARTIES PRENANTES / AUTRES PROJETS
        fiche.localisation = data.get('localisation', '')
        fiche.parties_prenantes = data.get('parties_prenantes', '')
        fiche.autres_projets_connexes = data.get('autres_projets_connexes', '')

        # Tableau 4: OBJECTIF / ACTIVITÉS / RÉSULTATS
        fiche.objectif_projet = data.get('objectif_projet', '')
        fiche.activites_principales = data.get('activites_principales', '')
        fiche.resultats_attendus = data.get('resultats_attendus', '')

        # Calcul automatique du score total
        score_total = fiche.calculer_score_total()

        # Calcul automatique de l'avis depuis le score (barème : 80+: favorable, 70-79: sous conditions, <70: défavorable)
        avis_calcule = fiche.calculer_avis_depuis_score()

        # Mise à jour de la proposition dans la fiche ET de l'avis du projet
        fiche.proposition = avis_calcule
        project.statut = 'évalué'
        project.avis = avis_calcule
        
        db.session.commit()

        # Ajouter l'entrée dans l'historique
        from models import Historique, User
        if is_update:
            action_text = f"Fiche d'évaluation modifiée - Score: {score_total}/100 - Proposition: {fiche.proposition}"
        else:
            action_text = f"Fiche d'évaluation soumise - Score: {score_total}/100 - Proposition: {fiche.proposition}"

        # Déterminer le rôle de l'auteur de l'action
        auteur_username = data.get('evaluateur_nom', fiche.evaluateur_nom)
        auteur_user = User.query.filter_by(username=auteur_username).first()

        # Si c'est une mise à jour, utiliser le rôle de l'utilisateur qui modifie
        # Sinon, utiliser "evaluateur" pour la création initiale
        if is_update and auteur_user:
            auteur_role = auteur_user.role
        else:
            auteur_role = "evaluateur"

        hist = Historique(
            project_id=project_id,
            action=action_text,
            auteur=auteur_username,
            role=auteur_role
        )
        db.session.add(hist)
        db.session.commit()

        # Générer le PDF à chaque création ou mise à jour
        print(f"[PDF] Début de la génération du PDF pour le projet {project_id}", flush=True)
        try:
            from pdf_generator_dgppe import generer_fiche_evaluation_dgppe_pdf
            import os

            # Récupérer le display_name de l'évaluateur
            from models import User
            evaluateur_display_name = fiche.evaluateur_nom
            if fiche.evaluateur_nom:
                evaluateur = User.query.filter_by(username=fiche.evaluateur_nom).first()
                if evaluateur and evaluateur.display_name:
                    evaluateur_display_name = evaluateur.display_name

            # Préparer les données pour le PDF
            import json

            # Parser les champs JSON si nécessaire
            origine_projet = {}
            typologie_projet = {}
            try:
                if project.origine_projet:
                    origine_projet = json.loads(project.origine_projet) if isinstance(project.origine_projet, str) else project.origine_projet
            except:
                pass

            try:
                if project.typologie_projet:
                    typologie_projet = json.loads(project.typologie_projet) if isinstance(project.typologie_projet, str) else project.typologie_projet
            except:
                pass

            project_data = {
                'id': project.id,
                'numero_projet': project.numero_projet,
                'titre': project.titre,
                'poles': project.poles,
                'secteur': project.secteur,
                'cout_estimatif': project.cout_estimatif,
                'date_soumission': project.date_soumission.isoformat() if project.date_soumission else None,
                'origine_projet': origine_projet,
                'typologie_projet': typologie_projet
            }

            fiche_data = fiche.to_dict()
            fiche_data['evaluateur_nom'] = evaluateur_display_name

            # Répertoire de sortie pour les PDFs
            # Utiliser DATA_DIR si défini (Render), sinon chemin local
            data_dir = os.environ.get('DATA_DIR', None)
            if data_dir:
                # Sur Render: stocker dans /data/pdfs/fiches_evaluation/
                pdf_directory = os.path.join(data_dir, 'pdfs', 'fiches_evaluation')
            else:
                # En local: stocker dans backend/routes/pdfs/fiches_evaluation/
                pdf_directory = os.path.join(os.path.dirname(__file__), 'pdfs', 'fiches_evaluation')
            os.makedirs(pdf_directory, exist_ok=True)
            print(f"[PDF] Répertoire PDF: {pdf_directory}", flush=True)

            # Archiver l'ancien PDF s'il existe (lors d'une modification)
            print(f"[PDF] Vérification archivage: is_update={is_update}, fiche.fichier_pdf={fiche.fichier_pdf}", flush=True)
            if is_update and fiche.fichier_pdf:
                print(f"[PDF] Lancement de l'archivage...", flush=True)
                from utils.archivage import archiver_fiche
                # Le modificateur est l'utilisateur actuel qui édite la fiche
                modificateur = data.get('evaluateur_nom', 'admin')
                # L'éditeur actuel de cette version (avant la mise à jour) est fiche.evaluateur_nom
                editeur_actuel = fiche.evaluateur_nom
                archive_path = archiver_fiche(fiche, 'modification', modificateur, editeur_actuel)
                if archive_path:
                    print(f"[PDF] Ancien PDF archivé: {archive_path}", flush=True)
                else:
                    print(f"[PDF] Avertissement: archivage de l'ancien PDF échoué", flush=True)
            else:
                print(f"[PDF] Archivage ignoré (première génération ou pas de PDF existant)", flush=True)

            # Générer le nouveau PDF
            pdf_path = generer_fiche_evaluation_dgppe_pdf(fiche_data, project_data, pdf_directory)
            fiche.fichier_pdf = os.path.basename(pdf_path)
            db.session.commit()
            print(f"[PDF] Nouveau PDF généré et enregistré: {fiche.fichier_pdf}")
        except Exception as e:
            print(f"Erreur lors de la génération du PDF: {str(e)}")
            # Ne pas bloquer l'enregistrement si la génération PDF échoue

        return jsonify({
            'message': 'Fiche d\'évaluation enregistrée avec succès',
            'score_total': score_total,
            'appreciation': fiche.get_appreciation_globale(),
            'fiche_id': fiche.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de l\'enregistrement: {str(e)}'}), 500

@evaluation_bp.route('/api/projects/<int:project_id>/fiche-evaluation/pdf', methods=['GET', 'POST'])
def generate_fiche_evaluation_pdf(project_id):
    """Récupération ou génération du PDF de la fiche d'évaluation"""
    try:
        # Récupérer le projet et sa fiche d'évaluation
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Projet non trouvé'}), 404

        # Vérifier si l'utilisateur est un soumissionnaire et si la fiche est visible
        user_role = request.headers.get('X-Role', request.args.get('role', ''))
        if user_role == 'soumissionnaire':
            # Vérifier si la fiche est visible pour le soumissionnaire
            fiche_visible = getattr(project, 'fiche_evaluation_visible', False)
            if not fiche_visible:
                return jsonify({'error': 'La fiche d\'évaluation n\'est pas encore disponible'}), 403

        fiche = FicheEvaluation.query.filter_by(project_id=project_id).first()
        if not fiche:
            return jsonify({'error': 'Aucune fiche d\'évaluation trouvée'}), 404

        # Répertoire de sortie pour les PDFs
        pdf_directory = os.path.join(os.path.dirname(__file__), 'pdfs', 'fiches_evaluation')
        os.makedirs(pdf_directory, exist_ok=True)

        # Vérifier si le PDF existe déjà
        if fiche.fichier_pdf:
            pdf_path = os.path.join(pdf_directory, fiche.fichier_pdf)
            if os.path.exists(pdf_path):
                # Le PDF existe déjà, le servir directement
                print(f"[PDF] Servir PDF existant: {fiche.fichier_pdf}")
                return send_file(
                    pdf_path,
                    as_attachment=False,
                    download_name=f"{fiche.reference_fiche}.pdf",
                    mimetype='application/pdf'
                )

        # Le PDF n'existe pas, le générer
        print(f"[PDF] Génération du PDF pour le projet {project_id}")

        # Récupérer le display_name de l'évaluateur
        from models import User
        evaluateur_display_name = fiche.evaluateur_nom
        if fiche.evaluateur_nom:
            evaluateur = User.query.filter_by(username=fiche.evaluateur_nom).first()
            if evaluateur and evaluateur.display_name:
                evaluateur_display_name = evaluateur.display_name

        # Préparer les données pour le PDF
        import json

        # Parser les champs JSON si nécessaire
        origine_projet = {}
        typologie_projet = {}
        try:
            if project.origine_projet:
                origine_projet = json.loads(project.origine_projet) if isinstance(project.origine_projet, str) else project.origine_projet
        except:
            pass

        try:
            if project.typologie_projet:
                typologie_projet = json.loads(project.typologie_projet) if isinstance(project.typologie_projet, str) else project.typologie_projet
        except:
            pass

        project_data = {
            'id': project.id,
            'numero_projet': project.numero_projet,
            'titre': project.titre,
            'poles': project.poles,
            'secteur': project.secteur,
            'cout_estimatif': project.cout_estimatif,
            'date_soumission': project.date_soumission.isoformat() if project.date_soumission else None,
            'origine_projet': origine_projet,
            'typologie_projet': typologie_projet
        }

        fiche_data = fiche.to_dict()
        # Remplacer evaluateur_nom par le display_name
        fiche_data['evaluateur_nom'] = evaluateur_display_name

        # Générer le PDF avec le générateur DGPPE
        pdf_path = generer_fiche_evaluation_dgppe_pdf(fiche_data, project_data, pdf_directory)

        # Mettre à jour le chemin du fichier PDF dans la base
        fiche.fichier_pdf = os.path.basename(pdf_path)
        db.session.commit()

        print(f"[PDF] PDF généré: {fiche.fichier_pdf}")

        # Retourner le fichier PDF pour ouverture dans un nouvel onglet
        return send_file(
            pdf_path,
            as_attachment=False,
            download_name=f"{fiche.reference_fiche}.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erreur lors de la génération du PDF: {str(e)}'}), 500

@evaluation_bp.route('/api/projects/<int:project_id>/fiche-evaluation/pdf/<filename>', methods=['GET'])
def download_fiche_evaluation_pdf(project_id, filename):
    """Téléchargement d'un PDF de fiche d'évaluation existant"""
    try:
        # Vérifier que le projet existe
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Projet non trouvé'}), 404

        # Vérifier si l'utilisateur est un soumissionnaire et si la fiche est visible
        user_role = request.headers.get('X-Role', request.args.get('role', ''))
        if user_role == 'soumissionnaire':
            # Vérifier si la fiche est visible pour le soumissionnaire
            fiche_visible = getattr(project, 'fiche_evaluation_visible', False)
            if not fiche_visible:
                return jsonify({'error': 'La fiche d\'évaluation n\'est pas encore disponible'}), 403

        # Vérifier que la fiche existe
        fiche = FicheEvaluation.query.filter_by(
            project_id=project_id,
            fichier_pdf=filename
        ).first()

        if not fiche:
            return jsonify({'error': 'Fiche d\'évaluation non trouvée'}), 404
        
        # Chemin vers le fichier PDF
        pdf_directory = os.path.join(os.path.dirname(__file__), 'pdfs', 'fiches_evaluation')
        pdf_path = os.path.join(pdf_directory, filename)
        
        if not os.path.exists(pdf_path):
            return jsonify({'error': 'Fichier PDF non trouvé'}), 404
        
        return send_file(
            pdf_path,
            as_attachment=False,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du téléchargement: {str(e)}'}), 500

@evaluation_bp.route('/api/projects/<int:project_id>/fiche-evaluation-brouillon', methods=['POST'])
def save_fiche_evaluation_brouillon(project_id):
    """Sauvegarde d'un brouillon d'évaluation"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Projet non trouvé'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Données manquantes'}), 400
        
        # Vérifier si une fiche brouillon existe déjà
        fiche_brouillon = FicheEvaluation.query.filter_by(
            project_id=project_id, 
            statut='brouillon'
        ).first()
        
        if fiche_brouillon:
            # Mettre à jour le brouillon existant
            fiche_brouillon.evaluateur_nom = data.get('evaluateur_nom', '')
            fiche_brouillon.criteres_json = json.dumps(data.get('criteres', {}))
            fiche_brouillon.proposition = data.get('proposition', '')
            fiche_brouillon.recommandations = data.get('recommandations', '')
            fiche_brouillon.date_modification = datetime.now()
        else:
            # Créer un nouveau brouillon
            fiche_brouillon = FicheEvaluation(
                project_id=project_id,
                evaluateur_nom=data.get('evaluateur_nom', ''),
                criteres_json=json.dumps(data.get('criteres', {})),
                proposition=data.get('proposition', ''),
                recommandations=data.get('recommandations', ''),
                statut='brouillon',
                date_creation=datetime.now(),
                date_modification=datetime.now()
            )
            db.session.add(fiche_brouillon)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Brouillon sauvegardé avec succès',
            'fiche_id': fiche_brouillon.id,
            'statut': 'brouillon',
            'date_sauvegarde': fiche_brouillon.date_modification.isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la sauvegarde du brouillon: {str(e)}'}), 500

@evaluation_bp.route('/api/projects/<int:project_id>/fiche-evaluation', methods=['DELETE'])
def delete_fiche_evaluation(project_id):
    """Suppression d'une fiche d'évaluation active (avec archivage automatique) - Admin uniquement"""
    try:
        # Vérification stricte : admin uniquement
        role = request.headers.get('X-Role', '')
        if role != 'admin':
            return jsonify({
                'error': 'Accès refusé',
                'message': 'Seuls les administrateurs peuvent supprimer une fiche d\'évaluation'
            }), 403

        fiche = FicheEvaluation.query.filter_by(project_id=project_id).first()

        if not fiche:
            return jsonify({'error': 'Aucune fiche d\'évaluation trouvée'}), 404

        # Archiver avant suppression si la fiche a du contenu
        username = request.headers.get('X-Username', 'admin')
        if fiche.fichier_pdf:
            try:
                print(f"[INFO] Archivage de la fiche pour le projet {project_id} (suppression manuelle)")
                archive = archiver_fiche(fiche, "suppression_manuelle", username)
                if archive:
                    print(f"✅ PDF archivé avec succès avant suppression")
                else:
                    print(f"⚠️ Échec de l'archivage, suppression annulée")
                    return jsonify({'error': 'Échec de l\'archivage de la fiche'}), 500
            except Exception as e:
                print(f"❌ Erreur lors de l'archivage: {e}")
                return jsonify({'error': f'Erreur lors de l\'archivage: {str(e)}'}), 500

        # Supprimer le fichier PDF s'il existe
        if fiche.fichier_pdf:
            pdf_directory = os.path.join(os.path.dirname(__file__), 'pdfs', 'fiches_evaluation')
            pdf_path = os.path.join(pdf_directory, fiche.fichier_pdf)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

        # Supprimer la fiche de la base
        db.session.delete(fiche)
        db.session.commit()

        return jsonify({'message': 'Fiche d\'évaluation archivée et supprimée avec succès'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la suppression: {str(e)}'}), 500

@evaluation_bp.route('/api/fiches-evaluation', methods=['GET'])
def get_all_fiches_evaluation():
    """Récupération de toutes les fiches d'évaluation"""
    try:
        # Paramètres de filtrage
        evaluateur = request.args.get('evaluateur')
        statut = request.args.get('statut')
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        
        # Construction de la requête
        query = FicheEvaluation.query.join(Project)
        
        if evaluateur:
            query = query.filter(FicheEvaluation.evaluateur_nom == evaluateur)
        
        if date_debut:
            query = query.filter(FicheEvaluation.date_evaluation >= date_debut)
        
        if date_fin:
            query = query.filter(FicheEvaluation.date_evaluation <= date_fin)
        
        fiches = query.all()
        
        # Enrichir avec les informations du projet
        result = []
        for fiche in fiches:
            fiche_dict = fiche.to_dict()
            fiche_dict['project_title'] = fiche.project.titre
            fiche_dict['project_numero'] = fiche.project.numero_projet
            result.append(fiche_dict)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération: {str(e)}'}), 500

@evaluation_bp.route('/api/fiches-evaluation/stats', methods=['GET'])
def get_fiches_evaluation_stats():
    """Statistiques des fiches d'évaluation"""
    try:
        # Compter les fiches par appréciation
        stats_appreciation = db.session.query(
            FicheEvaluation.appreciation_globale,
            db.func.count(FicheEvaluation.id)
        ).group_by(FicheEvaluation.appreciation_globale).all()
        
        # Compter les fiches par avis final
        stats_avis = db.session.query(
            FicheEvaluation.avis_final,
            db.func.count(FicheEvaluation.id)
        ).group_by(FicheEvaluation.avis_final).all()
        
        # Score moyen
        score_moyen = db.session.query(
            db.func.avg(FicheEvaluation.score_total)
        ).scalar() or 0
        
        # Nombre total de fiches
        total_fiches = FicheEvaluation.query.count()
        
        # Fiches par évaluateur
        stats_evaluateur = db.session.query(
            FicheEvaluation.evaluateur_nom,
            db.func.count(FicheEvaluation.id)
        ).group_by(FicheEvaluation.evaluateur_nom).all()
        
        return jsonify({
            'total_fiches': total_fiches,
            'score_moyen': round(score_moyen, 1),
            'repartition_appreciation': dict(stats_appreciation),
            'repartition_avis': dict(stats_avis),
            'repartition_evaluateur': dict(stats_evaluateur)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du calcul des statistiques: {str(e)}'}), 500


@evaluation_bp.route('/api/projects/<int:project_id>/fiches-archives', methods=['GET'])
def get_fiches_archives(project_id):
    """
    Récupère l'historique des PDFs archivés pour un projet
    Accessible uniquement aux membres du Comité (admin, secretariatsct, presidencesct, presidencecomite)
    """
    try:
        # Vérifier les permissions (membres du comité uniquement)
        role = request.headers.get('X-Role', '')
        roles_autorises = ['admin', 'secretariatsct', 'presidencesct', 'presidencecomite']

        if role not in roles_autorises:
            return jsonify({
                'error': 'Accès refusé',
                'message': 'Seuls les membres du Comité peuvent consulter l\'historique des fiches'
            }), 403

        # Vérifier que le projet existe
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Projet non trouvé'}), 404

        # Récupérer les archives depuis la table DocumentProjet
        archives_docs = DocumentProjet.query.filter_by(
            project_id=project_id,
            type_document='fiche_evaluation_archivee'
        ).order_by(DocumentProjet.date_ajout.desc()).all()

        # Construire la liste des archives avec les métadonnées
        archives_list = []
        for doc in archives_docs:
            # Parser le nom du fichier pour extraire la version
            # Format: DGPPE-25-004_v1_20250204_164530_modification_secretariatsct.pdf
            filename = doc.nom_fichier
            version = 'N/A'
            raison = 'modification'

            try:
                parts = filename.replace('.pdf', '').split('_')
                if len(parts) >= 2 and parts[1].startswith('v'):
                    version = parts[1].replace('v', '')
                if len(parts) >= 5:
                    raison = parts[4]
            except:
                pass

            archives_list.append({
                'filename': filename,
                'version': version,
                'date_archivage': doc.date_ajout.isoformat() if doc.date_ajout else None,
                'raison_archivage': raison,
                'archive_par': doc.auteur_nom or 'Système',  # Utiliser auteur_nom qui contient le nom du dernier éditeur
                'taille': doc.taille_fichier or 0
            })

        # Récupérer la fiche actuelle
        fiche_actuelle = FicheEvaluation.query.filter_by(project_id=project_id).first()

        return jsonify({
            'project_id': project_id,
            'numero_projet': project.numero_projet,
            'titre_projet': project.titre,
            'total_versions': len(archives_list),
            'fiche_actuelle': fiche_actuelle.to_dict() if fiche_actuelle else None,
            'archives': archives_list
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erreur lors de la récupération des archives: {str(e)}'}), 500


@evaluation_bp.route('/api/projects/<int:project_id>/fiches-archives/<filename>', methods=['DELETE'])
def delete_fiche_archive(project_id, filename):
    """
    Supprime un PDF archivé
    Accessible uniquement aux administrateurs
    """
    try:
        # Vérification stricte : admin uniquement
        role = request.headers.get('X-Role', '')
        if role != 'admin':
            return jsonify({
                'error': 'Accès refusé',
                'message': 'Seuls les administrateurs peuvent supprimer les archives'
            }), 403

        # Vérifier que le projet existe
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Projet non trouvé'}), 404

        # Dossier des archives
        backend_dir = os.path.dirname(os.path.dirname(__file__))
        archives_dir = os.path.join(backend_dir, 'archives', 'fiches_evaluation')

        # Chemin complet du fichier à supprimer
        file_path = os.path.join(archives_dir, filename)

        # Vérifications de sécurité
        # 1. Le fichier doit être dans le dossier d'archives (pas de path traversal)
        if not os.path.abspath(file_path).startswith(os.path.abspath(archives_dir)):
            return jsonify({'error': 'Chemin de fichier invalide'}), 400

        # 2. Le fichier doit appartenir au projet (vérifier le numéro de projet dans le nom)
        projet_ref = project.numero_projet or f'ID{project_id}'
        if not filename.startswith(projet_ref):
            return jsonify({'error': 'Ce fichier n\'appartient pas à ce projet'}), 400

        # 3. Le fichier doit exister
        if not os.path.exists(file_path):
            return jsonify({'error': 'Fichier non trouvé'}), 404

        # Supprimer le fichier
        os.remove(file_path)

        print(f"✅ Archive supprimée par admin: {filename}")

        return jsonify({
            'message': 'Archive supprimée avec succès',
            'filename': filename
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erreur lors de la suppression: {str(e)}'}), 500