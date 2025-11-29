"""
Script pour créer la table des ministères et initialiser la liste par défaut
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def init_ministeres():
    """Initialise les ministères par défaut si la table est vide"""
    from models import Ministere, db

    # Vérifier si des ministères existent déjà
    count = Ministere.query.count()
    if count > 0:
        print(f"[INIT MINISTERES] {count} ministères existent déjà. Pas d'initialisation.")
        return

    # Liste des ministères du Sénégal (ordre protocolaire)
    ministeres = [
        {"nom": "Ministère de la Justice", "abr": "MJ"},
        {"nom": "Ministère de l'Énergie, du Pétrole et des Mines", "abr": "MEPM"},
        {"nom": "Ministère de l'Intégration Africaine, des Affaires étrangères et des Sénégalais de l'Extérieur", "abr": "MIAESE"},
        {"nom": "Ministère des Forces Armées", "abr": "MFA"},
        {"nom": "Ministère de l'Intérieur et de la Sécurité publique", "abr": "MISP"},
        {"nom": "Ministère de l'Économie, du Plan et de la Coopération", "abr": "MEPC"},
        {"nom": "Ministère des Finances et du Budget", "abr": "MFB"},
        {"nom": "Ministère de l'Enseignement supérieur, de la Recherche et de l'Innovation", "abr": "MESRI"},
        {"nom": "Ministère des Transports Terrestres et Aériens", "abr": "MTTA"},
        {"nom": "Ministère de la Communication, des Télécommunications et du Numérique", "abr": "MCTN"},
        {"nom": "Ministère de l'Éducation Nationale", "abr": "MEN"},
        {"nom": "Ministère de l'Agriculture, de la Souveraineté Alimentaire et de l'Élevage", "abr": "MASAE"},
        {"nom": "Ministère de l'Hydraulique et de l'Assainissement", "abr": "MHA"},
        {"nom": "Ministère de la Santé et de l'Hygiène Publique", "abr": "MSHP"},
        {"nom": "Ministère de la Famille, de l'Action sociale et des Solidarités", "abr": "MFASS"},
        {"nom": "Ministère de l'Emploi et de la Formation Professionnelle et Technique", "abr": "MEFPT"},
        {"nom": "Ministère de l'Environnement et de la Transition Écologique", "abr": "METE"},
        {"nom": "Ministère de l'Urbanisme, des Collectivités territoriales et de l'Aménagement des Territoires", "abr": "MUCTAT"},
        {"nom": "Ministère de l'Industrie et du Commerce", "abr": "MIC"},
        {"nom": "Ministère des Pêches et de l'Économie Maritime", "abr": "MPEM"},
        {"nom": "Ministère de la Fonction Publique, du Travail et de la Réforme du Service Public", "abr": "MFPTRSP"},
        {"nom": "Ministère de la Jeunesse et des Sports", "abr": "MJS"},
        {"nom": "Ministère de la Microfinance et de l'Économie Sociale et Solidaire", "abr": "MMESS"},
        {"nom": "Ministère des Infrastructures", "abr": "MI"},
        {"nom": "Ministère de la Culture, de l'Artisanat et du Tourisme", "abr": "MCAT"},
    ]

    print(f"[INIT MINISTERES] Initialisation de {len(ministeres)} ministères...")

    for idx, min_data in enumerate(ministeres, 1):
        ministere = Ministere(
            nom_complet=min_data["nom"],
            abreviation=min_data["abr"],
            actif=True,
            ordre=idx
        )
        db.session.add(ministere)

    db.session.commit()

    print(f"[INIT MINISTERES] ✅ {len(ministeres)} ministères initialisés avec succès!")

if __name__ == "__main__":
    from app import app, db
    with app.app_context():
        print("[CREATE MINISTERES] Création de la table ministere...")
        db.create_all()
        print("[CREATE MINISTERES] ✅ Table créée avec succès!")
        init_ministeres()
