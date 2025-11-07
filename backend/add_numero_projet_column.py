#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migration pour ajouter la colonne numero_projet à la table projects
"""

import sqlite3
import os
from config import Config

def main():
    # Chemin vers la base de données
    db_path = "maturation.db"  # Base de données dans le dossier backend
    print(f"Migration de la base de données : {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ Erreur : La base de données {db_path} n'existe pas.")
        return
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(projects)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'numero_projet' in columns:
            print("✅ La colonne 'numero_projet' existe déjà dans la table 'projects'.")
        else:
            print("🔄 Ajout de la colonne 'numero_projet' à la table 'projects'...")
            
            # Ajouter la colonne numero_projet (sans contrainte UNIQUE pour l'instant)
            cursor.execute("ALTER TABLE projects ADD COLUMN numero_projet VARCHAR(8)")
            
            # Valider les changements
            conn.commit()
            print("✅ Colonne 'numero_projet' ajoutée avec succès!")
        
        # Fermer la connexion
        conn.close()
        
        print("✅ Migration terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration : {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    main()