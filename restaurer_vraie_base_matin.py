#!/usr/bin/env python3
"""
Script pour restaurer la vraie base comme elle était ce matin
avec 2 évaluateurs et 8-9 projets réalistes
"""

import sys
import os
from datetime import datetime, timedelta
import random

sys.path.append('backend')

from backend.app import app, User, Project, db

def restore_real_morning_users():
    """Restaurer les vrais utilisateurs comme ce matin avec 2 évaluateurs"""
    
    # Supprimer tous les utilisateurs actuels
    User.query.delete()
    
    # Vrais utilisateurs utilisés ce matin
    real_users = [
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
            'username': 'evaluateur1',
            'password': 'eval123',
            'role': 'evaluateur',
            'display_name': 'Dr. Aminata DIALLO'
        },
        {
            'username': 'evaluateur2',
            'password': 'eval123',
            'role': 'evaluateur',
            'display_name': 'Prof. Moussa FALL'
        },
        {
            'username': 'soumissionnaire',
            'password': 'soum123',
            'role': 'soumissionnaire',
            'display_name': 'Soumissionnaire Principal'
        }
    ]
    
    for user_data in real_users:
        new_user = User(
            username=user_data['username'],
            password=user_data['password'],
            role=user_data['role'],
            display_name=user_data['display_name']
        )
        db.session.add(new_user)
    
    db.session.commit()
    print(f"✅ {len(real_users)} utilisateurs restaurés (avec 2 évaluateurs)")

def restore_real_morning_projects():
    """Restaurer 8-9 projets comme ce matin"""
    
    # Supprimer tous les projets actuels
    Project.query.delete()
    
    # Projets réalistes comme ce matin
    real_projects = [
        {
            'titre': 'Programme National de Digitalisation Rurale',
            'description': 'Extension de la couverture numérique dans les zones rurales du Sénégal',
            'cout_estimatif': 12000000000,  # 12 milliards FCFA
            'secteur': 'Technologies de l\'Information',
            'poles': 'Centre (Kaolack, Fatick, Kaffrine)',
            'statut': 'soumis',
            'auteur_nom': 'TechConnect Sénégal',
            'evaluateur_nom': None,
            'avis': None
        },
        {
            'titre': 'Modernisation des Infrastructures Hospitalières',
            'description': 'Rénovation et équipement des hôpitaux régionaux',
            'cout_estimatif': 25000000000,  # 25 milliards FCFA
            'secteur': 'Santé et Action Sociale',
            'poles': 'Sud (Ziguinchor, Sédhiou, Kolda)',
            'statut': 'assigné',
            'auteur_nom': 'MedConstruct International',
            'evaluateur_nom': 'Dr. Aminata DIALLO',
            'avis': None
        },
        {
            'titre': 'Développement de l\'Agriculture Biologique',
            'description': 'Promotion des techniques agricoles durables et biologiques',
            'cout_estimatif': 8500000000,  # 8.5 milliards FCFA
            'secteur': 'Agriculture et Développement Rural',
            'poles': 'Diourbel-Louga (Diourbel, Louga)',
            'statut': 'en évaluation',
            'auteur_nom': 'AgriVert Sénégal',
            'evaluateur_nom': 'Prof. Moussa FALL',
            'avis': None
        },
        {
            'titre': 'Construction d\'Écoles Primaires Modernes',
            'description': 'Édification de nouvelles écoles avec équipements modernes',
            'cout_estimatif': 15000000000,  # 15 milliards FCFA
            'secteur': 'Éducation et Formation',
            'poles': 'Nord-Est (Matam)',
            'statut': 'approuvé',
            'auteur_nom': 'EduBuild SARL',
            'evaluateur_nom': 'Dr. Aminata DIALLO',
            'avis': 'favorable'
        },
        {
            'titre': 'Électrification par Énergie Solaire',
            'description': 'Installation de systèmes solaires dans 150 villages',
            'cout_estimatif': 18000000000,  # 18 milliards FCFA
            'secteur': 'Énergie et Mines',
            'poles': 'Sud-Est (Tambacounda, Kédougou)',
            'statut': 'validé par presidencesct',
            'auteur_nom': 'SolarTech Africa',
            'evaluateur_nom': 'Prof. Moussa FALL',
            'avis': 'favorable'
        },
        {
            'titre': 'Amélioration du Réseau Routier Inter-régional',
            'description': 'Réhabilitation et construction de routes stratégiques',
            'cout_estimatif': 35000000000,  # 35 milliards FCFA
            'secteur': 'Infrastructure et Transport',
            'poles': 'Dakar (Dakar)',
            'statut': 'compléments demandés',
            'auteur_nom': 'RouteMax Construction',
            'evaluateur_nom': 'Dr. Aminata DIALLO',
            'avis': None
        },
        {
            'titre': 'Gestion Intégrée des Déchets Urbains',
            'description': 'Système moderne de collecte et traitement des déchets',
            'cout_estimatif': 6500000000,  # 6.5 milliards FCFA
            'secteur': 'Environnement et Développement Durable',
            'poles': 'Thiès (Thiès)',
            'statut': 'rejeté',
            'auteur_nom': 'EcoClean Solutions',
            'evaluateur_nom': 'Prof. Moussa FALL',
            'avis': 'défavorable'
        },
        {
            'titre': 'Développement du Tourisme Culturel',
            'description': 'Valorisation des sites touristiques et patrimoine culturel',
            'cout_estimatif': 4200000000,  # 4.2 milliards FCFA
            'secteur': 'Culture et Tourisme',
            'poles': 'Nord (Saint-Louis)',
            'statut': 'compléments fournis',
            'auteur_nom': 'CultureTour Sénégal',
            'evaluateur_nom': 'Dr. Aminata DIALLO',
            'avis': None
        },
        {
            'titre': 'Modernisation des Ports de Pêche',
            'description': 'Rénovation et équipement des infrastructures portuaires',
            'cout_estimatif': 22000000000,  # 22 milliards FCFA
            'secteur': 'Pêche et Économie Maritime',
            'poles': 'Centre (Kaolack, Fatick, Kaffrine)',
            'statut': 'assigné',
            'auteur_nom': 'Ports & Marine SARL',
            'evaluateur_nom': 'Prof. Moussa FALL',
            'avis': None
        }
    ]
    
    for i, project_data in enumerate(real_projects, 1):
        # Générer un numéro de projet réaliste
        numero_projet = f"DGPPE-2025-{i:03d}"
        
        # Date de soumission récente (dernières semaines)
        date_soumission = datetime.now() - timedelta(days=random.randint(5, 45))
        
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
    print(f"✅ {len(real_projects)} projets restaurés")

def restore_complete_morning_database():
    """Restaurer la base complète comme ce matin"""
    
    with app.app_context():
        print("🔄 Restauration complète des données comme ce matin...")
        print()
        
        # Restaurer les utilisateurs avec 2 évaluateurs
        print("👥 Restauration des utilisateurs (avec 2 évaluateurs)...")
        restore_real_morning_users()
        
        # Restaurer 9 projets réalistes
        print("📋 Restauration de 9 projets réalistes...")
        restore_real_morning_projects()
        
        print()
        print("✅ RESTAURATION COMPLÈTE TERMINÉE!")
        print()
        
        # Vérification finale
        total_users = User.query.count()
        total_projects = Project.query.count()
        
        print(f"📊 BASE RESTAURÉE COMME CE MATIN:")
        print(f"   👥 Utilisateurs: {total_users}")
        print(f"   📋 Projets: {total_projects}")
        print()
        
        print("=== COMPTES UTILISATEURS ===")
        users = User.query.all()
        for user in users:
            print(f"👤 {user.username} / {user.password} - {user.display_name} ({user.role})")
        
        print()
        print("=== LES 2 ÉVALUATEURS ===")
        evaluateurs = User.query.filter_by(role='evaluateur').all()
        for evaluateur in evaluateurs:
            print(f"🎓 {evaluateur.username} - {evaluateur.display_name}")
        
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
        print("=== PROJETS ASSIGNÉS AUX ÉVALUATEURS ===")
        for project in projects:
            if project.evaluateur_nom:
                print(f"📋 {project.titre[:50]}... → {project.evaluateur_nom} ({project.statut})")

if __name__ == "__main__":
    restore_complete_morning_database()