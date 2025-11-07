# Script pour renseigner le champ evaluateur_nom dans la table Project
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from app import app, db
from models import Project

# Mapping projet_id -> nom évaluateur
AFFECTATIONS = {
    1: "Agent DPSE 1",
    2: "Agent DPSE 2"
}

with app.app_context():
    for pid, nom in AFFECTATIONS.items():
        projet = Project.query.get(pid)
        if projet:
            projet.evaluateur_nom = nom
            db.session.commit()
            print(f"Projet {pid} mis à jour avec évaluateur : {nom}")
        else:
            print(f"Projet {pid} introuvable")
print("Mise à jour terminée.")
