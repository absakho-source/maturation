from flask import Blueprint, jsonify, request
from models import User, db

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/api/users/<username>/profile', methods=['GET'])
def get_user_profile_by_username(username):
    """Récupère le profil d'un utilisateur par son nom d'utilisateur"""
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        return jsonify({
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
        }), 200
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
