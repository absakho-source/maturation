"""
Routes pour l'export de données (CSV, Excel)
"""
from flask import Blueprint, jsonify, request, send_file
from models import Project, FicheEvaluation, User
from db import db
from utils.decorators import role_required
import csv
import io
from datetime import datetime

export_bp = Blueprint('export', __name__)

@export_bp.route('/api/export/projects/csv', methods=['GET'])
def export_projects_csv():
    """
    Export la liste des projets au format CSV

    Query params:
    - statut: Filtrer par statut (optionnel)
    - secteur: Filtrer par secteur (optionnel)
    - poles: Filtrer par pôle territorial (optionnel)
    """
    try:
        # Récupérer le rôle et username pour autorisation
        role = request.headers.get('X-Role', '')
        username = request.headers.get('X-Username', '')

        if not role or role not in ['admin', 'secretariatsct', 'presidencesct', 'presidencecomite', 'evaluateur']:
            return jsonify({'error': 'Non autorisé'}), 403

        # Construire la requête avec filtres
        query = Project.query

        # Filtres optionnels
        statut = request.args.get('statut')
        if statut:
            query = query.filter_by(statut=statut)

        secteur = request.args.get('secteur')
        if secteur:
            query = query.filter_by(secteur=secteur)

        poles = request.args.get('poles')
        if poles:
            query = query.filter(Project.poles.contains(poles))

        # Récupérer tous les projets
        projets = query.order_by(Project.date_soumission.desc()).all()

        # Créer le CSV en mémoire
        output = io.StringIO()
        writer = csv.writer(output)

        # En-têtes
        writer.writerow([
            'Numéro',
            'Titre',
            'Secteur',
            'Pôles territoriaux',
            'Coût estimatif (FCFA)',
            'Statut',
            'Soumissionnaire',
            'Évaluateur',
            'Avis',
            'Décision finale',
            'Date soumission',
            'Organisme',
            'Structure',
            'Ministère de tutelle',
            'Région',
            'Département',
            'Commune'
        ])

        # Lignes de données
        for projet in projets:
            # Récupérer le nom du soumissionnaire
            soumissionnaire = User.query.get(projet.soumissionnaire_id)
            soumissionnaire_nom = soumissionnaire.display_name if soumissionnaire else 'Inconnu'

            writer.writerow([
                projet.numero_projet or f'ID-{projet.id}',
                projet.titre,
                projet.secteur or '',
                projet.poles or '',
                projet.cout_estimatif or 0,
                projet.statut,
                soumissionnaire_nom,
                projet.evaluateur_nom or '',
                projet.avis or '',
                projet.decision_finale or '',
                projet.date_soumission.strftime('%d/%m/%Y %H:%M') if projet.date_soumission else '',
                projet.organisme or '',
                projet.structure or '',
                projet.nom_ministere or '',
                projet.region or '',
                projet.departement or '',
                projet.commune or ''
            ])

        # Préparer le fichier pour téléchargement
        output.seek(0)

        # Générer nom de fichier avec timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'projets_export_{timestamp}.csv'

        # Convertir en bytes avec encodage UTF-8 BOM (pour Excel)
        csv_bytes = io.BytesIO()
        csv_bytes.write('\ufeff'.encode('utf-8'))  # BOM pour Excel
        csv_bytes.write(output.getvalue().encode('utf-8'))
        csv_bytes.seek(0)

        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        print(f"Erreur export CSV: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@export_bp.route('/api/export/evaluations/csv', methods=['GET'])
def export_evaluations_csv():
    """
    Export la liste des fiches d'évaluation au format CSV

    Query params:
    - statut_projet: Filtrer par statut de projet (optionnel)
    """
    try:
        # Récupérer le rôle et username pour autorisation
        role = request.headers.get('X-Role', '')
        username = request.headers.get('X-Username', '')

        if not role or role not in ['admin', 'secretariatsct', 'presidencesct', 'presidencecomite']:
            return jsonify({'error': 'Non autorisé'}), 403

        # Construire la requête
        query = db.session.query(FicheEvaluation, Project).join(
            Project, FicheEvaluation.project_id == Project.id
        )

        # Filtre optionnel par statut de projet
        statut_projet = request.args.get('statut_projet')
        if statut_projet:
            query = query.filter(Project.statut == statut_projet)

        # Récupérer toutes les évaluations
        evaluations = query.order_by(FicheEvaluation.date_evaluation.desc()).all()

        # Créer le CSV en mémoire
        output = io.StringIO()
        writer = csv.writer(output)

        # En-têtes
        writer.writerow([
            'Numéro projet',
            'Titre projet',
            'Évaluateur',
            'Date évaluation',
            'Score total (/100)',
            'Pertinence (/5)',
            'Alignement doctrine (/10)',
            'Activités et coûts (/15)',
            'Équité territoriale (/15)',
            'Viabilité financière (/5)',
            'Rentabilité (/5)',
            'Bénéfices stratégiques (/15)',
            'Pérennité (/5)',
            'Avantages intangibles (/10)',
            'Faisabilité (/5)',
            'PPP (/5)',
            'Impact environnemental (/5)',
            'Avis',
            'Proposition',
            'Recommandations'
        ])

        # Lignes de données
        for fiche, projet in evaluations:
            writer.writerow([
                projet.numero_projet or f'ID-{projet.id}',
                projet.titre,
                fiche.evaluateur_nom or '',
                fiche.date_evaluation.strftime('%d/%m/%Y %H:%M') if fiche.date_evaluation else '',
                fiche.score_total or 0,
                fiche.pertinence_score or 0,
                fiche.alignement_doctrine_score or 0,
                fiche.activites_couts_score or 0,
                fiche.equite_territoriale_score or 0,
                fiche.viabilite_financiere_score or 0,
                fiche.rentabilite_score or 0,
                fiche.benefices_strategiques_score or 0,
                fiche.perennite_score or 0,
                fiche.avantages_intangibles_score or 0,
                fiche.faisabilite_score or 0,
                fiche.ppp_score or 0,
                fiche.impact_environnemental_score or 0,
                fiche.avis or '',
                fiche.proposition or '',
                fiche.recommandations or ''
            ])

        # Préparer le fichier pour téléchargement
        output.seek(0)

        # Générer nom de fichier avec timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'evaluations_export_{timestamp}.csv'

        # Convertir en bytes avec encodage UTF-8 BOM (pour Excel)
        csv_bytes = io.BytesIO()
        csv_bytes.write('\ufeff'.encode('utf-8'))  # BOM pour Excel
        csv_bytes.write(output.getvalue().encode('utf-8'))
        csv_bytes.seek(0)

        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        print(f"Erreur export évaluations CSV: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
