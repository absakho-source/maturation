#!/usr/bin/env python3
"""
Script simple pour démarrer le serveur backend
"""
import os
import sys

# Changer vers le dossier backend
backend_dir = "/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/backend"
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

print("🔧 Démarrage du serveur backend...")
print(f"📂 Répertoire: {os.getcwd()}")

try:
    import app as app_module
    print("✅ Application importée avec succès")
    print("📝 Routes de projet chargées")
    
    # Vérifier la DB
    with app_module.app.app_context():
        projects = app_module.Project.query.limit(2).all()
        print(f"✅ Base de données: {len(projects)} projets trouvés")
    
    print("🚀 Démarrage sur http://127.0.0.1:5002...")
    app_module.app.run(debug=False, host='127.0.0.1', port=5002, use_reloader=False)
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()