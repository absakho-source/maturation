#!/usr/bin/env python3
"""
Migration : Ajouter la colonne must_change_password à la table users

Cette colonne indique si l'utilisateur doit changer son mot de passe
à la première connexion (pour les comptes créés par l'admin).
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

    # Vérifier si la colonne existe déjà
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'must_change_password' not in columns:
        print("[MIGRATION] Ajout de la colonne must_change_password...")

        sql = "ALTER TABLE users ADD COLUMN must_change_password BOOLEAN DEFAULT 0"
        print(f"[MIGRATION] Exécution: {sql}")
        cursor.execute(sql)

        conn.commit()
        print("✅ Colonne 'must_change_password' ajoutée avec succès !")
    else:
        print("✅ La colonne 'must_change_password' existe déjà. Aucune migration nécessaire.")

except Exception as e:
    print(f"❌ Erreur lors de la migration: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

finally:
    if conn:
        conn.close()
        print("[MIGRATION] Connexion fermée.")
