from flask import Blueprint, jsonify
from models import User

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
            "display_name": user.display_name,
            "role": user.role
        }), 200
    except Exception as e:
        print(f"[USER PROFILE] Erreur lors de la récupération du profil: {str(e)}")
        return jsonify({"error": "Erreur lors de la récupération du profil"}), 500
