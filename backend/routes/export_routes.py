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

@export_bp.route('/api/export/projects/csv', methods=['GET', 'OPTIONS'])
def export_projects_csv():
    """
    Export la liste des projets au format CSV

    Query params:
    - statut: Filtrer par statut (optionnel)
    - secteur: Filtrer par secteur (optionnel)
    - poles: Filtrer par pôle territorial (optionnel)
    """
    # Gérer la requête OPTIONS (preflight CORS)
    if request.method == 'OPTIONS':
        return '', 204

    try:
        print(f"[EXPORT CSV] Début de l'export, requête depuis {username if 'username' in locals() else 'inconnu'}")

        # Récupérer le rôle et username pour autorisation
        role = request.headers.get('X-Role', '')
        username = request.headers.get('X-Username', '')

        print(f"[EXPORT CSV] Role: {role}, Username: {username}")

        if not role or role not in ['admin', 'secretariatsct', 'presidencesct', 'presidencecomite', 'evaluateur']:
            print(f"[EXPORT CSV] Accès refusé pour role: {role}")
            return jsonify({'error': 'Non autorisé'}), 403

        # Construire la requête avec filtres
        print("[EXPORT CSV] Construction de la requête...")
        query = Project.query

        # Filtres optionnels
        statut = request.args.get('statut')
        if statut:
            query = query.filter_by(statut=statut)
            print(f"[EXPORT CSV] Filtre statut: {statut}")

        secteur = request.args.get('secteur')
        if secteur:
            query = query.filter_by(secteur=secteur)
            print(f"[EXPORT CSV] Filtre secteur: {secteur}")

        poles = request.args.get('poles')
        if poles:
            query = query.filter(Project.poles.contains(poles))
            print(f"[EXPORT CSV] Filtre poles: {poles}")

        # Récupérer tous les projets
        print("[EXPORT CSV] Récupération des projets...")
        projets = query.order_by(Project.date_soumission.desc()).all()
        print(f"[EXPORT CSV] {len(projets)} projets trouvés")

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
            'Structure',
            'Ministère de tutelle'
        ])

        # Lignes de données
        for projet in projets:
            # Récupérer le nom du soumissionnaire
            soumissionnaire = User.query.get(projet.soumissionnaire_id) if projet.soumissionnaire_id else None
            soumissionnaire_nom = (soumissionnaire.display_name or soumissionnaire.username) if soumissionnaire else 'Inconnu'

            writer.writerow([
                projet.numero_projet or f'ID-{projet.id}',
                projet.titre or '',
                projet.secteur or '',
                projet.poles or '',
                str(int(projet.cout_estimatif)) if projet.cout_estimatif is not None else '0',
                projet.statut or '',
                soumissionnaire_nom or '',
                projet.evaluateur_nom or '',
                projet.avis or '',
                projet.decision_finale or '',
                projet.date_soumission.strftime('%d/%m/%Y %H:%M') if projet.date_soumission else '',
                projet.structure_soumissionnaire or '',
                projet.organisme_tutelle or ''
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
            mimetype='text/csv; charset=utf-8',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        print(f"Erreur export CSV: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@export_bp.route('/api/export/evaluations/csv', methods=['GET', 'OPTIONS'])
def export_evaluations_csv():
    """
    Export la liste des fiches d'évaluation au format CSV

    Query params:
    - statut_projet: Filtrer par statut de projet (optionnel)
    """
    # Gérer la requête OPTIONS (preflight CORS)
    if request.method == 'OPTIONS':
        return '', 204

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
                projet.titre or '',
                fiche.evaluateur_nom or '',
                fiche.date_evaluation.strftime('%d/%m/%Y %H:%M') if fiche.date_evaluation else '',
                str(fiche.score_total) if fiche.score_total is not None else '0',
                str(fiche.pertinence_score) if fiche.pertinence_score is not None else '0',
                str(fiche.alignement_doctrine_score) if fiche.alignement_doctrine_score is not None else '0',
                str(fiche.activites_couts_score) if fiche.activites_couts_score is not None else '0',
                str(fiche.equite_territoriale_score) if fiche.equite_territoriale_score is not None else '0',
                str(fiche.viabilite_financiere_score) if fiche.viabilite_financiere_score is not None else '0',
                str(fiche.rentabilite_score) if fiche.rentabilite_score is not None else '0',
                str(fiche.benefices_strategiques_score) if fiche.benefices_strategiques_score is not None else '0',
                str(fiche.perennite_score) if fiche.perennite_score is not None else '0',
                str(fiche.avantages_intangibles_score) if fiche.avantages_intangibles_score is not None else '0',
                str(fiche.faisabilite_score) if fiche.faisabilite_score is not None else '0',
                str(fiche.ppp_score) if fiche.ppp_score is not None else '0',
                str(fiche.impact_environnemental_score) if fiche.impact_environnemental_score is not None else '0',
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
            mimetype='text/csv; charset=utf-8',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        print(f"Erreur export évaluations CSV: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
