# Configuration de la Corbeille (Soft Delete)

## Fonctionnement

Le système de **soft delete** protège contre les suppressions accidentelles :

1. Quand un admin supprime un projet → il est **marqué comme supprimé** (`deleted_at` = date actuelle)
2. Le projet disparaît de toutes les vues normales
3. Le projet apparaît dans l'onglet **Corbeille** de l'admin
4. Le projet peut être **restauré** à tout moment depuis la corbeille
5. Après **12 mois**, le projet est **automatiquement supprimé définitivement** (si configuré)

## Suppression Automatique

### Script de nettoyage

Le script `cleanup_old_deleted_projects.py` supprime définitivement les projets dans la corbeille depuis plus de 12 mois.

**Exécution manuelle :**
```bash
cd backend
source venv/bin/activate
python cleanup_old_deleted_projects.py
```

### Configuration automatique (Cron)

Pour exécuter le nettoyage automatiquement chaque jour à 2h du matin :

1. Ouvrir le crontab :
```bash
crontab -e
```

2. Ajouter cette ligne :
```bash
0 2 * * * cd /chemin/vers/maturation/backend && source venv/bin/activate && python cleanup_old_deleted_projects.py >> /var/log/corbeille_cleanup.log 2>&1
```

**Remplacer** `/chemin/vers/maturation/backend` par le chemin réel.

### Autres options de planification

**Tous les lundis à 3h :**
```bash
0 3 * * 1 cd /chemin/vers/maturation/backend && source venv/bin/activate && python cleanup_old_deleted_projects.py
```

**Le 1er de chaque mois à minuit :**
```bash
0 0 1 * * cd /chemin/vers/maturation/backend && source venv/bin/activate && python cleanup_old_deleted_projects.py
```

## Modifier la durée de rétention

Pour changer la durée de conservation (par défaut 12 mois) :

1. Éditer `cleanup_old_deleted_projects.py`
2. Modifier la ligne :
```python
RETENTION_MONTHS = 12  # Changer cette valeur
```

3. Mettre à jour le message dans l'interface :
   - Fichier : `frontend/src/views/AdminDashboard.vue`
   - Ligne : rechercher "12 mois"

## Endpoints API de la Corbeille

### Lister les projets supprimés
```bash
GET /api/admin/corbeille
```

### Restaurer un projet
```bash
POST /api/admin/corbeille/{project_id}/restore?username=admin
```

### Supprimer définitivement un projet
```bash
DELETE /api/admin/corbeille/{project_id}/delete-permanent
```

### Vider toute la corbeille
```bash
POST /api/admin/corbeille/vider
```

## Logs et Monitoring

Consulter les logs de nettoyage :
```bash
tail -f /var/log/corbeille_cleanup.log
```

## Sécurité

- ✅ Seuls les admins peuvent accéder à la corbeille
- ✅ La suppression définitive nécessite une double confirmation
- ✅ Toutes les opérations sont tracées dans l'historique
- ✅ Les projets récents (< 12 mois) ne sont jamais supprimés automatiquement

## Troubleshooting

**Le script ne trouve pas la base de données :**
```bash
# Définir la variable d'environnement DATA_DIR
export DATA_DIR=/chemin/vers/maturation/backend
python cleanup_old_deleted_projects.py
```

**Voir combien de projets seront supprimés (sans les supprimer) :**
Modifier temporairement le script pour commenter la ligne `db.session.commit()`.
