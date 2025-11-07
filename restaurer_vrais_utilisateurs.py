#!/usr/bin/env python3
"""
Restauration des VRAIS utilisateurs que vous aviez ce matin
Les 7 utilisateurs exacts : CT DGPPE, presidencecomite, presidencesct, secretariatsct, soumissionnaire, evaluateur1, evaluateur2
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime

# Configuration
DB_PATH = 'backend/maturation.db'
BACKUP_DIR = 'backups'

def sauvegarder_base():
    """Sauvegarder la base de données actuelle"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    if not os.path.exists(DB_PATH):
        print(f"Base de données {DB_PATH} non trouvée")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"avant_vrais_utilisateurs_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    try:
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Sauvegarde créée: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return None

def restaurer_vrais_utilisateurs():
    """Restaurer les 7 VRAIS utilisateurs que vous aviez"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Nettoyer les utilisateurs existants
        cursor.execute("DELETE FROM users")
        
        # Les 7 VRAIS utilisateurs exacts
        vrais_utilisateurs = [
            (1, 'admin', 'admin123', 'admin', 'CT DGPPE'),
            (2, 'presidencecomite', 'comite123', 'presidencecomite', 'Présidence du Comité'),
            (3, 'presidencesct', 'presid123', 'presidencesct', 'Présidence SCT'),
            (4, 'secretariatsct', 'secret123', 'secretariatsct', 'Secrétariat SCT'),
            (5, 'soumissionnaire', 'soum123', 'soumissionnaire', 'Soumissionnaire'),
            (6, 'evaluateur1', 'eval123', 'evaluateur', 'Évaluateur 1'),
            (7, 'evaluateur2', 'eval456', 'evaluateur', 'Évaluateur 2')
        ]
        
        for user in vrais_utilisateurs:
            cursor.execute("""
                INSERT INTO users (id, username, password, role, display_name) 
                VALUES (?, ?, ?, ?, ?)
            """, user)
        
        conn.commit()
        print("✅ VRAIS utilisateurs restaurés avec succès")
        print(f"   - {len(vrais_utilisateurs)} utilisateurs exactement comme vous les aviez")
        
    except Exception as e:
        print(f"❌ Erreur lors de la restauration: {e}")
        return False
    finally:
        conn.close()
    
    return True

def verifier_restauration():
    """Vérifier que les vrais utilisateurs sont bien là"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Compter les utilisateurs
        cursor.execute("SELECT COUNT(*) FROM users")
        nb_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'evaluateur'")
        nb_evaluateurs = cursor.fetchone()[0]
        
        print(f"\n📊 Vérification:")
        print(f"   - Utilisateurs: {nb_users} (attendu: 7)")
        print(f"   - Évaluateurs: {nb_evaluateurs} (attendu: 2)")
        
        # Liste complète
        cursor.execute("SELECT username, display_name, role FROM users ORDER BY id")
        utilisateurs = cursor.fetchall()
        print("\n👥 Utilisateurs restaurés:")
        for user in utilisateurs:
            print(f"   - {user[0]}: {user[1]} ({user[2]})")
            
        # Vérifier que ce sont bien les 7 exacts
        usernames_attendus = {'admin', 'presidencecomite', 'presidencesct', 'secretariatsct', 'soumissionnaire', 'evaluateur1', 'evaluateur2'}
        usernames_presents = {user[0] for user in utilisateurs}
        
        if usernames_attendus == usernames_presents:
            print("\n✅ PARFAIT! Ce sont exactement les 7 utilisateurs que vous aviez")
        else:
            print(f"\n⚠️  Différence détectée:")
            print(f"   Attendus: {usernames_attendus}")
            print(f"   Présents: {usernames_presents}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
    finally:
        conn.close()

def main():
    print("🔄 Restauration des VRAIS utilisateurs")
    print("=" * 50)
    print("Les 7 utilisateurs exacts que vous aviez:")
    print("1. admin (CT DGPPE)")
    print("2. presidencecomite")
    print("3. presidencesct") 
    print("4. secretariatsct")
    print("5. soumissionnaire")
    print("6. evaluateur1")
    print("7. evaluateur2")
    print()
    
    # 1. Sauvegarder l'état actuel
    print("1. Sauvegarde de l'état actuel...")
    backup_path = sauvegarder_base()
    
    # 2. Restaurer les vrais utilisateurs
    print("\n2. Restauration des vrais utilisateurs...")
    if not restaurer_vrais_utilisateurs():
        print("❌ Échec de la restauration")
        sys.exit(1)
    
    # 3. Vérifier la restauration
    print("\n3. Vérification...")
    verifier_restauration()
    
    print("\n✅ Restauration terminée!")
    print("Vous devriez maintenant retrouver vos 7 utilisateurs exacts.")
    
    if backup_path:
        print(f"\n📁 Sauvegarde de l'ancien état: {backup_path}")

if __name__ == "__main__":
    main()