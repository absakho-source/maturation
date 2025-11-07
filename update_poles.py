#!/usr/bin/env python3
"""
Script pour mettre à jour les pôles territoriaux dans la base de données
selon la nouvelle répartition géographique
"""

import sqlite3
import sys
import os

# Ajouter le chemin du backend
sys.path.insert(0, '/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/backend')

# Nouvelle mapping des régions aux pôles (corrigée)
nouveau_mapping = {
    'Dakar': ['DAKAR'],
    'Thiès': ['THIES'],
    'Centre': ['FATICK', 'KAOLACK', 'KAFFRINE'],      # Sans Diourbel
    'Diourbel-Louga': ['DIOURBEL', 'LOUGA'],          # Avec Diourbel maintenant
    'Sud': ['ZIGUINCHOR', 'SEDHIOU', 'KOLDA'],
    'Sud-Est': ['KEDOUGOU', 'TAMBACOUNDA'],
    'Nord': ['SAINT-LOUIS'],
    'Nord-Est': ['MATAM']
}

# Créer le mapping inverse région -> pôle
region_to_pole = {}
for pole, regions in nouveau_mapping.items():
    for region in regions:
        region_to_pole[region.upper()] = pole

def update_poles():
    """Met à jour les pôles territoriaux dans la base de données"""
    
    db_path = '/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/backend/maturation.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Voir les pôles actuels
        cursor.execute("SELECT DISTINCT poles, COUNT(*) FROM projects WHERE poles IS NOT NULL GROUP BY poles")
        poles_actuels = cursor.fetchall()
        
        print("🗺️ PÔLES ACTUELS DANS LA BASE:")
        for pole, count in poles_actuels:
            print(f"  📍 {pole}: {count} projets")
        
        print("\n🔄 MISE À JOUR SELON LA NOUVELLE RÉPARTITION:")
        print("  Centre: Fatick, Kaolack, Kaffrine (sans Diourbel)")
        print("  Diourbel-Louga: Diourbel, Louga (avec Diourbel maintenant)")
        
        # 2. Mettre à jour les labels des pôles selon la nouvelle répartition
        updates = [
            # Nom simplifié pour Centre (sans mention de Diourbel)
            ("Centre", "Centre (Kaolack, Fatick, Kaffrine)"),
            
            # Nom mis à jour pour Diourbel-Louga (avec Diourbel maintenant)
            ("Diourbel-Louga", "Diourbel-Louga"),
            
            # Les autres restent identiques mais on peut simplifier
            ("Dakar", "Dakar"),
            ("Thiès", "Thiès"),  
            ("Sud", "Sud (Ziguinchor, Sédhiou, Kolda)"),
            ("Sud-Est", "Sud-Est (Tambacounda, Kédougou)"),
            ("Nord", "Nord (Saint-Louis)"),
            ("Nord-Est", "Nord-Est (Matam)")
        ]
        
        # Applique les mises à jour
        for nouveau_nom, ancien_pattern in updates:
            cursor.execute("UPDATE projects SET poles = ? WHERE poles LIKE ?", (nouveau_nom, f"%{ancien_pattern.split('(')[0].strip()}%"))
            affected = cursor.rowcount
            if affected > 0:
                print(f"  ✅ Mis à jour {affected} projets: '{ancien_pattern}' → '{nouveau_nom}'")
        
        # 3. Vérifier le résultat
        cursor.execute("SELECT DISTINCT poles, COUNT(*) FROM projects WHERE poles IS NOT NULL GROUP BY poles")
        poles_nouveaux = cursor.fetchall()
        
        print("\n📊 PÔLES APRÈS MISE À JOUR:")
        for pole, count in poles_nouveaux:
            print(f"  📍 {pole}: {count} projets")
        
        # 4. Vérifier la cohérence avec le nouveau mapping
        print("\n🎯 VÉRIFICATION DE LA COHÉRENCE:")
        for pole_nom in nouveau_mapping.keys():
            cursor.execute("SELECT COUNT(*) FROM projects WHERE poles = ?", (pole_nom,))
            count = cursor.fetchone()[0]
            regions = ', '.join(nouveau_mapping[pole_nom])
            print(f"  📍 {pole_nom} ({regions}): {count} projets")
        
        conn.commit()
        print("\n✅ Mise à jour terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")
        conn.rollback()
        raise
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Mise à jour des pôles territoriaux")
    print("=" * 50)
    
    update_poles()