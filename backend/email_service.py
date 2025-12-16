#!/usr/bin/env python3
"""
Service d'envoi d'emails pour la plateforme de maturation
Gère les notifications automatiques aux soumissionnaires
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Import de la DB pour charger les templates
# On importe ici au lieu du début pour éviter les dépendances circulaires
_db = None
_EmailTemplate = None

def _get_db():
    """Lazy import de la DB pour éviter les dépendances circulaires"""
    global _db, _EmailTemplate
    if _db is None:
        from db import db as _db_import
        from models import EmailTemplate as _EmailTemplate_import
        _db = _db_import
        _EmailTemplate = _EmailTemplate_import
    return _db, _EmailTemplate

# Configuration SMTP (à définir dans les variables d'environnement)
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@dgppe.sn')
FROM_NAME = os.environ.get('FROM_NAME', 'Plateforme DGPPE')
EMAIL_ENABLED = os.environ.get('EMAIL_ENABLED', 'false').lower() == 'true'
EMAIL_DEBUG_MODE = os.environ.get('EMAIL_DEBUG_MODE', 'false').lower() == 'true'

# URL de la plateforme
PLATFORM_URL = os.environ.get('PLATFORM_URL', 'https://maturation-dgppe.onrender.com')

# Log de debug pour vérifier le chargement des variables
print(f"[EMAIL_CONFIG] EMAIL_ENABLED={EMAIL_ENABLED}, SMTP_SERVER={SMTP_SERVER}, SMTP_USERNAME={SMTP_USERNAME[:10] if SMTP_USERNAME else 'EMPTY'}...")


def send_email(to_email, subject, html_content, text_content=None):
    """
    Envoie un email

    Args:
        to_email (str): Email du destinataire
        subject (str): Sujet de l'email
        html_content (str): Contenu HTML de l'email
        text_content (str, optional): Version texte de l'email

    Returns:
        bool: True si envoyé avec succès, False sinon
    """
    # Vérifier si les emails sont activés
    if not EMAIL_ENABLED:
        print(f"[EMAIL] Service désactivé - Email non envoyé à {to_email}: {subject}")
        return False

    # Si pas de configuration SMTP, ne pas envoyer (mode développement)
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print(f"[EMAIL] Configuration SMTP manquante - Email non envoyé à {to_email}: {subject}")
        return False

    try:
        # Créer le message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg['To'] = to_email

        # Ajouter la version texte si fournie
        if text_content:
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            msg.attach(part1)

        # Ajouter la version HTML
        part2 = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(part2)

        # Envoyer l'email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"[EMAIL] ✅ Email envoyé à {to_email}: {subject}")
        return True

    except Exception as e:
        print(f"[EMAIL] ❌ Erreur envoi email à {to_email}: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_email_template(title, content, cta_text=None, cta_url=None):
    """
    Génère un template HTML professionnel pour les emails

    Args:
        title (str): Titre de l'email
        content (str): Contenu principal (peut contenir du HTML)
        cta_text (str, optional): Texte du bouton d'action
        cta_url (str, optional): URL du bouton d'action

    Returns:
        str: HTML complet de l'email
    """
    cta_html = ""
    if cta_text and cta_url:
        cta_html = f"""
        <div style="text-align: center; margin: 30px 0;">
            <a href="{cta_url}" style="display: inline-block; padding: 14px 32px; background: #2E6B6B; color: white; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px;">
                {cta_text}
            </a>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f3f4f6;">
        <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f3f4f6; padding: 40px 0;">
            <tr>
                <td align="center">
                    <table cellpadding="0" cellspacing="0" border="0" width="600" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <!-- Header -->
                        <tr>
                            <td style="background-color: #2E6B6B; padding: 30px; text-align: center;">
                                <table cellpadding="0" cellspacing="0" border="0" width="100%">
                                    <tr>
                                        <td align="center">
                                            <img src="{PLATFORM_URL}/static/logo-dgppe.png" alt="Logo DGPPE" style="height: 80px; width: auto; margin-bottom: 15px; display: block;">
                                        </td>
                                    </tr>
                                    <tr>
                                        <td align="center">
                                            <h1 style="margin: 0; color: #ffffff; font-size: 22px; font-weight: 600; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                                                Direction Générale de la Planification<br>et des Politiques Économiques
                                            </h1>
                                            <p style="margin: 10px 0 0 0; color: #E0F2F1; font-size: 14px; font-weight: 500;">
                                                Plateforme de Maturation des Projets Publics (PLASMAP)
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 30px;">
                                <h2 style="margin: 0 0 20px 0; color: #1f2937; font-size: 20px; font-weight: 600;">
                                    {title}
                                </h2>
                                <div style="color: #4b5563; font-size: 15px; line-height: 1.6;">
                                    {content}
                                </div>
                                {cta_html}
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f9fafb; padding: 20px 30px; border-top: 1px solid #e5e7eb;">
                                <p style="margin: 0; color: #6b7280; font-size: 13px; text-align: center;">
                                    Cet email a été envoyé automatiquement par la plateforme DGPPE.<br>
                                    Pour toute question, veuillez contacter le secrétariat SCT.
                                </p>
                                <p style="margin: 10px 0 0 0; color: #9ca3af; font-size: 12px; text-align: center;">
                                    © {datetime.now().year} Direction Générale de la Planification et des Politiques Économiques
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def get_template_from_db(template_key):
    """
    Récupère un template depuis la base de données

    Args:
        template_key (str): Clé du template (ex: 'projet_assigne')

    Returns:
        dict: Template avec sujet et contenu, ou None si non trouvé
    """
    try:
        db, EmailTemplate = _get_db()
        template = EmailTemplate.query.filter_by(template_key=template_key, actif=True).first()

        if template:
            return {
                'sujet': template.sujet,
                'contenu': template.contenu_html
            }
        else:
            print(f"[EMAIL] ⚠️ Template '{template_key}' non trouvé ou inactif")
            return None

    except Exception as e:
        print(f"[EMAIL] ❌ Erreur chargement template '{template_key}': {e}")
        return None


def replace_variables(text, variables):
    """
    Remplace les variables dans le texte

    Args:
        text (str): Texte contenant des variables entre accolades
        variables (dict): Dictionnaire des variables à remplacer

    Returns:
        str: Texte avec variables remplacées
    """
    for key, value in variables.items():
        text = text.replace(key, str(value) if value is not None else '')
    return text


def send_status_change_email(project, user_email, user_name):
    """
    Envoie un email lors d'un changement de statut du projet

    Args:
        project: Objet projet
        user_email (str): Email du soumissionnaire
        user_name (str): Nom du soumissionnaire

    Returns:
        bool: True si envoyé avec succès
    """
    # Mapping des statuts vers les clés de templates
    status_to_template = {
        'assigné': 'projet_assigne',
        'en évaluation': 'projet_en_evaluation',
        'compléments demandés': 'complements_demandes',
        'évalué': 'projet_evalue',
        'favorable': 'avis_favorable',
        'favorable sous conditions': 'avis_favorable_conditions',
        'défavorable': 'avis_defavorable'
    }

    template_key = status_to_template.get(project.statut)

    if not template_key:
        print(f"[EMAIL] ⚠️ Aucun template défini pour le statut '{project.statut}'")
        return False

    # Récupérer le template depuis la DB
    template = get_template_from_db(template_key)

    if not template:
        # Fallback vers les messages hardcodés (pour compatibilité)
        print(f"[EMAIL] ℹ️ Utilisation du fallback hardcodé pour '{project.statut}'")
        return _send_status_change_email_fallback(project, user_email, user_name)

    # Variables de remplacement
    variables = {
        '{user_name}': user_name,
        '{project_titre}': project.titre,
        '{numero_projet}': project.numero_projet,
        '{message_complements}': project.complements_demande_message or 'Veuillez consulter la plateforme pour plus de détails.'
    }

    # Remplacer les variables
    sujet = replace_variables(template['sujet'], variables)
    contenu = replace_variables(template['contenu'], variables)

    # Générer le HTML complet
    html_content = get_email_template(
        title=sujet.replace('[DGPPE] ', ''),
        content=contenu,
        cta_text="Voir mon projet",
        cta_url=f"{PLATFORM_URL}/project/{project.id}"
    )

    return send_email(
        to_email=user_email,
        subject=sujet,
        html_content=html_content
    )


def _send_status_change_email_fallback(project, user_email, user_name):
    """
    Fonction fallback utilisant les messages hardcodés
    (Pour compatibilité au cas où les templates DB ne seraient pas disponibles)
    """
    status_messages = {
        'assigné': {
            'title': 'Votre projet a été assigné pour évaluation',
            'content': f"""
                <p>Bonjour {user_name},</p>
                <p>Nous vous informons que votre projet <strong>"{project.titre}"</strong> (N° {project.numero_projet}) a été assigné à un évaluateur.</p>
                <p>L'évaluation de votre dossier va commencer prochainement.</p>
            """
        },
        'en évaluation': {
            'title': 'Évaluation de votre projet en cours',
            'content': f"""
                <p>Bonjour {user_name},</p>
                <p>Votre projet <strong>"{project.titre}"</strong> (N° {project.numero_projet}) est actuellement en cours d'évaluation.</p>
                <p>Vous serez informé dès que l'évaluation sera terminée.</p>
            """
        },
        'compléments demandés': {
            'title': 'Compléments d\'information requis pour votre projet',
            'content': f"""
                <p>Bonjour {user_name},</p>
                <p>Suite à l'examen de votre projet <strong>"{project.titre}"</strong> (N° {project.numero_projet}), des compléments d'information sont nécessaires.</p>
                <p><strong>Message du secrétariat :</strong></p>
                <blockquote style="border-left: 4px solid #f59e0b; padding-left: 16px; margin: 16px 0; color: #92400e; background: #fef3c7; padding: 12px 16px; border-radius: 4px;">
                    {project.complements_demande_message or 'Veuillez consulter la plateforme pour plus de détails.'}
                </blockquote>
                <p>Veuillez vous connecter à la plateforme pour fournir les informations demandées.</p>
            """
        },
        'évalué': {
            'title': 'Évaluation de votre projet terminée',
            'content': f"""
                <p>Bonjour {user_name},</p>
                <p>L'évaluation de votre projet <strong>"{project.titre}"</strong> (N° {project.numero_projet}) est terminée.</p>
                <p>Le dossier est en cours de validation par le Secrétariat SCT.</p>
                <p>Vous serez informé de la suite du processus prochainement.</p>
            """
        },
        'favorable': {
            'title': '✅ Avis favorable pour votre projet',
            'content': f"""
                <p>Bonjour {user_name},</p>
                <p>Nous avons le plaisir de vous informer que votre projet <strong>"{project.titre}"</strong> (N° {project.numero_projet}) a reçu un <strong style="color: #10b981;">avis favorable</strong>.</p>
                <p>La fiche d'évaluation détaillée est maintenant disponible sur la plateforme.</p>
            """
        },
        'favorable sous conditions': {
            'title': 'Avis favorable sous conditions pour votre projet',
            'content': f"""
                <p>Bonjour {user_name},</p>
                <p>Votre projet <strong>"{project.titre}"</strong> (N° {project.numero_projet}) a reçu un <strong style="color: #f59e0b;">avis favorable sous conditions</strong>.</p>
                <p>Veuillez consulter la fiche d'évaluation sur la plateforme pour connaître les conditions à remplir.</p>
            """
        },
        'défavorable': {
            'title': 'Avis défavorable pour votre projet',
            'content': f"""
                <p>Bonjour {user_name},</p>
                <p>Nous vous informons que votre projet <strong>"{project.titre}"</strong> (N° {project.numero_projet}) a reçu un <strong style="color: #ef4444;">avis défavorable</strong>.</p>
                <p>La fiche d'évaluation détaillée expliquant les raisons de cet avis est disponible sur la plateforme.</p>
            """
        }
    }

    if project.statut not in status_messages:
        return False

    msg_data = status_messages[project.statut]

    html_content = get_email_template(
        title=msg_data['title'],
        content=msg_data['content'],
        cta_text="Voir mon projet",
        cta_url=f"{PLATFORM_URL}/project/{project.id}"
    )

    return send_email(
        to_email=user_email,
        subject=f"[DGPPE] {msg_data['title']}",
        html_content=html_content
    )


def send_evaluator_assignment_email(project, evaluator_email, evaluator_name):
    """
    Envoie un email à l'évaluateur lors de l'assignation d'un projet

    Args:
        project: Objet projet
        evaluator_email (str): Email de l'évaluateur
        evaluator_name (str): Nom de l'évaluateur

    Returns:
        bool: True si envoyé avec succès
    """
    # Récupérer le template depuis la DB
    template = get_template_from_db('evaluateur_assignation')

    if template:
        # Variables de remplacement
        variables = {
            '{evaluateur_nom}': evaluator_name,
            '{project_titre}': project.titre,
            '{numero_projet}': project.numero_projet,
            '{auteur_nom}': project.auteur_nom or 'Non spécifié'
        }

        # Remplacer les variables
        sujet = replace_variables(template['sujet'], variables)
        contenu = replace_variables(template['contenu'], variables)

        # Générer le HTML complet
        html_content = get_email_template(
            title=sujet.replace('[DGPPE] ', '').replace(f' - {project.titre}', ''),
            content=contenu,
            cta_text="Voir le projet",
            cta_url=f"{PLATFORM_URL}/project/{project.id}"
        )
    else:
        # Fallback hardcodé
        print("[EMAIL] ℹ️ Utilisation du fallback hardcodé pour evaluateur_assignation")
        content = f"""
            <p>Bonjour {evaluator_name},</p>
            <p>Un nouveau projet vous a été assigné pour évaluation.</p>
            <p><strong>Projet :</strong> {project.titre}</p>
            <p><strong>Numéro :</strong> {project.numero_projet}</p>
            <p><strong>Soumissionnaire :</strong> {project.auteur_nom or 'Non spécifié'}</p>
            <p>Veuillez vous connecter à la plateforme pour consulter le dossier complet et procéder à l'évaluation.</p>
        """

        html_content = get_email_template(
            title="Nouveau projet à évaluer",
            content=content,
            cta_text="Voir le projet",
            cta_url=f"{PLATFORM_URL}/project/{project.id}"
        )
        sujet = f"[DGPPE] Nouveau projet assigné - {project.titre}"

    return send_email(
        to_email=evaluator_email,
        subject=sujet,
        html_content=html_content
    )


def send_new_message_email(project, user_email, user_name, message_author):
    """
    Envoie un email lors d'un nouveau message dans la discussion

    Args:
        project: Objet projet
        user_email (str): Email du destinataire
        user_name (str): Nom du destinataire
        message_author (str): Auteur du message

    Returns:
        bool: True si envoyé avec succès
    """
    # Récupérer le template depuis la DB
    template = get_template_from_db('nouveau_message')

    if template:
        # Variables de remplacement
        variables = {
            '{user_name}': user_name,
            '{project_titre}': project.titre,
            '{numero_projet}': project.numero_projet,
            '{message_auteur}': message_author
        }

        # Remplacer les variables
        sujet = replace_variables(template['sujet'], variables)
        contenu = replace_variables(template['contenu'], variables)

        # Générer le HTML complet
        html_content = get_email_template(
            title=sujet.replace('[DGPPE] ', '').replace(f' - {project.titre}', ''),
            content=contenu,
            cta_text="Voir les messages",
            cta_url=f"{PLATFORM_URL}/project/{project.id}"
        )
    else:
        # Fallback hardcodé
        print("[EMAIL] ℹ️ Utilisation du fallback hardcodé pour nouveau_message")
        content = f"""
            <p>Bonjour {user_name},</p>
            <p>Un nouveau message a été posté sur votre projet <strong>"{project.titre}"</strong> (N° {project.numero_projet}).</p>
            <p><strong>Message de :</strong> {message_author}</p>
            <p>Connectez-vous à la plateforme pour consulter ce message et y répondre si nécessaire.</p>
        """

        html_content = get_email_template(
            title="Nouveau message sur votre projet",
            content=content,
            cta_text="Voir les messages",
            cta_url=f"{PLATFORM_URL}/project/{project.id}"
        )
        sujet = f"[DGPPE] Nouveau message - {project.titre}"

    return send_email(
        to_email=user_email,
        subject=sujet,
        html_content=html_content
    )
