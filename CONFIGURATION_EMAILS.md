# Configuration des Emails - PLASMAP

## Vue d'ensemble

Le système de notifications par email permet d'envoyer automatiquement des emails aux utilisateurs lors d'événements importants sur la plateforme.

## Variables d'environnement

### Configuration SMTP (Requises pour l'envoi d'emails)

```bash
# Activer/Désactiver les emails
EMAIL_ENABLED=true              # false par défaut - Activer pour envoyer des emails réels

# Mode debug (affiche les emails dans les logs au lieu de les envoyer)
EMAIL_DEBUG_MODE=false          # true par défaut - Mettre à false en production

# Configuration du serveur SMTP
SMTP_HOST=smtp.gmail.com        # Serveur SMTP (Gmail par défaut)
SMTP_PORT=587                   # Port SMTP (587 pour TLS)
SMTP_USERNAME=votre.email@gmail.com      # Email d'authentification
SMTP_PASSWORD=votre_mot_de_passe_app     # Mot de passe d'application

# Informations de l'expéditeur
SMTP_FROM_EMAIL=noreply@dgppe.sn         # Email affiché comme expéditeur
SMTP_FROM_NAME=PLASMAP - DGPPE           # Nom affiché comme expéditeur

# URL du frontend (pour les liens dans les emails)
FRONTEND_URL=https://maturation-frontend.onrender.com
```

## Configuration Gmail

Pour utiliser Gmail comme serveur SMTP :

1. **Activer l'authentification à deux facteurs** sur votre compte Gmail
2. **Créer un mot de passe d'application** :
   - Allez dans https://myaccount.google.com/security
   - Cliquez sur "Mots de passe d'application"
   - Sélectionnez "Autre" et nommez-le "PLASMAP"
   - Copiez le mot de passe généré (16 caractères)
   - Utilisez ce mot de passe dans `SMTP_PASSWORD`

3. **Configuration recommandée** :
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre.email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # Mot de passe d'application
```

## Configuration Autres Services SMTP

### SendGrid
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=votre_clé_api_sendgrid
```

### Mailgun
```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=postmaster@votre-domaine.mailgun.org
SMTP_PASSWORD=votre_mot_de_passe_mailgun
```

### Serveur SMTP personnel
```bash
SMTP_HOST=smtp.votre-domaine.com
SMTP_PORT=587  # ou 465 pour SSL
SMTP_USERNAME=notifications@votre-domaine.com
SMTP_PASSWORD=votre_mot_de_passe
```

## Types de notifications par email

Les emails sont envoyés automatiquement pour :

1. **Assignation d'évaluation** (`assignation`)
   - Envoyé à l'évaluateur quand un projet lui est assigné
   - Template: Email vert avec bouton "Commencer l'évaluation"

2. **Décision finale** (`decision_finale`)
   - Envoyé au soumissionnaire quand une décision finale est prise
   - Template: Email violet avec couleur de décision (vert = approuvé, rouge = rejeté)

3. **Nouveau projet** (peut être activé)
   - Envoyé aux administrateurs lors d'une nouvelle soumission
   - Template: Email bleu avec détails du projet

## Contrôle de l'envoi

### Envoi prioritaire uniquement (par défaut)
```bash
EMAIL_SEND_ALL=false
```
Seules les notifications marquées comme `priorite_email=True` déclencheront un email.

### Envoi de toutes les notifications
```bash
EMAIL_SEND_ALL=true
```
Toutes les notifications créées déclencheront un email (peut générer beaucoup d'emails).

## Mode Debug

En développement, utilisez le mode debug pour voir les emails sans les envoyer :

```bash
EMAIL_ENABLED=true
EMAIL_DEBUG_MODE=true
```

Les emails seront affichés dans les logs de la console au lieu d'être envoyés.

## Test de la configuration

Après avoir configuré les variables d'environnement, vous pouvez tester l'envoi d'email :

```python
from utils.email_service import email_service

# Test simple
success = email_service.send_email(
    to_email='test@example.com',
    subject='Test PLASMAP',
    html_body='<h1>Test réussi !</h1>'
)

print(f"Email envoyé: {success}")
```

## Sécurité

⚠️ **IMPORTANT** :
- Ne JAMAIS commiter les mots de passe SMTP dans le code
- Utiliser des variables d'environnement sur Render.com
- Utiliser des mots de passe d'application (pas le mot de passe principal du compte)
- Limiter les permissions du compte email utilisé

## Configuration sur Render.com

1. Allez dans votre service backend sur Render.com
2. Cliquez sur "Environment"
3. Ajoutez les variables d'environnement :
   - `EMAIL_ENABLED` = `true`
   - `EMAIL_DEBUG_MODE` = `false`
   - `SMTP_HOST` = `smtp.gmail.com`
   - `SMTP_PORT` = `587`
   - `SMTP_USERNAME` = votre email
   - `SMTP_PASSWORD` = mot de passe d'application
   - `SMTP_FROM_EMAIL` = email expéditeur
   - `SMTP_FROM_NAME` = `PLASMAP - DGPPE`
   - `FRONTEND_URL` = `https://maturation-frontend.onrender.com`

4. Sauvegardez et redémarrez le service

## Personnalisation des templates

Les templates d'email sont définis dans `/backend/utils/email_service.py`.

Pour personnaliser un template :

1. Modifiez le dictionnaire `templates` dans la méthode `send_notification_email()`
2. Les templates supportent HTML complet avec CSS inline
3. Variables disponibles : `{user_name}`, `{titre}`, `{numero}`, `{secteur}`, `{lien}`, etc.

## Troubleshooting

### Les emails ne sont pas envoyés

1. Vérifiez que `EMAIL_ENABLED=true`
2. Vérifiez que `EMAIL_DEBUG_MODE=false` (en production)
3. Consultez les logs pour voir les erreurs SMTP
4. Vérifiez que le compte email autorise les connexions SMTP
5. Vérifiez que le mot de passe d'application est correct

### Emails marqués comme spam

1. Utilisez un serveur SMTP professionnel (SendGrid, Mailgun)
2. Configurez SPF, DKIM et DMARC pour votre domaine
3. Utilisez un domaine vérifié comme expéditeur

### Trop d'emails envoyés

1. Passez `EMAIL_SEND_ALL=false`
2. Seules les notifications prioritaires seront envoyées

## Support

Pour toute question sur la configuration des emails, consultez la documentation ou contactez l'équipe technique.
