# Manuel de Procédure PLASMAP
## Plateforme de Soumission et Maturation des Projets

**Direction Générale de la Planification et des Politiques Économiques (DGPPE)**

**Version 1.0 - Novembre 2024**

---

## Table des matières

1. [Introduction](#1-introduction)
2. [Accès à la plateforme](#2-accès-à-la-plateforme)
3. [Rôles et permissions](#3-rôles-et-permissions)
4. [Procédures par rôle](#4-procédures-par-rôle)
   - [Soumissionnaire](#41-soumissionnaire)
   - [Point Focal](#42-point-focal)
   - [Évaluateur](#43-évaluateur)
   - [Secrétariat SCT](#44-secrétariat-sct)
   - [Présidence SCT](#45-présidence-sct)
   - [Présidence Comité](#46-présidence-comité)
   - [Administrateur](#47-administrateur)
5. [Workflow des projets](#5-workflow-des-projets)
6. [Système de notifications](#6-système-de-notifications)
7. [Gestion documentaire](#7-gestion-documentaire)
8. [Annexes](#8-annexes)

---

## 1. Introduction

### 1.1 Objectif du manuel

Ce manuel décrit les procédures d'utilisation de PLASMAP, la plateforme de soumission et de maturation des projets de la DGPPE. Il s'adresse à tous les utilisateurs de la plateforme et détaille les processus de soumission, d'évaluation et de validation des projets.

### 1.2 Présentation de la plateforme

PLASMAP est une application web permettant de :
- Centraliser les soumissions de projets de développement
- Automatiser le workflow d'évaluation
- Assurer la traçabilité des décisions
- Faciliter la communication entre les acteurs
- Générer des documents officiels (fiches d'évaluation, rapports)

### 1.3 Accès à la plateforme

- **URL de production** : https://maturation-frontend.onrender.com
- **Navigateurs supportés** : Chrome, Firefox, Safari, Edge (versions récentes)
- **Compatibilité mobile** : Interface responsive adaptée aux tablettes et smartphones

---

## 2. Accès à la plateforme

### 2.1 Création d'un compte

1. Accéder à la page d'accueil
2. Cliquer sur **"S'inscrire"**
3. Remplir le formulaire d'inscription :
   - Identifiant (email professionnel recommandé)
   - Mot de passe
   - Nom complet
   - Téléphone
   - Fonction
   - Type de structure (Institution, Collectivité, Agence, Autre)
   - Détails de la structure selon le type sélectionné
4. Joindre un justificatif (optionnel mais recommandé)
5. Valider l'inscription

**Note importante** : Le compte sera en statut "Non vérifié" jusqu'à validation par le Secrétariat SCT ou un Administrateur.

### 2.2 Connexion

1. Accéder à la page de connexion
2. Saisir l'identifiant et le mot de passe
3. Cliquer sur **"Se connecter"**

### 2.3 Récupération de mot de passe

En cas d'oubli de mot de passe, contacter l'Administrateur de la plateforme.

---

## 3. Rôles et permissions

### 3.1 Tableau des rôles

| Rôle | Description | Permissions principales |
|------|-------------|------------------------|
| **Soumissionnaire** | Soumet des projets | Créer des projets, suivre l'avancement, répondre aux demandes de compléments |
| **Point Focal** | Coordonne les projets d'un organisme | Visualiser tous les projets de son organisme de tutelle |
| **Évaluateur** | Évalue les projets assignés | Remplir les fiches d'évaluation, donner un avis |
| **Secrétariat SCT** | Gère le flux des projets | Assigner des évaluateurs, vérifier les évaluations, gérer les comptes |
| **Présidence SCT** | Valide les évaluations | Valider ou renvoyer les évaluations |
| **Présidence Comité** | Décision finale | Rendre la décision finale sur les projets |
| **Administrateur** | Gestion technique | Configuration système, gestion des comptes, logs |

### 3.2 Hiérarchie des accès

```
Administrateur
    └── Secrétariat SCT
        └── Présidence SCT
            └── Présidence Comité
                └── Évaluateur
                    └── Soumissionnaire / Point Focal
```

---

## 4. Procédures par rôle

### 4.1 Soumissionnaire

#### 4.1.1 Soumettre un nouveau projet

**Prérequis** : Compte vérifié

1. Se connecter à la plateforme
2. Cliquer sur **"+ Nouveau projet"** dans le tableau de bord
3. Remplir le formulaire de soumission :

   **Informations générales**
   - Intitulé du projet (obligatoire)
   - Description détaillée
   - Secteur d'activité

   **Localisation**
   - Pôle territorial
   - Région(s) concernée(s)
   - Département(s)

   **Données financières**
   - Coût estimatif
   - Sources de financement envisagées

   **Documents obligatoires**
   - Lettre de soumission signée (PDF)
   - Note conceptuelle du projet (PDF)
   - Études ou plans techniques (PDF)

4. Cocher la certification d'exactitude des informations
5. Cliquer sur **"Soumettre le projet"**

**Note** : Si des champs obligatoires sont manquants, toutes les erreurs seront affichées simultanément pour correction.

#### 4.1.2 Suivre ses projets

1. Accéder au tableau de bord
2. Consulter la liste des projets avec leurs statuts
3. Cliquer sur **"Voir détails"** pour accéder à la page du projet

#### 4.1.3 Répondre à une demande de compléments

1. Recevoir une notification de demande de compléments
2. Accéder à la page du projet
3. Consulter le message de demande dans la section Discussion
4. Préparer les documents demandés
5. Utiliser la section **"Fournir des compléments"** pour :
   - Ajouter un message explicatif
   - Joindre les documents complémentaires
6. Valider l'envoi

#### 4.1.4 Participer aux discussions

1. Accéder à la page du projet
2. Utiliser la section **"Discussion"** pour :
   - Lire les messages des évaluateurs
   - Répondre aux questions
   - Apporter des clarifications

### 4.2 Point Focal

#### 4.2.1 Accéder aux projets de l'organisme

1. Se connecter avec un compte Point Focal
2. Cliquer sur **"Voir les projets de mon organisme"** dans l'encart dédié
3. Consulter la liste de tous les projets sous sa tutelle

#### 4.2.2 Filtrer et rechercher

1. Utiliser les filtres par statut (Soumis, Assigné, En évaluation, etc.)
2. Utiliser la barre de recherche pour trouver un projet spécifique

#### 4.2.3 Consulter les statistiques

Le tableau de bord affiche :
- Total des projets de l'organisme
- Nombre de projets par statut
- Projets avec avis favorable/défavorable

### 4.3 Évaluateur

#### 4.3.1 Consulter les projets assignés

1. Se connecter à la plateforme
2. Le tableau de bord affiche la liste des projets assignés
3. Les projets sont classés par priorité et date d'assignation

#### 4.3.2 Commencer une évaluation

1. Sélectionner un projet à évaluer
2. Cliquer sur **"Commencer l'évaluation"**
3. Consulter tous les documents du projet dans la Documenthèque

#### 4.3.3 Remplir la fiche d'évaluation

1. Accéder à la **"Fiche d'évaluation détaillée"**
2. Compléter toutes les sections :

   **I. Présentation du projet**
   - Origine du projet (Maturation, Offre spontanée, Autres)
   - Typologie (Productif, Appui à la production, Social, Environnemental)
   - Intitulé et porteur du projet
   - Localisation et coût

   **II. Analyse technique**
   - Pertinence du projet
   - Faisabilité technique
   - Viabilité économique
   - Impact environnemental et social

   **III. Recommandations**
   - Points forts identifiés
   - Points de vigilance
   - Recommandations pour amélioration

   **IV. Avis final**
   - Favorable / Défavorable / Favorable avec réserves
   - Justification de l'avis

3. Cliquer sur **"Sauvegarder"** pour enregistrer le brouillon
4. Cliquer sur **"Soumettre l'évaluation"** une fois terminé

#### 4.3.4 Générer le PDF de la fiche d'évaluation

1. Une fois l'évaluation soumise
2. Cliquer sur **"Télécharger PDF"**
3. Le document est généré avec l'en-tête officiel DGPPE

#### 4.3.5 Utiliser la discussion

1. Poser des questions au soumissionnaire si nécessaire
2. Les messages sont visibles par toutes les parties concernées

### 4.4 Secrétariat SCT

#### 4.4.1 Tableau de bord

Le tableau de bord affiche :
- Statistiques des projets (par statut, par pôle)
- Métriques de performance (délai moyen, taux de validation)
- Liste des projets à traiter

#### 4.4.2 Assigner des évaluateurs

1. Sélectionner un projet au statut "Soumis"
2. Cliquer sur **"Assigner"**
3. Choisir un ou plusieurs évaluateurs dans la liste
4. Valider l'assignation

Le projet passe au statut "Assigné" et les évaluateurs sont notifiés.

#### 4.4.3 Vérifier les évaluations

1. Consulter les projets au statut "Évalué"
2. Examiner la fiche d'évaluation remplie
3. Vérifier la cohérence et la complétude
4. Actions possibles :
   - **Transmettre à la Présidence SCT** si l'évaluation est satisfaisante
   - **Renvoyer à l'évaluateur** avec des commentaires si des corrections sont nécessaires

#### 4.4.4 Demander des compléments

1. Accéder à la page du projet
2. Cliquer sur **"Demander des compléments"**
3. Rédiger un message précisant les documents ou informations manquants
4. Valider la demande

Le soumissionnaire est notifié et le statut passe à "Compléments requis".

#### 4.4.5 Gérer les comptes utilisateurs

1. Accéder à **"Gestion des comptes"**
2. Consulter la liste des comptes avec leur statut
3. Actions disponibles :
   - **Vérifier** : Activer un compte non vérifié
   - **Suspendre** : Désactiver temporairement un compte
   - **Réintégrer** : Réactiver un compte suspendu
   - **Supprimer** : Supprimer définitivement un compte

4. Cliquer sur **"Détails"** pour voir :
   - Informations complètes de l'utilisateur
   - Justificatif fourni
   - Projets soumis (pour les soumissionnaires)

#### 4.4.6 Nommer un Point Focal

1. Dans les détails d'un compte
2. Activer l'option **"Désigner comme Point Focal"**
3. L'organisme de tutelle est automatiquement déterminé
4. Sauvegarder les modifications

### 4.5 Présidence SCT

#### 4.5.1 Valider les évaluations

1. Consulter les projets transmis par le Secrétariat
2. Examiner l'évaluation et les documents
3. Actions possibles :
   - **Valider** : Approuver l'évaluation et transmettre au Comité
   - **Renvoyer** : Demander des modifications au Secrétariat

#### 4.5.2 Consulter les statistiques

Le tableau de bord présente :
- Vue d'ensemble des projets par statut
- Performance du processus d'évaluation

### 4.6 Présidence Comité

#### 4.6.1 Rendre la décision finale

1. Consulter les projets validés par la Présidence SCT
2. Examiner l'ensemble du dossier
3. Rendre la décision :
   - **Favorable** : Projet approuvé
   - **Défavorable** : Projet rejeté
   - **Ajourné** : Décision reportée
4. Ajouter une justification si nécessaire

#### 4.6.2 Générer les procès-verbaux

Les décisions sont archivées et peuvent être exportées en PDF.

### 4.7 Administrateur

#### 4.7.1 Gestion des comptes

Toutes les fonctionnalités du Secrétariat SCT, plus :
- Modification des rôles utilisateurs
- Accès à tous les comptes sans restriction

#### 4.7.2 Configuration du formulaire

1. Accéder à **"Éditeur de formulaire"**
2. Modifier les champs du formulaire de soumission
3. Ajouter/supprimer des options dans les listes déroulantes

#### 4.7.3 Gestion des ministères

1. Accéder à **"Éditeur des ministères"**
2. Ajouter, modifier ou désactiver des ministères
3. Les modifications sont immédiatement disponibles dans les formulaires

#### 4.7.4 Consulter les logs de connexion

1. Accéder à **"Logs de connexion"**
2. Consulter l'historique des connexions
3. Filtrer par utilisateur, date ou statut

---

## 5. Workflow des projets

### 5.1 Cycle de vie d'un projet

```
SOUMIS
   │
   ▼
ASSIGNÉ ←──────────────┐
   │                   │
   ▼                   │
EN ÉVALUATION          │
   │                   │
   ▼                   │
ÉVALUÉ                 │
   │                   │
   ├─── [Renvoi] ──────┘
   │
   ▼
VÉRIFIÉ
   │
   ├─── [Compléments requis] ───► COMPLÉMENTS DEMANDÉS
   │                                      │
   │                              COMPLÉMENTS FOURNIS
   │                                      │
   │    ◄─────────────────────────────────┘
   ▼
VALIDÉ SCT
   │
   ▼
DÉCISION FINALE
   │
   ├─── FAVORABLE
   ├─── DÉFAVORABLE
   └─── AJOURNÉ
```

### 5.2 Statuts détaillés

| Statut | Description | Acteur responsable |
|--------|-------------|-------------------|
| Soumis | Projet déposé, en attente d'assignation | Secrétariat SCT |
| Assigné | Évaluateur(s) désigné(s) | Évaluateur |
| En évaluation | Évaluation en cours | Évaluateur |
| Évalué | Évaluation terminée | Secrétariat SCT |
| Compléments demandés | Informations supplémentaires requises | Soumissionnaire |
| Compléments fournis | Réponse du soumissionnaire | Secrétariat SCT |
| Validé SCT | Approuvé par la Présidence SCT | Présidence Comité |
| Favorable | Décision finale positive | - |
| Défavorable | Décision finale négative | - |
| Ajourné | Décision reportée | - |

### 5.3 Délais indicatifs

- **Assignation** : 48h après soumission
- **Évaluation** : 5 jours ouvrés
- **Validation SCT** : 48h après évaluation
- **Décision finale** : Variable selon calendrier du Comité

---

## 6. Système de notifications

### 6.1 Types de notifications

| Type | Destinataire | Déclencheur |
|------|-------------|-------------|
| Nouveau compte | Admin, Secrétariat | Création d'un compte |
| Projet soumis | Secrétariat | Soumission d'un projet |
| Assignation | Évaluateur | Assignation à un projet |
| Évaluation terminée | Secrétariat | Soumission d'une évaluation |
| Compléments requis | Soumissionnaire | Demande de compléments |
| Changement de statut | Soumissionnaire | Évolution du projet |
| Nouveau message | Concernés | Message dans la discussion |

### 6.2 Consulter les notifications

1. Cliquer sur l'icône cloche dans la barre de navigation
2. Le badge rouge indique le nombre de notifications non lues
3. Cliquer sur une notification pour :
   - La marquer comme lue
   - Accéder au contenu concerné

### 6.3 Gérer les notifications

- **Marquer comme lu** : Cliquer sur la coche
- **Tout marquer comme lu** : Bouton dans l'en-tête du menu
- **Voir plus** : Charger les notifications plus anciennes

---

## 7. Gestion documentaire

### 7.1 Documents obligatoires à la soumission

1. **Lettre de soumission** : Document officiel signé par l'autorité compétente
2. **Note conceptuelle** : Description détaillée du projet
3. **Études/Plans techniques** : Documents techniques justificatifs

### 7.2 Documenthèque du projet

Chaque projet dispose d'une documenthèque permettant de :
- Consulter tous les documents associés
- Télécharger les fichiers
- Ajouter des documents complémentaires
- Contrôler la visibilité des documents par rôle

### 7.3 Types de documents

| Type | Description | Ajouté par |
|------|-------------|-----------|
| Initial | Documents de la soumission | Soumissionnaire |
| Complément | Documents supplémentaires | Soumissionnaire |
| Évaluation | Fiches d'évaluation | Évaluateur |
| Administratif | Documents de suivi | Secrétariat |

### 7.4 Génération de PDF

La plateforme génère automatiquement :
- **Fiche de projet** : Synthèse des informations du projet
- **Fiche d'évaluation** : Rapport d'évaluation complet
- **Procès-verbal** : Décision du comité

Les PDF incluent l'en-tête officiel DGPPE et sont numérotés.

---

## 8. Annexes

### 8.1 Les pôles territoriaux

| Pôle | Régions |
|------|---------|
| Pôle Dakar | Dakar, Thiès |
| Pôle Centre | Diourbel, Fatick, Kaolack, Kaffrine |
| Pôle Nord | Saint-Louis, Louga |
| Pôle Nord-Est | Matam, Tambacounda |
| Pôle Sud-Est | Kédougou |
| Pôle Sud | Ziguinchor, Sédhiou, Kolda |

### 8.2 Secteurs d'activité

- Agriculture et élevage
- Pêche et aquaculture
- Industrie et transformation
- Commerce et services
- Énergie
- Transport et infrastructures
- Eau et assainissement
- Santé
- Éducation et formation
- Environnement
- Tourisme
- TIC et économie numérique
- Artisanat

### 8.3 Glossaire

- **DGPPE** : Direction Générale de la Planification et des Politiques Économiques
- **SCT** : Sous-Comité Technique
- **Point Focal** : Représentant désigné d'un organisme
- **Maturation** : Processus d'accompagnement des projets vers leur réalisation
- **Avis favorable** : Recommandation positive pour la réalisation du projet
- **Avis défavorable** : Recommandation négative

### 8.4 Contacts et support

- **Support technique** : support@dgppe.gouv.sn
- **Questions fonctionnelles** : secretariat.sct@dgppe.gouv.sn

### 8.5 Historique des versions

| Version | Date | Modifications |
|---------|------|---------------|
| 1.0 | Novembre 2024 | Version initiale |

---

**Document rédigé par la DGPPE**
**Tous droits réservés**
