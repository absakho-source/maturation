#!/usr/bin/env python3
"""
Script pour restaurer toutes les données de test : utilisateurs ET projets
"""

import sys
import os
from datetime import datetime, timedelta
import random

sys.path.append('backend')

from backend.app import app, User, Project, db

def create_users():
    """Créer les utilisateurs de test"""
    
    users_data = [
        {
            'username': 'admin',
            'password': 'admin123',
            'role': 'admin',
            'display_name': 'Administrateur Système'
        },
        {
            'username': 'secretariatsct',
            'password': 'secret123',
            'role': 'secretariatsct',
            'display_name': 'Secrétariat SCT'
        },
        {
            'username': 'presidencesct',
            'password': 'presid123',
            'role': 'presidencesct',
            'display_name': 'Présidence SCT'
        },
        {
            'username': 'presidencecomite',
            'password': 'comite123',
            'role': 'presidencecomite',
            'display_name': 'Présidence Comité'
        },
        {
            'username': 'evaluateur1',
            'password': 'eval123',
            'role': 'evaluateur',
            'display_name': 'Dr. Aminata DIOP'
        },
        {
            'username': 'evaluateur2',
            'password': 'eval123',
            'role': 'evaluateur',
            'display_name': 'Prof. Moussa NDIAYE'
        },
        {
            'username': 'evaluateur3',
            'password': 'eval123',
            'role': 'evaluateur',
            'display_name': 'Dr. Fatou SALL'
        },
        {
            'username': 'soumissionnaire1',
            'password': 'soum123',
            'role': 'soumissionnaire',
            'display_name': 'Société SENEGAL TECH'
        },
        {
            'username': 'soumissionnaire2',
            'password': 'soum123',
            'role': 'soumissionnaire',
            'display_name': 'Entreprise DAKAR SOLUTIONS'
        },
        {
            'username': 'soumissionnaire3',
            'password': 'soum123',
            'role': 'soumissionnaire',
            'display_name': 'SARL INNOVATIONS SENEGAL'
        }
    ]
    
    # Supprimer et recréer les utilisateurs
    User.query.delete()
    
    for user_data in users_data:
        new_user = User(
            username=user_data['username'],
            password=user_data['password'],
            role=user_data['role'],
            display_name=user_data['display_name']
        )
        db.session.add(new_user)
    
    db.session.commit()
    print(f"✅ {len(users_data)} utilisateurs créés")

def create_projects():
    """Créer les projets de test"""
    
    # Données des pôles territoriaux
    poles_territoriaux = [
        "Centre (Kaolack, Fatick, Kaffrine)",
        "Dakar (Dakar)",
        "Diourbel-Louga (Diourbel, Louga)",
        "Nord (Saint-Louis)",
        "Nord-Est (Matam)",
        "Sud (Ziguinchor, Sédhiou, Kolda)",
        "Sud-Est (Tambacounda, Kédougou)",
        "Thiès (Thiès)"
    ]
    
    secteurs = [
        "Agriculture et Développement Rural",
        "Santé et Action Sociale", 
        "Éducation et Formation",
        "Infrastructure et Transport",
        "Énergie et Mines",
        "Environnement et Développement Durable",
        "Industrie et Commerce",
        "Gouvernance et Administration Publique",
        "Eau et Assainissement",
        "Technologie et Innovation"
    ]
    
    statuts_possibles = [
        "soumis",
        "assigné", 
        "en évaluation",
        "approuvé",
        "rejeté",
        "compléments demandés",
        "compléments fournis",
        "validé par presidencesct",
        "décision finale prise"
    ]
    
    # Supprimer les projets existants
    Project.query.delete()
    
    projects_data = [
        {
            'titre': 'Modernisation du Système Éducatif Rural',
            'description': 'Projet visant à améliorer l\'accès à l\'éducation de qualité dans les zones rurales du Sénégal par la construction d\'écoles et la formation des enseignants.',
            'cout_estimatif': 15000000000,  # 15 milliards FCFA
            'secteur': 'Éducation et Formation',
            'pole_territorial': 'Sud (Ziguinchor, Sédhiou, Kolda)',
            'statut': 'validé par presidencesct',
            'auteur_nom': 'Société SENEGAL TECH',
            'evaluateur_nom': 'Dr. Aminata DIOP',
            'avis': 'favorable',
            'note_globale': 16.5
        },
        {
            'titre': 'Programme d\'Électrification Solaire',
            'description': 'Installation de systèmes d\'énergie solaire dans 200 villages pour améliorer l\'accès à l\'électricité.',
            'cout_estimatif': 25000000000,  # 25 milliards FCFA
            'secteur': 'Énergie et Mines',
            'pole_territorial': 'Centre (Kaolack, Fatick, Kaffrine)',
            'statut': 'approuvé',
            'auteur_nom': 'Entreprise DAKAR SOLUTIONS',
            'evaluateur_nom': 'Prof. Moussa NDIAYE',
            'avis': 'favorable',
            'note_globale': 17.2
        },
        {
            'titre': 'Renforcement du Système de Santé',
            'description': 'Construction de centres de santé et formation du personnel médical dans les régions défavorisées.',
            'cout_estimatif': 30000000000,  # 30 milliards FCFA
            'secteur': 'Santé et Action Sociale',
            'pole_territorial': 'Nord-Est (Matam)',
            'statut': 'en évaluation',
            'auteur_nom': 'SARL INNOVATIONS SENEGAL',
            'evaluateur_nom': 'Dr. Fatou SALL',
            'avis': None,
            'note_globale': None
        },
        {
            'titre': 'Développement de l\'Agriculture Intelligente',
            'description': 'Introduction de technologies modernes et durables pour améliorer la productivité agricole.',
            'cout_estimatif': 18000000000,  # 18 milliards FCFA
            'secteur': 'Agriculture et Développement Rural',
            'pole_territorial': 'Diourbel-Louga (Diourbel, Louga)',
            'statut': 'assigné',
            'auteur_nom': 'Société SENEGAL TECH',
            'evaluateur_nom': 'Dr. Aminata DIOP',
            'avis': None,
            'note_globale': None
        },
        {
            'titre': 'Infrastructure Routière et Transport',
            'description': 'Modernisation du réseau routier et amélioration des transports publics urbains.',
            'cout_estimatif': 45000000000,  # 45 milliards FCFA
            'secteur': 'Infrastructure et Transport',
            'pole_territorial': 'Dakar (Dakar)',
            'statut': 'compléments demandés',
            'auteur_nom': 'Entreprise DAKAR SOLUTIONS',
            'evaluateur_nom': 'Prof. Moussa NDIAYE',
            'avis': None,
            'note_globale': None
        },
        {
            'titre': 'Gestion Durable des Ressources en Eau',
            'description': 'Projet d\'amélioration de l\'accès à l\'eau potable et de gestion durable des ressources hydriques.',
            'cout_estimatif': 22000000000,  # 22 milliards FCFA
            'secteur': 'Eau et Assainissement',
            'pole_territorial': 'Sud-Est (Tambacounda, Kédougou)',
            'statut': 'soumis',
            'auteur_nom': 'SARL INNOVATIONS SENEGAL',
            'evaluateur_nom': None,
            'avis': None,
            'note_globale': None
        },
        {
            'titre': 'Digitalisation de l\'Administration Publique',
            'description': 'Modernisation des services publics par l\'introduction de solutions numériques.',
            'cout_estimatif': 12000000000,  # 12 milliards FCFA
            'secteur': 'Gouvernance et Administration Publique',
            'pole_territorial': 'Thiès (Thiès)',
            'statut': 'rejeté',
            'auteur_nom': 'Société SENEGAL TECH',
            'evaluateur_nom': 'Dr. Fatou SALL',
            'avis': 'défavorable',
            'note_globale': 8.5
        },
        {
            'titre': 'Protection de l\'Environnement Côtier',
            'description': 'Programme de protection et restauration des écosystèmes côtiers contre l\'érosion.',
            'cout_estimatif': 35000000000,  # 35 milliards FCFA
            'secteur': 'Environnement et Développement Durable',
            'pole_territorial': 'Nord (Saint-Louis)',
            'statut': 'validé par presidencesct',
            'auteur_nom': 'Entreprise DAKAR SOLUTIONS',
            'evaluateur_nom': 'Dr. Aminata DIOP',
            'avis': 'favorable',
            'note_globale': 18.0
        },
        {
            'titre': 'Hub Technologique et Innovation',
            'description': 'Création d\'un centre d\'innovation technologique pour startups et entreprises tech.',
            'cout_estimatif': 8000000000,  # 8 milliards FCFA
            'secteur': 'Technologie et Innovation',
            'pole_territorial': 'Dakar (Dakar)',
            'statut': 'approuvé',
            'auteur_nom': 'SARL INNOVATIONS SENEGAL',
            'evaluateur_nom': 'Prof. Moussa NDIAYE',
            'avis': 'favorable',
            'note_globale': 16.8
        },
        {
            'titre': 'Développement Industriel Local',
            'description': 'Soutien au développement d\'industries locales et création d\'emplois.',
            'cout_estimatif': 28000000000,  # 28 milliards FCFA
            'secteur': 'Industrie et Commerce',
            'pole_territorial': 'Centre (Kaolack, Fatick, Kaffrine)',
            'statut': 'compléments fournis',
            'auteur_nom': 'Société SENEGAL TECH',
            'evaluateur_nom': 'Dr. Fatou SALL',
            'avis': None,
            'note_globale': None
        }
    ]
    
    # Créer les projets
    for i, project_data in enumerate(projects_data, 1):
        # Générer un numéro de projet
        year = datetime.now().year
        numero_projet = f"DGPPE-{year}-{i:03d}"
        
        # Dates
        date_soumission = datetime.now() - timedelta(days=random.randint(30, 180))
        
        new_project = Project(
            numero_projet=numero_projet,
            titre=project_data['titre'],
            description=project_data['description'],
            cout_estimatif=project_data['cout_estimatif'],
            secteur=project_data['secteur'],
            poles=project_data['pole_territorial'],  # Le modèle utilise 'poles'
            statut=project_data['statut'],
            auteur_nom=project_data['auteur_nom'],
            evaluateur_nom=project_data['evaluateur_nom'],
            avis=project_data['avis'],
            date_soumission=date_soumission
        )
        
        db.session.add(new_project)
    
    db.session.commit()
    print(f"✅ {len(projects_data)} projets créés")

def restore_all_data():
    """Restaurer toutes les données"""
    
    with app.app_context():
        print("🚀 Restauration complète des données...")
        print()
        
        # Créer les utilisateurs
        print("👥 Création des utilisateurs...")
        create_users()
        
        # Créer les projets  
        print("📋 Création des projets...")
        create_projects()
        
        print()
        print("✅ RESTAURATION TERMINÉE!")
        print()
        
        # Vérification finale
        total_users = User.query.count()
        total_projects = Project.query.count()
        
        print(f"📊 RÉSUMÉ:")
        print(f"   👥 Utilisateurs: {total_users}")
        print(f"   📋 Projets: {total_projects}")
        print()
        
        print("=== UTILISATEURS ===")
        users = User.query.all()
        for user in users:
            print(f"👤 {user.username} - {user.display_name} ({user.role})")
        
        print()
        print("=== PROJETS PAR STATUT ===")
        projects = Project.query.all()
        statuts = {}
        for project in projects:
            statut = project.statut
            statuts[statut] = statuts.get(statut, 0) + 1
        
        for statut, count in sorted(statuts.items()):
            print(f"📊 {statut}: {count} projet(s)")
        
        print()
        print("=== PROJETS PAR PÔLE ===")
        poles = {}
        for project in projects:
            pole = project.poles  # Le modèle utilise 'poles'
            poles[pole] = poles.get(pole, 0) + 1
        
        for pole, count in sorted(poles.items()):
            print(f"🏛️ {pole}: {count} projet(s)")

if __name__ == "__main__":
    restore_all_data()