"""
Routes pour les fiches d'évaluation conformes au format réel DGPPE
"""

from flask import Blueprint, request, jsonify, send_file
import os
import sys
import json
from datetime import datetime
from models import db, Project, FicheEvaluation

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
            'snd_2025_2029': {
                'axes': '',
                'objectifs_strategiques': '',
                'odd': ''
            },
            'durees': {
                'analyse': '25 ans',
                'realisation': '05 ans',
                'exploitation': '20 ans'
            },
            'localisation': project.poles or 'Territoire national',
            'parties_prenantes': '',
            'projets_connexes': '',
            'objectif_projet': getattr(project, 'objectifs', ''),
            'activites_principales': project.description or '',
            'extrants_resultats': '',
            'evaluateur_nom': getattr(project, 'evaluateur_nom', '')
        }
        return jsonify(presentation_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération: {str(e)}'}), 500

@evaluation_bp.route('/api/projects/<int:project_id>/fiche-evaluation', methods=['GET'])
def get_fiche_evaluation(project_id):
    """Récupération de la fiche d'évaluation d'un projet"""
    try:
        fiche = FicheEvaluation.query.filter_by(project_id=project_id).first()
        
        if not fiche:
            return jsonify({'error': 'Aucune fiche d\'évaluation trouvée'}), 404
        
        # Convertir en dictionnaire avec les nouveaux champs
        fiche_data = {
            'id': fiche.id,
            'project_id': fiche.project_id,
            'evaluateur_nom': fiche.evaluateur_nom,
            'date_evaluation': fiche.date_evaluation.isoformat() if fiche.date_evaluation else None,
            'reference_fiche': fiche.reference_fiche,
            
            # Critères d'évaluation avec scores et descriptions
            'criteres': {
                'pertinence': {
                    'score': fiche.pertinence_score,
                    'max_score': 5,
                    'description': fiche.pertinence_description
                },
                'alignement': {
                    'score': fiche.alignement_score,
                    'max_score': 10,
                    'description': fiche.alignement_description
                },
                'activites_couts': {
                    'score': fiche.activites_couts_score,
                    'max_score': 15,
                    'description': fiche.activites_couts_description
                },
                'equite': {
                    'score': fiche.equite_score,
                    'max_score': 15,
                    'description': fiche.equite_description
                },
                'viabilite': {
                    'score': fiche.viabilite_score,
                    'max_score': 5,
                    'description': fiche.viabilite_description
                },
                'rentabilite': {
                    'score': fiche.rentabilite_score,
                    'max_score': 5,
                    'description': fiche.rentabilite_description
                },
                'benefices_strategiques': {
                    'score': fiche.benefices_strategiques_score,
                    'max_score': 10,
                    'description': fiche.benefices_strategiques_description
                },
                'perennite': {
                    'score': fiche.perennite_score,
                    'max_score': 5,
                    'description': fiche.perennite_description
                },
                'avantages_intangibles': {
                    'score': fiche.avantages_intangibles_score,
                    'max_score': 10,
                    'description': fiche.avantages_intangibles_description
                },
                'faisabilite': {
                    'score': fiche.faisabilite_score,
                    'max_score': 5,
                    'description': fiche.faisabilite_description
                },
                'ppp': {
                    'score': fiche.ppp_score,
                    'max_score': 5,
                    'description': fiche.ppp_description
                },
                'impact_environnemental': {
                    'score': fiche.impact_environnemental_score,
                    'max_score': 5,
                    'description': fiche.impact_environnemental_description
                }
            },
            
            'impact_emploi_description': fiche.impact_emploi_description,
            'score_total': fiche.score_total,
            'proposition': fiche.proposition,
            'recommandations': fiche.recommandations,
            'fichier_pdf': fiche.fichier_pdf
        }
        
        return jsonify(fiche_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération: {str(e)}'}), 500

@evaluation_bp.route('/api/projects/<int:project_id>/fiche-evaluation', methods=['POST', 'PUT'])
def create_or_update_fiche_evaluation(project_id):
    """Création ou mise à jour d'une fiche d'évaluation avec le nouveau format"""
    try:
        data = request.get_json()

        # Vérifier que le projet existe
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Projet non trouvé'}), 404

        # Récupérer ou créer la fiche d'évaluation
        fiche = FicheEvaluation.query.filter_by(project_id=project_id).first()

        is_update = fiche is not None

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
        
        # PERTINENCE (/5)
        if 'pertinence' in criteres:
            fiche.pertinence_score = min(criteres['pertinence'].get('score', 0), 5)
            fiche.pertinence_description = criteres['pertinence'].get('description', '')
        
        # ALIGNEMENT (/10)
        if 'alignement' in criteres:
            fiche.alignement_score = min(criteres['alignement'].get('score', 0), 10)
            fiche.alignement_description = criteres['alignement'].get('description', '')
        
        # ACTIVITES ET COUTS (/15)
        if 'activites_couts' in criteres:
            fiche.activites_couts_score = min(criteres['activites_couts'].get('score', 0), 15)
            fiche.activites_couts_description = criteres['activites_couts'].get('description', '')
        
        # EQUITE (/15)
        if 'equite' in criteres:
            fiche.equite_score = min(criteres['equite'].get('score', 0), 15)
            fiche.equite_description = criteres['equite'].get('description', '')
        
        # VIABILITE (/5)
        if 'viabilite' in criteres:
            fiche.viabilite_score = min(criteres['viabilite'].get('score', 0), 5)
            fiche.viabilite_description = criteres['viabilite'].get('description', '')
        
        # RENTABILITE (/5)
        if 'rentabilite' in criteres:
            fiche.rentabilite_score = min(criteres['rentabilite'].get('score', 0), 5)
            fiche.rentabilite_description = criteres['rentabilite'].get('description', '')
        
        # BENEFICES STRATEGIQUES (/10)
        if 'benefices_strategiques' in criteres:
            fiche.benefices_strategiques_score = min(criteres['benefices_strategiques'].get('score', 0), 10)
            fiche.benefices_strategiques_description = criteres['benefices_strategiques'].get('description', '')
        
        # PERENNITE (/5)
        if 'perennite' in criteres:
            fiche.perennite_score = min(criteres['perennite'].get('score', 0), 5)
            fiche.perennite_description = criteres['perennite'].get('description', '')
        
        # AVANTAGES INTANGIBLES (/10)
        if 'avantages_intangibles' in criteres:
            fiche.avantages_intangibles_score = min(criteres['avantages_intangibles'].get('score', 0), 10)
            fiche.avantages_intangibles_description = criteres['avantages_intangibles'].get('description', '')
        
        # FAISABILITE (/5)
        if 'faisabilite' in criteres:
            fiche.faisabilite_score = min(criteres['faisabilite'].get('score', 0), 5)
            fiche.faisabilite_description = criteres['faisabilite'].get('description', '')
        
        # PPP (/5)
        if 'ppp' in criteres:
            fiche.ppp_score = min(criteres['ppp'].get('score', 0), 5)
            fiche.ppp_description = criteres['ppp'].get('description', '')
        
        # IMPACT ENVIRONNEMENTAL (/5)
        if 'impact_environnemental' in criteres:
            fiche.impact_environnemental_score = min(criteres['impact_environnemental'].get('score', 0), 5)
            fiche.impact_environnemental_description = criteres['impact_environnemental'].get('description', '')
        
        # IMPACT SUR L'EMPLOI (/5)
        if 'impact_emploi' in criteres:
            fiche.impact_emploi_score = min(criteres['impact_emploi'].get('score', 0), 5)
            fiche.impact_emploi_description = criteres['impact_emploi'].get('description', '')
            fiche.impact_emploi_recommandations = criteres['impact_emploi'].get('recommandations', '')
        
        # Conclusion
        fiche.proposition = data.get('proposition', '')
        fiche.recommandations = data.get('recommandations', '')
        
        # Calcul automatique du score total
        score_total = fiche.calculer_score_total()
        
        # Mise à jour du statut du projet selon la proposition
        if fiche.proposition:
            if fiche.proposition.lower() == 'favorable':
                project.statut = 'évalué'
                project.avis = 'favorable'
            elif 'sous condition' in fiche.proposition.lower():
                project.statut = 'évalué'
                project.avis = 'favorable sous conditions'
            else:
                project.statut = 'évalué'
                project.avis = 'défavorable'
        
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
            pdf_directory = os.path.join(os.path.dirname(__file__), 'pdfs', 'fiches_evaluation')

            # Générer le PDF
            pdf_path = generer_fiche_evaluation_dgppe_pdf(fiche_data, project_data, pdf_directory)
            fiche.fichier_pdf = os.path.basename(pdf_path)
            db.session.commit()
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
    """Génération du PDF de la fiche d'évaluation"""
    try:
        # Récupérer le projet et sa fiche d'évaluation
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Projet non trouvé'}), 404
        
        fiche = FicheEvaluation.query.filter_by(project_id=project_id).first()
        if not fiche:
            return jsonify({'error': 'Aucune fiche d\'évaluation trouvée'}), 404

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
            # 'auteur_nom' supprimé
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
        
        # Répertoire de sortie pour les PDFs
        pdf_directory = os.path.join(os.path.dirname(__file__), 'pdfs', 'fiches_evaluation')

        # Générer le PDF avec le générateur DGPPE
        pdf_path = generer_fiche_evaluation_dgppe_pdf(fiche_data, project_data, pdf_directory)
        
        # Mettre à jour le chemin du fichier PDF dans la base
        fiche.fichier_pdf = os.path.basename(pdf_path)
        db.session.commit()
        
        # Retourner le fichier PDF pour ouverture dans un nouvel onglet
        return send_file(
            pdf_path,
            as_attachment=False,
            download_name=f"{fiche.reference_fiche}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la génération du PDF: {str(e)}'}), 500

@evaluation_bp.route('/api/projects/<int:project_id>/fiche-evaluation/pdf/<filename>', methods=['GET'])
def download_fiche_evaluation_pdf(project_id, filename):
    """Téléchargement d'un PDF de fiche d'évaluation existant"""
    try:
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
    """Suppression d'une fiche d'évaluation"""
    try:
        fiche = FicheEvaluation.query.filter_by(project_id=project_id).first()
        
        if not fiche:
            return jsonify({'error': 'Aucune fiche d\'évaluation trouvée'}), 404
        
        # Supprimer le fichier PDF s'il existe
        if fiche.fichier_pdf:
            pdf_directory = os.path.join(os.path.dirname(__file__), 'pdfs', 'fiches_evaluation')
            pdf_path = os.path.join(pdf_directory, fiche.fichier_pdf)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        
        # Supprimer la fiche de la base
        db.session.delete(fiche)
        db.session.commit()
        
        return jsonify({'message': 'Fiche d\'évaluation supprimée avec succès'}), 200
        
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