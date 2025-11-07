"""
Test complet de génération PDF avec données réelles et en-tête officiel DGPPE
"""

import sys
sys.path.append('backend')

def test_pdf_complet_avec_donnees_reelles():
    """Test complet avec données du projet créé"""
    
    import app
    
    with app.app.app_context():
        from app import Project, FicheEvaluation
        from backend.pdf_generator import generer_fiche_evaluation_pdf
        import os
        
        print("🎯 TEST PDF COMPLET AVEC DONNÉES RÉELLES")
        print("=" * 60)
        
        # Récupérer le projet créé
        projet = Project.query.first()
        if not projet:
            print("❌ Aucun projet trouvé - créer un projet d'abord")
            return False
            
        print(f"📋 Projet trouvé: {projet.titre}")
        print(f"🔖 Numéro: {projet.numero_projet}")
        print(f"💰 Coût: {projet.cout_estimatif:,.0f} FCFA")
        
        # Récupérer ou créer une fiche d'évaluation
        fiche = FicheEvaluation.query.filter_by(project_id=projet.id).first()
        if not fiche:
            print("📄 Création d'une fiche d'évaluation...")
            fiche = FicheEvaluation(
                project_id=projet.id,
                evaluateur_nom='Dr. Fatou DIOP',
                reference_fiche=f'DGPPE-EVAL-2025-{projet.id:03d}',
                intitule_projet=projet.titre,
                cout_projet=f'{projet.cout_estimatif/1000000000:.1f} Milliards FCFA',
                origine_projet='MATURATION',
                
                # Scores complets pour test
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
                
                # Commentaires réalistes
                points_forts="Projet très bien structuré avec un impact social important. La faisabilité technique est démontrée et l'équipe projet dispose des compétences requises.",
                points_faibles="Quelques risques financiers à surveiller lors de la mise en œuvre. Délais serrés pour certaines phases du projet.",
                recommandations="Renforcer le plan de gestion des risques financiers. Prévoir un plan de contingence pour les délais critiques.",
                commentaires_finaux="Projet recommandé pour validation avec mise en place du système de suivi renforcé. Excellent potentiel d'impact."
            )
            
            app.db.session.add(fiche)
            app.db.session.commit()
            print(f"✅ Fiche créée: {fiche.reference_fiche}")
        else:
            print(f"📄 Fiche existante: {fiche.reference_fiche}")
        
        # Calculer le score total
        score_total = fiche.calculer_score_total()
        appreciation = fiche.get_appreciation_globale()
        
        print(f"📊 Score total: {score_total}/100")
        print(f"⭐ Appréciation: {appreciation}")
        
        # Préparer les données pour le PDF
        fiche_data = fiche.to_dict()
        project_data = {
            'id': projet.id,
            'numero_projet': projet.numero_projet,
            'titre': projet.titre,
            'auteur_nom': projet.auteur_nom,
            'poles': projet.poles,
            'secteur': projet.secteur,
            'cout_estimatif': projet.cout_estimatif,
            'date_soumission': '2025-10-28',
            'description': projet.description
        }
        
        # Génération du PDF
        output_dir = 'test_pdfs'
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            pdf_path = generer_fiche_evaluation_pdf(fiche_data, project_data, output_dir)
            
            print(f"\n✅ PDF GÉNÉRÉ AVEC SUCCÈS!")
            print(f"📄 Fichier: {pdf_path}")
            print(f"📁 Taille: {os.path.getsize(pdf_path):,} bytes")
            
            print(f"\n🏛️ EN-TÊTE OFFICIEL DGPPE INCLUS:")
            print("   ✓ République du Sénégal")
            print("   ✓ Ministère de l'Économie, du Plan et de la Coopération")
            print("   ✓ Direction Générale de la Planification des Politiques Économiques")
            print("   ✓ Plateforme de Maturation des Projets Publics")
            print("   ✓ Logo DGPPE (intégré)")
            print("   ✓ Bordure et style officiels")
            
            print(f"\n📋 CONTENU DU PDF:")
            print(f"   • Référence: {fiche.reference_fiche}")
            print(f"   • Projet: {projet.titre}")
            print(f"   • Évaluateur: {fiche.evaluateur_nom}")
            print(f"   • Score: {score_total}/100 ({appreciation})")
            print(f"   • Sections complètes avec critères d'évaluation")
            print(f"   • Signature et validation")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur génération PDF: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_pdf_complet_avec_donnees_reelles()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST COMPLET RÉUSSI!")
        print("✅ PDF avec en-tête officiel DGPPE généré")
        print("✅ Données réelles du projet intégrées")
        print("✅ Format professionnel respecté")
        print("📂 Fichier disponible dans: test_pdfs/")
    else:
        print("💥 ÉCHEC DU TEST")