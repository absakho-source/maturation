#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour vérifier le secteur du projet DGPPE-2025-001 en production
"""
from app import app, db
from models import Project

def check_production_sector():
    """Vérifie le secteur du projet DGPPE-2025-001"""
    with app.app_context():
        # Chercher le projet DGPPE-2025-001
        project = Project.query.filter_by(numero_projet='DGPPE-2025-001').first()

        if project:
            print(f"✓ Projet trouvé: {project.numero_projet}")
            print(f"  Titre: {project.titre}")
            print(f"  Secteur: '{project.secteur}'")
            print(f"  Longueur secteur: {len(project.secteur) if project.secteur else 0}")
            print(f"  Bytes secteur: {project.secteur.encode('utf-8') if project.secteur else 'N/A'}")

            # Afficher tous les secteurs distincts
            print("\n📊 Tous les secteurs dans la base:")
            all_projects = Project.query.all()
            secteurs = set()
            for p in all_projects:
                if p.secteur:
                    secteurs.add(p.secteur)

            for secteur in sorted(secteurs):
                count = Project.query.filter_by(secteur=secteur).count()
                print(f"  - '{secteur}': {count} projet(s)")
        else:
            print("✗ Projet DGPPE-2025-001 non trouvé")

            # Lister tous les projets
            print("\n📋 Tous les projets:")
            all_projects = Project.query.all()
            for p in all_projects:
                print(f"  - {p.numero_projet}: {p.titre} ({p.secteur})")

if __name__ == "__main__":
    check_production_sector()
