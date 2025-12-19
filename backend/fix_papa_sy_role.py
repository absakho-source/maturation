#!/usr/bin/env python3
"""
Script pour corriger le rôle de papa.sy (Papa Baïdy SY)
qui est actuellement 'secretariatsct' mais devrait être 'evaluateur'
"""

import sqlite3
import os

DATA_DIR = os.environ.get("DATA_DIR", os.path.abspath(os.path.dirname(__file__)))
DB_PATH = os.path.join(DATA_DIR, "maturation.db")

def fix_role():
    """Corrige le rôle de papa.sy"""

    if not os.path.exists(DB_PATH):
        print(f"❌ Base de données non trouvée: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Vérifier l'état actuel
    cursor.execute("SELECT id, username, display_name, role FROM users WHERE username = 'papa.sy'")
    result = cursor.fetchone()

    if not result:
        print("❌ Compte papa.sy non trouvé")
        conn.close()
        return

    user_id, username, display_name, current_role = result
    print(f"Compte trouvé: ID={user_id}, username={username}, display_name={display_name}")
    print(f"Rôle actuel: {current_role}")

    if current_role == "evaluateur":
        print("✅ Le rôle est déjà correct (evaluateur)")
        conn.close()
        return

    # Corriger le rôle
    cursor.execute("UPDATE users SET role = 'evaluateur' WHERE username = 'papa.sy'")
    conn.commit()

    # Vérifier la correction
    cursor.execute("SELECT role FROM users WHERE username = 'papa.sy'")
    new_role = cursor.fetchone()[0]

    print(f"✅ Rôle corrigé: {current_role} → {new_role}")

    conn.close()

if __name__ == "__main__":
    fix_role()
