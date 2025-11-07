#!/usr/bin/env python3
"""
Test de la réassignation d'un projet rejeté avec préservation de l'historique
"""
import requests
import json
import sqlite3

def test_reassignation():
    print("🧪 TEST : Réassignation projet rejeté avec préservation historique")
    print("=" * 60)
    
    # Vérifier l'état avant réassignation
    print("\n1️⃣ AVANT RÉASSIGNATION :")
    conn = sqlite3.connect('backend/maturation.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, titre, statut, avis, commentaires, decision_finale, 
               commentaires_finaux, evaluateur_nom 
        FROM projects WHERE id=1
    """)
    before = cursor.fetchone()
    print(f"   Statut: {before[2]}")
    print(f"   Avis précédent: {before[3]}")
    print(f"   Commentaires: {before[4]}")
    print(f"   Décision finale: {before[5]}")
    print(f"   Motifs de rejet: {before[6]}")
    print(f"   Évaluateur actuel: {before[7]}")
    
    # Test de la réassignation via API
    print("\n2️⃣ RÉASSIGNATION VIA API :")
    url = "http://127.0.0.1:5002/api/projects/1/traiter"
    data = {
        "evaluateur_nom": "evaluateur1",
        "statut_action": "reassigner_rejete",
        "auteur": "secretariatsct",
        "role": "secretariatsct"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"   Status code: {response.status_code}")
        print(f"   Réponse: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Réassignation réussie !")
        else:
            print("   ❌ Erreur lors de la réassignation")
            return
            
    except Exception as e:
        print(f"   ❌ Erreur de connexion: {e}")
        return
    
    # Vérifier l'état après réassignation
    print("\n3️⃣ APRÈS RÉASSIGNATION :")
    cursor.execute("""
        SELECT id, titre, statut, avis, commentaires, decision_finale, 
               commentaires_finaux, evaluateur_nom 
        FROM projects WHERE id=1
    """)
    after = cursor.fetchone()
    print(f"   Nouveau statut: {after[2]}")
    print(f"   Avis préservé: {after[3]}")
    print(f"   Commentaires préservés: {after[4]}")
    print(f"   Décision finale préservée: {after[5]}")
    print(f"   Motifs de rejet préservés: {after[6]}")
    print(f"   Nouvel évaluateur: {after[7]}")
    
    # Validation du test
    print("\n4️⃣ VALIDATION :")
    success = True
    
    if after[2] != "assigné":
        print("   ❌ Le statut devrait être 'assigné'")
        success = False
    else:
        print("   ✅ Statut correctement mis à jour")
    
    if after[7] != "evaluateur1":
        print("   ❌ L'évaluateur devrait être 'evaluateur1'")
        success = False
    else:
        print("   ✅ Évaluateur correctement assigné")
    
    if after[3] != before[3]:
        print("   ❌ L'avis précédent n'a pas été préservé")
        success = False
    else:
        print("   ✅ Avis précédent préservé")
    
    if after[5] != before[5]:
        print("   ❌ La décision finale n'a pas été préservée")
        success = False
    else:
        print("   ✅ Décision finale préservée")
    
    if success:
        print("\n🎉 TEST RÉUSSI : Historique préservé, projet réassigné !")
    else:
        print("\n❌ TEST ÉCHOUÉ : Problèmes détectés")
    
    conn.close()
    return success

if __name__ == "__main__":
    test_reassignation()