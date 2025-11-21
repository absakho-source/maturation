"""
Routes API pour le système de Point Focal
"""

from flask import Blueprint, request, jsonify
from models import User, Project, Notification, db
from datetime import datetime

point_focal_bp = Blueprint('point_focal', __name__)

@point_focal_bp.route('/api/point-focal/projets', methods=['GET'])
def get_projets_point_focal():
    """
    Récupère tous les projets sous la tutelle du point focal connecté.
    Le point focal voit les projets où organisme_tutelle correspond à son point_focal_organisme.
    """
    username = request.args.get('username')

    if not username:
        return jsonify({'error': 'Username requis'}), 400

    # Récupérer l'utilisateur
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    # Vérifier qu'il est bien point focal
    if not user.is_point_focal:
        return jsonify({'error': 'Cet utilisateur n\'est pas un point focal'}), 403

    if not user.point_focal_organisme:
        return jsonify({'error': 'Aucun organisme assigné à ce point focal'}), 400

    # Récupérer les projets où organisme_tutelle correspond
    # On cherche une correspondance partielle car le format peut varier
    organisme = user.point_focal_organisme

    # Requête pour trouver les projets sous tutelle
    projets = Project.query.filter(
        Project.organisme_tutelle.ilike(f'%{organisme}%')
    ).order_by(Project.date_soumission.desc()).all()

    # Formater les résultats
    result = []
    for p in projets:
        # Récupérer le soumissionnaire
        soumissionnaire = User.query.get(p.soumissionnaire_id) if p.soumissionnaire_id else None

        result.append({
            'id': p.id,
            'numero_projet': p.numero_projet,
            'titre': p.titre,
            'description': p.description,
            'statut': p.statut,
            'date_soumission': p.date_soumission.isoformat() if p.date_soumission else None,
            'auteur_nom': p.auteur_nom,
            'structure_soumissionnaire': p.structure_soumissionnaire,
            'organisme_tutelle': p.organisme_tutelle,
            'secteur': p.secteur,
            'poles': p.poles,
            'cout_estimatif': p.cout_estimatif,
            'avis': p.avis,
            'soumissionnaire': {
                'nom_complet': soumissionnaire.nom_complet if soumissionnaire else None,
                'email': soumissionnaire.username if soumissionnaire else None,
                'telephone': soumissionnaire.telephone if soumissionnaire else None,
                'nom_structure': soumissionnaire.nom_structure if soumissionnaire else None
            } if soumissionnaire else None
        })

    return jsonify({
        'projets': result,
        'total': len(result),
        'organisme': organisme
    })


@point_focal_bp.route('/api/point-focal/stats', methods=['GET'])
def get_stats_point_focal():
    """
    Récupère les statistiques des projets sous tutelle du point focal.
    """
    username = request.args.get('username')

    if not username:
        return jsonify({'error': 'Username requis'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.is_point_focal:
        return jsonify({'error': 'Point focal non trouvé'}), 404

    organisme = user.point_focal_organisme
    if not organisme:
        return jsonify({'error': 'Aucun organisme assigné'}), 400

    # Récupérer tous les projets sous tutelle
    projets = Project.query.filter(
        Project.organisme_tutelle.ilike(f'%{organisme}%')
    ).all()

    # Calculer les statistiques
    stats = {
        'total': len(projets),
        'soumis': sum(1 for p in projets if p.statut == 'soumis'),
        'en_evaluation': sum(1 for p in projets if p.statut in ['assigné', 'en_evaluation']),
        'evalues': sum(1 for p in projets if p.statut == 'évalué'),
        'favorables': sum(1 for p in projets if p.avis == 'favorable'),
        'defavorables': sum(1 for p in projets if p.avis == 'défavorable'),
        'en_attente_complements': sum(1 for p in projets if p.statut == 'compléments_requis')
    }

    return jsonify(stats)


@point_focal_bp.route('/api/users/<int:user_id>/point-focal', methods=['PUT'])
def update_point_focal_status(user_id):
    """
    Met à jour le statut de point focal d'un utilisateur (admin seulement).
    """
    data = request.get_json()

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    # Mettre à jour les champs
    if 'is_point_focal' in data:
        user.is_point_focal = data['is_point_focal']

    if 'point_focal_organisme' in data:
        user.point_focal_organisme = data['point_focal_organisme']

    # Si on désactive le point focal, effacer l'organisme
    if not data.get('is_point_focal', user.is_point_focal):
        user.point_focal_organisme = None

    db.session.commit()

    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'display_name': user.display_name,
            'is_point_focal': user.is_point_focal,
            'point_focal_organisme': user.point_focal_organisme
        }
    })


@point_focal_bp.route('/api/points-focaux', methods=['GET'])
def get_all_points_focaux():
    """
    Liste tous les points focaux (pour admin).
    """
    points_focaux = User.query.filter_by(is_point_focal=True).all()

    result = []
    for pf in points_focaux:
        # Compter les projets sous sa tutelle
        nb_projets = 0
        if pf.point_focal_organisme:
            nb_projets = Project.query.filter(
                Project.organisme_tutelle.ilike(f'%{pf.point_focal_organisme}%')
            ).count()

        result.append({
            'id': pf.id,
            'username': pf.username,
            'display_name': pf.display_name,
            'nom_complet': pf.nom_complet,
            'point_focal_organisme': pf.point_focal_organisme,
            'nom_structure': pf.nom_structure,
            'telephone': pf.telephone,
            'nb_projets_tutelle': nb_projets
        })

    return jsonify(result)


def notifier_point_focal_nouveau_projet(project):
    """
    Envoie une notification aux points focaux quand un projet est soumis sous leur tutelle.
    Appelée depuis la route de soumission de projet.
    """
    if not project.organisme_tutelle:
        return

    # Trouver les points focaux de cet organisme
    points_focaux = User.query.filter(
        User.is_point_focal == True,
        User.point_focal_organisme.ilike(f'%{project.organisme_tutelle}%')
    ).all()

    for pf in points_focaux:
        notification = Notification(
            user_id=pf.id,
            project_id=project.id,
            type='nouveau_projet_tutelle',
            titre='Nouveau projet sous votre tutelle',
            message=f'Le projet "{project.titre}" a été soumis par {project.structure_soumissionnaire or project.auteur_nom}.',
            lien=f'/projets/{project.id}',
            priorite_email=True
        )
        db.session.add(notification)

    db.session.commit()
