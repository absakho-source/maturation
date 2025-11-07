#!/usr/bin/env python3
"""
Script de vérification de la cohérence des pôles territoriaux
"""

import json
import sqlite3
import os

def verification_coherence():
    """Vérifie la cohérence entre GeoJSON, API et base de données"""
    
    print("🔍 VÉRIFICATION DE LA COHÉRENCE DES PÔLES TERRITORIAUX")
    print("=" * 60)
    
    # 1. Charger les données GeoJSON
    geojson_path = '/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/frontend/src/assets/poles_geojson.json'
    debug_path = '/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/poles_debug.json'
    
    with open(debug_path, 'r', encoding='utf-8') as f:
        debug_data = json.load(f)
    
    print("📍 PÔLES DANS LE GEOJSON:")
    for pole, regions in debug_data['regions_per_pole'].items():
        print(f"  {pole}: {', '.join(regions)}")
    
    # 2. Vérifier la base de données
    db_path = '/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/backend/maturation.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT poles, COUNT(*) FROM projects WHERE poles IS NOT NULL GROUP BY poles ORDER BY poles")
    db_poles = cursor.fetchall()
    
    print("\n💾 PÔLES DANS LA BASE DE DONNÉES:")
    for pole, count in db_poles:
        print(f"  {pole}: {count} projets")
    
    # 3. Vérifications spécifiques demandées par l'utilisateur
    print("\n✅ VÉRIFICATIONS SPÉCIFIQUES:")
    
    # Centre doit contenir uniquement Kaolack, Fatick, Kaffrine
    centre_regions = debug_data['regions_per_pole'].get('Centre', [])
    expected_centre = ['FATICK', 'KAOLACK', 'KAFFRINE']
    if set(centre_regions) == set(expected_centre):
        print(f"  ✅ Centre correct: {', '.join(centre_regions)}")
    else:
        print(f"  ❌ Centre incorrect: {', '.join(centre_regions)} (attendu: {', '.join(expected_centre)})")
    
    # Diourbel-Louga doit contenir Diourbel et Louga
    diourbel_regions = debug_data['regions_per_pole'].get('Diourbel-Louga', [])
    expected_diourbel = ['DIOURBEL', 'LOUGA']
    if set(diourbel_regions) == set(expected_diourbel):
        print(f"  ✅ Diourbel-Louga correct: {', '.join(diourbel_regions)}")
    else:
        print(f"  ❌ Diourbel-Louga incorrect: {', '.join(diourbel_regions)} (attendu: {', '.join(expected_diourbel)})")
    
    # 4. Vérifier que tous les pôles GeoJSON existent en base
    geojson_poles = set(debug_data['regions_per_pole'].keys())
    db_poles_set = set(pole for pole, _ in db_poles)
    
    print("\n🔄 CORRESPONDANCE GEOJSON ↔ BASE:")
    for pole in geojson_poles:
        if pole in db_poles_set:
            print(f"  ✅ {pole}: Présent dans les deux")
        else:
            print(f"  ⚠️  {pole}: Présent dans GeoJSON mais pas en base")
    
    for pole in db_poles_set:
        if pole not in geojson_poles:
            print(f"  ⚠️  {pole}: Présent en base mais pas dans GeoJSON")
    
    conn.close()
    
    print("\n📊 RÉSUMÉ:")
    print(f"  • Pôles GeoJSON: {len(geojson_poles)}")
    print(f"  • Pôles en base: {len(db_poles_set)}")
    print(f"  • Total projets: {sum(count for _, count in db_poles)}")

if __name__ == "__main__":
    verification_coherence()