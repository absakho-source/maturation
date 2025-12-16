#!/usr/bin/env python3
"""
Script pour convertir le logo DGPPE en base64 et créer une constante
"""

import base64
import os

def convert_logo():
    logo_path = 'static/logo-dgppe.png'

    if not os.path.exists(logo_path):
        print(f"❌ Logo non trouvé: {logo_path}")
        return None

    with open(logo_path, 'rb') as f:
        logo_data = base64.b64encode(f.read()).decode('utf-8')

    logo_base64 = f"data:image/png;base64,{logo_data}"

    print("=" * 60)
    print("CONVERSION DU LOGO EN BASE64")
    print("=" * 60)
    print()
    print(f"📂 Fichier source: {logo_path}")
    print(f"📊 Taille base64: {len(logo_base64):,} caractères")
    print()
    print("✅ Logo converti avec succès!")
    print()
    print("Copiez cette ligne dans email_service.py:")
    print()
    print(f'LOGO_DGPPE_BASE64 = "{logo_base64}"')
    print()
    print("=" * 60)

    # Écrire dans un fichier
    with open('logo_base64.txt', 'w') as f:
        f.write(f'LOGO_DGPPE_BASE64 = "{logo_base64}"\n')

    print("📝 Constante sauvegardée dans logo_base64.txt")

    return logo_base64

if __name__ == '__main__':
    convert_logo()
