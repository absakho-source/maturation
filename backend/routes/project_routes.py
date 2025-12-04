"""
Routes pour la gestion des projets et des fiches d'évaluation
VERSION: 2025-12-04-11:30 - FORCE GUNICORN RELOAD
"""
from flask import request, jsonify
import traceback
import os
import sys

# FORCE RELOAD MARKER - Ne pas supprimer
_MODULE_VERSION = "2025-12-04-recommandations-fix-FINAL"
print(f"[PROJECT_ROUTES] Module chargé - Version: {_MODULE_VERSION}", file=sys.stderr, flush=True)

def register_project_routes(app, Project, FicheEvaluation, db, User=None, Historique=None):
    # Importer la fonction d'archivage
    try:
        from utils.archivage import archiver_fiche
    except ImportError:
        print("[WARNING] Module d'archivage non disponible")
        archiver_fiche = None
        
    @app.route('/api/projects/<int:project_id>/presentation', methods=['GET'])
    def get_project_presentation(project_id):
        """Récupère les données de présentation d'un projet pour pré-remplir la fiche d'évaluation"""
        try:
            # Vérifier le rôle de l'utilisateur
            role = request.args.get("role", "")

            # Les invités ne peuvent pas accéder aux données de présentation
            if role == "invite":
                return jsonify({"error": "Accès refusé: Les invités ne peuvent pas accéder aux données de projets"}), 403

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
            # Vérifier le rôle de l'utilisateur
            role = request.args.get("role", "")

            # Les invités ne peuvent pas accéder aux fiches d'évaluation
            if role == "invite":
                return jsonify({"error": "Accès refusé: Les invités ne peuvent pas accéder aux fiches d'évaluation"}), 403

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
                    'description': fiche.pertinence_description or '',
                    'recommandations': fiche.pertinence_recommandations or ''
                },
                'alignement': {
                    'score': fiche.alignement_score or 0,
                    'description': fiche.alignement_description or '',
                    'recommandations': fiche.alignement_recommandations or ''
                },
                'activites_couts': {
                    'score': fiche.activites_couts_score or 0,
                    'description': fiche.activites_couts_description or '',
                    'recommandations': fiche.activites_couts_recommandations or ''
                },
                'equite': {
                    'score': fiche.equite_score or 0,
                    'description': fiche.equite_description or '',
                    'recommandations': fiche.equite_recommandations or ''
                },
                'viabilite': {
                    'score': fiche.viabilite_score or 0,
                    'description': fiche.viabilite_description or '',
                    'recommandations': fiche.viabilite_recommandations or ''
                },
                'rentabilite': {
                    'score': fiche.rentabilite_score or 0,
                    'description': fiche.rentabilite_description or '',
                    'recommandations': fiche.rentabilite_recommandations or ''
                },
                'benefices_strategiques': {
                    'score': fiche.benefices_strategiques_score or 0,
                    'description': fiche.benefices_strategiques_description or '',
                    'recommandations': fiche.benefices_strategiques_recommandations or ''
                },
                'perennite': {
                    'score': fiche.perennite_score or 0,
                    'description': fiche.perennite_description or '',
                    'recommandations': fiche.perennite_recommandations or ''
                },
                'avantages_intangibles': {
                    'score': fiche.avantages_intangibles_score or 0,
                    'description': fiche.avantages_intangibles_description or '',
                    'recommandations': fiche.avantages_intangibles_recommandations or ''
                },
                'faisabilite': {
                    'score': fiche.faisabilite_score or 0,
                    'description': fiche.faisabilite_description or '',
                    'recommandations': fiche.faisabilite_recommandations or ''
                },
                'ppp': {
                    'score': fiche.ppp_score or 0,
                    'description': fiche.ppp_description or '',
                    'recommandations': fiche.ppp_recommandations or ''
                },
                'impact_environnemental': {
                    'score': fiche.impact_environnemental_score or 0,
                    'description': fiche.impact_environnemental_description or '',
                    'recommandations': fiche.impact_environnemental_recommandations or ''
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

            # Vérifier le rôle de l'utilisateur
            role = data.get("role", "")

            # Seuls certains rôles peuvent modifier les fiches d'évaluation
            roles_autorises = ['evaluateur', 'secretariatsct', 'presidencesct', 'presidencecomite', 'admin']
            if role not in roles_autorises:
                return jsonify({"error": "Accès refusé: Vous n'avez pas les permissions pour modifier les fiches d'évaluation"}), 403

            # Vérifier que le projet existe
            project = Project.query.get_or_404(project_id)
            
            # Chercher une fiche existante
            fiche = FicheEvaluation.query.filter_by(project_id=project_id).first()

            # Si la fiche existe déjà, l'archiver avant modification
            if fiche and archiver_fiche:
                evaluateur_nom = data.get('evaluateur_nom', fiche.evaluateur_nom)
                try:
                    archive_result = archiver_fiche(fiche, 'modification', evaluateur_nom)
                    if archive_result:
                        print(f"[FICHE UPDATE] Ancienne fiche archivée: {archive_result}")
                    else:
                        print(f"[FICHE UPDATE] Avertissement: archivage échoué")
                except Exception as archive_error:
                    print(f"[FICHE UPDATE] Erreur archivage: {archive_error}")
                    # Continue même si l'archivage échoue

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

            # DEBUG: Logger les données reçues (FORCE RELOAD - 2025-12-04)
            print(f"[FICHE UPDATE DEBUG] Données reçues:")
            print(f"  - Critères: {list(criteres.keys())}")
            for key, value in criteres.items():
                print(f"  - {key}: score={value.get('score')}, has_desc={bool(value.get('description'))}, has_reco={bool(value.get('recommandations'))}")

            # FORCE: Flush stdout pour garantir que les logs apparaissent
            import sys
            sys.stdout.flush()

            # Pertinence
            pertinence = criteres.get('pertinence', {})
            fiche.pertinence_score = pertinence.get('score', 0)
            fiche.pertinence_description = pertinence.get('description', '')
            fiche.pertinence_recommandations = pertinence.get('recommandations', '')

            # Alignement
            alignement = criteres.get('alignement', {})
            fiche.alignement_score = alignement.get('score', 0)
            fiche.alignement_description = alignement.get('description', '')
            fiche.alignement_recommandations = alignement.get('recommandations', '')

            # Activités et coûts
            activites_couts = criteres.get('activites_couts', {})
            fiche.activites_couts_score = activites_couts.get('score', 0)
            fiche.activites_couts_description = activites_couts.get('description', '')
            fiche.activites_couts_recommandations = activites_couts.get('recommandations', '')

            # Équité
            equite = criteres.get('equite', {})
            fiche.equite_score = equite.get('score', 0)
            fiche.equite_description = equite.get('description', '')
            fiche.equite_recommandations = equite.get('recommandations', '')

            # Viabilité
            viabilite = criteres.get('viabilite', {})
            fiche.viabilite_score = viabilite.get('score', 0)
            fiche.viabilite_description = viabilite.get('description', '')
            fiche.viabilite_recommandations = viabilite.get('recommandations', '')

            # Rentabilité
            rentabilite = criteres.get('rentabilite', {})
            fiche.rentabilite_score = rentabilite.get('score', 0)
            fiche.rentabilite_description = rentabilite.get('description', '')
            fiche.rentabilite_recommandations = rentabilite.get('recommandations', '')

            # Bénéfices stratégiques
            benefices_strategiques = criteres.get('benefices_strategiques', {})
            fiche.benefices_strategiques_score = benefices_strategiques.get('score', 0)
            fiche.benefices_strategiques_description = benefices_strategiques.get('description', '')
            fiche.benefices_strategiques_recommandations = benefices_strategiques.get('recommandations', '')

            # Pérennité
            perennite = criteres.get('perennite', {})
            fiche.perennite_score = perennite.get('score', 0)
            fiche.perennite_description = perennite.get('description', '')
            fiche.perennite_recommandations = perennite.get('recommandations', '')

            # Avantages intangibles
            avantages_intangibles = criteres.get('avantages_intangibles', {})
            fiche.avantages_intangibles_score = avantages_intangibles.get('score', 0)
            fiche.avantages_intangibles_description = avantages_intangibles.get('description', '')
            fiche.avantages_intangibles_recommandations = avantages_intangibles.get('recommandations', '')

            # Faisabilité
            faisabilite = criteres.get('faisabilite', {})
            fiche.faisabilite_score = faisabilite.get('score', 0)
            fiche.faisabilite_description = faisabilite.get('description', '')
            fiche.faisabilite_recommandations = faisabilite.get('recommandations', '')

            # PPP
            ppp = criteres.get('ppp', {})
            fiche.ppp_score = ppp.get('score', 0)
            fiche.ppp_description = ppp.get('description', '')
            fiche.ppp_recommandations = ppp.get('recommandations', '')

            # Impact environnemental
            impact_environnemental = criteres.get('impact_environnemental', {})
            fiche.impact_environnemental_score = impact_environnemental.get('score', 0)
            fiche.impact_environnemental_description = impact_environnemental.get('description', '')
            fiche.impact_environnemental_recommandations = impact_environnemental.get('recommandations', '')

            # Mettre à jour le champ avis du projet pour qu'il se reflète dans les dashboards
            if fiche.proposition:
                project.avis = fiche.proposition
                print(f"[FICHE UPDATE] Mise à jour de project.avis = {fiche.proposition}")

            db.session.commit()

            # DEBUG: Vérifier que les données sont bien sauvegardées
            print(f"[FICHE UPDATE DEBUG] Après sauvegarde:")
            print(f"  - pertinence_recommandations: '{fiche.pertinence_recommandations[:50] if fiche.pertinence_recommandations else None}'")
            print(f"  - alignement_recommandations: '{fiche.alignement_recommandations[:50] if fiche.alignement_recommandations else None}'")
            print(f"  - fichier_pdf avant génération: '{fiche.fichier_pdf}'")

            # Générer le nouveau PDF après la sauvegarde des données
            try:
                # Import du générateur PDF
                try:
                    from pdf_generator_dgppe import generer_fiche_evaluation_dgppe_pdf
                except ImportError:
                    import sys
                    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
                    from pdf_generator_dgppe import generer_fiche_evaluation_dgppe_pdf

                # Préparer les données pour le PDF
                fiche_data = {
                    'id': fiche.id,
                    'evaluateur_nom': fiche.evaluateur_nom,
                    'proposition': fiche.proposition,
                    'recommandations': fiche.recommandations_generales,
                    'criteres': {
                        'pertinence': {'score': fiche.pertinence_score, 'description': fiche.pertinence_description, 'recommandations': fiche.pertinence_recommandations},
                        'alignement': {'score': fiche.alignement_score, 'description': fiche.alignement_description, 'recommandations': fiche.alignement_recommandations},
                        'activites_couts': {'score': fiche.activites_couts_score, 'description': fiche.activites_couts_description, 'recommandations': fiche.activites_couts_recommandations},
                        'equite': {'score': fiche.equite_score, 'description': fiche.equite_description, 'recommandations': fiche.equite_recommandations},
                        'viabilite': {'score': fiche.viabilite_score, 'description': fiche.viabilite_description, 'recommandations': fiche.viabilite_recommandations},
                        'rentabilite': {'score': fiche.rentabilite_score, 'description': fiche.rentabilite_description, 'recommandations': fiche.rentabilite_recommandations},
                        'benefices_strategiques': {'score': fiche.benefices_strategiques_score, 'description': fiche.benefices_strategiques_description, 'recommandations': fiche.benefices_strategiques_recommandations},
                        'perennite': {'score': fiche.perennite_score, 'description': fiche.perennite_description, 'recommandations': fiche.perennite_recommandations},
                        'avantages_intangibles': {'score': fiche.avantages_intangibles_score, 'description': fiche.avantages_intangibles_description, 'recommandations': fiche.avantages_intangibles_recommandations},
                        'faisabilite': {'score': fiche.faisabilite_score, 'description': fiche.faisabilite_description, 'recommandations': fiche.faisabilite_recommandations},
                        'ppp': {'score': fiche.ppp_score, 'description': fiche.ppp_description, 'recommandations': fiche.ppp_recommandations},
                        'impact_environnemental': {'score': fiche.impact_environnemental_score, 'description': fiche.impact_environnemental_description, 'recommandations': fiche.impact_environnemental_recommandations}
                    }
                }

                project_data = {
                    'id': project.id,
                    'numero_projet': project.numero_projet,
                    'titre': project.titre,
                    'organisme_tutelle': project.organisme_tutelle,
                    'cout_estimatif': project.cout_estimatif
                }

                # Répertoire de sortie pour les PDFs
                pdf_directory = os.path.join(os.path.dirname(__file__), 'pdfs', 'fiches_evaluation')
                os.makedirs(pdf_directory, exist_ok=True)

                # Générer le nouveau PDF
                pdf_path = generer_fiche_evaluation_dgppe_pdf(fiche_data, project_data, pdf_directory)
                fiche.fichier_pdf = os.path.basename(pdf_path)
                db.session.commit()
                print(f"[FICHE UPDATE] Nouveau PDF généré: {fiche.fichier_pdf}")
            except Exception as pdf_error:
                print(f"[FICHE UPDATE] Erreur génération PDF: {pdf_error}")
                import traceback
                traceback.print_exc()
                # Continue même si la génération PDF échoue

            # Enregistrer dans l'historique
            if Historique:
                try:
                    evaluateur_nom = data.get('evaluateur_nom', fiche.evaluateur_nom)
                    score_total = fiche.calculer_score_total()
                    avis = fiche.proposition or 'non défini'
                    action_text = f"Modification de la fiche d'évaluation (Score: {score_total}/100, Avis: {avis})"
                    historique_entry = Historique(
                        project_id=project_id,
                        action=action_text,
                        auteur=evaluateur_nom or 'Evaluateur',
                        role='evaluateur'
                    )
                    db.session.add(historique_entry)
                    db.session.commit()
                except Exception as hist_error:
                    print(f"Erreur lors de l'enregistrement dans l'historique: {hist_error}")
                    # Continue même si l'historique échoue

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