#!/usr/bin/env python3
"""
Script de migration pour ajouter la table fichiers_message (fichiers multiples dans les messages)
"""
import sys
import os

# Ajouter le répertoire backend au path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Importer depuis le backend
os.chdir(backend_path)
from app import app, db
from models import FichierMessage

def migrate():
    """Crée la table fichiers_message si elle n'existe pas"""
    print("🔄 Démarrage de la migration pour les fichiers multiples dans les messages...")

    with app.app_context():
        try:
            # Créer toutes les tables manquantes
            db.create_all()

            print("\n✅ Migration terminée avec succès!")
            print("   La table fichiers_message a été créée.")
            print("   Les messages peuvent maintenant avoir plusieurs fichiers joints.")
            return True

        except Exception as e:
            print(f"❌ Erreur lors de la migration: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
