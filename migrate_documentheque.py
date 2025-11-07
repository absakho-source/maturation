#!/usr/bin/env python3
"""
Script de migration pour ajouter la table documents_projet (documenthèque)
"""
import sys
import os

# Ajouter le répertoire backend au path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Importer depuis le backend
os.chdir(backend_path)
from app import app, db
from models import DocumentProjet

def migrate():
    """Crée la table documents_projet si elle n'existe pas"""
    print("🔄 Démarrage de la migration pour la documenthèque...")

    with app.app_context():
        try:
            # Créer toutes les tables manquantes
            db.create_all()
            print("✅ Table documents_projet créée avec succès (ou déjà existante)")

            # Vérifier que la table existe bien
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            if 'documents_projet' in tables:
                print("✅ Vérification: la table documents_projet existe bien")

                # Afficher les colonnes
                columns = inspector.get_columns('documents_projet')
                print("\n📋 Colonnes de la table documents_projet:")
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
            else:
                print("❌ Erreur: la table documents_projet n'a pas été créée")
                return False

            print("\n✅ Migration terminée avec succès!")
            return True

        except Exception as e:
            print(f"❌ Erreur lors de la migration: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
