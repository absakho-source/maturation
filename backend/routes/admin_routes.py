"""
Routes d'administration pour opérations sensibles
À utiliser uniquement par les administrateurs
"""

from flask import jsonify, request
from models import Project
from functools import wraps

def admin_required(f):
    """Decorator pour vérifier que l'utilisateur est admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Vérifier le token admin dans les headers
        admin_token = request.headers.get('X-Admin-Token')

        # Token de sécurité (à changer en production)
        ADMIN_TOKEN = "DGPPE-ADMIN-2025-RESET"

        if admin_token != ADMIN_TOKEN:
            return jsonify({"error": "Accès non autorisé"}), 403

        return f(*args, **kwargs)
    return decorated_function

def register_admin_routes(app, db):
    """Enregistrer les routes d'administration"""

    @app.route('/api/admin/reset-projects', methods=['POST'])
    @admin_required
    def reset_projects():
        """
        Supprimer tous les projets
        Nécessite le header X-Admin-Token
        """
        try:
            # Compter les projets avant suppression
            count_avant = Project.query.count()

            # Supprimer tous les projets
            Project.query.delete()
            db.session.commit()

            return jsonify({
                "success": True,
                "message": f"{count_avant} projet(s) supprimé(s) avec succès",
                "count": count_avant
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/admin/create-test-projects', methods=['POST'])
    @admin_required
    def create_test_projects():
        """
        Créer les 10 projets de test
        Nécessite le header X-Admin-Token
        """
        try:
            from datetime import datetime

            # Données des projets (copié de creer_projets_exemple.py)
            PROJETS_DATA = [
                {
                    "titre": "Construction d'un centre de formation agricole moderne à Kaolack",
                    "description": "Projet visant à créer un centre de formation équipé pour former 500 jeunes par an aux techniques agricoles modernes.",
                    "secteur": "agriculture-élevage-pêche",
                    "poles": "Centre (Kaolack, Fatick, Kaffrine)",
                    "cout_estimatif": 2500000000,
                    "structure_soumissionnaire": "Direction Régionale du Développement Rural de Kaolack",
                    "niveau_priorite": "haute_priorite",
                    "nouveaute": "projet_initial"
                },
                {
                    "titre": "Aménagement hydro-agricole de la vallée du Saloum",
                    "description": "Aménagement de 1000 hectares de terres agricoles dans la vallée du Saloum avec système d'irrigation moderne.",
                    "secteur": "agriculture-élevage-pêche",
                    "poles": "Centre (Kaolack, Fatick, Kaffrine)",
                    "cout_estimatif": 8500000000,
                    "structure_soumissionnaire": "Agence Nationale d'Aménagement du Territoire",
                    "niveau_priorite": "urgence",
                    "nouveaute": "projet_initial"
                },
                {
                    "titre": "Électrification rurale par énergie solaire - Zone Nord",
                    "description": "Installation de mini-centrales solaires dans 45 villages des régions de Saint-Louis, Louga et Diourbel.",
                    "secteur": "énergies-mines",
                    "poles": "Nord (Saint-Louis), Diourbel-Louga",
                    "cout_estimatif": 12000000000,
                    "structure_soumissionnaire": "Agence Sénégalaise d'Électrification Rurale",
                    "niveau_priorite": "standard",
                    "nouveaute": "amelioration"
                },
                {
                    "titre": "Construction de 10 collèges de proximité en zone rurale",
                    "description": "Construction de 10 collèges dans les zones rurales de Tambacounda et Kédougou.",
                    "secteur": "éducation-formation-recherche",
                    "poles": "Sud-Est (Tambacounda, Kédougou)",
                    "cout_estimatif": 15000000000,
                    "structure_soumissionnaire": "Ministère de l'Éducation Nationale",
                    "niveau_priorite": "haute_priorite",
                    "nouveaute": "complement"
                },
                {
                    "titre": "Modernisation du réseau d'adduction d'eau potable de Thiès",
                    "description": "Réhabilitation et extension du réseau d'eau potable de Thiès.",
                    "secteur": "environnement-eau-assainissement",
                    "poles": "Thiès",
                    "cout_estimatif": 6800000000,
                    "structure_soumissionnaire": "Société Nationale des Eaux du Sénégal",
                    "niveau_priorite": "standard",
                    "nouveaute": "projet_initial"
                },
                {
                    "titre": "Centre hospitalier régional spécialisé de Ziguinchor",
                    "description": "Construction d'un centre hospitalier régional de 200 lits à Ziguinchor.",
                    "secteur": "santé-action sociale",
                    "poles": "Sud (Ziguinchor, Sédhiou, Kolda)",
                    "cout_estimatif": 18500000000,
                    "structure_soumissionnaire": "Ministère de la Santé et de l'Action Sociale",
                    "niveau_priorite": "urgence",
                    "nouveaute": "amelioration"
                },
                {
                    "titre": "Plateforme industrielle de transformation agroalimentaire de Diourbel",
                    "description": "Création d'une zone industrielle dédiée à la transformation des produits agricoles.",
                    "secteur": "industrie-artisanat",
                    "poles": "Diourbel-Louga",
                    "cout_estimatif": 25000000000,
                    "structure_soumissionnaire": "Agence de Promotion des Investissements et des Grands Travaux",
                    "niveau_priorite": "standard",
                    "nouveaute": "complement"
                },
                {
                    "titre": "Bitumage de la route Tambacounda - Kédougou",
                    "description": "Réhabilitation et bitumage de 150km de route nationale.",
                    "secteur": "transports-infrastructures",
                    "poles": "Sud-Est (Tambacounda, Kédougou)",
                    "cout_estimatif": 45000000000,
                    "structure_soumissionnaire": "Agence des Travaux et de Gestion des Routes",
                    "niveau_priorite": "haute_priorite",
                    "nouveaute": "projet_initial"
                },
                {
                    "titre": "Projet d'assainissement urbain de Saint-Louis",
                    "description": "Construction d'un réseau d'assainissement pour 25000 ménages.",
                    "secteur": "environnement-eau-assainissement",
                    "poles": "Nord (Saint-Louis)",
                    "cout_estimatif": 16500000000,
                    "structure_soumissionnaire": "Office National de l'Assainissement du Sénégal",
                    "niveau_priorite": "urgence",
                    "nouveaute": "complement"
                },
                {
                    "titre": "Centre de formation professionnelle aux métiers du numérique",
                    "description": "Construction d'un centre de formation de 400 places aux métiers du numérique.",
                    "secteur": "postes-communication-télécommunications-économie numérique",
                    "poles": "Dakar",
                    "cout_estimatif": 3200000000,
                    "structure_soumissionnaire": "Agence de l'Informatique de l'État",
                    "niveau_priorite": "standard",
                    "nouveaute": "amelioration"
                }
            ]

            projets_crees = 0
            for projet_data in PROJETS_DATA:
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
                    niveau_priorite=projet_data["niveau_priorite"],
                    nouveaute=projet_data["nouveaute"]
                )
                db.session.add(projet)
                projets_crees += 1

            db.session.commit()

            return jsonify({
                "success": True,
                "message": f"{projets_crees} projets créés avec succès",
                "count": projets_crees
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    print("Admin routes registered successfully")
