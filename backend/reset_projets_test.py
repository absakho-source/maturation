#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour supprimer tous les projets de test et les recréer
"""

import sys
import os

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Project

def reset_projets():
    """Supprimer tous les projets et recréer les projets de test"""

    with app.app_context():
        print("🗑️  Suppression de tous les projets...")
        print("=" * 70)

        # Compter les projets avant suppression
        count_avant = Project.query.count()
        print(f"📊 {count_avant} projet(s) trouvé(s) dans la base de données")

        if count_avant == 0:
            print("⚠️  Aucun projet à supprimer")
        else:
            # Supprimer tous les projets
            try:
                Project.query.delete()
                db.session.commit()
                print(f"✅ {count_avant} projet(s) supprimé(s) avec succès")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erreur lors de la suppression: {e}")
                return False

        print()
        print("=" * 70)
        print("🚀 Maintenant, lancez: python3 creer_projets_exemple.py")
        print("=" * 70)

        return True

if __name__ == "__main__":
    success = reset_projets()
    sys.exit(0 if success else 1)
