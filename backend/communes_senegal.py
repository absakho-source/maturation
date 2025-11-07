"""
Liste des principales communes du Sénégal (environ 100 communes majeures)
Pour liste complète : ~550 communes
"""

COMMUNES_PRINCIPALES = [
    # Région de Dakar
    "Commune de Dakar-Plateau",
    "Commune de Médina",
    "Commune de Fann-Point E-Amitié",
    "Commune de Gueule Tapée-Fass-Colobane",
    "Commune de Sicap Liberté",
    "Commune de HLM",
    "Commune de Grand-Dakar",
    "Commune de Biscuiterie",
    "Commune de Dieuppeul-Derklé",
    "Commune de Mermoz-Sacré Cœur",
    "Commune de Ouakam",
    "Commune de Ngor",
    "Commune de Yoff",
    "Commune de Hann Bel-Air",
    "Commune de Grand Yoff",
    "Commune de Parcelles Assainies",
    "Commune de Cambérène",
    "Commune de Pikine",
    "Commune de Thiaroye",
    "Commune de Mbao",
    "Commune de Keur Massar",
    "Commune de Guédiawaye",
    "Commune de Rufisque",
    "Commune de Bargny",
    "Commune de Diamniadio",
    "Commune de Sébikotane",

    # Région de Thiès
    "Commune de Thiès-Nord",
    "Commune de Thiès-Sud",
    "Commune de Thiès-Est",
    "Commune de Thiès-Ouest",
    "Commune de Mbour",
    "Commune de Joal-Fadiouth",
    "Commune de Saly Portudal",
    "Commune de Tivaouane",
    "Commune de Mékhé",
    "Commune de Pout",
    "Commune de Khombole",

    # Région de Diourbel
    "Commune de Diourbel",
    "Commune de Touba",
    "Commune de Mbacké",
    "Commune de Bambey",

    # Région de Kaolack
    "Commune de Kaolack",
    "Commune de Nioro du Rip",
    "Commune de Guinguinéo",
    "Commune de Kaffrine",

    # Région de Fatick
    "Commune de Fatick",
    "Commune de Foundiougne",
    "Commune de Gossas",

    # Région de Saint-Louis
    "Commune de Saint-Louis",
    "Commune de Dagana",
    "Commune de Podor",
    "Commune de Richard Toll",
    "Commune de Ross Béthio",

    # Région de Louga
    "Commune de Louga",
    "Commune de Kébémer",
    "Commune de Linguère",

    # Région de Matam
    "Commune de Matam",
    "Commune de Kanel",
    "Commune de Ourossogui",

    # Région de Tambacounda
    "Commune de Tambacounda",
    "Commune de Bakel",
    "Commune de Goudiry",
    "Commune de Koumpentoum",
    "Commune de Kidira",

    # Région de Kolda
    "Commune de Kolda",
    "Commune de Vélingara",
    "Commune de Médina Yoro Foulah",

    # Région de Ziguinchor
    "Commune de Ziguinchor",
    "Commune de Bignona",
    "Commune de Oussouye",
    "Commune de Thionck Essyl",

    # Région de Sédhiou
    "Commune de Sédhiou",
    "Commune de Bounkiling",
    "Commune de Goudomp",

    # Région de Kédougou
    "Commune de Kédougou",
    "Commune de Saraya",
    "Commune de Salémata",

    # Région de Kaffrine
    "Commune de Kaffrine",
    "Commune de Koungheul",
    "Commune de Birkelane",
    "Commune de Malem-Hodar",
]

# Fonction pour recherche/auto-complétion
def search_communes(query):
    """Recherche de communes par terme"""
    if not query:
        return sorted(COMMUNES_PRINCIPALES)

    query = query.lower()
    results = [c for c in COMMUNES_PRINCIPALES if query in c.lower()]
    return sorted(results)

def get_all_communes():
    """Retourne toutes les communes triées"""
    return sorted(COMMUNES_PRINCIPALES)

def get_communes_by_departement():
    """Retourne les communes organisées par département"""
    # Organisation simplifiée basée sur les principales villes
    communes_dict = {
        # Dakar
        "Dakar": [
            "Commune de Dakar-Plateau", "Commune de Médina", "Commune de Fann-Point E-Amitié",
            "Commune de Gueule Tapée-Fass-Colobane", "Commune de Sicap Liberté", "Commune de HLM",
            "Commune de Grand-Dakar", "Commune de Biscuiterie", "Commune de Dieuppeul-Derklé",
            "Commune de Mermoz-Sacré Cœur", "Commune de Ouakam", "Commune de Ngor",
            "Commune de Yoff", "Commune de Hann Bel-Air", "Commune de Grand Yoff"
        ],
        "Pikine": [
            "Commune de Pikine", "Commune de Thiaroye", "Commune de Mbao",
            "Commune de Parcelles Assainies", "Commune de Keur Massar"
        ],
        "Guédiawaye": ["Commune de Guédiawaye", "Commune de Cambérène"],
        "Rufisque": ["Commune de Rufisque", "Commune de Bargny", "Commune de Diamniadio", "Commune de Sébikotane"],

        # Thiès
        "Thiès": ["Commune de Thiès-Nord", "Commune de Thiès-Sud", "Commune de Thiès-Est", "Commune de Thiès-Ouest", "Commune de Pout", "Commune de Khombole"],
        "Mbour": ["Commune de Mbour", "Commune de Joal-Fadiouth", "Commune de Saly Portudal"],
        "Tivaouane": ["Commune de Tivaouane", "Commune de Mékhé"],

        # Diourbel
        "Diourbel": ["Commune de Diourbel", "Commune de Touba"],
        "Mbacké": ["Commune de Mbacké"],
        "Bambey": ["Commune de Bambey"],

        # Kaolack
        "Kaolack": ["Commune de Kaolack"],
        "Guinguinéo": ["Commune de Guinguinéo"],
        "Nioro du Rip": ["Commune de Nioro du Rip"],

        # Kaffrine
        "Kaffrine": ["Commune de Kaffrine"],
        "Birkelane": ["Commune de Birkelane"],
        "Koungheul": ["Commune de Koungheul"],
        "Malem-Hodar": ["Commune de Malem-Hodar"],

        # Fatick
        "Fatick": ["Commune de Fatick"],
        "Foundiougne": ["Commune de Foundiougne"],
        "Gossas": ["Commune de Gossas"],

        # Saint-Louis
        "Saint-Louis": ["Commune de Saint-Louis", "Commune de Ross Béthio"],
        "Dagana": ["Commune de Dagana", "Commune de Richard Toll"],
        "Podor": ["Commune de Podor"],

        # Louga
        "Louga": ["Commune de Louga"],
        "Kébémer": ["Commune de Kébémer"],
        "Linguère": ["Commune de Linguère"],

        # Matam
        "Matam": ["Commune de Matam", "Commune de Ourossogui"],
        "Kanel": ["Commune de Kanel"],

        # Tambacounda
        "Tambacounda": ["Commune de Tambacounda", "Commune de Koumpentoum"],
        "Bakel": ["Commune de Bakel"],
        "Goudiry": ["Commune de Goudiry", "Commune de Kidira"],

        # Kolda
        "Kolda": ["Commune de Kolda"],
        "Vélingara": ["Commune de Vélingara"],
        "Médina Yoro Foulah": ["Commune de Médina Yoro Foulah"],

        # Ziguinchor
        "Ziguinchor": ["Commune de Ziguinchor", "Commune de Thionck Essyl"],
        "Bignona": ["Commune de Bignona"],
        "Oussouye": ["Commune de Oussouye"],

        # Sédhiou
        "Sédhiou": ["Commune de Sédhiou"],
        "Bounkiling": ["Commune de Bounkiling"],
        "Goudomp": ["Commune de Goudomp"],

        # Kédougou
        "Kédougou": ["Commune de Kédougou"],
        "Saraya": ["Commune de Saraya"],
        "Salémata": ["Commune de Salémata"],
    }
    return communes_dict
