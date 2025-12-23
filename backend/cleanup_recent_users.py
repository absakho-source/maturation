#!/usr/bin/env python3
"""
Script pour supprimer les comptes récents et transférer leurs projets à 'soumissionnaire'
"""
import sqlite3
import sys
from datetime import datetime

# Liste des comptes à supprimer
ACCOUNTS_TO_DELETE = [
    'papa.sy',
    'papa.diouf',
    'mamadou.marone',
    'syleymane.niang',
    'suleymane.haidara',
    'mame.toure',
    'ndeye.sarr',
    'serigne.diene',
    'babacar.sall',
    'khady.ndiaye',
    'ousseynou.badiane',
    'deguene.mbodj',
    'aminata.faye',
    'sokhna.syll',
    'richard.tendeng',
    'fatou.mbow',
    'oumar.diedhiou',
    'fatou.ndiaye3',
    'abdou.sene',
    'moustaphadiamil.sy'
]

def cleanup_users(db_path='maturation.db'):
    """Supprime les comptes et transfère leurs projets"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print(f"🔍 Connexion à la base de données: {db_path}")

        # 1. Vérifier combien de projets appartiennent à ces comptes
        placeholders = ','.join(['?' for _ in ACCOUNTS_TO_DELETE])
        cursor.execute(f"""
            SELECT auteur_nom, COUNT(*)
            FROM project
            WHERE auteur_nom IN ({placeholders})
            GROUP BY auteur_nom
        """, ACCOUNTS_TO_DELETE)

        projects_by_user = cursor.fetchall()
        total_projects = sum(count for _, count in projects_by_user)

        print(f"\n📊 Projets à transférer: {total_projects}")
        for user, count in projects_by_user:
            print(f"   - {user}: {count} projet(s)")

        if total_projects == 0:
            print("\n✅ Aucun projet à transférer")
        else:
            # 2. Transférer tous les projets à 'soumissionnaire'
            print(f"\n📦 Transfert de {total_projects} projet(s) vers 'soumissionnaire'...")
            cursor.execute(f"""
                UPDATE project
                SET auteur_nom = 'soumissionnaire'
                WHERE auteur_nom IN ({placeholders})
            """, ACCOUNTS_TO_DELETE)

            affected = cursor.rowcount
            print(f"✅ {affected} projet(s) transféré(s)")

        # 3. Supprimer les comptes utilisateurs
        print(f"\n🗑️  Suppression de {len(ACCOUNTS_TO_DELETE)} compte(s)...")
        cursor.execute(f"""
            DELETE FROM users
            WHERE username IN ({placeholders})
        """, ACCOUNTS_TO_DELETE)

        deleted = cursor.rowcount
        print(f"✅ {deleted} compte(s) supprimé(s)")

        # 4. Commit
        conn.commit()
        print("\n✅ Opération réussie ! Tous les changements ont été enregistrés.")

        # 5. Vérification finale
        cursor.execute("SELECT COUNT(*) FROM project WHERE auteur_nom = 'soumissionnaire'")
        total_soumissionnaire = cursor.fetchone()[0]
        print(f"\n📊 Total des projets pour 'soumissionnaire': {total_soumissionnaire}")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'maturation.db'

    print("=" * 70)
    print("🧹 NETTOYAGE DES COMPTES RÉCENTS")
    print("=" * 70)
    print(f"\n📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n⚠️  Cette opération va:")
    print(f"   1. Transférer tous les projets de {len(ACCOUNTS_TO_DELETE)} comptes vers 'soumissionnaire'")
    print(f"   2. Supprimer ces {len(ACCOUNTS_TO_DELETE)} comptes")

    response = input("\n❓ Voulez-vous continuer ? (oui/non): ").strip().lower()
    if response not in ['oui', 'o', 'yes', 'y']:
        print("\n❌ Opération annulée")
        sys.exit(0)

    cleanup_users(db_path)
    print("\n" + "=" * 70)
