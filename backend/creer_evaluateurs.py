#!/usr/bin/env python3
"""
Script pour créer les comptes évaluateurs DGPPE
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

# Utiliser le même chemin que app.py
DATA_DIR = os.environ.get("DATA_DIR", os.path.abspath(os.path.dirname(__file__)))
DB_PATH = os.path.join(DATA_DIR, "maturation.db")

# Liste des évaluateurs à créer
evaluateurs = [
    {"prenom": "PAPA BAÏDY", "nom": "SY"},
    {"prenom": "PAPA DETHIÉ", "nom": "DIOUF"},
    {"prenom": "MAMADOU IBRAHIMA", "nom": "MARONE"},
    {"prenom": "SYLEYMANE", "nom": "NIANG"},
    {"prenom": "SULEYMANE", "nom": "HAÏDARA"},
    {"prenom": "MAME SANÉ", "nom": "TOURE"},
    {"prenom": "NDEYE FATOU", "nom": "SARR"},
    {"prenom": "SERIGNE DJIBRIL", "nom": "DIENE"},
    {"prenom": "BABACAR", "nom": "SALL"},
    {"prenom": "KHADY DIOP", "nom": "NDIAYE"},
    {"prenom": "OUSSEYNOU", "nom": "BADIANE"},
    {"prenom": "DEGUÈNE", "nom": "MBODJ"},
    {"prenom": "AMINATA", "nom": "FAYE"},
    {"prenom": "SOKHNA MAR", "nom": "SYLL"},
    {"prenom": "RICHARD", "nom": "TENDENG"},
    {"prenom": "FATOU BAMBA BACHIR", "nom": "MBOW"},
    {"prenom": "OUMAR", "nom": "DIEDHIOU"},
    {"prenom": "FATOU", "nom": "NDIAYE3"},
]

def generer_username(prenom, nom):
    """Génère un username à partir du prénom et nom"""
    # Prendre le premier prénom et le nom
    premier_prenom = prenom.split()[0].lower()
    nom_lower = nom.lower()

    # Supprimer les accents et caractères spéciaux
    import unicodedata
    premier_prenom = ''.join(c for c in unicodedata.normalize('NFD', premier_prenom) if unicodedata.category(c) != 'Mn')
    nom_lower = ''.join(c for c in unicodedata.normalize('NFD', nom_lower) if unicodedata.category(c) != 'Mn')

    # Remplacer les caractères spéciaux
    premier_prenom = premier_prenom.replace('ï', 'i').replace('é', 'e').replace('è', 'e')
    nom_lower = nom_lower.replace('ï', 'i').replace('é', 'e').replace('è', 'e')

    return f"{premier_prenom}.{nom_lower}"

def generer_email(prenom, nom):
    """Génère un email à partir du prénom et nom"""
    username = generer_username(prenom, nom)
    return f"{username}@dgppe.gouv.sn"

def creer_evaluateurs():
    """Crée les comptes évaluateurs dans la base de données"""

    if not os.path.exists(DB_PATH):
        print(f"❌ Base de données non trouvée: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 80)
    print("CRÉATION DES COMPTES ÉVALUATEURS")
    print("=" * 80)
    print()

    # Mot de passe par défaut
    default_password = "Dgppe@2025"
    password_hash = generate_password_hash(default_password)

    comptes_crees = []
    comptes_existants = []

    for eval_data in evaluateurs:
        prenom = eval_data["prenom"]
        nom = eval_data["nom"]

        username = generer_username(prenom, nom)
        email = generer_email(prenom, nom)
        display_name = f"{prenom} {nom}"

        # Vérifier si le compte existe déjà
        cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
        existing = cursor.fetchone()

        if existing:
            comptes_existants.append(username)
            print(f"⚠️  {username} existe déjà")
            continue

        # Créer le compte
        try:
            cursor.execute("""
                INSERT INTO user (username, email, password, role, display_name, statut_compte)
                VALUES (?, ?, ?, 'evaluateur', ?, 'verifie')
            """, (username, email, password_hash, display_name))

            comptes_crees.append({
                "username": username,
                "email": email,
                "display_name": display_name,
                "password": default_password
            })
            print(f"✅ Créé: {username} ({display_name})")

        except Exception as e:
            print(f"❌ Erreur pour {username}: {e}")

    conn.commit()
    conn.close()

    print()
    print("=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    print(f"Comptes créés: {len(comptes_crees)}")
    print(f"Comptes existants: {len(comptes_existants)}")
    print()

    if comptes_crees:
        print("LISTE DES COMPTES CRÉÉS:")
        print("-" * 80)
        print(f"{'USERNAME':<25} {'EMAIL':<35} {'NOM COMPLET':<30}")
        print("-" * 80)
        for compte in comptes_crees:
            print(f"{compte['username']:<25} {compte['email']:<35} {compte['display_name']:<30}")
        print("-" * 80)
        print(f"\n🔑 Mot de passe par défaut: {default_password}")
        print()

if __name__ == "__main__":
    creer_evaluateurs()
