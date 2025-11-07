#!/usr/bin/env python3
"""
Script pour analyser les shapefiles des pôles territoriaux et générer une carte précise
"""

import json
import os
import sys

try:
    import geopandas as gpd
    import matplotlib.pyplot as plt
    from shapely.geometry import Point, Polygon
    import fiona
except ImportError:
    print("Modules manquants. Installation en cours...")
    os.system("pip install geopandas matplotlib shapely fiona")
    import geopandas as gpd
    import matplotlib.pyplot as plt
    from shapely.geometry import Point, Polygon
    import fiona

def analyze_shapefile(shapefile_path):
    """Analyser un shapefile et extraire les informations"""
    try:
        print(f"📊 Analyse du shapefile: {shapefile_path}")
        
        # Lire le shapefile
        gdf = gpd.read_file(shapefile_path)
        
        print(f"✅ Shapefile chargé avec succès")
        print(f"   Nombre d'entités: {len(gdf)}")
        print(f"   Système de coordonnées: {gdf.crs}")
        print(f"   Colonnes disponibles: {list(gdf.columns)}")
        
        # Afficher quelques exemples
        print(f"\n📋 Premières entités:")
        for i, row in gdf.head().iterrows():
            print(f"   {i}: {dict(row.drop('geometry'))}")
        
        # Bornes géographiques
        bounds = gdf.total_bounds
        print(f"\n🗺️  Bornes géographiques:")
        print(f"   Longitude: {bounds[0]:.4f} à {bounds[2]:.4f}")
        print(f"   Latitude: {bounds[1]:.4f} à {bounds[3]:.4f}")
        
        return gdf
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        return None

def convert_to_geojson(gdf, output_path):
    """Convertir en GeoJSON pour usage web"""
    try:
        # Reprojeter en WGS84 si nécessaire
        if gdf.crs != 'EPSG:4326':
            print("🔄 Reprojection en WGS84...")
            gdf = gdf.to_crs('EPSG:4326')
        
        # Sauvegarder en GeoJSON
        gdf.to_file(output_path, driver='GeoJSON')
        print(f"✅ GeoJSON sauvegardé: {output_path}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la conversion: {e}")
        return False

def generate_svg_paths(gdf, output_path, width=800, height=600):
    """Générer des chemins SVG optimisés pour la carte Vue.js"""
    try:
        # Reprojeter en WGS84 si nécessaire
        if gdf.crs != 'EPSG:4326':
            gdf = gdf.to_crs('EPSG:4326')
        
        # Calculer les bornes pour la normalisation
        bounds = gdf.total_bounds
        min_lon, min_lat, max_lon, max_lat = bounds
        
        # Fonction pour normaliser les coordonnées vers SVG
        def normalize_coords(lon, lat):
            x = ((lon - min_lon) / (max_lon - min_lon)) * width
            y = height - ((lat - min_lat) / (max_lat - min_lat)) * height  # Inverser Y
            return x, y
        
        svg_data = {}
        
        print(f"🎨 Génération des chemins SVG...")
        for i, row in gdf.iterrows():
            geometry = row.geometry
            
            # Identifier le nom du pôle/région
            name_candidates = ['nom', 'name', 'region', 'pole', 'NAME', 'NOM', 'REGION']
            pole_name = None
            for candidate in name_candidates:
                if candidate in row.index and pd.notna(row[candidate]):
                    pole_name = str(row[candidate])
                    break
            
            if not pole_name:
                pole_name = f"Region_{i}"
            
            if geometry.geom_type == 'Polygon':
                # Convertir polygon en chemin SVG
                coords = list(geometry.exterior.coords)
                svg_points = []
                
                for lon, lat in coords:
                    x, y = normalize_coords(lon, lat)
                    svg_points.append(f"{x:.1f},{y:.1f}")
                
                svg_data[pole_name] = {
                    'type': 'polygon',
                    'points': ' '.join(svg_points),
                    'path': f"M {svg_points[0]} L {' L '.join(svg_points[1:])} Z"
                }
                
            elif geometry.geom_type == 'MultiPolygon':
                # Prendre le plus grand polygone
                largest_poly = max(geometry.geoms, key=lambda p: p.area)
                coords = list(largest_poly.exterior.coords)
                svg_points = []
                
                for lon, lat in coords:
                    x, y = normalize_coords(lon, lat)
                    svg_points.append(f"{x:.1f},{y:.1f}")
                
                svg_data[pole_name] = {
                    'type': 'polygon',
                    'points': ' '.join(svg_points),
                    'path': f"M {svg_points[0]} L {' L '.join(svg_points[1:])} Z"
                }
        
        # Sauvegarder les données SVG
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(svg_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Chemins SVG générés: {output_path}")
        print(f"   Pôles/régions détectés: {list(svg_data.keys())}")
        
        return svg_data
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération SVG: {e}")
        return None

def create_preview_map(gdf, output_path):
    """Créer un aperçu de la carte"""
    try:
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        # Dessiner la carte
        gdf.plot(ax=ax, color='lightblue', edgecolor='black', linewidth=0.5)
        
        # Ajouter les noms si disponible
        name_candidates = ['nom', 'name', 'region', 'pole', 'NAME', 'NOM', 'REGION']
        for i, row in gdf.iterrows():
            centroid = row.geometry.centroid
            
            name = None
            for candidate in name_candidates:
                if candidate in row.index and pd.notna(row[candidate]):
                    name = str(row[candidate])
                    break
            
            if name:
                ax.text(centroid.x, centroid.y, name, 
                       fontsize=8, ha='center', va='center',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
        
        ax.set_title("Aperçu des Pôles Territoriaux du Sénégal")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Aperçu sauvegardé: {output_path}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'aperçu: {e}")

def main():
    # Chercher les shapefiles dans le workspace
    base_dir = "/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation"
    possible_paths = [
        os.path.join(base_dir, "Regions_Poles_shape"),
        os.path.join(base_dir, "shapefiles"),
        os.path.join(base_dir, "data"),
        base_dir
    ]
    
    shapefile_found = None
    
    print("🔍 Recherche des shapefiles...")
    for path in possible_paths:
        if os.path.exists(path):
            print(f"   Vérification: {path}")
            for file in os.listdir(path):
                if file.endswith('.shp'):
                    shapefile_found = os.path.join(path, file)
                    print(f"✅ Shapefile trouvé: {shapefile_found}")
                    break
            if shapefile_found:
                break
    
    if not shapefile_found:
        print("❌ Aucun shapefile trouvé. Veuillez copier le dossier 'Regions_Poles_shape' dans le workspace.")
        print("   Emplacements recherchés:")
        for path in possible_paths:
            print(f"   - {path}")
        return
    
    # Analyser le shapefile
    gdf = analyze_shapefile(shapefile_found)
    if gdf is None:
        return
    
    # Créer les fichiers de sortie
    output_dir = os.path.join(base_dir, "frontend", "src", "assets")
    os.makedirs(output_dir, exist_ok=True)
    
    # Convertir en GeoJSON
    geojson_path = os.path.join(output_dir, "poles_territoriaux.geojson")
    convert_to_geojson(gdf, geojson_path)
    
    # Générer les chemins SVG
    svg_path = os.path.join(output_dir, "poles_svg_data.json")
    svg_data = generate_svg_paths(gdf, svg_path)
    
    # Créer un aperçu
    preview_path = os.path.join(base_dir, "apercu_poles_territoriaux.png")
    create_preview_map(gdf, preview_path)
    
    print(f"\n🎉 Analyse terminée!")
    print(f"   📁 GeoJSON: {geojson_path}")
    print(f"   📁 SVG Data: {svg_path}")
    print(f"   📁 Aperçu: {preview_path}")
    
    if svg_data:
        print(f"\n📋 Résumé des pôles détectés:")
        for i, pole in enumerate(svg_data.keys(), 1):
            print(f"   {i}. {pole}")

if __name__ == "__main__":
    # Vérifier si pandas est disponible
    try:
        import pandas as pd
    except ImportError:
        print("Installation de pandas...")
        os.system("pip install pandas")
        import pandas as pd
    
    main()