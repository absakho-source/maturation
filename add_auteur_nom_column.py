import sqlite3

# Chemin vers la base de données
DB_PATH = "backend/maturation.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

try:
    # Vérifier si la colonne auteur_nom existe déjà
    c.execute("PRAGMA table_info(project)")
    columns = [column[1] for column in c.fetchall()]

    if 'auteur_nom' not in columns:
        print("Ajout de la colonne 'auteur_nom' à la table 'project'...")
        c.execute("ALTER TABLE project ADD COLUMN auteur_nom VARCHAR(100)")
        conn.commit()
        print("✓ Colonne 'auteur_nom' ajoutée avec succès")
    else:
        print("✓ La colonne 'auteur_nom' existe déjà")

except Exception as e:
    print(f"✗ Erreur lors de l'ajout de la colonne: {e}")
    conn.rollback()
finally:
    conn.close()
