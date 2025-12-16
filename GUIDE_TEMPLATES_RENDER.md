# Guide: Résoudre le problème des templates sur Render

## Problème
Les templates d'emails ont été initialisés avec succès (`init_production.py`), mais l'API retourne toujours un tableau vide et les templates n'apparaissent pas dans l'interface.

## Diagnostic

### Étape 1: Vérifier les templates dans la base de données

Dans le **Render Shell**, exécutez:

```bash
cd /root/maturation/backend
python3 check_templates_render.py
```

Ce script va:
- Vérifier si les templates existent dans SQLite directement
- Vérifier si les templates sont accessibles via l'ORM Flask
- Identifier si c'est un problème de base de données ou de connexion

### Étape 2: Interpréter les résultats

**Cas 1: Templates existent dans SQLite mais pas dans l'ORM**
```
📧 Nombre de templates dans la base: 9
📧 Nombre de templates via ORM: 0
```
➡️ **Solution**: Le backend doit être redémarré pour recharger la connexion à la base de données.

**Cas 2: Templates n'existent ni dans SQLite ni dans l'ORM**
```
📧 Nombre de templates dans la base: 0
📧 Nombre de templates via ORM: 0
```
➡️ **Solution**: Les templates n'ont pas été initialisés correctement. Réexécutez `init_production.py`.

**Cas 3: Templates existent partout**
```
📧 Nombre de templates dans la base: 9
📧 Nombre de templates via ORM: 9
```
➡️ **Solution**: Le problème est ailleurs (API, permissions, etc.).

## Solutions

### Solution A: Redémarrer les services (le plus probable)

Dans le **Render Dashboard**:

1. Allez dans votre service backend
2. Cliquez sur **"Manual Deploy"** → **"Clear build cache & deploy"**
3. Attendez que le déploiement soit terminé
4. Testez l'API: https://maturation-backend.onrender.com/api/admin/email-templates

**OU** via SSH (si disponible):

```bash
./verify_and_restart_production.sh
```

Ce script va:
- Vérifier le nombre de templates dans la base
- Arrêter les services backend/frontend
- Redémarrer les services
- Vérifier que l'API retourne bien les templates

### Solution B: Réinitialiser les templates

Si les templates n'existent pas dans la base, dans le **Render Shell**:

```bash
cd /root/maturation/backend
source venv/bin/activate
python3 init_email_templates.py
```

Puis redémarrez les services (voir Solution A).

### Solution C: Vérifier la configuration de la base de données

Dans le **Render Shell**, vérifiez le chemin de la base:

```bash
cd /root/maturation/backend
grep -n "SQLALCHEMY_DATABASE_URI" app.py
```

Le chemin doit être: `sqlite:////data/maturation.db`

Si différent, vérifiez les variables d'environnement sur Render:
- Dashboard → Environment → Variables
- Vérifiez `DATABASE_PATH` ou `SQLALCHEMY_DATABASE_URI`

## Vérification finale

Une fois les services redémarrés, vérifiez:

### 1. API Backend
```bash
curl -s "https://maturation-backend.onrender.com/api/admin/email-templates" \
  -H "X-Role: admin" \
  -H "X-Username: admin" | python3 -m json.tool
```

Devrait retourner:
```json
{
  "templates": [
    {
      "id": 1,
      "template_key": "soumission_recue",
      "sujet": "Votre projet a été soumis avec succès",
      ...
    },
    ...
  ]
}
```

### 2. Interface Web
1. Connectez-vous en tant qu'admin sur: https://maturation-dgppe.onrender.com
2. Allez dans **Configuration Emails**
3. Scrollez jusqu'à la section **Templates d'Emails**
4. Vous devriez voir 9 templates modifiables

## En cas d'échec

Si après toutes ces étapes les templates n'apparaissent toujours pas:

1. **Vérifiez les logs backend** dans Render Dashboard → Logs
2. **Cherchez des erreurs** liées à:
   - `email_templates`
   - `Database`
   - `SQLALCHEMY`
3. **Contactez le support** avec les logs et le résultat de `check_templates_render.py`

## Configuration Gmail

Une fois les templates visibles, n'oubliez pas de configurer Gmail sur Render:

### Variables d'environnement à ajouter dans Render:

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=maturation.dgppe@gmail.com
SMTP_PASSWORD=pfjwdshjptitxypl
FROM_EMAIL=maturation.dgppe@gmail.com
FROM_NAME=Maturation DGPPE
PLATFORM_URL=https://maturation-dgppe.onrender.com
EMAIL_ENABLED=true
EMAIL_DEBUG_MODE=false
```

### Comment ajouter ces variables:

1. Dashboard Render → Votre service backend
2. **Environment** (menu gauche)
3. **Add Environment Variable**
4. Ajoutez chaque variable une par une
5. **Save Changes** et redéployez

---

## Résumé des fichiers créés

- `check_templates_render.py` - Script de diagnostic à exécuter dans Render Shell
- `verify_and_restart_production.sh` - Script complet de vérification et redémarrage (via SSH)
- `init_production.py` - Script d'initialisation des templates pour production
- `deploy_gmail_to_production.sh` - Déploiement complet Gmail + Templates (via SSH)

## Contact

En cas de problème, les informations de diagnostic à fournir:
- Résultat de `check_templates_render.py`
- Logs du backend Render
- Résultat de l'appel API `/api/admin/email-templates`
