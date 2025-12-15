#!/usr/bin/env python3
"""
Script de test pour l'envoi d'emails via Gmail

IMPORTANT: Vous devez configurer un "App Password" pour Gmail

Étapes:
1. Éditez le fichier .env.gmail avec vos informations Gmail
2. Créez un App Password sur https://myaccount.google.com/security
3. Exécutez: python3 test_gmail.py votre_email_destinataire@example.com
"""

import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Charger .env.gmail au lieu de .env
env_path = os.path.join(os.path.dirname(__file__), '.env.gmail')
if not os.path.exists(env_path):
    print("❌ Fichier .env.gmail non trouvé!")
    print("   Créez le fichier .env.gmail avec votre configuration Gmail")
    sys.exit(1)

load_dotenv(env_path)

def test_gmail_connection():
    """Teste la connexion au serveur Gmail"""

    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    from_email = os.getenv('FROM_EMAIL', '')

    print("=" * 60)
    print("TEST DE CONNEXION GMAIL")
    print("=" * 60)
    print(f"📧 Serveur SMTP : {smtp_server}:{smtp_port}")
    print(f"👤 Utilisateur  : {smtp_username}")
    print(f"🔑 Password     : {'*' * len(smtp_password) if smtp_password else '(vide)'}")
    print(f"📨 From Email   : {from_email}")
    print()

    if not smtp_username or not smtp_password:
        print("❌ ERREUR: SMTP_USERNAME ou SMTP_PASSWORD manquant dans .env.gmail")
        print()
        print("Veuillez éditer .env.gmail et remplir:")
        print("  SMTP_USERNAME=votre.email@gmail.com")
        print("  SMTP_PASSWORD=votre_app_password_16_caracteres")
        print()
        print("Pour créer un App Password:")
        print("  1. Allez sur https://myaccount.google.com/security")
        print("  2. Activez la validation en 2 étapes")
        print("  3. Dans 'App Passwords', créez un mot de passe pour 'Mail'")
        print("  4. Copiez le mot de passe de 16 caractères (sans espaces)")
        return False

    try:
        print("🔄 Connexion au serveur Gmail...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.set_debuglevel(1)  # Mode debug pour voir tous les détails

        print("\n🔄 Démarrage TLS...")
        server.starttls()

        print(f"\n🔄 Authentification avec {smtp_username}...")
        server.login(smtp_username, smtp_password)

        print("\n✅ CONNEXION RÉUSSIE!")
        server.quit()
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ ERREUR D'AUTHENTIFICATION: {e}")
        print()
        print("Solutions possibles:")
        print("  1. Vérifiez que vous utilisez un App Password (pas votre mot de passe Gmail normal)")
        print("  2. Créez un nouveau App Password sur https://myaccount.google.com/security")
        print("  3. Vérifiez que la validation en 2 étapes est activée sur votre compte Gmail")
        print("  4. Vérifiez que l'email dans SMTP_USERNAME est correct")
        return False

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return False


def send_test_email(to_email):
    """Envoie un email de test via Gmail"""

    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    from_email = os.getenv('FROM_EMAIL', '')
    from_name = os.getenv('FROM_NAME', 'Test Gmail')

    print("\n" + "=" * 60)
    print("ENVOI D'EMAIL DE TEST")
    print("=" * 60)
    print(f"📧 De      : {from_name} <{from_email}>")
    print(f"📧 Vers    : {to_email}")
    print()

    try:
        # Créer le message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = to_email
        msg['Subject'] = "✅ Test d'envoi Gmail - Plateforme Maturation DGPPE"

        # Corps HTML
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2c3e50;">✅ Test d'envoi réussi!</h2>
            <p>Cet email a été envoyé avec succès depuis la plateforme Maturation DGPPE via Gmail.</p>

            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <strong>Configuration utilisée:</strong><br>
                📧 Serveur SMTP: {smtp_server}:{smtp_port}<br>
                👤 Compte Gmail: {smtp_username}<br>
                📨 Email expéditeur: {from_email}
            </div>

            <p>Si vous recevez cet email, la configuration Gmail fonctionne correctement!</p>

            <hr style="margin: 30px 0;">
            <p style="color: #6c757d; font-size: 0.9em;">
                <strong>Plateforme Maturation DGPPE</strong><br>
                Direction Générale de la Planification et des Politiques Économiques
            </p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, 'html'))

        # Connexion et envoi
        print("🔄 Connexion au serveur Gmail...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()

        print("🔄 Authentification...")
        server.login(smtp_username, smtp_password)

        print("🔄 Envoi de l'email...")
        server.send_message(msg)
        server.quit()

        print("\n✅ EMAIL ENVOYÉ AVEC SUCCÈS!")
        print(f"   Vérifiez la boîte de réception de {to_email}")
        return True

    except Exception as e:
        print(f"\n❌ ERREUR LORS DE L'ENVOI: {e}")
        return False


if __name__ == '__main__':
    print("\n🚀 SCRIPT DE TEST GMAIL")
    print()

    # Vérifier l'adresse email destinataire
    if len(sys.argv) < 2:
        print("❌ Veuillez fournir une adresse email destinataire")
        print()
        print("Usage:")
        print(f"  python3 {sys.argv[0]} destinataire@example.com")
        print()
        print("Exemple:")
        print(f"  python3 {sys.argv[0]} abdou.sakho@economie.gouv.sn")
        sys.exit(1)

    to_email = sys.argv[1]

    # Étape 1: Tester la connexion
    if test_gmail_connection():
        print("\n" + "=" * 60)

        # Étape 2: Envoyer un email de test
        send_test_email(to_email)

        print("\n" + "=" * 60)
        print("✅ TEST TERMINÉ")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ TEST ÉCHOUÉ - Corrigez les erreurs ci-dessus")
        print("=" * 60)
        sys.exit(1)
