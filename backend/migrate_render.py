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
            ids_str = ','.join(map(str, test_project_ids))

            # Vérifier combien de projets vont être supprimés
            result = conn.execute(
                text(f"SELECT COUNT(*) FROM project WHERE id IN ({ids_str})")
            )
            count_to_delete = result.scalar()

            if count_to_delete > 0:
                result = conn.execute(
                    text(f"DELETE FROM project WHERE id IN ({ids_str})")
                )
                conn.commit()
                print(f"[MIGRATION] ✓ {count_to_delete} projet(s) de test supprimé(s)")
            else:
                print("[MIGRATION] ✓ Aucun projet de test à supprimer")

            # Migration 5: Ajouter les colonnes pour l'édition et le masquage des messages
            print("[MIGRATION] Vérification des colonnes pour l'édition des messages...")

            # Vérifier les colonnes de messages_projet
            try:
                columns = [col['name'] for col in inspector.get_columns('messages_projet')]
            except:
                columns = []

            # Ajouter modifie_par
            if 'modifie_par' not in columns:
                print("[MIGRATION] Ajout de la colonne 'modifie_par'...")
                conn.execute(text("""
                    ALTER TABLE messages_projet
                    ADD COLUMN modifie_par VARCHAR(100)
                """))
                conn.commit()
                print("[MIGRATION] ✓ Colonne 'modifie_par' ajoutée")
            else:
                print("[MIGRATION] ✓ La colonne 'modifie_par' existe déjà")

            # Ajouter masque
            if 'masque' not in columns:
                print("[MIGRATION] Ajout de la colonne 'masque'...")
                conn.execute(text("""
                    ALTER TABLE messages_projet
                    ADD COLUMN masque BOOLEAN DEFAULT 0
                """))
                conn.commit()
                print("[MIGRATION] ✓ Colonne 'masque' ajoutée")
            else:
                print("[MIGRATION] ✓ La colonne 'masque' existe déjà")

            # Ajouter masque_par
            if 'masque_par' not in columns:
                print("[MIGRATION] Ajout de la colonne 'masque_par'...")
                conn.execute(text("""
                    ALTER TABLE messages_projet
                    ADD COLUMN masque_par VARCHAR(100)
                """))
                conn.commit()
                print("[MIGRATION] ✓ Colonne 'masque_par' ajoutée")
            else:
                print("[MIGRATION] ✓ La colonne 'masque_par' existe déjà")

            # Ajouter masque_raison
            if 'masque_raison' not in columns:
                print("[MIGRATION] Ajout de la colonne 'masque_raison'...")
                conn.execute(text("""
                    ALTER TABLE messages_projet
                    ADD COLUMN masque_raison TEXT
                """))
                conn.commit()
                print("[MIGRATION] ✓ Colonne 'masque_raison' ajoutée")
            else:
                print("[MIGRATION] ✓ La colonne 'masque_raison' existe déjà")

            # Ajouter date_masquage
            if 'date_masquage' not in columns:
                print("[MIGRATION] Ajout de la colonne 'date_masquage'...")
                conn.execute(text("""
                    ALTER TABLE messages_projet
                    ADD COLUMN date_masquage DATETIME
                """))
                conn.commit()
                print("[MIGRATION] ✓ Colonne 'date_masquage' ajoutée")
            else:
                print("[MIGRATION] ✓ La colonne 'date_masquage' existe déjà")

            # Migration 6: Créer la table historique_messages si elle n'existe pas
            print("[MIGRATION] Vérification de la table 'historique_messages'...")

            try:
                # Vérifier si la table existe
                conn.execute(text("SELECT 1 FROM historique_messages LIMIT 1"))
                print("[MIGRATION] ✓ La table 'historique_messages' existe déjà")
            except:
                print("[MIGRATION] Création de la table 'historique_messages'...")
                conn.execute(text("""
                    CREATE TABLE historique_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message_id INTEGER NOT NULL,
                        project_id INTEGER NOT NULL,
                        contenu_avant TEXT,
                        contenu_apres TEXT,
                        modifie_par VARCHAR(100) NOT NULL,
                        date_modification DATETIME DEFAULT CURRENT_TIMESTAMP,
                        type_modification VARCHAR(50) NOT NULL,
                        raison TEXT,
                        FOREIGN KEY (message_id) REFERENCES messages_projet(id),
                        FOREIGN KEY (project_id) REFERENCES project(id)
                    )
                """))
                conn.commit()
                print("[MIGRATION] ✓ Table 'historique_messages' créée avec succès")

            # Migration 7: Ajouter les nouveaux champs au projet (nouveauté, priorité, financement)
            print("[MIGRATION] Vérification des nouveaux champs projet...")

            columns = [col['name'] for col in inspector.get_columns('project')]

            # Ajouter nouveaute
            if 'nouveaute' not in columns:
                print("[MIGRATION] Ajout de la colonne 'nouveaute'...")
                conn.execute(text("""
                    ALTER TABLE project
                    ADD COLUMN nouveaute VARCHAR(50)
                """))
                conn.commit()
                print("[MIGRATION] ✓ Colonne 'nouveaute' ajoutée")
            else:
                print("[MIGRATION] ✓ La colonne 'nouveaute' existe déjà")

            # Ajouter projet_initial_ref
            if 'projet_initial_ref' not in columns:
                print("[MIGRATION] Ajout de la colonne 'projet_initial_ref'...")
                conn.execute(text("""
                    ALTER TABLE project
                    ADD COLUMN projet_initial_ref VARCHAR(50)
                """))
                conn.commit()
                print("[MIGRATION] ✓ Colonne 'projet_initial_ref' ajoutée")
            else:
                print("[MIGRATION] ✓ La colonne 'projet_initial_ref' existe déjà")

            # Ajouter niveau_priorite
            if 'niveau_priorite' not in columns:
                print("[MIGRATION] Ajout de la colonne 'niveau_priorite'...")
                conn.execute(text("""
                    ALTER TABLE project
                    ADD COLUMN niveau_priorite VARCHAR(50)
                """))
                conn.commit()
                print("[MIGRATION] ✓ Colonne 'niveau_priorite' ajoutée")
            else:
                print("[MIGRATION] ✓ La colonne 'niveau_priorite' existe déjà")

            # Ajouter type_financement
            if 'type_financement' not in columns:
                print("[MIGRATION] Ajout de la colonne 'type_financement'...")
                conn.execute(text("""
                    ALTER TABLE project
                    ADD COLUMN type_financement TEXT
                """))
                conn.commit()
                print("[MIGRATION] ✓ Colonne 'type_financement' ajoutée")
            else:
                print("[MIGRATION] ✓ La colonne 'type_financement' existe déjà")

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
