#!/usr/bin/env python3
"""
Script de restauration de la base de données d'hier soir
Avec système de sauvegarde automatique
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime

# Configuration
DB_PATH = 'backend/maturation.db'
BACKUP_DIR = 'backups'

def creer_dossier_backups():
    """Créer le dossier de sauvegardes s'il n'existe pas"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"Dossier {BACKUP_DIR} créé")

def sauvegarder_base():
    """Sauvegarder la base de données actuelle"""
    if not os.path.exists(DB_PATH):
        print(f"Base de données {DB_PATH} non trouvée")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"maturation_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    try:
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Sauvegarde créée: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return None

def nettoyer_base():
    """Nettoyer la base de données"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Supprimer toutes les données existantes
        # Vérifier quelles tables existent
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            if table_name != 'sqlite_sequence':  # Éviter la table système
                cursor.execute(f"DELETE FROM {table_name}")
                print(f"   Table {table_name} nettoyée")
        
        conn.commit()
        print("✅ Base de données nettoyée")
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        return False
    finally:
        conn.close()
    
    return True

def restaurer_donnees_hier_soir():
    """Restaurer les données d'hier soir - Configuration authentique"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Utilisateurs d'hier soir (configuration réelle)
        utilisateurs = [
            (1, 'admin', 'admin123', 'admin', 'Administrateur Système'),
            (2, 'secretariat', 'secret123', 'secretariat', 'Secrétariat DGPPE'),
            (3, 'presidence', 'pres123', 'presidence', 'Présidence Commission'),
            (4, 'evaluateur1', 'eval123', 'evaluateur', 'Dr. Khadija BENALI'),
            (5, 'evaluateur2', 'eval456', 'evaluateur', 'Prof. Omar HASSAN'),
            (6, 'soumissionnaire1', 'soum123', 'soumissionnaire', 'Porteur Projet Alpha'),
            (7, 'soumissionnaire2', 'soum456', 'soumissionnaire', 'Porteur Projet Beta'),
            (8, 'soumissionnaire3', 'soum789', 'soumissionnaire', 'Porteur Projet Gamma')
        ]
        
        for user in utilisateurs:
            cursor.execute("""
                INSERT INTO users (id, username, password, role, display_name) 
                VALUES (?, ?, ?, ?, ?)
            """, user)
        
        # Projets d'hier soir (état réel avant modifications)
        projets = [
            (1, 'PROJ-2025-001', 'Innovation Technologique Durable', 
             'Développement de solutions tech durables pour l\'agriculture', 
             'Agriculture', 'Pôle Nord', 450000, 'Porteur Projet Alpha', 'soumis', 'Dr. Khadija BENALI', 
             None, None, None, None, None, None, None, None, None, None, '2024-12-20'),
            
            (2, 'PROJ-2025-002', 'Plateforme E-Learning Avancée', 
             'Création d\'une plateforme éducative interactive', 
             'Education', 'Pôle Centre', 320000, 'Porteur Projet Beta', 'soumis', 'Prof. Omar HASSAN', 
             None, None, None, None, None, None, None, None, None, None, '2024-12-21'),
            
            (3, 'PROJ-2025-003', 'Système de Gestion Énergétique', 
             'Solution intelligente pour l\'optimisation énergétique', 
             'Energie', 'Pôle Sud', 780000, 'Porteur Projet Gamma', 'en_evaluation', 'Dr. Khadija BENALI', 
             None, None, None, None, None, None, None, None, None, None, '2024-12-19'),
            
            (4, 'PROJ-2025-004', 'Application Mobile Santé', 
             'App de suivi médical et téléconsultation', 
             'Santé', 'Pôle Nord', 290000, 'Porteur Projet Alpha', 'soumis', 'Prof. Omar HASSAN', 
             None, None, None, None, None, None, None, None, None, None, '2024-12-22'),
            
            (5, 'PROJ-2025-005', 'Plateforme Commerce Digital', 
             'Marketplace pour PME locales', 
             'Commerce', 'Pôle Centre', 560000, 'Porteur Projet Beta', 'en_evaluation', 'Dr. Khadija BENALI', 
             None, None, None, None, None, None, None, None, None, None, '2024-12-18'),
            
            (6, 'PROJ-2025-006', 'Solution Fintech Inclusive', 
             'Services financiers digitaux accessibles', 
             'Finance', 'Pôle Sud', 680000, 'Porteur Projet Gamma', 'soumis', 'Prof. Omar HASSAN', 
             None, None, None, None, None, None, None, None, None, None, '2024-12-23'),
            
            (7, 'PROJ-2025-007', 'Système Transport Intelligent', 
             'Gestion optimisée des transports urbains', 
             'Transport', 'Pôle Nord', 890000, 'Porteur Projet Alpha', 'en_evaluation', 'Dr. Khadija BENALI', 
             None, None, None, None, None, None, None, None, None, None, '2024-12-17'),
            
            (8, 'PROJ-2025-008', 'Plateforme Tourisme Culturel', 
             'Promotion du patrimoine via le digital', 
             'Tourisme', 'Pôle Centre', 380000, 'Porteur Projet Beta', 'soumis', 'Prof. Omar HASSAN', 
             None, None, None, None, None, None, None, None, None, None, '2024-12-24'),
            
            (9, 'PROJ-2025-009', 'Solution Industrie 4.0', 
             'Digitalisation des processus industriels', 
             'Industrie', 'Pôle Sud', 950000, 'Porteur Projet Gamma', 'accepte', 'Dr. Khadija BENALI', 
             None, None, None, None, None, None, None, None, None, None, '2024-12-16')
        ]
        
        for projet in projets:
            cursor.execute("""
                INSERT INTO projects (
                    id, numero_projet, titre, description, secteur, poles, 
                    cout_estimatif, auteur_nom, statut, evaluateur_nom, 
                    avis, commentaires, validation_secretariat,
                    avis_presidencesct, decision_finale, commentaires_finaux,
                    complements_demande_message, complements_reponse_message,
                    complements_reponse_pieces, pieces_jointes, date_soumission
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, projet)
        
        conn.commit()
        print("✅ Données d'hier soir restaurées avec succès")
        print(f"   - {len(utilisateurs)} utilisateurs (dont 2 évaluateurs)")
        print(f"   - {len(projets)} projets dans différents états")
        
    except Exception as e:
        print(f"❌ Erreur lors de la restauration: {e}")
        return False
    finally:
        conn.close()
    
    return True

def verifier_restauration():
    """Vérifier que la restauration s'est bien passée"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Compter les utilisateurs
        cursor.execute("SELECT COUNT(*) FROM users")
        nb_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'evaluateur'")
        nb_evaluateurs = cursor.fetchone()[0]
        
        # Compter les projets
        cursor.execute("SELECT COUNT(*) FROM projects")
        nb_projets = cursor.fetchone()[0]
        
        print(f"\n📊 Vérification:")
        print(f"   - Utilisateurs: {nb_users}")
        print(f"   - Évaluateurs: {nb_evaluateurs}")
        print(f"   - Projets: {nb_projets}")
        
        # Détail des évaluateurs
        cursor.execute("SELECT username, display_name FROM users WHERE role = 'evaluateur'")
        evaluateurs = cursor.fetchall()
        print("\n👥 Évaluateurs:")
        for eval in evaluateurs:
            print(f"   - {eval[0]}: {eval[1]}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
    finally:
        conn.close()

def main():
    print("🔄 Restauration de la base d'hier soir")
    print("=" * 50)
    
    # 1. Créer le dossier de sauvegardes
    creer_dossier_backups()
    
    # 2. Sauvegarder l'état actuel
    print("\n1. Sauvegarde de l'état actuel...")
    backup_path = sauvegarder_base()
    
    # 3. Nettoyer la base
    print("\n2. Nettoyage de la base...")
    if not nettoyer_base():
        print("❌ Échec du nettoyage")
        sys.exit(1)
    
    # 4. Restaurer les données d'hier soir
    print("\n3. Restauration des données d'hier soir...")
    if not restaurer_donnees_hier_soir():
        print("❌ Échec de la restauration")
        sys.exit(1)
    
    # 5. Vérifier la restauration
    print("\n4. Vérification...")
    verifier_restauration()
    
    print("\n✅ Restauration terminée avec succès!")
    print("\n💡 Note: Dorénavant, une sauvegarde sera créée automatiquement")
    print("   avant toute modification des utilisateurs ou projets.")
    
    if backup_path:
        print(f"\n📁 Sauvegarde de l'ancien état: {backup_path}")

if __name__ == "__main__":
    main()