#!/usr/bin/env python3
"""
Script simplifié pour analyser les shapefiles des pôles territoriaux
"""

import json
import struct
import os
import sys

def read_dbf_file(dbf_path):
    """Lire un fichier DBF simplement pour extraire les attributs"""
    try:
        with open(dbf_path, 'rb') as f:
            # Lire l'en-tête DBF
            header = f.read(32)
            if len(header) < 32:
                return []
            
            # Extraire les informations de base
            record_count = struct.unpack('<I', header[4:8])[0]
            header_length = struct.unpack('<H', header[8:10])[0]
            record_length = struct.unpack('<H', header[10:12])[0]
            
            print(f"📊 Fichier DBF analysé:")
            print(f"   Nombre d'enregistrements: {record_count}")
            print(f"   Longueur d'en-tête: {header_length}")
            print(f"   Longueur d'enregistrement: {record_length}")
            
            # Lire les descripteurs de champs
            fields = []
            f.seek(32)
            while True:
                field_desc = f.read(32)
                if len(field_desc) < 32 or field_desc[0] == 0x0D:
                    break
                
                field_name = field_desc[:11].strip(b'\x00').decode('utf-8', errors='ignore')
                field_type = chr(field_desc[11])
                field_length = field_desc[16]
                
                fields.append({
                    'name': field_name,
                    'type': field_type,
                    'length': field_length
                })
            
            print(f"   Champs détectés: {[f['name'] for f in fields]}")
            
            # Lire quelques enregistrements
            records = []
            f.seek(header_length)
            
            for i in range(min(record_count, 10)):  # Lire maximum 10 enregistrements
                record_data = f.read(record_length)
                if len(record_data) < record_length:
                    break
                
                # Ignorer le marqueur de suppression
                if record_data[0] == ord('*'):
                    continue
                
                record = {}
                offset = 1
                
                for field in fields:
                    field_data = record_data[offset:offset + field['length']]
                    field_value = field_data.strip(b'\x00\x20').decode('utf-8', errors='ignore')
                    record[field['name']] = field_value
                    offset += field['length']
                
                records.append(record)
            
            return records
            
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier DBF: {e}")
        return []

def read_prj_file(prj_path):
    """Lire le fichier de projection"""
    try:
        with open(prj_path, 'r') as f:
            projection = f.read().strip()
            print(f"🗺️ Système de coordonnées: {projection[:100]}...")
            return projection
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier PRJ: {e}")
        return None

def analyze_shapefile_directory(shapefile_dir):
    """Analyser un répertoire de shapefiles"""
    print(f"🔍 Analyse du répertoire: {shapefile_dir}")
    
    # Trouver les fichiers
    shp_file = None
    dbf_file = None
    prj_file = None
    
    for file in os.listdir(shapefile_dir):
        if file.endswith('.shp'):
            shp_file = os.path.join(shapefile_dir, file)
        elif file.endswith('.dbf'):
            dbf_file = os.path.join(shapefile_dir, file)
        elif file.endswith('.prj'):
            prj_file = os.path.join(shapefile_dir, file)
    
    if not shp_file or not dbf_file:
        print("❌ Fichiers SHP ou DBF manquants")
        return None
    
    print(f"✅ Fichiers trouvés:")
    print(f"   SHP: {os.path.basename(shp_file)}")
    print(f"   DBF: {os.path.basename(dbf_file)}")
    if prj_file:
        print(f"   PRJ: {os.path.basename(prj_file)}")
    
    # Lire les attributs
    records = read_dbf_file(dbf_file)
    
    # Lire la projection
    if prj_file:
        projection = read_prj_file(prj_file)
    
    # Analyser les tailles de fichiers
    shp_size = os.path.getsize(shp_file)
    print(f"📏 Taille du fichier SHP: {shp_size:,} octets ({shp_size/1024:.1f} KB)")
    
    return {
        'records': records,
        'projection': projection if prj_file else None,
        'file_info': {
            'shp_size': shp_size,
            'record_count': len(records)
        }
    }

def generate_simple_map_data(records):
    """Générer des données de carte simplifiées basées sur les attributs"""
    
    # Chercher les champs qui pourraient contenir les noms des pôles
    name_fields = []
    if records:
        for field_name in records[0].keys():
            if any(keyword in field_name.lower() for keyword in ['nom', 'name', 'region', 'pole', 'libelle']):
                name_fields.append(field_name)
    
    print(f"🏷️ Champs de noms détectés: {name_fields}")
    
    # Extraire les noms des pôles
    pole_names = []
    for record in records:
        for field in name_fields:
            value = record.get(field, '').strip()
            if value and value not in pole_names:
                pole_names.append(value)
    
    print(f"📋 Pôles territoriaux trouvés: {pole_names}")
    
    # Créer un mapping vers les noms standardisés
    standard_mapping = {
        'Dakar': 'Dakar',
        'Thiès': 'Thiès',
        'Thies': 'Thiès',
        'Kaolack': 'Centre',
        'Fatick': 'Centre', 
        'Kaffrine': 'Centre',
        'Centre': 'Centre',
        'Diourbel': 'Diourbel-Louga',
        'Louga': 'Diourbel-Louga',
        'Saint-Louis': 'Nord',
        'Saint Louis': 'Nord',
        'Nord': 'Nord',
        'Matam': 'Nord-Est',
        'Nord-Est': 'Nord-Est',
        'Tambacounda': 'Sud-Est',
        'Kédougou': 'Sud-Est',
        'Kedougou': 'Sud-Est',
        'Sud-Est': 'Sud-Est',
        'Ziguinchor': 'Sud',
        'Sédhiou': 'Sud',
        'Sedhiou': 'Sud',
        'Kolda': 'Sud',
        'Sud': 'Sud'
    }
    
    mapped_poles = set()
    for name in pole_names:
        for key, value in standard_mapping.items():
            if key.lower() in name.lower():
                mapped_poles.add(value)
                break
    
    print(f"🎯 Pôles mappés: {sorted(mapped_poles)}")
    
    return {
        'detected_poles': pole_names,
        'mapped_poles': sorted(mapped_poles),
        'records': records
    }

def create_integration_files(analysis_result, output_dir):
    """Créer les fichiers d'intégration pour la carte Vue.js"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Fichier de métadonnées des pôles
    metadata_file = os.path.join(output_dir, 'poles_metadata.json')
    metadata = {
        'source': 'Regions_Poles_shape',
        'detected_poles': analysis_result['detected_poles'],
        'mapped_poles': analysis_result['mapped_poles'],
        'records': analysis_result['records'],
        'integration_status': 'metadata_only',
        'notes': 'Données géographiques précises disponibles mais nécessitent GeoPandas pour extraction complète'
    }
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Métadonnées sauvegardées: {metadata_file}")
    
    # 2. Fichier de configuration pour la carte
    config_file = os.path.join(output_dir, 'poles_config.json')
    config = {
        'use_shapefile_data': False,
        'fallback_reason': 'GDAL dependency not available',
        'available_poles': analysis_result['mapped_poles'],
        'data_source': 'simplified_geometry',
        'enhancement_available': True,
        'enhancement_instructions': [
            "Install GDAL and GeoPandas for precise geographical boundaries",
            "Run: pip install geopandas matplotlib shapely fiona",
            "Execute: python analyze_shapefiles.py --full-processing"
        ]
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuration sauvegardée: {config_file}")
    
    return metadata_file, config_file

def main():
    # Analyser le dossier de shapefiles
    shapefile_dir = "/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/Regions_Poles_shape"
    
    if not os.path.exists(shapefile_dir):
        print(f"❌ Dossier shapefile non trouvé: {shapefile_dir}")
        return
    
    print("🗺️ ANALYSE DES SHAPEFILES DES PÔLES TERRITORIAUX")
    print("=" * 60)
    
    # Analyser les fichiers
    analysis = analyze_shapefile_directory(shapefile_dir)
    
    if not analysis:
        print("❌ Échec de l'analyse")
        return
    
    # Générer les données de carte
    map_data = generate_simple_map_data(analysis['records'])
    
    # Créer les fichiers d'intégration
    output_dir = "/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/frontend/src/assets"
    metadata_file, config_file = create_integration_files(map_data, output_dir)
    
    print("\n" + "=" * 60)
    print("🎉 ANALYSE TERMINÉE!")
    print("=" * 60)
    print(f"📊 Pôles détectés: {len(map_data['mapped_poles'])}")
    print(f"📁 Métadonnées: {metadata_file}")
    print(f"⚙️ Configuration: {config_file}")
    print("\n🎨 La carte peut maintenant utiliser ces informations!")
    print("💡 Pour des frontières géographiques précises, installez GDAL/GeoPandas")

if __name__ == "__main__":
    main()