"""
Données territoriales et administratives du Sénégal
Pour le système de validation des comptes
"""

# Les 14 régions du Sénégal
REGIONS = [
    "Dakar",
    "Thiès",
    "Diourbel",
    "Fatick",
    "Kaolack",
    "Kaffrine",
    "Kolda",
    "Louga",
    "Matam",
    "Saint-Louis",
    "Sédhiou",
    "Tambacounda",
    "Kédougou",
    "Ziguinchor"
]

# Les 46 départements organisés par région
DEPARTEMENTS = {
    "Dakar": ["Dakar", "Pikine", "Guédiawaye", "Rufisque"],
    "Thiès": ["Thiès", "Mbour", "Tivaouane"],
    "Diourbel": ["Diourbel", "Bambey", "Mbacké"],
    "Fatick": ["Fatick", "Foundiougne", "Gossas"],
    "Kaolack": ["Kaolack", "Guinguinéo", "Nioro du Rip"],
    "Kaffrine": ["Kaffrine", "Birkelane", "Koungheul", "Malem-Hodar"],
    "Kolda": ["Kolda", "Médina Yoro Foulah", "Vélingara"],
    "Louga": ["Louga", "Kébémer", "Linguère"],
    "Matam": ["Matam", "Kanel", "Ranérou-Ferlo"],
    "Saint-Louis": ["Saint-Louis", "Dagana", "Podor"],
    "Sédhiou": ["Sédhiou", "Bounkiling", "Goudomp"],
    "Tambacounda": ["Tambacounda", "Bakel", "Goudiry", "Koumpentoum"],
    "Kédougou": ["Kédougou", "Saraya", "Salémata"],
    "Ziguinchor": ["Ziguinchor", "Bignona", "Oussouye"]
}

# Liste des principaux ministères du Sénégal
MINISTERES = [
    "Ministère de l'Économie, du Plan et de la Coopération",
    "Ministère des Finances et du Budget",
    "Ministère de la Santé et de l'Action Sociale",
    "Ministère de l'Éducation Nationale",
    "Ministère de l'Enseignement Supérieur, de la Recherche et de l'Innovation",
    "Ministère de l'Agriculture, de la Souveraineté Alimentaire et de l'Élevage",
    "Ministère des Infrastructures et des Transports Terrestres et Aériens",
    "Ministère de l'Hydraulique et de l'Assainissement",
    "Ministère de l'Urbanisme, des Collectivités Territoriales et de l'Aménagement des Territoires",
    "Ministère de l'Intérieur et de la Sécurité Publique",
    "Ministère de la Justice",
    "Ministère des Affaires Étrangères et des Sénégalais de l'Extérieur",
    "Ministère des Forces Armées",
    "Ministère de l'Environnement et de la Transition Écologique",
    "Ministère de l'Énergie, du Pétrole et des Mines",
    "Ministère de l'Industrie et du Commerce",
    "Ministère du Tourisme et de l'Artisanat",
    "Ministère de la Jeunesse, des Sports et de la Culture",
    "Ministère de la Femme, de la Famille et de la Protection des Enfants",
    "Ministère du Travail, de l'Emploi et des Relations avec les Institutions",
    "Ministère de la Communication, des Télécommunications et de l'Économie Numérique",
    "Ministère de la Pêche et de l'Économie Maritime",
    "Ministère de la Fonction Publique et de la Réforme du Service Public",
    "Autre administration (à préciser)"
]

# Principales agences et établissements publics
AGENCES = [
    "APIX SA - Agence de Promotion des Investissements et des Grands Travaux",
    "ARMP - Agence de Régulation des Marchés Publics",
    "ADIE - Agence de l'Informatique de l'État",
    "SENELEC - Société Nationale d'Électricité du Sénégal",
    "SENEAU - Société Nationale des Eaux du Sénégal",
    "SDE - Sénégalaise des Eaux",
    "OFOR - Office des Forages Ruraux",
    "ANER - Agence Nationale des Énergies Renouvelables",
    "AGEROUTE - Agence des Travaux et de Gestion des Routes",
    "ANAT - Agence Nationale de l'Aménagement du Territoire",
    "ANSD - Agence Nationale de la Statistique et de la Démographie",
    "ASER - Agence Sénégalaise d'Électrification Rurale",
    "BMHSN - Bureau Opérationnel de Suivi du Plan Sénégal Émergent",
    "CDC - Caisse des Dépôts et Consignations",
    "COSEC - Commissariat à la Sécurité Alimentaire",
    "DER - Délégation à l'Entrepreneuriat Rapide",
    "FONSIS - Fonds Souverain d'Investissements Stratégiques",
    "ISRA - Institut Sénégalais de Recherches Agricoles",
    "ONAS - Office National de l'Assainissement du Sénégal",
    "PROMOVILLES - Programme de Modernisation des Villes",
    "UGB - Université Gaston Berger",
    "UCAD - Université Cheikh Anta Diop",
    "Autre agence (à préciser)"
]

def get_all_departements():
    """Retourne une liste plate de tous les départements"""
    result = []
    for region, deps in DEPARTEMENTS.items():
        result.extend(deps)
    return sorted(result)

def get_departements_by_region(region):
    """Retourne les départements d'une région donnée"""
    return DEPARTEMENTS.get(region, [])
