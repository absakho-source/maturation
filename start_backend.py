#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/backend')

print("🚀 Démarrage du backend...")
try:
    import app
    print("✅ Module app importé")
    print("🌐 Démarrage serveur Flask sur port 5002...")
    app.app.run(host='127.0.0.1', port=5002, debug=False, use_reloader=False)
except Exception as e:
    print(f"❌ Erreur: {e}")
    sys.exit(1)