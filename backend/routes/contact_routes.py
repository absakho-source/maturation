from flask import Blueprint, jsonify, request, current_app
from models import ContactMessage, User, Notification
from db import db
from datetime import datetime
import re
import os
import json
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

contact_bp = Blueprint('contact', __name__)


def get_smtp_config():
    """Récupérer la configuration SMTP"""
    return {
        'host': os.environ.get('SMTP_HOST', 'smtp.gmail.com'),
        'port': int(os.environ.get('SMTP_PORT', 587)),
        'user': os.environ.get('SMTP_USER', ''),
        'password': os.environ.get('SMTP_PASSWORD', ''),
        'contact_email': os.environ.get('CONTACT_EMAIL', '')  # Email dédié pour recevoir les messages
    }


def send_new_message_notification(contact_message):
    """Envoyer le nouveau message de contact à l'email dédié"""
    try:
        config = get_smtp_config()
        if not config['user'] or not config['password']:
            print("[EMAIL] Configuration SMTP manquante")
            return False

        # Email de destination (soit CONTACT_EMAIL, soit SMTP_USER)
        to_email = config['contact_email'] or config['user']

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[PLASMAP Contact] {contact_message.objet} - de {contact_message.nom}"
        msg['From'] = f"PLASMAP Contact <{config['user']}>"
        msg['To'] = to_email
        msg['Reply-To'] = contact_message.email

        # Version texte
        text_content = f"""
Nouveau message de contact PLASMAP

De: {contact_message.nom}
Email: {contact_message.email}
Téléphone: {contact_message.telephone or 'Non renseigné'}
Objet: {contact_message.objet}

Message:
{contact_message.message}

---
Reçu le {contact_message.date_creation.strftime('%d/%m/%Y à %H:%M')}
"""

        # Version HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #1e3a8a; color: white; padding: 15px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f8fafc; padding: 20px; border: 1px solid #e2e8f0; }}
        .info-row {{ margin: 8px 0; }}
        .label {{ font-weight: bold; color: #1e40af; }}
        .message-box {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #3b82f6; white-space: pre-wrap; }}
        .footer {{ text-align: center; padding: 10px; font-size: 11px; color: #64748b; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h3 style="margin: 0;">Nouveau message de contact</h3>
        </div>
        <div class="content">
            <div class="info-row"><span class="label">De:</span> {contact_message.nom}</div>
            <div class="info-row"><span class="label">Email:</span> <a href="mailto:{contact_message.email}">{contact_message.email}</a></div>
            <div class="info-row"><span class="label">Téléphone:</span> {contact_message.telephone or 'Non renseigné'}</div>
            <div class="info-row"><span class="label">Objet:</span> {contact_message.objet}</div>

            <div class="message-box">{contact_message.message}</div>
        </div>
        <div class="footer">
            Reçu le {contact_message.date_creation.strftime('%d/%m/%Y à %H:%M')}
        </div>
    </div>
</body>
</html>
"""

        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP(config['host'], config['port']) as server:
            server.starttls()
            server.login(config['user'], config['password'])
            server.send_message(msg)

        print(f"[EMAIL] Notification nouveau message envoyée à {to_email}")
        return True

    except Exception as e:
        print(f"[EMAIL] Erreur envoi notification: {e}")
        return False


def send_response_email(to_email, to_name, subject, original_message, response_text, responder_name):
    """Envoyer la réponse par email au demandeur"""
    try:
        config = get_smtp_config()
        smtp_host = config['host']
        smtp_port = config['port']
        smtp_user = config['user']
        smtp_password = config['password']

        if not smtp_user or not smtp_password:
            print("[EMAIL] Configuration SMTP manquante")
            return False

        # Créer le message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Réponse à votre demande: {subject}"
        msg['From'] = f"PLASMAP - SCT <{smtp_user}>"
        msg['To'] = to_email

        # Version texte
        text_content = f"""
Bonjour {to_name},

Nous avons bien reçu votre message concernant: {subject}

--- Votre message ---
{original_message}

--- Notre réponse ---
{response_text}

Cordialement,
{responder_name}
Secrétariat du Comité de Technique
PLASMAP - Plateforme de Soumission des Projets de Maturation
"""

        # Version HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #1e3a8a; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f8fafc; padding: 20px; border: 1px solid #e2e8f0; }}
        .message-box {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #3b82f6; }}
        .response-box {{ background: #ecfdf5; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #10b981; }}
        .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #64748b; }}
        .label {{ font-weight: bold; color: #1e40af; margin-bottom: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2 style="margin: 0;">PLASMAP</h2>
            <p style="margin: 5px 0 0 0; font-size: 14px;">Plateforme de Soumission des Projets de Maturation</p>
        </div>
        <div class="content">
            <p>Bonjour <strong>{to_name}</strong>,</p>
            <p>Nous avons bien reçu votre message et y avons apporté une réponse.</p>

            <div class="label">Objet: {subject}</div>

            <div class="message-box">
                <div class="label">Votre message:</div>
                <p style="margin: 0; white-space: pre-wrap;">{original_message}</p>
            </div>

            <div class="response-box">
                <div class="label">Notre réponse:</div>
                <p style="margin: 0; white-space: pre-wrap;">{response_text}</p>
            </div>

            <p>Cordialement,<br><strong>{responder_name}</strong><br>Secrétariat du Comité Technique</p>
        </div>
        <div class="footer">
            <p>DGPPE - Direction Générale de la Planification et des Politiques Économiques</p>
            <p>Cet email a été envoyé automatiquement, merci de ne pas y répondre directement.</p>
        </div>
    </div>
</body>
</html>
"""

        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        # Envoyer l'email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        print(f"[EMAIL] Réponse envoyée à {to_email}")
        return True

    except Exception as e:
        print(f"[EMAIL] Erreur envoi: {e}")
        return False


@contact_bp.route('/api/contact', methods=['POST'])
def submit_contact():
    """Soumettre un message de contact"""
    try:
        # Gérer FormData ou JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form.to_dict()
        else:
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

        # Convertir en entiers pour comparaison
        try:
            captcha_reponse = int(captcha_reponse) if captcha_reponse else None
            captcha_attendu = int(captcha_attendu) if captcha_attendu else None
        except (ValueError, TypeError):
            return jsonify({"error": "Réponse au captcha invalide"}), 400

        if captcha_reponse != captcha_attendu:
            return jsonify({"error": "Réponse au captcha incorrecte"}), 400

        # Gérer les pièces jointes
        pieces_jointes_paths = []
        if 'pieces_jointes' in request.files:
            files = request.files.getlist('pieces_jointes')

            # Utiliser le UPLOAD_FOLDER configuré dans l'app
            base_upload = current_app.config.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads'))
            upload_folder = os.path.join(base_upload, 'contact')
            os.makedirs(upload_folder, exist_ok=True)

            for file in files:
                if file and file.filename:
                    # Sécuriser le nom de fichier
                    filename = secure_filename(file.filename)
                    # Ajouter timestamp pour unicité
                    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                    unique_filename = f"{timestamp}_{filename}"
                    filepath = os.path.join(upload_folder, unique_filename)
                    file.save(filepath)
                    pieces_jointes_paths.append(f"contact/{unique_filename}")

        # Créer le message de contact
        user_id = data.get('user_id')
        if user_id == '' or user_id == 'null':
            user_id = None
        else:
            try:
                user_id = int(user_id) if user_id else None
            except (ValueError, TypeError):
                user_id = None

        contact = ContactMessage(
            nom=nom,
            email=email,
            telephone=(data.get('telephone') or '').strip() or None,
            objet=objet,
            message=message,
            user_id=user_id,
            username=data.get('username') if data.get('username') else None,
            ip_address=request.remote_addr,
            pieces_jointes=json.dumps(pieces_jointes_paths) if pieces_jointes_paths else None
        )

        db.session.add(contact)
        db.session.commit()

        # Envoyer le message à l'email dédié
        email_sent = send_new_message_notification(contact)
        if email_sent:
            print(f"[CONTACT] Message {contact.id} envoyé par email")
        else:
            print(f"[CONTACT] Message {contact.id} enregistré (email non envoyé)")

        # Notifier selon l'objet du message (notifications sur la plateforme)
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
            message.date_reponse = datetime.utcnow()

            # Envoyer la réponse par email
            email_sent = send_response_email(
                to_email=message.email,
                to_name=message.nom,
                subject=message.objet,
                original_message=message.message,
                response_text=data['reponse'],
                responder_name=data.get('traite_par', 'Secrétariat SCT')
            )

            if not email_sent:
                print(f"[CONTACT] Email non envoyé pour message {message_id} - config SMTP manquante")

        if 'assigne_a' in data:
            message.assigne_a = data['assigne_a']
            message.date_assignation = datetime.utcnow()

        db.session.commit()

        # Retourner un message approprié
        response_msg = "Message mis à jour"
        if 'reponse' in data:
            response_msg = "Réponse enregistrée et envoyée par email" if email_sent else "Réponse enregistrée (email non envoyé - config SMTP manquante)"

        return jsonify({"message": response_msg, "email_sent": email_sent if 'reponse' in data else None}), 200

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
