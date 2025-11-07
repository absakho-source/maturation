#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour vérifier et corriger les assignations de pôles territoriaux
"""

import sqlite3
import json
import re

# Mapping des régions vers les pôles territoriaux
regions_per_pole = {
    'Dakar': ['DAKAR', 'PIKINE', 'GUEDIAWAYE', 'RUFISQUE'],
    'Thiès': ['THIES', 'MBOUR', 'TIVAOUANE'],
    'Diourbel-Louga': ['DIOURBEL', 'BAMBEY', 'MBACKE', 'LOUGA', 'KEBEMER', 'LINGUERE'],
    'Centre': ['KAOLACK', 'NIORO DU RIP', 'GUINGUINEO', 'FATICK', 'FOUNDIOUGNE', 'GOSSAS', 'KAFFRINE', 'BIRKELANE', 'KOUNGHEUL', 'MALEM HODAR'],
    'Sud': ['ZIGUINCHOR', 'OUSSOUYE', 'BIGNONA', 'KOLDA', 'VELINGARA', 'MEDINA YORO FOULAH', 'SEDHIOU', 'BOUNKILING', 'GOUDOMP'],
    'Nord': ['SAINT-LOUIS', 'DAGANA', 'PODOR'],
    'Nord-Est': ['MATAM', 'KANEL', 'RANEROU', 'TAMBACOUNDA', 'BAKEL', 'GOUDIRY', 'KOUMPENTOUM', 'KEDOUGOU', 'SALEMATA', 'SARAYA']
}

# Créer un mapping inverse : région -> pôle
region_to_pole = {}
for pole, regions in regions_per_pole.items():
    for region in regions:
        region_to_pole[region.upper()] = pole

def extraire_region_du_titre(titre):
    """Extraire la région probable du titre du projet"""
    titre_upper = titre.upper()
    
    # Rechercher des mots-clés de régions dans le titre
    for region in region_to_pole.keys():
        if region in titre_upper:
            return region
    
    # Rechercher des variantes communes
    variantes = {
        'SAINT LOUIS': 'SAINT-LOUIS',
        'ST LOUIS': 'SAINT-LOUIS',
        'SAINT-LOUIS': 'SAINT-LOUIS',
        'TAMBACOUNDA': 'TAMBACOUNDA',
        'TAMBA': 'TAMBACOUNDA',
        'KEDOUGOU': 'KEDOUGOU',
        'KÉDOUGOU': 'KEDOUGOU'
    }
    
    for variante, region_officielle in variantes.items():
        if variante in titre_upper:
            return region_officielle
            
    return None

def verifier_assignations():
    """Vérifier toutes les assignations de pôles"""
    conn = sqlite3.connect('backend/maturation.db')
    cursor = conn.cursor()
    
    # Récupérer tous les projets
    cursor.execute("SELECT id, titre, poles FROM projects")
    projets = cursor.fetchall()
    
    corrections = []
    
    print("=== Vérification des assignations de pôles ===\n")
    
    for projet_id, titre, pole_actuel in projets:
        region_detectee = extraire_region_du_titre(titre)
        
        if region_detectee:
            pole_attendu = region_to_pole[region_detectee]
            
            if pole_attendu != pole_actuel:
                print(f"❌ ERREUR - Projet {projet_id}: '{titre[:60]}...'")
                print(f"   Région détectée: {region_detectee}")
                print(f"   Pôle actuel: {pole_actuel}")
                print(f"   Pôle attendu: {pole_attendu}")
                print()
                
                corrections.append({
                    'id': projet_id,
                    'titre': titre,
                    'pole_actuel': pole_actuel,
                    'pole_attendu': pole_attendu,
                    'region': region_detectee
                })
            else:
                print(f"✅ OK - Projet {projet_id}: {region_detectee} → {pole_actuel}")
        else:
            print(f"⚠️  INDÉTERMINÉ - Projet {projet_id}: '{titre[:60]}...' (pôle: {pole_actuel})")
    
    print(f"\n=== Résumé ===")
    print(f"Total projets: {len(projets)}")
    print(f"Corrections nécessaires: {len(corrections)}")
    
    if corrections:
        print(f"\n=== Corrections à appliquer ===")
        for correction in corrections:
            print(f"UPDATE projects SET poles='{correction['pole_attendu']}' WHERE id={correction['id']};")
    
    conn.close()
    return corrections

if __name__ == "__main__":
    corrections = verifier_assignations()