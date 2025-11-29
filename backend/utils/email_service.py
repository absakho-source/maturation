"""
Service d'envoi d'emails pour les notifications
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailService:
    """Service d'envoi d'emails via SMTP"""

    def __init__(self):
        # Configuration SMTP depuis variables d'environnement
        self.smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_username = os.environ.get('SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.from_email = os.environ.get('SMTP_FROM_EMAIL', self.smtp_username)
        self.from_name = os.environ.get('SMTP_FROM_NAME', 'PLASMAP - DGPPE')

        # Mode debug (ne pas envoyer d'emails réels)
        self.debug_mode = os.environ.get('EMAIL_DEBUG_MODE', 'true').lower() == 'true'

        # Activer/désactiver les emails
        self.enabled = os.environ.get('EMAIL_ENABLED', 'false').lower() == 'true'

    def send_email(self, to_email, subject, html_body, text_body=None):
        """
        Envoie un email

        Args:
            to_email: Adresse email du destinataire
            subject: Sujet de l'email
            html_body: Corps de l'email en HTML
            text_body: Corps de l'email en texte brut (optionnel)

        Returns:
            bool: True si envoyé avec succès, False sinon
        """
        if not self.enabled:
            print(f"[EMAIL] Service désactivé - Email non envoyé à {to_email}")
            print(f"[EMAIL] Sujet: {subject}")
            return False

        if not to_email:
            print("[EMAIL] Aucune adresse email fournie")
            return False

        if not self.smtp_username or not self.smtp_password:
            print("[EMAIL] Configuration SMTP manquante (SMTP_USERNAME ou SMTP_PASSWORD)")
            return False

        try:
            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

            # Ajouter le corps en texte brut (fallback)
            if text_body:
                part1 = MIMEText(text_body, 'plain', 'utf-8')
                msg.attach(part1)

            # Ajouter le corps en HTML
            part2 = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(part2)

            if self.debug_mode:
                print(f"\n{'='*60}")
                print(f"[EMAIL DEBUG] Email qui serait envoyé:")
                print(f"{'='*60}")
                print(f"À: {to_email}")
                print(f"De: {self.from_name} <{self.from_email}>")
                print(f"Sujet: {subject}")
                print(f"\n{html_body}")
                print(f"{'='*60}\n")
                return True

            # Connexion SMTP et envoi
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            print(f"[EMAIL] ✓ Email envoyé avec succès à {to_email}")
            return True

        except Exception as e:
            print(f"[EMAIL] ✗ Erreur lors de l'envoi à {to_email}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def send_notification_email(self, user_email, user_name, notification_type, notification_data):
        """
        Envoie un email de notification basé sur le type

        Args:
            user_email: Email du destinataire
            user_name: Nom du destinataire
            notification_type: Type de notification (nouveau_projet, evaluation_assignee, etc.)
            notification_data: Données spécifiques à la notification

        Returns:
            bool: True si envoyé avec succès
        """
        templates = {
            'nouveau_projet': {
                'subject': 'Nouveau projet soumis - {titre}',
                'template': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; padding: 20px; text-align: center;">
                        <h1 style="margin: 0;">PLASMAP - DGPPE</h1>
                        <p style="margin: 5px 0;">Plateforme de Soumission et de Maturation de Projets Publics</p>
                    </div>

                    <div style="padding: 30px 20px; background: #f9fafb;">
                        <p>Bonjour <strong>{user_name}</strong>,</p>

                        <p>Un nouveau projet a été soumis sur la plateforme :</p>

                        <div style="background: white; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0;">
                            <h2 style="margin: 0 0 10px 0; color: #1e3a8a;">{titre}</h2>
                            <p style="margin: 5px 0;"><strong>Numéro :</strong> {numero}</p>
                            <p style="margin: 5px 0;"><strong>Secteur :</strong> {secteur}</p>
                            <p style="margin: 5px 0;"><strong>Soumis par :</strong> {soumissionnaire}</p>
                        </div>

                        <p>
                            <a href="{lien}" style="display: inline-block; background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0;">
                                Voir le projet
                            </a>
                        </p>
                    </div>

                    <div style="background: #e5e7eb; padding: 15px; text-align: center; font-size: 12px; color: #6b7280;">
                        <p>Ceci est un email automatique de la plateforme PLASMAP.</p>
                        <p>Direction Générale de la Planification et des Politiques Économiques (DGPPE)</p>
                    </div>
                </div>
                '''
            },

            'evaluation_assignee': {
                'subject': 'Évaluation assignée - {titre}',
                'template': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; padding: 20px; text-align: center;">
                        <h1 style="margin: 0;">PLASMAP - DGPPE</h1>
                        <p style="margin: 5px 0;">Nouvelle évaluation à réaliser</p>
                    </div>

                    <div style="padding: 30px 20px; background: #f9fafb;">
                        <p>Bonjour <strong>{user_name}</strong>,</p>

                        <p>Un projet vous a été assigné pour évaluation :</p>

                        <div style="background: white; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0;">
                            <h2 style="margin: 0 0 10px 0; color: #1e3a8a;">{titre}</h2>
                            <p style="margin: 5px 0;"><strong>Numéro :</strong> {numero}</p>
                            <p style="margin: 5px 0;"><strong>Secteur :</strong> {secteur}</p>
                        </div>

                        <p>Veuillez procéder à l'évaluation de ce projet dans les meilleurs délais.</p>

                        <p>
                            <a href="{lien}" style="display: inline-block; background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0;">
                                Commencer l'évaluation
                            </a>
                        </p>
                    </div>

                    <div style="background: #e5e7eb; padding: 15px; text-align: center; font-size: 12px; color: #6b7280;">
                        <p>Ceci est un email automatique de la plateforme PLASMAP.</p>
                        <p>Direction Générale de la Planification et des Politiques Économiques (DGPPE)</p>
                    </div>
                </div>
                '''
            },

            'decision_finale': {
                'subject': 'Décision finale - {titre}',
                'template': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; padding: 20px; text-align: center;">
                        <h1 style="margin: 0;">PLASMAP - DGPPE</h1>
                        <p style="margin: 5px 0;">Décision finale du Comité</p>
                    </div>

                    <div style="padding: 30px 20px; background: #f9fafb;">
                        <p>Bonjour <strong>{user_name}</strong>,</p>

                        <p>Une décision finale a été prise concernant votre projet :</p>

                        <div style="background: white; border-left: 4px solid #8b5cf6; padding: 15px; margin: 20px 0;">
                            <h2 style="margin: 0 0 10px 0; color: #1e3a8a;">{titre}</h2>
                            <p style="margin: 5px 0;"><strong>Numéro :</strong> {numero}</p>
                            <p style="margin: 5px 0;"><strong>Décision :</strong> <span style="color: {decision_color};">{decision}</span></p>
                        </div>

                        <p>
                            <a href="{lien}" style="display: inline-block; background: #8b5cf6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0;">
                                Voir les détails
                            </a>
                        </p>
                    </div>

                    <div style="background: #e5e7eb; padding: 15px; text-align: center; font-size: 12px; color: #6b7280;">
                        <p>Ceci est un email automatique de la plateforme PLASMAP.</p>
                        <p>Direction Générale de la Planification et des Politiques Économiques (DGPPE)</p>
                    </div>
                </div>
                '''
            }
        }

        template_info = templates.get(notification_type)
        if not template_info:
            print(f"[EMAIL] Type de notification inconnu: {notification_type}")
            return False

        # Formatter le sujet et le template
        subject = template_info['subject'].format(**notification_data)
        html_body = template_info['template'].format(user_name=user_name, **notification_data)

        return self.send_email(user_email, subject, html_body)


# Instance globale
email_service = EmailService()
