#!/usr/bin/env python3
"""
Script pour corriger la terminologie des avis dans la base de données
Remplace 'favorable sous réserve' par 'favorable sous conditions'
"""

from app import app, db
from models import Project, FicheEvaluation

def fix_avis_terminology():
    """Corrige la terminologie dans les projets et fiches d'évaluation"""
    with app.app_context():
        count_projects = 0
        count_fiches = 0

        # 1. Corriger les avis des projets
        print("🔍 Recherche des projets avec 'favorable sous réserve'...")
        projects = Project.query.filter(
            db.or_(
                Project.avis.like('%favorable sous réserve%'),
                Project.avis.like('%favorable sous reserve%')
            )
        ).all()

        for project in projects:
            old_avis = project.avis
            if old_avis:
                new_avis = old_avis.replace('favorable sous réserve', 'favorable sous conditions')
                new_avis = new_avis.replace('favorable sous reserve', 'favorable sous conditions')
                new_avis = new_avis.replace('Favorable sous réserve', 'Favorable sous conditions')

                if new_avis != old_avis:
                    project.avis = new_avis
                    count_projects += 1
                    print(f"  ✓ Projet {project.numero_projet}: '{old_avis}' → '{new_avis}'")

        # 2. Corriger les propositions des fiches d'évaluation
        print("\n🔍 Recherche des fiches avec 'favorable sous réserve'...")
        fiches = FicheEvaluation.query.filter(
            db.or_(
                FicheEvaluation.proposition.like('%favorable sous réserve%'),
                FicheEvaluation.proposition.like('%favorable sous reserve%')
            )
        ).all()

        for fiche in fiches:
            old_prop = fiche.proposition
            if old_prop:
                new_prop = old_prop.replace('favorable sous réserve', 'favorable sous conditions')
                new_prop = new_prop.replace('favorable sous reserve', 'favorable sous conditions')
                new_prop = new_prop.replace('Favorable sous réserve', 'Favorable sous conditions')

                if new_prop != old_prop:
                    fiche.proposition = new_prop
                    count_fiches += 1
                    project = Project.query.get(fiche.project_id)
                    print(f"  ✓ Fiche projet {project.numero_projet if project else fiche.project_id}: '{old_prop}' → '{new_prop}'")

        # 3. Commit les changements
        if count_projects > 0 or count_fiches > 0:
            db.session.commit()
            print(f"\n✅ Terminologie corrigée :")
            print(f"   - {count_projects} projet(s)")
            print(f"   - {count_fiches} fiche(s) d'évaluation")
            return True
        else:
            print("\n✓ Aucune correction nécessaire")
            return False

if __name__ == "__main__":
    print("🔧 Correction terminologie des avis\n")
    fix_avis_terminology()
