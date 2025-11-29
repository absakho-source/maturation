"""
Script pour créer les tables de configuration du formulaire dans la base de données existante
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app, db

with app.app_context():
    print("[CREATE TABLES] Création des tables de configuration du formulaire...")

    # Créer seulement les nouvelles tables
    from models import FormulaireConfig, SectionFormulaire, ChampFormulaire, CritereEvaluation

    # Créer les tables si elles n'existent pas
    db.create_all()

    print("[CREATE TABLES] ✅ Tables créées avec succès!")

    # Maintenant initialiser la configuration par défaut
    print("[CREATE TABLES] Initialisation de la configuration par défaut...")
    from init_formulaire_default import init_default_config
    init_default_config()

    print("[CREATE TABLES] ✅ Configuration par défaut initialisée!")
