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
            # Migration 1: Ajouter la colonne statut_comite à la table project (singulier)
            print("[MIGRATION] Vérification de la colonne 'statut_comite'...")

            # Récupérer les colonnes existantes
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('project')]

            if 'statut_comite' not in columns:
                print("[MIGRATION] Ajout de la colonne 'statut_comite'...")
                conn.execute(text("""
                    ALTER TABLE project
                    ADD COLUMN statut_comite VARCHAR(50)
                """))
                conn.commit()
                print("[MIGRATION] ✓ Colonne 'statut_comite' ajoutée avec succès")
            else:
                print("[MIGRATION] ✓ La colonne 'statut_comite' existe déjà")

            # Afficher quelques statistiques
            result = conn.execute(text("SELECT COUNT(*) FROM project"))
            total_projects = result.scalar()
            print(f"[MIGRATION] Nombre total de projets: {total_projects}")

            result = conn.execute(text("SELECT COUNT(*) FROM project WHERE statut_comite IS NOT NULL"))
            projects_with_status = result.scalar()
            print(f"[MIGRATION] Projets avec statut_comite défini: {projects_with_status}")

            # Migration 2: Ajouter la colonne fiche_evaluation_visible
            print("[MIGRATION] Vérification de la colonne 'fiche_evaluation_visible'...")

            columns = [col['name'] for col in inspector.get_columns('project')]

            if 'fiche_evaluation_visible' not in columns:
                print("[MIGRATION] Ajout de la colonne 'fiche_evaluation_visible'...")
                conn.execute(text("""
                    ALTER TABLE project
                    ADD COLUMN fiche_evaluation_visible BOOLEAN DEFAULT 0
                """))
                conn.commit()
                print("[MIGRATION] ✓ Colonne 'fiche_evaluation_visible' ajoutée avec succès")
            else:
                print("[MIGRATION] ✓ La colonne 'fiche_evaluation_visible' existe déjà")

            # Migration 3: Mettre à jour fiche_evaluation_visible pour les projets entérinés
            print("[MIGRATION] Mise à jour de fiche_evaluation_visible pour les projets entérinés...")
            result = conn.execute(text("""
                UPDATE project
                SET fiche_evaluation_visible = 1
                WHERE decision_finale = 'confirme'
                AND (fiche_evaluation_visible = 0 OR fiche_evaluation_visible IS NULL)
            """))
            conn.commit()
            count_updated = result.rowcount
            if count_updated > 0:
                print(f"[MIGRATION] ✓ {count_updated} projet(s) mis à jour avec fiche_evaluation_visible = True")
            else:
                print("[MIGRATION] ✓ Aucun projet à mettre à jour")

            # Migration 4: Supprimer les projets de test
            print("[MIGRATION] Suppression des projets de test...")
            test_project_ids = [1, 2, 4, 9, 13, 14, 15, 16, 18, 19]
            placeholders = ','.join(['?'] * len(test_project_ids))

            # Vérifier combien de projets vont être supprimés
            result = conn.execute(
                text(f"SELECT COUNT(*) FROM project WHERE id IN ({placeholders})"),
                test_project_ids
            )
            count_to_delete = result.scalar()

            if count_to_delete > 0:
                result = conn.execute(
                    text(f"DELETE FROM project WHERE id IN ({placeholders})"),
                    test_project_ids
                )
                conn.commit()
                print(f"[MIGRATION] ✓ {count_to_delete} projet(s) de test supprimé(s)")
            else:
                print("[MIGRATION] ✓ Aucun projet de test à supprimer")

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
