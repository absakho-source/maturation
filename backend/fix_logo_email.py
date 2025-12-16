#!/usr/bin/env python3
"""
Script pour remplacer le logo DGPPE dans les emails par une version base64
"""

import base64
import os
import re

def fix_logo_in_email_service():
    """Remplace l'URL du logo par le logo encodé en base64"""

    # Lire le logo et le convertir en base64
    logo_path = 'static/logo-dgppe.png'

    if not os.path.exists(logo_path):
        print(f"❌ Logo non trouvé: {logo_path}")
        return False

    with open(logo_path, 'rb') as f:
        logo_data = base64.b64encode(f.read()).decode('utf-8')

    logo_base64 = f"data:image/png;base64,{logo_data}"

    print("=" * 60)
    print("FIX: LOGO DGPPE DANS LES EMAILS")
    print("=" * 60)
    print()
    print(f"📂 Logo source: {logo_path}")
    print(f"📊 Taille base64: {len(logo_base64):,} caractères")
    print()

    # Lire email_service.py
    email_service_path = 'email_service.py'

    if not os.path.exists(email_service_path):
        print(f"❌ Fichier non trouvé: {email_service_path}")
        return False

    with open(email_service_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Chercher et remplacer l'URL du logo
    pattern = r'<img src="{PLATFORM_URL}/static/logo-dgppe\.png"'
    replacement = f'<img src="{logo_base64}"'

    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)

        # Écrire le fichier modifié
        with open(email_service_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ email_service.py modifié avec succès!")
        print()
        print("Le logo est maintenant intégré en base64 dans les emails")
        print("Il s'affichera correctement dans toutes les boîtes de réception")
        print()
        print("=" * 60)
        return True
    else:
        print("⚠️  Pattern non trouvé dans email_service.py")
        print("Le logo utilise peut-être déjà base64 ou un autre format")
        print()
        print("=" * 60)
        return False

if __name__ == '__main__':
    fix_logo_in_email_service()
