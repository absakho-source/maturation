"""
Routes pour la gestion du versioning des projets
"""
from flask import Blueprint, jsonify, request
from models import Project, ProjectVersion
from utils.project_versioning import get_project_versions, get_project_version, compare_versions, restore_project_version
from utils.decorators import role_required

versioning_bp = Blueprint('versioning', __name__)


@versioning_bp.route('/api/projects/<int:project_id>/versions', methods=['GET'])
def get_versions(project_id):
    """Récupère toutes les versions d'un projet"""
    try:
        role = request.headers.get('X-Role', '')
        username = request.headers.get('X-Username', '')

        if not role or role == 'invite':
            return jsonify({'error': 'Non autorisé'}), 403

        versions = get_project_versions(project_id)

        return jsonify({
            'versions': versions,
            'total': len(versions)
        }), 200

    except Exception as e:
        print(f"Erreur récupération versions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@versioning_bp.route('/api/projects/versions/<int:version_id>', methods=['GET'])
def get_version_detail(version_id):
    """Récupère les détails d'une version spécifique"""
    try:
        role = request.headers.get('X-Role', '')

        if not role or role == 'invite':
            return jsonify({'error': 'Non autorisé'}), 403

        version = get_project_version(version_id)

        if not version:
            return jsonify({'error': 'Version non trouvée'}), 404

        return jsonify(version), 200

    except Exception as e:
        print(f"Erreur récupération version: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@versioning_bp.route('/api/projects/versions/compare', methods=['POST'])
def compare_project_versions():
    """Compare deux versions d'un projet"""
    try:
        role = request.headers.get('X-Role', '')

        if not role or role == 'invite':
            return jsonify({'error': 'Non autorisé'}), 403

        data = request.json
        version_id_1 = data.get('version_id_1')
        version_id_2 = data.get('version_id_2')

        if not version_id_1 or not version_id_2:
            return jsonify({'error': 'Les deux IDs de version sont requis'}), 400

        comparison = compare_versions(version_id_1, version_id_2)

        if not comparison:
            return jsonify({'error': 'Impossible de comparer les versions'}), 404

        return jsonify(comparison), 200

    except Exception as e:
        print(f"Erreur comparaison versions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@versioning_bp.route('/api/projects/<int:project_id>/restore/<int:version_id>', methods=['POST'])
def restore_version(project_id, version_id):
    """Restaure un projet à une version antérieure"""
    try:
        role = request.headers.get('X-Role', '')
        username = request.headers.get('X-Username', '')

        # Seuls les admins et le secrétariat peuvent restaurer
        if role not in ['admin', 'secretariatsct']:
            return jsonify({'error': 'Non autorisé - Réservé aux administrateurs'}), 403

        success = restore_project_version(project_id, version_id, username)

        if success:
            return jsonify({
                'message': 'Projet restauré avec succès',
                'project_id': project_id,
                'restored_from_version': version_id
            }), 200
        else:
            return jsonify({'error': 'Échec de la restauration'}), 500

    except Exception as e:
        print(f"Erreur restauration version: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
