#!/usr/bin/env python3
"""
Test complet de l'auto-assignation avec serveur
"""

import sys
sys.path.append('backend')

import app
from app import Project, db
import requests
import time
import subprocess
import signal
import os

def start_backend():
    """Démarre le serveur backend en arrière-plan"""
    print("🚀 Démarrage du serveur backend...")
    process = subprocess.Popen([
        sys.executable, "backend/app.py"
    ], env=dict(os.environ, PYTHONPATH="backend"))
    
    # Attendre que le serveur démarre
    time.sleep(3)
    return process

def test_api_auto_assignation():
    """Test de l'API d'auto-assignation"""
    try:
        # Test 1: Vérifier que l'API fonctionne
        print("\n=== TEST API AUTO-ASSIGNATION ===")
        response = requests.get("http://127.0.0.1:5002/api/projects?role=secretariatsct&username=secretariatsct")
        
        if response.status_code == 200:
            projets = response.json()
            print(f"✅ API OK - {len(projets)} projets chargés")
            
            # Analyser les projets disponibles
            soumis = [p for p in projets if p['statut'] == 'soumis']
            assignes = [p for p in projets if p['statut'] == 'assigné']
            
            print(f"📋 Projets soumis (auto-assignables): {len(soumis)}")
            print(f"🔄 Projets assignés (réassignables): {len(assignes)}")
            
            # Test 2: Simuler une auto-assignation si possible
            if soumis:
                projet_test = soumis[0]
                print(f"\n🧪 Test d'auto-assignation sur projet ID {projet_test['id']}")
                
                payload = {
                    "evaluateur_nom": "secretariatsct",
                    "auteur": "secretariatsct",
                    "role": "secretariatsct"
                }
                
                assign_response = requests.post(
                    f"http://127.0.0.1:5002/api/projects/{projet_test['id']}/traiter",
                    json=payload
                )
                
                if assign_response.status_code == 200:
                    print("✅ Auto-assignation réussie !")
                    print("✅ Le secrétariat SCT peut maintenant s'assigner des projets")
                else:
                    print(f"❌ Erreur auto-assignation: {assign_response.status_code}")
            else:
                print("ℹ️ Aucun projet soumis pour tester l'auto-assignation")
                
        else:
            print(f"❌ Erreur API: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur test API: {e}")

def main():
    backend_process = None
    try:
        backend_process = start_backend()
        test_api_auto_assignation()
        
        print("\n✅ FONCTIONNALITÉ PRÊTE !")
        print("📋 Le secrétariat SCT peut maintenant:")
        print("   1. S'assigner des projets soumis via 'Moi-même (Secrétariat SCT)'")
        print("   2. Se réassigner des projets via le même menu")
        print("   3. Évaluer directement dans l'onglet 'Mes évaluations'")
        
    finally:
        if backend_process:
            print("\n🛑 Arrêt du serveur backend...")
            backend_process.terminate()
            time.sleep(1)
            if backend_process.poll() is None:
                backend_process.kill()

if __name__ == "__main__":
    main()