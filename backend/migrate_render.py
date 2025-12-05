#!/usr/bin/env python3
"""
Script de migration pour la base de données
Exécuté automatiquement au démarrage du backend
"""

import sqlite3
import os


def migrate_database(db_path):
    """
    Exécute toutes les migrations nécessaires sur la base de données
    Retourne True si succès, False sinon
    """
    print(f"[MIGRATION] Connexion à la base de données: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Migration 1: Ajouter la colonne statut_comite à la table projects
        print("[MIGRATION] Vérification de la colonne 'statut_comite'...")
        cursor.execute("PRAGMA table_info(projects)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'statut_comite' not in columns:
            print("[MIGRATION] Ajout de la colonne 'statut_comite'...")
            cursor.execute("""
                ALTER TABLE projects
                ADD COLUMN statut_comite TEXT
            """)
            conn.commit()
            print("[MIGRATION] ✓ Colonne 'statut_comite' ajoutée avec succès")
        else:
            print("[MIGRATION] ✓ La colonne 'statut_comite' existe déjà")

        # Afficher quelques statistiques
        cursor.execute("SELECT COUNT(*) FROM projects")
        total_projects = cursor.fetchone()[0]
        print(f"[MIGRATION] Nombre total de projets: {total_projects}")

        cursor.execute("SELECT COUNT(*) FROM projects WHERE statut_comite IS NOT NULL")
        projects_with_status = cursor.fetchone()[0]
        print(f"[MIGRATION] Projets avec statut_comite défini: {projects_with_status}")

        # Ajouter d'autres migrations ici au besoin
        # Migration 2: ...
        # Migration 3: ...

        conn.close()
        print("[MIGRATION] ✓ Toutes les migrations ont été appliquées avec succès!")
        return True

    except Exception as e:
        print(f"[MIGRATION] ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Permet d'exécuter le script directement pour tester
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else "maturation.db"
    success = migrate_database(db_path)
    exit(0 if success else 1)
