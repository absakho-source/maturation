#!/usr/bin/env python3
"""
Script pour mettre à jour les emails des utilisateurs
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
    # Afficher tous les utilisateurs sans email
    cursor.execute("""
        SELECT id, username, role, nom_complet, display_name
        FROM users
        WHERE email IS NULL OR email = ''
        ORDER BY role, username
    """)

    users_without_email = cursor.fetchall()

    if not users_without_email:
        print("\n✅ Tous les utilisateurs ont déjà une adresse email!")
        sys.exit(0)

    print(f"\n📋 Utilisateurs sans email ({len(users_without_email)}):\n")
    print(f"{'ID':<5} {'Username':<20} {'Rôle':<20} {'Nom':<30}")
    print("-" * 80)

    for user in users_without_email:
        user_id, username, role, nom_complet, display_name = user
        nom = nom_complet or display_name or "(pas de nom)"
        print(f"{user_id:<5} {username:<20} {role or 'N/A':<20} {nom:<30}")

    print("\n" + "="*80)
    print("MISE À JOUR DES EMAILS")
    print("="*80)

    # Mode interactif ou par arguments
    if len(sys.argv) > 1:
        # Mode par arguments: python update_user_emails.py username email@example.com
        if len(sys.argv) != 3:
            print("\nUsage: python update_user_emails.py <username> <email>")
            print("   ou: python update_user_emails.py (mode interactif)")
            sys.exit(1)

        username = sys.argv[1]
        email = sys.argv[2]

        cursor.execute("UPDATE users SET email = ? WHERE username = ?", (email, username))

        if cursor.rowcount > 0:
            conn.commit()
            print(f"\n✅ Email mis à jour pour {username}: {email}")
        else:
            print(f"\n❌ Utilisateur '{username}' non trouvé")
            sys.exit(1)
    else:
        # Mode interactif
        print("\nMode interactif: Entrez les emails pour chaque utilisateur")
        print("(Appuyez sur Entrée pour ignorer un utilisateur)\n")

        updates = []

        for user in users_without_email:
            user_id, username, role, nom_complet, display_name = user
            nom = nom_complet or display_name or ""

            print(f"\n📧 {username} ({role}) - {nom}")
            email = input(f"   Email: ").strip()

            if email:
                # Validation basique de l'email
                if '@' not in email or '.' not in email.split('@')[1]:
                    print(f"   ⚠️  Email invalide, ignoré")
                    continue

                updates.append((email, username))
                print(f"   ✓ Email enregistré: {email}")

        if updates:
            print(f"\n{'='*80}")
            print(f"CONFIRMATION - {len(updates)} emails à mettre à jour:")
            for email, username in updates:
                print(f"  • {username} → {email}")

            confirm = input("\nConfirmer les mises à jour ? (oui/non): ").strip().lower()

            if confirm in ['oui', 'o', 'yes', 'y']:
                for email, username in updates:
                    cursor.execute("UPDATE users SET email = ? WHERE username = ?", (email, username))

                conn.commit()
                print(f"\n✅ {len(updates)} emails mis à jour avec succès!")
            else:
                print("\n❌ Opération annulée")
        else:
            print("\n⚠️  Aucun email à mettre à jour")

    # Afficher les statistiques finales
    cursor.execute("SELECT COUNT(*) FROM users WHERE email IS NOT NULL AND email != ''")
    users_with_email = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    print(f"\n📊 Statistiques finales:")
    print(f"  - Utilisateurs avec email: {users_with_email}/{total_users}")
    print(f"  - Utilisateurs sans email: {total_users - users_with_email}/{total_users}")

except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
    sys.exit(1)
finally:
    conn.close()
