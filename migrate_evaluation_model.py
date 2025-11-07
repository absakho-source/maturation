#!/usr/bin/env python3
"""
Migration: Mise à jour du modèle FicheEvaluation vers le format réel DGPPE
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Migre la base de données pour le nouveau modèle FicheEvaluation"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'backend', 'maturation.db')
    
    if not os.path.exists(db_path):
        print("❌ Base de données non trouvée")
        return False
    
    # Sauvegarder la base de données
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Sauvegarde créée: {backup_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Migration de la table fiche_evaluation...")
        
        # Vérifier si la table existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='fiche_evaluation'
        """)
        
        if cursor.fetchone():
            # Supprimer l'ancienne table
            cursor.execute("DROP TABLE fiche_evaluation")
            print("🗑️ Ancienne table supprimée")
        
        # Créer la nouvelle table avec le format réel
        cursor.execute("""
            CREATE TABLE fiche_evaluation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                evaluateur_nom VARCHAR(100) NOT NULL,
                date_evaluation DATETIME DEFAULT CURRENT_TIMESTAMP,
                reference_fiche VARCHAR(50) NOT NULL,
                
                -- II - RESULTATS DE L'EVALUATION
                pertinence_score INTEGER DEFAULT 0,
                pertinence_description TEXT,
                
                alignement_score INTEGER DEFAULT 0,
                alignement_description TEXT,
                
                activites_couts_score INTEGER DEFAULT 0,
                activites_couts_description TEXT,
                
                equite_score INTEGER DEFAULT 0,
                equite_description TEXT,
                
                viabilite_score INTEGER DEFAULT 0,
                viabilite_description TEXT,
                
                rentabilite_score INTEGER DEFAULT 0,
                rentabilite_description TEXT,
                
                benefices_strategiques_score INTEGER DEFAULT 0,
                benefices_strategiques_description TEXT,
                
                perennite_score INTEGER DEFAULT 0,
                perennite_description TEXT,
                
                avantages_intangibles_score INTEGER DEFAULT 0,
                avantages_intangibles_description TEXT,
                
                faisabilite_score INTEGER DEFAULT 0,
                faisabilite_description TEXT,
                
                ppp_score INTEGER DEFAULT 0,
                ppp_description TEXT,
                
                impact_environnemental_score INTEGER DEFAULT 0,
                impact_environnemental_description TEXT,
                
                impact_emploi_description TEXT,
                
                score_total INTEGER DEFAULT 0,
                
                -- III - CONCLUSION
                proposition VARCHAR(50),
                recommandations TEXT,
                
                -- Fichier PDF
                fichier_pdf VARCHAR(200),
                
                FOREIGN KEY (project_id) REFERENCES project (id)
            )
        """)
        
        print("✅ Nouvelle table fiche_evaluation créée avec le format réel DGPPE")
        
        # Vérifier la structure
        cursor.execute("PRAGMA table_info(fiche_evaluation)")
        colonnes = cursor.fetchall()
        
        print(f"📊 Table fiche_evaluation: {len(colonnes)} colonnes")
        for col in colonnes:
            print(f"   - {col[1]} ({col[2]})")
        
        conn.commit()
        conn.close()
        
        print("🎉 Migration terminée avec succès!")
        print("📋 Format conforme au formulaire réel DGPPE:")
        print("   • Section I: Présentation (pré-remplie automatiquement)")
        print("   • Section II: Résultats évaluation (12 critères avec scores)")
        print("   • Section III: Conclusion (proposition + recommandations)")
        print("   • Section IV: Documents annexes (évaluateur)")
        print("   • Score total sur 100 points")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        # Restaurer la sauvegarde en cas d'erreur
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, db_path)
            print("🔄 Base de données restaurée depuis la sauvegarde")
        return False

if __name__ == "__main__":
    print("🚀 Migration du modèle FicheEvaluation vers le format réel DGPPE")
    print("=" * 70)
    
    success = migrate_database()
    
    if success:
        print("\n✅ Migration réussie!")
        print("🔗 Vous pouvez maintenant utiliser l'évaluation détaillée:")
        print("   1. Aller sur la page /evaluateur")
        print("   2. Cliquer sur 'Fiche d'évaluation détaillée' pour un projet")
        print("   3. Remplir le formulaire conforme au format réel")
        print("   4. Générer le PDF au format officiel DGPPE")
    else:
        print("\n❌ Migration échouée")
        exit(1)