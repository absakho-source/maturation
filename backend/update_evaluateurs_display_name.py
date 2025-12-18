#!/usr/bin/env python3
"""
Script pour mettre à jour les display_name des évaluateurs DGPPE
Format: Prénom avec première lettre majuscule, NOM tout en majuscules
"""

import sqlite3
import os

DATA_DIR = os.environ.get("DATA_DIR", os.path.abspath(os.path.dirname(__file__)))
DB_PATH = os.path.join(DATA_DIR, "maturation.db")

# Mapping des usernames vers les nouveaux display_name formatés
# Format: prénom (première lettre majuscule) + NOM (tout en majuscules)
evaluateurs_mapping = {
    "papa.sy": "Papa Baïdy SY",
    "papa.diouf": "Papa Dethié DIOUF",
    "mamadou.marone": "Mamadou Ibrahima MARONE",
    "syleymane.niang": "Syleymane NIANG",
    "suleymane.haidara": "Suleymane HAÏDARA",
    "mame.toure": "Mame Sané TOURE",
    "ndeye.sarr": "Ndeye Fatou SARR",
    "serigne.diene": "Serigne Djibril DIENE",
    "babacar.sall": "Babacar SALL",
    "khady.ndiaye": "Khady Diop NDIAYE",
    "ousseynou.badiane": "Ousseynou BADIANE",
    "deguene.mbodj": "Deguène MBODJ",
    "aminata.faye": "Aminata FAYE",
    "sokhna.syll": "Sokhna Mar SYLL",
    "richard.tendeng": "Richard TENDENG",
    "fatou.mbow": "Fatou Bamba Bachir MBOW",
    "oumar.diedhiou": "Oumar DIEDHIOU",
    "fatou.ndiaye3": "Fatou NDIAYE",
}

def update_display_names():
    """Met à jour les display_name des évaluateurs"""

    if not os.path.exists(DB_PATH):
        print(f"❌ Base de données non trouvée: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 80)
    print("MISE À JOUR DES NOMS D'AFFICHAGE DES ÉVALUATEURS")
    print("=" * 80)
    print()

    updated = 0
    not_found = 0

    for username, new_display_name in evaluateurs_mapping.items():
        # Vérifier si le compte existe
        cursor.execute("SELECT id, display_name FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()

        if result:
            old_display_name = result[1]
            cursor.execute(
                "UPDATE users SET display_name = ? WHERE username = ?",
                (new_display_name, username)
            )
            print(f"✅ {username}: '{old_display_name}' → '{new_display_name}'")
            updated += 1
        else:
            print(f"⚠️  {username} non trouvé dans la base")
            not_found += 1

    conn.commit()
    conn.close()

    print()
    print("=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    print(f"Comptes mis à jour: {updated}")
    print(f"Comptes non trouvés: {not_found}")
    print()

if __name__ == "__main__":
    update_display_names()
