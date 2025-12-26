#!/bin/bash
# Script pour exécuter la migration soft delete sur le serveur de production Render

echo "=========================================="
echo "Migration Soft Delete - Production Render"
echo "=========================================="
echo ""

# L'endpoint de migration existe déjà, mais nous devons créer un nouveau pour soft delete
# Appelons directement Python via l'API

echo "Tentative de connexion au serveur de production..."
echo ""

# Créer un script Python temporaire pour la migration
cat > /tmp/migrate_soft_delete_render.py << 'PYTHON_EOF'
import requests
import json

API_BASE = "https://maturation-backend.onrender.com"

print("🔍 Vérification de l'état actuel de la base de données...")
try:
    response = requests.get(f"{API_BASE}/api/admin/db-info")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Base de données accessible")
    else:
        print(f"⚠️  Erreur détectée (attendu - colonne deleted_at manquante)")
except Exception as e:
    print(f"⚠️  Erreur: {e}")

print("\n" + "="*60)
print("La migration doit être effectuée manuellement sur Render")
print("="*60)
print("\nInstructions:")
print("1. Connectez-vous à Render Dashboard")
print("2. Allez dans votre service 'maturation-backend'")
print("3. Ouvrez le Shell")
print("4. Exécutez les commandes suivantes:\n")
print("   cd /opt/render/project/src/backend")
print("   python3 migrate_add_soft_delete.py")
print("\nOu utilisez SSH si configuré:")
print("   ssh render")
print("   cd backend")
print("   python3 migrate_add_soft_delete.py")
PYTHON_EOF

python3 /tmp/migrate_soft_delete_render.py
rm /tmp/migrate_soft_delete_render.py
