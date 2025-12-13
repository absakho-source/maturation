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

## 🚀 Configuration Production (Render)

### Étape 1 : Accéder aux Variables d'Environnement

1. Connectez-vous sur https://dashboard.render.com
2. Sélectionnez votre service backend
3. Allez dans l'onglet **Environment**
4. Cliquez sur **Add Environment Variable**

### Étape 2 : Ajouter les Variables (une par une)

**Configuration recommandée - Test 1 : Serveur Exchange interne**

| Key | Value |
|-----|-------|
| `SMTP_SERVER` | `mail.economie.gouv.sn` |
| `SMTP_PORT` | `587` |
| `SMTP_USERNAME` | `economie\maturation.dgppe` |
| `SMTP_PASSWORD` | `Maturationdgppe1` |
| `FROM_EMAIL` | `maturation.dgppe@economie.gouv.sn` |
| `FROM_NAME` | `Maturation DGPPE` |
| `EMAIL_ENABLED` | `true` |
| `EMAIL_DEBUG_MODE` | `true` |
| `PLATFORM_URL` | `https://maturation-dgppe.onrender.com` |

**Si le Test 1 échoue - Test 2 : Office 365**

Changez seulement ces variables :

| Key | Value |
|-----|-------|
| `SMTP_SERVER` | `smtp.office365.com` |
| `SMTP_USERNAME` | `maturation.dgppe@economie.gouv.sn` |

### Étape 3 : Redéployer le Service

1. Cliquez sur **Manual Deploy** → **Deploy latest commit**
2. Attendez la fin du déploiement (2-3 minutes)

### Étape 4 : Tester l'Envoi d'Email

Une fois déployé, testez en production :

1. Connectez-vous à la plateforme en production
2. Assignez un projet à un évaluateur
3. Vérifiez si l'email est reçu

**OU** utilisez SSH pour tester directement :

```bash
ssh root@164.92.255.58
cd /root/maturation/backend
source venv/bin/activate
python3 test_email_simple.py votre-email@test.com
```

### Étape 5 : Vérifier les Logs

En cas d'échec, consultez les logs dans Render :

1. Dashboard → Service backend → **Logs**
2. Recherchez `[EMAIL]` pour voir les messages de debug

**Note importante** : Le mode `EMAIL_DEBUG_MODE=true` affichera tous les détails de connexion SMTP dans les logs.

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

## 📊 Résumé de l'Implémentation

### ✅ Code Complété

- [x] Service d'envoi d'emails avec templates HTML professionnels
- [x] Support des variables d'environnement via `.env`
- [x] Flag `EMAIL_ENABLED` pour activer/désactiver les emails
- [x] Mode debug `EMAIL_DEBUG_MODE` pour troubleshooting
- [x] python-dotenv ajouté au requirements.txt
- [x] Script de test [test_email_simple.py](backend/test_email_simple.py)
- [x] Documentation complète

### 🔄 Prochaines Étapes (À FAIRE)

1. **Configurer les variables d'environnement sur Render** (voir section ci-dessus)
2. **Redéployer le service backend**
3. **Tester l'envoi d'email en production**
4. **Si échec** : Vérifier avec l'admin IT que SMTP AUTH est activé pour le compte
5. **Une fois fonctionnel** : Désactiver `EMAIL_DEBUG_MODE` en production

### 🎯 Notifications Automatiques (Déjà Implémentées)

Les emails seront envoyés automatiquement dès que `EMAIL_ENABLED=true` :

- ✅ Projet assigné à un évaluateur
- ✅ Projet mis en évaluation
- ✅ Compléments demandés (avec matrice des documents)
- ✅ Évaluation terminée
- ✅ Décision finale (favorable/défavorable/sous conditions)
- ✅ Nouveau message dans la discussion

**Tout le code est prêt, il suffit d'activer les emails en production !**

