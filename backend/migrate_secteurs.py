#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migration : Corriger les secteurs incorrects dans les projets existants
"""

import sys
import os

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Project

# Mapping des anciens secteurs vers les secteurs officiels
SECTEUR_CORRECTIONS = {
    "énergie": "énergies-mines",
    "environnement-eau": "environnement-eau-assainissement",
    "environnement": "environnement-eau-assainissement",
    "éducation": "éducation-formation-recherche",
    "santé": "santé-action sociale",
    "transport": "transports-infrastructures",
    "industrie": "industrie-artisanat",
    "télécommunications": "postes-communication-télécommunications-économie numérique",
    "numérique": "postes-communication-télécommunications-économie numérique",
    "population": "population-jeunesse-emploi-travail-fonction publique",
    "gouvernance": "gouvernance-justice-défense-sécurité",
    "tourisme": "tourisme-culture",
    "agriculture": "agriculture-élevage-pêche",
    "habitat": "habitat-urbanisme",
    "sports": "sports-loisirs",
    "aménagement": "aménagement-développement territorial-décentralisation",
    "affaires étrangères": "affaires étrangères-intégration"
}

def migrate_secteurs():
    """Corriger les secteurs dans tous les projets existants"""

    with app.app_context():
        print("🔧 Migration des secteurs des projets...")
        print("=" * 70)

        # Récupérer tous les projets
        projets = Project.query.all()
        total = len(projets)
        modifies = 0

        print(f"📊 {total} projets trouvés dans la base de données\n")

        for projet in projets:
            secteur_original = projet.secteur

            # Vérifier si le secteur nécessite une correction
            if secteur_original in SECTEUR_CORRECTIONS:
                nouveau_secteur = SECTEUR_CORRECTIONS[secteur_original]
                projet.secteur = nouveau_secteur
                modifies += 1

                print(f"✏️  Projet #{projet.id} - {projet.numero_projet or 'sans numéro'}")
                print(f"   Titre: {projet.titre[:60]}...")
                print(f"   Ancien secteur: {secteur_original}")
                print(f"   Nouveau secteur: {nouveau_secteur}")
                print()

        if modifies > 0:
            try:
                db.session.commit()
                print("=" * 70)
                print(f"✅ Migration terminée avec succès!")
                print(f"   {modifies} projet(s) modifié(s) sur {total}")
                return True
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erreur lors du commit: {e}")
                return False
        else:
            print("=" * 70)
            print("✅ Aucune correction nécessaire - tous les secteurs sont déjà corrects")
            return True

if __name__ == "__main__":
    success = migrate_secteurs()
    sys.exit(0 if success else 1)
