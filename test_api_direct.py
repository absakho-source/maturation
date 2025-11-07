#!/usr/bin/env python3
"""
Test direct de la fiche d'évaluation
"""
import requests
import json

def test_evaluation_api():
    print("🔍 TEST DIRECT APIs FICHE D'ÉVALUATION")
    
    # URLs à tester
    test_urls = [
        ("Liste projets", "http://127.0.0.1:5002/api/projects?role=admin&username=admin"),
        ("Présentation projet 1", "http://127.0.0.1:5002/api/projects/1/presentation"), 
        ("Profil utilisateur", "http://127.0.0.1:5002/api/users/profile"),
        ("Proxy frontend présentation", "http://127.0.0.1:5173/api/projects/1/presentation")
    ]

    for name, url in test_urls:
        try:
            print(f"\n📡 {name}: {url}")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'projects' in url:
                        print(f"✅ Réussi - {len(data)} projets trouvés")
                    elif 'presentation' in url:
                        print(f"✅ Réussi - Projet: {data.get('titre', 'N/A')}")
                        print(f"   Secteur: {data.get('secteur', 'N/A')}")
                        print(f"   Coût: {data.get('cout_estimatif', 'N/A'):,} FCFA")
                    elif 'profile' in url:
                        print(f"✅ Réussi - Utilisateur: {data.get('nom', 'N/A')}")
                    else:
                        print(f"✅ Réussi - Données reçues")
                except:
                    print(f"✅ Réussi mais pas JSON - {response.text[:100]}...")
            else:
                print(f"❌ Erreur {response.status_code}: {response.text[:100]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connexion impossible - Serveur non démarré?")
        except requests.exceptions.Timeout:
            print(f"❌ Timeout")
        except Exception as e:
            print(f"❌ Erreur: {e}")

    print(f"\n🎯 DIAGNOSTIC:")
    print(f"- Si APIs backend (port 5002) OK → Problème frontend ou routage")
    print(f"- Si APIs backend échouent → Redémarrer backend avec nouvelles routes")
    print(f"- Si proxy frontend (port 5173) échoue → Vérifier proxy Vite")

if __name__ == "__main__":
    test_evaluation_api()