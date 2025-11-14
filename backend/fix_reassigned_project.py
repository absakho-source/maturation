#!/usr/bin/env python3
"""
Script pour réinitialiser l'évaluation préalable d'un projet réassigné
"""
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from db import db
from models import Project

def fix_reassigned_project(numero_projet):
    """Réinitialise l'évaluation préalable d'un projet réassigné"""
    with app.app_context():
        project = Project.query.filter_by(numero_projet=numero_projet).first()

        if not project:
            print(f"❌ Projet {numero_projet} non trouvé")
            return False

        print(f"[INFO] Projet trouvé: {project.titre}")
        print(f"  - Évaluateur: {project.evaluateur_nom}")
        print(f"  - Statut: {project.statut}")
        print(f"  - Évaluation préalable: {project.evaluation_prealable}")

        if project.evaluation_prealable:
            print(f"\n[FIX] Réinitialisation de l'évaluation préalable...")
            project.evaluation_prealable = None
            project.evaluation_prealable_date = None
            project.evaluation_prealable_commentaire = None

            db.session.commit()
            print(f"✅ Évaluation préalable réinitialisée pour {numero_projet}")
            print(f"   L'évaluateur {project.evaluateur_nom} peut maintenant faire son évaluation")
            return True
        else:
            print(f"ℹ️  Aucune évaluation préalable à réinitialiser")
            return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        numero = sys.argv[1]
    else:
        numero = "DGPPE-2025-001"

    print(f"[MIGRATION] Correction du projet {numero}...")
    fix_reassigned_project(numero)
