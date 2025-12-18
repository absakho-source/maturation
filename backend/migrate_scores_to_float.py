#!/usr/bin/env python3
"""
Script de migration pour convertir les colonnes de scores de INTEGER à FLOAT
pour permettre les notes décimales (ex: 3.5, 7.5)
"""

import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), "maturation.db")

def migrate_scores_to_float():
    """
    Migre les colonnes de scores de INTEGER à FLOAT dans fiche_evaluation
    SQLite ne supporte pas ALTER COLUMN, donc on doit recréer la table
    """

    if not os.path.exists(DB_PATH):
        print(f"❌ Base de données non trouvée: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 80)
    print("MIGRATION: Conversion des scores INTEGER → FLOAT")
    print("=" * 80)
    print()

    try:
        # 1. Vérifier que la table existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fiche_evaluation'")
        if not cursor.fetchone():
            print("⚠️  Table fiche_evaluation non trouvée - migration non nécessaire")
            return

        print("✓ Table fiche_evaluation trouvée")

        # 2. Récupérer le schéma complet de l'ancienne table
        print("\n1️⃣  Analyse du schéma existant...")

        cursor.execute("PRAGMA table_info(fiche_evaluation)")
        old_columns_info = cursor.fetchall()

        # Créer le schéma de la nouvelle table en remplaçant INTEGER par FLOAT pour les scores
        new_schema = []
        for col in old_columns_info:
            col_id, col_name, col_type, not_null, default_val, pk = col

            # Remplacer INTEGER par FLOAT pour les colonnes de score
            if "_score" in col_name or col_name == "score_total":
                col_type = "FLOAT"

            # Construire la définition de colonne
            col_def = f"{col_name} {col_type}"

            if pk:
                col_def += " PRIMARY KEY AUTOINCREMENT"
            elif not_null:
                col_def += " NOT NULL"

            if default_val is not None:
                col_def += f" DEFAULT {default_val}"

            new_schema.append(col_def)

        # Ajouter la foreign key si elle existe
        cursor.execute("PRAGMA foreign_key_list(fiche_evaluation)")
        fk_list = cursor.fetchall()
        if fk_list:
            for fk in fk_list:
                new_schema.append(f"FOREIGN KEY ({fk[3]}) REFERENCES {fk[2]} ({fk[4]})")

        schema_sql = ",\n                ".join(new_schema)

        print(f"   ✓ {len(old_columns_info)} colonnes analysées")

        # 3. Créer la table temporaire
        print("\n2️⃣  Création de la table temporaire avec scores FLOAT...")

        cursor.execute(f"""
            CREATE TABLE fiche_evaluation_new (
                {schema_sql}
            )
        """)
        print("   ✓ Table temporaire créée")

        # 4. Copier toutes les données
        print("\n3️⃣  Copie des données existantes...")

        old_columns = [col[1] for col in old_columns_info]
        columns_str = ", ".join(old_columns)

        cursor.execute(f"""
            INSERT INTO fiche_evaluation_new ({columns_str})
            SELECT {columns_str}
            FROM fiche_evaluation
        """)

        rows_copied = cursor.rowcount
        print(f"   ✓ {rows_copied} ligne(s) copiée(s)")

        # 5. Supprimer l'ancienne table
        print("\n4️⃣  Suppression de l'ancienne table...")
        cursor.execute("DROP TABLE fiche_evaluation")
        print("   ✓ Ancienne table supprimée")

        # 6. Renommer la nouvelle table
        print("\n5️⃣  Renommage de la nouvelle table...")
        cursor.execute("ALTER TABLE fiche_evaluation_new RENAME TO fiche_evaluation")
        print("   ✓ Table renommée")

        # 6. Commit des changements
        conn.commit()

        print()
        print("=" * 80)
        print("✅ MIGRATION RÉUSSIE!")
        print("=" * 80)
        print()
        print("Les colonnes de scores supportent maintenant les décimales:")
        print("  • Scores individuels: INTEGER → FLOAT")
        print("  • Score total: INTEGER → FLOAT")
        print()
        print("Exemples de scores valides:")
        print("  • 3.5 / 10")
        print("  • 7.5 / 15")
        print("  • 82.5 / 100 (total)")
        print()

    except Exception as e:
        conn.rollback()
        print()
        print("=" * 80)
        print("❌ ERREUR LORS DE LA MIGRATION")
        print("=" * 80)
        print(f"\n{e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        conn.close()

if __name__ == "__main__":
    migrate_scores_to_float()
