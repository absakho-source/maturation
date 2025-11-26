#!/usr/bin/env python3
"""
Script de correction pour projet DGPPE-25-003
Synchronise l'avis du projet avec la fiche d'évaluation
"""

from app import app, db
from models import Project, FicheEvaluation

def fix_project_avis():
    """Corrige l'avis du projet DGPPE-25-003"""
    with app.app_context():
        # Trouver le projet
        project = Project.query.filter_by(numero_projet='DGPPE-25-003').first()

        if not project:
            print("❌ Projet DGPPE-25-003 non trouvé")
            return False

        print(f"📋 Projet trouvé: {project.titre}")
        print(f"   Avis actuel: {project.avis}")

        # Trouver la fiche d'évaluation
        fiche = FicheEvaluation.query.filter_by(project_id=project.id).first()

        if not fiche:
            print("❌ Fiche d'évaluation non trouvée")
            return False

        print(f"   Fiche - Score: {fiche.score_total}/100")
        print(f"   Fiche - Proposition: {fiche.proposition}")

        # Synchroniser l'avis
        if fiche.proposition and project.avis != fiche.proposition:
            old_avis = project.avis
            project.avis = fiche.proposition

            db.session.commit()

            print(f"\n✅ Avis mis à jour:")
            print(f"   Avant: {old_avis}")
            print(f"   Après: {project.avis}")
            return True
        else:
            print("\n✓ Avis déjà synchronisé")
            return True

if __name__ == "__main__":
    print("🔧 Correction avis projet DGPPE-25-003\n")
    fix_project_avis()
