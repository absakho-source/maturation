#!/usr/bin/env python3
"""
Script one-time pour générer les notifications manquantes
basées sur l'historique et le statut actuel des projets.

Usage (sur le shell Render):
    python generate_missing_notifications.py
"""
import os
import sys
from datetime import datetime

# Configuration de la base de données
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
else:
    DATA_DIR = os.environ.get('DATA_DIR', '/data')
    db_path = os.path.join(DATA_DIR, 'maturation.db')
    if not os.path.exists(db_path):
        db_path = 'maturation.db'
    DATABASE_URL = f"sqlite:///{db_path}"

print(f"Base de données: {DATABASE_URL[:50]}...")

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def get_user_id_by_username(username):
    """Récupère l'ID d'un utilisateur par son username"""
    result = session.execute(
        text("SELECT id FROM users WHERE username = :username"),
        {"username": username}
    ).fetchone()
    return result[0] if result else None

def get_users_by_role(role):
    """Récupère tous les utilisateurs d'un rôle donné"""
    result = session.execute(
        text("SELECT id, username FROM users WHERE role = :role"),
        {"role": role}
    ).fetchall()
    return result

def notification_exists(user_id, project_id, notif_type):
    """Vérifie si une notification similaire existe déjà"""
    result = session.execute(
        text("""
            SELECT COUNT(*) FROM notifications
            WHERE user_id = :user_id
            AND project_id = :project_id
            AND type = :type
        """),
        {"user_id": user_id, "project_id": project_id, "type": notif_type}
    ).fetchone()
    return result[0] > 0

def create_notification(user_id, project_id, notif_type, titre, message, lien):
    """Crée une notification si elle n'existe pas déjà"""
    if notification_exists(user_id, project_id, notif_type):
        return False

    session.execute(
        text("""
            INSERT INTO notifications (user_id, project_id, type, titre, message, lien, lu, date_creation)
            VALUES (:user_id, :project_id, :type, :titre, :message, :lien, FALSE, :date_creation)
        """),
        {
            "user_id": user_id,
            "project_id": project_id,
            "type": notif_type,
            "titre": titre,
            "message": message,
            "lien": lien,
            "date_creation": datetime.utcnow()
        }
    )
    return True

def generate_notifications_for_project(project):
    """Génère les notifications manquantes pour un projet"""
    project_id = project[0]
    titre = project[1]
    statut = project[2]
    soumissionnaire_id = project[3]
    avis = project[4]
    decision_finale = project[5]

    titre_court = titre[:50] + "..." if len(titre) > 50 else titre
    lien = f"/project/{project_id}"
    created = 0

    # Statuts qui indiquent que le projet a été évalué
    statuts_evalues = [
        'évalué', 'en attente validation presidencesct', 'validé par presidencesct',
        'décision finale confirmée', 'favorable', 'favorable sous conditions', 'défavorable',
        'approuvé', 'rejeté'
    ]

    # 1. Notification "Projet évalué" au soumissionnaire
    if soumissionnaire_id and statut in statuts_evalues:
        if create_notification(
            soumissionnaire_id, project_id, "evaluation",
            "Projet évalué",
            f"Votre projet '{titre_court}' a été évalué.",
            lien
        ):
            created += 1

    # 2. Notification "Avis validé par secrétariat" au soumissionnaire
    statuts_valides_secretariat = [
        'en attente validation presidencesct', 'validé par presidencesct',
        'décision finale confirmée', 'favorable', 'favorable sous conditions', 'défavorable',
        'approuvé'
    ]
    if soumissionnaire_id and statut in statuts_valides_secretariat:
        if create_notification(
            soumissionnaire_id, project_id, "statut_change",
            "Avis en cours de validation",
            f"L'avis sur votre projet '{titre_court}' a été validé par le Secrétariat SCT.",
            lien
        ):
            created += 1

    # 3. Notification "Projet validé par présidence SCT" au soumissionnaire
    statuts_valides_psct = [
        'validé par presidencesct', 'décision finale confirmée',
        'favorable', 'favorable sous conditions', 'défavorable', 'approuvé'
    ]
    if soumissionnaire_id and statut in statuts_valides_psct:
        avis_text = avis if avis else "en cours"
        if create_notification(
            soumissionnaire_id, project_id, "statut_change",
            "Projet validé",
            f"Votre projet '{titre_court}' a été validé par la Présidence SCT. L'avis est : {avis_text}.",
            lien
        ):
            created += 1

    # 4. Notification "Décision finale" au soumissionnaire
    if soumissionnaire_id and statut == 'décision finale confirmée' and decision_finale:
        decision_text = "approuvé" if decision_finale == "confirme" else "non retenu"
        if create_notification(
            soumissionnaire_id, project_id, "statut_change",
            "Décision finale rendue",
            f"Votre projet '{titre_court}' a été {decision_text} par le Comité.",
            lien
        ):
            created += 1

    return created

def main():
    print("=" * 60)
    print("GÉNÉRATION DES NOTIFICATIONS MANQUANTES")
    print("=" * 60)

    # Récupérer tous les projets avec leur soumissionnaire
    projects = session.execute(text("""
        SELECT p.id, p.titre, p.statut, p.soumissionnaire_id, p.avis, p.decision_finale
        FROM project p
        WHERE p.soumissionnaire_id IS NOT NULL
    """)).fetchall()

    print(f"\nNombre de projets à traiter: {len(projects)}")

    total_created = 0
    for project in projects:
        project_id = project[0]
        titre = project[1]
        statut = project[2]

        created = generate_notifications_for_project(project)
        if created > 0:
            print(f"  Projet {project_id} ({titre[:30]}...): {created} notification(s) créée(s)")
            total_created += created

    session.commit()

    print(f"\n{'=' * 60}")
    print(f"TOTAL: {total_created} notification(s) créée(s)")
    print("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\nERREUR: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        sys.exit(1)
