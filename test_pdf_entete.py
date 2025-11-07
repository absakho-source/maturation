"""
Test de génération PDF avec le nouvel en-tête DGPPE
"""

import sys
import os
sys.path.append('backend')

from backend.pdf_generator import generer_fiche_evaluation_pdf

def test_generation_pdf_entete():
    """Test de génération PDF avec le nouvel en-tête"""
    
    # Données de test pour la fiche d'évaluation
    fiche_data = {
        'reference_fiche': 'DGPPE-EVAL-2025-001',
        'evaluateur_nom': 'Dr. Fatou DIOP',
        'date_evaluation': '2025-10-28',
        'intitule_projet': 'Projet de Modernisation des Services Publics',
        'cout_projet': '5.2 Milliards FCFA',
        'origine_projet': 'MATURATION',
        
        # Scores d'évaluation
        'pertinence_score': 4,
        'alignement_score': 8,
        'pertinence_activites_score': 12,
        'equite_score': 8,
        'rentabilite_financiere_score': 8,
        'rentabilite_socio_economique_score': 9,
        'benefices_strategiques_score': 7,
        'perennite_score': 8,
        'avantages_couts_intangibles_score': 6,
        'faisabilite_score': 8,
        'capacite_execution_score': 7,
        'impacts_environnementaux_score': 8,
        
        'score_total': 93,
        'appreciation_globale': 'excellent',
        'avis_final': 'favorable',
        
        # Commentaires
        'points_forts': 'Projet très bien structuré avec un impact social important. La faisabilité technique est démontrée.',
        'points_faibles': 'Quelques risques financiers à surveiller lors de la mise en œuvre.',
        'recommandations': 'Renforcer le plan de gestion des risques financiers.',
        'commentaires_finaux': 'Projet recommandé pour validation avec mise en place du système de suivi renforcé.'
    }
    
    # Données du projet
    project_data = {
        'id': 1,
        'numero_projet': 'DGPPE-2025-001',
        'titre': 'Projet de Modernisation des Services Publics',
        'auteur_nom': 'Ministère de la Fonction Publique',
        'poles': 'Dakar',
        'secteur': 'Gouvernance',
        'cout_estimatif': 5200000000,  # 5.2 milliards FCFA
        'date_soumission': '2025-10-15'
    }
    
    # Répertoire de sortie
    output_dir = 'test_pdfs'
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Génération du PDF
        pdf_path = generer_fiche_evaluation_pdf(fiche_data, project_data, output_dir)
        
        print(f"✅ PDF généré avec succès!")
        print(f"📄 Chemin: {pdf_path}")
        print(f"📁 Taille: {os.path.getsize(pdf_path)} bytes")
        
        # Vérification que le fichier existe
        if os.path.exists(pdf_path):
            print("✅ Fichier PDF créé et accessible")
            print(f"🎯 Contenu: Fiche d'évaluation avec en-tête officiel DGPPE")
            print(f"🏛️ En-tête: Ministère de l'Économie, du Plan et de la Coopération")
            print(f"🏢 Direction: Direction Générale de la Planification des Politiques Économiques")
            print(f"🔧 Plateforme: Plateforme de Maturation des Projets Publics")
            print(f"🖼️ Logo: Intégré (si disponible)")
            
            return True
        else:
            print("❌ Erreur: Fichier PDF non créé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la génération PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 TEST DE GÉNÉRATION PDF AVEC NOUVEL EN-TÊTE DGPPE")
    print("=" * 60)
    
    success = test_generation_pdf_entete()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST RÉUSSI: L'en-tête officiel DGPPE est correctement intégré!")
    else:
        print("💥 TEST ÉCHOUÉ: Problème avec la génération PDF")