import sqlite3

# Chemin vers la base de données
DB_PATH = "backend/maturation.db"

# Liste des colonnes à ajouter
COLUMNS_TO_ADD = [
    ("validation_secretariat", "VARCHAR(100)"),
    ("commentaires_finaux", "TEXT"),
    ("complements_demande_message", "TEXT"),
    ("complements_reponse_message", "TEXT"),
    ("complements_reponse_pieces", "TEXT")
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

try:
    # Vérifier les colonnes existantes
    c.execute("PRAGMA table_info(project)")
    existing_columns = [column[1] for column in c.fetchall()]

    print(f"Colonnes existantes : {existing_columns}")

    # Ajouter les colonnes manquantes
    for column_name, column_type in COLUMNS_TO_ADD:
        if column_name not in existing_columns:
            print(f"Ajout de la colonne '{column_name}'...")
            c.execute(f"ALTER TABLE project ADD COLUMN {column_name} {column_type}")
            conn.commit()
            print(f"✓ Colonne '{column_name}' ajoutée avec succès")
        else:
            print(f"✓ La colonne '{column_name}' existe déjà")

    print("\n✓ Migration terminée avec succès")

except Exception as e:
    print(f"✗ Erreur lors de la migration: {e}")
    conn.rollback()
finally:
    conn.close()
