"""
Restaurer des projets réalistes incluant le projet à Matam
"""

import sys
sys.path.append('backend')

def restaurer_projets_realistes():
    """Supprimer les projets fictifs et créer des projets réalistes"""
    
    import app
    
    with app.app.app_context():
        from app import Project, db
        
        print("🗑️ SUPPRESSION DES PROJETS FICTIFS")
        print("=" * 50)
        
        # Supprimer tous les projets actuels (fictifs)
        Project.query.delete()
        db.session.commit()
        print("✅ Tous les projets fictifs supprimés")
        
        print("\n📋 CRÉATION DE PROJETS RÉALISTES")
        print("=" * 50)
        
        # Créer des projets réalistes pour le Sénégal
        projets_realistes = [
            {
                'numero_projet': 'DGPPE-2025-001',
                'titre': 'Programme d\'électrification rurale à Matam',
                'auteur_nom': 'Ministère de l\'Énergie',
                'secteur': 'Énergie',
                'cout_estimatif': 2500000000,  # 2.5 milliards FCFA
                'poles': 'Nord-Est (Matam)',
                'statut': 'soumis',
                'description': 'Extension du réseau électrique dans les villages ruraux de la région de Matam',
            },
            {
                'numero_projet': 'DGPPE-2025-002',
                'titre': 'Construction d\'infrastructures scolaires à Dakar',
                'auteur_nom': 'Ministère de l\'Éducation',
                'secteur': 'Éducation',
                'cout_estimatif': 4200000000,  # 4.2 milliards FCFA
                'poles': 'Dakar',
                'statut': 'assigné',
                'evaluateur_nom': 'Agent DPSE 1',
                'description': 'Construction de 15 écoles primaires dans la banlieue dakaroise',
            },
            {
                'numero_projet': 'DGPPE-2025-003',
                'titre': 'Modernisation du port de Ziguinchor',
                'auteur_nom': 'Ministère des Transports',
                'secteur': 'Transport',
                'cout_estimatif': 8500000000,  # 8.5 milliards FCFA
                'poles': 'Sud (Ziguinchor)',
                'statut': 'évalué',
                'evaluateur_nom': 'Agent DPSE 2',
                'avis': 'favorable',
                'description': 'Réhabilitation et modernisation des infrastructures portuaires de Ziguinchor',
            },
            {
                'numero_projet': 'DGPPE-2025-004',
                'titre': 'Développement agricole à Kaolack',
                'auteur_nom': 'Ministère de l\'Agriculture',
                'secteur': 'Agriculture',
                'cout_estimatif': 3200000000,  # 3.2 milliards FCFA
                'poles': 'Centre (Kaolack)',
                'statut': 'assigné',
                'evaluateur_nom': 'Agent DPSE 1',
                'description': 'Programme d\'appui à la production agricole dans la région de Kaolack',
            },
            {
                'numero_projet': 'DGPPE-2025-005',
                'titre': 'Centre de santé régional à Saint-Louis',
                'auteur_nom': 'Ministère de la Santé',
                'secteur': 'Santé',
                'cout_estimatif': 5800000000,  # 5.8 milliards FCFA
                'poles': 'Nord (Saint-Louis)',
                'statut': 'soumis',
                'description': 'Construction d\'un centre de santé de référence à Saint-Louis',
            },
            {
                'numero_projet': 'DGPPE-2025-006',
                'titre': 'Infrastructure routière Thiès-Diourbel',
                'auteur_nom': 'Agence des Travaux et Gestion Routière',
                'secteur': 'Transport',
                'cout_estimatif': 12000000000,  # 12 milliards FCFA
                'poles': 'Thiès',
                'statut': 'évalué',
                'evaluateur_nom': 'Agent DPSE 2',
                'avis': 'favorable sous conditions',
                'description': 'Réhabilitation de la route Thiès-Diourbel sur 85 km',
            },
            {
                'numero_projet': 'DGPPE-2025-007',
                'titre': 'Adduction d\'eau potable à Tambacounda',
                'auteur_nom': 'Société Nationale des Eaux du Sénégal',
                'secteur': 'Eau et Assainissement',
                'cout_estimatif': 6500000000,  # 6.5 milliards FCFA
                'poles': 'Sud-Est (Tambacounda)',
                'statut': 'assigné',
                'evaluateur_nom': 'Agent DPSE 1',
                'description': 'Extension du réseau d\'adduction d\'eau potable à Tambacounda',
            },
            {
                'numero_projet': 'DGPPE-2025-008',
                'titre': 'Marché moderne de Fatick',
                'auteur_nom': 'Conseil Départemental de Fatick',
                'secteur': 'Commerce',
                'cout_estimatif': 1800000000,  # 1.8 milliards FCFA
                'poles': 'Centre (Fatick)',
                'statut': 'soumis',
                'description': 'Construction d\'un marché moderne à Fatick',
            },
            {
                'numero_projet': 'DGPPE-2025-009',
                'titre': 'Centre de formation professionnelle à Kolda',
                'auteur_nom': 'Ministère de la Formation Professionnelle',
                'secteur': 'Formation',
                'cout_estimatif': 2900000000,  # 2.9 milliards FCFA
                'poles': 'Sud (Kolda)',
                'statut': 'évalué',
                'evaluateur_nom': 'Agent DPSE 2',
                'avis': 'favorable',
                'description': 'Construction d\'un centre de formation aux métiers techniques à Kolda',
            }
        ]
        
        for i, projet_data in enumerate(projets_realistes, 1):
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
                description=projet_data['description']
            )
            db.session.add(projet)
            print(f"📋 {i}. {projet_data['titre']}")
            print(f"   💰 {projet_data['cout_estimatif']/1000000000:.1f} Md FCFA - {projet_data['poles']}")
        
        try:
            db.session.commit()
            print("\n✅ PROJETS RÉALISTES CRÉÉS AVEC SUCCÈS!")
            
            # Vérification
            nb_projets = Project.query.count()
            projets_matam = Project.query.filter(Project.titre.like('%Matam%')).all()
            
            print(f"\n📊 Résumé:")
            print(f"   • {nb_projets} projets créés")
            print(f"   • Projets à Matam: {len(projets_matam)}")
            
            if projets_matam:
                print(f"   • Projet Matam: {projets_matam[0].titre}")
            
            print(f"\n🎯 PROJETS PAR RÉGION:")
            regions = {}
            for p in Project.query.all():
                region = p.poles
                if region not in regions:
                    regions[region] = []
                regions[region].append(p.titre[:40] + "...")
            
            for region, titres in regions.items():
                print(f"   📍 {region}: {len(titres)} projet(s)")
                for titre in titres:
                    print(f"      - {titre}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = restaurer_projets_realistes()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 PROJETS RÉALISTES RESTAURÉS!")
        print("✅ Incluant le projet d'électrification à Matam")
        print("📍 Projets répartis dans toutes les régions du Sénégal")
        print("👥 Évaluateurs: Agent DPSE 1 & Agent DPSE 2")
    else:
        print("\n💥 ERREUR LORS DE LA RESTAURATION")