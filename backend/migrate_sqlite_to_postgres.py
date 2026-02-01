#!/usr/bin/env python3
"""
Script de migration one-time: SQLite → PostgreSQL
Exécuter une seule fois après le premier déploiement PostgreSQL.

Usage (sur le shell Render):
    python migrate_sqlite_to_postgres.py          # migration normale
    python migrate_sqlite_to_postgres.py --clear   # vider les tables PG avant de migrer
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.types import Boolean

# --- Configuration ---
SQLITE_PATH = os.environ.get('SQLITE_PATH', '/data/maturation.db')
POSTGRES_URL = os.environ.get('DATABASE_URL')

if not POSTGRES_URL:
    print("ERREUR: La variable DATABASE_URL n'est pas définie.")
    print("Ce script doit être exécuté dans un environnement avec PostgreSQL configuré.")
    sys.exit(1)

if POSTGRES_URL.startswith('postgres://'):
    POSTGRES_URL = POSTGRES_URL.replace('postgres://', 'postgresql://', 1)

if not os.path.exists(SQLITE_PATH):
    print(f"ERREUR: Le fichier SQLite n'existe pas: {SQLITE_PATH}")
    sys.exit(1)

CLEAR_MODE = '--clear' in sys.argv

# Ordre d'insertion respectant les clés étrangères
TABLES_ORDERED = [
    # Niveau 0: pas de FK
    'users',
    'ministere',
    'email_templates',
    'connexion_log',
    'formulaire_config',
    # Niveau 1: FK vers niveau 0
    'project',
    'section_formulaire',
    # Niveau 2: FK vers niveau 1
    'log',
    'historique',
    'fiche_evaluation',
    'fiches_evaluation_archive',
    'documents_projet',
    'messages_projet',
    'notifications',
    'contact_messages',
    'project_version',
    'champ_formulaire',
    'critere_evaluation',
    # Niveau 3: FK vers niveau 2
    'fichiers_message',
    'historique_messages',
]

# Ordre inverse pour TRUNCATE (respecter les FK)
TABLES_REVERSE = list(reversed(TABLES_ORDERED))


def get_boolean_columns(pg_inspector, table_name):
    """Retourne l'ensemble des colonnes de type BOOLEAN dans une table PostgreSQL."""
    bool_cols = set()
    for col in pg_inspector.get_columns(table_name):
        if isinstance(col['type'], Boolean):
            bool_cols.add(col['name'])
    return bool_cols


def convert_row(row_dict, boolean_columns):
    """Convertit les valeurs SQLite (0/1) en Python bool pour les colonnes BOOLEAN."""
    for col in boolean_columns:
        if col in row_dict and row_dict[col] is not None:
            row_dict[col] = bool(row_dict[col])
    return row_dict


def migrate():
    print("=" * 60)
    print("MIGRATION SQLite → PostgreSQL")
    if CLEAR_MODE:
        print("MODE: --clear (vidage des tables avant migration)")
    print("=" * 60)
    print(f"Source SQLite: {SQLITE_PATH}")
    print(f"Destination PostgreSQL: {POSTGRES_URL[:50]}...")
    print()

    sqlite_engine = create_engine(f"sqlite:///{SQLITE_PATH}")
    pg_engine = create_engine(POSTGRES_URL)

    sqlite_inspector = inspect(sqlite_engine)
    pg_inspector = inspect(pg_engine)

    sqlite_tables = set(sqlite_inspector.get_table_names())
    pg_tables = set(pg_inspector.get_table_names())

    # Mode --clear : vider les tables PostgreSQL (ordre inverse pour FK)
    if CLEAR_MODE:
        print("Vidage des tables PostgreSQL...")
        with pg_engine.connect() as conn:
            for table in TABLES_REVERSE:
                if table in pg_tables:
                    count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    if count > 0:
                        conn.execute(text(f"DELETE FROM {table}"))
                        conn.commit()
                        print(f"  Vidé {table} ({count} lignes supprimées)")
        print()

    total_rows = 0
    migrated_tables = 0
    skipped_tables = 0
    failed_tables = []

    for table in TABLES_ORDERED:
        if table not in sqlite_tables:
            print(f"  SKIP {table}: n'existe pas dans SQLite")
            skipped_tables += 1
            continue

        if table not in pg_tables:
            print(f"  SKIP {table}: n'existe pas dans PostgreSQL (db.create_all() pas encore exécuté?)")
            skipped_tables += 1
            continue

        # Lire les données depuis SQLite
        with sqlite_engine.connect() as src:
            columns = [col['name'] for col in sqlite_inspector.get_columns(table)]
            rows = src.execute(text(f"SELECT * FROM {table}")).fetchall()

        if not rows:
            print(f"  {table}: 0 lignes (vide)")
            continue

        # Vérifier si la table PostgreSQL contient déjà des données
        with pg_engine.connect() as dst:
            count = dst.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            if count > 0:
                print(f"  SKIP {table}: contient déjà {count} lignes dans PostgreSQL")
                skipped_tables += 1
                continue

        # Colonnes disponibles dans PostgreSQL
        pg_col_info = pg_inspector.get_columns(table)
        pg_columns = {col['name'] for col in pg_col_info}
        # Ne garder que les colonnes communes (SQLite peut avoir des colonnes obsolètes)
        common_columns = [c for c in columns if c in pg_columns]

        if not common_columns:
            print(f"  SKIP {table}: aucune colonne commune")
            skipped_tables += 1
            continue

        # Détecter les colonnes BOOLEAN pour la conversion
        boolean_columns = get_boolean_columns(pg_inspector, table)

        # Insérer dans PostgreSQL
        with pg_engine.connect() as dst:
            cols_str = ", ".join(common_columns)
            params_str = ", ".join([f":{c}" for c in common_columns])
            insert_sql = f"INSERT INTO {table} ({cols_str}) VALUES ({params_str})"

            inserted = 0
            errors = 0

            for row in rows:
                row_dict = {}
                for idx, col_name in enumerate(columns):
                    if col_name in pg_columns:
                        row_dict[col_name] = row[idx]

                # Convertir 0/1 → True/False pour les colonnes BOOLEAN
                convert_row(row_dict, boolean_columns)

                try:
                    dst.execute(text(insert_sql), row_dict)
                    dst.commit()
                    inserted += 1
                except Exception as e:
                    dst.rollback()
                    errors += 1
                    if errors <= 3:
                        print(f"    ERREUR ligne {inserted + errors} dans {table}: {e}")
                    elif errors == 4:
                        print(f"    ... (erreurs suivantes masquées)")

            # Reset de la séquence PostgreSQL pour l'auto-increment
            if 'id' in common_columns and inserted > 0:
                try:
                    dst.execute(text(f"""
                        SELECT setval(
                            pg_get_serial_sequence('{table}', 'id'),
                            COALESCE((SELECT MAX(id) FROM {table}), 0) + 1,
                            false
                        )
                    """))
                    dst.commit()
                except Exception as e:
                    print(f"    Note: Pas de séquence à reset pour {table}.id ({e})")

            status = "OK" if errors == 0 else "PARTIEL"
            print(f"  {status} {table}: {inserted}/{len(rows)} lignes migrées" +
                  (f" ({errors} erreurs)" if errors > 0 else ""))
            total_rows += inserted
            if inserted > 0:
                migrated_tables += 1
            if errors > 0:
                failed_tables.append(f"{table} ({errors} erreurs)")

    print()
    print("=" * 60)
    print(f"RÉSUMÉ: {migrated_tables} tables migrées, {total_rows} lignes total, {skipped_tables} tables ignorées")
    if failed_tables:
        print(f"ERREURS: {', '.join(failed_tables)}")
    print("=" * 60)

    # Vérification finale
    print("\nVérification:")
    with pg_engine.connect() as conn:
        for table in ['users', 'project', 'fiche_evaluation', 'documents_projet',
                       'messages_projet', 'notifications', 'formulaire_config']:
            if table in pg_tables:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"  {table}: {count} lignes")


if __name__ == '__main__':
    try:
        migrate()
    except Exception as e:
        print(f"\nERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
