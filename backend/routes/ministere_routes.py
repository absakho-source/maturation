"""
Routes API pour la gestion des ministères
"""

from flask import Blueprint, request, jsonify
from models import db, Ministere
from datetime import datetime

ministere_bp = Blueprint('ministere', __name__)


@ministere_bp.route('/api/ministeres', methods=['GET'])
def get_ministeres_actifs():
    """Récupérer la liste des ministères actifs pour les formulaires"""
    try:
        ministeres = Ministere.query.filter_by(actif=True).order_by(Ministere.ordre).all()
        return jsonify([m.to_dict() for m in ministeres]), 200
    except Exception as e:
        print(f"[MINISTERES API] Erreur récupération ministères actifs: {str(e)}")
        return jsonify({"error": "Erreur lors de la récupération des ministères"}), 500


@ministere_bp.route('/api/ministeres/all', methods=['GET'])
def get_all_ministeres():
    """Récupérer tous les ministères (admin seulement)"""
    try:
        # Vérifier le rôle
        data = request.get_json() if request.is_json else {}
        role = data.get('role') if data else request.args.get('role')

        if role not in ['admin', 'secretariatsct']:
            return jsonify({"error": "Accès non autorisé"}), 403

        ministeres = Ministere.query.order_by(Ministere.ordre).all()
        return jsonify([m.to_dict() for m in ministeres]), 200
    except Exception as e:
        print(f"[MINISTERES API] Erreur récupération tous ministères: {str(e)}")
        return jsonify({"error": "Erreur lors de la récupération des ministères"}), 500


@ministere_bp.route('/api/ministeres', methods=['POST'])
def create_ministere():
    """Créer un nouveau ministère (admin seulement)"""
    try:
        data = request.get_json()

        # Vérifier le rôle
        if data.get('role') not in ['admin', 'secretariatsct']:
            return jsonify({"error": "Accès non autorisé"}), 403

        # Valider les données
        if not data.get('nom_complet'):
            return jsonify({"error": "Le nom complet est requis"}), 400

        # Déterminer l'ordre
        max_ordre = db.session.query(db.func.max(Ministere.ordre)).scalar() or 0

        # Créer le ministère
        ministere = Ministere(
            nom_complet=data['nom_complet'],
            abreviation=data.get('abreviation'),
            actif=data.get('actif', True),
            ordre=max_ordre + 1
        )

        db.session.add(ministere)
        db.session.commit()

        print(f"[MINISTERES API] Ministère créé: {ministere.nom_complet}")
        return jsonify(ministere.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        print(f"[MINISTERES API] Erreur création ministère: {str(e)}")
        return jsonify({"error": "Erreur lors de la création du ministère"}), 500


@ministere_bp.route('/api/ministeres/<int:ministere_id>', methods=['PUT'])
def update_ministere(ministere_id):
    """Mettre à jour un ministère (admin seulement)"""
    try:
        data = request.get_json()

        # Vérifier le rôle
        if data.get('role') not in ['admin', 'secretariatsct']:
            return jsonify({"error": "Accès non autorisé"}), 403

        ministere = Ministere.query.get(ministere_id)
        if not ministere:
            return jsonify({"error": "Ministère non trouvé"}), 404

        # Mettre à jour les champs
        if 'nom_complet' in data:
            ministere.nom_complet = data['nom_complet']
        if 'abreviation' in data:
            ministere.abreviation = data['abreviation']
        if 'actif' in data:
            ministere.actif = data['actif']
        if 'ordre' in data:
            ministere.ordre = data['ordre']

        ministere.date_modification = datetime.utcnow()

        db.session.commit()

        print(f"[MINISTERES API] Ministère mis à jour: {ministere.nom_complet}")
        return jsonify(ministere.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        print(f"[MINISTERES API] Erreur mise à jour ministère: {str(e)}")
        return jsonify({"error": "Erreur lors de la mise à jour du ministère"}), 500


@ministere_bp.route('/api/ministeres/<int:ministere_id>', methods=['DELETE'])
def delete_ministere(ministere_id):
    """Supprimer un ministère (admin seulement)"""
    try:
        data = request.get_json()

        # Vérifier le rôle
        if data.get('role') not in ['admin', 'secretariatsct']:
            return jsonify({"error": "Accès non autorisé"}), 403

        ministere = Ministere.query.get(ministere_id)
        if not ministere:
            return jsonify({"error": "Ministère non trouvé"}), 404

        nom = ministere.nom_complet
        db.session.delete(ministere)
        db.session.commit()

        print(f"[MINISTERES API] Ministère supprimé: {nom}")
        return jsonify({"message": "Ministère supprimé avec succès"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"[MINISTERES API] Erreur suppression ministère: {str(e)}")
        return jsonify({"error": "Erreur lors de la suppression du ministère"}), 500


@ministere_bp.route('/api/ministeres/reorder', methods=['POST'])
def reorder_ministeres():
    """Réorganiser l'ordre des ministères (admin seulement)"""
    try:
        data = request.get_json()

        # Vérifier le rôle
        if data.get('role') not in ['admin', 'secretariatsct']:
            return jsonify({"error": "Accès non autorisé"}), 403

        # data['ordres'] devrait être un dictionnaire {id: ordre}
        ordres = data.get('ordres', {})

        for ministere_id, ordre in ordres.items():
            ministere = Ministere.query.get(int(ministere_id))
            if ministere:
                ministere.ordre = ordre
                ministere.date_modification = datetime.utcnow()

        db.session.commit()

        print(f"[MINISTERES API] Ordre des ministères mis à jour")
        return jsonify({"message": "Ordre mis à jour avec succès"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"[MINISTERES API] Erreur réorganisation: {str(e)}")
        return jsonify({"error": "Erreur lors de la réorganisation"}), 500
