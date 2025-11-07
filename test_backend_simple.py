#!/usr/bin/env python3
import requests
import json
import time

def test_backend():
    print("🔍 Test du backend...")
    
    try:
        # Test de l'API projets
        print("📋 Test API projets...")
        response = requests.get('http://127.0.0.1:5001/api/projects?role=admin&username=admin', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API projets OK - {len(data)} projets trouvés")
            if len(data) > 0:
                print(f"   Premier projet: {data[0]['titre'][:50]}...")
        else:
            print(f"❌ API projets erreur: {response.status_code}")
            
        # Test de l'API pôles
        print("🗺️ Test API pôles...")
        response = requests.get('http://127.0.0.1:5001/api/stats/poles', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API pôles OK - {len(data)} pôles trouvés")
            for pole, stats in list(data.items())[:3]:
                print(f"   📍 {pole}: {stats['total']} projets")
        else:
            print(f"❌ API pôles erreur: {response.status_code}")
            print(f"   Réponse: {response.text[:100]}...")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    test_backend()