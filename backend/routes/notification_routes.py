from flask import Blueprint, jsonify, request
from models import Notification, User, Project
from db import db
from datetime import datetime

notification_bp = Blueprint('notifications', __name__)


@notification_bp.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Récupère les notifications d'un utilisateur"""
    username = request.args.get('username')
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    limit = request.args.get('limit', 50, type=int)

    if not username:
        return jsonify({"error": "Username requis"}), 400

    # Trouver l'utilisateur
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404

    # Construire la requête
    query = Notification.query.filter_by(user_id=user.id)

    if unread_only:
        query = query.filter_by(lu=False)

    # Trier par date décroissante et limiter
    notifications = query.order_by(Notification.date_creation.desc()).limit(limit).all()

    return jsonify([n.to_dict() for n in notifications]), 200


@notification_bp.route('/api/notifications/count', methods=['GET'])
def get_notification_count():
    """Récupère le nombre de notifications non lues"""
    username = request.args.get('username')

    if not username:
        return jsonify({"error": "Username requis"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404

    count = Notification.query.filter_by(user_id=user.id, lu=False).count()

    return jsonify({"count": count}), 200


@notification_bp.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    """Marque une notification comme lue"""
    notification = Notification.query.get(notification_id)

    if not notification:
        return jsonify({"error": "Notification non trouvée"}), 404

    notification.lu = True
    notification.date_lecture = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "Notification marquée comme lue"}), 200


@notification_bp.route('/api/notifications/read-all', methods=['PUT'])
def mark_all_notifications_read():
    """Marque toutes les notifications d'un utilisateur comme lues"""
    username = request.json.get('username') if request.json else None

    if not username:
        return jsonify({"error": "Username requis"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404

    # Marquer toutes comme lues
    Notification.query.filter_by(user_id=user.id, lu=False).update({
        'lu': True,
        'date_lecture': datetime.utcnow()
    })
    db.session.commit()

    return jsonify({"message": "Toutes les notifications marquées comme lues"}), 200


@notification_bp.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """Supprime une notification"""
    notification = Notification.query.get(notification_id)

    if not notification:
        return jsonify({"error": "Notification non trouvée"}), 404

    db.session.delete(notification)
    db.session.commit()

    return jsonify({"message": "Notification supprimée"}), 200


# ============ FONCTIONS UTILITAIRES POUR CRÉER DES NOTIFICATIONS ============

def create_notification(user_id, type, titre, message, project_id=None, lien=None, priorite_email=False):
    """
    Crée une nouvelle notification

    Types disponibles:
    - 'statut_change': Changement de statut du projet
    - 'nouveau_message': Nouveau message dans le chat
    - 'complement_requis': Compléments demandés
    - 'avis_rendu': Avis rendu sur le projet
    - 'document_ajoute': Nouveau document ajouté
    - 'assignation': Projet assigné à l'évaluateur
    - 'evaluation': Évaluation soumise
    - 'validation': Projet validé par secrétariat
    """
    notification = Notification(
        user_id=user_id,
        project_id=project_id,
        type=type,
        titre=titre,
        message=message,
        lien=lien,
        priorite_email=priorite_email
    )
    db.session.add(notification)
    db.session.commit()

    return notification


def notify_user_by_username(username, type, titre, message, project_id=None, lien=None, priorite_email=False):
    """Crée une notification pour un utilisateur par son username"""
    user = User.query.filter_by(username=username).first()
    if user:
        return create_notification(user.id, type, titre, message, project_id, lien, priorite_email)
    return None


def notify_users_by_role(role, type, titre, message, project_id=None, lien=None, priorite_email=False):
    """Crée des notifications pour tous les utilisateurs d'un rôle donné"""
    users = User.query.filter_by(role=role).all()
    notifications = []
    for user in users:
        notif = create_notification(user.id, type, titre, message, project_id, lien, priorite_email)
        notifications.append(notif)
    return notifications


def notify_project_owner(project_id, type, titre, message, lien=None, priorite_email=False):
    """Notifie le propriétaire d'un projet"""
    project = Project.query.get(project_id)
    if project and project.soumissionnaire_id:
        return create_notification(
            project.soumissionnaire_id, type, titre, message,
            project_id, lien, priorite_email
        )
    return None
