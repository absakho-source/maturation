"""
Script pour créer la table des ministères et initialiser la liste par défaut
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from models import Ministere

with app.app_context():
    print("[CREATE MINISTERES] Création de la table ministere...")

    # Créer la table si elle n'existe pas
    db.create_all()

    print("[CREATE MINISTERES] ✅ Table créée avec succès!")

    # Vérifier si des ministères existent déjà
    count = Ministere.query.count()
    if count > 0:
        print(f"[CREATE MINISTERES] ⚠️  {count} ministères existent déjà. Pas d'initialisation.")
        sys.exit(0)

    # Liste des ministères du Sénégal (gouvernement actuel)
    ministeres = [
        {"nom": "Ministère des Affaires étrangères et des Sénégalais de l'Extérieur", "abr": "MAESE"},
        {"nom": "Ministère des Forces armées", "abr": "MFA"},
        {"nom": "Ministère de l'Intérieur et de la Sécurité publique", "abr": "MISP"},
        {"nom": "Ministère de la Justice", "abr": "MJ"},
        {"nom": "Ministère de l'Économie, du Plan et de la Coopération", "abr": "MEPC"},
        {"nom": "Ministère des Finances et du Budget", "abr": "MFB"},
        {"nom": "Ministère de l'Hydraulique et de l'Assainissement", "abr": "MHA"},
        {"nom": "Ministère de l'Énergie, du Pétrole et des Mines", "abr": "MEPM"},
        {"nom": "Ministère de l'Agriculture, de la Souveraineté alimentaire et de l'Élevage", "abr": "MASAE"},
        {"nom": "Ministère de l'Industrie et du Commerce", "abr": "MIC"},
        {"nom": "Ministère des Infrastructures et des Transports terrestres et aériens", "abr": "MITTA"},
        {"nom": "Ministère de la Pêche et des Infrastructures maritimes et portuaires", "abr": "MPIMP"},
        {"nom": "Ministère de l'Urbanisme, des Collectivités territoriales et de l'Aménagement des territoires", "abr": "MUCTAT"},
        {"nom": "Ministère de la Santé et de l'Action sociale", "abr": "MSAS"},
        {"nom": "Ministère de l'Éducation nationale", "abr": "MEN"},
        {"nom": "Ministère de l'Enseignement supérieur, de la Recherche et de l'Innovation", "abr": "MESRI"},
        {"nom": "Ministère de la Formation professionnelle", "abr": "MFP"},
        {"nom": "Ministère de la Jeunesse, des Sports et de la Culture", "abr": "MJSC"},
        {"nom": "Ministère de la Famille et des Solidarités", "abr": "MFS"},
        {"nom": "Ministère du Travail et de la Fonction publique", "abr": "MTFP"},
        {"nom": "Ministère de l'Environnement et de la Transition écologique", "abr": "METE"},
        {"nom": "Ministère du Tourisme et de l'Artisanat", "abr": "MTA"},
        {"nom": "Ministère de la Communication, des Télécommunications et du Numérique", "abr": "MCTN"},
    ]

    print(f"[CREATE MINISTERES] Initialisation de {len(ministeres)} ministères...")

    for idx, min_data in enumerate(ministeres, 1):
        ministere = Ministere(
            nom_complet=min_data["nom"],
            abreviation=min_data["abr"],
            actif=True,
            ordre=idx
        )
        db.session.add(ministere)

    db.session.commit()

    print(f"[CREATE MINISTERES] ✅ {len(ministeres)} ministères initialisés avec succès!")
