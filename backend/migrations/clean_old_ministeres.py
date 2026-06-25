"""
Script pour supprimer les anciens ministères qui ne sont pas dans la liste 2025
"""
import sqlite3
import sys
import os

# Chemin vers la base de données
db_path = os.path.join(os.path.dirname(__file__), 'maturation.db')

# Liste officielle des ministères 2025
MINISTERES_2025 = [
    "Ministère de la Justice",
    "Ministère de l'Énergie, du Pétrole et des Mines",
    "Ministère de l'Intégration Africaine, des Affaires étrangères et des Sénégalais de l'Extérieur",
    "Ministère des Forces Armées",
    "Ministère de l'Intérieur et de la Sécurité publique",
    "Ministère de l'Économie, des Finances et du Plan",
    "Ministère des Finances et du Budget",
    "Ministère de l'Enseignement supérieur, de la Recherche et de l'Innovation",
    "Ministère des Transports Terrestres et Aériens",
    "Ministère de la Communication, des Télécommunications et du Numérique",
    "Ministère de l'Éducation Nationale",
    "Ministère de l'Agriculture, de la Souveraineté Alimentaire et de l'Élevage",
    "Ministère de l'Hydraulique et de l'Assainissement",
    "Ministère de la Santé et de l'Hygiène Publique",
    "Ministère de la Famille, de l'Action sociale et des Solidarités",
    "Ministère de l'Emploi et de la Formation Professionnelle et Technique",
    "Ministère de l'Environnement et de la Transition Écologique",
    "Ministère de l'Urbanisme, des Collectivités territoriales et de l'Aménagement des Territoires",
    "Ministère de l'Industrie et du Commerce",
    "Ministère des Pêches et de l'Économie Maritime",
    "Ministère de la Fonction Publique, du Travail et de la Réforme du Service Public",
    "Ministère de la Jeunesse et des Sports",
    "Ministère de la Microfinance et de l'Économie Sociale et Solidaire",
    "Ministère des Infrastructures",
    "Ministère de la Culture, de l'Artisanat et du Tourisme"
]

def clean_old_ministeres():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("=" * 80)
        print("NETTOYAGE DES ANCIENS MINISTÈRES")
        print("=" * 80)

        # 1. Récupérer tous les ministères actuels
        cursor.execute("SELECT id, nom_complet, actif FROM ministere")
        tous_ministeres = cursor.fetchall()

        print(f"\n📊 Total de ministères dans la base: {len(tous_ministeres)}")

        # 2. Identifier ceux à supprimer
        to_delete = []
        to_keep = []

        for mid, nom, actif in tous_ministeres:
            if nom in MINISTERES_2025:
                to_keep.append((mid, nom))
            else:
                to_delete.append((mid, nom))

        print(f"✓ Ministères à conserver: {len(to_keep)}")
        print(f"✗ Ministères à supprimer: {len(to_delete)}")

        if to_delete:
            print(f"\n📋 Ministères qui seront supprimés:")
            print("-" * 80)
            for mid, nom in to_delete:
                print(f"  ✗ {nom}")

            # 3. Supprimer les anciens ministères
            ids_to_delete = [str(mid) for mid, _ in to_delete]
            placeholders = ','.join(['?' for _ in ids_to_delete])
            cursor.execute(f"DELETE FROM ministere WHERE id IN ({placeholders})", ids_to_delete)

            conn.commit()
            print(f"\n✅ {len(to_delete)} ministères supprimés")

        # 4. Afficher la liste finale
        cursor.execute("SELECT id, nom_complet, ordre FROM ministere WHERE actif = 1 ORDER BY ordre")
        ministeres_finaux = cursor.fetchall()

        print(f"\n📋 Liste finale ({len(ministeres_finaux)} ministères actifs):")
        print("-" * 80)
        for mid, nom, ordre in ministeres_finaux:
            print(f"✓ {ordre:2d}. {nom}")

        return True

    except sqlite3.Error as e:
        print(f"❌ Erreur SQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = clean_old_ministeres()
    sys.exit(0 if success else 1)
