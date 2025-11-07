#!/usr/bin/env python3
"""
Script pour générer une carte SVG précise des pôles territoriaux du Sénégal
à partir des données shapefiles officielles.
"""

import geopandas as gpd
import json
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
from pathlib import Path

# Correspondance entre régions administratives et pôles territoriaux
REGIONS_TO_POLES = {
    # Pôle Dakar
    'Dakar': 'Dakar',
    
    # Pôle Thiès  
    'Thiès': 'Thiès',
    
    # Pôle Centre (Kaolack, Fatick, Kaffrine)
    'Kaolack': 'Centre (Kaolack, Fatick, Kaffrine)',
    'Fatick': 'Centre (Kaolack, Fatick, Kaffrine)', 
    'Kaffrine': 'Centre (Kaolack, Fatick, Kaffrine)',
    
    # Pôle Diourbel-Louga
    'Diourbel': 'Diourbel-Louga',
    'Louga': 'Diourbel-Louga',
    
    # Pôle Sud (Ziguinchor, Sédhiou, Kolda)
    'Ziguinchor': 'Sud (Ziguinchor, Sédhiou, Kolda)',
    'Sédhiou': 'Sud (Ziguinchor, Sédhiou, Kolda)',
    'Sedhiou': 'Sud (Ziguinchor, Sédhiou, Kolda)',  # Variante orthographe
    'Kolda': 'Sud (Ziguinchor, Sédhiou, Kolda)',
    
    # Pôle Sud-Est (Tambacounda, Kédougou)
    'Tambacounda': 'Sud-Est (Tambacounda, Kédougou)',
    'Kédougou': 'Sud-Est (Tambacounda, Kédougou)',
    'Kedougou': 'Sud-Est (Tambacounda, Kédougou)',  # Variante orthographe
    
    # Pôle Nord (Saint-Louis)
    'Saint-Louis': 'Nord (Saint-Louis)',
    'Saint Louis': 'Nord (Saint-Louis)',
    
    # Pôle Nord-Est (Matam)
    'Matam': 'Nord-Est (Matam)'
}

def load_shapefile_data(shapefile_path):
    """Charge les données shapefile des régions du Sénégal"""
    try:
        # Charger le fichier shapefile des régions (niveau administratif 1)
        gdf = gpd.read_file(shapefile_path)
        print(f"✅ Shapefile chargé: {len(gdf)} régions trouvées")
        
        # Afficher les noms des régions disponibles
        print("\n📍 Régions disponibles dans le shapefile:")
        for idx, row in gdf.iterrows():
            # Chercher les colonnes contenant les noms
            name_cols = [col for col in gdf.columns if any(x in col.lower() for x in ['name', 'nom', 'region', 'adm1'])]
            region_name = "Nom non trouvé"
            for col in name_cols:
                if row[col] and str(row[col]).strip():
                    region_name = str(row[col]).strip()
                    break
            print(f"  - {region_name}")
        
        return gdf
    except Exception as e:
        print(f"❌ Erreur lors du chargement du shapefile: {e}")
        return None

def group_regions_by_poles(gdf):
    """Groupe les régions par pôles territoriaux"""
    poles_data = {}
    
    # Identifier la colonne contenant les noms de régions
    name_cols = [col for col in gdf.columns if any(x in col.lower() for x in ['name', 'nom', 'region', 'adm1'])]
    name_col = name_cols[0] if name_cols else None
    
    if not name_col:
        print("❌ Impossible de trouver la colonne des noms de régions")
        return None
    
    print(f"\n🔍 Utilisation de la colonne '{name_col}' pour les noms de régions")
    
    for idx, row in gdf.iterrows():
        region_name = str(row[name_col]).strip()
        
        # Trouver le pôle correspondant
        pole = None
        for region_key, pole_name in REGIONS_TO_POLES.items():
            if region_key.lower() in region_name.lower() or region_name.lower() in region_key.lower():
                pole = pole_name
                break
        
        if pole:
            if pole not in poles_data:
                poles_data[pole] = {
                    'regions': [],
                    'geometries': []
                }
            poles_data[pole]['regions'].append(region_name)
            poles_data[pole]['geometries'].append(row.geometry)
            print(f"  ✅ {region_name} → {pole}")
        else:
            print(f"  ⚠️ Région non mappée: {region_name}")
    
    return poles_data

def convert_to_svg_coordinates(poles_data, svg_width=800, svg_height=600):
    """Convertit les coordonnées géographiques en coordonnées SVG"""
    import numpy as np
    from shapely.ops import unary_union
    
    # Calculer les limites globales de toutes les géométries
    all_geometries = []
    for pole_data in poles_data.values():
        all_geometries.extend(pole_data['geometries'])
    
    if not all_geometries:
        return None
    
    # Union de toutes les géométries pour avoir les limites du Sénégal
    total_bounds = gpd.GeoSeries(all_geometries).total_bounds
    min_x, min_y, max_x, max_y = total_bounds
    
    print(f"\n📏 Limites géographiques du Sénégal:")
    print(f"  Longitude: {min_x:.4f} à {max_x:.4f}")
    print(f"  Latitude: {min_y:.4f} à {max_y:.4f}")
    
    # Marge pour le SVG (10% de chaque côté)
    margin = 0.1
    svg_margin_x = svg_width * margin
    svg_margin_y = svg_height * margin
    effective_width = svg_width - 2 * svg_margin_x
    effective_height = svg_height - 2 * svg_margin_y
    
    def geo_to_svg(lon, lat):
        """Convertit longitude/latitude en coordonnées SVG"""
        # Normaliser les coordonnées géographiques
        x_norm = (lon - min_x) / (max_x - min_x)
        y_norm = (lat - min_y) / (max_y - min_y)
        
        # Convertir en coordonnées SVG (Y inversé pour SVG)
        svg_x = svg_margin_x + x_norm * effective_width
        svg_y = svg_margin_y + (1 - y_norm) * effective_height
        
        return svg_x, svg_y
    
    svg_poles = {}
    
    for pole_name, pole_data in poles_data.items():
        # Fusionner toutes les géométries du pôle
        merged_geometry = unary_union(pole_data['geometries'])
        
        # Convertir en coordonnées SVG
        if hasattr(merged_geometry, 'exterior'):
            # Polygon simple
            coords = list(merged_geometry.exterior.coords)
        elif hasattr(merged_geometry, 'geoms'):
            # MultiPolygon - prendre le plus grand polygon
            largest_poly = max(merged_geometry.geoms, key=lambda x: x.area)
            coords = list(largest_poly.exterior.coords)
        else:
            print(f"⚠️ Géométrie non supportée pour {pole_name}")
            continue
        
        # Convertir les coordonnées
        svg_coords = []
        for lon, lat in coords:
            svg_x, svg_y = geo_to_svg(lon, lat)
            svg_coords.append(f"{svg_x:.1f},{svg_y:.1f}")
        
        # Calculer le centroïde pour le label
        centroid = merged_geometry.centroid
        label_x, label_y = geo_to_svg(centroid.x, centroid.y)
        
        svg_poles[pole_name] = {
            'path': " ".join(svg_coords),
            'label_x': label_x,
            'label_y': label_y,
            'regions': pole_data['regions']
        }
        
        print(f"✅ {pole_name}: {len(coords)} points, centroïde à ({label_x:.1f}, {label_y:.1f})")
    
    return svg_poles

def generate_vue_component(svg_poles):
    """Génère le code Vue.js avec les coordonnées SVG précises"""
    
    template = '''    <!-- Carte interactive avec coordonnées géographiques précises -->
    <div class="carte-senegal">
      <svg viewBox="0 0 800 600" class="senegal-map">
        <!-- Carte géographiquement précise des pôles territoriaux du Sénégal -->
        
'''
    
    for pole_name, pole_data in svg_poles.items():
        # Nettoyer le nom pour l'ID
        pole_id = pole_name.replace(' ', '_').replace('(', '').replace(')', '').replace(',', '')
        
        template += f'''        <!-- Pôle {pole_name} -->
        <polygon 
          points="{pole_data['path']}"
          :class="getPoleClass('{pole_name}')"
          @click="selectPole('{pole_name}')"
          @mouseover="showTooltip($event, '{pole_name}')"
          @mouseleave="hideTooltip"
        />
        <text x="{pole_data['label_x']:.1f}" y="{pole_data['label_y']:.1f}" class="pole-label">{pole_name.split('(')[0].strip()}</text>
        
'''
    
    template += '''        <!-- Contour du Sénégal -->
        <g class="country-border">
'''
    
    # Ajouter le contour global (optionnel)
    template += '''        </g>
      </svg>
    </div>'''
    
    return template

def main():
    """Fonction principale"""
    print("🗺️ Génération de la carte des pôles territoriaux du Sénégal")
    print("=" * 60)
    
    # Chemin vers les shapefiles
    shapefile_dir = Path("/Users/abou/Downloads/sen_admbnd_anat_20240520_ab_shp")
    
    # Essayer les différents niveaux administratifs
    shapefiles = [
        shapefile_dir / "sen_admbnda_adm1_anat_20240520.shp",  # Régions
        shapefile_dir / "sen_admbnda_adm0_anat_20240520.shp",  # Pays
        shapefile_dir / "sen_admbnda_adm2_anat_20240520.shp",  # Départements
    ]
    
    gdf = None
    for shapefile_path in shapefiles:
        if shapefile_path.exists():
            print(f"\n📂 Tentative de chargement: {shapefile_path.name}")
            gdf = load_shapefile_data(shapefile_path)
            if gdf is not None:
                break
    
    if gdf is None:
        print("❌ Aucun shapefile valide trouvé")
        return
    
    # Grouper les régions par pôles
    print(f"\n🏢 Groupement des régions par pôles territoriaux")
    poles_data = group_regions_by_poles(gdf)
    
    if not poles_data:
        print("❌ Erreur lors du groupement des régions")
        return
    
    print(f"\n📊 Résumé des pôles créés:")
    for pole_name, pole_data in poles_data.items():
        print(f"  📍 {pole_name}: {len(pole_data['regions'])} régions")
        for region in pole_data['regions']:
            print(f"     - {region}")
    
    # Convertir en coordonnées SVG
    print(f"\n🎨 Conversion en coordonnées SVG...")
    svg_poles = convert_to_svg_coordinates(poles_data)
    
    if not svg_poles:
        print("❌ Erreur lors de la conversion SVG")
        return
    
    # Générer le code Vue.js
    print(f"\n📝 Génération du code Vue.js...")
    vue_code = generate_vue_component(svg_poles)
    
    # Sauvegarder le code généré
    output_file = "carte_poles_generated.vue"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(vue_code)
    
    print(f"\n✅ Code Vue.js généré dans {output_file}")
    print(f"\n📋 Vous pouvez maintenant copier ce code dans CartePolesTerritoriaux.vue")
    
    # Afficher un aperçu
    print(f"\n👀 Aperçu du code généré:")
    print("=" * 60)
    print(vue_code[:500] + "..." if len(vue_code) > 500 else vue_code)

if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        print(f"❌ Modules manquants: {e}")
        print("📦 Installez les dépendances avec:")
        print("   pip install geopandas matplotlib shapely")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()