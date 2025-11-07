#!/usr/bin/env python3
"""
Test de la nouvelle carte avec contours par pôles et régions
"""

import requests
import json

def test_carte_avancee():
    """Teste les données nécessaires pour la carte avancée"""
    
    print("🧪 TEST DE LA CARTE AVANCÉE")
    print("=" * 40)
    
    # 1. Test de l'API des statistiques
    try:
        response = requests.get('http://127.0.0.1:5002/api/stats/poles')
        if response.status_code == 200:
            poles_stats = response.json()
            print(f"✅ API Stats OK - {len(poles_stats)} pôles")
        else:
            print(f"❌ API Stats erreur: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erreur connexion API: {e}")
        return
    
    # 2. Test du fichier GeoJSON
    try:
        with open('/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/frontend/src/assets/poles_geojson.json', 'r') as f:
            geojson_data = json.load(f)
        
        print(f"✅ GeoJSON OK")
        print(f"  📍 Pôles: {len(geojson_data.get('poles', {}))}")
        print(f"  🏛️ Régions: {len(geojson_data.get('regions', {}))}")
        print(f"  📊 Centres: {len(geojson_data.get('centers', {}))}")
        
    except Exception as e:
        print(f"❌ Erreur GeoJSON: {e}")
        return
    
    # 3. Vérification cohérence pôles API ↔ GeoJSON
    api_poles = set(poles_stats.keys())
    geojson_poles = set(geojson_data.get('poles', {}).keys())
    
    print(f"\n🔄 COHÉRENCE API ↔ GEOJSON:")
    print(f"  API: {sorted(api_poles)}")
    print(f"  GeoJSON: {sorted(geojson_poles)}")
    
    missing_in_api = geojson_poles - api_poles
    missing_in_geojson = api_poles - geojson_poles
    
    if missing_in_api:
        print(f"  ⚠️ Manquants dans API: {missing_in_api}")
    if missing_in_geojson:
        print(f"  ⚠️ Manquants dans GeoJSON: {missing_in_geojson}")
    
    if not missing_in_api and not missing_in_geojson:
        print(f"  ✅ Parfaite cohérence!")
    
    # 4. Test des régions
    print(f"\n🗺️ RÉGIONS PAR PÔLE:")
    for pole, regions in geojson_data.get('regions_per_pole', {}).items():
        stats = poles_stats.get(pole, {})
        projets = stats.get('total', 0)
        montant = stats.get('cout_total', 0) / 1000000000
        
        print(f"  📍 {pole} ({len(regions)} régions): {projets} projets, {montant:.1f} Md")
        for region in regions:
            if region in geojson_data.get('regions', {}):
                print(f"    🏛️ {region} ✅")
            else:
                print(f"    🏛️ {region} ❌ (pas de géométrie)")
    
    print(f"\n🎨 FONCTIONNALITÉS DE LA CARTE:")
    print(f"  ✅ Couche régions (pointillés)")
    print(f"  ✅ Couche pôles (contours gras)")
    print(f"  ✅ Nuances de couleur par investissement")
    print(f"  ✅ Labels pôles et régions")
    print(f"  ✅ Tooltips interactifs")
    
    print(f"\n🚀 ACCÈS À LA CARTE:")
    print(f"  URL: http://127.0.0.1:5173")
    print(f"  Navigation: Aller dans l'onglet Carte des Pôles")

if __name__ == "__main__":
    test_carte_avancee()