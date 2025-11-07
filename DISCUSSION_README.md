# Espace de Discussion du Projet - Guide d'utilisation

## Vue d'ensemble

La fonctionnalité **Discussion du projet** offre un espace d'échange transparent entre le soumissionnaire et l'ensemble du comité d'évaluation. Elle permet des communications formelles et traçables tout au long du processus d'évaluation.

## Objectifs

- **Communication transparente** : Tous les échanges sont visibles par tous les participants autorisés
- **Traçabilité** : Chaque message est horodaté et attribué à son auteur avec son rôle
- **Questions/Réponses** : Facilite les demandes de clarifications et les réponses du soumissionnaire
- **Collaboration** : Permet au comité d'échanger également entre ses membres sur le projet
- **Permanence** : L'historique complet des échanges reste accessible

## Qui peut participer ?

Tous les utilisateurs ayant accès au projet peuvent participer à la discussion :

- **Soumissionnaires** : peuvent répondre aux questions et fournir des clarifications
- **Évaluateurs** : peuvent poser des questions et partager leurs observations
- **Secrétariat SCT** : peuvent communiquer des informations administratives
- **Présidence SCT** : peuvent demander des compléments d'information
- **Présidence Comité** : peuvent diriger la discussion
- **Membres du comité** : peuvent consulter et contribuer

## Fonctionnalités

### 1. Envoi de messages

Les utilisateurs peuvent :
- Écrire des messages en texte libre
- Utiliser **Ctrl + Entrée** pour envoyer rapidement
- Voir un aperçu de leur message avant l'envoi

**Format supporté :**
- Texte multiligne
- Espaces et retours à la ligne préservés
- Limite raisonnable de caractères

### 2. Lecture des messages

L'interface affiche :
- **Avatar coloré** : Chaque rôle a une couleur distinctive
- **Auteur et rôle** : Identification claire de qui parle
- **Date relative** : "Il y a 5 min", "Il y a 2h", etc.
- **Contenu du message** : Texte intégral formaté
- **Distinction visuelle** : Bordure bleue pour soumissionnaire, violette pour comité

### 3. Gestion des messages

- **Suppression** : Seul l'auteur ou un administrateur peut supprimer un message
- **Pas d'édition** : Pour garantir l'intégrité des échanges, les messages ne sont pas modifiables
- **Auto-refresh** : Les messages se rafraîchissent automatiquement toutes les 10 secondes
- **Auto-scroll** : L'affichage se positionne automatiquement sur les derniers messages

## Interface utilisateur

### Section de messages

L'interface de discussion comprend :

1. **En-tête** : Titre et description de l'espace
2. **Zone de messages** : Liste scrollable avec hauteur maximale de 500px
3. **Formulaire d'envoi** : Textarea et bouton d'envoi

### Design des messages

Chaque message affiche :

**Ligne 1 (En-tête) :**
- Avatar circulaire avec initiales (couleur selon rôle)
- Nom de l'auteur en gras
- Rôle de l'auteur en petit
- Date/heure relative
- Bouton de suppression (si autorisé)

**Ligne 2 (Contenu) :**
- Texte du message avec formatage préservé

### Codes couleur par rôle

- **Soumissionnaire** : Bleu (#3b82f6)
- **Évaluateur** : Violet (#8b5cf6)
- **Secrétariat SCT** : Vert (#10b981)
- **Présidence SCT** : Orange (#f59e0b)
- **Présidence Comité** : Rouge (#ef4444)
- **Administrateur** : Indigo (#6366f1)

## Architecture technique

### Backend

**Nouveau modèle de données : `MessageProjet`**

```python
class MessageProjet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    auteur_nom = db.Column(db.String(100))
    auteur_role = db.Column(db.String(50))
    contenu = db.Column(db.Text)
    date_creation = db.Column(db.DateTime)
    date_modification = db.Column(db.DateTime)  # Pour usage futur
```

**Nouvelles routes API :**

1. `GET /api/projects/<project_id>/messages`
   - Récupère tous les messages d'un projet
   - Triés par date (anciens en premier)

2. `POST /api/projects/<project_id>/messages`
   - Ajoute un nouveau message
   - Paramètres : auteur_nom, auteur_role, contenu

3. `DELETE /api/projects/<project_id>/messages/<message_id>`
   - Supprime un message (admin ou auteur uniquement)

### Frontend

**Nouveau composant : `DiscussionProjet.vue`**

Le composant est intégré dans la vue détails du projet (`ProjectDetail.vue`) et offre :
- Zone de discussion scrollable
- Formulaire d'envoi de message
- Rafraîchissement automatique toutes les 10s
- Interface responsive et moderne

**Features techniques :**
- Auto-scroll vers le bas lors de nouveaux messages
- Raccourci clavier Ctrl+Enter
- Gestion d'état (loading, sending)
- Formatage des dates relatives

## Migration de la base de données

Pour activer cette fonctionnalité sur une installation existante :

```bash
cd "/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation"
source venv/bin/activate
python3 migrate_discussion.py
```

Ou directement :

```bash
cd backend
python3 -c "from app import app, db; from models import MessageProjet; app.app_context().__enter__(); db.create_all(); print('✅ Migration réussie')"
```

## Sécurité et permissions

### Contrôle d'accès
- Les messages sont associés à un projet spécifique
- Seuls les utilisateurs ayant accès au projet peuvent voir ses messages
- La suppression est restreinte à l'auteur du message ou aux administrateurs

### Traçabilité
- Chaque message est enregistré avec son auteur et son rôle
- Chaque ajout/suppression génère une entrée dans l'historique du projet
- Les dates sont préservées avec précision

### Intégrité
- Les messages ne sont pas modifiables après envoi
- Chaque message est identifié de manière unique
- L'historique complet est permanent

## Cas d'usage

### Scénario 1 : Demande de clarification

Un évaluateur pose une question :
> "Pouvez-vous préciser le nombre de bénéficiaires prévus pour la première année ?"

Le soumissionnaire répond :
> "Nous prévoyons 150 bénéficiaires directs la première année, répartis sur 5 sites."

### Scénario 2 : Demande de complément

La présidence du comité demande :
> "Merci de fournir le CV détaillé du chef de projet mentionné page 12."

Le soumissionnaire confirme :
> "Le CV a été ajouté à la documenthèque du projet."

### Scénario 3 : Échange entre membres du comité

Un membre du comité partage :
> "J'ai consulté le projet similaire mentionné. Les résultats étaient encourageants."

Autre membre répond :
> "Merci pour cette vérification. Cela renforce la crédibilité de l'approche proposée."

### Scénario 4 : Communication administrative

Le secrétariat informe :
> "La date de présentation devant le comité est fixée au 15 novembre à 14h."

## Bonnes pratiques

### Pour les soumissionnaires
- Répondre rapidement aux questions posées
- Être précis et factuel dans les réponses
- Faire référence aux documents de la documenthèque si nécessaire
- Rester professionnel et courtois

### Pour le comité
- Poser des questions claires et précises
- Numéroter les questions multiples
- Laisser un délai raisonnable pour les réponses
- Remercier pour les informations fournies

### Pour tous
- Vérifier régulièrement les nouveaux messages
- Éviter les messages trop longs (privilégier les documents pour détails)
- Utiliser un langage professionnel
- Ne pas supprimer de messages sauf erreur manifeste

## Différences avec d'autres fonctionnalités

### Discussion vs Compléments
- **Compléments** : Demande formelle avec documents à fournir
- **Discussion** : Échange rapide, questions/réponses, clarifications

### Discussion vs Historique
- **Historique** : Actions automatiques du système
- **Discussion** : Messages intentionnels des utilisateurs

### Discussion vs Documenthèque
- **Documenthèque** : Fichiers et documents
- **Discussion** : Messages textuels courts

## Support et maintenance

Pour toute question ou problème concernant la discussion :
1. Vérifier que la table `messages_projet` existe dans la base
2. Vérifier l'authentification de l'utilisateur
3. Consulter les logs du backend pour les erreurs
4. Vérifier la connexion réseau pour le rafraîchissement auto

## Évolutions futures possibles

- Notifications push pour les nouveaux messages
- Mention d'utilisateurs avec @username
- Pièces jointes légères dans les messages
- Réponses en fil (threading)
- Recherche dans les messages
- Export de la discussion en PDF
- Marquage des messages comme importants
- Filtrage des messages par auteur ou rôle
- WebSocket pour mise à jour en temps réel (au lieu du polling)

## Conformité et archivage

L'espace de discussion fait partie intégrante du dossier du projet :
- Tous les messages sont archivés
- L'historique complet est préservé même après décision finale
- Les messages peuvent être exportés avec le reste du projet
- La traçabilité complète est garantie pour audit

---

**Note** : Cette fonctionnalité complète l'arsenal d'outils collaboratifs de la plateforme et vise à faciliter une communication transparente et efficace entre toutes les parties prenantes.
