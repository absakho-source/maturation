"""
Utilitaire pour le versioning des projets

Capture et stocke les versions successives d'un projet pour traçabilité complète.
"""
import json
from datetime import datetime
from models import Project, ProjectVersion
from db import db


def create_project_version(project, modified_by, modification_type, change_summary=None, statut_before=None):
    """
    Crée une version snapshot du projet actuel

    Args:
        project: Instance du projet à versioner
        modified_by: Username de la personne qui modifie
        modification_type: Type de modification ('creation', 'update', 'status_change', 'evaluation', etc.)
        change_summary: Description des modifications (optionnel)
        statut_before: Statut avant modification (optionnel)

    Returns:
        ProjectVersion: L'instance de version créée
    """
    try:
        # Compter les versions existantes pour ce projet
        existing_versions = ProjectVersion.query.filter_by(project_id=project.id).count()
        version_number = existing_versions + 1

        # Capturer toutes les données du projet en JSON
        project_data = {
            'id': project.id,
            'numero_projet': project.numero_projet,
            'titre': project.titre,
            'description': project.description,
            'secteur': project.secteur,
            'poles': project.poles,
            'cout_estimatif': project.cout_estimatif,
            'statut': project.statut,
            'date_soumission': project.date_soumission.isoformat() if project.date_soumission else None,
            'soumissionnaire_id': project.soumissionnaire_id,
            'evaluateur_nom': project.evaluateur_nom,
            'avis': project.avis,
            'decision_finale': project.decision_finale,

            # Données géographiques
            'region': project.region,
            'departement': project.departement,
            'commune': project.commune,
            'latitude': project.latitude,
            'longitude': project.longitude,
            'pays': project.pays,
            'ville': project.ville,

            # Données organisationnelles
            'organisme': project.organisme,
            'structure': project.structure,
            'nom_ministere': project.nom_ministere,

            # Autres champs
            'fichiers': project.fichiers,
            'commentaires_finaux': project.commentaires_finaux,
            'motivation_resoumission': project.motivation_resoumission,

            # Métadonnées de la version
            'version_capture_date': datetime.utcnow().isoformat()
        }

        # Créer la version
        version = ProjectVersion(
            project_id=project.id,
            version_number=version_number,
            modified_by=modified_by,
            modification_type=modification_type,
            change_summary=change_summary,
            project_data=json.dumps(project_data, ensure_ascii=False),
            statut_before=statut_before,
            statut_after=project.statut
        )

        db.session.add(version)
        db.session.commit()

        print(f"[VERSIONING] ✓ Version {version_number} créée pour projet {project.numero_projet or project.id}")
        print(f"[VERSIONING]   Type: {modification_type}, Par: {modified_by}")

        return version

    except Exception as e:
        print(f"[VERSIONING] ✗ Erreur lors de la création de version: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return None


def get_project_versions(project_id):
    """
    Récupère toutes les versions d'un projet

    Args:
        project_id: ID du projet

    Returns:
        list: Liste des versions triées par date (plus récente en premier)
    """
    versions = ProjectVersion.query.filter_by(project_id=project_id).order_by(
        ProjectVersion.modified_at.desc()
    ).all()

    return [v.to_dict() for v in versions]


def get_project_version(version_id):
    """
    Récupère une version spécifique

    Args:
        version_id: ID de la version

    Returns:
        dict: Données de la version ou None
    """
    version = ProjectVersion.query.get(version_id)
    return version.to_dict() if version else None


def compare_versions(version_id_1, version_id_2):
    """
    Compare deux versions d'un projet

    Args:
        version_id_1: ID de la première version (ancienne)
        version_id_2: ID de la deuxième version (récente)

    Returns:
        dict: Différences entre les deux versions
    """
    version1 = ProjectVersion.query.get(version_id_1)
    version2 = ProjectVersion.query.get(version_id_2)

    if not version1 or not version2:
        return None

    data1 = json.loads(version1.project_data)
    data2 = json.loads(version2.project_data)

    # Comparer les champs
    differences = {}
    all_keys = set(data1.keys()) | set(data2.keys())

    for key in all_keys:
        val1 = data1.get(key)
        val2 = data2.get(key)

        if val1 != val2:
            differences[key] = {
                'before': val1,
                'after': val2,
                'changed': True
            }

    return {
        'version1': {
            'id': version1.id,
            'version_number': version1.version_number,
            'modified_at': version1.modified_at.isoformat() if version1.modified_at else None,
            'modified_by': version1.modified_by
        },
        'version2': {
            'id': version2.id,
            'version_number': version2.version_number,
            'modified_at': version2.modified_at.isoformat() if version2.modified_at else None,
            'modified_by': version2.modified_by
        },
        'differences': differences,
        'fields_changed': len(differences)
    }


def restore_project_version(project_id, version_id, restored_by):
    """
    Restaure un projet à une version antérieure

    ATTENTION: Cette opération crée une nouvelle version avec les données de l'ancienne version
    Elle ne supprime pas l'historique, mais ajoute une nouvelle entrée de type 'restore'

    Args:
        project_id: ID du projet
        version_id: ID de la version à restaurer
        restored_by: Username de la personne qui restaure

    Returns:
        bool: True si la restauration a réussi
    """
    try:
        project = Project.query.get(project_id)
        version = ProjectVersion.query.get(version_id)

        if not project or not version:
            print(f"[VERSIONING] ✗ Projet ou version introuvable")
            return False

        if version.project_id != project_id:
            print(f"[VERSIONING] ✗ La version ne correspond pas au projet")
            return False

        # Sauvegarder l'état actuel avant de restaurer
        current_statut = project.statut
        create_project_version(
            project,
            restored_by,
            'pre_restore',
            f'Sauvegarde avant restauration à version {version.version_number}',
            current_statut
        )

        # Charger les données de la version à restaurer
        old_data = json.loads(version.project_data)

        # Restaurer les champs (sauf id et numero_projet)
        restorable_fields = [
            'titre', 'description', 'secteur', 'poles', 'cout_estimatif',
            'region', 'departement', 'commune', 'latitude', 'longitude',
            'pays', 'ville', 'organisme', 'structure', 'nom_ministere'
        ]

        for field in restorable_fields:
            if field in old_data:
                setattr(project, field, old_data[field])

        db.session.commit()

        # Créer une nouvelle version de type 'restore'
        create_project_version(
            project,
            restored_by,
            'restore',
            f'Restauration depuis version {version.version_number} (modifiée le {version.modified_at.strftime("%d/%m/%Y à %H:%M")})',
            current_statut
        )

        print(f"[VERSIONING] ✓ Projet {project.numero_projet} restauré à version {version.version_number}")
        return True

    except Exception as e:
        print(f"[VERSIONING] ✗ Erreur lors de la restauration: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return False
