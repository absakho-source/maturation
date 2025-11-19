#!/usr/bin/env python3
"""
Script de migration pour corriger le statut obsolète 'approuvé'

Le statut 'approuvé' était utilisé dans l'ancien workflow mais n'existe plus.
Avec le nouveau workflow, les projets approuvés ont :
- decision_finale = 'confirme'
- statut = 'décision finale confirmée'

Ce script corrige les projets ayant encore l'ancien statut.
"""
import sqlite3
import sys
from datetime import datetime

def migrate_database(db_path='projects.db'):
    """Corrige les statuts obsolètes 'approuvé' en 'décision finale confirmée'"""
    try:
        print(f"[MIGRATION] Connexion à la base de données: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Trouver tous les projets avec statut 'approuvé'
        cursor.execute("""
            SELECT id, numero_projet, titre, statut, decision_finale, avis_presidencesct
            FROM project
            WHERE statut = 'approuvé'
        """)

        projets_obsoletes = cursor.fetchall()

        if not projets_obsoletes:
            print("[MIGRATION] Aucun projet avec statut obsolète 'approuvé' trouvé")
            conn.close()
            return True

        print(f"[MIGRATION] {len(projets_obsoletes)} projet(s) à corriger trouvé(s)\n")

        for projet in projets_obsoletes:
            project_id, numero, titre, statut, decision_finale, avis_presidencesct = projet

            print(f"  Projet #{project_id} - {numero} - {titre}")
            print(f"    Statut actuel: {statut}")
            print(f"    decision_finale: {decision_finale}")
            print(f"    avis_presidencesct: {avis_presidencesct}")

            # Déterminer le nouveau statut correct
            nouveau_statut = None
            action_historique = None

            if decision_finale == 'confirme':
                # Projet avec décision finale confirmée
                nouveau_statut = 'décision finale confirmée'
                action_historique = "Migration: Correction statut 'approuvé' → 'décision finale confirmée'"
            elif decision_finale == 'infirme':
                # Projet avec décision finale infirmée (rejeté)
                nouveau_statut = 'décision finale confirmée'
                action_historique = "Migration: Correction statut 'approuvé' → 'décision finale confirmée' (décision infirmée)"
            elif avis_presidencesct == 'valide':
                # Projet validé par présidence SCT mais pas encore de décision finale
                nouveau_statut = 'validé par presidencesct'
                action_historique = "Migration: Correction statut 'approuvé' → 'validé par presidencesct' (en attente décision Comité)"
            else:
                # Cas par défaut : mettre en évalué
                nouveau_statut = 'évalué'
                action_historique = "Migration: Correction statut 'approuvé' → 'évalué' (nécessite réévaluation workflow)"

            print(f"    → Nouveau statut: {nouveau_statut}")

            # Mettre à jour le statut
            cursor.execute("""
                UPDATE project
                SET statut = ?
                WHERE id = ?
            """, (nouveau_statut, project_id))

            # Ajouter une entrée dans l'historique
            cursor.execute("""
                INSERT INTO historique (project_id, action, auteur, role, date)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, action_historique, 'system', 'admin', datetime.utcnow().isoformat()))

            print(f"    ✓ Statut corrigé\n")

        conn.commit()

        print(f"[MIGRATION] Migration terminée avec succès: {len(projets_obsoletes)} projet(s) corrigé(s)")

        # Vérification finale
        cursor.execute("SELECT COUNT(*) FROM project WHERE statut = 'approuvé'")
        count_remaining = cursor.fetchone()[0]

        if count_remaining > 0:
            print(f"[ATTENTION] Il reste encore {count_remaining} projet(s) avec statut 'approuvé'")
            return False
        else:
            print("[MIGRATION] ✓ Plus aucun projet avec statut 'approuvé'")

        conn.close()
        return True

    except Exception as e:
        print(f"[ERREUR] Migration échouée: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'projects.db'
    success = migrate_database(db_path)
    sys.exit(0 if success else 1)
