from flask import Blueprint, jsonify, request
from models import User, db
from werkzeug.security import generate_password_hash
import unicodedata

user_bp = Blueprint('user_bp', __name__)

def generer_username(prenom, nom):
    """Génère un username à partir du prénom et nom"""
    premier_prenom = prenom.split()[0].lower()
    nom_lower = nom.lower()
    # Supprimer les accents
    premier_prenom = ''.join(c for c in unicodedata.normalize('NFD', premier_prenom) if unicodedata.category(c) != 'Mn')
    nom_lower = ''.join(c for c in unicodedata.normalize('NFD', nom_lower) if unicodedata.category(c) != 'Mn')
    return f"{premier_prenom}.{nom_lower}"

@user_bp.route('/api/admin/creer-evaluateurs-dgppe', methods=['POST'])
def creer_evaluateurs_dgppe():
    """Crée les comptes évaluateurs DGPPE en masse - Admin uniquement"""
    try:
        # Vérifier le rôle admin
        role = request.headers.get('X-Role', '')
        if role != 'admin':
            return jsonify({'error': 'Accès refusé - Admin uniquement'}), 403

        # Liste des évaluateurs à créer
        evaluateurs = [
            {"prenom": "PAPA BAÏDY", "nom": "SY"},
            {"prenom": "PAPA DETHIÉ", "nom": "DIOUF"},
            {"prenom": "MAMADOU IBRAHIMA", "nom": "MARONE"},
            {"prenom": "SYLEYMANE", "nom": "NIANG"},
            {"prenom": "SULEYMANE", "nom": "HAÏDARA"},
            {"prenom": "MAME SANÉ", "nom": "TOURE"},
            {"prenom": "NDEYE FATOU", "nom": "SARR"},
            {"prenom": "SERIGNE DJIBRIL", "nom": "DIENE"},
            {"prenom": "BABACAR", "nom": "SALL"},
            {"prenom": "KHADY DIOP", "nom": "NDIAYE"},
            {"prenom": "OUSSEYNOU", "nom": "BADIANE"},
            {"prenom": "DEGUÈNE", "nom": "MBODJ"},
            {"prenom": "AMINATA", "nom": "FAYE"},
            {"prenom": "SOKHNA MAR", "nom": "SYLL"},
            {"prenom": "RICHARD", "nom": "TENDENG"},
            {"prenom": "FATOU BAMBA BACHIR", "nom": "MBOW"},
            {"prenom": "OUMAR", "nom": "DIEDHIOU"},
            {"prenom": "FATOU", "nom": "NDIAYE3"},
        ]

        default_password = "Dgppe@2025"
        password_hash = generate_password_hash(default_password)

        comptes_crees = []
        comptes_existants = []

        for eval_data in evaluateurs:
            prenom = eval_data["prenom"]
            nom = eval_data["nom"]

            username = generer_username(prenom, nom)
            email = f"{username}@dgppe.gouv.sn"
            display_name = f"{prenom} {nom}"

            # Vérifier si le compte existe déjà
            existing = User.query.filter_by(username=username).first()
            if existing:
                comptes_existants.append(username)
                continue

            # Créer le compte
            new_user = User(
                username=username,
                email=email,
                password=password_hash,
                role='evaluateur',
                display_name=display_name,
                statut_compte='verifie'
            )
            db.session.add(new_user)
            comptes_crees.append({
                "username": username,
                "email": email,
                "display_name": display_name
            })

        db.session.commit()

        return jsonify({
            'message': f'{len(comptes_crees)} comptes créés avec succès',
            'comptes_crees': comptes_crees,
            'comptes_existants': comptes_existants,
            'mot_de_passe_defaut': default_password
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"[ADMIN] Erreur création évaluateurs: {str(e)}")
        return jsonify({'error': f'Erreur: {str(e)}'}), 500

@user_bp.route('/api/users/<username>/profile', methods=['GET'])
def get_user_profile_by_username(username):
    """Récupère le profil d'un utilisateur par son nom d'utilisateur"""
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        profile_data = {
            "username": user.username,
            "email": user.username,
            "telephone": user.telephone or "",
            "fonction": user.fonction or "",
            "nom_structure": user.nom_structure or "",
            "direction_service": user.direction_service or "",
            "display_name": user.display_name,
            "role": user.role,
            # Champs supplémentaires pour l'organisme de tutelle
            "type_structure": user.type_structure or "",
            "type_institution": user.type_institution or ""
        }

        # DEBUG: Afficher les données retournées
        print(f"[USER PROFILE] Profil retourné pour {username}:")
        print(f"  - type_structure: {profile_data['type_structure']}")
        print(f"  - type_institution: {profile_data['type_institution']}")
        print(f"  - nom_structure: {profile_data['nom_structure']}")
        print(f"  - direction_service: {profile_data['direction_service']}")

        return jsonify(profile_data), 200
    except Exception as e:
        print(f"[USER PROFILE] Erreur lors de la récupération du profil: {str(e)}")
        return jsonify({"error": "Erreur lors de la récupération du profil"}), 500

@user_bp.route('/api/users/<username>/profile', methods=['PUT'])
def update_user_profile(username):
    """Met à jour le profil d'un utilisateur"""
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        data = request.get_json()

        # Mettre à jour les champs modifiables
        if 'email' in data:
            user.username = data['email']  # L'email est le username
        if 'telephone' in data:
            user.telephone = data['telephone']
        if 'fonction' in data:
            user.fonction = data['fonction']

        # Note: nom_structure ne doit PAS être modifiable ici (seulement par admin)

        db.session.commit()

        return jsonify({
            "message": "Profil mis à jour avec succès",
            "user": {
                "username": user.username,
                "telephone": user.telephone,
                "fonction": user.fonction
            }
        }), 200
    except Exception as e:
        print(f"[USER PROFILE] Erreur lors de la mise à jour du profil: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Erreur lors de la mise à jour du profil"}), 500

@user_bp.route('/api/users/<username>/password', methods=['PUT'])
def update_user_password(username):
    """Change le mot de passe d'un utilisateur"""
    try:
        from werkzeug.security import check_password_hash, generate_password_hash

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not old_password or not new_password:
            return jsonify({"error": "Ancien et nouveau mot de passe requis"}), 400

        # Vérifier l'ancien mot de passe
        if not check_password_hash(user.password, old_password):
            return jsonify({"error": "Ancien mot de passe incorrect"}), 400

        # Mettre à jour le mot de passe
        user.password = generate_password_hash(new_password)
        db.session.commit()

        return jsonify({"message": "Mot de passe changé avec succès"}), 200
    except Exception as e:
        print(f"[USER PASSWORD] Erreur lors du changement de mot de passe: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Erreur lors du changement de mot de passe"}), 500
