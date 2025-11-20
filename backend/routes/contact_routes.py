from flask import Blueprint, jsonify, request
from models import ContactMessage, User, Notification
from db import db
from datetime import datetime
import re

contact_bp = Blueprint('contact', __name__)


@contact_bp.route('/api/contact', methods=['POST'])
def submit_contact():
    """Soumettre un message de contact"""
    try:
        data = request.json or {}

        # Validation des champs requis
        nom = (data.get('nom') or '').strip()
        email = (data.get('email') or '').strip()
        objet = (data.get('objet') or '').strip()
        message = (data.get('message') or '').strip()

        if not nom or not email or not objet or not message:
            return jsonify({"error": "Tous les champs obligatoires doivent être remplis"}), 400

        # Validation email basique
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return jsonify({"error": "Adresse email invalide"}), 400

        # Validation captcha simple (somme)
        captcha_reponse = data.get('captcha_reponse')
        captcha_attendu = data.get('captcha_attendu')
        if captcha_reponse != captcha_attendu:
            return jsonify({"error": "Réponse au captcha incorrecte"}), 400

        # Créer le message de contact
        contact = ContactMessage(
            nom=nom,
            email=email,
            telephone=(data.get('telephone') or '').strip() or None,
            objet=objet,
            message=message,
            user_id=data.get('user_id'),
            username=data.get('username'),
            ip_address=request.remote_addr
        )

        db.session.add(contact)
        db.session.commit()

        # Notifier selon l'objet du message
        try:
            # Déterminer les destinataires selon l'objet
            if objet == "Problème technique":
                # Problème technique → admin + secrétariat
                roles_to_notify = ['admin', 'secretariatsct']
            elif objet == "Autre":
                # Autre → admin + secrétariat
                roles_to_notify = ['admin', 'secretariatsct']
            else:
                # Demande d'information, Question sur la soumission, Demande de compte → secrétariat
                roles_to_notify = ['secretariatsct']

            for role in roles_to_notify:
                users = User.query.filter_by(role=role).all()
                for user in users:
                    notification = Notification(
                        user_id=user.id,
                        type='nouveau_message',
                        titre='Nouveau message de contact',
                        message=f"Message de {nom} - Objet: {objet}",
                        lien='/gestion-comptes',  # Page accessible aux admin/secrétariat
                        priorite_email=True
                    )
                    db.session.add(notification)
            db.session.commit()
        except Exception as e:
            print(f"[CONTACT] Erreur notification: {e}")

        return jsonify({
            "message": "Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.",
            "id": contact.id
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@contact_bp.route('/api/contact/messages', methods=['GET'])
def get_contact_messages():
    """Récupère tous les messages de contact (pour admin/secrétariat)"""
    try:
        role = request.args.get('role', '')
        if role not in ['admin', 'secretariatsct']:
            return jsonify({"error": "Accès non autorisé"}), 403

        statut = request.args.get('statut')
        query = ContactMessage.query

        if statut:
            query = query.filter_by(statut=statut)

        messages = query.order_by(ContactMessage.date_creation.desc()).all()
        return jsonify([m.to_dict() for m in messages]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@contact_bp.route('/api/contact/messages/<int:message_id>', methods=['GET'])
def get_contact_message(message_id):
    """Récupère un message de contact spécifique"""
    try:
        message = ContactMessage.query.get_or_404(message_id)

        # Marquer comme lu si nouveau
        if message.statut == 'nouveau':
            message.statut = 'lu'
            message.date_lecture = datetime.utcnow()
            db.session.commit()

        return jsonify(message.to_dict()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@contact_bp.route('/api/contact/messages/<int:message_id>', methods=['PUT'])
def update_contact_message(message_id):
    """Met à jour le statut d'un message de contact"""
    try:
        message = ContactMessage.query.get_or_404(message_id)
        data = request.json or {}

        if 'statut' in data:
            message.statut = data['statut']
        if 'traite_par' in data:
            message.traite_par = data['traite_par']
        if 'reponse' in data:
            message.reponse = data['reponse']

        db.session.commit()
        return jsonify({"message": "Message mis à jour"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@contact_bp.route('/api/contact/messages/<int:message_id>', methods=['DELETE'])
def delete_contact_message(message_id):
    """Supprime un message de contact"""
    try:
        message = ContactMessage.query.get_or_404(message_id)
        db.session.delete(message)
        db.session.commit()
        return jsonify({"message": "Message supprimé"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@contact_bp.route('/api/contact/count', methods=['GET'])
def get_unread_contact_count():
    """Compte les messages non lus"""
    try:
        count = ContactMessage.query.filter_by(statut='nouveau').count()
        return jsonify({"count": count}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
