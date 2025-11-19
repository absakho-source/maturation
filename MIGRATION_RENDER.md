# Migration Base de Données Render - URGENT

## Problème Actuel

L'erreur 500 sur `/api/projects` est causée par les colonnes manquantes dans la base de données Render :
- `organisme_tutelle_data`
- `structure_soumissionnaire`

## Solution : Exécuter la Migration sur Render

### Étape 1 : Accéder au Shell Render

1. Aller sur https://dashboard.render.com
2. Cliquer sur le service **backend** (maturation-backend)
3. Dans le menu de gauche, cliquer sur **"Shell"**

### Étape 2 : Exécuter la Migration

Dans le Shell Render, copier-coller cette commande :

```bash
cd backend && python migrate_render.py
```

**OU** si la base de données s'appelle `projects.db` :

```bash
cd backend && python migrate_render.py projects.db
```

**Résultat attendu :**
```
[MIGRATION] Base de données: maturation.db
[MIGRATION] Colonnes actuelles: 31
✓ Colonne organisme_tutelle_data ajoutée
✓ Colonne structure_soumissionnaire ajoutée

✓ Migration terminée avec succès

Vous pouvez maintenant redémarrer le service backend sur Render.
```

### Étape 3 : Redémarrer le Service (optionnel)

Le service Render devrait automatiquement utiliser les nouvelles colonnes. Si l'erreur persiste :

1. Dans le dashboard Render, aller sur le service backend
2. Cliquer sur **"Manual Deploy"** → **"Deploy latest commit"**
3. Attendre la fin du déploiement (2-3 minutes)

### Étape 4 : Vérifier que ça fonctionne

Ouvrir l'application : https://maturation-frontend.onrender.com

Se connecter avec le compte `asakho@outlook.com` et vérifier que :
- ✅ Le dashboard charge sans erreur 500
- ✅ La liste des projets s'affiche
- ✅ La soumission d'un nouveau projet fonctionne

---

## Alternative : Exécuter depuis votre ordinateur (si Shell Render ne fonctionne pas)

Si le Shell Render n'est pas disponible, vous pouvez exécuter la migration depuis votre ordinateur via SSH (si configuré) ou créer un script de migration automatique au démarrage.

### Option A : Ajouter la migration au démarrage du backend

Modifier `backend/app.py` pour exécuter la migration au démarrage :

```python
# Au début de app.py, après les imports
if __name__ == "__main__":
    # Exécuter migration automatique au démarrage
    import subprocess
    print("[STARTUP] Exécution des migrations...")
    try:
        subprocess.run(["python", "migrate_render.py"], check=True)
        print("[STARTUP] ✓ Migrations terminées")
    except Exception as e:
        print(f"[STARTUP] ⚠️ Erreur migration: {e}")

    # Démarrer l'application
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
```

**Puis pousser sur GitHub :**
```bash
git add backend/app.py
git commit -m "Auto-migration au démarrage"
git push origin main
```

Render déploiera automatiquement et exécutera la migration au démarrage.

---

## Vérification Post-Migration

Après la migration, vérifier dans les logs Render (section "Logs") que ces lignes apparaissent :

```
✓ Colonne organisme_tutelle_data ajoutée
✓ Colonne structure_soumissionnaire ajoutée
✓ Migration terminée avec succès
```

---

## Contact en Cas de Problème

Si vous rencontrez des difficultés :

1. **Vérifier les logs Render** : Dashboard → Service backend → Logs
2. **Erreur "table locked"** : Redémarrer le service backend
3. **Erreur "permission denied"** : Vérifier que `migrate_render.py` a les permissions d'exécution

**Support :** [Votre contact]
