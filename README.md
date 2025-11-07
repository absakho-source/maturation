# Plateforme de Maturation - DGPPE

Plateforme de soumission et de gestion des projets de maturation pour la Direction Générale de la Planification des Politiques Économiques (DGPPE).

## Architecture

- **Backend**: Flask (Python) - API REST
- **Frontend**: Vue.js 3 - Interface utilisateur
- **Base de données**: SQLite (dev) / PostgreSQL (production recommandé)

## Développement Local

### Prérequis
- Python 3.11+
- Node.js 18+
- npm ou yarn

### Installation Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Le backend démarre sur http://localhost:5000

### Installation Frontend

```bash
cd frontend
npm install
npm run dev
```

Le frontend démarre sur http://localhost:5173

## Déploiement sur Render.com

### Étape 1: Préparer le dépôt Git

```bash
# Initialiser Git si pas déjà fait
git init
git add .
git commit -m "Initial commit - Plateforme de maturation DGPPE"
```

### Étape 2: Créer un dépôt GitHub

1. Allez sur https://github.com et créez un nouveau dépôt
2. Suivez les instructions pour pousser votre code:

```bash
git remote add origin https://github.com/VOTRE_USERNAME/VOTRE_REPO.git
git branch -M main
git push -u origin main
```

### Étape 3: Déployer sur Render

1. Allez sur https://render.com et connectez-vous
2. Cliquez sur "New" → "Blueprint"
3. Connectez votre dépôt GitHub
4. Render détectera automatiquement le fichier `render.yaml` et créera les services

### Étape 4: Configuration des variables d'environnement

Le fichier `render.yaml` configure automatiquement les services, mais vous pouvez ajouter:

**Backend:**
- `DATABASE_URL`: URL de la base de données PostgreSQL (si vous utilisez une DB externe)
- `SECRET_KEY`: Clé secrète pour les sessions Flask
- `FLASK_ENV`: production

**Frontend:**
- `VITE_API_URL`: URL du backend (configurée automatiquement)

### Étape 5: Workflow de développement

Pour garder la flexibilité de modification en local tout en ayant une version en ligne:

1. **Développement local**: Modifiez le code localement
2. **Test local**: Testez avec `./lancer_serveurs.sh`
3. **Commit**: `git add . && git commit -m "Description des changements"`
4. **Push**: `git push` - Render redéploiera automatiquement!

## Structure du Projet

```
maturation/
├── backend/
│   ├── app.py              # Application Flask principale
│   ├── models.py           # Modèles de base de données
│   ├── db.py               # Configuration DB
│   ├── requirements.txt    # Dépendances Python
│   └── start.sh           # Script de démarrage Render
├── frontend/
│   ├── src/
│   │   ├── views/         # Pages Vue.js
│   │   ├── components/    # Composants réutilisables
│   │   └── assets/        # Ressources statiques
│   ├── package.json       # Dépendances npm
│   └── vite.config.js     # Configuration Vite
├── render.yaml            # Configuration Render
├── .gitignore
└── README.md
```

## Rôles Utilisateurs

- **Soumissionnaire**: Soumet des projets
- **Évaluateur**: Évalue les projets (DPSE)
- **Secrétariat SCT**: Valide les évaluations
- **Présidence SCT**: Décision finale sur les projets
- **Présidence Comité**: Confirmation finale
- **Admin**: Gestion complète de la plateforme

## Fonctionnalités Principales

- Soumission de projets avec fiches détaillées
- Workflow de validation multi-niveaux
- Tableaux de bord personnalisés par rôle
- Génération de rapports et statistiques
- Cartes interactives des pôles territoriaux
- Gestion des comptes utilisateurs
- Export PDF des projets

## Support

Pour toute question ou problème, contactez l'équipe de développement.

---
Développé par Abou Sakho pour la DGPPE • Version 1.0
