# Présentation PLASMAP
## Plateforme de Soumission et Maturation des Projets

---

## Slide 1 : Page de titre

**PLASMAP**
Plateforme de Soumission et Maturation des Projets

Direction Générale de la Planification et des Politiques Économiques (DGPPE)

*[Capture d'écran : Page d'accueil https://maturation-frontend.onrender.com]*

---

## Slide 2 : Contexte et Objectifs

### Contexte
- Besoin de digitaliser le processus de soumission et d'évaluation des projets de développement
- Améliorer la traçabilité et la transparence des décisions
- Faciliter la coordination entre les différents acteurs

### Objectifs
- Centraliser les soumissions de projets
- Automatiser le workflow d'évaluation
- Permettre le suivi en temps réel des projets
- Générer des rapports et fiches d'évaluation

---

## Slide 3 : Architecture de la Plateforme

### Technologies utilisées
- **Frontend** : Vue.js 3 (Composition API)
- **Backend** : Flask (Python)
- **Base de données** : SQLite / PostgreSQL
- **Hébergement** : Render.com

### Points forts
- Interface responsive (mobile-friendly)
- API RESTful
- Génération automatique de PDF
- Système de rôles et permissions

---

## Slide 4 : Les Rôles Utilisateurs

| Rôle | Description |
|------|-------------|
| **Soumissionnaire** | Soumet des projets, suit leur avancement |
| **Point Focal** | Coordonne les projets de son organisme de tutelle |
| **Évaluateur** | Évalue les projets assignés |
| **Secrétariat SCT** | Gère les assignations, vérifie les évaluations |
| **Présidence SCT** | Valide les évaluations, prend les décisions |
| **Présidence Comité** | Décision finale sur les projets |
| **Administrateur** | Gestion des comptes et configuration |

*[Capture d'écran : Page de connexion avec les différents rôles]*

---

## Slide 5 : Inscription et Création de Compte

### Processus d'inscription
1. Remplir le formulaire d'inscription
2. Sélectionner le type de structure (Institution, Collectivité, Agence, Autre)
3. Fournir les informations de contact
4. Upload des justificatifs (optionnel)
5. Validation par le Secrétariat SCT

### Types de structures supportés
- Institutions gouvernementales (Présidence, Primature, Ministères)
- Collectivités territoriales (Régions, Départements, Communes)
- Agences et établissements publics
- Autres structures

*[Capture d'écran : Formulaire d'inscription complet]*

---

## Slide 6 : Dashboard Soumissionnaire

### Fonctionnalités
- Vue d'ensemble des projets soumis
- Statistiques personnelles (projets soumis, en cours, validés)
- Accès rapide à la soumission de nouveaux projets
- Suivi du statut de chaque projet

### Point Focal
- Encart spécial pour les Points Focaux
- Accès aux projets sous leur tutelle
- Vue consolidée de tous les projets de l'organisme

*[Capture d'écran : Dashboard soumissionnaire avec l'encart Point Focal]*

---

## Slide 7 : Soumission d'un Projet

### Informations requises
- **Identification** : Titre, description, secteur d'activité
- **Localisation** : Pôle territorial, région, département
- **Budget** : Coût estimatif, sources de financement
- **Calendrier** : Durée prévue, phases du projet
- **Documents** : Pièces jointes, études préalables

### Validation automatique
- Numéro de projet généré automatiquement (DGPPE-YYYY-XXX)
- Vérification des champs obligatoires
- Upload sécurisé des fichiers

*[Capture d'écran : Formulaire de soumission de projet]*

---

## Slide 8 : Les Pôles Territoriaux

### 6 Pôles de développement
1. **Pôle Dakar** : Dakar, Thiès
2. **Pôle Centre** : Diourbel, Fatick, Kaolack, Kaffrine
3. **Pôle Nord** : Saint-Louis, Louga
4. **Pôle Nord-Est** : Matam, Tambacounda
5. **Pôle Sud-Est** : Kédougou
6. **Pôle Sud** : Ziguinchor, Sédhiou, Kolda

### Visualisation cartographique
- Carte interactive des pôles
- Statistiques par pôle
- Filtrage des projets par localisation

*[Capture d'écran : Carte des pôles territoriaux avec statistiques]*

---

## Slide 9 : Workflow d'Évaluation

### Étapes du processus
1. **Soumission** → Projet créé par le soumissionnaire
2. **Assignation** → Secrétariat SCT assigne les évaluateurs
3. **Évaluation** → Les évaluateurs remplissent leur grille
4. **Vérification** → Secrétariat vérifie les évaluations
5. **Validation SCT** → Présidence SCT valide
6. **Décision finale** → Présidence Comité statue

### Statuts possibles
- Soumis → Assigné → En évaluation → Évalué → Validé/Rejeté

*[Capture d'écran : Diagramme du workflow ou vue timeline d'un projet]*

---

## Slide 10 : Interface Secrétariat SCT

### Fonctionnalités principales
- Liste de tous les projets soumis
- Assignation des évaluateurs aux projets
- Suivi des évaluations en cours
- Vérification et validation des évaluations
- Gestion des comptes utilisateurs
- Tableau de bord statistique

### Actions disponibles
- Assigner/Réassigner des évaluateurs
- Demander des compléments d'information
- Transmettre à la Présidence SCT

*[Capture d'écran : Dashboard Secrétariat SCT]*

---

## Slide 11 : Interface Évaluateur

### Grille d'évaluation
- Critères prédéfinis et pondérés
- Notes sur échelle standardisée
- Commentaires et recommandations
- Upload de documents complémentaires

### Fiche d'évaluation détaillée
- Évaluation complète du projet
- Recommandations techniques
- Avis motivé (Favorable/Défavorable)

*[Capture d'écran : Formulaire d'évaluation avec grille de critères]*

---

## Slide 12 : Génération de Documents

### Documents générés automatiquement
- **Fiche de projet** : Synthèse complète du projet
- **Fiche d'évaluation** : Résultats de l'évaluation
- **Procès-verbal** : Décisions du comité

### Format et export
- Export PDF professionnel
- En-tête DGPPE officiel
- Numérotation et traçabilité
- Téléchargement direct

*[Capture d'écran : Exemple de fiche PDF générée]*

---

## Slide 13 : Système de Discussion

### Communication intégrée
- Fil de discussion par projet
- Échanges entre soumissionnaire et évaluateurs
- Notifications en temps réel
- Historique complet des échanges

### Fonctionnalités
- Messages texte
- Pièces jointes
- Visibilité contrôlée par rôle

*[Capture d'écran : Interface de discussion d'un projet]*

---

## Slide 14 : Documenthèque

### Gestion des documents
- Upload de documents supplémentaires
- Catégorisation par type
- Contrôle de visibilité par rôle
- Historique des versions

### Types de documents
- Documents initiaux (soumission)
- Documents complémentaires
- Rapports d'évaluation
- Documents administratifs

*[Capture d'écran : Section documenthèque d'un projet]*

---

## Slide 15 : Administration

### Gestion des comptes
- Création/modification des utilisateurs
- Attribution des rôles
- Vérification des comptes
- Nomination des Points Focaux

### Configuration
- Éditeur de formulaire dynamique
- Gestion des ministères et structures
- Logs de connexion
- Paramètres système

*[Capture d'écran : Interface d'administration]*

---

## Slide 16 : Sécurité et Traçabilité

### Mesures de sécurité
- Authentification sécurisée
- Contrôle d'accès par rôle
- Journalisation des actions
- Sauvegarde des données

### Traçabilité
- Historique complet des modifications
- Logs de connexion
- Audit trail des décisions
- Archivage des projets

*[Capture d'écran : Page des logs de connexion]*

---

## Slide 17 : Statistiques et Rapports

### Tableaux de bord
- Nombre de projets par statut
- Répartition par pôle territorial
- Évolution temporelle
- Performance des évaluateurs

### Indicateurs clés
- Taux de validation
- Délai moyen d'évaluation
- Budget total des projets
- Répartition sectorielle

*[Capture d'écran : Dashboard avec graphiques statistiques]*

---

## Slide 18 : Responsive Design

### Accessibilité multi-appareils
- Interface adaptative
- Navigation mobile optimisée
- Fonctionnalités complètes sur tablette
- Notifications push (à venir)

*[Captures d'écran : Même page sur desktop, tablette et mobile]*

---

## Slide 19 : Évolutions Futures

### Fonctionnalités planifiées
- Intégration avec d'autres systèmes gouvernementaux
- Module de géolocalisation avancé
- Tableau de bord BI intégré
- Application mobile native
- Notifications par email/SMS
- Signature électronique

### Améliorations continues
- Retours utilisateurs
- Optimisation des performances
- Nouvelles fonctionnalités métier

---

## Slide 20 : Conclusion

### Bénéfices de PLASMAP
- **Efficacité** : Réduction des délais de traitement
- **Transparence** : Suivi en temps réel
- **Traçabilité** : Historique complet
- **Collaboration** : Communication facilitée
- **Qualité** : Évaluations standardisées

### Contact
- URL : https://maturation-frontend.onrender.com
- Support : [email de support]

**Merci de votre attention !**

---

## Guide pour les captures d'écran

### Captures recommandées
1. Page d'accueil
2. Page de connexion
3. Formulaire d'inscription complet
4. Dashboard soumissionnaire avec encart Point Focal
5. Formulaire de soumission de projet
6. Carte des pôles territoriaux
7. Dashboard Secrétariat SCT
8. Formulaire d'évaluation
9. Fiche PDF générée
10. Interface de discussion
11. Documenthèque
12. Interface d'administration
13. Logs de connexion
14. Vue mobile responsive

### Conseils
- Utiliser des données de démonstration réalistes
- Flouter les informations sensibles
- Capturer en haute résolution (1920x1080 minimum)
- Maintenir une cohérence visuelle
