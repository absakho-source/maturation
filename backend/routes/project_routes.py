"""
Routes pour la gestion des projets et des fiches d'évaluation
VERSION: 2025-12-04-12:00 - FORCE RELOAD WITH ROLE FIX
"""
from flask import request, jsonify
import traceback
import os
import sys
from workflow_validator import WorkflowValidator

# FORCE RELOAD MARKER - Ne pas supprimer - TIMESTAMP: 2025-12-04T12:00:00
_MODULE_VERSION = "2025-12-04-12:00-ROLE-FIX-CRITICAL"
print(f"[PROJECT_ROUTES] ===== MODULE CHARGÉ - VERSION: {_MODULE_VERSION} =====", file=sys.stderr, flush=True)
print(f"[PROJECT_ROUTES] Le fix du paramètre 'role' est actif!", file=sys.stderr, flush=True)

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
            print(f"[PRESENTATION] Chargement du projet {project_id}")
            project = Project.query.get_or_404(project_id)
            print(f"[PRESENTATION] Projet trouvé: {project.titre}")

            # Lire les cases à cocher depuis la base de données (JSON)
            try:
                origine_db = getattr(project, 'origine_projet', None)
                print(f"[PRESENTATION] origine_projet DB: {origine_db}")
                if origine_db:
                    origine_projet = json.loads(origine_db)
                else:
                    origine_projet = {'maturation': False, 'offre_spontanee': False, 'autres': False}
            except Exception as e:
                print(f"[PRESENTATION] Erreur parsing origine_projet: {e}")
                origine_projet = {'maturation': False, 'offre_spontanee': False, 'autres': False}

            print(f"[PRESENTATION] Construction de presentation_data")
            presentation_data = {
                'id': project.id,
                'intitule': project.titre,
                'titre': project.titre,
                'secteur': getattr(project, 'secteur', None) or 'Non spécifié',
                'description': getattr(project, 'description', None) or '',
                'cout_estimatif': getattr(project, 'cout_estimatif', None) or 0,
                'poles': getattr(project, 'poles', None) or 'Territoire national',
                'organisme_tutelle': getattr(project, 'organisme_tutelle', None) or '',
                'origine_projet': origine_projet,
                'evaluateur_nom': getattr(project, 'evaluateur_nom', None) or ''
            }
            print(f"[PRESENTATION] Données construites avec succès")
            return jsonify(presentation_data)

        except Exception as e:
            print(f"[PRESENTATION] ERREUR: {str(e)}", flush=True)
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

                # Section I - Présentation du projet
                'intitule': fiche.intitule_projet or '',
                'secteur': fiche.sous_secteur or '',
                'poles': '',  # Ce champ vient du projet, pas de la fiche
                'cout_estimatif': fiche.cout_projet or '',
                'organisme_tutelle': fiche.organisme_tutelle or '',
                'description': '',  # Ce champ vient du projet, pas de la fiche

                # Section II - Classification
                'origine_projet_choix': fiche.origine_projet or '',
                'origine_projet_autres_precision': '',
                'changement_climatique_adaptation': fiche.changement_climatique_adaptation or False,
                'changement_climatique_attenuation': fiche.changement_climatique_attenuation or False,
                'genre': fiche.genre or False,

                # Tableaux détaillés
                'articulation': fiche.articulation or '',
                'axes': fiche.axes or '',
                'objectifs_strategiques': fiche.objectifs_strategiques or '',
                'odd': fiche.odd or '',
                'duree_analyse': fiche.duree_analyse or '',
                'realisation': fiche.realisation or '',
                'exploitation': fiche.exploitation or '',
                'localisation': fiche.localisation or '',
                'parties_prenantes': fiche.parties_prenantes or '',
                'autres_projets_connexes': fiche.autres_projets_connexes or '',
                'objectif_projet': fiche.objectif_projet or '',
                'activites_principales': fiche.activites_principales or '',
                'resultats_attendus': fiche.resultats_attendus or '',

                # Section III - Critères d'évaluation
                'criteres': criteres,
                'proposition': fiche.proposition or '',
                'recommandations': fiche.recommandations_generales or '',
                'score_total': fiche.calculer_score_total(),
                'appreciation_globale': fiche.get_appreciation_globale(),
                'date_evaluation': fiche.date_evaluation.isoformat() if fiche.date_evaluation else None,
                'fichier_pdf': fiche.fichier_pdf  # IMPORTANT: Nécessaire pour afficher le bouton PDF dans le frontend
            }
            return jsonify(evaluation_data)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/projects/<int:project_id>/fiche-evaluation/pdf', methods=['GET'])
    def download_fiche_evaluation_pdf(project_id):
        """Route pour télécharger le PDF de la fiche d'évaluation"""
        try:
            fiche = FicheEvaluation.query.filter_by(project_id=project_id).first()
            if not fiche:
                return jsonify({"error": "Fiche d'évaluation non trouvée"}), 404

            if not fiche.fichier_pdf:
                return jsonify({"error": "PDF non disponible pour cette fiche"}), 404

            # Construire le chemin complet vers le fichier PDF
            fiches_folder = os.path.join(app.config["UPLOAD_FOLDER"], "fiches_evaluation")
            pdf_path = os.path.join(fiches_folder, fiche.fichier_pdf)

            # Vérifier que le fichier existe
            if not os.path.exists(pdf_path):
                print(f"[FICHE_PDF] Fichier PDF introuvable: {pdf_path}")
                return jsonify({"error": "Fichier PDF introuvable"}), 404

            # Envoyer le fichier
            from flask import send_file
            return send_file(
                pdf_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=fiche.fichier_pdf
            )
        except Exception as e:
            print(f"[FICHE_PDF] Erreur téléchargement PDF: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route('/api/projects/<int:project_id>/fiche-evaluation', methods=['POST', 'PUT'])
    def save_fiche_evaluation(project_id):
        """Sauvegarde ou met à jour une fiche d'évaluation"""
        try:
            # LOG IMMÉDIAT pour prouver que la fonction est appelée
            import sys
            print(f"[FICHE SAVE] Requête reçue pour projet {project_id}", file=sys.stderr, flush=True)

            data = request.get_json()
            print(f"[FICHE SAVE] Données reçues: {list(data.keys())}", file=sys.stderr, flush=True)

            # Vérifier le rôle de l'utilisateur
            role = data.get("role", "")
            print(f"[FICHE SAVE] Rôle: '{role}'", file=sys.stderr, flush=True)

            # Seuls certains rôles peuvent modifier les fiches d'évaluation
            roles_autorises = ['evaluateur', 'secretariatsct', 'presidencesct', 'presidencecomite', 'admin']
            if role not in roles_autorises:
                print(f"[FICHE SAVE] ❌ ACCÈS REFUSÉ - Rôle '{role}' non autorisé", file=sys.stderr, flush=True)
                return jsonify({"error": "Accès refusé: Vous n'avez pas les permissions pour modifier les fiches d'évaluation"}), 403

            print(f"[FICHE SAVE] ✅ Rôle autorisé, poursuite du traitement", file=sys.stderr, flush=True)

            # Vérifier que le projet existe
            project = Project.query.get_or_404(project_id)

            # Vérifier si la fiche peut être modifiée
            peut, erreur = WorkflowValidator.peut_modifier_fiche_evaluation(project, role)
            if not peut:
                return jsonify({"error": erreur}), 403
            
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

            # SECTION I - Présentation du projet
            fiche.intitule_projet = data.get('intitule', '')
            fiche.sous_secteur = data.get('secteur', '')
            fiche.cout_projet = data.get('cout_estimatif', '')
            fiche.organisme_tutelle = data.get('organisme_tutelle', '')
            # Note: description et poles viennent du projet, pas de la fiche

            # SECTION II - Classification du projet
            fiche.origine_projet = data.get('origine_projet_choix', '')
            fiche.changement_climatique_adaptation = data.get('changement_climatique_adaptation', False)
            fiche.changement_climatique_attenuation = data.get('changement_climatique_attenuation', False)
            fiche.genre = data.get('genre', False)

            # Tableaux détaillés de présentation
            fiche.articulation = data.get('articulation', '')
            fiche.axes = data.get('axes', '')
            fiche.objectifs_strategiques = data.get('objectifs_strategiques', '')
            fiche.odd = data.get('odd', '')
            fiche.duree_analyse = data.get('duree_analyse', '')
            fiche.realisation = data.get('realisation', '')
            fiche.exploitation = data.get('exploitation', '')
            fiche.localisation = data.get('localisation', '')
            fiche.parties_prenantes = data.get('parties_prenantes', '')
            fiche.autres_projets_connexes = data.get('autres_projets_connexes', '')
            fiche.objectif_projet = data.get('objectif_projet', '')
            fiche.activites_principales = data.get('activites_principales', '')
            fiche.resultats_attendus = data.get('resultats_attendus', '')

            # SECTION III - Mettre à jour les critères selon le modèle réel
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
                # IMPORTANT: fiche_data contient les données Section II (tableaux détaillés)
                # car le générateur PDF les cherche dans self.fiche_data.get(...)
                fiche_data = {
                    'id': fiche.id,
                    'evaluateur_nom': fiche.evaluateur_nom,
                    'proposition': fiche.proposition,
                    'recommandations': fiche.recommandations_generales,

                    # Section III - Critères d'évaluation
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
                    },

                    # Section II - Tableaux détaillés (utilisés par le générateur PDF)
                    'articulation': fiche.articulation or '',
                    'axes': fiche.axes or '',
                    'objectifs_strategiques': fiche.objectifs_strategiques or '',
                    'odd': fiche.odd or '',
                    'duree_analyse': fiche.duree_analyse or '',
                    'realisation': fiche.realisation or '',
                    'exploitation': fiche.exploitation or '',
                    'localisation': fiche.localisation or '',
                    'parties_prenantes': fiche.parties_prenantes or '',
                    'autres_projets_connexes': fiche.autres_projets_connexes or '',
                    'objectif_projet': fiche.objectif_projet or '',
                    'activites_principales': fiche.activites_principales or '',
                    'resultats_attendus': fiche.resultats_attendus or ''
                }

                # Préparer project_data avec TOUTES les données (projet + fiche)
                # Le générateur PDF utilise project_data pour les Sections I et II
                project_data = {
                    'id': project.id,
                    'numero_projet': project.numero_projet,
                    'titre': fiche.intitule_projet or project.titre,  # Priorité à la fiche
                    'organisme_tutelle': fiche.organisme_tutelle or project.organisme_tutelle,
                    'cout_estimatif': fiche.cout_projet or project.cout_estimatif,

                    # Section I - Données de la fiche
                    'secteur': fiche.sous_secteur or project.secteur,
                    'poles': project.poles_territoriaux,  # Vient toujours du projet
                    'description': project.description,  # Vient toujours du projet

                    # Section II - Classification (depuis fiche)
                    'origine_projet': {
                        'maturation': fiche.origine_projet == 'maturation' if fiche.origine_projet else False,
                        'offre_spontanee': fiche.origine_projet == 'offre_spontanee' if fiche.origine_projet else False,
                        'autres': fiche.origine_projet == 'autres' if fiche.origine_projet else False
                    },
                    'cc_adaptation': fiche.changement_climatique_adaptation or False,
                    'cc_attenuation': fiche.changement_climatique_attenuation or False,
                    'genre': fiche.genre or False,

                    # Tableaux détaillés (depuis fiche)
                    'articulation': fiche.articulation or '',
                    'axes': fiche.axes or '',
                    'objectifs_strategiques': fiche.objectifs_strategiques or '',
                    'odd': fiche.odd or '',
                    'duree_analyse': fiche.duree_analyse or '',
                    'realisation': fiche.realisation or '',
                    'exploitation': fiche.exploitation or '',
                    'localisation': fiche.localisation or '',
                    'parties_prenantes': fiche.parties_prenantes or '',
                    'autres_projets_connexes': fiche.autres_projets_connexes or '',
                    'objectif_projet': fiche.objectif_projet or '',
                    'activites_principales': fiche.activites_principales or '',
                    'resultats_attendus': fiche.resultats_attendus or ''
                }

                # Répertoire de sortie pour les PDFs - CORRECTION: utiliser UPLOAD_FOLDER
                pdf_directory = os.path.join(app.config["UPLOAD_FOLDER"], 'fiches_evaluation')
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
                'message': 'Fiche d\'évaluation enregistrée avec succès',
                'fiche_id': fiche.id,
                'score_total': fiche.calculer_score_total(),
                'appreciation': fiche.get_appreciation_globale(),
                '_debug_code_version': _MODULE_VERSION,
                '_debug_recommandations_saved': {
                    'pertinence': fiche.pertinence_recommandations[:20] if fiche.pertinence_recommandations else None,
                    'alignement': fiche.alignement_recommandations[:20] if fiche.alignement_recommandations else None
                }
            })
            
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    # Note: la route '/api/users/profile' est définie dans routes/user_routes.py
    # pour centraliser la gestion des utilisateurs et éviter les conflits de route.
    # Si une intégration avec flask-login est nécessaire, elle doit être réalisée
    # dans `routes/user_routes.py` et non ici.