"""
Créer le projet "test marone" avec les utilisateurs correspondants
"""

import sys
sys.path.append('backend')

def creer_projet_test_marone():
    """Créer le projet test marone et configurer les utilisateurs"""
    
    import app
    
    with app.app.app_context():
        from app import Project, User, db
        
        print("🎯 CRÉATION DU PROJET TEST MARONE")
        print("=" * 50)
        
        # Vérifier si le projet existe déjà
        projet_existant = Project.query.filter_by(titre="projet test marone").first()
        if projet_existant:
            print(f"✅ Le projet 'projet test marone' existe déjà (ID: {projet_existant.id})")
            return projet_existant.id
        
        # Créer le projet test marone
        projet_marone = Project(
            numero_projet='DGPPE-TEST-MARONE-001',
            titre='projet test marone',
            auteur_nom='Équipe Test DGPPE',
            secteur='Test/Validation',
            cout_estimatif=1000000000,  # 1 milliard FCFA pour test
            poles='Dakar',
            statut='soumis',
            description='Projet de test pour validation des fonctionnalités de la plateforme DGPPE - Tester le workflow complet : soumission, assignation, évaluation - Validation des processus avant mise en production'
        )
        
        db.session.add(projet_marone)
        
        try:
            db.session.commit()
            print(f"📋 Projet créé: {projet_marone.titre}")
            print(f"   📍 ID: {projet_marone.id}")
            print(f"   📊 Statut: {projet_marone.statut}")
            print(f"   💰 Coût: {projet_marone.cout_estimatif:,} FCFA")
            
            # Lister les utilisateurs disponibles pour assignation
            print(f"\n👥 UTILISATEURS DISPONIBLES POUR ASSIGNATION:")
            users = User.query.all()
            for user in users:
                print(f"   • {user.username} ({user.role}) - {user.display_name or 'Pas de nom'}")
            
            return projet_marone.id
            
        except Exception as e:
            print(f"❌ Erreur lors de la création: {e}")
            db.session.rollback()
            return None

def assigner_evaluateurs_projet_marone(project_id):
    """Assigner les évaluateurs au projet test marone"""
    
    import app
    
    with app.app.app_context():
        from app import Project, User, db
        
        print(f"\n🎯 ASSIGNATION ÉVALUATEURS AU PROJET ID {project_id}")
        print("=" * 50)
        
        projet = Project.query.get(project_id)
        if not projet:
            print(f"❌ Projet ID {project_id} non trouvé")
            return False
        
        # Assigner evaluateur1 comme évaluateur principal
        evaluateur1 = User.query.filter_by(username='evaluateur1').first()
        if evaluateur1:
            projet.evaluateur_nom = evaluateur1.display_name or 'evaluateur1'
            projet.statut = 'assigné'
            print(f"✅ Évaluateur assigné: {projet.evaluateur_nom}")
        else:
            print("❌ Utilisateur 'evaluateur1' non trouvé")
            return False
        
        try:
            db.session.commit()
            print(f"📋 Projet '{projet.titre}' assigné à {projet.evaluateur_nom}")
            print(f"📊 Statut mis à jour: {projet.statut}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'assignation: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    # Créer le projet
    project_id = creer_projet_test_marone()
    
    if project_id:
        # Assigner les évaluateurs
        success = assigner_evaluateurs_projet_marone(project_id)
        
        if success:
            print("\n" + "=" * 50)
            print("🎉 PROJET TEST MARONE CRÉÉ ET CONFIGURÉ!")
            print("✅ Projet créé avec assignation d'évaluateurs")
            print("📱 Accessible via l'interface: http://127.0.0.1:5173")
        else:
            print("\n💥 ERREUR LORS DE LA CONFIGURATION")
    else:
        print("\n💥 ERREUR LORS DE LA CRÉATION DU PROJET")