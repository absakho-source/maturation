#!/usr/bin/env python3
"""
Script à exécuter dans le Render Shell pour vérifier les templates
Usage: python3 check_templates_render.py
"""

import os
import sys

print("=" * 60)
print("VÉRIFICATION DES TEMPLATES EN PRODUCTION")
print("=" * 60)
print()

# Vérifier le chemin de la base de données
db_path = os.environ.get('DATABASE_PATH', '/data/maturation.db')
print(f"📂 Chemin de la base de données: {db_path}")
print(f"📊 Base de données existe: {os.path.exists(db_path)}")
print()

# Vérifier avec SQLite directement
try:
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Compter les templates
    cursor.execute("SELECT COUNT(*) FROM email_templates")
    count = cursor.fetchone()[0]
    print(f"📧 Nombre de templates dans la base: {count}")
    print()

    if count > 0:
        # Lister les templates
        cursor.execute("SELECT id, template_key, sujet, actif FROM email_templates")
        templates = cursor.fetchall()

        print("📋 Liste des templates:")
        print("-" * 60)
        for template in templates:
            print(f"  ID: {template[0]}, Key: {template[1]}, Sujet: {template[2]}, Actif: {template[3]}")
        print()

    conn.close()

except Exception as e:
    print(f"❌ Erreur SQLite: {e}")
    print()

# Vérifier avec l'ORM Flask
print("🔍 Vérification avec Flask ORM...")
try:
    # Charger l'app Flask
    sys.path.insert(0, os.path.dirname(__file__))

    # Configuration minimale
    os.environ['FORCE_INIT'] = 'false'  # Ne pas réinitialiser

    from app import app, db, EmailTemplate

    with app.app_context():
        # Compter avec l'ORM
        count = EmailTemplate.query.count()
        print(f"📧 Nombre de templates via ORM: {count}")

        if count > 0:
            # Lister les templates
            templates = EmailTemplate.query.all()
            print()
            print("📋 Templates via ORM:")
            print("-" * 60)
            for template in templates:
                print(f"  ID: {template.id}, Key: {template.template_key}")
                print(f"     Sujet: {template.sujet}")
                print(f"     Actif: {template.actif}")
                print()
        else:
            print()
            print("⚠️  Aucun template trouvé via ORM!")
            print("   Réinitialisation des templates...")

            # Importer et exécuter l'initialisation
            import init_email_templates

            # Vérifier à nouveau
            count = EmailTemplate.query.count()
            print(f"✅ Templates après initialisation: {count}")

except Exception as e:
    print(f"❌ Erreur Flask: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("✅ VÉRIFICATION TERMINÉE")
print("=" * 60)
print()
print("Si les templates existent dans SQLite mais pas dans l'ORM,")
print("le backend doit être redémarré pour recharger la base de données.")
