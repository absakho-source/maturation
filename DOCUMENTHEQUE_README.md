# Documenthèque de Projet - Guide d'utilisation

## Vue d'ensemble

La fonctionnalité de **documenthèque** permet à tous les membres autorisés de la plateforme d'ajouter des fichiers supplémentaires à un projet soumis, et ce durant toute la présence du projet sur la plateforme.

## Objectifs

- **Enrichissement continu** : Permettre l'ajout de documents tout au long du cycle de vie du projet
- **Collaboration** : Tous les membres qui peuvent voir le projet peuvent contribuer à sa documentation
- **Traçabilité** : Chaque document est tracé avec son auteur, son rôle, et sa date d'ajout
- **Consultation permanente** : Les documents restent accessibles même après la fin du processus d'évaluation

## Qui peut ajouter des documents ?

Tous les utilisateurs ayant accès au projet peuvent ajouter des documents :
- **Soumissionnaires** : peuvent enrichir leur dossier
- **Évaluateurs** : peuvent ajouter des notes d'évaluation, analyses complémentaires
- **Secrétariat SCT** : peuvent ajouter des documents administratifs
- **Présidence SCT** : peuvent ajouter des recommandations
- **Présidence Comité** : peuvent ajouter des décisions ou notes
- **Membres du comité** : peuvent consulter et enrichir

## Fonctionnalités

### 1. Ajout de documents

Les utilisateurs peuvent :
- Ajouter un ou plusieurs fichiers simultanément
- Spécifier un type de document (note technique, étude, rapport, etc.)
- Ajouter une description optionnelle
- Voir une prévisualisation des fichiers avant envoi

**Types de documents supportés :**
- Documents : PDF, DOC, DOCX, TXT
- Tableurs : XLSX, XLS
- Images : JPG, JPEG, PNG

### 2. Consultation des documents

La documenthèque affiche pour chaque document :
- Le nom du fichier
- La taille du fichier
- Le type de document
- La description (si fournie)
- L'auteur et son rôle
- La date d'ajout

### 3. Gestion des documents

- **Téléchargement** : Tous les utilisateurs peuvent télécharger les documents
- **Suppression** : Seul l'auteur du document ou un administrateur peut le supprimer
- **Historique** : Chaque ajout/suppression est tracé dans l'historique du projet

## Architecture technique

### Backend

**Nouveau modèle de données : `DocumentProjet`**

```python
class DocumentProjet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    nom_fichier = db.Column(db.String(500))  # Nom stocké
    nom_original = db.Column(db.String(500))  # Nom original
    description = db.Column(db.Text)
    type_document = db.Column(db.String(100))
    auteur_nom = db.Column(db.String(100))
    auteur_role = db.Column(db.String(50))
    date_ajout = db.Column(db.DateTime)
    taille_fichier = db.Column(db.Integer)
```

**Nouvelles routes API :**

1. `GET /api/projects/<project_id>/documents`
   - Récupère tous les documents d'un projet
   - Retourne une liste de documents triés par date

2. `POST /api/projects/<project_id>/documents`
   - Ajoute un ou plusieurs documents
   - Paramètres : files, auteur_nom, auteur_role, description, type_document

3. `DELETE /api/projects/<project_id>/documents/<document_id>`
   - Supprime un document (admin ou auteur uniquement)
   - Supprime le fichier physique et l'entrée en base

### Frontend

**Nouveau composant : `DocumenthequeProjet.vue`**

Le composant est intégré dans la vue détails du projet (`ProjectDetail.vue`) et offre :
- Formulaire d'upload avec prévisualisation
- Liste des documents en grille responsive
- Actions (télécharger, supprimer avec permissions)
- Interface moderne et intuitive

## Migration de la base de données

Pour activer cette fonctionnalité sur une installation existante :

```bash
cd "/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation"
source venv/bin/activate
python3 migrate_documentheque.py
```

Ou directement :

```bash
cd backend
python3 -c "from app import app, db; from models import DocumentProjet; app.app_context().__enter__(); db.create_all(); print('✅ Migration réussie')"
```

## Sécurité et permissions

### Contrôle d'accès
- Les documents sont associés à un projet spécifique
- Seuls les utilisateurs ayant accès au projet peuvent voir ses documents
- La suppression est restreinte à l'auteur du document ou aux administrateurs

### Stockage des fichiers
- Les fichiers sont stockés dans le répertoire `backend/uploads/`
- Chaque fichier reçoit un nom unique avec timestamp : `DOC_YYYYMMDD_HHMMSS_filename`
- Les noms de fichiers sont sécurisés avec `secure_filename()`

### Traçabilité
- Chaque opération (ajout/suppression) est enregistrée dans l'historique du projet
- Les métadonnées incluent : auteur, rôle, date, taille

## Cas d'usage

### Scénario 1 : Enrichissement par le soumissionnaire
Un soumissionnaire reçoit une demande de compléments. Au lieu d'utiliser uniquement le système de compléments, il peut ajouter des documents à la documenthèque pour référence future.

### Scénario 2 : Notes d'évaluation
Un évaluateur peut ajouter des notes techniques ou des analyses complémentaires qui ne font pas partie de la fiche d'évaluation formelle mais qui peuvent être utiles pour le comité.

### Scénario 3 : Documentation administrative
Le secrétariat peut ajouter des documents administratifs, procès-verbaux, ou correspondances liées au projet.

### Scénario 4 : Archivage
Même après la décision finale, tous les documents restent accessibles pour consultation ultérieure, créant ainsi un dossier complet du projet.

## Avantages

1. **Centralisation** : Tous les documents liés au projet sont au même endroit
2. **Transparence** : Tous les membres peuvent voir qui a ajouté quoi et quand
3. **Flexibilité** : Pas de limitation sur le moment où les documents peuvent être ajoutés
4. **Pérennité** : Les documents restent disponibles tout au long du cycle de vie du projet
5. **Collaboration** : Favorise l'échange d'informations entre tous les acteurs

## Interface utilisateur

L'interface de la documenthèque comprend :

### Section d'ajout (formulaire)
- Sélection du type de document (optionnel)
- Zone de description (optionnelle)
- Upload de fichiers avec prévisualisation
- Bouton d'envoi avec indication de progression

### Section de consultation (grille)
- Cartes pour chaque document avec :
  - Icône de fichier
  - Nom cliquable pour téléchargement
  - Métadonnées (taille, type, auteur, date)
  - Description si présente
  - Boutons d'action (ouvrir, supprimer)

## Support et maintenance

Pour toute question ou problème concernant la documenthèque :
1. Vérifier que la table `documents_projet` existe dans la base
2. Vérifier les permissions du répertoire `backend/uploads/`
3. Consulter les logs du backend pour les erreurs d'upload
4. Vérifier que l'utilisateur est bien authentifié

## Évolutions futures possibles

- Catégorisation avancée des documents
- Recherche dans les documents
- Versioning des documents
- Notifications lors de l'ajout de documents
- Export de la documenthèque complète
- Aperçu des documents PDF dans l'interface
- Tags et étiquettes personnalisés
