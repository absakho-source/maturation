#!/usr/bin/env python3
"""
Extraction des coordonnées géographiques réelles du shapefile Sénégal
et création de la configuration pour la carte interactive
"""

import struct
import json
import sys

def read_dbf_file(dbf_path):
    """Lire les métadonnées du fichier DBF"""
    records = []
    
    with open(dbf_path, 'rb') as f:
        # Lire l'en-tête DBF
        header = f.read(32)
        if len(header) < 32:
            return records
            
        # Extraire les informations de l'en-tête
        num_records = struct.unpack('<I', header[4:8])[0]
        header_length = struct.unpack('<H', header[8:10])[0]
        record_length = struct.unpack('<H', header[10:12])[0]
        
        print(f"DBF: {num_records} records, header: {header_length} bytes, record: {record_length} bytes")
        
        # Lire les descripteurs de champs
        field_descriptors = []
        pos = 32
        
        while pos < header_length - 1:
            field_data = f.read(32)
            if len(field_data) < 32 or field_data[0] == 0x0D:
                break
                
            field_name = field_data[:11].rstrip(b'\x00').decode('latin-1', errors='ignore')
            field_type = chr(field_data[11])
            field_length = field_data[16]
            
            field_descriptors.append({
                'name': field_name,
                'type': field_type,
                'length': field_length
            })
            pos += 32
        
        # Positionner après le marqueur de fin d'en-tête
        f.seek(header_length)
        
        # Lire les enregistrements
        for i in range(num_records):
            record_data = f.read(record_length)
            if len(record_data) < record_length:
                break
                
            # Le premier byte est un indicateur de suppression
            if record_data[0] == 0x2A:  # Record supprimé
                continue
                
            record = {}
            offset = 1  # Ignorer le premier byte
            
            for field in field_descriptors:
                field_data = record_data[offset:offset + field['length']]
                value = field_data.rstrip(b'\x00 ').decode('latin-1', errors='ignore')
                
                # Conversion selon le type
                if field['type'] == 'N':  # Numérique
                    try:
                        value = int(value) if value else 0
                    except ValueError:
                        try:
                            value = float(value) if value else 0.0
                        except ValueError:
                            value = 0
                elif field['type'] == 'F':  # Float
                    try:
                        value = float(value) if value else 0.0
                    except ValueError:
                        value = 0.0
                
                record[field['name']] = value
                offset += field['length']
            
            records.append(record)
    
    return records

def read_shapefile_coordinates(shp_path):
    """Extraire les coordonnées du fichier .shp"""
    coordinates = []
    
    with open(shp_path, 'rb') as f:
        # Lire l'en-tête
        header = f.read(100)
        if len(header) < 100:
            return coordinates
            
        # Bounding box globale
        bbox_global = struct.unpack('<dddd', header[36:68])
        print(f"Bounding box Sénégal: {bbox_global}")
        
        record_num = 0
        while True:
            # En-tête de l'enregistrement
            record_header = f.read(8)
            if len(record_header) < 8:
                break
                
            record_number, content_length = struct.unpack('>ii', record_header)
            content_length *= 2
            
            # Contenu de l'enregistrement
            content = f.read(content_length)
            if len(content) < content_length:
                break
                
            if len(content) >= 4:
                shape_type = struct.unpack('<i', content[:4])[0]
                
                if shape_type == 5:  # Polygon
                    if len(content) >= 44:
                        # Bounding box du polygone
                        bbox = struct.unpack('<dddd', content[4:36])
                        num_parts = struct.unpack('<i', content[36:40])[0]
                        num_points = struct.unpack('<i', content[40:44])[0]
                        
                        # Calculer le centre approximatif
                        center_lon = (bbox[0] + bbox[2]) / 2
                        center_lat = (bbox[1] + bbox[3]) / 2
                        
                        coordinates.append({
                            'id': record_num,
                            'bbox': bbox,
                            'center': [center_lon, center_lat],
                            'num_points': num_points
                        })
                        
            record_num += 1
            
    return coordinates

def create_poles_map():
    """Créer la carte des pôles territoriaux avec vraies coordonnées"""
    
    # Lire les métadonnées DBF
    dbf_records = read_dbf_file('Regions_Poles_shape/Regions_Poles_shape.dbf')
    
    # Lire les coordonnées SHP
    coordinates = read_shapefile_coordinates('Regions_Poles_shape/Regions_Poles_shape.shp')
    
    print(f"\nMétadonnées: {len(dbf_records)} régions")
    print(f"Coordonnées: {len(coordinates)} régions")
    
    # Associer les données
    poles_data = {}
    
    for i, (dbf, coord) in enumerate(zip(dbf_records, coordinates)):
        region_name = dbf.get('NOMREG', '').strip()
        pole_name = dbf.get('POLE', '').strip()
        
        if pole_name and region_name:
            # Normaliser le nom du pôle
            pole_normalized = pole_name.replace('-', ' ').title()
            
            # Mapping spécifique pour correspondre aux données API
            pole_mapping = {
                'Dakar': 'Dakar',
                'Centre': 'Centre', 
                'Diourbel Louga': 'Diourbel-Louga',
                'Sud': 'Sud',
                'Sud Est': 'Sud-Est', 
                'Nord': 'Nord',
                'Nord Est': 'Nord-Est'
            }
            
            pole_final = pole_mapping.get(pole_normalized, pole_normalized)
            
            if pole_final not in poles_data:
                poles_data[pole_final] = {
                    'name': pole_final,
                    'regions': [],
                    'coordinates': [],
                    'bbox': None
                }
            
            poles_data[pole_final]['regions'].append({
                'name': region_name,
                'coordinate': coord['center'],
                'bbox': coord['bbox']
            })
            
            poles_data[pole_final]['coordinates'].append(coord['center'])
    
    # Calculer les centres des pôles et bounding boxes
    for pole_name, data in poles_data.items():
        if data['coordinates']:
            # Centre du pôle = moyenne des centres des régions
            avg_lon = sum(c[0] for c in data['coordinates']) / len(data['coordinates'])
            avg_lat = sum(c[1] for c in data['coordinates']) / len(data['coordinates'])
            data['center'] = [avg_lon, avg_lat]
            
            # Bounding box du pôle
            all_bboxes = [r['bbox'] for r in data['regions']]
            min_lon = min(bbox[0] for bbox in all_bboxes)
            min_lat = min(bbox[1] for bbox in all_bboxes)
            max_lon = max(bbox[2] for bbox in all_bboxes)
            max_lat = max(bbox[3] for bbox in all_bboxes)
            data['bbox'] = [min_lon, min_lat, max_lon, max_lat]
    
    print(f"\n=== PÔLES TERRITORIAUX AVEC COORDONNÉES RÉELLES ===")
    for pole_name, data in poles_data.items():
        center = data.get('center', [0, 0])
        regions = [r['name'] for r in data['regions']]
        print(f"{pole_name}: Centre=[{center[0]:.4f}, {center[1]:.4f}] - Régions: {', '.join(regions)}")
    
    return poles_data

if __name__ == "__main__":
    # Créer la carte des pôles
    poles_map = create_poles_map()
    
    # Sauvegarder la configuration
    with open('frontend/src/assets/poles_coordinates.json', 'w', encoding='utf-8') as f:
        json.dump(poles_map, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Configuration sauvegardée dans 'frontend/src/assets/poles_coordinates.json'")
    print(f"📊 {len(poles_map)} pôles territoriaux configurés avec coordonnées réelles du Sénégal")