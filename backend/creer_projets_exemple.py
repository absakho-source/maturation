#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour créer 10 projets crédibles dans la base de données
Tous soumis par 'soumissionnaire' avec statut 'soumis'
"""

import sys
import os
from datetime import datetime

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Project

# Liste des pôles territoriaux du Sénégal
POLES = [
    "Dakar-Thiès",
    "Kaolack-Kaffrine",
    "Saint-Louis-Louga",
    "Diourbel-Louga",
    "Tambacounda-Kédougou",
    "Ziguinchor-Sédhiou-Kolda",
    "Fatick-Kaolack"
]

# Secteurs de planification
SECTEURS = [
    "agriculture-élevage-pêche",
    "éducation-formation",
    "santé-action-sociale",
    "eau-assainissement",
    "énergie",
    "industrie-artisanat",
    "mines-géologie",
    "commerce",
    "tourisme-loisirs-sports",
    "transport-désenclavement",
    "télécommunications-TIC",
    "environnement-développement-durable",
    "urbanisme-habitat-aménagement",
    "justice-droits-humains",
    "gouvernance-décentralisation"
]

# Projets à créer (titres crédibles et descriptions)
PROJETS_DATA = [
    {
        "titre": "Construction d'un centre de formation agricole moderne à Kaolack",
        "description": "Projet visant à créer un centre de formation équipé pour former 500 jeunes par an aux techniques agricoles modernes, à l'agro-écologie et à l'entrepreneuriat agricole. Le centre comprendra des salles de classe, un laboratoire, des champs d'application et un incubateur d'entreprises agricoles.",
        "secteur": "agriculture-élevage-pêche",
        "poles": "Kaolack-Kaffrine",
        "cout_estimatif": 2500000000,
        "structure_soumissionnaire": "Direction Régionale du Développement Rural de Kaolack"
    },
    {
        "titre": "Aménagement hydro-agricole de la vallée du Saloum",
        "description": "Aménagement de 1000 hectares de terres agricoles avec système d'irrigation moderne, construction de digues anti-sel, et création de pistes de production. Le projet bénéficiera à 800 producteurs et permettra 3 cycles de culture par an.",
        "secteur": "agriculture-élevage-pêche",
        "poles": "Fatick-Kaolack",
        "cout_estimatif": 8500000000,
        "structure_soumissionnaire": "Agence Nationale d'Aménagement du Territoire"
    },
    {
        "titre": "Électrification rurale par énergie solaire - Zone Nord",
        "description": "Installation de mini-centrales solaires et réseaux de distribution dans 45 villages de la zone Nord (Saint-Louis et Louga). Le projet vise à électrifier 15000 ménages et 200 équipements communautaires (écoles, centres de santé, mosquées).",
        "secteur": "énergie",
        "poles": "Saint-Louis-Louga",
        "cout_estimatif": 12000000000,
        "structure_soumissionnaire": "Agence Sénégalaise d'Électrification Rurale"
    },
    {
        "titre": "Construction de 10 collèges de proximité en zone rurale",
        "description": "Construction de 10 collèges d'enseignement moyen dans les zones rurales mal desservies de Tambacounda et Kédougou. Chaque établissement comprendra 12 salles de classe, un laboratoire, une bibliothèque, des logements pour enseignants et un terrain de sport. Capacité totale: 5000 élèves.",
        "secteur": "éducation-formation",
        "poles": "Tambacounda-Kédougou",
        "cout_estimatif": 15000000000,
        "structure_soumissionnaire": "Ministère de l'Éducation Nationale"
    },
    {
        "titre": "Modernisation du réseau d'adduction d'eau potable de Thiès",
        "description": "Réhabilitation et extension du réseau d'eau potable de la ville de Thiès: construction d'un nouveau réservoir de 10000m³, remplacement de 50km de canalisations vétustes, installation de 3000 nouveaux branchements sociaux, et mise en place d'un système de télégestion.",
        "secteur": "eau-assainissement",
        "poles": "Dakar-Thiès",
        "cout_estimatif": 6800000000,
        "structure_soumissionnaire": "Société Nationale des Eaux du Sénégal"
    },
    {
        "titre": "Centre hospitalier régional spécialisé de Ziguinchor",
        "description": "Construction d'un centre hospitalier de 200 lits avec services de chirurgie, maternité, pédiatrie, réanimation et imagerie médicale. Le projet inclut la formation de 150 personnels de santé et l'acquisition d'équipements médicaux de pointe.",
        "secteur": "santé-action-sociale",
        "poles": "Ziguinchor-Sédhiou-Kolda",
        "cout_estimatif": 18500000000,
        "structure_soumissionnaire": "Ministère de la Santé et de l'Action Sociale"
    },
    {
        "titre": "Plateforme industrielle de transformation agroalimentaire de Diourbel",
        "description": "Création d'une zone industrielle dédiée à la transformation des produits agricoles (arachide, mil, sorgho). Infrastructure comprenant: unités de transformation, entrepôts frigorifiques, laboratoire de contrôle qualité, station de traitement des eaux, et centre de formation. Création de 800 emplois directs.",
        "secteur": "industrie-artisanat",
        "poles": "Diourbel-Louga",
        "cout_estimatif": 25000000000,
        "structure_soumissionnaire": "Agence de Promotion des Investissements et des Grands Travaux"
    },
    {
        "titre": "Bitumage de la route Tambacounda - Kédougou",
        "description": "Réhabilitation et bitumage de 150km de route nationale reliant Tambacounda à Kédougou, avec construction de 8 ponts, aménagement de passages pour le bétail, éclairage des traversées de villages, et création d'aires de repos. Durée des travaux: 24 mois.",
        "secteur": "transport-désenclavement",
        "poles": "Tambacounda-Kédougou",
        "cout_estimatif": 45000000000,
        "structure_soumissionnaire": "Agence des Travaux et de Gestion des Routes"
    },
    {
        "titre": "Projet d'assainissement urbain de Saint-Louis",
        "description": "Construction d'un réseau d'assainissement des eaux usées et pluviales pour 25000 ménages, réalisation d'une station d'épuration de 15000m³/jour, aménagement de caniveaux et bassins de rétention. Le projet inclut un volet sensibilisation à l'hygiène et à l'environnement.",
        "secteur": "eau-assainissement",
        "poles": "Saint-Louis-Louga",
        "cout_estimatif": 16500000000,
        "structure_soumissionnaire": "Office National de l'Assainissement du Sénégal"
    },
    {
        "titre": "Centre de formation professionnelle aux métiers du numérique",
        "description": "Construction et équipement d'un centre de formation de 400 places aux métiers du numérique (développement web, cybersécurité, data science, design graphique). Le centre disposera de salles informatiques équipées, d'espaces de coworking, d'un incubateur de startups et d'une connexion internet haut débit. Partenariats avec entreprises du secteur.",
        "secteur": "télécommunications-TIC",
        "poles": "Dakar-Thiès",
        "cout_estimatif": 3200000000,
        "structure_soumissionnaire": "Agence de l'Informatique de l'État"
    }
]

def creer_projets():
    """Créer les 10 projets dans la base de données"""

    with app.app_context():
        print("🚀 Début de la création des projets...")
        print("=" * 70)

        projets_crees = 0

        for i, projet_data in enumerate(PROJETS_DATA, 1):
            try:
                # Créer le projet
                projet = Project(
                    titre=projet_data["titre"],
                    description=projet_data["description"],
                    secteur=projet_data["secteur"],
                    poles=projet_data["poles"],
                    cout_estimatif=projet_data["cout_estimatif"],
                    structure_soumissionnaire=projet_data["structure_soumissionnaire"],
                    auteur_nom="soumissionnaire",
                    statut="soumis",
                    date_soumission=datetime.utcnow(),
                    # Données par défaut
                    niveau_priorite="standard",
                    nouveaute="projet_initial"
                )

                db.session.add(projet)
                db.session.commit()

                print(f"✅ Projet {i}/10 créé: {projet.titre[:60]}...")
                print(f"   📍 Pôle: {projet.poles}")
                print(f"   🏢 Secteur: {projet.secteur}")
                print(f"   💰 Coût: {projet.cout_estimatif:,} FCFA")
                print()

                projets_crees += 1

            except Exception as e:
                print(f"❌ Erreur lors de la création du projet {i}: {e}")
                db.session.rollback()

        print("=" * 70)
        print(f"✅ Création terminée: {projets_crees}/10 projets créés avec succès")

        # Afficher les statistiques
        total_projets = Project.query.filter_by(statut="soumis").count()
        print(f"📊 Total de projets 'soumis' dans la base: {total_projets}")

        return True

if __name__ == "__main__":
    success = creer_projets()
    sys.exit(0 if success else 1)
