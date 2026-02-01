#!/usr/bin/env python3
"""
Script de migration pré-démarrage (compatible SQLite + PostgreSQL)
Exécuté AVANT app.py pour s'assurer que toutes les colonnes/tables existent
"""
import os
import sys

# Déterminer l'URI de la base de données
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Render fournit 'postgres://' mais SQLAlchemy 2.x exige 'postgresql://'
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    is_postgres = True
    print(f"[PRE-MIGRATION] Base de données: PostgreSQL")
else:
    DATA_DIR = os.environ.get('DATA_DIR', '/data')
    db_path = os.path.join(DATA_DIR, 'maturation.db')
    if not os.path.exists(db_path):
        db_path = 'maturation.db'
    DATABASE_URL = f"sqlite:///{db_path}"
    is_postgres = False
    print(f"[PRE-MIGRATION] Base de données: SQLite ({db_path})")

try:
    from sqlalchemy import create_engine, text, inspect

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        inspector = inspect(engine)

        def get_columns(table_name):
            """Retourne l'ensemble des noms de colonnes d'une table"""
            try:
                return {col['name'] for col in inspector.get_columns(table_name)}
            except Exception:
                return set()

        def add_column_if_missing(table_name, col_name, col_type):
            cols = get_columns(table_name)
            if cols and col_name not in cols:
                print(f"[PRE-MIGRATION] Ajout de {table_name}.{col_name}...")
                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"))
                conn.commit()
                return True
            return False

        # WAL checkpoint uniquement pour SQLite
        if not is_postgres:
            print("[PRE-MIGRATION] Checkpoint WAL en cours...")
            conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
            result = conn.execute(text("PRAGMA wal_checkpoint")).fetchone()
            print(f"[PRE-MIGRATION] ✓ WAL checkpoint terminé")

        # Migration 1: Colonne must_change_password dans users
        cols = get_columns('users')
        if cols and 'must_change_password' not in cols:
            print("[PRE-MIGRATION] Ajout de la colonne must_change_password...")
            conn.execute(text("ALTER TABLE users ADD COLUMN must_change_password BOOLEAN DEFAULT FALSE"))
            conn.commit()
            print("[PRE-MIGRATION] ✓ Colonne must_change_password ajoutée")
        else:
            print("[PRE-MIGRATION] ✓ Colonne must_change_password existe déjà")

        # Migration 2: Colonnes GPS dans project
        project_cols = get_columns('project')
        if project_cols and 'gps_latitude' not in project_cols:
            print("[PRE-MIGRATION] Ajout des colonnes GPS au projet...")
            conn.execute(text("ALTER TABLE project ADD COLUMN gps_latitude FLOAT"))
            conn.execute(text("ALTER TABLE project ADD COLUMN gps_longitude FLOAT"))
            conn.execute(text("ALTER TABLE project ADD COLUMN gps_accuracy INTEGER"))
            conn.commit()
            print("[PRE-MIGRATION] ✓ Colonnes GPS ajoutées")
        else:
            print("[PRE-MIGRATION] ✓ Colonnes GPS existent déjà")

        # Récupérer la liste des tables existantes
        table_names = inspector.get_table_names()

        # Migration 3: Activer must_change_password pour les comptes admin existants
        if 'users' in table_names:
            print("[PRE-MIGRATION] Activation du changement de mot de passe obligatoire pour les comptes admin...")
            result = conn.execute(text("""
                UPDATE users
                SET must_change_password = TRUE
                WHERE role IN ('admin', 'secretariatsct', 'presidencesct', 'presidencecomite')
                AND (must_change_password IS NULL OR must_change_password = FALSE)
            """))
            conn.commit()
            print(f"[PRE-MIGRATION] ✓ {result.rowcount} compte(s) admin mis à jour")
        else:
            print("[PRE-MIGRATION] ✓ Table users n'existe pas encore (premier démarrage)")

        # Migration 4: Table project_version (nécessite que 'project' existe pour la FK)
        if 'project' in table_names and 'project_version' not in table_names:
            print("[PRE-MIGRATION] Création de la table project_version...")
            pk_type = "SERIAL PRIMARY KEY" if is_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
            conn.execute(text(f"""
                CREATE TABLE project_version (
                    id {pk_type},
                    project_id INTEGER NOT NULL,
                    version_number INTEGER NOT NULL,
                    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    modified_by VARCHAR(100),
                    modification_type VARCHAR(50),
                    change_summary TEXT,
                    project_data TEXT NOT NULL,
                    statut_before VARCHAR(100),
                    statut_after VARCHAR(100),
                    FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE
                )
            """))
            conn.execute(text("CREATE INDEX idx_project_version_project_id ON project_version(project_id)"))
            conn.execute(text("CREATE INDEX idx_project_version_modified_at ON project_version(modified_at)"))
            conn.commit()
            print("[PRE-MIGRATION] ✓ Table project_version créée")
        else:
            print("[PRE-MIGRATION] ✓ Table project_version existe déjà")

        # Migration 5: Colonnes recommandations pour fiche_evaluation
        fiche_cols = get_columns('fiche_evaluation')
        recommandations_cols = [
            'pertinence_recommandations',
            'alignement_recommandations',
            'activites_couts_recommandations',
            'equite_recommandations',
            'viabilite_recommandations',
            'rentabilite_recommandations',
            'benefices_strategiques_recommandations',
            'perennite_recommandations',
            'avantages_intangibles_recommandations',
            'faisabilite_recommandations',
            'ppp_recommandations',
            'impact_environnemental_recommandations'
        ]

        added_count = 0
        for col in recommandations_cols:
            if fiche_cols and col not in fiche_cols:
                print(f"[PRE-MIGRATION] Ajout de la colonne {col}...")
                conn.execute(text(f"ALTER TABLE fiche_evaluation ADD COLUMN {col} TEXT"))
                added_count += 1

        if added_count > 0:
            conn.commit()
            print(f"[PRE-MIGRATION] ✓ {added_count} colonne(s) recommandations ajoutée(s)")
        else:
            print("[PRE-MIGRATION] ✓ Toutes les colonnes recommandations existent déjà")

        # Migration 7: Élargir project.poles de VARCHAR(150) à TEXT (PostgreSQL uniquement)
        if is_postgres and 'project' in table_names:
            try:
                conn.execute(text("ALTER TABLE project ALTER COLUMN poles TYPE TEXT"))
                conn.commit()
                print("[PRE-MIGRATION] ✓ Colonne project.poles élargie à TEXT")
            except Exception:
                conn.rollback()

        # Migration 6: Corriger les projets "en évaluation" sans évaluabilité confirmée
        if 'project' in table_names:
            print("[PRE-MIGRATION] Correction des projets 'en évaluation' sans évaluabilité confirmée...")
            result = conn.execute(text("""
                UPDATE project
                SET statut = 'assigné'
                WHERE statut = 'en évaluation'
                  AND (evaluabilite IS NULL OR evaluabilite != 'evaluable')
            """))
            if result.rowcount > 0:
                conn.commit()
                print(f"[PRE-MIGRATION] ✓ {result.rowcount} projet(s) corrigé(s) → statut remis à 'assigné'")
            else:
                print("[PRE-MIGRATION] ✓ Aucun projet à corriger")
        else:
            print("[PRE-MIGRATION] ✓ Table project n'existe pas encore (premier démarrage)")

    print("[PRE-MIGRATION] ✓ Migrations terminées avec succès!")
    sys.exit(0)

except Exception as e:
    print(f"[PRE-MIGRATION] ✗ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
