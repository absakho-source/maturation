#!/usr/bin/env python3
"""
Test simple de la fiche d'évaluation
"""
import sys
import os

# Ajouter le backend au path
backend_path = "/Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/backend"
sys.path.insert(0, backend_path)
os.chdir(backend_path)

print("🔧 Test de la fiche d'évaluation...")

try:
    import app
    
    print("✅ Module app importé avec succès")
    print("📝 Routes disponibles:")
    for rule in app.app.url_map.iter_rules():
        if 'evaluation' in rule.rule or 'presentation' in rule.rule:
            print(f"  - {rule.rule} [{rule.methods}]")
    
    # Test de la base de données
    with app.app.app_context():
        projects = app.Project.query.limit(3).all()
        print(f"✅ Base de données OK - {len(projects)} projets trouvés")
        for p in projects:
            print(f"  📋 {p.id}: {p.titre[:40]}...")
    
    print("\n🚀 Démarrage du serveur Flask...")
    app.app.run(debug=False, host='127.0.0.1', port=5002, use_reloader=False)
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()