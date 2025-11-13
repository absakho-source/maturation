#!/usr/bin/env python3
"""
Script de migration pour corriger les projets qui ont une decision_finale
obsolète après avoir été revalidés par presidencesct.

Scénario: Un projet a été rejeté par presidencecomite (decision_finale='infirme'),
puis rejeté par presidencesct et réassigné, puis réévalué et revalidé par
presidencesct. Le projet devrait maintenant être dans le panier de
presidencecomite pour une nouvelle décision, mais l'ancienne decision_finale
l'en empêche.
"""

import sqlite3
import sys
from datetime import datetime

def fix_stale_decision_finale(db_path='maturation.db'):
    """
    Corrige les projets validés par presidencesct qui ont une decision_finale obsolète.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("=" * 70)
        print("CORRECTION DES decision_finale OBSOLÈTES")
        print("=" * 70)
        print()

        # Trouver les projets avec:
        # - statut = 'validé par presidencesct' (actuellement validé)
        # - avis_presidencesct = 'valide' (validé par présidence SCT)
        # - decision_finale n'est pas NULL (a une vieille décision)
        print("Recherche des projets concernés...")
        cursor.execute("""
            SELECT id, numero_projet, titre, statut, avis_presidencesct, decision_finale
            FROM project
            WHERE statut = 'validé par presidencesct'
            AND avis_presidencesct = 'valide'
            AND decision_finale IS NOT NULL
        """)
        projets = cursor.fetchall()

        if not projets:
            print("✓ Aucun projet trouvé avec decision_finale obsolète.")
            print("  Tous les projets sont dans le bon état.")
            conn.close()
            return

        print(f"\n✓ {len(projets)} projet(s) trouvé(s) avec decision_finale obsolète:")
        for p in projets:
            print(f"  - ID {p[0]}: {p[1]} - {p[2]}")
            print(f"    Statut: {p[3]} | avis_presidencesct: {p[4]} | decision_finale: {p[5]}")
        print()

        # Demander confirmation
        print("=" * 70)
        print(f"Ces projets devraient être dans le panier de presidencecomite")
        print(f"pour une NOUVELLE décision, mais leur ancienne decision_finale")
        print(f"les en empêche.")
        print("=" * 70)
        response = input("\nVoulez-vous réinitialiser leur decision_finale? (oui/non): ").strip().lower()

        if response not in ['oui', 'o', 'yes', 'y']:
            print("❌ Correction annulée par l'utilisateur")
            conn.close()
            return

        print()
        print("Correction en cours...")
        corrections = 0

        for projet in projets:
            projet_id = projet[0]
            numero = projet[1]
            old_decision = projet[5]

            # Réinitialiser decision_finale et commentaires_finaux
            cursor.execute("""
                UPDATE project
                SET decision_finale = NULL,
                    commentaires_finaux = NULL
                WHERE id = ?
            """, (projet_id,))

            # Ajouter une entrée dans l'historique
            cursor.execute("""
                INSERT INTO log (project_id, action, timestamp, auteur)
                VALUES (?, ?, ?, ?)
            """, (
                projet_id,
                f"Migration: Réinitialisation de decision_finale (ancienne valeur: '{old_decision}') pour permettre nouvelle décision du Comité",
                datetime.now().isoformat(),
                "system"
            ))

            corrections += 1
            print(f"  ✓ Corrigé: {numero} (decision_finale: '{old_decision}' → NULL)")

        # Valider les modifications
        conn.commit()

        print()
        print("=" * 70)
        print(f"✓ SUCCÈS: {corrections} projet(s) corrigé(s)")
        print("  Ces projets apparaîtront maintenant dans le panier de presidencecomite")
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

    fix_stale_decision_finale()
