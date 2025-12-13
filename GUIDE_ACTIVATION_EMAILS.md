# 📧 Guide Rapide - Activation des Emails

## ✅ Ce qui est déjà fait

Tout le code est prêt et déployé ! Il ne reste plus qu'à **activer les emails en production**.

## 🚀 Activation en 5 Minutes

### Étape 1 : Configurer Render

1. Aller sur https://dashboard.render.com
2. Sélectionner le service **backend**
3. Aller dans **Environment**
4. Ajouter ces 9 variables :

```
SMTP_SERVER = mail.economie.gouv.sn
SMTP_PORT = 587
SMTP_USERNAME = economie\maturation.dgppe
SMTP_PASSWORD = Maturationdgppe1
FROM_EMAIL = maturation.dgppe@economie.gouv.sn
FROM_NAME = Maturation DGPPE
EMAIL_ENABLED = true
EMAIL_DEBUG_MODE = true
PLATFORM_URL = https://maturation-dgppe.onrender.com
```

### Étape 2 : Redéployer

1. Cliquer sur **Manual Deploy** → **Deploy latest commit**
2. Attendre 2-3 minutes

### Étape 3 : Tester

Option A - Via l'interface web :
1. Se connecter à https://maturation-dgppe.onrender.com
2. Assigner un projet à un évaluateur
3. Vérifier si l'email est reçu

Option B - Via SSH :
```bash
ssh root@164.92.255.58
cd /root/maturation/backend
source venv/bin/activate
python3 test_email_simple.py votre-email@test.com
```

### Étape 4 : Vérifier les Logs (si problème)

1. Dashboard Render → Service backend → **Logs**
2. Rechercher `[EMAIL]` pour voir les messages

## 🔄 Si le Test Échoue

### Option 1 : Essayer Office 365

Dans Render Environment, changer seulement :
```
SMTP_SERVER = smtp.office365.com
SMTP_USERNAME = maturation.dgppe@economie.gouv.sn
```

Puis redéployer.

### Option 2 : Contacter l'Admin IT

Demander à l'admin de :
- Vérifier que SMTP AUTH est activé pour `maturation.dgppe@economie.gouv.sn`
- Désactiver MFA pour ce compte (si activé)
- Ou créer un mot de passe d'application

## 📩 Emails Automatiques Configurés

Dès que `EMAIL_ENABLED=true`, les emails seront envoyés pour :

- 📩 Projet assigné à un évaluateur
- 🔄 Projet mis en évaluation
- ⚠️ Compléments demandés (avec matrice)
- ✅ Évaluation terminée
- 🎯 Décision finale
- 💬 Nouveau message dans la discussion

## 🎯 Une Fois Fonctionnel

Désactiver le mode debug dans Render :
```
EMAIL_DEBUG_MODE = false
```

Et redéployer.

---

**Pour plus de détails**, voir [CONFIGURATION_EMAILS.md](CONFIGURATION_EMAILS.md)
