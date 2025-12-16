#!/usr/bin/env python3
"""
Script d'initialisation pour la production Render
À exécuter une seule fois depuis le shell Render
"""

import os
import sys

# Configuration Gmail pour la production
print("=" * 60)
print("INITIALISATION PRODUCTION - Configuration Gmail + Templates")
print("=" * 60)
print()

# 1. Afficher la configuration actuelle
print("1️⃣  Configuration actuelle:")
print(f"   SMTP_SERVER: {os.getenv('SMTP_SERVER', 'non défini')}")
print(f"   SMTP_USERNAME: {os.getenv('SMTP_USERNAME', 'non défini')}")
print(f"   EMAIL_ENABLED: {os.getenv('EMAIL_ENABLED', 'non défini')}")
print()

# 2. Initialiser les templates d'emails
print("2️⃣  Initialisation des templates d'emails...")
try:
    # Importer et exécuter le script d'initialisation
    import init_email_templates
    print("✅ Templates initialisés avec succès!")
except Exception as e:
    print(f"❌ Erreur lors de l'initialisation des templates: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("✅ INITIALISATION TERMINÉE AVEC SUCCÈS")
print("=" * 60)
print()
print("Les templates d'emails sont maintenant disponibles.")
print("Vous pouvez fermer ce shell et recharger la page Configuration Emails.")
