# Système de Validation des Comptes - Documentation

## Vue d'ensemble

Ce document décrit le système de validation des comptes soumissionnaires implémenté pour la plateforme de maturation des projets publics de la DGPPE.

## Fonctionnalités

### 1. Inscription Simplifiée
- ✅ Email personnel accepté (Gmail, Yahoo, etc.)
- ✅ Upload de justificatif **facultatif**
- ✅ Accès immédiat après inscription (statut: non vérifié)
- ✅ Possibilité de soumettre des projets même sans vérification

### 2. Types de Structures
- Ministère / Direction nationale
- Région (14)
- Département (46)
- Commune (~100 principales)
- Agence / Établissement public (~23)
- Autre (ONG, Association, Cabinet)

### 3. Validation Multi-niveaux
Rôles pouvant valider les comptes :
- `admin`
- `secretariatsct`
- `presidencecomite`
- `presidencesct`

### 4. Statuts de Compte
- **🟡 Non vérifié** (par défaut) - Peut soumettre, projets marqués "Source non vérifiée"
- **✅ Vérifié** (après validation) - Accès complet, badge "Compte vérifié"
- **🔴 Suspendu** (action admin) - Ne peut plus soumettre

## Structure de la Base de Données

### Table `users` - Nouveaux champs ajoutés :

```sql
telephone VARCHAR(20)           -- Téléphone professionnel
fonction VARCHAR(255)           -- Fonction/Poste
type_structure VARCHAR(50)      -- Type de structure
nom_structure VARCHAR(255)      -- Nom de la structure
justificatif_path VARCHAR(500)  -- Chemin vers le justificatif (facultatif)
statut_compte VARCHAR(50)       -- Statut : 'non_verifie', 'verifie', 'suspendu'
date_verification TIMESTAMP     -- Date de validation
verifie_par VARCHAR(100)        -- Username du validateur
date_creation TIMESTAMP         -- Date de création du compte
```

## Listes de Données

### Fichiers créés :
- `backend/data_senegal.py` - Régions, départements, ministères, agences
- `backend/communes_senegal.py` - ~100 communes principales

### Contenu :
- **14 régions** du Sénégal
- **46 départements** organisés par région
- **24 ministères**
- **23 agences/établissements publics**
- **~100 communes** principales

## Flux d'Inscription et Validation

### Étape 1 : Inscription
1. Utilisateur remplit le formulaire (email personnel accepté)
2. Upload de justificatif (facultatif mais recommandé)
3. Compte créé immédiatement avec statut "non_verifie"
4. Peut soumettre des projets dès maintenant

### Étape 2 : Validation (par admin/secretariatsct/presidences)
1. Validateur accède au dashboard de gestion des comptes
2. Visualise les comptes "non vérifiés"
3. Examine le justificatif (si fourni)
4. Clic sur "✅ Vérifier" → compte passe à "verifie"
5. Email automatique envoyé à l'utilisateur

### Étape 3 : Utilisation
- **Compte vérifié** : Badge "✓" visible, projets traités normalement
- **Compte non vérifié** : Projets marqués "⚠️ Source non vérifiée" lors de l'évaluation

## Endpoints API (à implémenter)

### Backend (Flask)
```python
GET  /api/admin/users                    # Liste tous les comptes
POST /api/admin/users/<id>/verify        # Vérifier un compte
POST /api/admin/users/<id>/suspend       # Suspendre un compte
POST /api/users/upload-justificatif      # Upload justificatif (soumissionnaire)
GET  /api/data/regions                   # Liste des régions
GET  /api/data/departements              # Liste des départements
GET  /api/data/communes                  # Liste des communes
GET  /api/data/ministeres                # Liste des ministères
GET  /api/data/agences                   # Liste des agences
```

## Fichiers Modifiés/Créés

### Backend
- ✅ `migrations/add_user_validation_fields.sql` - Migration SQL
- ✅ `migrate_user_validation.py` - Script de migration
- ✅ `backend/data_senegal.py` - Listes de données
- ✅ `backend/communes_senegal.py` - Liste des communes
- ⏳ `backend/app.py` - Endpoints API (à compléter)

### Frontend
- ⏳ `frontend/src/views/Login.vue` - Formulaire d'inscription enrichi
- ⏳ `frontend/src/views/GestionComptes.vue` - Dashboard de validation (nouveau)
- ⏳ Badges de statut sur tous les dashboards

## Prochaines Étapes

1. ✅ Migration BDD - **TERMINÉ**
2. ✅ Listes de données - **TERMINÉ**
3. ⏳ Endpoints API backend - **EN COURS**
4. ⏳ Page d'inscription enrichie - **EN COURS**
5. ⏳ Dashboard de validation - **EN COURS**
6. ⏳ Badges de statut - **EN COURS**
7. ⏳ Tests complets - **À FAIRE**

## Notes Importantes

- **Justificatif facultatif** : Pas de blocage si l'utilisateur n'upload pas de document
- **Validation manuelle** : Tous les comptes nécessitent une validation humaine
- **4 rôles validateurs** : admin, secretariatsct, presidencecomite, presidencesct
- **Soumission possible sans vérification** : Favorise l'accessibilité tout en maintenant le contrôle qualité

---

*Document créé le 03/11/2025*
*Plateforme de Maturation des Projets Publics - DGPPE Sénégal*
