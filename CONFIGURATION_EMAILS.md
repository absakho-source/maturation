# Configuration des Emails - Plateforme DGPPE

## ✅ Ce qui a été fait

1. **Service d'envoi d'emails configuré** ([email_service.py](backend/email_service.py))
2. **Templates HTML professionnels** pour tous les types de notifications
3. **Support des variables d'environnement** via fichier `.env`
4. **Script de test** ([test_email_simple.py](backend/test_email_simple.py))
5. **python-dotenv installé** dans le venv

## ⚠️ Problème Actuel - Authentification Exchange

### Erreur rencontrée

```
SMTPAuthenticationError: (535, '5.7.3 Authentication unsuccessful')
```

### Cause probable

Le compte `maturation.dgppe@economie.gouv.sn` :
- A peut-être un mot de passe incorrect
- OU a l'authentification multifacteur (MFA/2FA) activée
- OU l'authentification SMTP de base est désactivée

## Solutions à Tester

### 1. Vérifier les Identifiants

**Testez la connexion** sur https://outlook.office.com avec :
- Email: `maturation.dgppe@economie.gouv.sn`
- Mot de passe: `Maturationdgppe1`

Si la connexion échoue → le mot de passe est incorrect

### 2. Créer un Mot de Passe d'Application (si MFA activé)

Si MFA est activé sur le compte :

1. Se connecter sur https://account.microsoft.com/security
2. Aller dans **Sécurité** → **Options de sécurité avancées** 
3. Cliquer sur **Créer un mot de passe d'application**
4. Remplacer dans `.env` :
   ```env
   SMTP_PASSWORD=<nouveau-mot-de-passe-application>
   ```

### 3. Contacter l'Administrateur Exchange

Demander à l'admin IT de :
- Vérifier que SMTP AUTH est activé pour ce compte
- Désactiver MFA pour ce compte de service
- Ou autoriser "Authentification de base" (Basic Auth) pour SMTP

## Configuration Production (Render)

### Variables d'Environnement à Ajouter

Dans le dashboard Render → Service backend → Environment :

```
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=maturation.dgppe@economie.gouv.sn
SMTP_PASSWORD=Maturationdgppe1
FROM_EMAIL=maturation.dgppe@economie.gouv.sn
FROM_NAME=Maturation DGPPE
EMAIL_ENABLED=true
EMAIL_DEBUG_MODE=false
PLATFORM_URL=https://maturation-dgppe.onrender.com
```

**Note** : Utilisez le **mot de passe d'application** si MFA est activé

## Test Local

```bash
cd backend
source venv/bin/activate
python3 test_email_simple.py votre-email@test.com
```

## Notifications Configurées

Les emails sont envoyés automatiquement pour :

1. 📩 **Projet assigné** → Notification au soumissionnaire
2. 🔄 **Projet en évaluation** → Notification au soumissionnaire  
3. ⚠️ **Compléments demandés** → Email avec matrice des documents manquants
4. ✅ **Évaluation terminée** → Notification au soumissionnaire
5. 🎯 **Décision finale** (favorable/défavorable/sous conditions)
6. 💬 **Nouveau message** dans la discussion

## Fichiers Modifiés

- ✅ `backend/email_service.py` - Service d'envoi (load_dotenv ajouté)
- ✅ `backend/.env` - Configuration locale (non versionné)
- ✅ `backend/test_email_simple.py` - Script de test
- ✅ `backend/requirements.txt` - python-dotenv ajouté (à faire)

## Prochaines Étapes

1. ⏳ Résoudre l'authentification Office365/Exchange
2. ⏳ Ajouter `python-dotenv` au requirements.txt
3. ⏳ Configurer les variables sur Render
4. ⏳ Tester l'envoi depuis la production

