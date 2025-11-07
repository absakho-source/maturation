import random
from app import app
from models import db, Project, User

EXAMPLE_TITLES = [
    "Projet Agricole Innovant",
    "Développement Touristique Local",
    "Plateforme Éducation Numérique",
    "Centre de Santé Communautaire",
    "Réseau d'Énergie Verte",
    "Valorisation des Déchets",
    "Incubateur d'Entreprises",
    "Programme d'Appui Social",
    "Modernisation des Transports",
    "Projet Culturel Territorial"
]

with app.app_context():
    # Crée un utilisateur test si nécessaire
    user = User.query.filter_by(username="testuser").first()
    if not user:
        user = User(username="testuser", password="testpass", role="soumissionnaire", display_name="Test User")
        db.session.add(user)
        db.session.commit()

    for i, title in enumerate(EXAMPLE_TITLES):
        projet = Project(
            numero_projet=f"202510{i+1:02d}",
            titre=title,
            description=f"Description du projet {title}",
            secteur=random.choice(["Agriculture", "Tourisme", "Éducation", "Santé", "Énergie", "Environnement", "Entrepreneuriat", "Social", "Transport", "Culture"]),
            poles="Pôle A",
            cout_estimatif=random.randint(10000, 100000),
            budget=random.randint(5000, 90000),
            statut="soumis",
            soumissionnaire_id=user.id,
            organisme_tutelle="Ministère de l'Exemple",
            origine_projet="{\"maturation\": true}",
            typologie_projet="{\"productif\": true}"
        )
        db.session.add(projet)
    db.session.commit()
    print("10 projets exemples créés.")
