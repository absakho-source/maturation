#!/usr/bin/env python3
"""
Migration Flask-native pour ajouter la colonne statut_comite
Utilise directement la connexion db de Flask pour éviter les conflits
"""

def migrate_with_flask_db(db):
    """
    Exécute la migration en utilisant la connexion db de Flask
    Retourne True si succès, False sinon
    """
    print("[MIGRATION FLASK] Début de la migration...")

    try:
        from sqlalchemy import text

        # Utiliser la connexion existante de Flask
        with db.engine.connect() as conn:
            # Vérifier si la colonne existe déjà
            result = conn.execute(text("PRAGMA table_info(project)"))
            columns = [row[1] for row in result]

            if 'statut_comite' in columns:
                print("[MIGRATION FLASK] ✓ La colonne 'statut_comite' existe déjà")
                return True

            # Ajouter la colonne
            print("[MIGRATION FLASK] Ajout de la colonne 'statut_comite'...")
            conn.execute(text("""
                ALTER TABLE project
                ADD COLUMN statut_comite VARCHAR(50)
            """))
            conn.commit()

            print("[MIGRATION FLASK] ✓ Colonne 'statut_comite' ajoutée avec succès!")

            # Statistiques
            result = conn.execute(text("SELECT COUNT(*) FROM project"))
            total = result.scalar()
            print(f"[MIGRATION FLASK] Nombre total de projets: {total}")

            return True

    except Exception as e:
        print(f"[MIGRATION FLASK] ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
