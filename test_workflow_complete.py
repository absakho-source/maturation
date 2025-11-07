#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test complet du workflow de gestion des compléments
"""

import sys
import os
from datetime import datetime

# Ajouter le dossier backend au path pour importer les modèles
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, db, Project, User, Historique

def test_workflow_complet():
    """Test complet du workflow avec demande de compléments"""
    
    with app.app_context():
        print("=== TEST WORKFLOW COMPLET ===")
        print()
        
        # 1. Créer un projet de test
        print("1. Création du projet de test...")
        projet = Project(
            titre="Test Workflow Complet - Demande Compléments",
            description="Projet pour tester le workflow complet avec demande de compléments",
            secteur="Agriculture",
            poles="Dakar",
            cout_estimatif=50000,
            auteur_nom="Test Soumissionnaire",
            statut="soumis"
        )
        
        db.session.add(projet)
        db.session.commit()
        print(f"✅ Projet créé avec ID: {projet.id}")
        print()
        
        # 2. Simuler l'assignation par secrétariat
        print("2. Assignation par le secrétariat...")
        projet.statut = "assigné"
        projet.evaluateur_nom = "Test Evaluateur"
        projet.validation_secretariat = "valide"
        db.session.commit()
        print(f"✅ Projet assigné à l'évaluateur: {projet.evaluateur_nom}")
        print()
        
        # 3. Simuler demande de compléments par évaluateur
        print("3. Demande de compléments par l'évaluateur...")
        projet.statut = "compléments demandés"
        projet.complements_demande_message = "Merci de fournir le budget détaillé et le calendrier de mise en œuvre"
        db.session.commit()
        print(f"✅ Compléments demandés: {projet.complements_demande_message}")
        print()
        
        # 4. État actuel - Le soumissionnaire doit répondre
        print("4. État du workflow:")
        print(f"   - Statut: {projet.statut}")
        print(f"   - Évaluateur: {projet.evaluateur_nom}")
        print(f"   - Demande: {projet.complements_demande_message}")
        print("   - Action attendue: Soumissionnaire doit fournir les compléments")
        print()
        
        # 5. Simuler réponse du soumissionnaire
        print("5. Réponse du soumissionnaire...")
        projet.statut = "compléments fournis"
        projet.complements_reponse_message = "Voici le budget détaillé et le calendrier demandés"
        projet.complements_reponse_pieces = "budget_detaille.pdf,calendrier.pdf"
        db.session.commit()
        print(f"✅ Compléments fournis: {projet.complements_reponse_message}")
        print(f"   Pièces: {projet.complements_reponse_pieces}")
        print()
        
        # 6. Vérifier que le projet revient au secrétariat
        print("6. Vérification du retour au secrétariat:")
        if projet.statut == "compléments fournis":
            print("✅ Le projet est maintenant dans le panier du secretariatsct")
            print("   - Le secrétariat peut valider la demande de compléments")
            print("   - Cela déclenchera la réévaluation")
        else:
            print("❌ Erreur: le projet n'est pas revenu au secrétariat")
        print()
        
        # 7. Simuler validation secrétariat des compléments
        print("7. Validation secrétariat des compléments...")
        projet.statut = "réassigné"  # pour réévaluation
        db.session.commit()
        print("✅ Secrétariat valide - projet réassigné pour réévaluation")
        print()
        
        # 8. Simuler évaluation finale
        print("8. Évaluation finale...")
        projet.statut = "évalué"
        projet.avis = "favorable"
        projet.commentaires = "Projet conforme après fourniture des compléments"
        db.session.commit()
        print(f"✅ Évaluation finale: {projet.avis}")
        print(f"   Commentaires: {projet.commentaires}")
        print()
        
        # 9. Simuler validation presidencesct (SANS decision_finale)
        print("9. Validation par presidencesct...")
        projet.statut = "validé par presidencesct"
        projet.avis_presidencesct = "favorable"
        # IMPORTANT: Ne pas assigner decision_finale ici !
        db.session.commit()
        print(f"✅ Validation presidencesct: {projet.avis_presidencesct}")
        print(f"   Statut: {projet.statut}")
        print(f"   Decision finale: {projet.decision_finale} (doit être None)")
        print()
        
        # 10. Vérifier que le projet va à presidencecomite
        print("10. Vérification handoff vers presidencecomite:")
        if projet.statut == "validé par presidencesct" and projet.decision_finale is None:
            print("✅ Le projet est correctement transmis à presidencecomite")
            print("   - presidencecomite peut prendre la décision finale")
        else:
            print("❌ Erreur: le projet n'est pas correctement transmis")
            print(f"   Statut: {projet.statut}")
            print(f"   Decision finale: {projet.decision_finale}")
        print()
        
        # 11. Simuler décision finale presidencecomite
        print("11. Décision finale par presidencecomite...")
        projet.decision_finale = "confirme"
        projet.commentaires_finaux = "Projet validé définitivement"
        db.session.commit()
        print(f"✅ Décision finale: {projet.decision_finale}")
        print(f"   Commentaires: {projet.commentaires_finaux}")
        print()
        
        print("=== RÉSULTAT FINAL ===")
        print(f"Projet ID: {projet.id}")
        print(f"Titre: {projet.titre}")
        print(f"Statut final: {projet.statut}")
        print(f"Avis: {projet.avis}")
        print(f"Validation SCT: {projet.avis_presidencesct}")
        print(f"Décision finale: {projet.decision_finale}")
        print()
        print("✅ WORKFLOW COMPLET TESTÉ AVEC SUCCÈS")
        
        return projet.id

def nettoyer_projet_test(project_id):
    """Nettoyer le projet de test"""
    with app.app_context():
        projet = Project.query.get(project_id)
        if projet:
            db.session.delete(projet)
            db.session.commit()
            print(f"🧹 Projet de test {project_id} supprimé")

if __name__ == "__main__":
    project_id = test_workflow_complet()
    
    # Demander si on veut nettoyer
    response = input("\nVoulez-vous supprimer le projet de test ? (o/n): ")
    if response.lower() in ['o', 'oui', 'y', 'yes']:
        nettoyer_projet_test(project_id)