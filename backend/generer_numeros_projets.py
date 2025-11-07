#!/usr/bin/env python3
"""
Script pour générer rétroactivement les numéros de projets pour les projets existants.
Usage: python generer_numeros_projets.py
"""

import os
import sys
from datetime import datetime

# Ajouter le répertoire backend au path pour importer app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Project

def generer_numero_retroactif(projet):
    """Génère un numéro de projet basé sur la date de soumission du projet"""
    if projet.date_soumission:
        date_ref = projet.date_soumission
    else:
        # Si pas de date de soumission, utiliser une date par défaut (début 2025)
        date_ref = datetime(2025, 1, 1)
    
    # Format année-mois
    prefix = date_ref.strftime("%Y%m")
    
    # Trouver le dernier numéro pour ce mois (en incluant les numéros déjà générés)
    existing_projects = Project.query.filter(
        Project.numero_projet.like(f"{prefix}%")
    ).order_by(Project.numero_projet.desc()).all()
    
    if existing_projects:
        # Extraire le numéro séquentiel le plus élevé
        max_number = 0
        for p in existing_projects:
            if p.numero_projet and len(p.numero_projet) >= 8:
                try:
                    number = int(p.numero_projet[-2:])
                    max_number = max(max_number, number)
                except (ValueError, IndexError):
                    pass
        next_number = max_number + 1
    else:
        next_number = 1
    
    # Assurer que le numéro reste sur 2 chiffres
    if next_number > 99:
        # Si on dépasse 99 pour un mois, utiliser le mois suivant
        if date_ref.month < 12:
            new_date = date_ref.replace(month=date_ref.month + 1)
        else:
            new_date = date_ref.replace(year=date_ref.year + 1, month=1)
        return generer_numero_retroactif_avec_date(new_date, 1)
    
    return f"{prefix}{next_number:02d}"

def generer_numero_retroactif_avec_date(date, numero):
    """Génère un numéro avec une date et numéro spécifiques"""
    prefix = date.strftime("%Y%m")
    return f"{prefix}{numero:02d}"

def main():
    with app.app_context():
        print("🔄 Génération des numéros de projets pour les projets existants...")
        
        # Récupérer tous les projets sans numéro
        projets_sans_numero = Project.query.filter(
            (Project.numero_projet == None) | (Project.numero_projet == "")
        ).order_by(Project.date_soumission.asc()).all()
        
        if not projets_sans_numero:
            print("✅ Tous les projets ont déjà un numéro.")
            return
        
        print(f"📋 {len(projets_sans_numero)} projets à traiter...")
        
        compteur = 0
        for projet in projets_sans_numero:
            try:
                nouveau_numero = generer_numero_retroactif(projet)
                projet.numero_projet = nouveau_numero
                compteur += 1
                
                date_str = projet.date_soumission.strftime("%Y-%m-%d") if projet.date_soumission else "N/A"
                print(f"✓ Projet ID {projet.id}: {nouveau_numero} (soumis le {date_str})")
                
            except Exception as e:
                print(f"❌ Erreur pour le projet ID {projet.id}: {e}")
        
        # Sauvegarder en base
        try:
            db.session.commit()
            print(f"💾 {compteur} numéros de projets générés avec succès!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de la sauvegarde: {e}")

if __name__ == "__main__":
    main()