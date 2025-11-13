#!/usr/bin/env python3
"""
Script de migration pour corriger le statut des projets rejetés.
Les projets qui ont été rejetés par Présidence SCT ou Présidence Comité
mais qui ont encore le statut 'soumis' seront mis à jour vers 'rejeté'.
"""

import sqlite3
import sys
from datetime import datetime

def fix_rejected_status(db_path='maturation.db'):
    """
    Corrige le statut des projets rejetés qui ont encore le statut 'soumis'.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("=" * 70)
        print("CORRECTION DU STATUT DES PROJETS REJETÉS")
        print("=" * 70)
        print()

        # 1. Trouver les projets avec avis_presidencesct = 'non' et statut = 'soumis'
        print("1. Recherche des projets rejetés par Présidence SCT...")
        cursor.execute("""
            SELECT id, numero_projet, titre, statut, avis_presidencesct
            FROM project
            WHERE avis_presidencesct = 'non' AND statut = 'soumis'
        """)
        projets_presidencesct = cursor.fetchall()

        if projets_presidencesct:
            print(f"   ✓ {len(projets_presidencesct)} projet(s) trouvé(s):")
            for p in projets_presidencesct:
                print(f"     - ID {p[0]}: {p[1]} - {p[2]}")
        else:
            print("   ✓ Aucun projet trouvé")
        print()

        # 2. Trouver les projets avec decision_finale = 'non' et statut = 'soumis'
        print("2. Recherche des projets rejetés par Présidence Comité...")
        cursor.execute("""
            SELECT id, numero_projet, titre, statut, decision_finale
            FROM project
            WHERE decision_finale = 'non' AND statut = 'soumis'
        """)
        projets_presidencecomite = cursor.fetchall()

        if projets_presidencecomite:
            print(f"   ✓ {len(projets_presidencecomite)} projet(s) trouvé(s):")
            for p in projets_presidencecomite:
                print(f"     - ID {p[0]}: {p[1]} - {p[2]}")
        else:
            print("   ✓ Aucun projet trouvé")
        print()

        total_projets = len(projets_presidencesct) + len(projets_presidencecomite)

        if total_projets == 0:
            print("✓ Aucune correction nécessaire. Tous les projets ont le bon statut.")
            conn.close()
            return

        # Demander confirmation
        print("=" * 70)
        print(f"TOTAL: {total_projets} projet(s) à corriger")
        print("=" * 70)
        response = input("\nVoulez-vous procéder à la correction? (oui/non): ").strip().lower()

        if response not in ['oui', 'o', 'yes', 'y']:
            print("❌ Correction annulée par l'utilisateur")
            conn.close()
            return

        print()
        print("3. Correction en cours...")
        corrections = 0

        # Corriger les projets rejetés par Présidence SCT
        for projet in projets_presidencesct:
            projet_id = projet[0]
            numero = projet[1]

            # Mettre à jour le statut
            cursor.execute("""
                UPDATE project
                SET statut = 'rejeté'
                WHERE id = ?
            """, (projet_id,))

            # Ajouter une entrée dans l'historique
            cursor.execute("""
                INSERT INTO log (project_id, action, timestamp, auteur)
                VALUES (?, ?, ?, ?)
            """, (
                projet_id,
                "Migration: Statut corrigé de 'soumis' à 'rejeté' (rejet par Présidence SCT)",
                datetime.now().isoformat(),
                "system"
            ))

            corrections += 1
            print(f"   ✓ Corrigé: {numero}")

        # Corriger les projets rejetés par Présidence Comité
        for projet in projets_presidencecomite:
            projet_id = projet[0]
            numero = projet[1]

            # Mettre à jour le statut
            cursor.execute("""
                UPDATE project
                SET statut = 'rejeté'
                WHERE id = ?
            """, (projet_id,))

            # Ajouter une entrée dans l'historique
            cursor.execute("""
                INSERT INTO log (project_id, action, timestamp, auteur)
                VALUES (?, ?, ?, ?)
            """, (
                projet_id,
                "Migration: Statut corrigé de 'soumis' à 'rejeté' (rejet par Présidence Comité)",
                datetime.now().isoformat(),
                "system"
            ))

            corrections += 1
            print(f"   ✓ Corrigé: {numero}")

        # Valider les modifications
        conn.commit()

        print()
        print("=" * 70)
        print(f"✓ SUCCÈS: {corrections} projet(s) corrigé(s)")
        print("=" * 70)

        conn.close()

    except sqlite3.Error as e:
        print(f"❌ Erreur de base de données: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    import os

    # Vérifier si on est dans le bon répertoire
    if not os.path.exists('maturation.db'):
        print("❌ Erreur: Le fichier maturation.db n'a pas été trouvé.", file=sys.stderr)
        print("   Veuillez exécuter ce script depuis le répertoire backend/", file=sys.stderr)
        sys.exit(1)

    fix_rejected_status()
