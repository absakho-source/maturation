#!/usr/bin/env python3
"""
Script de migration pour ajouter les champs Impact Emploi à la table fiche_evaluation
"""
import sqlite3
import sys
import os
from datetime import datetime

# Chemin vers la base de données
DB_PATH = "/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/backend/maturation.db"

def migrate_database():
    """Ajoute les champs impact_emploi à la table fiche_evaluation"""
    try:
        # Backup de la base
        backup_name = f"maturation.db.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(os.path.dirname(DB_PATH), backup_name)
        
        # Copier la base pour backup
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Backup créé: {backup_name}")
        
        # Connexion à la base
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Vérifier si les colonnes existent déjà
        cursor.execute("PRAGMA table_info(fiche_evaluation)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        # Ajouter les nouvelles colonnes si elles n'existent pas
        new_columns = [
            ("impact_emploi_score", "INTEGER DEFAULT 0"),
            ("impact_emploi_recommandations", "TEXT")
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                query = f"ALTER TABLE fiche_evaluation ADD COLUMN {column_name} {column_type}"
                cursor.execute(query)
                print(f"✅ Colonne ajoutée: {column_name}")
            else:
                print(f"ℹ️  Colonne existe déjà: {column_name}")
        
        # Commit et fermeture
        conn.commit()
        conn.close()
        
        print("✅ Migration terminée avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Début de la migration pour les champs Impact Emploi...")
    success = migrate_database()
    if success:
        print("🎉 Migration réussie!")
        sys.exit(0)
    else:
        print("💥 Migration échouée!")
        sys.exit(1)