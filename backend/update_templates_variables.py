#!/usr/bin/env python3
"""
Script pour remplacer {user_name} par {nom} dans tous les templates
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app
from db import db
from models import EmailTemplate
import json

def update_template_variables():
    """Remplace user_name par nom dans tous les templates"""

    with app.app_context():
        print("=" * 60)
        print("MISE À JOUR DES VARIABLES DES TEMPLATES")
        print("=" * 60)
        print()

        # Récupérer tous les templates
        templates = EmailTemplate.query.all()
        print(f"📧 Nombre de templates trouvés: {len(templates)}")
        print()

        updated_count = 0

        for template in templates:
            modified = False

            # Mettre à jour le contenu HTML
            if '{user_name}' in template.contenu_html:
                template.contenu_html = template.contenu_html.replace('{user_name}', '{nom}')
                modified = True
                print(f"  ✓ Contenu HTML mis à jour: {template.nom}")

            # Mettre à jour les variables disponibles
            try:
                variables = json.loads(template.variables_disponibles)
                variables_updated = False

                for var in variables:
                    if var['var'] == '{user_name}':
                        var['var'] = '{nom}'
                        var['description'] = 'Nom complet du destinataire'
                        variables_updated = True

                if variables_updated:
                    template.variables_disponibles = json.dumps(variables)
                    modified = True
                    print(f"  ✓ Variables mises à jour: {template.nom}")

            except Exception as e:
                print(f"  ⚠️  Erreur lors de la mise à jour des variables pour {template.nom}: {e}")

            if modified:
                updated_count += 1

        # Sauvegarder les modifications
        if updated_count > 0:
            db.session.commit()
            print()
            print(f"✅ {updated_count} template(s) mis à jour avec succès!")
        else:
            print()
            print("ℹ️  Aucun template à mettre à jour")

        print()
        print("=" * 60)
        print("MISE À JOUR TERMINÉE")
        print("=" * 60)

if __name__ == '__main__':
    update_template_variables()
