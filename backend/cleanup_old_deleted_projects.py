#!/usr/bin/env python3
"""
Script de nettoyage automatique des projets supprimés depuis plus de 12 mois.
À exécuter périodiquement via cron ou un scheduler.
"""
import os
import sys
from datetime import datetime, timedelta
from flask import Flask
from db import db
from models import Project, FicheEvaluation, DocumentProjet, Historique, MessageProjet, Log

# Configuration
DATA_DIR = os.environ.get("DATA_DIR", os.path.abspath(os.path.dirname(__file__)))
DB_PATH = os.path.join(DATA_DIR, "maturation.db")
RETENTION_MONTHS = 12  # Durée de conservation dans la corbeille

def create_app():
    """Créer une instance Flask minimale pour accéder à la DB"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def cleanup_old_deleted_projects():
    """Supprime définitivement les projets dans la corbeille depuis plus de 12 mois"""
    app = create_app()

    with app.app_context():
        try:
            # Calculer la date limite (12 mois avant aujourd'hui)
            date_limite = datetime.utcnow() - timedelta(days=RETENTION_MONTHS * 30)

            print(f"🔍 Recherche des projets supprimés avant le {date_limite.strftime('%Y-%m-%d %H:%M:%S')}...")

            # Trouver tous les projets supprimés depuis plus de 12 mois
            old_deleted_projects = Project.query.filter(
                Project.deleted_at.isnot(None),
                Project.deleted_at < date_limite
            ).all()

            if not old_deleted_projects:
                print("✅ Aucun projet à supprimer (corbeille vide ou tous récents)")
                return 0

            print(f"📋 {len(old_deleted_projects)} projet(s) à supprimer définitivement:")

            deleted_info = []
            for project in old_deleted_projects:
                days_in_trash = (datetime.utcnow() - project.deleted_at).days
                print(f"   - [{project.numero_projet or f'PROJ-{project.id}'}] {project.titre}")
                print(f"     Supprimé le: {project.deleted_at.strftime('%Y-%m-%d')} ({days_in_trash} jours)")

                deleted_info.append({
                    'id': project.id,
                    'numero_projet': project.numero_projet,
                    'titre': project.titre,
                    'deleted_at': project.deleted_at,
                    'days_in_trash': days_in_trash
                })

                # Supprimer toutes les relations en cascade
                FicheEvaluation.query.filter_by(project_id=project.id).delete()
                DocumentProjet.query.filter_by(project_id=project.id).delete()
                Historique.query.filter_by(project_id=project.id).delete()
                MessageProjet.query.filter_by(project_id=project.id).delete()
                Log.query.filter_by(projet_id=project.id).delete()

                # Supprimer le projet
                db.session.delete(project)

            # Commit les suppressions
            db.session.commit()

            print(f"\n✅ {len(old_deleted_projects)} projet(s) supprimé(s) définitivement de la base de données")

            # Afficher un résumé
            total_days = sum(p['days_in_trash'] for p in deleted_info)
            avg_days = total_days / len(deleted_info) if deleted_info else 0
            print(f"📊 Durée moyenne dans la corbeille: {int(avg_days)} jours")

            return len(old_deleted_projects)

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erreur lors du nettoyage: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    print("=" * 80)
    print("🗑️  NETTOYAGE AUTOMATIQUE DE LA CORBEILLE")
    print("=" * 80)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  Durée de rétention: {RETENTION_MONTHS} mois")
    print(f"🗄️  Base de données: {DB_PATH}")
    print("=" * 80)
    print()

    deleted_count = cleanup_old_deleted_projects()

    print()
    print("=" * 80)
    print(f"✅ Nettoyage terminé - {deleted_count} projet(s) supprimé(s)")
    print("=" * 80)
