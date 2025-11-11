"""
Routes pour la gestion des projets et des fiches d'évaluation
"""
from flask import request, jsonify
import traceback

def register_project_routes(app, Project, FicheEvaluation, db, User=None):
        
    @app.route('/api/projects/<int:project_id>/presentation', methods=['GET'])
    def get_project_presentation(project_id):
        """Récupère les données de présentation d'un projet pour pré-remplir la fiche d'évaluation"""
        try:
            import json
            project = Project.query.get_or_404(project_id)
            
            # Lire les cases à cocher depuis la base de données (JSON)
            try:
                origine_db = getattr(project, 'origine_projet', None)
                if origine_db:
                    origine_projet = json.loads(origine_db)
                else:
                    origine_projet = {'maturation': False, 'offre_spontanee': False, 'autres': False}
            except Exception:
                origine_projet = {'maturation': False, 'offre_spontanee': False, 'autres': False}

            try:
                typologie_db = getattr(project, 'typologie_projet', None)
                if typologie_db:
                    typologie_projet = json.loads(typologie_db)
                else:
                    typologie_projet = {'productif': False, 'appui_production': False, 'social': False, 'environnemental': False}
            except Exception:
                typologie_projet = {'productif': False, 'appui_production': False, 'social': False, 'environnemental': False}

            presentation_data = {
                'id': project.id,
                'intitule': project.titre,
                'titre': project.titre,
                'secteur': project.secteur or 'Non spécifié',
                'description': project.description or '',
                'cout_estimatif': project.cout_estimatif or 0,
                'poles': project.poles or 'Territoire national',
                'organisme_tutelle': getattr(project, 'organisme_tutelle', None) or '',
                # 'auteur_nom' supprimé
                'origine_projet': origine_projet,
                'typologie_projet': typologie_projet,
                'evaluateur_nom': project.evaluateur_nom if hasattr(project, 'evaluateur_nom') else ''
            }
            return jsonify(presentation_data)
            
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': f'Erreur lors de la récupération: {str(e)}'}), 500

    @app.route('/api/projects/<int:project_id>/fiche-evaluation', methods=['GET'])
    def get_fiche_evaluation(project_id):
        """Récupère une fiche d'évaluation existante"""
        try:
            fiche = FicheEvaluation.query.filter_by(project_id=project_id).first()
            if not fiche:
                # Si aucune fiche, retourner l'évaluateur affecté au projet (si existant)
                project = Project.query.get_or_404(project_id)
                evaluateur_nom = project.evaluateur_nom or ''
                return jsonify({
                    'id': None,
                    'project_id': project_id,
                    'evaluateur_nom': evaluateur_nom,
                    'criteres': {},
                    'proposition': '',
                    'recommandations': '',
                    'score_total': 0,
                    'appreciation_globale': '',
                    'date_evaluation': None
                })
            # Préparer les critères
            criteres = {
                'pertinence': {
                    'score': fiche.pertinence_score or 0,
                    'description': fiche.pertinence_appreciation or '',
                    'recommandations': fiche.pertinence_recommandations or ''
                },
                'alignement': {
                    'score': fiche.alignement_score or 0,
                    'description': fiche.alignement_appreciation or '',
                    'recommandations': fiche.alignement_recommandations or ''
                },
                'activites_couts': {
                    'score': fiche.pertinence_activites_score or 0,
                    'description': fiche.pertinence_activites_appreciation or '',
                    'recommandations': fiche.pertinence_activites_recommandations or ''
                },
                'equite': {
                    'score': fiche.equite_score or 0,
                    'description': fiche.equite_appreciation or '',
                    'recommandations': fiche.equite_recommandations or ''
                },
                'viabilite': {
                    'score': fiche.rentabilite_financiere_score or 0,
                    'description': fiche.rentabilite_financiere_appreciation or '',
                    'recommandations': fiche.rentabilite_financiere_recommandations or ''
                },
                'rentabilite': {
                    'score': fiche.rentabilite_socio_score or 0,
                    'description': fiche.rentabilite_socio_appreciation or '',
                    'recommandations': fiche.rentabilite_socio_recommandations or ''
                },
                'benefices_strategiques': {
                    'score': fiche.benefices_strategiques_score or 0,
                    'description': fiche.benefices_strategiques_appreciation or '',
                    'recommandations': fiche.benefices_strategiques_recommandations or ''
                },
                'perennite': {
                    'score': fiche.perennite_score or 0,
                    'description': fiche.perennite_appreciation or '',
                    'recommandations': fiche.perennite_recommandations or ''
                },
                'avantages_intangibles': {
                    'score': fiche.avantages_couts_score or 0,
                    'description': fiche.avantages_couts_appreciation or '',
                    'recommandations': fiche.avantages_couts_recommandations or ''
                },
                'faisabilite': {
                    'score': fiche.faisabilite_score or 0,
                    'description': fiche.faisabilite_appreciation or '',
                    'recommandations': fiche.faisabilite_recommandations or ''
                },
                'ppp': {
                    'score': fiche.capacite_execution_score or 0,
                    'description': fiche.capacite_execution_appreciation or '',
                    'recommandations': fiche.capacite_execution_recommandations or ''
                },
                'impact_environnemental': {
                    'score': fiche.impacts_environnementaux_score or 0,
                    'description': fiche.impacts_environnementaux_appreciation or '',
                    'recommandations': fiche.impacts_environnementaux_recommandations or ''
                },
                'impact_emploi': {
                    'score': 0,  # Pas de score pour l'impact emploi selon le modèle
                    'description': fiche.impact_sur_emploi or '',
                    'recommandations': ''
                }
            }
            evaluation_data = {
                'id': fiche.id,
                'project_id': fiche.project_id,
                'evaluateur_nom': fiche.evaluateur_nom or '',
                'criteres': criteres,
                'proposition': fiche.proposition or '',
                'recommandations': fiche.recommandations_generales or '',
                'score_total': fiche.calculer_score_total(),
                'appreciation_globale': fiche.get_appreciation_globale(),
                'date_evaluation': fiche.date_evaluation.isoformat() if fiche.date_evaluation else None
            }
            return jsonify(evaluation_data)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/projects/<int:project_id>/fiche-evaluation', methods=['POST', 'PUT'])
    def save_fiche_evaluation(project_id):
        """Sauvegarde ou met à jour une fiche d'évaluation"""
        try:
            data = request.get_json()
            
            # Vérifier que le projet existe
            project = Project.query.get_or_404(project_id)
            
            # Chercher une fiche existante
            fiche = FicheEvaluation.query.filter_by(project_id=project_id).first()
            
            if not fiche:
                # Créer une nouvelle fiche
                fiche = FicheEvaluation(project_id=project_id)
                db.session.add(fiche)
            
            # Mettre à jour les données générales
            fiche.evaluateur_nom = data.get('evaluateur_nom', '')
            fiche.proposition = data.get('proposition', '')
            fiche.recommandations_generales = data.get('recommandations', '')
            
            # Mettre à jour les critères selon le modèle réel
            criteres = data.get('criteres', {})
            
            # Pertinence
            pertinence = criteres.get('pertinence', {})
            fiche.pertinence_score = pertinence.get('score', 0)
            fiche.pertinence_appreciation = pertinence.get('description', '')
            fiche.pertinence_recommandations = pertinence.get('recommandations', '')
            
            # Alignement
            alignement = criteres.get('alignement', {})
            fiche.alignement_score = alignement.get('score', 0)
            fiche.alignement_appreciation = alignement.get('description', '')
            fiche.alignement_recommandations = alignement.get('recommandations', '')
            
            # Activités et coûts
            activites_couts = criteres.get('activites_couts', {})
            fiche.pertinence_activites_score = activites_couts.get('score', 0)
            fiche.pertinence_activites_appreciation = activites_couts.get('description', '')
            fiche.pertinence_activites_recommandations = activites_couts.get('recommandations', '')
            
            # Équité
            equite = criteres.get('equite', {})
            fiche.equite_score = equite.get('score', 0)
            fiche.equite_appreciation = equite.get('description', '')
            fiche.equite_recommandations = equite.get('recommandations', '')
            
            # Viabilité -> rentabilité financière 
            viabilite = criteres.get('viabilite', {})
            fiche.rentabilite_financiere_score = viabilite.get('score', 0)
            fiche.rentabilite_financiere_appreciation = viabilite.get('description', '')
            fiche.rentabilite_financiere_recommandations = viabilite.get('recommandations', '')
            
            # Rentabilité -> rentabilité socio-économique
            rentabilite = criteres.get('rentabilite', {})
            fiche.rentabilite_socio_score = rentabilite.get('score', 0)
            fiche.rentabilite_socio_appreciation = rentabilite.get('description', '')
            fiche.rentabilite_socio_recommandations = rentabilite.get('recommandations', '')
            
            # Bénéfices stratégiques
            benefices_strategiques = criteres.get('benefices_strategiques', {})
            fiche.benefices_strategiques_score = benefices_strategiques.get('score', 0)
            fiche.benefices_strategiques_appreciation = benefices_strategiques.get('description', '')
            fiche.benefices_strategiques_recommandations = benefices_strategiques.get('recommandations', '')
            
            # Pérennité
            perennite = criteres.get('perennite', {})
            fiche.perennite_score = perennite.get('score', 0)
            fiche.perennite_appreciation = perennite.get('description', '')
            fiche.perennite_recommandations = perennite.get('recommandations', '')
            
            # Avantages intangibles
            avantages_intangibles = criteres.get('avantages_intangibles', {})
            fiche.avantages_couts_score = avantages_intangibles.get('score', 0)
            fiche.avantages_couts_appreciation = avantages_intangibles.get('description', '')
            fiche.avantages_couts_recommandations = avantages_intangibles.get('recommandations', '')
            
            # Faisabilité
            faisabilite = criteres.get('faisabilite', {})
            fiche.faisabilite_score = faisabilite.get('score', 0)
            fiche.faisabilite_appreciation = faisabilite.get('description', '')
            fiche.faisabilite_recommandations = faisabilite.get('recommandations', '')
            
            # PPP -> capacité d'exécution
            ppp = criteres.get('ppp', {})
            fiche.capacite_execution_score = ppp.get('score', 0)
            fiche.capacite_execution_appreciation = ppp.get('description', '')
            fiche.capacite_execution_recommandations = ppp.get('recommandations', '')
            
            # Impact environnemental
            impact_environnemental = criteres.get('impact_environnemental', {})
            fiche.impacts_environnementaux_score = impact_environnemental.get('score', 0)
            fiche.impacts_environnementaux_appreciation = impact_environnemental.get('description', '')
            fiche.impacts_environnementaux_recommandations = impact_environnemental.get('recommandations', '')
            
            # Impact emploi (description seulement selon le modèle)
            impact_emploi = criteres.get('impact_emploi', {})
            fiche.impact_sur_emploi = impact_emploi.get('description', '')
            
            db.session.commit()
            
            return jsonify({
                'message': 'Fiche d\'évaluation sauvegardée avec succès',
                'id': fiche.id,
                'score_total': fiche.calculer_score_total(),
                'appreciation_globale': fiche.get_appreciation_globale()
            })
            
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    # Note: la route '/api/users/profile' est définie dans routes/user_routes.py
    # pour centraliser la gestion des utilisateurs et éviter les conflits de route.
    # Si une intégration avec flask-login est nécessaire, elle doit être réalisée
    # dans `routes/user_routes.py` et non ici.