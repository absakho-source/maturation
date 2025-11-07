#!/usr/bin/env python3
"""
Script pour remettre la base comme elle était ce matin
avec les vrais comptes utilisateurs originaux
"""

import sys
import os
from datetime import datetime, timedelta
import random

sys.path.append('backend')

from backend.app import app, User, Project, db

def restore_original_users():
    """Restaurer les vrais utilisateurs comme ce matin"""
    
    # Supprimer tous les utilisateurs actuels
    User.query.delete()
    
    # Vrais utilisateurs utilisés ce matin
    original_users = [
        {
            'username': 'admin',
            'password': 'admin123',
            'role': 'admin',
            'display_name': 'Administrateur'
        },
        {
            'username': 'secretariat',
            'password': 'secret123',
            'role': 'secretariatsct',
            'display_name': 'Secrétariat SCT'
        },
        {
            'username': 'presidence',
            'password': 'presid123',
            'role': 'presidencesct',
            'display_name': 'Présidence SCT'
        },
        {
            'username': 'comite',
            'password': 'comite123',
            'role': 'presidencecomite',
            'display_name': 'Présidence Comité'
        },
        {
            'username': 'evaluateur',
            'password': 'eval123',
            'role': 'evaluateur',
            'display_name': 'Évaluateur'
        },
        {
            'username': 'soumissionnaire',
            'password': 'soum123',
            'role': 'soumissionnaire',
            'display_name': 'Soumissionnaire'
        }
    ]
    
    for user_data in original_users:
        new_user = User(
            username=user_data['username'],
            password=user_data['password'],
            role=user_data['role'],
            display_name=user_data['display_name']
        )
        db.session.add(new_user)
    
    db.session.commit()
    print(f"✅ {len(original_users)} utilisateurs originaux restaurés")

def restore_original_projects():
    """Restaurer quelques projets comme ce matin"""
    
    # Supprimer tous les projets actuels
    Project.query.delete()
    
    # Projets originaux simples
    original_projects = [
        {
            'titre': 'Projet de Modernisation Agricole',
            'description': 'Amélioration des techniques agricoles dans les régions rurales',
            'cout_estimatif': 5000000000,  # 5 milliards FCFA
            'secteur': 'Agriculture',
            'poles': 'Centre',
            'statut': 'soumis',
            'auteur_nom': 'Société AgriTech',
            'evaluateur_nom': None,
            'avis': None
        },
        {
            'titre': 'Infrastructure Routière Rurale',
            'description': 'Construction et réhabilitation de routes rurales',
            'cout_estimatif': 8000000000,  # 8 milliards FCFA
            'secteur': 'Infrastructure',
            'poles': 'Sud',
            'statut': 'assigné',
            'auteur_nom': 'Entreprise BTP Sénégal',
            'evaluateur_nom': 'Évaluateur',
            'avis': None
        },
        {
            'titre': 'Électrification Solaire',
            'description': 'Installation de panneaux solaires dans les villages',
            'cout_estimatif': 3000000000,  # 3 milliards FCFA
            'secteur': 'Énergie',
            'poles': 'Nord',
            'statut': 'en évaluation',
            'auteur_nom': 'SolarTech Sénégal',
            'evaluateur_nom': 'Évaluateur',
            'avis': None
        },
        {
            'titre': 'Centre de Santé Communautaire',
            'description': 'Construction de centres de santé dans les zones reculées',
            'cout_estimatif': 2000000000,  # 2 milliards FCFA
            'secteur': 'Santé',
            'poles': 'Est',
            'statut': 'approuvé',
            'auteur_nom': 'MedConstruct',
            'evaluateur_nom': 'Évaluateur',
            'avis': 'favorable'
        }
    ]
    
    for i, project_data in enumerate(original_projects, 1):
        # Générer un numéro de projet simple
        numero_projet = f"2025{i:02d}"
        
        # Date de soumission récente
        date_soumission = datetime.now() - timedelta(days=random.randint(1, 30))
        
        new_project = Project(
            numero_projet=numero_projet,
            titre=project_data['titre'],
            description=project_data['description'],
            cout_estimatif=project_data['cout_estimatif'],
            secteur=project_data['secteur'],
            poles=project_data['poles'],
            statut=project_data['statut'],
            auteur_nom=project_data['auteur_nom'],
            evaluateur_nom=project_data['evaluateur_nom'],
            avis=project_data['avis'],
            date_soumission=date_soumission
        )
        
        db.session.add(new_project)
    
    db.session.commit()
    print(f"✅ {len(original_projects)} projets originaux restaurés")

def restore_morning_database():
    """Restaurer la base comme ce matin"""
    
    with app.app_context():
        print("🔄 Restauration de la base comme ce matin...")
        print()
        
        # Restaurer les utilisateurs originaux
        print("👥 Restauration des utilisateurs originaux...")
        restore_original_users()
        
        # Restaurer les projets originaux
        print("📋 Restauration des projets originaux...")
        restore_original_projects()
        
        print()
        print("✅ RESTAURATION TERMINÉE!")
        print()
        
        # Vérification finale
        total_users = User.query.count()
        total_projects = Project.query.count()
        
        print(f"📊 BASE RESTAURÉE:")
        print(f"   👥 Utilisateurs: {total_users}")
        print(f"   📋 Projets: {total_projects}")
        print()
        
        print("=== COMPTES UTILISATEURS ORIGINAUX ===")
        users = User.query.all()
        for user in users:
            print(f"👤 {user.username} / {user.password} - {user.display_name} ({user.role})")
        
        print()
        print("=== PROJETS ORIGINAUX ===")
        projects = Project.query.all()
        for project in projects:
            print(f"📋 [{project.numero_projet}] {project.titre} - {project.statut}")
            print(f"    Secteur: {project.secteur} | Pôle: {project.poles}")
            print(f"    Coût: {project.cout_estimatif/1000000000:.1f} Md FCFA")
            print()

if __name__ == "__main__":
    restore_morning_database()