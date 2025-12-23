#!/usr/bin/env python3
"""
Endpoint API pour nettoyer les comptes récents
À appeler via: curl -X POST http://localhost:5000/api/admin/cleanup-recent-users
"""
from flask import Blueprint, jsonify
import sqlite3

cleanup_bp = Blueprint('cleanup', __name__)

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
        conn = sqlite3.connect('maturation.db')
        cursor = conn.cursor()

        # 1. Compter les projets à transférer
        placeholders = ','.join(['?' for _ in ACCOUNTS_TO_DELETE])
        cursor.execute(f"""
            SELECT auteur_nom, COUNT(*)
            FROM project
            WHERE auteur_nom IN ({placeholders})
            GROUP BY auteur_nom
        """, ACCOUNTS_TO_DELETE)

        projects_by_user = cursor.fetchall()
        total_projects = sum(count for _, count in projects_by_user)

        # 2. Transférer les projets
        if total_projects > 0:
            cursor.execute(f"""
                UPDATE project
                SET auteur_nom = 'soumissionnaire'
                WHERE auteur_nom IN ({placeholders})
            """, ACCOUNTS_TO_DELETE)
            projects_transferred = cursor.rowcount
        else:
            projects_transferred = 0

        # 3. Supprimer les comptes
        cursor.execute(f"""
            DELETE FROM users
            WHERE username IN ({placeholders})
        """, ACCOUNTS_TO_DELETE)
        users_deleted = cursor.rowcount

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Nettoyage réussi',
            'users_deleted': users_deleted,
            'projects_transferred': projects_transferred,
            'deleted_accounts': ACCOUNTS_TO_DELETE
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
