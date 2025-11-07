import sqlite3

# Chemin vers la base de données
DB_PATH = "backend/maturation.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

try:
    # Mettre à jour tous les projets qui n'ont pas d'auteur_nom
    # en leur attribuant 'soumissionnaire' (le seul compte soumissionnaire)
    c.execute("""
        UPDATE project
        SET auteur_nom = 'soumissionnaire'
        WHERE auteur_nom IS NULL OR auteur_nom = ''
    """)

    nb_updated = c.rowcount
    conn.commit()

    print(f"✓ {nb_updated} projets mis à jour avec auteur_nom='soumissionnaire'")

    # Vérifier les résultats
    c.execute("SELECT id, numero_projet, titre, auteur_nom FROM project")
    projets = c.fetchall()

    print("\nListe des projets après mise à jour:")
    for p in projets:
        print(f"  - ID={p[0]}, N°{p[1]}, {p[2]}, auteur={p[3]}")

except Exception as e:
    print(f"✗ Erreur: {e}")
    conn.rollback()
finally:
    conn.close()
