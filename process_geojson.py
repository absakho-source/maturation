#!/usr/bin/env python3
"""
Script pour traiter le fichier GeoJSON des pôles territoriaux
et générer les données optimisées pour la carte Vue.js
"""

import json
import os

def calculate_center(geometry):
    """Calcule le centre géographique d'une géométrie"""
    coords = geometry.get('coordinates', [])
    total_lon, total_lat, total_points = 0, 0, 0
    
    if geometry.get('type') == 'Polygon':
        for ring in coords:
            for coord in ring:
                if len(coord) >= 2:
                    total_lon += coord[0]
                    total_lat += coord[1]
                    total_points += 1
    elif geometry.get('type') == 'MultiPolygon':
        for polygon in coords:
            for ring in polygon:
                for coord in ring:
                    if len(coord) >= 2:
                        total_lon += coord[0]
                        total_lat += coord[1]
                        total_points += 1
    
    if total_points > 0:
        return [total_lon / total_points, total_lat / total_points]
    return [0, 0]

def process_geojson():
    """Traite le fichier GeoJSON et génère les coordonnées pour Vue.js"""
    
    # Lire le fichier GeoJSON
    geojson_path = "/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/Regions_Poles_shape_clean.geojson"
    
    if not os.path.exists(geojson_path):
        print(f"❌ Fichier GeoJSON non trouvé: {geojson_path}")
        return
    
    print("📂 Lecture du fichier GeoJSON...")
    
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    
    print(f"✅ GeoJSON chargé avec {len(geojson_data.get('features', []))} régions")
    
    # Mapper les régions aux pôles territoriaux (corrigé selon spécifications)
    poles_mapping = {
        'Dakar': ['DAKAR'],
        'Thiès': ['THIES'],
        'Centre': ['FATICK', 'KAOLACK', 'KAFFRINE'],  # Correction: supprimé Diourbel
        'Diourbel-Louga': ['DIOURBEL', 'LOUGA'],      # Correction: ajouté Diourbel
        'Sud': ['ZIGUINCHOR', 'SEDHIOU', 'KOLDA'],
        'Sud-Est': ['KEDOUGOU', 'TAMBACOUNDA'],
        'Nord': ['SAINT-LOUIS'],
        'Nord-Est': ['MATAM']
    }
    
    # Inverser le mapping pour avoir region -> pole
    region_to_pole = {}
    for pole, regions in poles_mapping.items():
        for region in regions:
            region_to_pole[region] = pole
    
    print(f"🗺️ Mapping des régions aux pôles: {len(region_to_pole)} régions")
    
    # Traiter chaque région
    poles_geojson = {}
    regions_geojson = {}
    region_centers = {}  # Centres des régions individuelles
    bounds = {'minLon': float('inf'), 'maxLon': float('-inf'), 
              'minLat': float('inf'), 'maxLat': float('-inf')}
    
    for feature in geojson_data.get('features', []):
        properties = feature.get('properties', {})
        geometry = feature.get('geometry', {})
        
        region_name = properties.get('NOMREG', '').upper()
        pole_name = region_to_pole.get(region_name)
        
        if not pole_name:
            print(f"⚠️ Région non mappée: {region_name}")
            continue
        
        # Calculer le centre de chaque région individuelle
        region_center = calculate_center(geometry)
        if region_center:
            region_centers[region_name] = region_center
        
        # Traiter les pôles
        if pole_name not in poles_geojson:
            poles_geojson[pole_name] = {
                'type': 'Feature',
                'properties': {'name': pole_name, 'regions': []},
                'geometry': {'type': 'MultiPolygon', 'coordinates': []}
            }
        
        poles_geojson[pole_name]['properties']['regions'].append(region_name)
        
        # Ajouter les coordonnées au pôle
        if geometry.get('type') == 'Polygon':
            poles_geojson[pole_name]['geometry']['coordinates'].append(geometry['coordinates'])
        elif geometry.get('type') == 'MultiPolygon':
            poles_geojson[pole_name]['geometry']['coordinates'].extend(geometry['coordinates'])
        
        # Traiter les régions individuelles
        regions_geojson[region_name] = {
            'type': 'Feature',
            'properties': {'name': region_name, 'pole': pole_name},
            'geometry': geometry,
            'center': calculate_center(geometry)
        }
        
        # Calculer les bounds
        coords = geometry.get('coordinates', [])
        if geometry.get('type') == 'Polygon':
            for ring in coords:
                for coord in ring:
                    if len(coord) >= 2:
                        lon, lat = coord[0], coord[1]
                        bounds['minLon'] = min(bounds['minLon'], lon)
                        bounds['maxLon'] = max(bounds['maxLon'], lon)
                        bounds['minLat'] = min(bounds['minLat'], lat)
                        bounds['maxLat'] = max(bounds['maxLat'], lat)
        elif geometry.get('type') == 'MultiPolygon':
            for polygon in coords:
                for ring in polygon:
                    for coord in ring:
                        if len(coord) >= 2:
                            lon, lat = coord[0], coord[1]
                            bounds['minLon'] = min(bounds['minLon'], lon)
                            bounds['maxLon'] = max(bounds['maxLon'], lon)
                            bounds['minLat'] = min(bounds['minLat'], lat)
                            bounds['maxLat'] = max(bounds['maxLat'], lat)
    
    print(f"🎯 Pôles traités: {list(poles_geojson.keys())}")
    print(f"📏 Bounds: Lon[{bounds['minLon']:.3f}, {bounds['maxLon']:.3f}], Lat[{bounds['minLat']:.3f}, {bounds['maxLat']:.3f}]")
    
    # Calculer les centres des pôles
    poles_centers = {}
    for pole_name, pole_data in poles_geojson.items():
        coords = pole_data['geometry']['coordinates']
        
        total_lon, total_lat, total_points = 0, 0, 0
        
        for polygon in coords:
            for ring in polygon:
                for coord in ring:
                    if len(coord) >= 2:
                        total_lon += coord[0]
                        total_lat += coord[1]
                        total_points += 1
        
        if total_points > 0:
            center_lon = total_lon / total_points
            center_lat = total_lat / total_points
            poles_centers[pole_name] = [center_lon, center_lat]
        
    print(f"📍 Centres calculés pour {len(poles_centers)} pôles")
    
    # Générer le fichier pour Vue.js
    vue_data = {
        'bounds': bounds,
        'poles': poles_geojson,
        'regions': regions_geojson,
        'centers': poles_centers,
        'region_centers': region_centers,  # Centres des régions individuelles
        'regions_per_pole': poles_mapping,
        'metadata': {
            'source': 'Regions_Poles_shape_clean.geojson',
            'processed_date': '2025-10-27',
            'total_poles': len(poles_geojson),
            'total_regions': len(regions_geojson),
            'mapping': poles_mapping
        }
    }
    
    # Sauvegarder le fichier optimisé
    output_path = "/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/frontend/src/assets/poles_geojson.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(vue_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Fichier optimisé sauvegardé: {output_path}")
    
    # Générer aussi une version simplifiée pour debug
    debug_data = {
        'poles_list': list(poles_geojson.keys()),
        'bounds': bounds,
        'centers': poles_centers,
        'regions_per_pole': {pole: data['properties']['regions'] for pole, data in poles_geojson.items()}
    }
    
    debug_path = "/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/poles_debug.json"
    with open(debug_path, 'w', encoding='utf-8') as f:
        json.dump(debug_data, f, ensure_ascii=False, indent=2)
    
    print(f"🔍 Fichier debug sauvegardé: {debug_path}")
    
    return vue_data

if __name__ == "__main__":
    print("🚀 Traitement du fichier GeoJSON des pôles territoriaux")
    print("=" * 60)
    
    result = process_geojson()
    
    if result:
        print("=" * 60)
        print("✅ Traitement terminé avec succès!")
        print(f"📊 {len(result['poles'])} pôles territoriaux traités")
        print(f"🗺️ Bounds: {result['bounds']}")
    else:
        print("❌ Erreur lors du traitement")