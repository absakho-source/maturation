from flask import Blueprint, jsonify

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/api/users/profile', methods=['GET'])
def get_user_profile():
    # Exemple de profil utilisateur fictif
    user_profile = {
        'id': 1,
        'username': 'testuser',
        'display_name': 'Test User',
        'role': 'evaluateur'
    }
    return jsonify(user_profile)
