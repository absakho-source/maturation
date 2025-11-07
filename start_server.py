#!/usr/bin/env python3
"""
Script de démarrage simple pour le serveur backend
"""
import os
import sys

# Ajouter le chemin du backend au PYTHONPATH
backend_path = "/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

os.chdir(backend_path)

try:
    # Import et test de l'application
    print("🔧 Initialisation du serveur...")
    import app
    
    # Test rapide de la base de données
    with app.app.app_context():
        from app import Project
        count = Project.query.count()
        print(f"✅ Base de données: {count} projets trouvés")
    
    # Démarrage du serveur
    print("🚀 Démarrage du serveur Flask sur http://127.0.0.1:5002")
    print("📡 API disponible sur /api/projects")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    app.app.run(
        debug=False, 
        host='127.0.0.1', 
        port=5002, 
        use_reloader=False,
        threaded=True
    )
    
except KeyboardInterrupt:
    print("\n🛑 Serveur arrêté par l'utilisateur")
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()