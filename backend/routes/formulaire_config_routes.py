"""
Routes pour la gestion de la configuration du formulaire d'évaluation
Accessible uniquement par les admins et secretariatsct
"""

from flask import Blueprint, request, jsonify
from models import db, FormulaireConfig, SectionFormulaire, ChampFormulaire, CritereEvaluation
from datetime import datetime
import json

formulaire_config_bp = Blueprint('formulaire_config', __name__)

def check_admin_access(username, role):
    """Vérifie que l'utilisateur a les droits d'admin ou secretariatsct"""
    if role not in ['admin', 'secretariatsct']:
        return False, jsonify({'error': 'Accès non autorisé. Réservé aux administrateurs et secrétariat SCT.'}), 403
    return True, None, None

@formulaire_config_bp.route('/api/formulaire-config', methods=['GET'])
def get_configurations():
    """Récupère toutes les configurations"""
    try:
        configs = FormulaireConfig.query.order_by(FormulaireConfig.date_creation.desc()).all()
        return jsonify([c.to_dict() for c in configs]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@formulaire_config_bp.route('/api/formulaire-config/active', methods=['GET'])
def get_active_configuration():
    """Récupère la configuration active"""
    try:
        config = FormulaireConfig.query.filter_by(active=True).first()
        if not config:
            return jsonify({'error': 'Aucune configuration active'}), 404
        return jsonify(config.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@formulaire_config_bp.route('/api/formulaire-config/<int:config_id>', methods=['GET'])
def get_configuration(config_id):
    """Récupère une configuration spécifique"""
    try:
        config = FormulaireConfig.query.get_or_404(config_id)
        return jsonify(config.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@formulaire_config_bp.route('/api/formulaire-config', methods=['POST'])
def create_configuration():
    """Crée une nouvelle configuration"""
    try:
        # Vérifier les permissions
        data = request.json
        username = data.get('username')
        role = data.get('role')

        is_authorized, error_response, status_code = check_admin_access(username, role)
        if not is_authorized:
            return error_response, status_code

        # Créer la nouvelle configuration
        config = FormulaireConfig(
            nom=data.get('nom'),
            version=data.get('version'),
            description=data.get('description'),
            score_total_max=data.get('score_total_max', 100),
            seuil_favorable=data.get('seuil_favorable', 80),
            seuil_conditionnel=data.get('seuil_conditionnel', 70),
            active=False,  # Nouvelle config pas active par défaut
            modifie_par=username
        )

        db.session.add(config)
        db.session.commit()

        return jsonify(config.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@formulaire_config_bp.route('/api/formulaire-config/<int:config_id>', methods=['PUT'])
def update_configuration(config_id):
    """Met à jour une configuration"""
    try:
        data = request.json
        username = data.get('username')
        role = data.get('role')

        is_authorized, error_response, status_code = check_admin_access(username, role)
        if not is_authorized:
            return error_response, status_code

        config = FormulaireConfig.query.get_or_404(config_id)

        # Mettre à jour les champs
        if 'nom' in data:
            config.nom = data['nom']
        if 'version' in data:
            config.version = data['version']
        if 'version_affichage' in data:
            config.version_affichage = data['version_affichage']
        if 'description' in data:
            config.description = data['description']
        if 'score_total_max' in data:
            config.score_total_max = data['score_total_max']
        if 'seuil_favorable' in data:
            config.seuil_favorable = data['seuil_favorable']
        if 'seuil_conditionnel' in data:
            config.seuil_conditionnel = data['seuil_conditionnel']

        config.date_modification = datetime.utcnow()
        config.modifie_par = username

        db.session.commit()

        return jsonify(config.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@formulaire_config_bp.route('/api/formulaire-config/<int:config_id>/activer', methods=['POST'])
def activer_configuration(config_id):
    """Active une configuration (désactive les autres)"""
    try:
        data = request.json
        username = data.get('username')
        role = data.get('role')

        is_authorized, error_response, status_code = check_admin_access(username, role)
        if not is_authorized:
            return error_response, status_code

        # Désactiver toutes les configs
        FormulaireConfig.query.update({'active': False})

        # Activer celle-ci
        config = FormulaireConfig.query.get_or_404(config_id)
        config.active = True
        config.date_modification = datetime.utcnow()
        config.modifie_par = username

        db.session.commit()
        return jsonify(config.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@formulaire_config_bp.route('/api/formulaire-config/<int:config_id>', methods=['DELETE'])
def delete_configuration(config_id):
    """Supprime une configuration (si elle n'est pas active)"""
    try:
        data = request.json
        username = data.get('username')
        role = data.get('role')

        is_authorized, error_response, status_code = check_admin_access(username, role)
        if not is_authorized:
            return error_response, status_code

        config = FormulaireConfig.query.get_or_404(config_id)

        if config.active:
            return jsonify({'error': 'Impossible de supprimer une configuration active'}), 400

        db.session.delete(config)
        db.session.commit()
        return jsonify({'message': 'Configuration supprimée'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Routes pour les sections
@formulaire_config_bp.route('/api/formulaire-config/<int:config_id>/sections', methods=['POST'])
def create_section(config_id):
    """Crée une nouvelle section dans une configuration"""
    try:
        data = request.json
        username = data.get('username')
        role = data.get('role')

        is_authorized, error_response, status_code = check_admin_access(username, role)
        if not is_authorized:
            return error_response, status_code

        config = FormulaireConfig.query.get_or_404(config_id)

        section = SectionFormulaire(
            config_id=config_id,
            titre=data.get('titre'),
            numero=data.get('numero'),
            ordre=data.get('ordre'),
            type_section=data.get('type_section'),
            editable=data.get('editable', True)
        )

        db.session.add(section)
        db.session.commit()

        return jsonify(section.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@formulaire_config_bp.route('/api/section/<int:section_id>', methods=['PUT'])
def update_section(section_id):
    """Met à jour une section"""
    try:
        data = request.json
        username = data.get('username')
        role = data.get('role')

        is_authorized, error_response, status_code = check_admin_access(username, role)
        if not is_authorized:
            return error_response, status_code

        section = SectionFormulaire.query.get_or_404(section_id)

        if 'titre' in data:
            section.titre = data['titre']
        if 'numero' in data:
            section.numero = data['numero']
        if 'ordre' in data:
            section.ordre = data['ordre']
        if 'type_section' in data:
            section.type_section = data['type_section']
        if 'editable' in data:
            section.editable = data['editable']

        db.session.commit()
        return jsonify(section.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@formulaire_config_bp.route('/api/section/<int:section_id>', methods=['DELETE'])
def delete_section(section_id):
    """Supprime une section"""
    try:
        data = request.json
        username = data.get('username')
        role = data.get('role')

        is_authorized, error_response, status_code = check_admin_access(username, role)
        if not is_authorized:
            return error_response, status_code

        section = SectionFormulaire.query.get_or_404(section_id)
        db.session.delete(section)
        db.session.commit()

        return jsonify({'message': 'Section supprimée'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Routes pour les champs
@formulaire_config_bp.route('/api/section/<int:section_id>/champs', methods=['POST'])
def create_champ(section_id):
    """Crée un nouveau champ dans une section"""
    try:
        data = request.json
        username = data.get('username')
        role = data.get('role')

        is_authorized, error_response, status_code = check_admin_access(username, role)
        if not is_authorized:
            return error_response, status_code

        section = SectionFormulaire.query.get_or_404(section_id)

        # Convertir les options en JSON si nécessaire
        options = data.get('options')
        if options and isinstance(options, (list, dict)):
            options = json.dumps(options)

        champ = ChampFormulaire(
            section_id=section_id,
            libelle=data.get('libelle'),
            cle=data.get('cle'),
            type_champ=data.get('type_champ'),
            ordre=data.get('ordre'),
            obligatoire=data.get('obligatoire', False),
            largeur=data.get('largeur', 'full'),
            options=options,
            valeur_defaut=data.get('valeur_defaut'),
            aide=data.get('aide'),
            lecture_seule=data.get('lecture_seule', False)
        )

        db.session.add(champ)
        db.session.commit()

        return jsonify(champ.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@formulaire_config_bp.route('/api/champ/<int:champ_id>', methods=['PUT'])
def update_champ(champ_id):
    """Met à jour un champ"""
    try:
        data = request.json
        username = data.get('username')
        role = data.get('role')

        is_authorized, error_response, status_code = check_admin_access(username, role)
        if not is_authorized:
            return error_response, status_code

        champ = ChampFormulaire.query.get_or_404(champ_id)

        if 'libelle' in data:
            champ.libelle = data['libelle']
        if 'cle' in data:
            champ.cle = data['cle']
        if 'type_champ' in data:
            champ.type_champ = data['type_champ']
        if 'ordre' in data:
            champ.ordre = data['ordre']
        if 'obligatoire' in data:
            champ.obligatoire = data['obligatoire']
        if 'largeur' in data:
            champ.largeur = data['largeur']
        if 'options' in data:
            options = data['options']
            if isinstance(options, (list, dict)):
                options = json.dumps(options)
            champ.options = options
        if 'valeur_defaut' in data:
            champ.valeur_defaut = data['valeur_defaut']
        if 'aide' in data:
            champ.aide = data['aide']
        if 'lecture_seule' in data:
            champ.lecture_seule = data['lecture_seule']

        db.session.commit()
        return jsonify(champ.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@formulaire_config_bp.route('/api/champ/<int:champ_id>', methods=['DELETE'])
def delete_champ(champ_id):
    """Supprime un champ"""
    try:
        data = request.json
        username = data.get('username')
        role = data.get('role')

        is_authorized, error_response, status_code = check_admin_access(username, role)
        if not is_authorized:
            return error_response, status_code

        champ = ChampFormulaire.query.get_or_404(champ_id)
        db.session.delete(champ)
        db.session.commit()

        return jsonify({'message': 'Champ supprimé'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Routes pour les critères
@formulaire_config_bp.route('/api/section/<int:section_id>/criteres', methods=['POST'])
def create_critere(section_id):
    """Crée un nouveau critère dans une section"""
    try:
        data = request.json
        username = data.get('username')
        role = data.get('role')

        is_authorized, error_response, status_code = check_admin_access(username, role)
        if not is_authorized:
            return error_response, status_code

        section = SectionFormulaire.query.get_or_404(section_id)

        critere = CritereEvaluation(
            section_id=section_id,
            nom=data.get('nom'),
            cle=data.get('cle'),
            description_aide=data.get('description_aide'),
            score_max=data.get('score_max'),
            ordre=data.get('ordre'),
            avec_description=data.get('avec_description', True),
            avec_recommandations=data.get('avec_recommandations', False)
        )

        db.session.add(critere)
        db.session.commit()

        return jsonify(critere.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@formulaire_config_bp.route('/api/critere/<int:critere_id>', methods=['PUT'])
def update_critere(critere_id):
    """Met à jour un critère"""
    try:
        data = request.json
        username = data.get('username')
        role = data.get('role')

        is_authorized, error_response, status_code = check_admin_access(username, role)
        if not is_authorized:
            return error_response, status_code

        critere = CritereEvaluation.query.get_or_404(critere_id)

        if 'nom' in data:
            critere.nom = data['nom']
        if 'cle' in data:
            critere.cle = data['cle']
        if 'description_aide' in data:
            critere.description_aide = data['description_aide']
        if 'score_max' in data:
            critere.score_max = data['score_max']
        if 'ordre' in data:
            critere.ordre = data['ordre']
        if 'avec_description' in data:
            critere.avec_description = data['avec_description']
        if 'avec_recommandations' in data:
            critere.avec_recommandations = data['avec_recommandations']

        db.session.commit()
        return jsonify(critere.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@formulaire_config_bp.route('/api/critere/<int:critere_id>', methods=['DELETE'])
def delete_critere(critere_id):
    """Supprime un critère"""
    try:
        data = request.json
        username = data.get('username')
        role = data.get('role')

        is_authorized, error_response, status_code = check_admin_access(username, role)
        if not is_authorized:
            return error_response, status_code

        critere = CritereEvaluation.query.get_or_404(critere_id)
        db.session.delete(critere)
        db.session.commit()

        return jsonify({'message': 'Critère supprimé'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@formulaire_config_bp.route('/api/formulaire-config/preview-pdf', methods=['POST'])
def preview_pdf():
    """Génère un PDF de prévisualisation du formulaire vide avec la configuration actuelle"""
    try:
        from flask import send_file
        from io import BytesIO
        import sys
        import os

        # Ajouter le dossier backend au path pour importer le générateur
        backend_path = os.path.dirname(os.path.dirname(__file__))
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        from pdf_generator_dgppe import FicheEvaluationDGPPEPDF

        data = request.json
        username = data.get('username')
        role = data.get('role')
        config_id = data.get('config_id')

        is_authorized, error_response, status_code = check_admin_access(username, role)
        if not is_authorized:
            return error_response, status_code

        # Récupérer la configuration
        config = FormulaireConfig.query.get_or_404(config_id)

        # Créer des données vides pour la fiche d'évaluation
        # Structure conforme à EvaluationDetaillee.vue
        fiche_data_vide = {
            'reference_fiche': '[Référence]',
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
            'criteres': {
                'pertinence': {'score': 0, 'description': '', 'recommandations': ''},
                'alignement': {'score': 0, 'description': '', 'recommandations': ''},
                'activites_couts': {'score': 0, 'description': '', 'recommandations': ''},
                'equite': {'score': 0, 'description': '', 'recommandations': ''},
                'viabilite': {'score': 0, 'description': '', 'recommandations': ''},
                'rentabilite': {'score': 0, 'description': '', 'recommandations': ''},
                'benefices_strategiques': {'score': 0, 'description': '', 'recommandations': ''},
                'perennite': {'score': 0, 'description': '', 'recommandations': ''},
                'avantages_intangibles': {'score': 0, 'description': '', 'recommandations': ''},
                'faisabilite': {'score': 0, 'description': '', 'recommandations': ''},
                'ppp': {'score': 0, 'description': '', 'recommandations': ''},
                'impact_environnemental': {'score': 0, 'description': '', 'recommandations': ''},
                'impact_emploi': {'score': 0, 'description': '', 'recommandations': ''}
            },
            'recommandations': '[Recommandations finales]'
        }

        # Données projet vides
        project_data_vide = {
            'id': 'XXX',
            'numero_projet': '[Numéro]',
            'titre': '[Titre du projet - Exemple de prévisualisation]',
            'secteur': '[Secteur de planification]',
            'poles': '[Pôles territoriaux]',
            'cout_estimatif': 1000000000,
            'organisme_tutelle': "MINISTÈRE DE L'ÉCONOMIE, DU PLAN ET DE LA COOPÉRATION",
            'description': '[Description du projet - Cette section contiendra une description détaillée du projet d\'investissement]'
        }

        # Créer un fichier temporaire pour le PDF
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.pdf', delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Utiliser la méthode generate() du générateur avec la version
            pdf_generator = FicheEvaluationDGPPEPDF(
                fiche_data_vide,
                project_data_vide,
                tmp_path,
                version_affichage=config.version_affichage
            )
            pdf_generator.generate()

            # Lire le fichier et l'envoyer
            return send_file(
                tmp_path,
                mimetype='application/pdf',
                as_attachment=False,
                download_name='fiche_evaluation_vide.pdf'
            )
        finally:
            # Nettoyer le fichier temporaire après l'envoi
            import time
            import threading
            def cleanup_after_delay():
                time.sleep(2)
                try:
                    os.unlink(tmp_path)
                except:
                    pass
            threading.Thread(target=cleanup_after_delay, daemon=True).start()
    except Exception as e:
        print(f"Erreur génération PDF preview: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
