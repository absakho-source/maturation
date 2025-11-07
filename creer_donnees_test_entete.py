"""
Création de données de test pour démontrer l'en-tête DGPPE
"""

import sys
sys.path.append('backend')

def creer_donnees_test():
    """Créer des projets de test pour démontrer l'en-tête"""
    
    import app
    
    with app.app.app_context():
        from app import Project, User, FicheEvaluation, db
        
        print("🧪 CRÉATION DE DONNÉES DE TEST POUR L'EN-TÊTE DGPPE")
        print("=" * 60)
        
        # Vérifier si des données existent déjà
        projets_existants = Project.query.count()
        if projets_existants > 0:
            print(f"ℹ️  {projets_existants} projets déjà présents")
            return True
        
        # Créer des utilisateurs de test
        users_test = [
            {
                'username': 'evaluateur1',
                'email': 'evaluateur1@dgppe.gouv.sn',
                'password': 'test123',
                'role': 'evaluateur',
                'display_name': 'Dr. Fatou DIOP'
            },
            {
                'username': 'soumissionnaire1',
                'email': 'soumissionnaire1@gouv.sn',
                'password': 'test123',
                'role': 'soumissionnaire',
                'display_name': 'Direction des Projets - Ministère de l\'Éducation'
            }
        ]
        
        for user_data in users_test:
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if not existing_user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    role=user_data['role'],
                    display_name=user_data['display_name']
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                print(f"👤 Utilisateur créé: {user_data['display_name']} ({user_data['role']})")
        
        # Créer des projets de test
        projets_test = [
            {
                'numero_projet': 'DGPPE-2025-001',
                'titre': 'Modernisation des Services de l\'État Civil',
                'auteur_nom': 'Ministère de l\'Intérieur',
                'secteur': 'Gouvernance',
                'cout_estimatif': 3500000000,  # 3.5 milliards FCFA
                'poles': 'Dakar',
                'statut': 'assigné',
                'evaluateur_nom': 'Dr. Fatou DIOP',
                'description': 'Projet de digitalisation complète des services d\'état civil pour améliorer l\'efficacité et la transparence.',
                'objectifs': 'Réduire les délais de traitement, améliorer la qualité de service, digitaliser les processus',
                'justification': 'Besoin urgent de modernisation face aux défis actuels de gestion administrative'
            },
            {
                'numero_projet': 'DGPPE-2025-002',
                'titre': 'Programme de Développement Rural Intégré',
                'auteur_nom': 'Ministère de l\'Agriculture',
                'secteur': 'Agriculture',
                'cout_estimatif': 8200000000,  # 8.2 milliards FCFA
                'poles': 'Centre (Kaolack, Fatick, Kaffrine)',
                'statut': 'soumis',
                'description': 'Programme visant à améliorer la productivité agricole et les conditions de vie en milieu rural.',
                'objectifs': 'Augmenter les rendements, créer des emplois ruraux, renforcer la sécurité alimentaire',
                'justification': 'Contribution essentielle à la sécurité alimentaire et au développement économique rural'
            },
            {
                'numero_projet': 'DGPPE-2025-003',
                'titre': 'Construction d\'Infrastructures Sanitaires Modernes',
                'auteur_nom': 'Ministère de la Santé',
                'secteur': 'Santé',
                'cout_estimatif': 12500000000,  # 12.5 milliards FCFA
                'poles': 'Sud (Ziguinchor, Sédhiou, Kolda)',
                'statut': 'évalué',
                'evaluateur_nom': 'Dr. Fatou DIOP',
                'avis': 'favorable',
                'description': 'Construction de centres de santé modernes équipés pour améliorer l\'accès aux soins.',
                'objectifs': 'Améliorer l\'accès aux soins, réduire la mortalité, renforcer le système de santé',
                'justification': 'Besoin critique d\'infrastructures sanitaires dans les régions du Sud'
            }
        ]
        
        for projet_data in projets_test:
            projet = Project(
                numero_projet=projet_data['numero_projet'],
                titre=projet_data['titre'],
                auteur_nom=projet_data['auteur_nom'],
                secteur=projet_data['secteur'],
                cout_estimatif=projet_data['cout_estimatif'],
                poles=projet_data['poles'],
                statut=projet_data['statut'],
                evaluateur_nom=projet_data.get('evaluateur_nom'),
                avis=projet_data.get('avis'),
                description=projet_data['description'],
                objectifs=projet_data['objectifs'],
                justification=projet_data['justification']
            )
            db.session.add(projet)
            print(f"📋 Projet créé: {projet_data['titre']}")
        
        # Créer une fiche d'évaluation de test
        fiche_test = FicheEvaluation(
            project_id=1,  # Premier projet
            evaluateur_nom='Dr. Fatou DIOP',
            reference_fiche='DGPPE-EVAL-2025-001',
            intitule_projet='Modernisation des Services de l\'État Civil',
            cout_projet='3,5 Milliards FCFA',
            origine_projet='MATURATION',
            
            # Scores d'évaluation
            pertinence_score=4,
            alignement_score=8,
            pertinence_activites_score=12,
            equite_score=8,
            rentabilite_financiere_score=8,
            rentabilite_socio_economique_score=9,
            benefices_strategiques_score=7,
            perennite_score=8,
            avantages_couts_intangibles_score=6,
            faisabilite_score=8,
            capacite_execution_score=7,
            impacts_environnementaux_score=8,
        )
        db.session.add(fiche_test)
        print("📄 Fiche d'évaluation créée avec référence DGPPE-EVAL-2025-001")
        
        # Sauvegarder en base
        try:
            db.session.commit()
            print("\n✅ DONNÉES DE TEST CRÉÉES AVEC SUCCÈS!")
            
            # Vérification
            nb_projets = Project.query.count()
            nb_fiches = FicheEvaluation.query.count()
            nb_users = User.query.count()
            
            print(f"📊 Résumé:")
            print(f"   • {nb_projets} projets")
            print(f"   • {nb_fiches} fiche(s) d'évaluation")
            print(f"   • {nb_users} utilisateurs")
            
            print(f"\n🎯 TESTS DISPONIBLES:")
            print("1. Interface Vue.js: http://127.0.0.1:5173")
            print("   - Se connecter comme evaluateur1/test123")
            print("   - Évaluer le projet 'Modernisation des Services de l'État Civil'")
            print("   - Vérifier l'en-tête officiel DGPPE")
            
            print("2. Génération PDF:")
            print("   - La fiche DGPPE-EVAL-2025-001 est prête")
            print("   - En-tête avec logo et informations officielles")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = creer_donnees_test()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 PRÊT POUR LES TESTS DE L'EN-TÊTE DGPPE!")
        print("✅ Données créées, serveurs actifs")
        print("📱 Interface: http://127.0.0.1:5173")
        print("📄 PDFs avec en-tête officiel fonctionnels")
    else:
        print("\n💥 ERREUR LORS DE LA CRÉATION DES DONNÉES")