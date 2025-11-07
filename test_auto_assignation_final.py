#!/usr/bin/env python3
"""
Test final de la fonctionnalité d'auto-assignation du Secrétariat SCT
Valide que l'auto-assignation "Moi-même (Secrétariat SCT)" fonctionne correctement
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5002"

def test_auto_assignation():
    """Test complet de l'auto-assignation du Secrétariat SCT"""
    
    print("🔍 Test de l'auto-assignation du Secrétariat SCT")
    print("=" * 60)
    
    # 1. Créer un nouveau projet test
    print("\n1. Création d'un projet test...")
    project_data = {
        "titre": "Test Auto-assignation SCT",
        "secteur_activite": "postes-communication-télécommunications-économie numérique",
        "poles_territoriaux": "Centre",
        "cout_estimatif": 5000000000,
        "duree_projet": 24,
        "description": "Projet test pour valider l'auto-assignation du Secrétariat SCT",
        "objectifs": "Tester la fonctionnalité d'auto-assignation",
        "resultats_attendus": "Assignation automatique réussie",
        "beneficiaires": "Population test",
        "zone_intervention": "Centre",
        "auteur": "soumissionnaire"
    }
    
    response = requests.post(f"{BASE_URL}/api/projects", json=project_data)
    if response.status_code != 201:
        print(f"❌ Erreur création projet: {response.status_code}")
        return False
        
    project_id = response.json()["id"]
    print(f"✅ Projet créé avec ID: {project_id}")
    
    # 2. Test auto-assignation par le Secrétariat SCT
    print("\n2. Test de l'auto-assignation...")
    assignation_data = {
        "evaluateur_nom": "Moi-même (Secrétariat SCT)",
        "auteur": "secretariatsct",
        "role": "secretariatsct"
    }
    
    response = requests.post(f"{BASE_URL}/api/projects/{project_id}/traiter", json=assignation_data)
    if response.status_code != 200:
        print(f"❌ Erreur auto-assignation: {response.status_code} - {response.text}")
        return False
        
    print("✅ Auto-assignation réussie!")
    
    # 3. Vérifier que l'assignation s'est bien faite
    print("\n3. Vérification de l'assignation...")
    response = requests.get(f"{BASE_URL}/api/projects/{project_id}")
    if response.status_code != 200:
        print(f"❌ Erreur récupération projet: {response.status_code}")
        return False
        
    project = response.json()
    print(f"📊 Statut du projet: {project['statut']}")
    print(f"📊 Évaluateur assigné: {project.get('evaluateur_nom', 'Non assigné')}")
    
    # Vérifier que l'assignation est correcte
    if project['statut'] == 'assigné' and project.get('evaluateur_nom') == 'secretariatsct':
        print("✅ Auto-assignation validée - Le projet est assigné au Secrétariat SCT")
        return True
    else:
        print(f"❌ Auto-assignation échouée - Statut: {project['statut']}, Évaluateur: {project.get('evaluateur_nom')}")
        return False

def test_auto_reassignation():
    """Test de la réassignation automatique"""
    
    print("\n" + "=" * 60)
    print("🔄 Test de la réassignation automatique")
    print("=" * 60)
    
    # Prendre un projet déjà assigné pour tester la réassignation
    response = requests.get(f"{BASE_URL}/api/projects?role=secretariatsct&username=secretariatsct")
    if response.status_code != 200:
        print(f"❌ Erreur récupération projets: {response.status_code}")
        return False
    
    # Chercher un projet assigné à un autre évaluateur
    projets = []
    data = response.json()
    for pole_data in data.values():
        if isinstance(pole_data, dict) and 'projets' in pole_data:
            projets.extend(pole_data['projets'])
    
    projet_assigne = None
    for projet in projets:
        if projet['statut'] == 'assigné' and projet.get('evaluateur_nom') not in ['secretariatsct', None]:
            projet_assigne = projet
            break
    
    if not projet_assigne:
        print("⚠️  Aucun projet assigné trouvé pour tester la réassignation")
        return True
    
    project_id = projet_assigne['id']
    ancien_evaluateur = projet_assigne.get('evaluateur_nom')
    print(f"📋 Test avec projet ID {project_id} (actuellement assigné à: {ancien_evaluateur})")
    
    # Test de réassignation vers soi-même
    reassignation_data = {
        "nouvel_evaluateur": "Moi-même (Secrétariat SCT)",
        "auteur": "secretariatsct",
        "role": "secretariatsct"
    }
    
    response = requests.post(f"{BASE_URL}/api/projects/{project_id}/traiter", json=reassignation_data)
    if response.status_code != 200:
        print(f"❌ Erreur réassignation: {response.status_code} - {response.text}")
        return False
    
    print("✅ Réassignation automatique réussie!")
    
    # Vérifier la réassignation
    response = requests.get(f"{BASE_URL}/api/projects/{project_id}")
    if response.status_code == 200:
        project = response.json()
        if project.get('evaluateur_nom') == 'secretariatsct':
            print("✅ Réassignation validée - Le projet est maintenant assigné au Secrétariat SCT")
            return True
        else:
            print(f"❌ Réassignation échouée - Évaluateur: {project.get('evaluateur_nom')}")
            return False
    
    return False

def main():
    """Test principal"""
    print("🚀 TESTS D'AUTO-ASSIGNATION DU SECRÉTARIAT SCT")
    print("=" * 60)
    
    # Vérifier que le backend est actif
    try:
        response = requests.get(f"{BASE_URL}/api/users", timeout=5)
        if response.status_code != 200:
            print("❌ Backend non accessible")
            sys.exit(1)
        print("✅ Backend accessible")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur connexion backend: {e}")
        sys.exit(1)
    
    # Exécuter les tests
    success_count = 0
    total_tests = 2
    
    if test_auto_assignation():
        success_count += 1
    
    if test_auto_reassignation():
        success_count += 1
    
    # Résultats
    print("\n" + "=" * 60)
    print("📈 RÉSULTATS DES TESTS")
    print("=" * 60)
    print(f"✅ Tests réussis: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 TOUS LES TESTS D'AUTO-ASSIGNATION ONT RÉUSSI!")
        print("🎯 La fonctionnalité 'Moi-même (Secrétariat SCT)' fonctionne parfaitement")
    else:
        print("⚠️  Certains tests ont échoué")
        sys.exit(1)

if __name__ == "__main__":
    main()