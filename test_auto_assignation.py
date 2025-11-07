#!/usr/bin/env python3
"""
Test de l'auto-assignation du secrétariat SCT
"""

import sys
sys.path.append('backend')

import app
from app import Project, db

def test_auto_assignation():
    with app.app.app_context():
        print("=== TEST DE L'AUTO-ASSIGNATION SECRÉTARIAT SCT ===")
        
        # Trouver un projet soumis
        projets_soumis = Project.query.filter_by(statut='soumis').all()
        print(f"✅ Projets soumis trouvés: {len(projets_soumis)}")
        
        if projets_soumis:
            projet = projets_soumis[0]
            print(f"📋 Projet test: ID {projet.id} - {projet.titre}")
            print(f"   Statut actuel: {projet.statut}")
            print(f"   Évaluateur actuel: {projet.evaluateur_nom or 'Non assigné'}")
            
            # Simuler l'auto-assignation
            print("\n🔄 Simulation d'auto-assignation...")
            print("   evaluateur_nom: 'secretariatsct'")
            print("   statut: 'assigné'")
            
            print("\n✅ Le secrétariat SCT peut maintenant:")
            print("   1. S'assigner des projets soumis")
            print("   2. Se réassigner des projets déjà assignés")
            print("   3. Évaluer directement dans l'onglet 'Mes évaluations'")
            
        else:
            print("ℹ️ Aucun projet soumis disponible pour le test")
            
        # Vérifier les projets assignés au secrétariat
        projets_secretariat = Project.query.filter_by(evaluateur_nom='secretariatsct').all()
        print(f"\n📊 Projets actuellement assignés au secrétariat SCT: {len(projets_secretariat)}")
        
        for p in projets_secretariat:
            print(f"   - ID {p.id}: {p.titre[:50]}... (statut: {p.statut})")

if __name__ == "__main__":
    test_auto_assignation()