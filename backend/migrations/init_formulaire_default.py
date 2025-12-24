"""
Script pour initialiser la configuration par défaut du formulaire d'évaluation
Basé sur la structure actuelle du formulaire EvaluationDetaillee.vue
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app
from models import db, FormulaireConfig, SectionFormulaire, ChampFormulaire, CritereEvaluation
import json

def init_default_config():
    """Initialise la configuration par défaut si elle n'existe pas"""

    with app.app_context():
        # Vérifier s'il existe déjà une configuration active
        existing_config = FormulaireConfig.query.filter_by(active=True).first()
        if existing_config:
            print("[INIT FORMULAIRE] Configuration active déjà existante, pas d'initialisation nécessaire")
            return

        print("[INIT FORMULAIRE] Création de la configuration par défaut...")

        # Créer la configuration principale
        config = FormulaireConfig(
            nom="Configuration Standard DGPPE",
            version="1.0",
            description="Configuration standard du formulaire d'évaluation DGPPE avec tous les critères actuels",
            active=True,
            score_total_max=100,
            seuil_favorable=80,
            seuil_conditionnel=70,
            modifie_par="system"
        )
        db.session.add(config)
        db.session.flush()  # Pour obtenir l'ID

        # Section I - PRÉSENTATION DU PROJET
        section1 = SectionFormulaire(
            config_id=config.id,
            titre="PRÉSENTATION DU PROJET",
            numero="I",
            ordre=1,
            type_section="presentation",
            editable=False  # Section auto-remplie depuis les données du projet
        )
        db.session.add(section1)
        db.session.flush()

        # Champs de la section I (lecture seule, remplis automatiquement)
        champs_section1 = [
            {"libelle": "INTITULÉ DU PROJET", "cle": "intitule", "type_champ": "text", "ordre": 1, "largeur": "full", "lecture_seule": True},
            {"libelle": "SECTEUR DE PLANIFICATION", "cle": "secteur", "type_champ": "text", "ordre": 2, "largeur": "half", "lecture_seule": True},
            {"libelle": "PÔLES TERRITORIAUX", "cle": "poles", "type_champ": "text", "ordre": 3, "largeur": "half", "lecture_seule": True},
            {"libelle": "COÛT DU PROJET", "cle": "cout_estimatif", "type_champ": "number", "ordre": 4, "largeur": "half", "lecture_seule": True},
            {"libelle": "ORGANISME DE TUTELLE", "cle": "organisme_tutelle", "type_champ": "text", "ordre": 5, "largeur": "half", "lecture_seule": True},
            {"libelle": "DESCRIPTION DU PROJET", "cle": "description", "type_champ": "textarea", "ordre": 6, "largeur": "full", "lecture_seule": True},
        ]

        for champ_data in champs_section1:
            champ = ChampFormulaire(
                section_id=section1.id,
                **champ_data
            )
            db.session.add(champ)

        # Section II - CLASSIFICATION DU PROJET
        section2 = SectionFormulaire(
            config_id=config.id,
            titre="CLASSIFICATION DU PROJET",
            numero="II",
            ordre=2,
            type_section="classification",
            editable=False
        )
        db.session.add(section2)
        db.session.flush()

        # Champs de la section II
        origine_options = json.dumps(["MATURATION", "OFFRE SPONTANÉE", "AUTRES"])
        typologie_options = json.dumps(["PRODUCTIF", "APPUI À LA PRODUCTION", "SOCIAL", "ENVIRONNEMENTAL"])

        champ_origine = ChampFormulaire(
            section_id=section2.id,
            libelle="ORIGINE DU PROJET",
            cle="origine_projet",
            type_champ="checkbox_group",
            ordre=1,
            largeur="half",
            options=origine_options,
            lecture_seule=True
        )
        db.session.add(champ_origine)

        champ_typologie = ChampFormulaire(
            section_id=section2.id,
            libelle="TYPOLOGIE DU PROJET",
            cle="typologie_projet",
            type_champ="checkbox_group",
            ordre=2,
            largeur="half",
            options=typologie_options,
            lecture_seule=True
        )
        db.session.add(champ_typologie)

        # Section III - RÉSULTATS DE L'ÉVALUATION
        section3 = SectionFormulaire(
            config_id=config.id,
            titre="RÉSULTATS DE L'ÉVALUATION",
            numero="III",
            ordre=3,
            type_section="evaluation",
            editable=True
        )
        db.session.add(section3)
        db.session.flush()

        # Critères de la section III (basés sur le modèle actuel)
        criteres = [
            {"nom": "PERTINENCE", "cle": "pertinence", "score_max": 5, "ordre": 1},
            {"nom": "ALIGNEMENT À LA DOCTRINE DE TRANSFORMATION SYSTÉMIQUE", "cle": "alignement", "score_max": 10, "ordre": 2},
            {"nom": "PERTINENCE DES ACTIVITÉS ET BIEN FONDÉ DES COÛTS/PART DE FONCTIONNEMENT", "cle": "activites_couts", "score_max": 15, "ordre": 3},
            {"nom": "ÉQUITÉ (SOCIALE-TERRITORIALE-GENRE)", "cle": "equite", "score_max": 15, "ordre": 4},
            {"nom": "VIABILITÉ/RENTABILITÉ FINANCIÈRE", "cle": "viabilite", "score_max": 5, "ordre": 5},
            {"nom": "RENTABILITÉ SOCIO-ÉCONOMIQUE (ACA/MPR)", "cle": "rentabilite", "score_max": 5, "ordre": 6},
            {"nom": "BÉNÉFICES STRATÉGIQUES (SÉCURITÉ-RÉSILIENCE-INNOVATION-COMPÉTITIVITÉ-CONTENU LOCAL, ETC.)", "cle": "benefices_strategiques", "score_max": 15, "ordre": 7},
            {"nom": "PÉRENNITÉ ET DURABILITÉ DES EFFETS ET IMPACTS DU PROJET", "cle": "perennite", "score_max": 5, "ordre": 8},
            {"nom": "AVANTAGES ET COÛTS INTANGIBLES", "cle": "avantages_intangibles", "score_max": 10, "ordre": 9},
            {"nom": "FAISABILITÉ DU PROJET / RISQUES POTENTIELS", "cle": "faisabilite", "score_max": 5, "ordre": 10},
            {"nom": "POTENTIALITÉ OU OPPORTUNITÉ DU PROJET À ÊTRE RÉALISÉ EN PPP", "cle": "ppp", "score_max": 5, "ordre": 11},
            {"nom": "IMPACTS ENVIRONNEMENTAUX", "cle": "impact_environnemental", "score_max": 5, "ordre": 12},
            {"nom": "IMPACT SUR L'EMPLOI", "cle": "impact_emploi", "score_max": 5, "ordre": 13, "avec_recommandations": True},
        ]

        for critere_data in criteres:
            avec_reco = critere_data.pop('avec_recommandations', False)
            critere = CritereEvaluation(
                section_id=section3.id,
                avec_description=True,
                avec_recommandations=avec_reco,
                **critere_data
            )
            db.session.add(critere)

        # Section IV - CONCLUSION
        section4 = SectionFormulaire(
            config_id=config.id,
            titre="CONCLUSION",
            numero="IV",
            ordre=4,
            type_section="conclusion",
            editable=True
        )
        db.session.add(section4)
        db.session.flush()

        # Champs de la section IV
        proposition_options = json.dumps(["Favorable", "Favorable sous condition", "Défavorable"])

        champ_proposition = ChampFormulaire(
            section_id=section4.id,
            libelle="PROPOSITION",
            cle="proposition",
            type_champ="select",
            ordre=1,
            largeur="full",
            options=proposition_options,
            lecture_seule=True,  # Auto-calculé basé sur le score
            aide="Proposition basée sur le score total: Score < 70 points = Défavorable (automatique), Score ≥ 70 points = L'évaluateur choisit entre Favorable ou Favorable sous conditions"
        )
        db.session.add(champ_proposition)

        champ_recommandations = ChampFormulaire(
            section_id=section4.id,
            libelle="RECOMMANDATIONS",
            cle="recommandations",
            type_champ="textarea",
            ordre=2,
            largeur="full",
            obligatoire=False
        )
        db.session.add(champ_recommandations)

        # Sauvegarder
        db.session.commit()

        print("[INIT FORMULAIRE] Configuration par défaut créée avec succès!")
        print(f"  - Configuration ID: {config.id}")
        print(f"  - 4 sections créées")
        print(f"  - 13 critères d'évaluation créés")

if __name__ == "__main__":
    init_default_config()
