#!/usr/bin/env python3
"""
Script pour créer des utilisateurs de test dans la base de données
"""

import sys
import os
sys.path.append('backend')

from backend.app import app, User, db

def create_test_users():
    """Créer des utilisateurs de test pour la plateforme"""
    
    with app.app_context():
        print("🚀 Création des utilisateurs de test...")
        
        # Définir les utilisateurs de test
        test_users = [
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
            }
        ]
        
        # Supprimer les utilisateurs existants (si any)
        User.query.delete()
        
        # Créer les nouveaux utilisateurs
        for user_data in test_users:
            # Vérifier si l'utilisateur existe déjà
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if existing_user:
                print(f"⚠️  L'utilisateur {user_data['username']} existe déjà")
                continue
                
            # Créer le nouvel utilisateur
            new_user = User(
                username=user_data['username'],
                password=user_data['password'],  # En production, utiliser un hash
                role=user_data['role'],
                display_name=user_data['display_name']
            )
            
            db.session.add(new_user)
            print(f"✅ Utilisateur créé: {user_data['username']} ({user_data['role']}) - {user_data['display_name']}")
        
        # Sauvegarder en base
        db.session.commit()
        print("✅ Tous les utilisateurs ont été créés avec succès!")
        
        # Vérification finale
        total_users = User.query.count()
        print(f"📊 Total des utilisateurs en base: {total_users}")
        
        print("\n=== UTILISATEURS CRÉÉS ===")
        users = User.query.all()
        for user in users:
            print(f"👤 {user.username} - {user.display_name} ({user.role})")

if __name__ == "__main__":
    create_test_users()