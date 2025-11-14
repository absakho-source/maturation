#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier l'état d'un projet
"""
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from db import db
from models import Project, FicheEvaluation, DocumentProjet

def diagnose_project(project_id):
    """Diagnostic complet d'un projet"""
    with app.app_context():
        project = Project.query.get(project_id)

        if not project:
            print(f"❌ Projet avec ID {project_id} non trouvé")
            return

        print(f"\n{'='*60}")
        print(f"DIAGNOSTIC DU PROJET #{project_id}")
        print(f"{'='*60}\n")

        print(f"[INFORMATIONS PROJET]")
        print(f"  Numéro: {project.numero_projet}")
        print(f"  Titre: {project.titre}")
        print(f"  Statut: {project.statut}")
        print(f"  Évaluateur: {project.evaluateur_nom}")
        print(f"  Soumissionnaire: {project.auteur_nom}")

        print(f"\n[ÉTAT ÉVALUATION]")
        print(f"  evaluation_prealable: {project.evaluation_prealable}")
        print(f"  evaluation_prealable_date: {project.evaluation_prealable_date}")
        print(f"  evaluation_prealable_commentaire: {project.evaluation_prealable_commentaire}")
        print(f"  avis: {project.avis}")
        print(f"  commentaires: {project.commentaires}")

        # Vérifier fiche d'évaluation
        fiche = FicheEvaluation.query.filter_by(project_id=project_id).first()
        print(f"\n[FICHE D'ÉVALUATION]")
        if fiche:
            print(f"  ✅ Fiche existante:")
            print(f"     - Évaluateur: {fiche.evaluateur_nom}")
            print(f"     - Score total: {fiche.score_total}/100")
            print(f"     - Date: {fiche.date_evaluation}")
        else:
            print(f"  ℹ️  Aucune fiche d'évaluation active")

        # Vérifier documents archivés
        documents = DocumentProjet.query.filter_by(project_id=project_id).all()
        print(f"\n[DOCUMENTS DU PROJET]")
        if documents:
            print(f"  Nombre de documents: {len(documents)}")
            for doc in documents:
                print(f"\n  Document: {doc.nom_original}")
                print(f"    - Nom fichier: {doc.nom_fichier}")
                print(f"    - Type: {doc.type_document}")
                print(f"    - Auteur: {doc.auteur_nom} ({doc.auteur_role})")
                print(f"    - Description: {doc.description}")
                print(f"    - Visible pour: {doc.visible_pour_roles}")
                print(f"    - Date upload: {doc.date_upload}")
        else:
            print(f"  ℹ️  Aucun document")

        print(f"\n{'='*60}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        project_id = int(sys.argv[1])
    else:
        project_id = 13  # Par défaut projet test 1

    print(f"[DIAGNOSTIC] Analyse du projet {project_id}...")
    diagnose_project(project_id)
