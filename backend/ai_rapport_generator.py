"""
Générateur de rapports élaborés avec analyse IA
Génère des insights, analyses de tendances et résumés exécutifs
"""

from models import Project, User
from sqlalchemy import func
from datetime import datetime, timedelta

def generer_resume_executif(projects):
    """Génère un résumé exécutif en langage naturel"""
    total = len(projects)
    if total == 0:
        return "Aucun projet n'a été soumis pour le moment."

    # Analyser les secteurs dominants
    secteurs = {}
    for p in projects:
        secteur = p.secteur or 'Non spécifié'
        secteurs[secteur] = secteurs.get(secteur, 0) + 1

    secteur_dominant = max(secteurs.items(), key=lambda x: x[1])
    pct_dominant = round(secteur_dominant[1] / total * 100, 1)

    # Analyser les pôles
    poles = {}
    for p in projects:
        pole = p.poles or 'Non spécifié'
        poles[pole] = poles.get(pole, 0) + 1

    pole_dominant = max(poles.items(), key=lambda x: x[1])

    # Analyser les statuts
    approuves = len([p for p in projects if p.statut == 'approuvé'])
    rejetes = len([p for p in projects if p.statut == 'rejeté'])
    en_cours = total - approuves - rejetes

    taux_approbation = round(approuves / total * 100, 1) if total > 0 else 0

    # Générer le résumé
    resume = f"""La plateforme compte actuellement {total} projet(s) soumis. Le secteur {secteur_dominant[0]} domine avec {secteur_dominant[1]} projet(s) ({pct_dominant}% du total). """

    resume += f"""Le pôle territorial {pole_dominant[0]} est le plus représenté avec {pole_dominant[1]} projet(s). """

    if approuves > 0:
        resume += f"""{approuves} projet(s) ont été approuvés (taux d'approbation: {taux_approbation}%), """

    if rejetes > 0:
        resume += f"""{rejetes} ont été rejetés, """

    if en_cours > 0:
        resume += f"""et {en_cours} sont encore en cours de traitement."""

    return resume


def analyser_tendances(projects):
    """Analyse les tendances temporelles et sectorielles"""
    tendances = {
        'evolution': {},
        'secteurs_croissance': {},
        'poles_sous_representes': []
    }

    if not projects:
        return tendances

    # Évolution temporelle (30 derniers jours)
    aujourd_hui = datetime.now()
    il_y_a_30j = aujourd_hui - timedelta(days=30)

    projets_recents = [p for p in projects if p.date_soumission and p.date_soumission >= il_y_a_30j]
    projets_anciens = [p for p in projects if p.date_soumission and p.date_soumission < il_y_a_30j]

    if len(projets_anciens) > 0:
        croissance = ((len(projets_recents) - len(projets_anciens)) / len(projets_anciens)) * 100
        tendances['evolution']['texte'] = f"Les soumissions ont {'augmenté' if croissance > 0 else 'diminué'} de {abs(round(croissance, 1))}% ce dernier mois."
        tendances['evolution']['croissance'] = croissance
    else:
        tendances['evolution']['texte'] = f"{len(projets_recents)} projet(s) soumis ce dernier mois."

    # Secteurs en croissance
    secteurs = {}
    cout_par_secteur = {}
    for p in projects:
        secteur = p.secteur or 'Non spécifié'
        secteurs[secteur] = secteurs.get(secteur, 0) + 1
        cout_par_secteur[secteur] = cout_par_secteur.get(secteur, 0) + (p.cout_estimatif or 0)

    if secteurs:
        top_secteur = max(secteurs.items(), key=lambda x: x[1])
        pct_secteur = round(top_secteur[1] / len(projects) * 100, 1)
        tendances['secteurs_croissance']['dominant'] = {
            'nom': top_secteur[0],
            'nombre': top_secteur[1],
            'pourcentage': pct_secteur,
            'cout_total': cout_par_secteur[top_secteur[0]]
        }

    # Pôles sous-représentés (moins de 10% des projets)
    poles = {}
    for p in projects:
        pole = p.poles or 'Non spécifié'
        poles[pole] = poles.get(pole, 0) + 1

    seuil = len(projects) * 0.1
    poles_faibles = [(pole, count) for pole, count in poles.items() if count < seuil and pole != 'Non spécifié']
    tendances['poles_sous_representes'] = poles_faibles

    return tendances


def analyser_finances(projects):
    """Analyse financière détaillée"""
    analyse = {
        'cout_total': 0,
        'cout_moyen': 0,
        'cout_median': 0,
        'distribution': {},
        'concentration': {}
    }

    if not projects:
        return analyse

    couts = [p.cout_estimatif or 0 for p in projects]
    analyse['cout_total'] = sum(couts)
    analyse['cout_moyen'] = analyse['cout_total'] / len(projects) if projects else 0

    # Médiane
    couts_tries = sorted(couts)
    n = len(couts_tries)
    if n > 0:
        if n % 2 == 0:
            analyse['cout_median'] = (couts_tries[n//2 - 1] + couts_tries[n//2]) / 2
        else:
            analyse['cout_median'] = couts_tries[n//2]

    # Distribution par tranches
    tranches = {
        'Moins de 5 Mds': 0,
        '5-15 Mds': 0,
        '15-30 Mds': 0,
        'Plus de 30 Mds': 0
    }

    for cout in couts:
        if cout < 5_000_000_000:
            tranches['Moins de 5 Mds'] += 1
        elif cout < 15_000_000_000:
            tranches['5-15 Mds'] += 1
        elif cout < 30_000_000_000:
            tranches['15-30 Mds'] += 1
        else:
            tranches['Plus de 30 Mds'] += 1

    analyse['distribution'] = tranches

    # Concentration (top 3 secteurs représentent quel % du coût total)
    cout_par_secteur = {}
    for p in projects:
        secteur = p.secteur or 'Non spécifié'
        cout_par_secteur[secteur] = cout_par_secteur.get(secteur, 0) + (p.cout_estimatif or 0)

    top3_secteurs = sorted(cout_par_secteur.items(), key=lambda x: x[1], reverse=True)[:3]
    cout_top3 = sum([cout for _, cout in top3_secteurs])
    concentration_pct = round(cout_top3 / analyse['cout_total'] * 100, 1) if analyse['cout_total'] > 0 else 0

    analyse['concentration'] = {
        'top3_secteurs': [{'nom': nom, 'cout': cout} for nom, cout in top3_secteurs],
        'pourcentage': concentration_pct
    }

    return analyse


def generer_insights(projects):
    """Génère des insights clés pour la prise de décision"""
    insights = []

    if not projects:
        return ["Aucune donnée disponible pour générer des insights."]

    # Insight 1: Répartition géographique
    poles = {}
    for p in projects:
        pole = p.poles or 'Non spécifié'
        poles[pole] = poles.get(pole, 0) + 1

    if len(poles) > 1:
        poles_tries = sorted(poles.items(), key=lambda x: x[1], reverse=True)
        pole_max = poles_tries[0]
        pole_min = poles_tries[-1]

        if pole_min[0] != 'Non spécifié' and pole_min[1] < pole_max[1] / 2:
            insights.append(f"⚠️ Déséquilibre territorial : Le pôle {pole_max[0]} ({pole_max[1]} projets) est surreprésenté par rapport au pôle {pole_min[0]} ({pole_min[1]} projets). Un rééquilibrage pourrait être envisagé.")

    # Insight 2: Taux d'approbation par secteur
    secteurs_stats = {}
    for p in projects:
        secteur = p.secteur or 'Non spécifié'
        if secteur not in secteurs_stats:
            secteurs_stats[secteur] = {'total': 0, 'approuves': 0}
        secteurs_stats[secteur]['total'] += 1
        if p.statut == 'approuvé':
            secteurs_stats[secteur]['approuves'] += 1

    for secteur, stats in secteurs_stats.items():
        if stats['total'] >= 3:  # Au moins 3 projets pour être significatif
            taux = (stats['approuves'] / stats['total']) * 100
            if taux >= 80:
                insights.append(f"✅ Le secteur {secteur} affiche un excellent taux d'approbation ({round(taux, 1)}%). Les projets de ce secteur sont particulièrement bien préparés.")
            elif taux <= 30 and stats['total'] >= 5:
                insights.append(f"⚠️ Le secteur {secteur} présente un faible taux d'approbation ({round(taux, 1)}%). Une revue des critères d'évaluation ou un accompagnement renforcé des soumissionnaires pourrait être nécessaire.")

    # Insight 3: Délais de traitement
    projets_termines = [p for p in projects if p.statut in ['approuvé', 'rejeté']]
    if len(projets_termines) >= 5:
        delais = []
        for p in projets_termines:
            if p.date_soumission and p.date_decision:
                delai = (p.date_decision - p.date_soumission).days
                delais.append(delai)

        if delais:
            delai_moyen = sum(delais) / len(delais)
            if delai_moyen > 30:
                insights.append(f"⏱️ Le délai moyen de traitement est de {round(delai_moyen)} jours, ce qui dépasse le seuil optimal de 30 jours. Une optimisation du processus d'évaluation est recommandée.")
            elif delai_moyen <= 15:
                insights.append(f"✅ Excellent délai de traitement moyen : {round(delai_moyen)} jours. Le processus d'évaluation est efficace.")

    # Insight 4: Volume financier
    cout_total = sum([p.cout_estimatif or 0 for p in projects])
    cout_approuve = sum([p.cout_estimatif or 0 for p in projects if p.statut == 'approuvé'])

    if cout_total > 0:
        taux_financier = (cout_approuve / cout_total) * 100
        insights.append(f"💰 Sur un montant total de {format_montant(cout_total)} FCFA demandé, {format_montant(cout_approuve)} FCFA ont été approuvés ({round(taux_financier, 1)}%).")

    if not insights:
        insights.append("Les données actuelles ne permettent pas de dégager d'insights significatifs. Attendez d'avoir plus de projets évalués.")

    return insights


def format_montant(montant):
    """Formate un montant en milliards/millions"""
    if montant >= 1_000_000_000:
        return f"{round(montant / 1_000_000_000, 2)} Mds"
    elif montant >= 1_000_000:
        return f"{round(montant / 1_000_000, 2)} M"
    else:
        return f"{montant:,}"
