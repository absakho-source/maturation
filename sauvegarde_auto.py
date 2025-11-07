#!/usr/bin/env python3
"""
Système de sauvegarde automatique de la base de données
À utiliser avant toute modification des utilisateurs ou projets
"""

import os
import shutil
from datetime import datetime
import sqlite3

# Configuration
DB_PATH = 'maturation.db'
BACKUP_DIR = 'backups'
MAX_BACKUPS = 20  # Garder maximum 20 sauvegardes

def creer_sauvegarde_automatique(description="modification"):
    """Créer une sauvegarde automatique avec description"""
    
    # Créer le dossier si nécessaire
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Base de données {DB_PATH} non trouvée")
        return None
    
    # Générer le nom du fichier
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"auto_backup_{timestamp}_{description.replace(' ', '_')}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    try:
        # Copier la base
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Sauvegarde automatique créée: {backup_filename}")
        
        # Nettoyer les anciennes sauvegardes
        nettoyer_anciennes_sauvegardes()
        
        return backup_path
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde automatique: {e}")
        return None

def nettoyer_anciennes_sauvegardes():
    """Supprimer les anciennes sauvegardes pour éviter l'accumulation"""
    try:
        # Lister tous les fichiers de sauvegarde
        backups = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith(('auto_backup_', 'maturation_backup_')) and filename.endswith('.db'):
                filepath = os.path.join(BACKUP_DIR, filename)
                mtime = os.path.getmtime(filepath)
                backups.append((filepath, mtime, filename))
        
        # Trier par date de modification (plus récent en premier)
        backups.sort(key=lambda x: x[1], reverse=True)
        
        # Supprimer les plus anciennes si on dépasse la limite
        if len(backups) > MAX_BACKUPS:
            for filepath, _, filename in backups[MAX_BACKUPS:]:
                os.remove(filepath)
                print(f"🗑️  Ancienne sauvegarde supprimée: {filename}")
                
    except Exception as e:
        print(f"⚠️  Erreur lors du nettoyage des sauvegardes: {e}")

def lister_sauvegardes():
    """Lister toutes les sauvegardes disponibles"""
    if not os.path.exists(BACKUP_DIR):
        print("Aucun dossier de sauvegarde trouvé")
        return
    
    backups = []
    for filename in os.listdir(BACKUP_DIR):
        if filename.endswith('.db'):
            filepath = os.path.join(BACKUP_DIR, filename)
            mtime = os.path.getmtime(filepath)
            size = os.path.getsize(filepath)
            backups.append((filename, mtime, size))
    
    if not backups:
        print("Aucune sauvegarde trouvée")
        return
    
    # Trier par date (plus récent en premier)
    backups.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n📁 Sauvegardes disponibles ({len(backups)}):")
    print("-" * 60)
    for filename, mtime, size in backups:
        date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        size_mb = size / 1024 / 1024
        print(f"{filename} - {date_str} ({size_mb:.2f} MB)")

def restaurer_sauvegarde(backup_filename):
    """Restaurer une sauvegarde spécifique"""
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    if not os.path.exists(backup_path):
        print(f"❌ Sauvegarde {backup_filename} non trouvée")
        return False
    
    try:
        # Sauvegarder l'état actuel avant restauration
        creer_sauvegarde_automatique("avant_restauration")
        
        # Restaurer la sauvegarde
        shutil.copy2(backup_path, DB_PATH)
        print(f"✅ Sauvegarde {backup_filename} restaurée")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la restauration: {e}")
        return False

def verifier_etat_base():
    """Vérifier l'état actuel de la base"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM user")
        nb_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user WHERE role = 'evaluateur'")
        nb_evaluateurs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM project")
        nb_projets = cursor.fetchone()[0]
        
        print(f"\n📊 État actuel de la base:")
        print(f"   - Utilisateurs: {nb_users}")
        print(f"   - Évaluateurs: {nb_evaluateurs}")
        print(f"   - Projets: {nb_projets}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python sauvegarde_auto.py backup [description]  - Créer une sauvegarde")
        print("  python sauvegarde_auto.py list                  - Lister les sauvegardes")
        print("  python sauvegarde_auto.py restore <filename>    - Restaurer une sauvegarde")
        print("  python sauvegarde_auto.py status                - Vérifier l'état de la base")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "backup":
        description = sys.argv[2] if len(sys.argv) > 2 else "manuelle"
        creer_sauvegarde_automatique(description)
        
    elif command == "list":
        lister_sauvegardes()
        
    elif command == "restore":
        if len(sys.argv) < 3:
            print("❌ Nom du fichier de sauvegarde requis")
            sys.exit(1)
        restaurer_sauvegarde(sys.argv[2])
        
    elif command == "status":
        verifier_etat_base()
        
    else:
        print(f"❌ Commande inconnue: {command}")
        sys.exit(1)