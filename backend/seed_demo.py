#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de création de données de démonstration PLASMAP
Projets fictifs mais réalistes à des stades différents du workflow
avec matrices de recevabilité et fiches d'évaluation préremplies.

Usage : python seed_demo.py
"""

import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from db import db
from models import Project, FicheEvaluation, Historique, User

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def date_ago(days):
    return datetime.utcnow() - timedelta(days=days)

def get_or_create_user(username, password, role, display_name, email, structure):
    u = User.query.filter_by(username=username).first()
    if not u:
        from werkzeug.security import generate_password_hash
        u = User(
            username=username,
            password=generate_password_hash(password),
            role=role,
            display_name=display_name,
            email=email,
            nom_complet=display_name,
            nom_structure=structure,
            statut_compte='verifie',
        )
        db.session.add(u)
        db.session.flush()
        print(f"   ✔ Utilisateur créé : {username} ({role})")
    return u

def add_historique(project_id, action, auteur, role, date=None):
    h = Historique(
        project_id=project_id,
        action=action,
        auteur=auteur,
        role=role,
        date_action=date or datetime.utcnow(),
    )
    db.session.add(h)

# ─────────────────────────────────────────────────────────────────────────────
# MATRICES DE RECEVABILITÉ
# ─────────────────────────────────────────────────────────────────────────────

MATRICE_COMPLETE = {
    "documents": [
        {"nom": "Note de présentation du projet", "requis": True, "transmis": True},
        {"nom": "Étude de faisabilité technique", "requis": True, "transmis": True},
        {"nom": "Étude socio-économique", "requis": True, "transmis": True},
        {"nom": "Plan de financement détaillé", "requis": True, "transmis": True},
        {"nom": "Analyse environnementale préliminaire", "requis": True, "transmis": True},
        {"nom": "Calendrier prévisionnel de réalisation", "requis": True, "transmis": True},
        {"nom": "Cadre logique du projet", "requis": True, "transmis": True},
        {"nom": "Acte de propriété / sécurisation foncière", "requis": False, "transmis": True},
    ],
    "commentaires_globaux": "Dossier complet. Toutes les pièces obligatoires ont été transmises. Le projet est évaluable."
}

MATRICE_INCOMPLETE = {
    "documents": [
        {"nom": "Note de présentation du projet", "requis": True, "transmis": True},
        {"nom": "Étude de faisabilité technique", "requis": True, "transmis": True},
        {"nom": "Étude socio-économique", "requis": True, "transmis": False},
        {"nom": "Plan de financement détaillé", "requis": True, "transmis": False},
        {"nom": "Analyse environnementale préliminaire", "requis": True, "transmis": True},
        {"nom": "Calendrier prévisionnel de réalisation", "requis": True, "transmis": True},
        {"nom": "Cadre logique du projet", "requis": True, "transmis": False},
        {"nom": "Acte de propriété / sécurisation foncière", "requis": False, "transmis": False},
    ],
    "commentaires_globaux": "Dossier incomplet. Trois documents obligatoires manquants : étude socio-économique, plan de financement et cadre logique. Le soumissionnaire est invité à compléter son dossier dans un délai de 15 jours."
}

# ─────────────────────────────────────────────────────────────────────────────
# DONNÉES DES PROJETS
# ─────────────────────────────────────────────────────────────────────────────

PROJETS = [

    # ── 1. SOUMIS (tout frais) ─────────────────────────────────────────────
    {
        "meta": {"stade": "soumis", "tag": "PROJ-DEMO-01"},
        "projet": {
            "titre": "Création d'un centre de santé communautaire à Vélingara",
            "description": (
                "Construction et équipement d'un centre de santé de niveau II à Vélingara (région de Kolda) "
                "desservant 12 villages environnants. Le centre comprendra une maternité de 10 lits, "
                "un service de consultation générale, un laboratoire d'analyses, une pharmacie et "
                "un groupe électrogène solaire. Il bénéficiera à une population d'environ 25 000 habitants "
                "actuellement à plus de 40 km du centre de santé le plus proche."
            ),
            "secteur": "santé-action sociale",
            "poles": "Sud (Ziguinchor, Sédhiou, Kolda)",
            "cout_estimatif": 850_000_000,
            "structure_soumissionnaire": "Direction Régionale de la Santé de Kolda",
            "organisme_tutelle": "Ministère de la Santé et de l'Action Sociale",
            "nouveaute": "projet_initial",
            "niveau_priorite": "prioritaire_ant",
            "type_financement": json.dumps(["budget_etat", "partenaire_technique"]),
            "duree_annees": 2,
            "genre": True,
            "cc_adaptation": False,
            "lieu_soumission_region": "Kolda",
            "lieu_soumission_ville": "Vélingara",
            "lieu_soumission_pays": "Sénégal",
            "point_focal_nom": "Dr. Mariama Diallo",
            "point_focal_fonction": "Médecin Chef de District",
            "point_focal_telephone": "77 345 67 89",
            "point_focal_email": "m.diallo@sante.gouv.sn",
            "auteur_nom": "soumissionnaire",
            "statut": "soumis",
            "date_soumission": date_ago(3),
        },
    },

    # ── 2. ASSIGNÉ ─────────────────────────────────────────────────────────
    {
        "meta": {"stade": "assigné", "tag": "PROJ-DEMO-02", "evaluateur": "evaluateur1"},
        "projet": {
            "titre": "Aménagement de la plaine de Ndiaël pour l'agriculture irriguée",
            "description": (
                "Aménagement de 2 500 hectares dans la plaine du Ndiaël (région de Saint-Louis) "
                "pour l'agriculture irriguée intensive. Le projet comprend la réhabilitation de canaux "
                "d'irrigation, la construction de stations de pompage, la viabilisation des terres "
                "et la mise en place de périmètres agricoles. Objectif : 3 500 producteurs bénéficiaires, "
                "production estimée à 50 000 tonnes de riz paddy par an."
            ),
            "secteur": "agriculture-élevage-pêche",
            "poles": "Nord (Saint-Louis)",
            "cout_estimatif": 14_200_000_000,
            "structure_soumissionnaire": "Société d'Aménagement et d'Exploitation des Terres du Delta",
            "organisme_tutelle": "Ministère de l'Agriculture, de la Souveraineté Alimentaire et de l'Élevage",
            "nouveaute": "phase_2",
            "niveau_priorite": "prioritaire_ant",
            "type_financement": json.dumps(["budget_etat", "banque_mondiale", "bad"]),
            "duree_annees": 4,
            "genre": True,
            "cc_adaptation": True,
            "lieu_soumission_region": "Saint-Louis",
            "lieu_soumission_pays": "Sénégal",
            "point_focal_nom": "Ibrahima Wane",
            "point_focal_fonction": "Directeur Technique",
            "point_focal_telephone": "77 512 34 56",
            "point_focal_email": "i.wane@saed.sn",
            "auteur_nom": "soumissionnaire",
            "statut": "assigné",
            "evaluateur_nom": "evaluateur1",
            "date_soumission": date_ago(12),
        },
    },

    # ── 3. EN ÉVALUATION (matrice remplie, évaluable) ─────────────────────
    {
        "meta": {"stade": "en évaluation", "tag": "PROJ-DEMO-03", "evaluateur": "evaluateur1"},
        "projet": {
            "titre": "Parc industriel agro-alimentaire de Kaolack",
            "description": (
                "Création d'un parc industriel dédié à la transformation des produits agricoles "
                "à Kaolack : unités de décorticage et trituration d'arachide, de transformation "
                "de la tomate et de conditionnement de céréales. Surface totale : 15 ha. "
                "Capacité de traitement : 80 000 tonnes/an. Création de 1 200 emplois directs "
                "et 3 000 emplois indirects. Puissance électrique : 5 MW raccordée au réseau SENELEC."
            ),
            "secteur": "industrie-artisanat",
            "poles": "Centre (Kaolack, Fatick, Kaffrine)",
            "cout_estimatif": 28_500_000_000,
            "structure_soumissionnaire": "Agence de Promotion des Investissements et des Grands Travaux",
            "organisme_tutelle": "Ministère de l'Industrie et du Commerce",
            "nouveaute": "projet_initial",
            "niveau_priorite": "prioritaire_ant",
            "type_financement": json.dumps(["ppp", "budget_etat", "prive_national"]),
            "duree_annees": 3,
            "genre": False,
            "cc_adaptation": False,
            "lieu_soumission_region": "Kaolack",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire",
            "statut": "en évaluation",
            "evaluateur_nom": "evaluateur1",
            "date_soumission": date_ago(25),
            # Matrice de recevabilité remplie → évaluable
            "evaluation_prealable": "dossier_evaluable",
            "evaluation_prealable_date": date_ago(18),
            "evaluation_prealable_commentaire": "Dossier complet. Toutes les pièces obligatoires ont été transmises. Projet déclaré évaluable.",
            "evaluation_prealable_matrice": json.dumps(MATRICE_COMPLETE),
            "evaluabilite": "evaluable",
            "evaluabilite_date": date_ago(16),
            "evaluabilite_commentaire": "Projet confirmé évaluable. Évaluation détaillée en cours.",
        },
    },

    # ── 4. COMPLÉMENTS DEMANDÉS ───────────────────────────────────────────
    {
        "meta": {"stade": "compléments demandés", "tag": "PROJ-DEMO-04", "evaluateur": "evaluateur2"},
        "projet": {
            "titre": "Réhabilitation du réseau routier urbain de Thiès",
            "description": (
                "Réhabilitation de 45 km de voirie urbaine à Thiès : rechargement de la chaussée, "
                "construction de trottoirs, installation de caniveaux pluviaux, signalisation "
                "horizontale et verticale, et mise en place de 120 lampadaires solaires. "
                "Le projet couvrira les quartiers de Nguinth, Randoulène et Médina-Fall, "
                "bénéficiant à 180 000 habitants."
            ),
            "secteur": "transports-infrastructures",
            "poles": "Thiès",
            "cout_estimatif": 9_800_000_000,
            "structure_soumissionnaire": "Agence des Travaux et de Gestion des Routes",
            "organisme_tutelle": "Ministère des Infrastructures et des Transports Terrestres",
            "nouveaute": "projet_initial",
            "niveau_priorite": "standard",
            "type_financement": json.dumps(["budget_etat", "collectivite_locale"]),
            "duree_annees": 2,
            "genre": False,
            "cc_adaptation": False,
            "lieu_soumission_region": "Thiès",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire2",
            "statut": "compléments demandés",
            "evaluateur_nom": "evaluateur2",
            "date_soumission": date_ago(30),
            "evaluation_prealable": "complements_requis",
            "evaluation_prealable_date": date_ago(22),
            "evaluation_prealable_matrice": json.dumps(MATRICE_INCOMPLETE),
            "complements_demande_message": (
                "Le dossier transmis est incomplet. Merci de fournir dans un délai de 15 jours :\n"
                "1. L'étude socio-économique actualisée avec données 2024\n"
                "2. Le plan de financement détaillé avec lettres d'intention des co-financeurs\n"
                "3. Le cadre logique du projet avec indicateurs mesurables\n"
                "4. Le certificat d'inscription au PIP du Ministère des Finances"
            ),
        },
    },

    # ── 5. COMPLÉMENTS FOURNIS ─────────────────────────────────────────────
    {
        "meta": {"stade": "compléments fournis", "tag": "PROJ-DEMO-05", "evaluateur": "evaluateur2"},
        "projet": {
            "titre": "Construction de 200 forages pastoraux dans le Ferlo",
            "description": (
                "Construction de 200 forages pastoraux équipés de systèmes d'exhaure solaires "
                "dans la zone sylvopastorale du Ferlo (régions de Louga, Matam, Tambacounda). "
                "Chaque forage sera équipé d'un château d'eau de 30 m³, d'abreuvoirs et "
                "d'un point d'eau potable. Le projet bénéficiera à 120 000 éleveurs "
                "et sécurisera les déplacements de 4 millions de têtes de bétail."
            ),
            "secteur": "agriculture-élevage-pêche",
            "poles": "Diourbel-Louga, Nord-Est (Matam), Sud-Est (Tambacounda, Kédougou)",
            "cout_estimatif": 22_000_000_000,
            "structure_soumissionnaire": "Direction de l'Élevage",
            "organisme_tutelle": "Ministère de l'Agriculture, de la Souveraineté Alimentaire et de l'Élevage",
            "nouveaute": "projet_initial",
            "niveau_priorite": "prioritaire_ant",
            "type_financement": json.dumps(["budget_etat", "bad", "fida"]),
            "duree_annees": 3,
            "genre": True,
            "cc_adaptation": True,
            "lieu_soumission_region": "Louga",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire2",
            "statut": "compléments fournis",
            "evaluateur_nom": "evaluateur2",
            "date_soumission": date_ago(45),
            "evaluation_prealable": "complements_requis",
            "evaluation_prealable_date": date_ago(38),
            "evaluation_prealable_matrice": json.dumps(MATRICE_INCOMPLETE),
            "complements_demande_message": (
                "Documents manquants : plan de financement et étude pastorale actualisée."
            ),
            "complements_reponse_message": (
                "Suite à votre demande du 18 mars 2026, nous avons le plaisir de vous soumettre "
                "les documents complémentaires suivants : (1) l'étude pastorale actualisée 2025 "
                "réalisée par le LNERV, (2) le plan de financement avec lettres de confirmation "
                "de la BAD et du FIDA, (3) les données GPS des 200 sites de forage préidentifiés. "
                "Nous restons disponibles pour tout renseignement complémentaire."
            ),
            "complements_reponse_pieces": json.dumps([
                "etude_pastorale_2025.pdf",
                "plan_financement_confirme.pdf",
                "coordonnees_gps_forages.xlsx"
            ]),
        },
    },

    # ── 6. ÉVALUÉ — Avis favorable (score élevé) ─────────────────────────
    {
        "meta": {"stade": "évalué_favorable", "tag": "PROJ-DEMO-06", "evaluateur": "evaluateur1",
                 "avec_fiche": True},
        "projet": {
            "titre": "Programme d'électrification rurale solaire – Zones enclavées du Sud-Est",
            "description": (
                "Électrification de 68 villages des régions de Tambacounda et Kédougou par mini-réseaux "
                "solaires. Chaque village recevra une centrale solaire de 20 à 80 kWc avec stockage "
                "par batteries. Le programme couvrira 22 000 ménages, 135 écoles, 42 postes de santé "
                "et 280 points d'eau. Durée : 30 mois. Opérateur : ASER en partenariat avec des "
                "opérateurs privés (modèle de délégation de service public)."
            ),
            "secteur": "énergies-mines",
            "poles": "Sud-Est (Tambacounda, Kédougou)",
            "cout_estimatif": 18_600_000_000,
            "structure_soumissionnaire": "Agence Sénégalaise d'Électrification Rurale",
            "organisme_tutelle": "Ministère de l'Énergie, du Pétrole et des Mines",
            "nouveaute": "phase_2",
            "niveau_priorite": "prioritaire_ant",
            "type_financement": json.dumps(["budget_etat", "bad", "banque_islamique", "prive_national"]),
            "duree_annees": 3,
            "genre": True,
            "cc_attenuation": True,
            "cc_adaptation": True,
            "lieu_soumission_region": "Tambacounda",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire",
            "statut": "évalué",
            "evaluateur_nom": "evaluateur1",
            "avis": "favorable",
            "fiche_evaluation_visible": True,
            "date_soumission": date_ago(60),
            "evaluation_prealable": "dossier_evaluable",
            "evaluation_prealable_date": date_ago(52),
            "evaluation_prealable_matrice": json.dumps(MATRICE_COMPLETE),
            "evaluabilite": "evaluable",
            "evaluabilite_date": date_ago(50),
        },
        "fiche": {
            "evaluateur_nom": "evaluateur1",
            "date_evaluation": date_ago(5),
            "intitule_projet": "Programme d'électrification rurale solaire – Zones enclavées du Sud-Est",
            "cout_projet": "18 600 000 000 FCFA",
            "origine_projet": "Initiative gouvernementale inscrite au PIP 2025-2029 dans le cadre de l'agenda d'accélération de l'accès universel à l'électricité",
            "cc_adaptation": True, "cc_attenuation": True, "genre": True,
            "articulation": "Plan Sénégal Émergent (PSE) - Axe 1 : Transformation structurelle de l'économie et croissance",
            "axes": "Axe 2 : Capital humain, protection sociale et développement durable",
            "objectifs_strategiques": "OS3 - Accélération de l'accès aux services énergétiques de base pour les populations rurales",
            "odd": "ODD 7 (Énergie propre), ODD 13 (Action climatique), ODD 1 (Pas de pauvreté)",
            "duree_analyse": "30 mois",
            "realisation": "36 mois",
            "exploitation": "25 ans",
            "localisation": "Régions de Tambacounda et Kédougou – 68 villages",
            "parties_prenantes": "ASER, Ministère de l'Énergie, collectivités locales, opérateurs privés délégués, BAD, BID",
            "objectif_projet": "Électrifier 68 villages enclavés par mini-réseaux solaires hybrides pour améliorer les conditions de vie, réduire la pauvreté énergétique et soutenir le développement des activités économiques locales.",
            "activites_principales": (
                "1. Études techniques détaillées et géotechniques des 68 sites\n"
                "2. Appel d'offres international pour la fourniture et installation\n"
                "3. Construction des centrales solaires et réseaux de distribution\n"
                "4. Formation des techniciens locaux\n"
                "5. Mise en service et transfert de gestion aux opérateurs"
            ),
            "resultats_attendus": (
                "- 22 000 ménages électrifiés\n"
                "- 135 écoles et 42 postes de santé alimentés\n"
                "- 280 points d'eau fonctionnels\n"
                "- 120 emplois locaux créés et maintenus\n"
                "- Réduction de 45 000 tonnes de CO₂/an"
            ),
            "organisme_tutelle": "Ministère de l'Énergie, du Pétrole et des Mines",
            "snd_2025_2029": "Axe stratégique 2 – Développement du capital humain et réduction des inégalités spatiales",
            # Scores (/100) — total ~82 → Favorable
            "pertinence_score": 4.5,
            "pertinence_description": "Le projet répond à un besoin avéré et prioritaire : le taux d'électrification des zones ciblées est inférieur à 8%. La cohérence avec les objectifs nationaux d'accès universel à l'énergie est totale.",
            "pertinence_recommandations": "Veiller à l'implication des communautés dès la phase de conception pour assurer l'appropriation.",
            "alignement_score": 8.5,
            "alignement_description": "Projet parfaitement aligné sur le PSE et l'agenda Vision 2050. L'approche par délégation de service public s'inscrit dans la doctrine de transformation systémique prônée par le gouvernement.",
            "alignement_recommandations": "Renforcer les synergies avec le programme PUMA et les projets d'eau potable en cours.",
            "activites_couts_score": 12.0,
            "activites_couts_description": "Le coût unitaire par village (274 M FCFA) est conforme aux références sectorielles. Les activités sont bien définies et le calendrier réaliste.",
            "activites_couts_recommandations": "Prévoir une provision de 10% pour imprévus liés aux contraintes logistiques en zones enclavées.",
            "equite_score": 13.0,
            "equite_description": "Le projet cible les zones les plus défavorisées du pays. La dimension genre est intégrée avec des tarifs sociaux pour les ménages vulnérables. Impact territorial fort.",
            "equite_recommandations": "Inclure un volet sensibilisation spécifique pour les femmes chefs de ménage.",
            "viabilite_score": 4.0,
            "viabilite_description": "Le modèle de délégation de service public avec recouvrement de charges est financièrement viable. Les subventions d'exploitation sont clairement budgétées.",
            "viabilite_recommandations": "Sécuriser les financements de la BAD et de la BID avant le démarrage.",
            "rentabilite_score": 4.0,
            "rentabilite_description": "Le TRI socio-économique estimé à 18% est satisfaisant. Les bénéfices indirects (santé, éducation, productivité) sont significatifs.",
            "rentabilite_recommandations": "Intégrer une étude d'impact ex-post pour mesurer les effets réels sur les revenus.",
            "benefices_strategiques_score": 12.5,
            "benefices_strategiques_description": "Fort impact sur la résilience climatique et la sécurité énergétique. Réduction de la dépendance aux combustibles fossiles. Contenu local estimé à 35%.",
            "benefices_strategiques_recommandations": "Maximiser le contenu local en privilégiant les entreprises sénégalaises pour l'installation.",
            "perennite_score": 4.0,
            "perennite_description": "Durée de vie des équipements de 25 ans. Mécanisme de maintenance assuré par les opérateurs délégués. Fonds de renouvellement intégré.",
            "perennite_recommandations": "Mettre en place un système de monitoring à distance pour détecter les pannes rapidement.",
            "avantages_intangibles_score": 8.0,
            "avantages_intangibles_description": "Amélioration significative de la qualité de vie, extension des heures de travail et d'étude, réduction des risques sécuritaires. Image internationale positive pour le Sénégal.",
            "avantages_intangibles_recommandations": "Documenter et communiquer les impacts pour valoriser le modèle auprès des partenaires.",
            "faisabilite_score": 4.0,
            "faisabilite_description": "Maîtrise d'ouvrage expérimentée (ASER). Technologies éprouvées. Risques logistiques identifiés et atténués.",
            "faisabilite_recommandations": "Établir un plan de gestion des risques avec des solutions de contournement pour chaque risque majeur.",
            "ppp_score": 4.0,
            "ppp_description": "Le modèle PPP est au cœur du projet. Le régime de concession est bien structuré.",
            "ppp_recommandations": "Standardiser les contrats de concession pour faciliter la réplication.",
            "impact_environnemental_score": 4.0,
            "impact_environnemental_description": "Impact environnemental très positif. Réduction de 45 000 t CO₂/an. Pas de déforestation ni d'impact sur les zones humides.",
            "impact_environnemental_recommandations": "Prévoir un plan de gestion des batteries en fin de vie.",
            "impact_emploi_score": 4.5,
            "impact_emploi_description": "Création de 120 emplois permanents locaux et 350 emplois temporaires en phase travaux. Forte valeur ajoutée pour les techniciens formés.",
            "impact_emploi_recommandations": "Contractualiser les engagements d'emploi local avec les entreprises adjudicataires.",
            "score_total": 82.5,  # /100 — sum des 12 critères hors impact_emploi
            "proposition": "Favorable",
            "recommandations": (
                "La Commission recommande l'inscription de ce projet au programme d'investissement prioritaire. "
                "Le projet présente un excellent rapport coût-bénéfice socio-économique et s'inscrit parfaitement "
                "dans les objectifs de transformation du territoire. Points de vigilance : (1) sécurisation "
                "des financements extérieurs avant lancement, (2) renforcement du volet gestion des risques "
                "logistiques, (3) intégration d'un système de monitoring centralisé dès la conception."
            ),
        },
    },

    # ── 7. ÉVALUÉ — Avis défavorable (score faible) ───────────────────────
    {
        "meta": {"stade": "évalué_défavorable", "tag": "PROJ-DEMO-07", "evaluateur": "evaluateur2",
                 "avec_fiche": True},
        "projet": {
            "titre": "Aménagement touristique de l'île de Carabane",
            "description": (
                "Développement d'une zone touristique de luxe sur l'île de Carabane (Casamance) : "
                "construction d'un hôtel 4 étoiles de 80 chambres, d'un centre de conférences "
                "de 500 places, d'un marina de 40 anneaux, d'un golf 9 trous et d'infrastructures "
                "d'accueil. Investissement total : 35 milliards FCFA, dont 70% par un investisseur privé étranger."
            ),
            "secteur": "tourisme-culture",
            "poles": "Sud (Ziguinchor, Sédhiou, Kolda)",
            "cout_estimatif": 35_000_000_000,
            "structure_soumissionnaire": "Agence Sénégalaise de Promotion Touristique",
            "organisme_tutelle": "Ministère du Tourisme et de l'Artisanat",
            "nouveaute": "projet_initial",
            "niveau_priorite": "standard",
            "type_financement": json.dumps(["prive_etranger", "budget_etat"]),
            "duree_annees": 4,
            "genre": False,
            "cc_adaptation": False,
            "lieu_soumission_region": "Ziguinchor",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire2",
            "statut": "évalué",
            "evaluateur_nom": "evaluateur2",
            "avis": "défavorable",
            "fiche_evaluation_visible": True,
            "date_soumission": date_ago(55),
            "evaluation_prealable": "dossier_evaluable",
            "evaluation_prealable_date": date_ago(48),
            "evaluation_prealable_matrice": json.dumps(MATRICE_COMPLETE),
            "evaluabilite": "evaluable",
            "evaluabilite_date": date_ago(46),
        },
        "fiche": {
            "evaluateur_nom": "evaluateur2",
            "date_evaluation": date_ago(8),
            "intitule_projet": "Aménagement touristique de l'île de Carabane",
            "cout_projet": "35 000 000 000 FCFA",
            "origine_projet": "Initiative privée présentée par un consortium d'investisseurs, reprise par l'ASPT",
            "cc_adaptation": False, "cc_attenuation": False, "genre": False,
            "articulation": "PSE Axe 3 – Gouvernance, institutions, paix et sécurité",
            "axes": "Développement du tourisme durable",
            "objectifs_strategiques": "Diversification de l'offre touristique et augmentation des recettes en devises",
            "odd": "ODD 8 (Travail décent), ODD 14 (Vie aquatique)",
            "duree_analyse": "48 mois",
            "realisation": "48 mois",
            "exploitation": "20 ans",
            "localisation": "Île de Carabane, région de Ziguinchor",
            "parties_prenantes": "ASPT, Ministère du Tourisme, investisseur privé étranger, collectivité de Carabane",
            "objectif_projet": "Créer une destination touristique haut de gamme en Casamance pour attirer la clientèle internationale.",
            "activites_principales": "Construction hôtel, marina, golf, centre de conférences. Aménagement des accès.",
            "resultats_attendus": "80 chambres, 500 employés, 5 000 touristes/an, 2 Md FCFA de recettes annuelles",
            "organisme_tutelle": "Ministère du Tourisme et de l'Artisanat",
            # Scores (/100) — total 48 → Défavorable
            "pertinence_score": 2.5,
            "pertinence_description": "La pertinence du projet pour les populations locales est limitée. Un hôtel de luxe sur une île accessible bénéficiera peu aux communautés rurales de Casamance.",
            "pertinence_recommandations": "Revoir la stratégie pour intégrer davantage les communautés locales.",
            "alignement_score": 5.0,
            "alignement_description": "Alignement partiel avec le PSE. Le projet n'intègre pas suffisamment les priorités de transformation systémique ni le contenu local.",
            "alignement_recommandations": "Retravailler le cadre logique pour mieux articuler avec les ODD et la SND.",
            "activites_couts_score": 8.0,
            "activites_couts_description": "Le coût estimé est plausible pour ce type d'infrastructure. Cependant, la part du budget d'État (30%) dans un projet à dominante privée soulève des questions.",
            "activites_couts_recommandations": "Clarifier la justification de la participation publique et le retour attendu pour l'État.",
            "equite_score": 4.0,
            "equite_description": "Faible intégration de la dimension équité. Le projet ne cible pas les populations les plus vulnérables. Risque de gentrification de l'île.",
            "equite_recommandations": "Inclure un volet d'emploi prioritaire pour les habitants de l'île.",
            "viabilite_score": 3.0,
            "viabilite_description": "La viabilité financière dépend fortement de l'investisseur privé étranger, dont l'engagement ferme n'est pas établi. Risque de désengagement élevé.",
            "viabilite_recommandations": "Exiger des garanties financières solides de l'investisseur avant tout engagement public.",
            "rentabilite_score": 2.5,
            "rentabilite_description": "Le TRI socio-économique n'a pas été calculé. Le rapport coût-bénéfice pour l'État n'est pas démontré.",
            "rentabilite_recommandations": "Fournir une analyse coût-bénéfice complète incluant les externalités.",
            "benefices_strategiques_score": 6.0,
            "benefices_strategiques_description": "Impact limité en termes de résilience et de sécurité. Faible contenu local estimé (15%).",
            "benefices_strategiques_recommandations": "Porter le contenu local à au moins 40%.",
            "perennite_score": 3.0,
            "perennite_description": "La durabilité du projet est incertaine en l'absence d'un opérateur national identifié pour la reprise à terme.",
            "perennite_recommandations": "Prévoir un mécanisme de reprise par des opérateurs locaux.",
            "avantages_intangibles_score": 5.0,
            "avantages_intangibles_description": "Valeur symbolique pour l'image touristique du Sénégal, mais retombées concrètes pour les populations locales insuffisantes.",
            "avantages_intangibles_recommandations": None,
            "faisabilite_score": 3.0,
            "faisabilite_description": "La faisabilité est compromise par l'accessibilité de l'île (transport maritime) et les risques liés à l'instabilité régionale en Casamance.",
            "faisabilite_recommandations": "Réaliser une étude de risques sécuritaires actualisée.",
            "ppp_score": 3.0,
            "ppp_description": "Le montage PPP est peu documenté. Les modalités de partage des risques entre l'État et l'investisseur ne sont pas clairement définies.",
            "ppp_recommandations": "Structurer formellement le PPP avec l'appui de l'APIX.",
            "impact_environnemental_score": 3.0,
            "impact_environnemental_description": "Risques environnementaux importants : perturbation de l'écosystème marin, risques sur la mangrove. L'étude d'impact environnemental fournie est insuffisante.",
            "impact_environnemental_recommandations": "Réaliser une ÉIES complète conforme aux normes CICES.",
            "impact_emploi_score": 3.0,
            "impact_emploi_description": "500 emplois annoncés mais la part locale n'est pas garantie. Risque d'importation de main-d'œuvre.",
            "impact_emploi_recommandations": "Contractualiser un minimum de 60% d'emplois locaux.",
            "score_total": 48.0,  # /100
            "proposition": "Défavorable",
            "recommandations": (
                "La Commission émet un avis défavorable sur ce projet en l'état. Les principales insuffisances "
                "constatées sont : (1) absence d'engagement ferme de l'investisseur privé ; (2) étude d'impact "
                "environnemental incomplète avec risques avérés sur la mangrove ; (3) faible intégration des "
                "populations locales et contenu local insuffisant ; (4) montage PPP non formalisé. "
                "Le projet pourrait être reconsidéré si le porteur soumet un dossier révisé intégrant "
                "ces recommandations, accompagné d'une ÉIES complète et de garanties financières solides."
            ),
        },
    },

    # ── 8. EN ATTENTE VALIDATION PRÉSIDENCE SCT ───────────────────────────
    {
        "meta": {"stade": "en attente validation presidencesct", "tag": "PROJ-DEMO-08",
                 "evaluateur": "evaluateur1", "avec_fiche": True},
        "projet": {
            "titre": "Modernisation du Port de Ziguinchor et développement de la filière pêche",
            "description": (
                "Réhabilitation et extension du port de Ziguinchor : construction d'un quai de pêche "
                "de 300 m, d'une halle à marée de 2 000 m², d'une chambre froide de 500 tonnes, "
                "d'une fabrique de glace de 20 t/jour, d'un chantier naval et de 150 magasins "
                "pour les mareyeurs. Dragage du chenal d'accès. Bénéficiaires : 8 000 pêcheurs "
                "et transformateurs de la Casamance."
            ),
            "secteur": "agriculture-élevage-pêche",
            "poles": "Sud (Ziguinchor, Sédhiou, Kolda)",
            "cout_estimatif": 32_000_000_000,
            "structure_soumissionnaire": "Direction des Pêches Maritimes",
            "organisme_tutelle": "Ministère des Pêches et de l'Économie Maritime",
            "nouveaute": "projet_initial",
            "niveau_priorite": "prioritaire_ant",
            "type_financement": json.dumps(["budget_etat", "bad", "ue"]),
            "duree_annees": 4,
            "genre": True,
            "cc_adaptation": True,
            "lieu_soumission_region": "Ziguinchor",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire",
            "statut": "en attente validation presidencesct",
            "evaluateur_nom": "evaluateur1",
            "avis": "favorable sous conditions",
            "fiche_evaluation_visible": True,
            "date_soumission": date_ago(80),
            "evaluation_prealable": "dossier_evaluable",
            "evaluation_prealable_date": date_ago(72),
            "evaluation_prealable_matrice": json.dumps(MATRICE_COMPLETE),
            "evaluabilite": "evaluable",
            "evaluabilite_date": date_ago(70),
            "commentaires": "Projet recommandé par l'évaluateur. En attente de validation de la Présidence du SCT.",
        },
        "fiche": {
            "evaluateur_nom": "evaluateur1",
            "date_evaluation": date_ago(15),
            "intitule_projet": "Modernisation du Port de Ziguinchor et développement de la filière pêche",
            "cout_projet": "32 000 000 000 FCFA",
            "origine_projet": "Initiative sectorielle inscrite au PDIDAS et au programme de développement des pêches de la FAO",
            "cc_adaptation": True, "cc_attenuation": False, "genre": True,
            "localisation": "Port de Ziguinchor – Région de Ziguinchor",
            "objectif_projet": "Moderniser les infrastructures portuaires de Ziguinchor pour améliorer la compétitivité de la filière pêche casamançaise et réduire les pertes post-capture.",
            "activites_principales": "Dragage, construction quai, halle à marée, chambre froide, chantier naval, formation.",
            "resultats_attendus": "8 000 pêcheurs bénéficiaires, réduction des pertes post-capture de 40%, augmentation des revenus de 25%.",
            "pertinence_score": 4.5, "pertinence_description": "Besoin critique identifié. Les infrastructures actuelles sont vétustes et inadaptées.", "pertinence_recommandations": None,
            "alignement_score": 8.0, "alignement_description": "Cohérent avec le PSE et les orientations de la vision 2050.", "alignement_recommandations": None,
            "activites_couts_score": 11.0, "activites_couts_description": "Coûts conformes aux références. Quelques postes à préciser.", "activites_couts_recommandations": "Affiner l'estimation pour le dragage.",
            "equite_score": 12.0, "equite_description": "Bénéfice direct pour les femmes transformatrices de poisson (60% des bénéficiaires).", "equite_recommandations": None,
            "viabilite_score": 3.5, "viabilite_description": "Viable avec subventions d'exploitation initiales.", "viabilite_recommandations": "Planifier la transition vers l'autofinancement sur 5 ans.",
            "rentabilite_score": 3.5, "rentabilite_description": "TRI de 14%, acceptable pour le secteur.", "rentabilite_recommandations": None,
            "benefices_strategiques_score": 12.0, "benefices_strategiques_description": "Fort impact sur la souveraineté alimentaire et la sécurité alimentaire régionale.", "benefices_strategiques_recommandations": None,
            "perennite_score": 4.0, "perennite_description": "Bonne durabilité avec plan de maintenance inclus.", "perennite_recommandations": None,
            "avantages_intangibles_score": 7.5, "avantages_intangibles_description": "Réduction des migrations des jeunes pêcheurs vers l'Europe.", "avantages_intangibles_recommandations": None,
            "faisabilite_score": 3.5, "faisabilite_description": "Faisabilité bonne avec quelques risques logistiques.", "faisabilite_recommandations": "Prévoir un plan de continuité des activités pendant les travaux.",
            "ppp_score": 3.0, "ppp_description": "Opportunités PPP pour la gestion de la chambre froide.", "ppp_recommandations": None,
            "impact_environnemental_score": 3.5, "impact_environnemental_description": "Impact limité. ÉIES réalisée et plan de gestion environnementale satisfaisant.", "impact_environnemental_recommandations": None,
            "impact_emploi_score": 4.0, "impact_emploi_description": "850 emplois permanents créés (pêche, transformation, logistique).", "impact_emploi_recommandations": None,
            "score_total": 76.0,  # /100 — 4.5+8+11+12+3.5+3.5+12+4+7.5+3.5+3+3.5
            "proposition": "Favorable sous condition",
            "recommandations": (
                "La Commission recommande le projet sous deux conditions : (1) finalisation du plan de dragage "
                "avec estimation actualisée du volume de sédiments et de la méthode d'élimination conforme "
                "aux normes environnementales ; (2) signature d'un accord de co-financement avec la BAD "
                "avant le démarrage des travaux. Sous réserve de la levée de ces conditions, le projet "
                "mérite d'être inscrit en priorité au PIP 2025-2029."
            ),
        },
    },

    # ── 9. VALIDÉ PAR PRÉSIDENCE SCT ─────────────────────────────────────
    {
        "meta": {"stade": "validé presidencesct", "tag": "PROJ-DEMO-09",
                 "evaluateur": "evaluateur2", "avec_fiche": True},
        "projet": {
            "titre": "Hub numérique et centre d'innovation de Dakar",
            "description": (
                "Construction d'un hub numérique de 12 000 m² à Dakar Plateau incluant : "
                "espace de coworking de 600 places, centre de formation aux métiers du numérique "
                "(1 200 jeunes/an), incubateur de startups (100 entreprises), datacenter "
                "Tier III de 500 serveurs, studio de production audiovisuelle et résidence "
                "d'entrepreneurs. Partenariats avec Microsoft, Orange et Google."
            ),
            "secteur": "postes-communication-télécommunications-économie numérique",
            "poles": "Dakar",
            "cout_estimatif": 21_500_000_000,
            "structure_soumissionnaire": "Agence de l'Informatique de l'État",
            "organisme_tutelle": "Ministère de la Communication, des Télécommunications et de l'Économie Numérique",
            "nouveaute": "projet_initial",
            "niveau_priorite": "prioritaire_ant",
            "type_financement": json.dumps(["budget_etat", "prive_national", "prive_etranger"]),
            "duree_annees": 3,
            "genre": True,
            "cc_attenuation": True,
            "lieu_soumission_region": "Dakar",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire",
            "statut": "validé par presidencesct",
            "evaluateur_nom": "evaluateur2",
            "avis": "favorable",
            "avis_presidencesct": "valide",
            "fiche_evaluation_visible": True,
            "date_soumission": date_ago(100),
            "evaluation_prealable": "dossier_evaluable",
            "evaluation_prealable_date": date_ago(90),
            "evaluation_prealable_matrice": json.dumps(MATRICE_COMPLETE),
            "evaluabilite": "evaluable",
            "evaluabilite_date": date_ago(88),
            "commentaires_finaux": "Projet validé par la Présidence du SCT. Transmis pour présentation au Comité de Maturation.",
        },
        "fiche": {
            "evaluateur_nom": "evaluateur2",
            "date_evaluation": date_ago(30),
            "intitule_projet": "Hub numérique et centre d'innovation de Dakar",
            "cout_projet": "21 500 000 000 FCFA",
            "origine_projet": "Initiative gouvernementale dans le cadre de la Stratégie Sénégal Numérique 2025",
            "cc_adaptation": False, "cc_attenuation": True, "genre": True,
            "localisation": "Dakar Plateau",
            "objectif_projet": "Positionner Dakar comme hub numérique régional de référence en Afrique de l'Ouest.",
            "activites_principales": "Construction, équipement, recrutement formateurs, partenariats tech.",
            "resultats_attendus": "1 200 jeunes formés/an, 100 startups incubées, 2 500 emplois créés sur 5 ans.",
            "pertinence_score": 5.0, "pertinence_description": "Pertinence maximale dans le contexte de la révolution numérique africaine.", "pertinence_recommandations": None,
            "alignement_score": 9.5, "alignement_description": "Alignement parfait avec la SND et la Vision 2050.", "alignement_recommandations": None,
            "activites_couts_score": 13.0, "activites_couts_description": "Coûts bien documentés et comparables aux références internationales.", "activites_couts_recommandations": None,
            "equite_score": 11.0, "equite_description": "Programme de bourses pour jeunes défavorisés et parité genre dans les admissions.", "equite_recommandations": None,
            "viabilite_score": 4.5, "viabilite_description": "Modèle économique hybride (formation payante, location espaces, revenus datacenter) solide.", "viabilite_recommandations": None,
            "rentabilite_score": 4.0, "rentabilite_description": "TRI de 22% sur 10 ans. Impact indirect sur l'économie numérique estimé à 50 Md FCFA.", "rentabilite_recommandations": None,
            "benefices_strategiques_score": 14.0, "benefices_strategiques_description": "Positionnement stratégique du Sénégal comme leader du numérique en Afrique de l'Ouest.", "benefices_strategiques_recommandations": None,
            "perennite_score": 4.5, "perennite_description": "Structure de gouvernance robuste avec conseil d'administration mixte public-privé.", "perennite_recommandations": None,
            "avantages_intangibles_score": 9.0, "avantages_intangibles_description": "Attractivité internationale, rétention des talents, rayonnement diplomatique.", "avantages_intangibles_recommandations": None,
            "faisabilite_score": 4.5, "faisabilite_description": "Équipe projet compétente, site identifié, partenariats confirmés.", "faisabilite_recommandations": None,
            "ppp_score": 4.5, "ppp_description": "Modèle PPP exemplaire avec Microsoft et Orange. Réplicable.", "ppp_recommandations": None,
            "impact_environnemental_score": 4.0, "impact_environnemental_description": "Bâtiment à haute performance énergétique, certification EDGE visée.", "impact_environnemental_recommandations": None,
            "impact_emploi_score": 4.5, "impact_emploi_description": "2 500 emplois en 5 ans. 70% de jeunes de moins de 35 ans.", "impact_emploi_recommandations": None,
            "score_total": 87.5,  # /100 — 5+9.5+13+11+4.5+4+14+4.5+9+4.5+4.5+4
            "proposition": "Favorable",
            "recommandations": (
                "La Commission recommande très favorablement ce projet. Il représente un investissement "
                "stratégique majeur pour le positionnement du Sénégal dans l'économie numérique africaine. "
                "Le montage financier est solide, les partenaires de renom engagés. "
                "Recommandation : inscrire en priorité 1 au PIP 2025-2029 et désigner un coordinateur "
                "interministériel pour accélérer la phase de démarrage."
            ),
        },
    },

    # ── 10. VALIDÉ PAR PRÉSIDENCE COMITÉ ─────────────────────────────────
    {
        "meta": {"stade": "validé presidencecomite", "tag": "PROJ-DEMO-10",
                 "evaluateur": "evaluateur1"},
        "projet": {
            "titre": "Programme de construction de 500 salles de classe au primaire",
            "description": (
                "Construction de 500 salles de classe dans les zones rurales déficitaires "
                "des régions de Matam, Kédougou, Sédhiou et Kaffrine. Chaque salle est équipée "
                "en mobilier scolaire, dispose de sanitaires séparés filles/garçons et d'un "
                "point d'eau. Programme inclus dans le Plan Sectoriel de l'Éducation et cofinancé "
                "par le GPE. Bénéficiaires : 22 500 élèves supplémentaires."
            ),
            "secteur": "éducation-formation-recherche",
            "poles": "Nord-Est (Matam), Sud-Est (Tambacounda, Kédougou), Sud (Ziguinchor, Sédhiou, Kolda), Centre (Kaolack, Fatick, Kaffrine)",
            "cout_estimatif": 12_500_000_000,
            "structure_soumissionnaire": "Direction des Constructions Scolaires",
            "organisme_tutelle": "Ministère de l'Éducation Nationale",
            "nouveaute": "projet_initial",
            "niveau_priorite": "prioritaire_ant",
            "type_financement": json.dumps(["budget_etat", "gpe", "unicef"]),
            "duree_annees": 2,
            "genre": True,
            "cc_adaptation": False,
            "lieu_soumission_region": "Dakar",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire",
            "statut": "validé par presidencecomite",
            "evaluateur_nom": "evaluateur1",
            "avis": "favorable",
            "avis_presidencesct": "valide",
            "decision_finale": "confirme",
            "statut_comite": "approuve_definitif",
            "fiche_evaluation_visible": True,
            "date_soumission": date_ago(130),
            "evaluation_prealable": "dossier_evaluable",
            "evaluation_prealable_date": date_ago(120),
            "evaluation_prealable_matrice": json.dumps(MATRICE_COMPLETE),
            "evaluabilite": "evaluable",
            "evaluabilite_date": date_ago(118),
            "commentaires_finaux": "Approuvé définitivement par le Comité de Maturation. Transmission au Ministère des Finances pour inscription au PIP.",
        },
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# SCRIPT PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def seed():
    with app.app_context():
        print("=" * 70)
        print("  SEED DEMO — PLASMAP")
        print("=" * 70)

        # ── Utilisateurs ────────────────────────────────────────────────────
        print("\n[1/3] Vérification / création des utilisateurs...")

        # Soumissionnaires
        soum1 = get_or_create_user(
            "soumissionnaire", "soum123", "soumissionnaire",
            "Mamadou Diallo – ANIDA",
            "m.diallo@anida.sn",
            "Agence Nationale pour l'Insertion et le Développement Agricole"
        )
        soum2 = get_or_create_user(
            "soumissionnaire2", "soum456", "soumissionnaire",
            "Aissatou Mbaye – DDT",
            "a.mbaye@ddt.gouv.sn",
            "Direction du Développement Territorial"
        )

        # Évaluateurs
        eval1 = get_or_create_user(
            "evaluateur1", "eval123", "evaluateur",
            "Dr. Ousmane Ndiaye",
            "o.ndiaye@dgppe.gouv.sn",
            "DGPPE – Direction des Études et de la Planification"
        )
        eval2 = get_or_create_user(
            "evaluateur2", "eval456", "evaluateur",
            "Dr. Fatou Sow",
            "f.sow@dgppe.gouv.sn",
            "DGPPE – Direction des Études et de la Planification"
        )

        # Secrétariat SCT
        get_or_create_user(
            "secretariat", "secret123", "secretariatsct",
            "Secrétariat du Comité Technique",
            "secretariat.sct@dgppe.gouv.sn",
            "DGPPE – Secrétariat du Comité Technique"
        )

        # Présidence SCT
        get_or_create_user(
            "presidencesct", "presct123", "presidencesct",
            "Directeur Général DGPPE",
            "dg@dgppe.gouv.sn",
            "DGPPE – Direction Générale"
        )

        # Présidence Comité
        get_or_create_user(
            "presidencecomite", "precomite123", "presidencecomite",
            "Ministre de l'Économie et de la Planification",
            "cabinet@economie.gouv.sn",
            "Ministère de l'Économie, du Plan et de la Coopération"
        )

        # Membres du Comité (compte partagé)
        get_or_create_user(
            "membrecomite", "comite123", "membrecomite",
            "Membre du Comité",
            "comite@dgppe.gouv.sn",
            "Comité de Maturation des Projets"
        )

        # Ministre de l'Économie
        get_or_create_user(
            "ministre_economie", "ministre123", "ministre_economie",
            "Cabinet du Ministre",
            "cabinet@economie.gouv.sn",
            "Ministère de l'Économie, du Plan et de la Coopération"
        )

        # Point Focal (exemple : Ministère de l'Agriculture)
        pf = get_or_create_user(
            "point_focal", "pf123", "point_focal",
            "Point Focal Agriculture",
            "pointfocal@agriculture.gouv.sn",
            "Ministère de l'Agriculture"
        )
        pf.point_focal_organisme = "Ministère de l'Agriculture"

        # Invité (grand public)
        get_or_create_user(
            "invite", "invite123", "invite",
            "Visiteur",
            None,
            "Grand public"
        )

        # Administrateur
        get_or_create_user(
            "admin", "admin123", "admin",
            "Administrateur PLASMAP",
            "admin@dgppe.gouv.sn",
            "DGPPE"
        )

        db.session.commit()

        # ── Projets ─────────────────────────────────────────────────────────
        print("\n[2/3] Création des projets de démonstration...")
        compteur = 0

        for entry in PROJETS:
            meta = entry["meta"]
            pdata = entry["projet"].copy()

            # Vérifier doublon sur titre
            existing = Project.query.filter_by(titre=pdata["titre"]).first()
            if existing:
                print(f"   ⚠ Déjà existant, ignoré : {pdata['titre'][:55]}...")
                continue

            # Résoudre soumissionnaire_id
            auteur = pdata.pop("auteur_nom", "soumissionnaire")
            if auteur == "soumissionnaire2":
                soum_user = soum2
            else:
                soum_user = soum1

            projet = Project(
                soumissionnaire_id=soum_user.id,
                auteur_nom=soum_user.username,
                **pdata,
            )
            db.session.add(projet)
            db.session.flush()  # pour obtenir projet.id

            # Historique de base
            add_historique(projet.id, "Projet soumis", soum_user.display_name or soum_user.username, "soumissionnaire", pdata.get("date_soumission"))

            stade = meta["stade"]
            eval_user = eval1 if meta.get("evaluateur") == "evaluateur1" else eval2

            if stade in ("assigné", "en évaluation", "compléments demandés",
                         "compléments fournis", "évalué_favorable", "évalué_défavorable",
                         "en attente validation presidencesct",
                         "validé presidencesct", "validé presidencecomite"):
                add_historique(projet.id, f"Projet assigné à {eval_user.display_name}", "Secrétariat SCT", "secretariatsct", date_ago(10))

            if stade in ("en évaluation", "évalué_favorable", "évalué_défavorable",
                         "en attente validation presidencesct",
                         "validé presidencesct", "validé presidencecomite"):
                add_historique(projet.id, "Évaluation démarrée", eval_user.display_name, "evaluateur", date_ago(8))

            if stade in ("compléments demandés", "compléments fournis"):
                add_historique(projet.id, "Compléments demandés au soumissionnaire", eval_user.display_name, "evaluateur", date_ago(7))

            if stade == "compléments fournis":
                add_historique(projet.id, "Compléments fournis par le soumissionnaire", soum_user.display_name or soum_user.username, "soumissionnaire", date_ago(4))

            # ── Fiche d'évaluation ───────────────────────────────────────
            if meta.get("avec_fiche") and "fiche" in entry:
                fdata = entry["fiche"].copy()
                fiche = FicheEvaluation(
                    project_id=projet.id,
                    reference_fiche=f"EVAL-{projet.id}-{fdata['date_evaluation'].strftime('%Y%m%d')}",
                    **fdata,
                )
                db.session.add(fiche)
                add_historique(projet.id, f"Fiche d'évaluation soumise (score : {fdata.get('score_total')})", eval_user.display_name, "evaluateur", fdata["date_evaluation"])

            db.session.commit()
            compteur += 1
            print(f"   ✔ [{stade.upper():35s}] {pdata['titre'][:52]}...")

        # ── Résumé ───────────────────────────────────────────────────────────
        print(f"\n[3/3] Terminé. {compteur} projet(s) créé(s).")
        total = Project.query.filter(Project.deleted_at.is_(None)).count()
        print(f"   Total projets actifs en base : {total}")
        print("=" * 70)


if __name__ == "__main__":
    seed()
    sys.exit(0)
