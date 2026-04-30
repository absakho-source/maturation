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
            "evaluation_prealable_commentaire": "Dossier complet. Le projet est recevable.",
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
            "evaluation_prealable_commentaire": "Dossier incomplet. Documents manquants à fournir sous 15 jours.",
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
            "evaluation_prealable_commentaire": "Dossier incomplet. Documents manquants à fournir sous 15 jours.",
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
            "evaluation_prealable_commentaire": "Dossier complet. Le projet est recevable.",
            "evaluabilite": "evaluable",
            "evaluabilite_date": date_ago(50),
        },
        "fiche": {
            "evaluateur_nom": "evaluateur1",
            "date_evaluation": date_ago(5),
            "score_total": 82.5,
            "proposition": "Favorable",
            "recommandations": "La Commission recommande l'inscription au programme d'investissement prioritaire. Excellent rapport coût-bénéfice. Points de vigilance : sécurisation des financements extérieurs, gestion des risques logistiques, monitoring centralisé.",
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
            "evaluation_prealable_commentaire": "Dossier complet. Le projet est recevable.",
            "evaluabilite": "evaluable",
            "evaluabilite_date": date_ago(46),
        },
        "fiche": {
            "evaluateur_nom": "evaluateur2",
            "date_evaluation": date_ago(8),
            "score_total": 48.0,
            "proposition": "Défavorable",
            "recommandations": "Avis défavorable. Insuffisances : absence d'engagement ferme de l'investisseur privé, ÉIES incomplète, faible intégration des populations locales, montage PPP non formalisé.",
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
            "evaluation_prealable_commentaire": "Dossier complet. Le projet est recevable.",
            "evaluabilite": "evaluable",
            "evaluabilite_date": date_ago(70),
            "commentaires": "Projet recommandé sous conditions par l'évaluateur. En attente d'inscription à l'ordre du jour.",
        },
        "fiche": {
            "evaluateur_nom": "evaluateur1",
            "date_evaluation": date_ago(15),
            "score_total": 76.0,
            "proposition": "Favorable sous conditions",
            "recommandations": "Projet recommandé sous conditions : (1) finaliser le plan de dragage conforme aux normes environnementales ; (2) signer l'accord de co-financement BAD avant démarrage.",
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
            "evaluation_prealable_commentaire": "Dossier complet. Le projet est recevable.",
            "evaluabilite": "evaluable",
            "evaluabilite_date": date_ago(88),
            "commentaires_finaux": "Avis validé par le Secrétariat SCT. Inscrit à l'ordre du jour du Comité de Maturation.",
        },
        "fiche": {
            "evaluateur_nom": "evaluateur2",
            "date_evaluation": date_ago(30),
            "score_total": 87.5,
            "proposition": "Favorable",
            "recommandations": "Recommandation très favorable. Investissement stratégique majeur pour l'économie numérique. Inscrire en priorité 1 au PIP 2025-2029.",
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
            "evaluation_prealable_commentaire": "Dossier complet. Le projet est recevable.",
            "evaluabilite": "evaluable",
            "evaluabilite_date": date_ago(118),
            "commentaires_finaux": "Approuvé définitivement par le Comité de Maturation. Transmission au Ministère des Finances pour inscription au PIP.",
        },
    },

    # ── 11-20. PROJETS COMPLÉMENTAIRES (couverture 8 pôles + montants variés) ──

    {
        "meta": {"stade": "évalué_favorable", "tag": "PROJ-DEMO-11", "evaluateur": "evaluateur1", "avec_fiche": True},
        "projet": {
            "titre": "Autoroute Dakar-Saint-Louis (tronçon Thiès-Louga)",
            "description": "Construction de 180 km d'autoroute reliant Thiès à Louga, avec échangeurs et aires de repos.",
            "secteur": "transport-infrastructure",
            "poles": "Diourbel-Louga",
            "cout_estimatif": 95_000_000_000,
            "structure_soumissionnaire": "AGEROUTE",
            "organisme_tutelle": "Ministère des Infrastructures et des Transports Terrestres",
            "nouveaute": "projet_initial",
            "niveau_priorite": "prioritaire_ant",
            "type_financement": json.dumps(["budget_etat", "bad", "prive_etranger"]),
            "duree_annees": 5,
            "lieu_soumission_region": "Diourbel",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire",
            "statut": "évalué",
            "evaluateur_nom": "evaluateur1",
            "avis": "favorable",
            "fiche_evaluation_visible": True,
            "date_soumission": date_ago(90),
            "evaluation_prealable": "dossier_evaluable",
            "evaluation_prealable_date": date_ago(82),
            "evaluation_prealable_commentaire": "Dossier complet.",
            "evaluabilite": "evaluable",
            "evaluabilite_date": date_ago(80),
        },
        "fiche": {
            "evaluateur_nom": "evaluateur1", "date_evaluation": date_ago(20),
            "score_total": 88.0, "proposition": "Favorable",
            "recommandations": "Projet structurant majeur. Accélérer les études d'impact et le bouclage financier.",
        },
    },

    {
        "meta": {"stade": "soumis", "tag": "PROJ-DEMO-12"},
        "projet": {
            "titre": "Plateforme logistique et marché de gros de Diourbel",
            "description": "Construction d'un marché de gros moderne avec chambres froides, entrepôts et plateforme de distribution régionale.",
            "secteur": "commerce-secteur-privé",
            "poles": "Diourbel-Louga",
            "cout_estimatif": 4_500_000_000,
            "structure_soumissionnaire": "Chambre de Commerce de Diourbel",
            "organisme_tutelle": "Ministère du Commerce et des PME",
            "nouveaute": "projet_initial",
            "niveau_priorite": "standard",
            "type_financement": json.dumps(["budget_etat", "prive_national"]),
            "duree_annees": 2,
            "lieu_soumission_region": "Diourbel",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire2",
            "statut": "soumis",
            "date_soumission": date_ago(2),
        },
    },

    {
        "meta": {"stade": "assigné", "tag": "PROJ-DEMO-13", "evaluateur": "evaluateur2"},
        "projet": {
            "titre": "Extension du réseau d'assainissement de Dakar-Pikine",
            "description": "Pose de 45 km de collecteurs d'eaux usées et construction de 3 stations de pompage dans la banlieue de Dakar.",
            "secteur": "eau-assainissement",
            "poles": "Dakar",
            "cout_estimatif": 42_000_000_000,
            "structure_soumissionnaire": "ONAS",
            "organisme_tutelle": "Ministère de l'Eau et de l'Assainissement",
            "nouveaute": "projet_initial",
            "niveau_priorite": "prioritaire_ant",
            "type_financement": json.dumps(["budget_etat", "bm", "afd"]),
            "duree_annees": 4,
            "lieu_soumission_region": "Dakar",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire",
            "statut": "assigné",
            "evaluateur_nom": "evaluateur2",
            "date_soumission": date_ago(15),
        },
    },

    {
        "meta": {"stade": "évalué_favorable", "tag": "PROJ-DEMO-14", "evaluateur": "evaluateur2", "avec_fiche": True},
        "projet": {
            "titre": "Barrage anti-sel et aménagement rizicole de la vallée du Soungrougrou",
            "description": "Construction d'un barrage anti-sel sur le Soungrougrou et aménagement de 3 000 ha de rizières.",
            "secteur": "agriculture-élevage-pêche",
            "poles": "Sud (Ziguinchor, Sédhiou, Kolda)",
            "cout_estimatif": 8_500_000_000,
            "structure_soumissionnaire": "SAED",
            "organisme_tutelle": "Ministère de l'Agriculture",
            "nouveaute": "projet_initial",
            "niveau_priorite": "prioritaire_ant",
            "type_financement": json.dumps(["budget_etat", "bad"]),
            "duree_annees": 3,
            "lieu_soumission_region": "Sédhiou",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire2",
            "statut": "évalué",
            "evaluateur_nom": "evaluateur2",
            "avis": "favorable sous conditions",
            "fiche_evaluation_visible": True,
            "date_soumission": date_ago(70),
            "evaluation_prealable": "dossier_evaluable",
            "evaluation_prealable_date": date_ago(62),
            "evaluation_prealable_commentaire": "Recevable.",
            "evaluabilite": "evaluable",
            "evaluabilite_date": date_ago(60),
        },
        "fiche": {
            "evaluateur_nom": "evaluateur2", "date_evaluation": date_ago(12),
            "score_total": 72.5, "proposition": "Favorable sous conditions",
            "recommandations": "Conditionné à l'obtention de l'ÉIES et à la sécurisation foncière des 3 000 ha.",
        },
    },

    {
        "meta": {"stade": "soumis", "tag": "PROJ-DEMO-15"},
        "projet": {
            "titre": "Centre hospitalier régional de Matam (niveau 2)",
            "description": "Construction et équipement d'un hôpital régional de 120 lits à Matam.",
            "secteur": "santé-action sociale",
            "poles": "Nord-Est (Matam)",
            "cout_estimatif": 15_000_000_000,
            "structure_soumissionnaire": "Direction des Établissements de Santé",
            "organisme_tutelle": "Ministère de la Santé et de l'Action Sociale",
            "nouveaute": "projet_initial",
            "niveau_priorite": "prioritaire_ant",
            "type_financement": json.dumps(["budget_etat", "bid"]),
            "duree_annees": 3,
            "genre": True,
            "lieu_soumission_region": "Matam",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire",
            "statut": "soumis",
            "date_soumission": date_ago(5),
        },
    },

    {
        "meta": {"stade": "en évaluation", "tag": "PROJ-DEMO-16", "evaluateur": "evaluateur1"},
        "projet": {
            "titre": "Cité universitaire et campus numérique de Thiès",
            "description": "Construction d'une cité universitaire de 2 000 lits et d'un campus numérique connecté pour l'Université de Thiès.",
            "secteur": "éducation-formation-recherche",
            "poles": "Thiès",
            "cout_estimatif": 18_500_000_000,
            "structure_soumissionnaire": "Université Iba Der Thiam de Thiès",
            "organisme_tutelle": "Ministère de l'Enseignement Supérieur",
            "nouveaute": "projet_initial",
            "niveau_priorite": "standard",
            "type_financement": json.dumps(["budget_etat", "bm"]),
            "duree_annees": 3,
            "lieu_soumission_region": "Thiès",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire2",
            "statut": "en évaluation",
            "evaluateur_nom": "evaluateur1",
            "date_soumission": date_ago(25),
            "evaluation_prealable": "dossier_evaluable",
            "evaluation_prealable_date": date_ago(18),
            "evaluation_prealable_commentaire": "Recevable.",
            "evaluabilite": "evaluable",
            "evaluabilite_date": date_ago(16),
        },
    },

    {
        "meta": {"stade": "assigné", "tag": "PROJ-DEMO-17", "evaluateur": "evaluateur1"},
        "projet": {
            "titre": "Centrale solaire photovoltaïque de Louga (50 MW)",
            "description": "Installation d'une centrale solaire de 50 MW avec stockage batterie de 20 MWh à Louga.",
            "secteur": "énergies-mines",
            "poles": "Diourbel-Louga",
            "cout_estimatif": 38_000_000_000,
            "structure_soumissionnaire": "SENELEC",
            "organisme_tutelle": "Ministère de l'Énergie, du Pétrole et des Mines",
            "nouveaute": "projet_initial",
            "niveau_priorite": "prioritaire_ant",
            "type_financement": json.dumps(["ppp", "prive_etranger"]),
            "duree_annees": 2,
            "cc_attenuation": True,
            "lieu_soumission_region": "Louga",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire",
            "statut": "assigné",
            "evaluateur_nom": "evaluateur1",
            "date_soumission": date_ago(10),
        },
    },

    {
        "meta": {"stade": "évalué_favorable", "tag": "PROJ-DEMO-18", "evaluateur": "evaluateur1", "avec_fiche": True},
        "projet": {
            "titre": "Aménagement hydro-agricole de la vallée du fleuve (Podor-Matam)",
            "description": "Réhabilitation de 5 000 ha de périmètres irrigués le long du fleuve Sénégal entre Podor et Matam.",
            "secteur": "agriculture-élevage-pêche",
            "poles": "Nord (Saint-Louis)",
            "cout_estimatif": 52_000_000_000,
            "structure_soumissionnaire": "SAED",
            "organisme_tutelle": "Ministère de l'Agriculture",
            "nouveaute": "phase_2",
            "niveau_priorite": "prioritaire_ant",
            "type_financement": json.dumps(["budget_etat", "bad", "bm"]),
            "duree_annees": 5,
            "cc_adaptation": True,
            "lieu_soumission_region": "Saint-Louis",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire",
            "statut": "évalué",
            "evaluateur_nom": "evaluateur1",
            "avis": "favorable",
            "fiche_evaluation_visible": True,
            "date_soumission": date_ago(95),
            "evaluation_prealable": "dossier_evaluable",
            "evaluation_prealable_date": date_ago(88),
            "evaluation_prealable_commentaire": "Dossier complet.",
            "evaluabilite": "evaluable",
            "evaluabilite_date": date_ago(86),
        },
        "fiche": {
            "evaluateur_nom": "evaluateur1", "date_evaluation": date_ago(25),
            "score_total": 85.0, "proposition": "Favorable",
            "recommandations": "Projet à fort impact sur la sécurité alimentaire. Coordination nécessaire avec l'OMVS.",
        },
    },

    {
        "meta": {"stade": "soumis", "tag": "PROJ-DEMO-19"},
        "projet": {
            "titre": "Zone économique spéciale de Kaolack (phase 1)",
            "description": "Viabilisation de 150 ha pour une zone économique spéciale dédiée à l'agro-industrie et la transformation de l'arachide.",
            "secteur": "industrie-mines",
            "poles": "Centre (Kaolack, Fatick, Kaffrine)",
            "cout_estimatif": 25_000_000_000,
            "structure_soumissionnaire": "APIX",
            "organisme_tutelle": "Ministère de l'Industrie et du Commerce",
            "nouveaute": "projet_initial",
            "niveau_priorite": "standard",
            "type_financement": json.dumps(["budget_etat", "prive_national", "prive_etranger"]),
            "duree_annees": 3,
            "lieu_soumission_region": "Kaolack",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire2",
            "statut": "soumis",
            "date_soumission": date_ago(1),
        },
    },

    {
        "meta": {"stade": "en évaluation", "tag": "PROJ-DEMO-20", "evaluateur": "evaluateur2"},
        "projet": {
            "titre": "Programme de résilience climatique du bassin arachidier",
            "description": "Reboisement de 10 000 ha, restauration des sols dégradés et mise en place de 200 bassins de rétention dans les régions de Kaffrine et Fatick.",
            "secteur": "environnement-changement-climatique",
            "poles": "Centre (Kaolack, Fatick, Kaffrine)",
            "cout_estimatif": 7_200_000_000,
            "structure_soumissionnaire": "Direction des Eaux et Forêts",
            "organisme_tutelle": "Ministère de l'Environnement et de la Transition Écologique",
            "nouveaute": "projet_initial",
            "niveau_priorite": "standard",
            "type_financement": json.dumps(["budget_etat", "fonds_vert_climat"]),
            "duree_annees": 4,
            "cc_adaptation": True,
            "cc_attenuation": True,
            "genre": True,
            "lieu_soumission_region": "Kaffrine",
            "lieu_soumission_pays": "Sénégal",
            "auteur_nom": "soumissionnaire",
            "statut": "en évaluation",
            "evaluateur_nom": "evaluateur2",
            "date_soumission": date_ago(20),
            "evaluation_prealable": "dossier_evaluable",
            "evaluation_prealable_date": date_ago(14),
            "evaluation_prealable_commentaire": "Recevable.",
            "evaluabilite": "evaluable",
            "evaluabilite_date": date_ago(12),
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
