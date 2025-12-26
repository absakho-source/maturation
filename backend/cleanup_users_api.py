#!/usr/bin/env python3
"""
Endpoint API pour nettoyer les comptes récents et effectuer les migrations
À appeler via: curl -X POST http://localhost:5000/api/admin/cleanup-recent-users
"""
from flask import Blueprint, jsonify, request
from models import Project, User, FicheEvaluation, DocumentProjet, Historique, MessageProjet, Log
from db import db
from datetime import datetime
import os

cleanup_bp = Blueprint('cleanup', __name__)

@cleanup_bp.route('/api/admin/db-info', methods=['GET'])
def get_db_info():
    """Endpoint de diagnostic pour voir les utilisateurs et projets"""
    try:
        # Compter les utilisateurs et projets
        users_count = User.query.count()
        projects_count = Project.query.count()

        # Trouver les utilisateurs à supprimer
        users_to_delete = User.query.filter(User.username.in_(ACCOUNTS_TO_DELETE)).all()
        users_found = [u.username for u in users_to_delete]

        # Compter les projets de ces utilisateurs
        projects_to_transfer = Project.query.filter(Project.auteur_nom.in_(ACCOUNTS_TO_DELETE)).all()
        projects_by_user = {}
        for project in projects_to_transfer:
            if project.auteur_nom not in projects_by_user:
                projects_by_user[project.auteur_nom] = 0
            projects_by_user[project.auteur_nom] += 1

        return jsonify({
            'success': True,
            'total_users': users_count,
            'total_projects': projects_count,
            'users_to_delete': users_found,
            'users_to_delete_count': len(users_found),
            'projects_to_transfer': len(projects_to_transfer),
            'projects_by_user': projects_by_user
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Liste des comptes à supprimer
ACCOUNTS_TO_DELETE = [
    'papa.sy',
    'papa.diouf',
    'mamadou.marone',
    'syleymane.niang',
    'suleymane.haidara',
    'mame.toure',
    'ndeye.sarr',
    'serigne.diene',
    'babacar.sall',
    'khady.ndiaye',
    'ousseynou.badiane',
    'deguene.mbodj',
    'aminata.faye',
    'sokhna.syll',
    'richard.tendeng',
    'fatou.mbow',
    'oumar.diedhiou',
    'fatou.ndiaye3',
    'abdou.sene',
    'moustaphadiamil.sy'
]

@cleanup_bp.route('/api/admin/cleanup-recent-users', methods=['POST'])
def cleanup_recent_users():
    """Supprime les comptes récents et transfère leurs projets"""
    try:
        # 1. Compter les projets à transférer
        projects_to_transfer = Project.query.filter(Project.auteur_nom.in_(ACCOUNTS_TO_DELETE)).all()
        total_projects = len(projects_to_transfer)

        projects_by_user = {}
        for project in projects_to_transfer:
            if project.auteur_nom not in projects_by_user:
                projects_by_user[project.auteur_nom] = 0
            projects_by_user[project.auteur_nom] += 1

        # 2. Transférer les projets
        projects_transferred = 0
        if total_projects > 0:
            for project in projects_to_transfer:
                project.auteur_nom = 'soumissionnaire'
                projects_transferred += 1

        # 3. Supprimer les comptes
        users_to_delete = User.query.filter(User.username.in_(ACCOUNTS_TO_DELETE)).all()
        users_deleted = len(users_to_delete)

        for user in users_to_delete:
            db.session.delete(user)

        # Commit toutes les modifications
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Nettoyage réussi',
            'users_deleted': users_deleted,
            'projects_transferred': projects_transferred,
            'projects_by_user': projects_by_user,
            'deleted_accounts': ACCOUNTS_TO_DELETE
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cleanup_bp.route('/api/admin/migrate-evaluabilite', methods=['POST'])
def migrate_evaluabilite():
    """Endpoint pour exécuter la migration d'évaluabilité"""
    try:
        import sqlite3

        DATA_DIR = os.environ.get("DATA_DIR", os.path.abspath(os.path.dirname(__file__)))
        DB_PATH = os.path.join(DATA_DIR, "maturation.db")

        if not os.path.exists(DB_PATH):
            return jsonify({
                'success': False,
                'error': f'Database not found: {DB_PATH}'
            }), 500

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Vérifier si les colonnes existent déjà
        cursor.execute("PRAGMA table_info(project)")
        columns = [col[1] for col in cursor.fetchall()]

        columns_to_add = [
            ("evaluabilite", "VARCHAR(50)"),
            ("evaluabilite_date", "DATETIME"),
            ("evaluabilite_commentaire", "TEXT")
        ]

        added_columns = []
        existing_columns = []

        for col_name, col_type in columns_to_add:
            if col_name not in columns:
                cursor.execute(f"ALTER TABLE project ADD COLUMN {col_name} {col_type}")
                added_columns.append(col_name)
            else:
                existing_columns.append(col_name)

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Migration réussie',
            'added_columns': added_columns,
            'existing_columns': existing_columns,
            'db_path': DB_PATH
        }), 200

    except Exception as e:
        if conn:
            conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cleanup_bp.route('/api/admin/migrate-seuil-minimum', methods=['POST'])
def migrate_seuil_minimum():
    """Endpoint pour ajouter la colonne seuil_minimum à formulaire_config"""
    try:
        import sqlite3

        DATA_DIR = os.environ.get("DATA_DIR", os.path.abspath(os.path.dirname(__file__)))
        DB_PATH = os.path.join(DATA_DIR, "maturation.db")

        if not os.path.exists(DB_PATH):
            return jsonify({
                'success': False,
                'error': f'Database not found: {DB_PATH}'
            }), 500

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(formulaire_config)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'seuil_minimum' not in columns:
            cursor.execute("ALTER TABLE formulaire_config ADD COLUMN seuil_minimum INTEGER DEFAULT 70")
            # Synchroniser avec seuil_conditionnel existant
            cursor.execute("UPDATE formulaire_config SET seuil_minimum = seuil_conditionnel WHERE seuil_minimum IS NULL")
            conn.commit()
            message = "Colonne seuil_minimum ajoutée et synchronisée"
        else:
            message = "Colonne seuil_minimum existe déjà"

        conn.close()

        return jsonify({
            'success': True,
            'message': message,
            'db_path': DB_PATH
        }), 200

    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cleanup_bp.route('/api/admin/migrate-soft-delete', methods=['POST'])
def migrate_soft_delete():
    """Endpoint pour ajouter la colonne deleted_at à la table project (soft delete)"""
    try:
        import sqlite3

        DATA_DIR = os.environ.get("DATA_DIR", os.path.abspath(os.path.dirname(__file__)))
        DB_PATH = os.path.join(DATA_DIR, "maturation.db")

        if not os.path.exists(DB_PATH):
            return jsonify({
                'success': False,
                'error': f'Database not found: {DB_PATH}'
            }), 500

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(project)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'deleted_at' not in columns:
            cursor.execute("ALTER TABLE project ADD COLUMN deleted_at DATETIME DEFAULT NULL")
            conn.commit()

            # Vérifier le nombre de projets
            cursor.execute("SELECT COUNT(*) FROM project")
            total_projects = cursor.fetchone()[0]

            message = f"Colonne deleted_at ajoutée avec succès. Total de projets: {total_projects}"
        else:
            # Vérifier le nombre de projets actifs et supprimés
            cursor.execute("SELECT COUNT(*) FROM project WHERE deleted_at IS NULL")
            active_projects = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM project WHERE deleted_at IS NOT NULL")
            deleted_projects = cursor.fetchone()[0]

            message = f"Colonne deleted_at existe déjà. Projets actifs: {active_projects}, Projets supprimés: {deleted_projects}"

        conn.close()

        return jsonify({
            'success': True,
            'message': message,
            'db_path': DB_PATH
        }), 200

    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============ ENDPOINTS DE GESTION DE LA CORBEILLE (SOFT DELETE) ============

@cleanup_bp.route('/api/admin/corbeille', methods=['GET'])
def get_corbeille():
    """Lister tous les projets supprimés (corbeille)"""
    try:
        # Récupérer tous les projets supprimés (deleted_at IS NOT NULL)
        deleted_projects = Project.query.filter(Project.deleted_at.isnot(None)).order_by(Project.deleted_at.desc()).all()

        result = []
        for p in deleted_projects:
            result.append({
                'id': p.id,
                'numero_projet': p.numero_projet,
                'titre': p.titre,
                'auteur_nom': p.auteur_nom,
                'statut': p.statut,
                'date_soumission': p.date_soumission.isoformat() if p.date_soumission else None,
                'deleted_at': p.deleted_at.isoformat() if p.deleted_at else None,
                'secteur': p.secteur,
                'poles': p.poles
            })

        return jsonify({
            'success': True,
            'projects': result,
            'total': len(result)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cleanup_bp.route('/api/admin/corbeille/<int:project_id>/restore', methods=['POST'])
def restore_project(project_id):
    """Restaurer un projet depuis la corbeille"""
    try:
        project = Project.query.get_or_404(project_id)

        if not project.deleted_at:
            return jsonify({
                'success': False,
                'error': 'Ce projet n\'est pas dans la corbeille'
            }), 400

        # Restaurer le projet
        project.deleted_at = None

        # Ajouter dans l'historique
        hist = Historique(
            project_id=project_id,
            action=f"Projet restauré depuis la corbeille",
            auteur=request.args.get('username', 'admin'),
            role='admin',
            date_action=datetime.utcnow()
        )
        db.session.add(hist)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Projet {project.numero_projet} restauré avec succès',
            'project': {
                'id': project.id,
                'numero_projet': project.numero_projet,
                'titre': project.titre
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cleanup_bp.route('/api/admin/corbeille/<int:project_id>/delete-permanent', methods=['DELETE'])
def delete_project_permanent(project_id):
    """Supprimer définitivement un projet (suppression permanente)"""
    try:
        project = Project.query.get_or_404(project_id)

        if not project.deleted_at:
            return jsonify({
                'success': False,
                'error': 'Ce projet n\'est pas dans la corbeille. Déplacez-le d\'abord vers la corbeille.'
            }), 400

        projet_numero = project.numero_projet
        projet_titre = project.titre

        # Supprimer toutes les relations en cascade
        FicheEvaluation.query.filter_by(project_id=project_id).delete()
        DocumentProjet.query.filter_by(project_id=project_id).delete()
        Historique.query.filter_by(project_id=project_id).delete()
        MessageProjet.query.filter_by(project_id=project_id).delete()
        Log.query.filter_by(projet_id=project_id).delete()

        # Supprimer définitivement le projet
        db.session.delete(project)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Projet {projet_numero} supprimé définitivement',
            'deleted': {
                'numero_projet': projet_numero,
                'titre': projet_titre
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cleanup_bp.route('/api/admin/corbeille/vider', methods=['POST'])
def vider_corbeille():
    """Vider complètement la corbeille (suppression permanente de tous les projets supprimés)"""
    try:
        # Récupérer tous les projets supprimés
        deleted_projects = Project.query.filter(Project.deleted_at.isnot(None)).all()
        total_deleted = len(deleted_projects)

        if total_deleted == 0:
            return jsonify({
                'success': True,
                'message': 'La corbeille est déjà vide',
                'total_deleted': 0
            }), 200

        deleted_info = []
        for project in deleted_projects:
            deleted_info.append({
                'numero_projet': project.numero_projet,
                'titre': project.titre
            })

            # Supprimer toutes les relations
            FicheEvaluation.query.filter_by(project_id=project.id).delete()
            DocumentProjet.query.filter_by(project_id=project.id).delete()
            Historique.query.filter_by(project_id=project.id).delete()
            MessageProjet.query.filter_by(project_id=project.id).delete()
            Log.query.filter_by(projet_id=project.id).delete()

            # Supprimer le projet
            db.session.delete(project)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'{total_deleted} projet(s) supprimé(s) définitivement',
            'total_deleted': total_deleted,
            'deleted_projects': deleted_info
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
