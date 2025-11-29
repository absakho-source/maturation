# Améliorations Plateforme PLASMAP - 2025

## Résumé des améliorations apportées

Ce document décrit les améliorations majeures apportées à la plateforme de soumission et maturation de projets publics (PLASMAP) de la DGPPE.

---

## 1. Nettoyage et Organisation du Code ✅

### 1.1 Fichiers Obsolètes Supprimés

Les fichiers de test et debug suivants ont été supprimés :
- `test_ai_integration.py` - Test pour fonctionnalité AI désactivée
- `check_logs_production.py` - Script de diagnostic temporaire
- `check_production_sector.py` - Script de diagnostic temporaire
- `diagnose_project.py` - Script de diagnostic temporaire
- `fix_avis_terminologie.py` - Script one-off déjà appliqué
- `fix_dgppe_25_003_avis.py` - Script one-off déjà appliqué
- `fix_reassigned_project.py` - Script one-off déjà appliqué
- `fix_rejected_status.py` - Script one-off déjà appliqué
- `fix_stale_decision_finale.py` - Script one-off déjà appliqué

**Impact** : Code plus propre, moins de confusion

### 1.2 Organisation des Migrations

**24 scripts de migration** déplacés dans `backend/migrations/` :
- `add_*.py` (11 fichiers) - Ajout de colonnes
- `migrate_*.py` (6 fichiers) - Migrations de données
- `create_*.py` (3 fichiers) - Création de tables
- `init_*.py` (2 fichiers) - Initialisation
- `update_*.py`, `reset_*.py`, `clean_*.py` - Scripts de maintenance

**Localisation** : `/backend/migrations/`

**Impact** : Structure plus claire, migrations faciles à trouver

---

## 2. Export CSV/Excel des Projets ✅

### Fonctionnalité

Export complet de la liste des projets au format CSV compatible Excel.

### Endpoints API

**`GET /api/export/projects/csv`**
- Exporte tous les projets avec filtres optionnels
- Paramètres query :
  - `statut` - Filtrer par statut
  - `secteur` - Filtrer par secteur
  - `poles` - Filtrer par pôle territorial
- Headers requis : `X-Role`, `X-Username`
- Accès : admin, secretariatsct, presidencesct, presidencecomite, evaluateur

**`GET /api/export/evaluations/csv`**
- Exporte toutes les fiches d'évaluation
- Paramètre query : `statut_projet`
- Headers requis : `X-Role`, `X-Username`
- Accès : admin, secretariatsct, presidencesct, presidencecomite

### Données Exportées (Projets)

- Numéro de projet
- Titre
- Secteur
- Pôles territoriaux
- Coût estimatif (FCFA)
- Statut
- Soumissionnaire
- Évaluateur
- Avis
- Décision finale
- Date de soumission
- Organisme
- Structure
- Ministère de tutelle
- Région / Département / Commune

### Données Exportées (Évaluations)

- Informations du projet
- Évaluateur et date
- Score total (/100)
- Détail des 12 critères de notation
- Avis, proposition, recommandations

### Interface Utilisateur

**Nouveau bouton dans AdminDashboard** :
- Bouton "Exporter CSV" (vert)
- Respecte les filtres actifs
- Téléchargement direct avec nom horodaté

**Fichiers modifiés** :
- `backend/routes/export_routes.py` (nouveau)
- `backend/app.py` (enregistrement blueprint)
- `frontend/src/views/AdminDashboard.vue` (bouton + méthode)

**Format** : UTF-8 avec BOM pour compatibilité Excel

---

## 3. Système de Notifications Email ✅

### Fonctionnalité

Envoi automatique d'emails aux utilisateurs lors d'événements importants.

### Service Email

**Fichier** : `backend/utils/email_service.py`

**Classe** : `EmailService`
- Support SMTP (Gmail, SendGrid, Mailgun, etc.)
- Templates HTML professionnels
- Mode debug (affichage sans envoi)
- Activation/désactivation par configuration

### Types de Notifications Email

1. **Assignation d'évaluation** (`evaluation_assignee`)
   - Envoyé à l'évaluateur
   - Template : Email vert avec bouton "Commencer l'évaluation"

2. **Décision finale** (`decision_finale`)
   - Envoyé au soumissionnaire
   - Template : Email violet avec couleur de décision (vert/rouge)

3. **Nouveau projet** (`nouveau_projet`)
   - Envoyé aux administrateurs
   - Template : Email bleu avec détails du projet

### Configuration

**Variables d'environnement** (voir `CONFIGURATION_EMAILS.md`) :

```bash
EMAIL_ENABLED=true                    # Activer les emails
EMAIL_DEBUG_MODE=false                # Mode production
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre.email@gmail.com
SMTP_PASSWORD=mot_de_passe_app
SMTP_FROM_EMAIL=noreply@dgppe.sn
SMTP_FROM_NAME=PLASMAP - DGPPE
FRONTEND_URL=https://maturation-frontend.onrender.com
```

### Intégration

**Fichiers modifiés** :
- `backend/utils/email_service.py` (nouveau) - Service email
- `backend/routes/notification_routes.py` - Intégration dans `create_notification()`
- `CONFIGURATION_EMAILS.md` (nouveau) - Documentation complète

**Logique** :
- Email envoyé si `priorite_email=True` OU `EMAIL_SEND_ALL=true`
- Ne bloque pas la création de notification en cas d'échec email
- Logs détaillés pour debugging

---

## 4. Versioning des Projets ✅

### Fonctionnalité

Historique complet des modifications apportées à un projet avec possibilité de restauration.

### Table de Base de Données

**Table** : `project_version`

**Colonnes** :
- `id` - ID unique de la version
- `project_id` - Référence au projet
- `version_number` - Numéro de version (incrémental)
- `modified_at` - Date/heure de modification
- `modified_by` - Utilisateur ayant modifié
- `modification_type` - Type ('creation', 'update', 'status_change', etc.)
- `change_summary` - Description des modifications
- `project_data` - Snapshot complet du projet (JSON)
- `statut_before` - Statut avant modification
- `statut_after` - Statut après modification

**Indexes** :
- `idx_project_version_project_id` - Recherche par projet
- `idx_project_version_modified_at` - Tri chronologique

### Modèle

**Fichier** : `backend/models.py`
**Classe** : `ProjectVersion`

### Utilitaires

**Fichier** : `backend/utils/project_versioning.py`

**Fonctions** :
- `create_project_version()` - Créer une version snapshot
- `get_project_versions()` - Récupérer toutes les versions
- `get_project_version()` - Récupérer une version spécifique
- `compare_versions()` - Comparer deux versions
- `restore_project_version()` - Restaurer une version antérieure

### Endpoints API

**`GET /api/projects/<id>/versions`**
- Liste toutes les versions d'un projet
- Retourne : `{versions: [...], total: N}`

**`GET /api/projects/versions/<version_id>`**
- Détails d'une version spécifique
- Retourne le snapshot complet du projet

**`POST /api/projects/versions/compare`**
- Compare deux versions
- Body : `{version_id_1: X, version_id_2: Y}`
- Retourne les différences champ par champ

**`POST /api/projects/<id>/restore/<version_id>`**
- Restaure un projet à une version antérieure
- Accès : admin, secretariatsct uniquement
- Crée deux nouvelles versions : 'pre_restore' et 'restore'

### Types de Versions

- `creation` - Création initiale du projet
- `update` - Modification des données du projet
- `status_change` - Changement de statut
- `evaluation` - Évaluation soumise
- `pre_restore` - Sauvegarde avant restauration
- `restore` - Restauration effectuée

### Fichiers Créés/Modifiés

- `backend/migrations/add_project_versions_table.py` (nouveau) - Migration
- `backend/models.py` - Ajout modèle `ProjectVersion`
- `backend/utils/project_versioning.py` (nouveau) - Utilitaires
- `backend/routes/versioning_routes.py` (nouveau) - Routes API
- `backend/app.py` - Import modèle et enregistrement blueprint

---

## 5. Corrections CORS ✅

### Problème

Headers personnalisés `X-Role` et `X-Username` bloqués par politique CORS.

### Solution

Ajout des headers dans la configuration CORS :

**Fichier** : `backend/app.py`

**Modifications** :
- Ligne 66 : `"allow_headers": [..., "X-Role", "X-Username"]`
- Ligne 85 : `Access-Control-Allow-Headers` inclut `X-Role, X-Username`

**Impact** : API fonctionnelle avec authentification par headers

---

## 6. Archivage des PDFs ✅

### Problème

Ancien PDF de fiche d'évaluation supprimé au lieu d'être archivé lors de modification.

### Solution

Remplacement de `os.remove()` par appel à `archiver_fiche()`.

**Fichier** : `backend/routes/evaluation_routes.py` (lignes 499-507)

**Logique** :
1. Vérifier si ancien PDF existe
2. Appeler `archiver_fiche()` pour créer archive versionnée
3. Générer nouveau PDF
4. Archive conserve : `{projet}_v{version}_{timestamp}_modification_{user}.pdf`

**Impact** : Traçabilité complète, aucune perte de données

---

## Résumé des Fichiers Créés

### Backend

1. `backend/migrations/` (dossier)
   - 24 scripts de migration déplacés
   - `add_project_versions_table.py` (nouveau)

2. `backend/routes/export_routes.py` - Export CSV
3. `backend/routes/versioning_routes.py` - Versioning API
4. `backend/utils/email_service.py` - Service email
5. `backend/utils/project_versioning.py` - Utilitaires versioning

### Frontend

- `frontend/src/views/AdminDashboard.vue` - Ajout bouton export + styles

### Documentation

1. `CONFIGURATION_EMAILS.md` - Guide configuration emails
2. `AMELIORATIONS_2025.md` - Ce document

---

## Résumé des Fichiers Modifiés

### Backend

1. `backend/app.py`
   - Import `ProjectVersion`
   - Enregistrement blueprints (export, versioning)
   - Configuration CORS (headers X-Role, X-Username)

2. `backend/models.py`
   - Ajout modèle `ProjectVersion`

3. `backend/routes/evaluation_routes.py`
   - Archivage PDF au lieu de suppression

4. `backend/routes/notification_routes.py`
   - Import `email_service`
   - Intégration emails dans `create_notification()`

### Frontend

1. `frontend/src/views/AdminDashboard.vue`
   - Bouton "Exporter CSV"
   - Méthode `exporterProjetsCSV()`
   - Styles CSS pour bouton export

---

## Tests Recommandés

### Export CSV
1. Se connecter en tant qu'admin
2. Aller sur "Tous les projets"
3. Appliquer des filtres (statut, secteur)
4. Cliquer sur "Exporter CSV"
5. Vérifier que le fichier CSV contient les projets filtrés
6. Ouvrir dans Excel et vérifier encodage UTF-8

### Emails
1. Configurer variables SMTP dans Render.com
2. Mettre `EMAIL_ENABLED=true` et `EMAIL_DEBUG_MODE=false`
3. Assigner une évaluation à un utilisateur avec email
4. Vérifier réception email
5. Prendre une décision finale
6. Vérifier email au soumissionnaire

### Versioning
1. Créer un nouveau projet
2. Modifier le projet plusieurs fois
3. Appeler `GET /api/projects/{id}/versions`
4. Vérifier que toutes les versions sont listées
5. Comparer deux versions
6. Restaurer une version antérieure (en tant qu'admin)
7. Vérifier que le projet a été restauré correctement

---

## Prochaines Étapes Recommandées (Optionnel)

### Court Terme

1. **Tests automatisés**
   - Implémenter pytest pour backend
   - Tests unitaires pour export, email, versioning

2. **Documentation API**
   - Générer documentation Swagger/OpenAPI
   - Documenter tous les endpoints

3. **Interface Versioning**
   - Composant Vue pour afficher historique versions
   - Comparaison visuelle des différences
   - Bouton de restauration dans interface admin

### Moyen Terme

1. **Recherche avancée**
   - Filtres sauvegardés
   - Recherche full-text
   - Facettes de recherche

2. **Notifications push**
   - Activer socket.io pour notifications temps réel
   - Badge de notifications dans header

3. **Rapports personnalisés**
   - Générateur de rapports avec filtres
   - Scheduling de rapports automatiques
   - Templates de rapports personnalisables

### Long Terme

1. **Internationalisation**
   - Support multi-langue (français, anglais)
   - Système de traduction

2. **API publique**
   - Endpoints publics pour intégrations externes
   - Authentification OAuth2
   - Rate limiting

3. **Mobile App**
   - Application mobile native
   - Notifications push natives

---

## Configuration de Production

### Variables d'Environnement à Ajouter sur Render.com

```bash
# Emails
EMAIL_ENABLED=true
EMAIL_DEBUG_MODE=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=notifications@dgppe.sn
SMTP_PASSWORD=xxxx_xxxx_xxxx_xxxx
SMTP_FROM_EMAIL=noreply@dgppe.sn
SMTP_FROM_NAME=PLASMAP - DGPPE
FRONTEND_URL=https://maturation-frontend.onrender.com
```

### Migrations à Exécuter

```bash
# Sur le serveur de production
cd /root/maturation/backend
python3 migrations/add_project_versions_table.py
```

### Redémarrage Requis

Après déploiement, redémarrer les services Render.com pour :
- Charger nouveaux blueprints
- Appliquer configuration CORS
- Activer service email

---

## Support

Pour toute question ou problème :
1. Consulter les documentations (`.md`)
2. Vérifier les logs du backend
3. Contacter l'équipe technique

**Date de mise à jour** : 2025-01-29
**Version de la plateforme** : 2.0
