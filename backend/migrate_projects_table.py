import sqlite3

# Chemin vers la base
DB_PATH = "backend/maturation.db"

# Colonnes à transférer (adapter si besoin)
PROJECTS_COLUMNS = [
    "id", "numero_projet", "titre", "description", "secteur", "poles", "cout_estimatif", "auteur_nom", "statut", "evaluateur_nom", "avis", "commentaires", "date_soumission"
]
PROJECT_COLUMNS = [
    "id", "numero_projet", "titre", "description", "secteur", "poles", "cout_estimatif", "statut", "evaluateur_nom", "avis", "commentaires", "date_soumission"
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Lire tous les projets de la table legacy
c.execute(f"SELECT {', '.join(PROJECTS_COLUMNS)} FROM projects")
rows = c.fetchall()

# Insérer dans la nouvelle table (en ignorant les colonnes non présentes)
for row in rows:
    # On retire 'auteur_nom' qui n'existe plus
    row_dict = dict(zip(PROJECTS_COLUMNS, row))
    values = [row_dict.get(col) for col in PROJECT_COLUMNS]
    placeholders = ','.join(['?'] * len(PROJECT_COLUMNS))
    c.execute(f"INSERT OR IGNORE INTO project ({', '.join(PROJECT_COLUMNS)}) VALUES ({placeholders})", values)

conn.commit()
print(f"{len(rows)} projets migrés de 'projects' vers 'project'.")
conn.close()
