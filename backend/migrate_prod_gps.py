#!/usr/bin/env python3
"""
Migration production : Ajouter les colonnes GPS à connexion_log

Ajoute les colonnes pour la géolocalisation hybride GPS/IP :
- latitude : Float
- longitude : Float
- source_geoloc : String(20) - 'gps', 'ip', ou 'fallback'
- precision_geoloc : Integer - Précision en mètres (pour GPS)
"""

import sqlite3
import os
import sys

# Chemin de la base de données
db_path = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "maturation.db"))
print(f"[MIGRATION] Utilisation de la base de données: {db_path}")

# Vérifier que la base existe
if not os.path.exists(db_path):
    print(f"❌ ERREUR: Base de données introuvable: {db_path}")
    sys.exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Vérifier si les colonnes existent déjà
    cursor.execute("PRAGMA table_info(connexion_log)")
    columns = [row[1] for row in cursor.fetchall()]

    columns_to_add = []

    if 'latitude' not in columns:
        columns_to_add.append(('latitude', 'REAL'))

    if 'longitude' not in columns:
        columns_to_add.append(('longitude', 'REAL'))

    if 'source_geoloc' not in columns:
        columns_to_add.append(('source_geoloc', 'VARCHAR(20)'))

    if 'precision_geoloc' not in columns:
        columns_to_add.append(('precision_geoloc', 'INTEGER'))

    if columns_to_add:
        print(f"[MIGRATION] Ajout de {len(columns_to_add)} colonnes...")

        for col_name, col_type in columns_to_add:
            sql = f"ALTER TABLE connexion_log ADD COLUMN {col_name} {col_type}"
            print(f"[MIGRATION] Exécution: {sql}")
            cursor.execute(sql)
            print(f"✅ Colonne '{col_name}' ajoutée avec succès")

        conn.commit()
        print(f"\n✅ Migration terminée avec succès ! {len(columns_to_add)} colonnes ajoutées.")
    else:
        print("✅ Toutes les colonnes existent déjà. Aucune migration nécessaire.")

except Exception as e:
    print(f"❌ Erreur lors de la migration: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

finally:
    if conn:
        conn.close()
        print("[MIGRATION] Connexion fermée.")
