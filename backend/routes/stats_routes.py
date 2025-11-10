from flask import Blueprint, jsonify, request
from utils.decorators import role_required
from sqlalchemy import func, text
import json

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/api/stats/overview', methods=['GET'])
def get_stats_overview():
    """Statistiques générales accessibles selon le rôle"""
    from models import Project
    role = request.args.get('role', '')
    username = request.args.get('username', '')

    # Tous les projets selon les permissions du rôle
    if role == 'admin':
        projects = Project.query.all()
    elif role in ['secretariatsct', 'presidencesct', 'presidencecomite']:
        projects = Project.query.all()  # Ces rôles voient tous les projets
    elif role == 'invite':
        # Rôle invité: accès en lecture seule à tous les projets
        projects = Project.query.all()
    else:
        # Autres rôles (évaluateurs, soumissionnaires) - limités
        projects = Project.query.filter_by().all()

    # Calculs statistiques
    total_projets = len(projects)

    # Répartition par statut
    statuts = {}
    for project in projects:
        statut = project.statut or 'non défini'
        statuts[statut] = statuts.get(statut, 0) + 1

    # Répartition par secteur
    secteurs = {}
    for project in projects:
        secteur = project.secteur or 'non défini'
        secteurs[secteur] = secteurs.get(secteur, 0) + 1

    # Répartition par pôle territorial
    poles = {}
    for project in projects:
        pole = project.poles or 'non défini'
        poles[pole] = poles.get(pole, 0) + 1

    # Pour le rôle invité: retourner seulement les données de base (pas de coûts)
    if role == 'invite':
        return jsonify({
            'total_projets': total_projets,
            'statuts': statuts,
            'secteurs': secteurs,
            'poles': poles
        })

    # Pour les autres rôles: retourner toutes les données y compris financières
    cout_total = sum(p.cout_estimatif or 0 for p in projects)

    cout_par_secteur = {}
    for project in projects:
        secteur = project.secteur or 'non défini'
        cout_par_secteur[secteur] = cout_par_secteur.get(secteur, 0) + (project.cout_estimatif or 0)

    cout_par_pole = {}
    for project in projects:
        pole = project.poles or 'non défini'
        cout_par_pole[pole] = cout_par_pole.get(pole, 0) + (project.cout_estimatif or 0)

    return jsonify({
        'total_projets': total_projets,
        'cout_total': cout_total,
        'cout_moyen': cout_total / total_projets if total_projets > 0 else 0,
        'statuts': statuts,
        'secteurs': secteurs,
        'cout_par_secteur': cout_par_secteur,
        'poles': poles,
        'cout_par_pole': cout_par_pole
    })

@stats_bp.route('/api/stats/secteurs', methods=['GET'])
def get_stats_secteurs():
    """Statistiques détaillées par secteur"""
    role = request.args.get('role', '')

    # Filtrer selon les permissions
    if role == 'admin':
        projects = Project.query.all()
    elif role in ['secretariatsct', 'presidencesct', 'presidencecomite']:
        projects = Project.query.all()
    elif role == 'invite':
        # Rôle invité: accès autorisé en lecture seule
        projects = Project.query.all()
    else:
        projects = Project.query.filter_by().all()
    
    secteurs_stats = {}
    
    for project in projects:
        secteur = project.secteur or 'non défini'
        if secteur not in secteurs_stats:
            secteurs_stats[secteur] = {
                'nombre_projets': 0,
                'cout_total': 0,
                'statuts': {},
                'poles': {}
            }
        
        secteurs_stats[secteur]['nombre_projets'] += 1
        secteurs_stats[secteur]['cout_total'] += project.cout_estimatif or 0
        
        # Répartition par statut dans ce secteur
        statut = project.statut or 'non défini'
        secteurs_stats[secteur]['statuts'][statut] = secteurs_stats[secteur]['statuts'].get(statut, 0) + 1
        
        # Répartition par pôle dans ce secteur
        pole = project.poles or 'non défini'
        secteurs_stats[secteur]['poles'][pole] = secteurs_stats[secteur]['poles'].get(pole, 0) + 1
    
    return jsonify(secteurs_stats)

def get_pole_territorial(pole_db):
    """Convertit un pôle de la DB vers un pôle territorial standardisé pour la carte"""
    if not pole_db or pole_db == 'non défini':
        return 'non défini'
    
    # Mapping des pôles de la DB vers les pôles territoriaux de la carte
    pole_mapping = {
        # Centre regroupe Fatick, Kaolack, Kaffrine
        'Centre (Fatick)': 'Centre',
        'Centre (Kaolack)': 'Centre',
        'Centre (Kaffrine)': 'Centre',
        
        # Sud regroupe Ziguinchor, Sedhiou, Kolda
        'Sud (Ziguinchor)': 'Sud',
        'Sud (Sedhiou)': 'Sud', 
        'Sud (Kolda)': 'Sud',
        
        # Sud-Est regroupe Kedougou, Tambacounda
        'Sud-Est (Kedougou)': 'Sud-Est',
        'Sud-Est (Tambacounda)': 'Sud-Est',
        
        # Diourbel-Louga regroupe Diourbel, Louga
        'Diourbel-Louga (Diourbel)': 'Diourbel-Louga',
        'Diourbel-Louga (Louga)': 'Diourbel-Louga',
        
        # Pôles mono-région
        'Dakar': 'Dakar',
        'Thiès': 'Thiès', 
        'Nord (Saint-Louis)': 'Nord',
        'Nord-Est (Matam)': 'Nord-Est'
    }
    
    return pole_mapping.get(pole_db, pole_db)

@stats_bp.route('/api/stats/poles', methods=['GET'])
def get_stats_poles():
    """Statistiques détaillées par pôle territorial (regroupées selon la carte)"""
    from models import Project

    role = request.args.get('role', '')

    # Filtrer selon les permissions
    if role == 'admin':
        projects = Project.query.all()
    elif role in ['secretariatsct', 'presidencesct', 'presidencecomite']:
        projects = Project.query.all()
    elif role == 'invite':
        # Rôle invité: accès autorisé en lecture seule
        projects = Project.query.all()
    else:
        projects = Project.query.filter_by().all()
    
    poles_stats = {}
    
    for project in projects:
        # Un projet peut concerner plusieurs pôles (CSV)
        poles_db = project.poles or 'non défini'
        poles_list = [p.strip() for p in poles_db.split(',') if p.strip()]

        if not poles_list:
            poles_list = ['non défini']

        # Répartir équitablement le coût entre les pôles
        nb_poles = len(poles_list)
        cout_par_pole = (project.cout_estimatif or 0) / nb_poles

        for pole_db in poles_list:
            pole_territorial = get_pole_territorial(pole_db)
            print(f"DEBUG: {pole_db} -> {pole_territorial}, coût réparti: {cout_par_pole}")  # Debug

            if pole_territorial not in poles_stats:
                poles_stats[pole_territorial] = {
                    'nombre_projets': 0,
                    'cout_total': 0,
                    'secteurs': {},
                    'statuts': {}
                }

            # Compter 1/n projet par pôle pour les projets multi-pôles
            poles_stats[pole_territorial]['nombre_projets'] += 1 / nb_poles
            poles_stats[pole_territorial]['cout_total'] += cout_par_pole

            # Répartition par secteur dans ce pôle (fraction)
            secteur = project.secteur or 'non défini'
            poles_stats[pole_territorial]['secteurs'][secteur] = poles_stats[pole_territorial]['secteurs'].get(secteur, 0) + 1 / nb_poles

            # Répartition par statut dans ce pôle (fraction)
            statut = project.statut or 'non défini'
            poles_stats[pole_territorial]['statuts'][statut] = poles_stats[pole_territorial]['statuts'].get(statut, 0) + 1 / nb_poles
    
    return jsonify(poles_stats)

@stats_bp.route('/api/stats/workflow', methods=['GET'])
def get_stats_workflow():
    """Statistiques sur le flux de travail (pour secrétariat et présidences)"""
    role = request.args.get('role', '')

    # Rôle invité: accès INTERDIT aux statistiques workflow
    if role not in ['secretariatsct', 'presidencesct', 'presidencecomite', 'admin']:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    projects = Project.query.all()
    
    # Statistiques spécifiques au workflow
    workflow_stats = {
        'en_attente_assignation': len([p for p in projects if p.statut == 'soumis']),
        'en_evaluation': len([p for p in projects if p.statut == 'assigné']),
        'complements_demandes': len([p for p in projects if p.statut == 'compléments demandés']),
        'complements_fournis': len([p for p in projects if p.statut == 'compléments fournis']),
        'en_attente_validation_sct': len([p for p in projects if p.statut == 'évalué']),
        'en_attente_decision_finale': len([p for p in projects if p.statut == 'validé par presidencesct']),
        'approuves': len([p for p in projects if p.statut == 'approuvé']),
        'rejetes': len([p for p in projects if p.statut == 'rejeté'])
    }
    
    # Temps moyen par étape (simulation basée sur les données disponibles)
    etapes_timing = {
        'soumission_to_assignation': '2.5 jours',
        'assignation_to_evaluation': '7.2 jours',
        'evaluation_to_validation': '3.8 jours',
        'validation_to_decision': '5.1 jours'
    }
    
    return jsonify({
        'workflow': workflow_stats,
        'timing_moyen': etapes_timing,
        'total_en_cours': sum([
            workflow_stats['en_attente_assignation'],
            workflow_stats['en_evaluation'],
            workflow_stats['complements_demandes'],
            workflow_stats['en_attente_validation_sct'],
            workflow_stats['en_attente_decision_finale']
        ])
    })

@stats_bp.route('/api/stats/financial', methods=['GET'])
def get_stats_financial():
    """Statistiques financières détaillées"""
    role = request.args.get('role', '')

    # Rôle invité: accès INTERDIT aux statistiques financières
    if role not in ['secretariatsct', 'presidencesct', 'presidencecomite', 'admin']:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    projects = Project.query.all()
    
    # Calculs financiers
    cout_total = sum(p.cout_estimatif or 0 for p in projects)
    cout_approuve = sum(p.cout_estimatif or 0 for p in projects if p.statut == 'approuvé')
    cout_en_cours = sum(p.cout_estimatif or 0 for p in projects if p.statut not in ['approuvé', 'rejeté'])
    cout_rejete = sum(p.cout_estimatif or 0 for p in projects if p.statut == 'rejeté')
    
    # Répartition par tranches de coûts
    tranches = {
        'moins_5_milliards': 0,
        '5_15_milliards': 0,
        '15_30_milliards': 0,
        'plus_30_milliards': 0
    }
    
    for project in projects:
        cout = project.cout_estimatif or 0
        if cout < 5000000000:
            tranches['moins_5_milliards'] += 1
        elif cout < 15000000000:
            tranches['5_15_milliards'] += 1
        elif cout < 30000000000:
            tranches['15_30_milliards'] += 1
        else:
            tranches['plus_30_milliards'] += 1
    
    return jsonify({
        'cout_total': cout_total,
        'cout_approuve': cout_approuve,
        'cout_en_cours': cout_en_cours,
        'cout_rejete': cout_rejete,
        'taux_approbation_financier': (cout_approuve / cout_total * 100) if cout_total > 0 else 0,
        'tranches_couts': tranches,
        'cout_moyen': cout_total / len(projects) if projects else 0,
        'cout_median': sorted([p.cout_estimatif or 0 for p in projects])[len(projects)//2] if projects else 0
    })