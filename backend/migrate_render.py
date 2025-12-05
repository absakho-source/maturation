#!/usr/bin/env python3
"""
Script de migration pour la base de données
Exécuté automatiquement au démarrage du backend
Utilise SQLAlchemy pour éviter les conflits de connexion
"""

from sqlalchemy import create_engine, text, inspect
import os


def migrate_database(db_path):
    """
    Exécute toutes les migrations nécessaires sur la base de données
    Retourne True si succès, False sinon
    """
    print(f"[MIGRATION] Connexion à la base de données: {db_path}")

    try:
        # Utiliser SQLAlchemy au lieu de sqlite3 directement
        engine = create_engine(f"sqlite:///{db_path}")

        with engine.connect() as conn:
            # Migration 1: Ajouter la colonne statut_comite à la table projects
            print("[MIGRATION] Vérification de la colonne 'statut_comite'...")

            # Récupérer les colonnes existantes
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('projects')]

            if 'statut_comite' not in columns:
                print("[MIGRATION] Ajout de la colonne 'statut_comite'...")
                conn.execute(text("""
                    ALTER TABLE projects
                    ADD COLUMN statut_comite VARCHAR(50)
                """))
                conn.commit()
                print("[MIGRATION] ✓ Colonne 'statut_comite' ajoutée avec succès")
            else:
                print("[MIGRATION] ✓ La colonne 'statut_comite' existe déjà")

            # Afficher quelques statistiques
            result = conn.execute(text("SELECT COUNT(*) FROM projects"))
            total_projects = result.scalar()
            print(f"[MIGRATION] Nombre total de projets: {total_projects}")

            result = conn.execute(text("SELECT COUNT(*) FROM projects WHERE statut_comite IS NOT NULL"))
            projects_with_status = result.scalar()
            print(f"[MIGRATION] Projets avec statut_comite défini: {projects_with_status}")

            # Ajouter d'autres migrations ici au besoin
            # Migration 2: ...
            # Migration 3: ...

        print("[MIGRATION] ✓ Toutes les migrations ont été appliquées avec succès!")
        return True

    except Exception as e:
        print(f"[MIGRATION] ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Permet d'exécuter le script directement pour tester
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else "maturation.db"
    success = migrate_database(db_path)
    exit(0 if success else 1)
