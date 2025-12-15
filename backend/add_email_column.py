#!/usr/bin/env python3
"""
Migration: Ajouter la colonne 'email' à la table users si elle n'existe pas
"""
import sqlite3
import os
import sys

# Déterminer le chemin de la base de données
DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(DATA_DIR, 'maturation.db')

print(f"📂 Base de données: {DB_PATH}")

if not os.path.exists(DB_PATH):
    print(f"❌ Erreur: La base de données n'existe pas à {DB_PATH}")
    sys.exit(1)

# Connexion à la base
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Vérifier si la colonne 'email' existe
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]

    print(f"\n📋 Colonnes actuelles dans 'users':")
    for col in columns:
        print(f"  - {col}")

    if 'email' in columns:
        print(f"\n✅ La colonne 'email' existe déjà dans la table 'users'")
    else:
        print(f"\n⚠️  La colonne 'email' N'EXISTE PAS dans la table 'users'")
        print(f"🔧 Ajout de la colonne 'email'...")

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN email TEXT
        """)

        conn.commit()
        print(f"✅ Colonne 'email' ajoutée avec succès!")

        # Vérification
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'email' in columns:
            print(f"✅ Vérification: La colonne 'email' est maintenant présente")
        else:
            print(f"❌ Erreur: La colonne 'email' n'a pas été ajoutée correctement")
            sys.exit(1)

    # Afficher quelques statistiques
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE email IS NOT NULL AND email != ''")
    users_with_email = cursor.fetchone()[0]

    print(f"\n📊 Statistiques:")
    print(f"  - Nombre total d'utilisateurs: {total_users}")
    print(f"  - Utilisateurs avec email: {users_with_email}")
    print(f"  - Utilisateurs sans email: {total_users - users_with_email}")

    if users_with_email < total_users:
        print(f"\n⚠️  ATTENTION: {total_users - users_with_email} utilisateurs n'ont pas d'email")
        print(f"   Les notifications email ne pourront pas leur être envoyées")
        print(f"   Il faudra ajouter les emails manuellement via l'interface d'administration")

except Exception as e:
    print(f"\n❌ Erreur lors de la migration: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
    sys.exit(1)
finally:
    conn.close()

print(f"\n✅ Migration terminée avec succès!")
