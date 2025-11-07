"""
Script d'initialisation des données de démonstration
Crée des utilisateurs et projets par défaut pour tester l'application
"""
from datetime import datetime
import os
from db import db
from models import User, Project
from app import app

def init_demo_data():
    """Initialise les données de démonstration"""

    with app.app_context():
        # Vérifier si des utilisateurs existent déjà
        existing_users = User.query.count()
        existing_projects = Project.query.count()

        # Forcer la réinitialisation si FORCE_INIT=true dans les variables d'environnement
        force_init = os.environ.get('FORCE_INIT', 'false').lower() == 'true'

        if existing_users > 0 and not force_init:
            print(f"[DEMO] ✅ Base de données déjà initialisée:")
            print(f"  - {existing_users} utilisateurs existants")
            print(f"  - {existing_projects} projets existants")
            print("[DEMO] Conservation des données existantes")
            return

        if force_init and existing_users > 0:
            print(f"[DEMO] ⚠️ FORCE_INIT activé - Suppression des données existantes...")
            Project.query.delete()
            User.query.delete()
            db.session.commit()
            print("[DEMO] Données supprimées")

        print("[DEMO] Création des utilisateurs de démonstration...")

        # Créer les utilisateurs par défaut
        users_data = [
            {
                'username': 'soumissionnaire',
                'password': 'demo123',
                'role': 'soumissionnaire',
                'display_name': 'Ministère Agriculture',
                'nom_complet': 'Direction Planning Agricole',
                'telephone': '+221 77 123 45 67',
                'type_structure': 'ministere',
                'nom_structure': 'Ministère de l\'Agriculture',
                'statut_compte': 'verifie'
            },
            {
                'username': 'evaluateur1',
                'password': 'demo123',
                'role': 'evaluateur',
                'display_name': 'Agent DPSE 1',
                'nom_complet': 'Mamadou Diop',
                'telephone': '+221 77 234 56 78',
                'statut_compte': 'verifie'
            },
            {
                'username': 'evaluateur2',
                'password': 'demo123',
                'role': 'evaluateur',
                'display_name': 'Agent DPSE 2',
                'nom_complet': 'Fatou Sall',
                'telephone': '+221 77 345 67 89',
                'statut_compte': 'verifie'
            },
            {
                'username': 'secretariatsct',
                'password': 'demo123',
                'role': 'secretariatsct',
                'display_name': 'Chef Division DP',
                'nom_complet': 'Amadou Ba',
                'telephone': '+221 77 456 78 90',
                'statut_compte': 'verifie'
            },
            {
                'username': 'presidencesct',
                'password': 'demo123',
                'role': 'presidencesct',
                'display_name': 'Directeur Planification',
                'nom_complet': 'Ousmane Ndiaye',
                'telephone': '+221 77 567 89 01',
                'statut_compte': 'verifie'
            },
            {
                'username': 'presidencecomite',
                'password': 'demo123',
                'role': 'presidencecomite',
                'display_name': 'DG DGPPE',
                'nom_complet': 'Awa Thiam',
                'telephone': '+221 77 678 90 12',
                'statut_compte': 'verifie'
            },
            {
                'username': 'admin',
                'password': 'demo123',
                'role': 'admin',
                'display_name': 'CT DGPPE',
                'nom_complet': 'Abdou Kane',
                'telephone': '+221 77 789 01 23',
                'statut_compte': 'verifie'
            },
            {
                'username': 'abou.sakho@economie.gouv.sn',
                'password': 'demo123',
                'role': 'soumissionnaire',
                'display_name': 'Abou Sakho',
                'nom_complet': 'Abou Sakho',
                'telephone': '+221 77 000 00 00',
                'type_structure': 'ministere',
                'nom_structure': 'DGPPE',
                'statut_compte': 'verifie'
            }
        ]

        created_users = []
        for user_data in users_data:
            user = User(**user_data)
            db.session.add(user)
            created_users.append(user)

        db.session.commit()
        print(f"[DEMO] ✅ {len(created_users)} utilisateurs créés")

        # Créer quelques projets de démonstration
        print("[DEMO] Création de projets de démonstration...")

        soumissionnaire = User.query.filter_by(username='soumissionnaire').first()

        projects_data = [
            {
                'titre': 'Construction d\'infrastructures scolaires à Dakar',
                'description': 'Projet de construction de 5 écoles élémentaires dans la région de Dakar pour améliorer l\'accès à l\'éducation.',
                'secteur': 'Éducation',
                'poles': 'Dakar',
                'cout_estimatif': 2500000000.0,  # 2.5 milliards FCFA
                'budget': 2500000000.0,
                'statut': 'soumis',
                'auteur_nom': 'Ministère Agriculture',
                'soumissionnaire_id': soumissionnaire.id if soumissionnaire else None,
                'organisme_tutelle': 'Ministère de l\'Éducation Nationale'
            },
            {
                'titre': 'Programme d\'électrification rurale dans le Ferlo',
                'description': 'Extension du réseau électrique dans les zones rurales de la région de Matam.',
                'secteur': 'Énergie',
                'poles': 'Nord-Est (Matam)',
                'cout_estimatif': 1800000000.0,
                'budget': 1800000000.0,
                'statut': 'soumis',
                'auteur_nom': 'Ministère Agriculture',
                'soumissionnaire_id': soumissionnaire.id if soumissionnaire else None,
                'organisme_tutelle': 'Ministère de l\'Énergie'
            },
            {
                'titre': 'Développement de l\'agriculture maraîchère à Thiès',
                'description': 'Programme de soutien aux producteurs maraîchers avec installation de systèmes d\'irrigation moderne.',
                'secteur': 'Agriculture',
                'poles': 'Centre (Kaolack, Fatick, Kaffrine)',
                'cout_estimatif': 950000000.0,
                'budget': 950000000.0,
                'statut': 'soumis',
                'auteur_nom': 'Ministère Agriculture',
                'soumissionnaire_id': soumissionnaire.id if soumissionnaire else None,
                'organisme_tutelle': 'Ministère de l\'Agriculture'
            },
            {
                'titre': 'Centre de santé communautaire à Kolda',
                'description': 'Construction d\'un centre de santé avec maternité et équipements médicaux.',
                'secteur': 'Santé',
                'poles': 'Sud (Ziguinchor, Sédhiou, Kolda)',
                'cout_estimatif': 680000000.0,
                'budget': 680000000.0,
                'statut': 'soumis',
                'auteur_nom': 'Ministère Agriculture',
                'soumissionnaire_id': soumissionnaire.id if soumissionnaire else None,
                'organisme_tutelle': 'Ministère de la Santé'
            },
            {
                'titre': 'Aménagement hydro-agricole à Tambacounda',
                'description': 'Aménagement de 500 hectares de terres pour la culture irriguée.',
                'secteur': 'Agriculture',
                'poles': 'Sud-Est (Tambacounda, Kédougou)',
                'cout_estimatif': 1200000000.0,
                'budget': 1200000000.0,
                'statut': 'soumis',
                'auteur_nom': 'Ministère Agriculture',
                'soumissionnaire_id': soumissionnaire.id if soumissionnaire else None,
                'organisme_tutelle': 'Ministère de l\'Agriculture'
            },
            {
                'titre': 'Réhabilitation des routes départementales à Louga',
                'description': 'Réfection de 80 km de routes départementales pour améliorer la mobilité.',
                'secteur': 'Infrastructure',
                'poles': 'Diourbel-Louga',
                'cout_estimatif': 3200000000.0,
                'budget': 3200000000.0,
                'statut': 'soumis',
                'auteur_nom': 'Ministère Agriculture',
                'soumissionnaire_id': soumissionnaire.id if soumissionnaire else None,
                'organisme_tutelle': 'Ministère des Infrastructures'
            },
            {
                'titre': 'Construction de forages dans la région de Saint-Louis',
                'description': 'Installation de 20 forages pour l\'accès à l\'eau potable en zone rurale.',
                'secteur': 'Hydraulique',
                'poles': 'Nord (Saint-Louis)',
                'cout_estimatif': 850000000.0,
                'budget': 850000000.0,
                'statut': 'en_evaluation',
                'auteur_nom': 'Ministère Agriculture',
                'soumissionnaire_id': soumissionnaire.id if soumissionnaire else None,
                'organisme_tutelle': 'Ministère de l\'Hydraulique'
            },
            {
                'titre': 'Centre de formation professionnelle à Kaolack',
                'description': 'Construction d\'un centre de formation aux métiers du bâtiment.',
                'secteur': 'Formation',
                'poles': 'Centre (Kaolack, Fatick, Kaffrine)',
                'cout_estimatif': 1400000000.0,
                'budget': 1400000000.0,
                'statut': 'en_evaluation',
                'auteur_nom': 'Ministère Agriculture',
                'soumissionnaire_id': soumissionnaire.id if soumissionnaire else None,
                'organisme_tutelle': 'Ministère de la Formation Professionnelle'
            },
            {
                'titre': 'Modernisation du marché central de Ziguinchor',
                'description': 'Rénovation complète et équipement du marché central.',
                'secteur': 'Commerce',
                'poles': 'Sud (Ziguinchor, Sédhiou, Kolda)',
                'cout_estimatif': 560000000.0,
                'budget': 560000000.0,
                'statut': 'valide_sct',
                'auteur_nom': 'Ministère Agriculture',
                'soumissionnaire_id': soumissionnaire.id if soumissionnaire else None,
                'organisme_tutelle': 'Ministère du Commerce'
            },
            {
                'titre': 'Parc solaire photovoltaïque à Kédougou',
                'description': 'Installation d\'un parc solaire de 10 MW pour l\'électrification.',
                'secteur': 'Énergie',
                'poles': 'Sud-Est (Tambacounda, Kédougou)',
                'cout_estimatif': 5600000000.0,
                'budget': 5600000000.0,
                'statut': 'valide_sct',
                'auteur_nom': 'Ministère Agriculture',
                'soumissionnaire_id': soumissionnaire.id if soumissionnaire else None,
                'organisme_tutelle': 'Ministère de l\'Énergie'
            },
            {
                'titre': 'Construction de lycée technique à Diourbel',
                'description': 'Nouveau lycée technique avec 18 salles de classe et équipements.',
                'secteur': 'Éducation',
                'poles': 'Diourbel-Louga',
                'cout_estimatif': 1900000000.0,
                'budget': 1900000000.0,
                'statut': 'valide_comite',
                'auteur_nom': 'Ministère Agriculture',
                'soumissionnaire_id': soumissionnaire.id if soumissionnaire else None,
                'organisme_tutelle': 'Ministère de l\'Éducation Nationale'
            },
            {
                'titre': 'Aménagement de périmètres maraîchers à Fatick',
                'description': 'Développement de 200 hectares pour la production maraîchère.',
                'secteur': 'Agriculture',
                'poles': 'Centre (Kaolack, Fatick, Kaffrine)',
                'cout_estimatif': 720000000.0,
                'budget': 720000000.0,
                'statut': 'valide_comite',
                'auteur_nom': 'Ministère Agriculture',
                'soumissionnaire_id': soumissionnaire.id if soumissionnaire else None,
                'organisme_tutelle': 'Ministère de l\'Agriculture'
            }
        ]

        for project_data in projects_data:
            project = Project(**project_data)
            db.session.add(project)

        db.session.commit()
        print(f"[DEMO] ✅ {len(projects_data)} projets créés")
        print("[DEMO] 🎉 Initialisation des données de démonstration terminée!")
        print("\n[DEMO] Comptes disponibles:")
        print("  - soumissionnaire / demo123")
        print("  - evaluateur1 / demo123")
        print("  - secretariatsct / demo123")
        print("  - presidencesct / demo123")
        print("  - presidencecomite / demo123")
        print("  - admin / demo123")

if __name__ == '__main__':
    init_demo_data()
