import sys
import os
import json
import shutil
import requests
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from flask import Flask, request, jsonify, send_from_directory, send_file
from db import db
from models import Project, User, FicheEvaluation, Historique, DocumentProjet, MessageProjet, FichierMessage, FormulaireConfig, SectionFormulaire, ChampFormulaire, CritereEvaluation, ConnexionLog, Log, Notification, ContactMessage, ProjectVersion, EmailTemplate
from flask_cors import CORS
from utils.archivage import archiver_fiche
from workflow_validator import WorkflowValidator
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
from pdf_generator_dgppe import generer_fiche_evaluation_dgppe_pdf
from io import BytesIO
from reportlab.lib.pagesizes import A4
import email_service
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-me-in-production"

# Configuration pour gérer correctement les proxies (Render, Nginx, etc.)
# x_for=1: Fait confiance à 1 proxy pour X-Forwarded-For (IP réelle du client)
# x_proto=1: Fait confiance à 1 proxy pour X-Forwarded-Proto (http/https)
# x_host=1: Fait confiance à 1 proxy pour X-Forwarded-Host
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Configuration du stockage persistant
# En production Render, utilise /data (disque persistant)
# En local, utilise le dossier backend
DATA_DIR = os.environ.get("DATA_DIR", os.path.abspath(os.path.dirname(__file__)))
print(f"[CONFIG] DATA_DIR: {DATA_DIR}")

# Créer le dossier data s'il n'existe pas
os.makedirs(DATA_DIR, exist_ok=True)

# Configuration de la base de données
app.config["DB_PATH"] = os.path.join(DATA_DIR, "maturation.db")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + app.config["DB_PATH"]
print(f"[CONFIG] Using DB: {app.config['DB_PATH']}")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configuration du dossier uploads
app.config["UPLOAD_FOLDER"] = os.path.join(DATA_DIR, "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
# Configuration de la taille maximale des fichiers (50MB)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
print(f"[CONFIG] Using UPLOAD_FOLDER: {app.config['UPLOAD_FOLDER']}")
print(f"[CONFIG] MAX_CONTENT_LENGTH: {app.config['MAX_CONTENT_LENGTH'] / (1024*1024)}MB")

# Configuration CORS pour permettre les requêtes depuis le frontend
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://127.0.0.1:5173",  # Dev local
            "http://localhost:5173",
            "https://maturation-frontend.onrender.com"  # Production
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Cache-Control", "Pragma", "X-Role", "X-Username"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "Authorization"],
        "max_age": 3600  # Cache preflight pour 1 heure
    }
})

# Handler supplémentaire pour les requêtes OPTIONS
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    allowed_origins = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "https://maturation-frontend.onrender.com"
    ]
    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cache-Control, Pragma, X-Role, X-Username'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

db.init_app(app)

# Fonction pour générer le numéro de projet automatiquement
def generer_numero_projet():
    """Génère un numéro de projet au format DGPPE-YY-NNN où YY = 2 derniers chiffres de l'année et NNN = compteur séquentiel annuel"""

    # Format année actuelle sur 2 chiffres
    now = datetime.now()
    year = now.strftime("%y")  # Exemple: 25 pour 2025
    prefix = f"DGPPE-{year}-"

    # Trouver le dernier numéro pour cette année
    last_project = Project.query.filter(
        Project.numero_projet.like(f"{prefix}%")
    ).order_by(Project.numero_projet.desc()).first()

    if last_project and last_project.numero_projet:
        # Extraire le numéro séquentiel des 3 derniers chiffres
        try:
            last_number = int(last_project.numero_projet.split('-')[-1])
            next_number = last_number + 1
        except (ValueError, IndexError):
            next_number = 1
    else:
        next_number = 1

    # Assurer que le numéro reste sur 3 chiffres (max 999 projets par an)
    if next_number > 999:
        raise ValueError("Limite de 999 projets par an atteinte")

    return f"{prefix}{next_number:03d}"

# Helper pour accéder au champ statut_comite de manière sécurisée
def get_statut_comite(projet):
    """
    Retourne le statut_comite d'un projet de manière sécurisée.
    Gère le cas où la colonne n'existe pas encore (migration en cours).
    """
    try:
        return getattr(projet, 'statut_comite', None)
    except Exception:
        return None

def set_statut_comite(projet, valeur):
    """
    Définit le statut_comite d'un projet de manière sécurisée.
    Gère le cas où la colonne n'existe pas encore (migration en cours).
    """
    try:
        if hasattr(projet, 'statut_comite'):
            projet.statut_comite = valeur
        return True
    except Exception:
        return False

# Fonction pour simplifier les statuts vus par le soumissionnaire
def get_statut_soumissionnaire(projet):
    """Convertit les statuts internes en statuts simplifiés pour le soumissionnaire"""
    statut_reel = projet.statut

    # PRIORITÉ 1: Décision finale du Comité
    if projet.decision_finale == 'confirme' and projet.avis:
        # Décision confirmée par le Comité = avis final validé
        return projet.avis  # "favorable", "favorable sous conditions", "défavorable"
    elif projet.decision_finale == 'infirme':
        # Décision infirmée par le Comité = retour au Secrétariat SCT pour réexamen
        # On ne montre PAS de décision finale, on affiche "en réexamen"
        return "en réexamen"

    # PRIORITÉ 2: Si le projet est approuvé (sans passer par le comité), afficher l'avis
    if statut_reel == "approuvé" and projet.avis:
        return projet.avis  # "favorable", "favorable sous conditions", "défavorable"

    # PRIORITÉ 3: Si le projet est rejeté avant comité, il retourne vers le secrétariat → "en instruction"
    if statut_reel == "rejeté":
        return "en instruction"

    # PRIORITÉ 4: Statuts simplifiés selon les étapes du workflow
    if statut_reel == "soumis":
        return "soumis"
    elif statut_reel == "assigné":
        return "assigné"
    elif statut_reel == "compléments demandés":
        return "compléments demandés"
    elif statut_reel == "compléments fournis":
        return "compléments fournis"
    else:
        # Tous les autres statuts internes = "en instruction"
        return "en instruction"

# ============ FONCTIONS HELPERS POUR LES NOTIFICATIONS ============

def create_notification_for_user(user_id, notif_type, titre, message, project_id=None, lien=None, priorite_email=False):
    """Crée une notification pour un utilisateur"""
    try:
        notification = Notification(
            user_id=user_id,
            project_id=project_id,
            type=notif_type,
            titre=titre,
            message=message,
            lien=lien,
            priorite_email=priorite_email
        )
        db.session.add(notification)
        return notification
    except Exception as e:
        print(f"[NOTIFICATION] Erreur création: {e}")
        return None

def notify_user_by_username(username, notif_type, titre, message, project_id=None, lien=None, priorite_email=False):
    """Crée une notification pour un utilisateur par son username"""
    user = User.query.filter_by(username=username).first()
    if user:
        return create_notification_for_user(user.id, notif_type, titre, message, project_id, lien, priorite_email)
    return None

def notify_users_by_role(role, notif_type, titre, message, project_id=None, lien=None, priorite_email=False):
    """Crée des notifications pour tous les utilisateurs d'un rôle donné"""
    users = User.query.filter_by(role=role).all()
    for user in users:
        create_notification_for_user(user.id, notif_type, titre, message, project_id, lien, priorite_email)

def notify_project_owner(project, notif_type, titre, message, lien=None, priorite_email=False):
    """Notifie le propriétaire d'un projet"""
    if project and project.soumissionnaire_id:
        return create_notification_for_user(
            project.soumissionnaire_id, notif_type, titre, message,
            project.id, lien, priorite_email
        )
    return None

# Migration de base de données: ajout automatique des colonnes manquantes
def ensure_sqlite_columns():
    import sqlite3
    con = sqlite3.connect(app.config["DB_PATH"])
    cur = con.cursor()

    # Migration pour la table projects
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
    if cur.fetchone():
        cur.execute("PRAGMA table_info(projects)")
        cols = {r[1] for r in cur.fetchall()}
        needed = {
            "numero_projet": "TEXT",
            "validation_secretariat": "TEXT",
            "commentaires_finaux": "TEXT",
            "complements_demande_message": "TEXT",
            "complements_reponse_message": "TEXT",
            "complements_reponse_pieces": "TEXT",
            "auteur_nom": "TEXT",
        }
        for c, cdef in needed.items():
            if c not in cols:
                print(f"[DB MIGRATION] Adding projects.{c}")
                cur.execute(f"ALTER TABLE projects ADD COLUMN {c} {cdef}")

    # Migration pour la table connexion_log (geolocation columns)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='connexion_log'")
    if cur.fetchone():
        cur.execute("PRAGMA table_info(connexion_log)")
        cols = {r[1] for r in cur.fetchall()}
        needed_geo = {
            "pays": "VARCHAR(100)",
            "ville": "VARCHAR(100)",
            "region": "VARCHAR(100)"
        }
        for c, cdef in needed_geo.items():
            if c not in cols:
                print(f"[DB MIGRATION] Adding connexion_log.{c}")
                cur.execute(f"ALTER TABLE connexion_log ADD COLUMN {c} {cdef}")

    # Migration pour la table project (lieu de soumission - territorialisation)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project'")
    if cur.fetchone():
        cur.execute("PRAGMA table_info(project)")
        cols = {r[1] for r in cur.fetchall()}
        needed_lieu = {
            "lieu_soumission_pays": "VARCHAR(100)",
            "lieu_soumission_ville": "VARCHAR(100)",
            "lieu_soumission_region": "VARCHAR(100)"
        }
        for c, cdef in needed_lieu.items():
            if c not in cols:
                print(f"[DB MIGRATION] Adding project.{c}")
                cur.execute(f"ALTER TABLE project ADD COLUMN {c} {cdef}")

        # Migration pour la matrice d'évaluation préalable
        needed_matrice = {
            "evaluation_prealable_matrice": "TEXT"
        }
        for c, cdef in needed_matrice.items():
            if c not in cols:
                print(f"[DB MIGRATION] Adding project.{c}")
                cur.execute(f"ALTER TABLE project ADD COLUMN {c} {cdef}")

    # Migration pour la table contact_messages
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contact_messages'")
    if cur.fetchone():
        cur.execute("PRAGMA table_info(contact_messages)")
        cols = {r[1] for r in cur.fetchall()}
        needed_contact = {
            "pieces_jointes": "TEXT",
            "assigne_a": "VARCHAR(100)",
            "date_assignation": "DATETIME",
            "date_reponse": "DATETIME"
        }
        for c, cdef in needed_contact.items():
            if c not in cols:
                print(f"[DB MIGRATION] Adding contact_messages.{c}")
                cur.execute(f"ALTER TABLE contact_messages ADD COLUMN {c} {cdef}")

    # Migration pour la table users (Point Focal + ministère/tutelle + must_change_password)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cur.fetchone():
        cur.execute("PRAGMA table_info(users)")
        cols = {r[1] for r in cur.fetchall()}
        needed_user_cols = {
            "is_point_focal": "BOOLEAN DEFAULT 0",
            "point_focal_organisme": "VARCHAR(300)",
            "nom_ministere": "VARCHAR(300)",
            "tutelle_agence": "VARCHAR(300)",
            "must_change_password": "BOOLEAN DEFAULT 0"
        }
        for c, cdef in needed_user_cols.items():
            if c not in cols:
                print(f"[DB MIGRATION] Adding users.{c}")
                cur.execute(f"ALTER TABLE users ADD COLUMN {c} {cdef}")

    # Migration pour la table project_version (versioning)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='project_version'")
    if not cur.fetchone():
        print(f"[DB MIGRATION] Creating project_version table")
        cur.execute("""
            CREATE TABLE project_version (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                version_number INTEGER NOT NULL,
                modified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                modified_by VARCHAR(100),
                modification_type VARCHAR(50),
                change_summary TEXT,
                project_data TEXT NOT NULL,
                statut_before VARCHAR(100),
                statut_after VARCHAR(100),
                FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE
            )
        """)
        cur.execute("CREATE INDEX idx_project_version_project_id ON project_version(project_id)")
        cur.execute("CREATE INDEX idx_project_version_modified_at ON project_version(modified_at)")

    con.commit()
    con.close()

def _save_files(files):
    upload_folder = app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    filenames = []
    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            filenames.append(filename)
    return filenames

def _archiver_fiche_evaluation(fiche, project, auteur="system"):
    """
    Archive une fiche d'évaluation dans la documenthèque du projet.
    La fiche archivée n'est PAS visible pour le soumissionnaire.

    Args:
        fiche: Instance FicheEvaluation à archiver
        project: Instance Project associée
        auteur: Nom de l'auteur de l'archivage

    Returns:
        bool: True si l'archivage a réussi, False sinon
    """
    if not fiche:
        return False

    try:
        # Préparer les données pour générer le PDF
        fiche_data = fiche.to_dict()
        project_data = project.to_dict()

        # Créer un répertoire temporaire pour générer le PDF
        import tempfile
        temp_dir = tempfile.mkdtemp()

        try:
            # Générer le PDF de la fiche d'évaluation
            pdf_path = generer_fiche_evaluation_dgppe_pdf(fiche_data, project_data, temp_dir)

            # Créer le nom du fichier archivé avec timestamp et évaluateur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            evaluateur = fiche.evaluateur_nom or "inconnu"
            nom_archive = f"Fiche_Evaluation_Archivee_{evaluateur}_{timestamp}.pdf"

            # Copier le PDF vers le dossier des documents du projet
            documents_folder = os.path.join(app.config["UPLOAD_FOLDER"], "documents_projet")
            os.makedirs(documents_folder, exist_ok=True)

            dest_path = os.path.join(documents_folder, nom_archive)
            shutil.copy2(pdf_path, dest_path)

            # Obtenir la taille du fichier
            taille_fichier = os.path.getsize(dest_path)

            # Créer l'entrée dans la table documents_projet
            # Rôles autorisés: tous sauf soumissionnaire
            # Inclure "evaluateur" pour couvrir tous les évaluateurs génériques, et "admin" pour gestion
            roles_autorises = ["admin", "evaluateur", "evaluateur1", "evaluateur2", "secretariatsct", "presidencesct", "presidencecomite"]

            document = DocumentProjet(
                project_id=project.id,
                nom_fichier=nom_archive,
                nom_original=f"Fiche_Evaluation_{evaluateur}.pdf",
                description=f"Fiche d'évaluation archivée lors de la réassignation (Score: {fiche.score_total}/100)",
                type_document="fiche_evaluation_archivee",
                auteur_nom=auteur,
                auteur_role="system",
                taille_fichier=taille_fichier,
                visible_pour_roles=json.dumps(roles_autorises)
            )

            db.session.add(document)
            db.session.flush()  # Pour obtenir l'ID du document

            print(f"[ARCHIVAGE] Fiche d'évaluation archivée: {nom_archive} (Document ID: {document.id})")

            return True

        finally:
            # Nettoyer le répertoire temporaire
            import shutil as shutil_cleanup
            try:
                shutil_cleanup.rmtree(temp_dir)
            except Exception:
                pass

    except Exception as e:
        print(f"[ERREUR ARCHIVAGE] Échec de l'archivage de la fiche d'évaluation: {e}")
        import traceback
        traceback.print_exc()
        return False

# Routes
@app.route("/api/projects", methods=["GET", "POST"])
@app.route("/api/projets", methods=["GET", "POST"])  # Alias français
def projects():
    if request.method == "GET":
        try:
            role = request.args.get("role", "")
            username = request.args.get("username", "")

            # Correction : filtrage pour le dashboard soumissionnaire
            if role == "soumissionnaire" and username:
                items = Project.query.filter_by(auteur_nom=username).all()
            elif role == "evaluateur":
                # Les évaluateurs voient tous les projets de l'équipe
                items = Project.query.all()
            elif role == "presidencecomite":
                items = Project.query.all()
            elif role in ["secretariatsct", "presidencesct", "admin"]:
                items = Project.query.all()
            elif role == "invite":
                # Rôle invité: voir tous les projets mais avec données limitées
                items = Project.query.all()
            else:
                items = Project.query.all()

            # Filter out projects from suspended accounts
            # Note: Projects from non-verified accounts ARE visible but will be marked with soumissionnaire_statut_compte
            if role in ['secretariatsct', 'presidencesct', 'presidencecomite', 'evaluateur', 'admin']:
                # These roles should not see projects from suspended accounts in their workflow
                # Get list of suspended user IDs
                suspended_users = User.query.filter_by(statut_compte='suspendu').all()
                suspended_ids = [u.id for u in suspended_users]
                # Filter out ONLY projects from suspended users (not projects without soumissionnaire_id)
                items = [p for p in items if not (p.soumissionnaire_id and p.soumissionnaire_id in suspended_ids)]

            # Correction : si aucun projet, retourne explicitement une liste vide
            if not items:
                return jsonify([]), 200

            result = []
            for p in items:
                try:
                    if role == "soumissionnaire" or role == "invite":
                        statut_affiche = get_statut_soumissionnaire(p)
                    else:
                        # Pour les rôles internes (admin, secrétariat, présidence, évaluateur):
                        # Si une décision finale confirmée existe, afficher l'avis en priorité
                        if p.decision_finale == 'confirme' and p.avis:
                            # Afficher directement l'avis: favorable, favorable sous conditions, défavorable
                            statut_affiche = p.avis
                        elif p.decision_finale == 'infirme':
                            # Décision infirmée par le Comité = retour au Secrétariat SCT
                            statut_affiche = 'en réexamen par le Secrétariat SCT'
                        else:
                            # Pas de décision finale ou décision non confirmée
                            statut_affiche = p.statut

                    pieces_jointes = []
                    if p.pieces_jointes:
                        if isinstance(p.pieces_jointes, str):
                            pieces_jointes = [f for f in p.pieces_jointes.split(",") if f]
                        elif isinstance(p.pieces_jointes, list):
                            pieces_jointes = p.pieces_jointes

                    date_soumission = None
                    if hasattr(p, "date_soumission") and p.date_soumission:
                        try:
                            date_soumission = p.date_soumission.isoformat()
                        except Exception:
                            date_soumission = str(p.date_soumission)

                    # Récupérer le display_name et le rôle de l'évaluateur si applicable
                    evaluateur_display_name = ""
                    evaluateur_role = ""
                    if p.evaluateur_nom:
                        evaluateur = User.query.filter_by(username=p.evaluateur_nom).first()
                        if evaluateur:
                            evaluateur_display_name = evaluateur.display_name or evaluateur.username
                            evaluateur_role = evaluateur.role or ""

                    # Récupérer le statut de compte du soumissionnaire
                    soumissionnaire_statut_compte = ""
                    if p.auteur_nom:
                        soumissionnaire = User.query.filter_by(username=p.auteur_nom).first()
                        if soumissionnaire:
                            soumissionnaire_statut_compte = soumissionnaire.statut_compte or ""

                    # Conversion de evaluation_prealable_date
                    evaluation_prealable_date = None
                    if hasattr(p, "evaluation_prealable_date") and p.evaluation_prealable_date:
                        try:
                            evaluation_prealable_date = p.evaluation_prealable_date.isoformat()
                        except Exception:
                            evaluation_prealable_date = str(p.evaluation_prealable_date)

                    # Vérifier si le projet est assigné à l'utilisateur connecté ou à son équipe (même rôle)
                    # Pour secretariatsct: tous les membres de l'équipe voient les projets assignés à n'importe quel secretariatsct
                    # Pour evaluateur: chaque évaluateur voit uniquement ses propres projets
                    est_assigne_a_moi = False
                    if role and username and p.evaluateur_nom:
                        if role == "secretariatsct":
                            # Tous les secretariatsct voient les projets assignés à n'importe quel secretariatsct
                            est_assigne_a_moi = (evaluateur_role == "secretariatsct")
                        elif role == "evaluateur":
                            # Les évaluateurs voient uniquement leurs propres projets
                            est_assigne_a_moi = (p.evaluateur_nom == username)
                        else:
                            est_assigne_a_moi = (p.evaluateur_nom == username)

                    # Rôle invité: retourner SEULEMENT les champs de base (pas de données sensibles)
                    if role == "invite":
                        result.append({
                            "id": int(p.id) if p.id is not None else None,
                            "numero_projet": str(p.numero_projet) if p.numero_projet else "",
                            "titre": str(p.titre) if p.titre else "",
                            "secteur": str(p.secteur) if p.secteur else "",
                            "poles": str(p.poles) if p.poles else "",
                            "statut": str(statut_affiche) if statut_affiche else "",
                            "date_soumission": date_soumission,
                            "nouveaute": str(p.nouveaute) if p.nouveaute else "",
                            "niveau_priorite": str(p.niveau_priorite) if p.niveau_priorite else "",
                            "type_financement": str(p.type_financement) if p.type_financement else "",
                            "soumissionnaire_statut_compte": str(soumissionnaire_statut_compte)
                        })
                    else:
                        # Correction : conversion systématique des champs pour éviter les erreurs de type
                        result.append({
                            "id": int(p.id) if p.id is not None else None,
                            "numero_projet": str(p.numero_projet) if p.numero_projet else "",
                            "titre": str(p.titre) if p.titre else "",
                            "description": str(p.description) if p.description else "",
                            "secteur": str(p.secteur) if p.secteur else "",
                            "poles": str(p.poles) if p.poles else "",
                            "cout_estimatif": float(p.cout_estimatif) if p.cout_estimatif else 0,
                            "organisme_tutelle": str(p.organisme_tutelle) if p.organisme_tutelle else "",
                            "auteur_nom": str(p.auteur_nom) if p.auteur_nom else "",
                            "statut": str(statut_affiche) if statut_affiche else "",
                            "evaluateur_nom": str(p.evaluateur_nom) if p.evaluateur_nom else "",
                            "evaluateur_display_name": str(evaluateur_display_name),
                            "evaluateur_role": str(evaluateur_role),
                            "est_assigne_a_moi": est_assigne_a_moi,
                            "avis": str(p.avis) if p.avis else "",
                            "commentaires": str(p.commentaires) if p.commentaires else "",
                            "validation_secretariat": str(p.validation_secretariat) if p.validation_secretariat else "",
                            "avis_presidencesct": str(p.avis_presidencesct) if p.avis_presidencesct else "",
                            "decision_finale": str(p.decision_finale) if p.decision_finale else "",
                            "statut_comite": str(get_statut_comite(p)) if get_statut_comite(p) else "",
                            "commentaires_finaux": str(p.commentaires_finaux) if p.commentaires_finaux else "",
                            "complements_demande_message": str(p.complements_demande_message) if p.complements_demande_message else "",
                            "complements_reponse_message": str(p.complements_reponse_message) if p.complements_reponse_message else "",
                            "complements_reponse_pieces": str(p.complements_reponse_pieces) if p.complements_reponse_pieces else "",
                            "evaluation_prealable": str(p.evaluation_prealable) if p.evaluation_prealable else "",
                            "evaluation_prealable_date": evaluation_prealable_date,
                            "evaluation_prealable_commentaire": str(p.evaluation_prealable_commentaire) if p.evaluation_prealable_commentaire else "",
                            "evaluation_prealable_commentaires": str(p.evaluation_prealable_commentaire) if p.evaluation_prealable_commentaire else "",  # Alias pour compatibilité frontend
                            "pieces_jointes": pieces_jointes,
                            "date_soumission": date_soumission,
                            "fiche_evaluation_visible": p.fiche_evaluation_visible if hasattr(p, 'fiche_evaluation_visible') else False,
                            "nouveaute": str(p.nouveaute) if p.nouveaute else "",
                            "projet_initial_ref": str(p.projet_initial_ref) if p.projet_initial_ref else "",
                            "niveau_priorite": str(p.niveau_priorite) if p.niveau_priorite else "",
                            "type_financement": str(p.type_financement) if p.type_financement else "",
                            "soumissionnaire_statut_compte": str(soumissionnaire_statut_compte)
                        })
                except Exception as err:
                    import traceback
                    print(f"[ERROR] Projet id={getattr(p, 'id', None)}: {err}")
                    traceback.print_exc()
            return jsonify(result), 200
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify([]), 500

    # POST: soumission d'un projet
    try:
        auteur_nom = request.form.get("auteur_nom")

        # Vérifier le statut du compte de l'utilisateur
        # Les comptes non vérifiés PEUVENT soumettre, mais leurs projets seront "grisés" jusqu'à validation
        if auteur_nom:
            user = User.query.filter_by(username=auteur_nom).first()
            if user:
                if user.statut_compte == 'suspendu':
                    return jsonify({
                        "error": "Votre compte est suspendu. Vous ne pouvez pas soumettre de projet."
                    }), 403

        titre = request.form.get("titre")
        description = request.form.get("description")
        secteur = request.form.get("secteur")
        poles = request.form.get("poles")  # CSV
        cout_estimatif = request.form.get("cout_estimatif")
        organisme_tutelle = request.form.get("organisme_tutelle")
        organisme_tutelle_data = request.form.get("organisme_tutelle_data")  # JSON structuré
        structure_soumissionnaire = request.form.get("structure_soumissionnaire")

        # Nouveaux champs (Décembre 2025)
        nouveaute = request.form.get("nouveaute")
        projet_initial_ref = request.form.get("projet_initial_ref")
        niveau_priorite = request.form.get("niveau_priorite")
        type_financement = request.form.get("type_financement")  # JSON array

        # Récupérer tous les fichiers catégorisés
        files = []
        files.extend(request.files.getlist("lettre_soumission"))
        files.extend(request.files.getlist("note_conceptuelle"))
        files.extend(request.files.getlist("etudes_plans"))
        files.extend(request.files.getlist("autres_pieces"))
        files.extend(request.files.getlist("files"))  # Garde la compatibilité

        filenames = _save_files(files)

        # Générer le numéro de projet automatiquement
        numero_projet = generer_numero_projet()

        # Récupérer les coordonnées GPS si fournies
        gps_coords_str = request.form.get("gps_coordinates")
        gps_latitude = None
        gps_longitude = None
        gps_accuracy = None

        if gps_coords_str:
            try:
                import json
                gps_coords = json.loads(gps_coords_str)
                gps_latitude = gps_coords.get('latitude')
                gps_longitude = gps_coords.get('longitude')
                gps_accuracy = gps_coords.get('accuracy')
                print(f"[SOUMISSION] Coordonnées GPS reçues: lat={gps_latitude}, lon={gps_longitude}, accuracy={gps_accuracy}m")
            except Exception as e:
                print(f"[SOUMISSION] Erreur parsing GPS coordinates: {e}")

        # Capturer le lieu de soumission depuis le formulaire (priorité) ou via géolocalisation (fallback)
        lieu_pays = request.form.get("lieu_soumission_pays")
        lieu_ville = request.form.get("lieu_soumission_ville")
        lieu_region = request.form.get("lieu_soumission_region")

        # Si les champs ne sont pas fournis, essayer la géolocalisation IP (fallback)
        if not lieu_pays or not lieu_ville or not lieu_region:
            # Récupérer l'adresse IP réelle (en tenant compte des proxies)
            ip_address = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
            if not ip_address:
                ip_address = request.headers.get('X-Real-IP', '').strip()
            if not ip_address:
                ip_address = request.remote_addr

            print(f"[SOUMISSION] IP détectée pour géolocalisation: {ip_address}")

            try:
                geo_pays, geo_ville, geo_region = get_geolocation(ip_address)
                lieu_pays = lieu_pays or geo_pays
                lieu_ville = lieu_ville or geo_ville
                lieu_region = lieu_region or geo_region
                print(f"[SOUMISSION] Géolocalisation IP utilisée: {geo_ville}, {geo_region}, {geo_pays} (IP: {ip_address})")
            except Exception as e:
                print(f"[SOUMISSION] Impossible de géolocaliser l'IP {ip_address}: {e}")
        else:
            print(f"[SOUMISSION] Projet soumis depuis (formulaire): {lieu_ville}, {lieu_region}, {lieu_pays}")

        project = Project(
            numero_projet=numero_projet,
            titre=titre,
            description=description,
            secteur=secteur,
            poles=poles,
            cout_estimatif=float(cout_estimatif) if cout_estimatif else None,
            organisme_tutelle=organisme_tutelle,
            organisme_tutelle_data=organisme_tutelle_data,
            structure_soumissionnaire=structure_soumissionnaire,
            pieces_jointes=",".join(filenames) if filenames else None,
            auteur_nom=auteur_nom,
            lieu_soumission_pays=lieu_pays,
            lieu_soumission_ville=lieu_ville,
            lieu_soumission_region=lieu_region,
            gps_latitude=gps_latitude,
            gps_longitude=gps_longitude,
            gps_accuracy=gps_accuracy,
            nouveaute=nouveaute,
            projet_initial_ref=projet_initial_ref,
            niveau_priorite=niveau_priorite,
            type_financement=type_financement
        )
        db.session.add(project)
        db.session.commit()

        hist = Historique(
            project_id=project.id,
            action=f"Projet '{titre}' soumis avec le numéro {numero_projet}",
            auteur=auteur_nom,
            role="soumissionnaire"
        )
        db.session.add(hist)
        db.session.commit()

        # Notifier les points focaux si le projet a un organisme de tutelle
        try:
            from routes.point_focal_routes import notifier_point_focal_nouveau_projet
            notifier_point_focal_nouveau_projet(project)
        except Exception as notif_err:
            print(f"Erreur notification point focal: {notif_err}")

        return jsonify({
            "message": "Projet soumis avec succès",
            "id": project.id,
            "numero_projet": numero_projet
        }), 201

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<int:project_id>", methods=["GET"])
def get_project(project_id):
    try:
        # Vérifier le rôle de l'utilisateur (passé en query params ou headers)
        role = request.args.get("role", "")
        username = request.args.get("username", "")

        # Les invités ne peuvent pas accéder aux détails des projets
        if role == "invite":
            return jsonify({"error": "Accès refusé: Les invités ne peuvent pas voir les détails des projets"}), 403

        p = Project.query.get_or_404(project_id)

        # Récupérer le display_name de l'évaluateur si applicable
        evaluateur_display_name = ""
        if p.evaluateur_nom:
            evaluateur = User.query.filter_by(username=p.evaluateur_nom).first()
            if evaluateur:
                evaluateur_display_name = evaluateur.display_name or evaluateur.username

        # Récupérer le statut de compte du soumissionnaire
        soumissionnaire_statut_compte = ""
        if p.auteur_nom:
            soumissionnaire = User.query.filter_by(username=p.auteur_nom).first()
            if soumissionnaire:
                soumissionnaire_statut_compte = soumissionnaire.statut_compte or ""

        return jsonify({
            "id": p.id,
            "numero_projet": p.numero_projet,
            "titre": p.titre,
            "description": p.description,
            "secteur": p.secteur,
            "poles": p.poles,
            "cout_estimatif": p.cout_estimatif,
            "auteur_nom": p.auteur_nom,
            "statut": p.statut,
            "evaluateur_nom": p.evaluateur_nom,
            "evaluateur_display_name": evaluateur_display_name,
            "avis": p.avis,
            "commentaires": p.commentaires,
            "validation_secretariat": p.validation_secretariat,
            "avis_presidencesct": p.avis_presidencesct,
            "decision_finale": p.decision_finale,
            "statut_comite": get_statut_comite(p),
            "commentaires_finaux": p.commentaires_finaux,
            "complements_demande_message": p.complements_demande_message,
            "complements_reponse_message": p.complements_reponse_message,
            "complements_reponse_pieces": p.complements_reponse_pieces,
            "pieces_jointes": p.pieces_jointes.split(",") if p.pieces_jointes else [],
            "date_soumission": p.date_soumission.isoformat() if p.date_soumission else None,
            "lieu_soumission_pays": p.lieu_soumission_pays,
            "lieu_soumission_ville": p.lieu_soumission_ville,
            "lieu_soumission_region": p.lieu_soumission_region,
            "organisme_tutelle": p.organisme_tutelle,
            "organisme_tutelle_data": p.organisme_tutelle_data,
            "structure_soumissionnaire": p.structure_soumissionnaire,
            "fiche_evaluation_visible": p.fiche_evaluation_visible if hasattr(p, 'fiche_evaluation_visible') else False,
            "nouveaute": p.nouveaute,
            "projet_initial_ref": p.projet_initial_ref,
            "niveau_priorite": p.niveau_priorite,
            "type_financement": p.type_financement,
            "soumissionnaire_statut_compte": soumissionnaire_statut_compte
        }), 200
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<int:project_id>", methods=["DELETE", "OPTIONS"])
def delete_project(project_id):
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        role = request.args.get('role', '').lower()
        if role != 'admin':
            return jsonify({"error": "Accès non autorisé. Seuls les administrateurs peuvent supprimer des projets."}), 403

        # Récupérer le projet
        project = Project.query.get_or_404(project_id)
        projet_titre = project.titre
        projet_numero = project.numero_projet

        # Supprimer tous les enregistrements liés AVANT de supprimer le projet
        # 1. Supprimer les fiches d'évaluation
        FicheEvaluation.query.filter_by(project_id=project_id).delete()

        # 2. Supprimer les documents du projet
        DocumentProjet.query.filter_by(project_id=project_id).delete()

        # 3. Supprimer l'historique
        Historique.query.filter_by(project_id=project_id).delete()

        # 4. Supprimer les messages de discussion
        MessageProjet.query.filter_by(project_id=project_id).delete()

        # 5. Supprimer les logs
        Log.query.filter_by(projet_id=project_id).delete()

        # 6. Maintenant on peut supprimer le projet
        db.session.delete(project)
        db.session.commit()

        print(f"[ADMIN] Projet supprimé: {projet_numero} - {projet_titre}")
        return jsonify({"message": "Projet supprimé avec succès"}), 200

    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({"error": f"Erreur lors de la suppression: {str(e)}"}), 500

@app.route("/api/projects/<int:project_id>/traiter", methods=["POST"])
def traiter_project(project_id):
    try:
        print(f"[TRAITER_DEBUG] Fonction traiter_project appelée pour projet {project_id}")
        data = request.json or {}
        p = Project.query.get_or_404(project_id)
        print(f"[TRAITER_DEBUG] Projet trouvé: {p.titre}, Statut actuel: {p.statut}, Auteur: {p.auteur_nom}")
        auteur = data.get("auteur", "")
        role = data.get("role", "")
        username = data.get("username", auteur)
        action = ""
        print(f"[TRAITER_DEBUG] Data reçue: {data}")

        # Vérifier que l'utilisateur a le rôle nécessaire pour traiter le projet
        # Seuls secretariatsct, presidencesct, presidencecomite, evaluateur et admin peuvent traiter
        roles_autorises = ['secretariatsct', 'presidencesct', 'presidencecomite', 'evaluateur', 'admin']
        if role not in roles_autorises:
            return jsonify({"error": "Vous n'avez pas les permissions pour traiter ce projet"}), 403

        # Vérifier le statut du soumissionnaire
        if p.auteur_nom:
            soumissionnaire = User.query.filter_by(username=p.auteur_nom).first()
            if soumissionnaire:
                if soumissionnaire.statut_compte == 'suspendu':
                    return jsonify({
                        "error": "Ce projet ne peut pas être traité car le compte du soumissionnaire est suspendu. Veuillez contacter l'administration pour réintégrer le compte avant de traiter ce projet."
                    }), 403
                elif soumissionnaire.statut_compte == 'non_verifie':
                    return jsonify({
                        "error": "Ce projet ne peut pas être traité car le compte du soumissionnaire n'a pas encore été vérifié."
                    }), 403

        # Détection de l'intention de réassignation explicite
        is_reassignment = (
            data.get("validation_secretariat") == "reassigne" or
            (p.evaluateur_nom and "evaluateur_nom" in data and "avis" not in data)
        )

        # Assignation (mais pas pour la réassignation de projets rejetés)
        if ("evaluateur_nom" in data and "avis" not in data and data.get("validation_secretariat") != "reassigne"
            and data.get("statut_action") != "reassigner_rejete"):

            # Vérifier que le projet n'a pas de statut définitif (seulement lors d'une réassignation)
            # Si c'est une première assignation (pas d'évaluateur existant), on autorise
            if p.evaluateur_nom:  # C'est une réassignation
                statuts_definitifs = ['favorable', 'favorable sous conditions', 'défavorable']
                if (p.statut in statuts_definitifs or p.avis in statuts_definitifs or
                    p.decision_finale == 'confirme' or get_statut_comite(p) == 'approuve_definitif'):
                    # Exception pour secretariatsct et admin qui peuvent forcer la réassignation
                    if role not in ['secretariatsct', 'admin']:
                        return jsonify({
                            "error": "Impossible d'assigner un projet ayant déjà un avis définitif ou une décision du Comité"
                        }), 403

            nouveau_evaluateur = data["evaluateur_nom"]

            # Archiver et supprimer la fiche d'évaluation existante lors d'une réassignation
            fiche_existante = FicheEvaluation.query.filter_by(project_id=project_id).first()
            if fiche_existante and fiche_existante.fichier_pdf:
                try:
                    print(f"[INFO] Archivage de la fiche pour le projet {project_id} (assignation/réassignation)")
                    # Déterminer la raison selon le contexte
                    if p.statut in ["soumis", "en attente d'assignation"]:
                        raison = "assignation_initiale"
                    else:
                        raison = "reassignation_avant_hierarchie"

                    archive = archiver_fiche(fiche_existante, raison, username)
                    if archive:
                        print(f"✅ PDF archivé avec succès pour le projet {project_id}")
                    else:
                        print(f"⚠️ Échec de l'archivage pour le projet {project_id}")
                except Exception as e:
                    print(f"❌ Erreur lors de l'archivage de la fiche: {e}")
                    import traceback
                    traceback.print_exc()

                # Supprimer la fiche de la base de données
                print(f"[INFO] Suppression de la fiche de la base de données pour le projet {project_id}")
                db.session.delete(fiche_existante)

            # Réinitialiser les champs d'évaluation lors de la réassignation
            p.avis = None
            p.commentaires = None

            # Réinitialiser l'évaluation préalable lors de la réassignation
            # pour permettre au nouvel évaluateur de faire une nouvelle évaluation
            p.evaluation_prealable = None
            p.evaluation_prealable_date = None
            p.evaluation_prealable_commentaire = None

            p.evaluateur_nom = nouveau_evaluateur
            p.statut = "assigné"

            # Récupérer la motivation facultative
            motivation = (data.get("motivation") or "").strip()
            if motivation:
                action = f"Projet assigné à {nouveau_evaluateur} - Motivation: {motivation}"
            else:
                action = f"Projet assigné à {nouveau_evaluateur}"

        # Réassignation explicite (via validation_secretariat: "reassigne")
        elif data.get("validation_secretariat") == "reassigne":
            # Vérifier que le projet peut être réassigné (sauf pour secretariatsct et admin)
            if role not in ['secretariatsct', 'admin']:
                peut, erreur = WorkflowValidator.peut_etre_assigne(p)
                if not peut:
                    return jsonify({"error": erreur}), 403

            nouveau_evaluateur = data["evaluateur_nom"]

            # Archiver et supprimer la fiche d'évaluation existante
            fiche_existante = FicheEvaluation.query.filter_by(project_id=project_id).first()
            if fiche_existante and fiche_existante.fichier_pdf:
                try:
                    print(f"[INFO] Archivage de la fiche pour le projet {project_id} (réassignation explicite)")
                    archive = archiver_fiche(fiche_existante, "reassignation_avant_hierarchie", username)
                    if archive:
                        print(f"✅ PDF archivé avec succès pour le projet {project_id}")
                    else:
                        print(f"⚠️ Échec de l'archivage pour le projet {project_id}")
                except Exception as e:
                    print(f"❌ Erreur lors de l'archivage de la fiche: {e}")
                    import traceback
                    traceback.print_exc()

                # Supprimer la fiche de la base de données
                print(f"[INFO] Suppression de la fiche de la base de données pour le projet {project_id}")
                db.session.delete(fiche_existante)

            # Réinitialiser les champs d'évaluation
            p.avis = None
            p.commentaires = None

            # Réinitialiser l'évaluation préalable pour permettre une nouvelle évaluation
            p.evaluation_prealable = None
            p.evaluation_prealable_date = None
            p.evaluation_prealable_commentaire = None

            p.evaluateur_nom = nouveau_evaluateur
            p.statut = "assigné"
            action = f"Projet réassigné à {nouveau_evaluateur}"

        # Avis (par évaluateur ou secrétariat)
        elif "avis" in data:
            avis = data.get("avis")
            commentaires = (data.get("commentaires") or "").strip()
            # commentaire obligatoire pour tout avis sauf 'favorable'
            if avis != "favorable" and not commentaires:
                return jsonify({"error": "Le commentaire est obligatoire pour cet avis"}), 400

            p.avis = avis
            p.commentaires = commentaires

            # si le secrétariat émet l'avis sans assignation préalable, on s'auto-assigne
            if role == "secretariatsct" and not p.evaluateur_nom:
                p.evaluateur_nom = "secretariatsct"

            if avis == "compléments demandés":
                # Demande de compléments transmise directement au soumissionnaire
                p.statut = "compléments demandés"
                p.complements_demande_message = commentaires
                action = "Compléments demandés au soumissionnaire"
                # on efface une éventuelle réponse précédente
                p.complements_reponse_message = None
                p.complements_reponse_pieces = None
            else:
                p.statut = "évalué"
                action = f"Avis émis: {avis}"

        # Actions spéciales sur les compléments
        elif "statut_action" in data and "validation_secretariat" not in data:
            statut_action = data.get("statut_action")
            if statut_action == "reevaluer_complements":
                # Archiver et supprimer la fiche d'évaluation existante pour une nouvelle évaluation
                fiche_existante = FicheEvaluation.query.filter_by(project_id=project_id).first()
                if fiche_existante and fiche_existante.fichier_pdf:
                    try:
                        print(f"[INFO] Archivage de la fiche pour le projet {project_id} (réévaluation après compléments)")
                        archive = archiver_fiche(fiche_existante, "reevaluation_apres_complements", username)
                        if archive:
                            print(f"✅ PDF archivé avec succès pour le projet {project_id}")
                        else:
                            print(f"⚠️ Échec de l'archivage pour le projet {project_id}")
                    except Exception as e:
                        print(f"❌ Erreur lors de l'archivage de la fiche: {e}")
                        import traceback
                        traceback.print_exc()

                    # Supprimer la fiche de la base de données
                    db.session.delete(fiche_existante)

                # Réinitialiser l'évaluation préalable
                p.evaluation_prealable = None
                p.evaluation_prealable_date = None
                p.evaluation_prealable_commentaire = None

                p.statut = "assigné"
                action = "Compléments fournis - réassigné pour réévaluation"
            elif statut_action == "validation_complements":
                p.statut = "évalué"
                p.avis = data.get("avis", "favorable")
                p.commentaires = data.get("commentaires", "Compléments validés")
                action = "Compléments validés directement par le secrétariat"
            elif statut_action == "reinitialiser_evaluation":
                # Réinitialiser complètement le projet pour une nouvelle évaluation
                p.statut = "assigné"
                p.avis = None
                p.commentaires = None
                p.complements_demande_message = None
                # Réinitialiser l'évaluation préalable
                p.evaluation_prealable = None
                p.evaluation_prealable_date = None
                p.evaluation_prealable_commentaire = None
                action = "Projet réinitialisé - réassigné pour réévaluation"
            elif statut_action == "reassigner_rejete":
                # Réassignation d'un projet avec avis rejeté avec préservation de l'historique
                if p.statut != "rejeté":
                    return jsonify({"error": "Seuls les projets avec avis rejetés peuvent être réassignés"}), 400

                to = data.get("evaluateur_nom")
                if not to:
                    return jsonify({"error": "evaluateur_nom requis pour la réassignation"}), 400

                # Archiver et supprimer la fiche d'évaluation existante lors d'une réassignation
                fiche_existante = FicheEvaluation.query.filter_by(project_id=project_id).first()
                if fiche_existante and fiche_existante.fichier_pdf:
                    try:
                        print(f"[INFO] Archivage de la fiche pour le projet {project_id} (réassignation après rejet)")
                        # Déterminer la raison selon qui a rejeté
                        if p.avis_presidencesct == "rejeté":
                            raison = "reassignation_apres_rejet_presidencesct"
                        elif p.decision_finale == "infirme":
                            raison = "reassignation_apres_rejet_comite"
                        else:
                            raison = "reassignation_apres_rejet"

                        archive = archiver_fiche(fiche_existante, raison, username)
                        if archive:
                            print(f"✅ PDF archivé avec succès pour le projet {project_id}")
                        else:
                            print(f"⚠️ Échec de l'archivage pour le projet {project_id}")
                    except Exception as e:
                        print(f"❌ Erreur lors de l'archivage de la fiche: {e}")
                        import traceback
                        traceback.print_exc()

                    # Supprimer la fiche de la base de données (même si l'archivage a échoué)
                    db.session.delete(fiche_existante)

                # Réinitialiser pour permettre une nouvelle évaluation
                p.evaluateur_nom = to
                p.statut = "assigné"
                p.avis = None
                p.commentaires = None

                # Réinitialiser les avis des présidences (SCT et Comité)
                p.avis_presidencesct = None
                p.decision_finale = None
                p.commentaires_finaux = None
                set_statut_comite(p, None)  # Réinitialiser le statut_comite

                # Réinitialiser l'évaluation préalable
                p.evaluation_prealable = None
                p.evaluation_prealable_date = None
                p.evaluation_prealable_commentaire = None

                # Récupérer la motivation facultative
                motivation = (data.get("motivation") or "").strip()
                if motivation:
                    action = f"Avis rejeté réassigné à {to} pour nouvelle évaluation - Motivation: {motivation}"
                else:
                    action = f"Avis rejeté réassigné à {to} pour nouvelle évaluation"

        # Validation secrétariat
        elif "validation_secretariat" in data:
            v = data.get("validation_secretariat")

            # Vérifier que le projet peut être validé
            peut, erreur = WorkflowValidator.peut_etre_valide_par_secretariat(p)
            if not peut:
                return jsonify({"error": erreur}), 403

            if v == "valide":
                p.validation_secretariat = "valide"
                p.statut = "en attente validation presidencesct"
                # Retirer l'assignation de l'évaluateur pour que le projet sorte de son panier
                p.evaluateur_nom = None

                # Synchroniser l'avis du projet avec la fiche d'évaluation (si elle existe)
                fiche_eval = FicheEvaluation.query.filter_by(project_id=project_id).first()
                if fiche_eval and fiche_eval.proposition:
                    p.avis = fiche_eval.proposition

                # Vérifier si c'est une resoumission après rejet (par Présidence SCT ou Comité)
                if data.get("statut_action") == "resoumission_apres_rejet":
                    # Enregistrer la motivation de resoumission si fournie (compatible avec anciennes BDD)
                    motivation = data.get("motivation_resoumission")
                    if motivation and hasattr(p, 'motivation_resoumission'):
                        try:
                            p.motivation_resoumission = motivation
                        except Exception:
                            pass  # Ignorer silencieusement si la colonne n'existe pas

                    # Récupérer les données de la fiche d'évaluation pour le log
                    fiche = FicheEvaluation.query.filter_by(project_id=project_id).first()
                    if fiche:
                        action = (f"Projet soumis à la Présidence SCT malgré le rejet - "
                                f"Score: {fiche.score_total}/100, "
                                f"Avis: {fiche.proposition or 'N/A'}, "
                                f"Évaluateur: {fiche.evaluateur_nom or 'N/A'}")
                        if motivation:
                            action += f" - Motivation: {motivation[:100]}..." if len(motivation) > 100 else f" - Motivation: {motivation}"
                    else:
                        action = "Projet soumis à la Présidence SCT malgré le rejet"
                        if motivation:
                            action += f" - Motivation: {motivation[:100]}..." if len(motivation) > 100 else f" - Motivation: {motivation}"
                else:
                    action = "Avis validé par le Secrétariat SCT"
            elif v == "reassigne":
                to = data.get("evaluateur_nom")
                if not to:
                    return jsonify({"error": "evaluateur_nom requis pour la réassignation"}), 400

                # Archiver et supprimer la fiche d'évaluation existante lors d'une réassignation
                fiche_existante = FicheEvaluation.query.filter_by(project_id=project_id).first()
                if fiche_existante and fiche_existante.fichier_pdf:
                    try:
                        print(f"[INFO] Archivage de la fiche pour le projet {project_id} (réassignation par SecretariatSCT)")
                        archive = archiver_fiche(fiche_existante, "reassignation_par_secretariat", username)
                        if archive:
                            print(f"✅ PDF archivé avec succès pour le projet {project_id}")
                        else:
                            print(f"⚠️ Échec de l'archivage pour le projet {project_id}")
                    except Exception as e:
                        print(f"❌ Erreur lors de l'archivage de la fiche: {e}")
                        import traceback
                        traceback.print_exc()

                    # Supprimer la fiche de la base de données
                    db.session.delete(fiche_existante)

                p.validation_secretariat = "reassigne"
                p.evaluateur_nom = to
                p.avis = None
                p.commentaires = None

                # Réinitialiser les avis des présidences (SCT et Comité)
                p.avis_presidencesct = None
                p.decision_finale = None
                p.commentaires_finaux = None
                set_statut_comite(p, None)  # Réinitialiser le statut_comite

                p.statut = "assigné"
                action = f"Avis rejeté par le Secrétariat — réassigné à {to}"
            else:
                return jsonify({"error": "validation_secretariat invalide"}), 400

        # Validation Présidence SCT
        elif "avis_presidencesct" in data:
            # Vérifier que la Présidence SCT peut valider
            peut, erreur = WorkflowValidator.peut_etre_valide_par_presidence_sct(p)
            if not peut:
                return jsonify({"error": erreur}), 403

            p.avis_presidencesct = data["avis_presidencesct"]
            if data["avis_presidencesct"] == "valide":
                p.statut = "validé par presidencesct"
                # NE PAS mettre de statut_comite ici - c'est le rôle de PresidenceComite
                action = "Validation par Présidence SCT - transmission à Présidence du Comité"

                # Ajouter la fiche d'évaluation PDF à la documenthèque
                try:
                    import shutil
                    fiche = FicheEvaluation.query.filter_by(project_id=project_id).first()
                    if fiche and fiche.fichier_pdf:
                        # Chemin source du PDF (dans routes/pdfs/fiches_evaluation/)
                        pdf_source_dir = os.path.join(os.path.dirname(__file__), 'routes', 'pdfs', 'fiches_evaluation')
                        pdf_source_path = os.path.join(pdf_source_dir, fiche.fichier_pdf)

                        if os.path.exists(pdf_source_path):
                            # Chemin destination dans uploads
                            pdf_dest_name = f"FICHE_EVAL_{fiche.reference_fiche}.pdf"
                            pdf_dest_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_dest_name)

                            # Copier le PDF vers uploads
                            shutil.copy2(pdf_source_path, pdf_dest_path)

                            # Vérifier si une entrée DocumentProjet existe déjà pour cette fiche
                            existing_doc = DocumentProjet.query.filter_by(
                                project_id=project_id,
                                type_document='fiche_evaluation'
                            ).first()

                            if not existing_doc:
                                # Créer une entrée DocumentProjet
                                taille_fichier = os.path.getsize(pdf_dest_path)
                                doc = DocumentProjet(
                                    project_id=project_id,
                                    nom_fichier=pdf_dest_name,
                                    nom_original=f"Fiche_Evaluation_{fiche.reference_fiche}.pdf",
                                    description="Fiche d'évaluation du projet (validée par Présidence SCT)",
                                    type_document='fiche_evaluation',
                                    auteur_nom='presidencesct',
                                    auteur_role='presidencesct',
                                    date_ajout=datetime.utcnow(),
                                    taille_fichier=taille_fichier
                                )
                                db.session.add(doc)
                                print(f"[INFO] Fiche d'évaluation PDF ajoutée à la documenthèque du projet {project_id}")
                except Exception as e:
                    print(f"[ERREUR] Impossible d'ajouter la fiche PDF à la documenthèque: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    # On ne bloque pas la validation même si l'ajout échoue

            else:
                # Rejet par Présidence SCT
                p.statut = "rejeté"
                p.evaluateur_nom = None

                # Réinitialiser les décisions de présidence pour permettre un nouveau cycle
                p.decision_finale = None
                p.commentaires_finaux = None
                set_statut_comite(p, None)  # Réinitialiser aussi le statut_comite

                action = "Avis rejeté par Présidence SCT"

        # Validation Présidence du Comité
        elif "decision_finale" in data:
            dec = data.get("decision_finale")

            # Vérifier que la Présidence du Comité peut décider
            peut, erreur = WorkflowValidator.peut_etre_decide_par_presidence_comite(p)
            if not peut:
                return jsonify({"error": erreur}), 403

            # PHASE 2: PresidenceComite confirme ou infirme l'avis
            if dec == "confirme":
                # PresidenceComite confirme l'avis de l'évaluateur
                p.decision_finale = dec

                # Cas B1: Avis défavorable confirmé → FIN DE VIE du projet
                if p.avis == "défavorable":
                    p.statut = "avis défavorable confirmé"
                    set_statut_comite(p, None)  # Pas de recommandation au Comité
                    # Rendre la fiche d'évaluation visible pour le soumissionnaire
                    p.fiche_evaluation_visible = True
                    action = "Décision de la Présidence du Comité : avis défavorable confirmé (fin de vie du projet)"

                # Cas B2: Avis favorable/favorable sous conditions → Recommandation AUTOMATIQUE au Comité
                elif p.avis in ["favorable", "favorable sous conditions"]:
                    p.statut = "validé par presidencecomite"
                    set_statut_comite(p, 'recommande_comite')  # Recommandation automatique
                    action = "Décision de la Présidence du Comité : avis confirmé - Recommandé au Comité"

                else:
                    # Cas de sécurité si l'avis n'est pas défini
                    p.statut = "validé par presidencecomite"
                    action = "Décision de la Présidence du Comité : avis confirmé"

                if data.get("commentaires"):
                    p.commentaires_finaux = data.get("commentaires")

            elif dec == "infirme":
                # Option A: PresidenceComite infirme l'avis → retour au Secrétariat SCT
                p.decision_finale = dec
                p.statut = "en réexamen par le Secrétariat SCT"
                p.evaluateur_nom = None
                # Réinitialiser la validation SCT pour forcer un nouveau cycle
                p.avis_presidencesct = None
                action = "Décision de la Présidence du Comité : avis infirmé, retour au Secrétariat SCT"
                if data.get("commentaires"):
                    p.commentaires_finaux = data.get("commentaires")
            else:
                return jsonify({"error": "decision_finale invalide"}), 400

        db.session.commit()
        if action:
            hist = Historique(project_id=project_id, action=action, auteur=auteur, role=role)
            db.session.add(hist)
            db.session.commit()

        # ============ NOTIFICATIONS ============
        try:
            projet_titre = p.titre[:50] + "..." if len(p.titre) > 50 else p.titre
            lien_projet = f"/project/{project_id}"

            # Notification pour assignation d'évaluateur
            if "evaluateur_nom" in data and p.evaluateur_nom:
                notify_user_by_username(
                    p.evaluateur_nom,
                    "assignation",
                    "Nouveau projet assigné",
                    f"Le projet '{projet_titre}' vous a été assigné pour évaluation.",
                    project_id,
                    lien_projet
                )

            # Notification pour compléments demandés au soumissionnaire
            if p.statut == "compléments demandés":
                notify_project_owner(
                    p,
                    "complement_requis",
                    "Compléments demandés",
                    f"Des compléments ont été demandés pour votre projet '{projet_titre}'.",
                    lien_projet,
                    priorite_email=True
                )

            # Notification pour avis émis (vers secrétariat)
            if p.statut == "évalué":
                notify_users_by_role(
                    "secretariatsct",
                    "avis_rendu",
                    "Avis en attente de validation",
                    f"Le projet '{projet_titre}' a reçu un avis et attend votre validation.",
                    project_id,
                    lien_projet
                )

            # Notification pour validation présidence SCT
            if p.statut == "en attente validation presidencesct":
                notify_users_by_role(
                    "presidencesct",
                    "statut_change",
                    "Projet à valider",
                    f"Le projet '{projet_titre}' attend votre validation.",
                    project_id,
                    lien_projet
                )

            # Notification pour validation par présidence SCT (vers comité)
            if p.statut == "validé par presidencesct":
                notify_users_by_role(
                    "presidencecomite",
                    "statut_change",
                    "Projet à examiner",
                    f"Le projet '{projet_titre}' a été validé par la Présidence SCT et attend votre décision.",
                    project_id,
                    lien_projet
                )

            # Notification pour décision finale au soumissionnaire
            if p.statut == "décision finale confirmée":
                decision_text = "approuvé" if p.decision_finale == "confirme" else "non retenu"
                notify_project_owner(
                    p,
                    "statut_change",
                    "Décision finale rendue",
                    f"Votre projet '{projet_titre}' a été {decision_text} par le Comité.",
                    lien_projet,
                    priorite_email=True
                )

            # Notification pour rejet
            if p.statut == "rejeté" and "avis_presidencesct" in data:
                notify_project_owner(
                    p,
                    "statut_change",
                    "Projet non retenu",
                    f"Votre projet '{projet_titre}' n'a pas été retenu par la Présidence SCT.",
                    lien_projet,
                    priorite_email=True
                )

            db.session.commit()
        except Exception as notif_error:
            print(f"[NOTIFICATION] Erreur lors de la création des notifications: {notif_error}")
            # Ne pas bloquer le traitement principal si les notifications échouent

        print(f"[TRAITER_DEBUG] Fin du traitement - Action effectuée: {action}")
        print(f"[TRAITER_DEBUG] Statut final du projet: {p.statut}")

        # ============ ENVOI D'EMAILS ============
        # Envoyer des emails au soumissionnaire selon le changement de statut
        try:
            print(f"[EMAIL_DEBUG] Tentative d'envoi d'email - Projet: {project_id}, Statut: {p.statut}, Auteur: {p.auteur_nom}")

            # Email au soumissionnaire pour tous les changements de statut
            if p.auteur_nom:
                soumissionnaire = User.query.filter_by(username=p.auteur_nom).first()
                print(f"[EMAIL_DEBUG] Soumissionnaire trouvé: {soumissionnaire.username if soumissionnaire else 'None'}, Email: {soumissionnaire.email if soumissionnaire else 'None'}")
                if soumissionnaire and soumissionnaire.email:
                    # Déterminer si on doit envoyer un email selon le statut
                    statuts_avec_email = ["assigné", "en évaluation", "compléments demandés", "évalué",
                                         "favorable", "favorable sous conditions", "défavorable"]

                    if p.statut in statuts_avec_email:
                        print(f"[EMAIL_DEBUG] Envoi d'email au soumissionnaire {soumissionnaire.email} pour le statut '{p.statut}'")
                        email_service.send_status_change_email(
                            project=p,
                            user_email=soumissionnaire.email,
                            user_name=soumissionnaire.nom_complet or soumissionnaire.display_name or soumissionnaire.username
                        )
                    else:
                        print(f"[EMAIL_DEBUG] Statut '{p.statut}' non dans la liste des statuts avec email")
                else:
                    print(f"[EMAIL_DEBUG] Pas d'envoi d'email au soumissionnaire - Email manquant")
            else:
                print(f"[EMAIL_DEBUG] Pas d'envoi d'email au soumissionnaire - Pas d'auteur_nom sur le projet")

            # Email à l'évaluateur lors de l'assignation
            if p.statut == "assigné" and p.evaluateur_nom:
                evaluateur = User.query.filter_by(username=p.evaluateur_nom).first()
                print(f"[EMAIL_DEBUG] Évaluateur trouvé: {evaluateur.username if evaluateur else 'None'}, Email: {evaluateur.email if evaluateur else 'None'}")
                if evaluateur and evaluateur.email:
                    print(f"[EMAIL_DEBUG] Envoi d'email à l'évaluateur {evaluateur.email}")
                    email_service.send_evaluator_assignment_email(
                        project=p,
                        evaluator_email=evaluateur.email,
                        evaluator_name=evaluateur.nom_complet or evaluateur.display_name or evaluateur.username
                    )
                else:
                    print(f"[EMAIL_DEBUG] Pas d'envoi d'email à l'évaluateur - Email manquant")

        except Exception as email_error:
            print(f"[EMAIL] Erreur lors de l'envoi d'email: {email_error}")
            import traceback
            traceback.print_exc()
            # Ne pas bloquer le traitement principal si l'email échoue

        return jsonify({"message": "Traitement effectué"}), 200

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Évaluation préalable (par l'évaluateur)
@app.route("/api/projects/<int:project_id>/evaluation-prealable", methods=["POST"])
def evaluation_prealable(project_id):
    try:
        data = request.json or {}
        p = Project.query.get_or_404(project_id)

        # Vérifier que le projet peut être évalué
        peut, erreur = WorkflowValidator.peut_etre_evalue(p, include_prealable=True)
        if not peut:
            return jsonify({"error": erreur}), 403

        auteur = data.get("auteur", "")
        role = data.get("role", "")

        decision = data.get("decision")  # "dossier_evaluable", "complements_requis", ou "dossier_rejete"
        # Le frontend envoie "commentaire" (sans s) - accepter les deux formats
        commentaires = data.get("commentaire", data.get("commentaires", "")).strip()
        # Récupérer la matrice d'évaluation (JSON stringifié)
        matrice = data.get("matrice")


        if not decision or decision not in ["dossier_evaluable", "complements_requis", "dossier_rejete"]:
            return jsonify({"error": "Décision invalide"}), 400

        # Sauvegarder l'état précédent de evaluation_prealable AVANT de le modifier
        previous_evaluation_prealable = p.evaluation_prealable

        # Enregistrer l'évaluation préalable
        p.evaluation_prealable = decision
        p.evaluation_prealable_date = datetime.utcnow()
        p.evaluation_prealable_commentaire = commentaires
        # Enregistrer la matrice d'évaluation si fournie
        if matrice:
            p.evaluation_prealable_matrice = matrice

        # Changer le statut en fonction de la décision
        action = ""
        if decision == "dossier_evaluable":
            p.statut = "en évaluation"
            if commentaires:
                action = f"Évaluation préalable: dossier évaluable - {commentaires}"
            else:
                action = "Évaluation préalable: dossier évaluable - passage à l'évaluation détaillée"
        elif decision == "complements_requis":
            p.statut = "compléments demandés"
            p.complements_demande_message = commentaires
            # Réinitialiser les réponses de compléments
            p.complements_reponse_message = None
            p.complements_reponse_pieces = None
            action = f"Évaluation préalable: compléments requis - {commentaires}"
        elif decision == "dossier_rejete":
            # Dossier rejeté lors de l'évaluation préalable
            # Si c'est le secretariatsct qui valide (et que evaluation_prealable ÉTAIT déjà 'dossier_rejete'), on rejette définitivement
            # Sinon, c'est une proposition de rejet par l'évaluateur
            if role == "secretariatsct" and previous_evaluation_prealable == "dossier_rejete":
                # Validation du rejet par le Secrétariat SCT
                # Conserver le commentaire original de l'évaluateur (déjà dans evaluation_prealable_commentaire)
                p.statut = "rejeté"
                p.avis = "dossier rejeté"
                # Conserver le commentaire de l'évaluateur qui est dans evaluation_prealable_commentaire
                p.commentaires = p.evaluation_prealable_commentaire or commentaires
                action = f"Rejet validé par le Secrétariat SCT"
            else:
                # Proposition de rejet par l'évaluateur - attend validation du secrétariat
                # Le statut ne change PAS, le soumissionnaire n'est PAS encore informé
                p.avis = None
                p.commentaires = commentaires
                p.evaluation_prealable_commentaire = commentaires  # Sauvegarder aussi dans ce champ pour la validation ultérieure
                action = f"Évaluation préalable: rejet proposé par l'évaluateur - {commentaires}"

        db.session.commit()

        # Enregistrer dans l'historique
        if action:
            hist = Historique(project_id=project_id, action=action, auteur=auteur, role=role)
            db.session.add(hist)
            db.session.commit()

        return jsonify({"message": "Évaluation préalable enregistrée"}), 200

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Routes pour la fiche d'évaluation détaillée

# GET - Récupérer une fiche d'évaluation
# NOTE: Les routes GET/POST/PUT pour /api/projects/<id>/fiche-evaluation
# sont maintenant dans routes/project_routes.py pour éviter les conflits.
# La route PDF a également été déplacée dans project_routes.py

def soumettre_fiche_evaluation_legacy(project_id):
    """
    Route pour soumettre la fiche d'évaluation détaillée avec génération du PDF
    """
    try:
        print(f"[FICHE_EVAL] Réception de la fiche d'évaluation pour le projet {project_id}")
        data = request.json or {}
        p = Project.query.get_or_404(project_id)

        # Récupérer les informations de l'évaluateur
        evaluateur_nom = data.get('evaluateur_nom', p.evaluateur_nom or 'inconnu')

        # Vérifier si une fiche existe déjà
        fiche = FicheEvaluation.query.filter_by(project_id=project_id).first()

        if not fiche:
            # Créer une nouvelle fiche
            print(f"[FICHE_EVAL] Création d'une nouvelle fiche pour le projet {project_id}")
            fiche = FicheEvaluation(
                project_id=project_id,
                evaluateur_nom=evaluateur_nom,
                reference_fiche=f"DGPPE-FE-{p.numero_projet or project_id}"
            )
            db.session.add(fiche)
        else:
            print(f"[FICHE_EVAL] Mise à jour de la fiche existante {fiche.id}")

        # Mise à jour de la fiche avec les données reçues
        fiche.date_evaluation = datetime.utcnow()

        # Section I - Présentation du projet (données éditables)
        if 'intitule' in data:
            fiche.intitule_projet = data['intitule']
            p.intitule = data['intitule']  # Mettre à jour aussi dans Project
        if 'cout_estimatif' in data:
            fiche.cout_projet = data['cout_estimatif']
            p.cout_estimatif = data['cout_estimatif']
        if 'origine_projet_choix' in data:
            fiche.origine_projet = data['origine_projet_choix']

        # Dimensions transversales
        fiche.cc_adaptation = data.get('changement_climatique_adaptation', False)
        fiche.cc_attenuation = data.get('changement_climatique_attenuation', False)
        fiche.genre = data.get('genre', False)

        # Tableaux de présentation détaillée
        fiche.articulation = data.get('articulation', '')
        fiche.axes = data.get('axes', '')
        fiche.objectifs_strategiques = data.get('objectifs_strategiques', '')
        fiche.odd = data.get('odd', '')
        fiche.duree_analyse = data.get('duree_analyse', '')
        fiche.realisation = data.get('realisation', '')
        fiche.exploitation = data.get('exploitation', '')
        fiche.localisation = data.get('localisation', '')
        fiche.parties_prenantes = data.get('parties_prenantes', '')
        fiche.autres_projets_connexes = data.get('autres_projets_connexes', '')
        fiche.objectif_projet = data.get('objectif_projet', '')
        fiche.activites_principales = data.get('activites_principales', '')
        fiche.resultats_attendus = data.get('resultats_attendus', '')

        # Autres champs éditables de Section I
        if 'secteur' in data:
            p.secteur = data['secteur']
        if 'poles' in data:
            p.poles_territoriaux = data['poles']
        if 'organisme_tutelle' in data:
            fiche.organisme_tutelle = data['organisme_tutelle']
        if 'description' in data:
            p.description = data['description']

        # Section III - Critères d'évaluation
        criteres = data.get('criteres', {})

        # Mapper les critères vers les champs de la base de données
        if 'pertinence' in criteres:
            fiche.pertinence_score = criteres['pertinence'].get('score', 0)
            fiche.pertinence_description = criteres['pertinence'].get('description', '')
            fiche.pertinence_recommandations = criteres['pertinence'].get('recommandations', '')

        if 'alignement' in criteres:
            fiche.alignement_score = criteres['alignement'].get('score', 0)
            fiche.alignement_description = criteres['alignement'].get('description', '')
            fiche.alignement_recommandations = criteres['alignement'].get('recommandations', '')

        if 'activites_couts' in criteres:
            fiche.activites_couts_score = criteres['activites_couts'].get('score', 0)
            fiche.activites_couts_description = criteres['activites_couts'].get('description', '')
            fiche.activites_couts_recommandations = criteres['activites_couts'].get('recommandations', '')

        if 'equite' in criteres:
            fiche.equite_score = criteres['equite'].get('score', 0)
            fiche.equite_description = criteres['equite'].get('description', '')
            fiche.equite_recommandations = criteres['equite'].get('recommandations', '')

        if 'viabilite' in criteres:
            fiche.viabilite_score = criteres['viabilite'].get('score', 0)
            fiche.viabilite_description = criteres['viabilite'].get('description', '')
            fiche.viabilite_recommandations = criteres['viabilite'].get('recommandations', '')

        if 'rentabilite' in criteres:
            fiche.rentabilite_score = criteres['rentabilite'].get('score', 0)
            fiche.rentabilite_description = criteres['rentabilite'].get('description', '')
            fiche.rentabilite_recommandations = criteres['rentabilite'].get('recommandations', '')

        if 'benefices_strategiques' in criteres:
            fiche.benefices_strategiques_score = criteres['benefices_strategiques'].get('score', 0)
            fiche.benefices_strategiques_description = criteres['benefices_strategiques'].get('description', '')
            fiche.benefices_strategiques_recommandations = criteres['benefices_strategiques'].get('recommandations', '')

        if 'perennite' in criteres:
            fiche.perennite_score = criteres['perennite'].get('score', 0)
            fiche.perennite_description = criteres['perennite'].get('description', '')
            fiche.perennite_recommandations = criteres['perennite'].get('recommandations', '')

        if 'avantages_intangibles' in criteres:
            fiche.avantages_intangibles_score = criteres['avantages_intangibles'].get('score', 0)
            fiche.avantages_intangibles_description = criteres['avantages_intangibles'].get('description', '')
            fiche.avantages_intangibles_recommandations = criteres['avantages_intangibles'].get('recommandations', '')

        if 'faisabilite' in criteres:
            fiche.faisabilite_score = criteres['faisabilite'].get('score', 0)
            fiche.faisabilite_description = criteres['faisabilite'].get('description', '')
            fiche.faisabilite_recommandations = criteres['faisabilite'].get('recommandations', '')

        if 'ppp' in criteres:
            fiche.ppp_score = criteres['ppp'].get('score', 0)
            fiche.ppp_description = criteres['ppp'].get('description', '')
            fiche.ppp_recommandations = criteres['ppp'].get('recommandations', '')

        if 'impact_environnemental' in criteres:
            fiche.impact_environnemental_score = criteres['impact_environnemental'].get('score', 0)
            fiche.impact_environnemental_description = criteres['impact_environnemental'].get('description', '')
            fiche.impact_environnemental_recommandations = criteres['impact_environnemental'].get('recommandations', '')

        # Calculer le score total
        score_total = (
            (fiche.pertinence_score or 0) +
            (fiche.alignement_score or 0) +
            (fiche.activites_couts_score or 0) +
            (fiche.equite_score or 0) +
            (fiche.viabilite_score or 0) +
            (fiche.rentabilite_score or 0) +
            (fiche.benefices_strategiques_score or 0) +
            (fiche.perennite_score or 0) +
            (fiche.avantages_intangibles_score or 0) +
            (fiche.faisabilite_score or 0) +
            (fiche.ppp_score or 0) +
            (fiche.impact_environnemental_score or 0)
        )
        fiche.score_total = score_total
        p.score = score_total

        # Proposition et recommandations finales
        fiche.proposition = data.get('proposition', data.get('avis', ''))
        fiche.recommandations = data.get('recommandations', '')

        # Mettre à jour le projet
        p.avis = fiche.proposition
        p.commentaires = fiche.recommandations
        p.statut = "évalué"

        # Sauvegarder la fiche dans la base de données
        db.session.commit()
        print(f"[FICHE_EVAL] Fiche {fiche.id} sauvegardée avec score {score_total}/100")

        # Générer le PDF
        try:
            import tempfile
            import shutil

            temp_dir = tempfile.mkdtemp()

            try:
                fiche_data = fiche.to_dict()
                project_data = p.to_dict()

                # Générer le PDF
                pdf_path = generer_fiche_evaluation_dgppe_pdf(fiche_data, project_data, temp_dir)
                print(f"[FICHE_EVAL] PDF généré: {pdf_path}")

                # Créer le dossier pour les fiches d'évaluation
                fiches_folder = os.path.join(app.config["UPLOAD_FOLDER"], "fiches_evaluation")
                os.makedirs(fiches_folder, exist_ok=True)

                # Nom du fichier final
                pdf_filename = f"Fiche_Evaluation_{p.numero_projet or project_id}_{evaluateur_nom}.pdf"
                dest_path = os.path.join(fiches_folder, pdf_filename)

                # Copier le PDF vers le dossier final
                shutil.copy2(pdf_path, dest_path)

                # Enregistrer le chemin du PDF dans la fiche
                fiche.fichier_pdf = pdf_filename
                db.session.commit()

                print(f"[FICHE_EVAL] PDF sauvegardé: {pdf_filename}")

            finally:
                # Nettoyer le répertoire temporaire
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass

        except Exception as pdf_error:
            print(f"[FICHE_EVAL] Erreur lors de la génération du PDF: {pdf_error}")
            import traceback
            traceback.print_exc()
            # Ne pas bloquer la soumission si le PDF échoue

        # Ajouter une entrée dans l'historique
        hist = Historique(
            project_id=project_id,
            action=f"Fiche d'évaluation soumise - Score: {score_total}/100 - Avis: {fiche.proposition}",
            auteur=evaluateur_nom,
            role='evaluateur'
        )
        db.session.add(hist)
        db.session.commit()

        print(f"[FICHE_EVAL] Fiche d'évaluation complétée avec succès pour le projet {project_id}")

        return jsonify({
            "message": "Fiche d'évaluation enregistrée avec succès",
            "fiche_id": fiche.id,
            "score_total": score_total,
            "pdf_generated": fiche.fichier_pdf is not None
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"[FICHE_EVAL] Erreur: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Soumission des compléments par le soumissionnaire
@app.route("/api/projects/<int:project_id>/complements", methods=["POST"])
def submit_complements(project_id):
    try:
        p = Project.query.get_or_404(project_id)

        # Vérifier que le projet peut recevoir des compléments
        peut, erreur = WorkflowValidator.peut_recevoir_complements(p)
        if not peut:
            return jsonify({"error": erreur}), 403

        message = (request.form.get("message") or "").strip()
        files = request.files.getlist("files")
        
        # Validation : au moins un message ou un fichier
        if not message and not files:
            return jsonify({"error": "Veuillez fournir au moins un message ou un fichier en complément"}), 400

        filenames = _save_files(files)
        
        # Accumulation des messages (pas de remplacement)
        if message:
            if p.complements_reponse_message:
                p.complements_reponse_message += f"\n\n--- Complément {datetime.now().strftime('%d/%m/%Y %H:%M')} ---\n{message}"
            else:
                p.complements_reponse_message = message
        
        # Accumulation des fichiers (pas de remplacement)
        if filenames:
            existing_files = p.complements_reponse_pieces.split(",") if p.complements_reponse_pieces else []
            all_files = existing_files + filenames
            p.complements_reponse_pieces = ",".join(all_files)

        # Le statut reste "compléments fournis" pour que tous les acteurs
        # (soumissionnaire, secrétariat, présidences, évaluateur) voient qu'il y a
        # des compléments qui ont été fournis et attendent traitement
        p.statut = "compléments fournis"
        if p.evaluateur_nom:
            action = f"Compléments fournis - en attente de traitement par {p.evaluateur_nom}"
        else:
            action = "Compléments fournis - en attente d'assignation"

        db.session.commit()

        hist = Historique(
            project_id=p.id,
            action=action,
            auteur=p.auteur_nom,
            role="soumissionnaire"
        )
        db.session.add(hist)
        db.session.commit()

        return jsonify({"message": "Compléments envoyés"}), 200
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Enregistrement de la décision du Comité (par le Secrétariat SCT)
@app.route("/api/projects/<int:project_id>/decision-comite", methods=["POST"])
def enregistrer_decision_comite(project_id):
    """
    PHASE 3: Endpoint pour enregistrer la décision du Comité.
    Le Secrétariat SCT OU la Présidence Comité enregistre si le Comité a entériné ou contesté.

    Paramètres attendus:
    - decision: 'enterine' ou 'conteste'
    - commentaires: OBLIGATOIRE si decision='conteste', optionnel sinon
    - auteur: username de l'utilisateur qui enregistre la décision
    - role: rôle de l'utilisateur (doit être secretariatsct, presidencecomite ou admin)
    """
    try:
        data = request.json or {}
        p = Project.query.get_or_404(project_id)

        auteur = data.get("auteur", "")
        role = data.get("role", "")
        decision = data.get("decision", "")  # 'enterine' ou 'conteste'
        commentaires = data.get("commentaires", "").strip()

        # Vérifier les permissions (SecretariatSCT OU PresidenceComite)
        if role not in ['secretariatsct', 'presidencecomite', 'admin']:
            return jsonify({"error": "Seuls le Secrétariat SCT et la Présidence Comité peuvent enregistrer les décisions du Comité"}), 403

        # Vérifier que le projet est bien recommandé au Comité
        # Accepter soit les projets avec statut_comite='recommande_comite'
        # soit les anciens projets validés par la Présidence Comité (avant l'implémentation de statut_comite)
        statut_comite_actuel = get_statut_comite(p)

        # Bloquer si déjà entériné
        if statut_comite_actuel == 'approuve_definitif':
            return jsonify({
                "error": "Ce projet a déjà été entériné par le Comité. Aucune modification n'est possible."
            }), 403

        # Vérifier que le Comité peut décider
        peut, erreur = WorkflowValidator.peut_recevoir_decision_comite(p)
        if not peut:
            return jsonify({"error": erreur}), 403

        if statut_comite_actuel != 'recommande_comite':
            # Permettre aussi les anciens projets "validé par presidencecomite" sans statut_comite
            if p.statut != 'validé par presidencecomite' or p.decision_finale:
                return jsonify({"error": "Ce projet n'est pas en attente de décision du Comité"}), 400
            # Pour les anciens projets, initialiser le statut_comite
            set_statut_comite(p, 'recommande_comite')

        # Vérifier la décision
        if decision not in ['enterine', 'conteste']:
            return jsonify({"error": "Décision invalide. Valeurs acceptées: 'enterine' ou 'conteste'"}), 400

        # IMPORTANT: Commentaires OBLIGATOIRES si le Comité conteste
        if decision == 'conteste' and not commentaires:
            return jsonify({"error": "Les commentaires sont obligatoires lorsque le Comité conteste la recommandation"}), 400

        # Mettre à jour le statut_comite
        if decision == 'enterine':
            set_statut_comite(p, 'approuve_definitif')
            # Rendre la fiche d'évaluation visible pour le soumissionnaire
            p.fiche_evaluation_visible = True
            # Garder l'avis de l'évaluateur comme statut final
            # L'avis peut être: favorable, favorable sous conditions, ou défavorable
            if p.avis:
                p.statut = p.avis
            else:
                # Fallback si pas d'avis (ne devrait pas arriver)
                p.statut = "validé par presidencecomite"
            action = f"Décision du Comité: projet entériné - Avis final confirmé: {p.avis}"
            if commentaires:
                action += f" - {commentaires}"
        else:  # conteste
            set_statut_comite(p, 'en_reevaluation')
            p.statut = "en réexamen par le Secrétariat SCT"
            # Réinitialiser les validations pour permettre un nouveau cycle
            p.avis_presidencesct = None
            p.decision_finale = None  # Réinitialiser aussi la décision de PresidenceComite
            p.evaluateur_nom = None
            action = f"Décision du Comité: projet contesté, retour au Secrétariat SCT - Motivation: {commentaires}"

        # Sauvegarder les commentaires si fournis
        if commentaires:
            if p.commentaires_finaux:
                p.commentaires_finaux += f"\n\n--- Décision Comité ({datetime.utcnow().strftime('%d/%m/%Y')}) ---\n{commentaires}"
            else:
                p.commentaires_finaux = commentaires

        db.session.commit()

        # Ajouter l'entrée dans l'historique
        hist = Historique(
            project_id=project_id,
            action=action,
            auteur=auteur,
            role=role
        )
        db.session.add(hist)
        db.session.commit()

        # Ajouter un log pour la traçabilité
        log_entry = Log(
            projet_id=project_id,
            action="decision_comite",
            details=action,
            auteur=auteur,
            role=role
        )
        db.session.add(log_entry)
        db.session.commit()

        # Notification au soumissionnaire
        try:
            projet_titre = p.titre[:50] + "..." if len(p.titre) > 50 else p.titre
            lien_projet = f"/project/{project_id}"

            if decision == 'enterine':
                notify_project_owner(
                    p,
                    "statut_change",
                    "Décision du Comité",
                    f"Votre projet '{projet_titre}' a été approuvé définitivement par le Comité.",
                    lien_projet,
                    priorite_email=True
                )
            else:
                notify_project_owner(
                    p,
                    "statut_change",
                    "Décision du Comité - Réévaluation demandée",
                    f"Le Comité a demandé une réévaluation de votre projet '{projet_titre}'.",
                    lien_projet,
                    priorite_email=True
                )
        except Exception as notif_error:
            print(f"[NOTIFICATION] Erreur lors de la création de la notification: {notif_error}")

        # ============ ENVOI D'EMAILS ============
        # Envoyer un email au soumissionnaire si le Comité a entériné le projet
        try:
            if decision == 'enterine' and p.auteur_nom:
                soumissionnaire = User.query.filter_by(username=p.auteur_nom).first()
                if soumissionnaire and soumissionnaire.email:
                    # Statut final du projet après entérinement (favorable, défavorable, etc.)
                    email_service.send_status_change_email(
                        project=p,
                        user_email=soumissionnaire.email,
                        user_name=soumissionnaire.nom or soumissionnaire.username
                    )
        except Exception as email_error:
            print(f"[EMAIL] Erreur lors de l'envoi d'email: {email_error}")
            # Ne pas bloquer le traitement principal si l'email échoue

        return jsonify({"message": "Décision du Comité enregistrée avec succès"}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Édition de la fiche d'évaluation par le Secrétariat SCT
@app.route("/api/projects/<int:project_id>/editer-fiche", methods=["POST"])
def editer_fiche(project_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Données manquantes"}), 400

        p = Project.query.get_or_404(project_id)

        # Vérifier que le projet a une fiche d'évaluation
        if not p.avis:
            return jsonify({"error": "Aucune fiche d'évaluation à modifier"}), 400

        # Récupérer les données de la requête
        fiche_data = data.get('fiche', {})
        motif = data.get('motif', '').strip()
        auteur = data.get('auteur', 'Inconnu')
        role = data.get('role', 'SecretariatSCT')

        # Charger la fiche existante
        try:
            fiche_actuelle = json.loads(p.fiche_evaluation) if p.fiche_evaluation else {}
        except:
            fiche_actuelle = {}

        # Mettre à jour la fiche avec les nouvelles valeurs
        fiche_actuelle['criteres'] = fiche_data.get('criteres', {})
        fiche_actuelle['avis'] = fiche_data.get('avis', p.avis)
        fiche_actuelle['commentaires'] = fiche_data.get('commentaires', '')

        # Calculer le nouveau score total (gérer les valeurs None)
        score_total = sum(
            critere.get('score', 0) or 0
            for critere in fiche_actuelle.get('criteres', {}).values()
        )
        fiche_actuelle['score_total'] = score_total

        # Sauvegarder dans la base de données
        p.fiche_evaluation = json.dumps(fiche_actuelle, ensure_ascii=False)
        p.avis = fiche_actuelle['avis']
        p.score = score_total

        db.session.commit()

        # Ajouter une entrée dans l'historique
        if motif:
            action = f"Fiche d'évaluation modifiée par {auteur} ({role}). Motif: {motif} - Nouveau score: {score_total}/100"
        else:
            action = f"Fiche d'évaluation modifiée par {auteur} ({role}) - Nouveau score: {score_total}/100"
        hist = Historique(
            project_id=p.id,
            action=action,
            auteur=auteur,
            role=role
        )
        db.session.add(hist)
        db.session.commit()

        return jsonify({
            "message": "Fiche modifiée avec succès",
            "score_total": score_total
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/uploads/<path:filename>")
def uploaded_file(filename):
    """Serve uploaded files including those in subfolders"""
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route("/api/archives/fiches_evaluation/<path:filename>")
def archived_fiche_file(filename):
    """Serve archived evaluation form PDFs"""
    try:
        # Utiliser DATA_DIR si défini (Render), sinon chemin local
        data_dir = os.environ.get('DATA_DIR', None)
        if data_dir:
            archives_dir = os.path.join(data_dir, 'archives', 'fiches_evaluation')
        else:
            backend_dir = os.path.dirname(__file__)
            archives_dir = os.path.join(backend_dir, 'archives', 'fiches_evaluation')

        return send_from_directory(archives_dir, filename)
    except Exception as e:
        return jsonify({"error": f"Archive non trouvée: {str(e)}"}), 404

@app.route("/api/logs/<int:project_id>")
def get_project_logs(project_id):
    try:
        import re

        # Récupérer le projet pour vérifier son statut
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404

        # Déterminer si on doit masquer les scores/propositions
        # On les masque tant que le projet n'est pas approuvé ou rejeté (validation complète)
        should_hide_scores = project.statut not in ['approuvé', 'rejeté']

        logs = Historique.query.filter_by(project_id=project_id).order_by(Historique.date_action.desc()).all()
        result = []

        for log in logs:
            action = log.action

            # Si on doit masquer les scores et que l'action contient score/proposition
            if should_hide_scores and action and "Fiche d'évaluation soumise" in action:
                # Strip score and proposition, keep only "Fiche d'évaluation soumise"
                action = re.sub(r'\s*-\s*Score:.*$', '', action)

            result.append({
                "id": log.id,
                "action": action,
                "auteur": log.auteur,
                "role": log.role,
                "date": log.date_action.isoformat() if log.date_action else None,
                "statut": "",  # Le statut peut être extrait de l'action si nécessaire
                "commentaire": ""  # Les commentaires sont dans l'action principale
            })

        return jsonify(result), 200
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ============ Routes de gestion des utilisateurs ============
@app.route("/api/users", methods=["GET"])
def get_users():
    """Récupérer tous les utilisateurs"""
    try:
        users = User.query.all()
        result = [{
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "display_name": u.display_name or u.username,
            "email": (u.email if hasattr(u, 'email') and u.email else u.username) if '@' in u.username else None,
            "telephone": u.telephone if hasattr(u, 'telephone') else None,
            "is_point_focal": u.is_point_focal if hasattr(u, 'is_point_focal') else False,
            "point_focal_organisme": u.point_focal_organisme if hasattr(u, 'point_focal_organisme') else None,
            "nom_structure": u.nom_structure if hasattr(u, 'nom_structure') else None,
            "type_structure": u.type_structure if hasattr(u, 'type_structure') else None,
            "statut_compte": u.statut_compte if hasattr(u, 'statut_compte') else 'non_verifie'
        } for u in users]
        return jsonify(result), 200
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/login", methods=["POST"])
def login():
    """Endpoint de connexion avec validation des identifiants et logging"""
    try:
        data = request.json
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        # Récupérer l'adresse IP et le User-Agent
        adresse_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')

        if not username or not password:
            # Logger la tentative échouée
            log_entry = ConnexionLog(
                username=username or "unknown",
                date_connexion=datetime.utcnow(),
                adresse_ip=adresse_ip,
                user_agent=user_agent,
                statut='echec',
                raison_echec='Identifiant ou mot de passe manquant'
            )
            db.session.add(log_entry)
            db.session.commit()
            return jsonify({"error": "Identifiant et mot de passe requis"}), 400

        # Vérifier les identifiants (username OU email)
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if not user or user.password != password:
            # Logger la tentative échouée
            log_entry = ConnexionLog(
                username=username,
                display_name=user.display_name if user else None,
                role=user.role if user else None,
                date_connexion=datetime.utcnow(),
                adresse_ip=adresse_ip,
                user_agent=user_agent,
                statut='echec',
                raison_echec='Identifiant ou mot de passe incorrect'
            )
            db.session.add(log_entry)
            db.session.commit()
            return jsonify({"error": "Identifiant ou mot de passe incorrect"}), 401

        # Vérifier le statut du compte
        if hasattr(user, 'statut_compte') and user.statut_compte == 'suspendu':
            log_entry = ConnexionLog(
                username=username,
                display_name=user.display_name,
                role=user.role,
                date_connexion=datetime.utcnow(),
                adresse_ip=adresse_ip,
                user_agent=user_agent,
                statut='echec',
                raison_echec='Compte suspendu'
            )
            db.session.add(log_entry)
            db.session.commit()
            return jsonify({"error": "Votre compte a été suspendu"}), 403

        # Connexion réussie - Logger le succès
        log_entry = ConnexionLog(
            username=username,
            display_name=user.display_name or username,
            role=user.role,
            date_connexion=datetime.utcnow(),
            adresse_ip=adresse_ip,
            user_agent=user_agent,
            statut='succes'
        )
        db.session.add(log_entry)
        db.session.commit()

        print(f"[LOGIN SUCCESS] User {username} ({user.role}) logged in from {adresse_ip}")

        # Retourner les informations de l'utilisateur
        return jsonify({
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "display_name": user.display_name or user.username,
            "nom": user.username,
            "email": getattr(user, 'email', None),
            "telephone": user.telephone if hasattr(user, 'telephone') else None,
            "statut_compte": user.statut_compte if hasattr(user, 'statut_compte') else 'actif',
            "is_point_focal": user.is_point_focal if hasattr(user, 'is_point_focal') else False,
            "point_focal_organisme": user.point_focal_organisme if hasattr(user, 'point_focal_organisme') else None,
            "must_change_password": user.must_change_password if hasattr(user, 'must_change_password') else False
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/connexion-logs", methods=["GET"])
def get_connexion_logs():
    """Récupérer l'historique des connexions (réservé admin et secretariatsct)"""
    try:
        # Vérifier les permissions
        role = request.args.get('role', '').lower()
        if role not in ['admin', 'secretariatsct']:
            return jsonify({"error": "Accès non autorisé. Cette fonctionnalité est réservée aux administrateurs et au secrétariat SCT."}), 403

        # Paramètres de filtrage
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        username_filter = request.args.get('username', '').strip()
        statut_filter = request.args.get('statut', '').strip()  # 'succes' ou 'echec'
        date_debut = request.args.get('date_debut', '').strip()
        date_fin = request.args.get('date_fin', '').strip()

        # Construire la requête
        query = ConnexionLog.query

        if username_filter:
            query = query.filter(ConnexionLog.username.like(f'%{username_filter}%'))

        if statut_filter:
            query = query.filter_by(statut=statut_filter)

        if date_debut:
            try:
                date_debut_obj = datetime.fromisoformat(date_debut)
                query = query.filter(ConnexionLog.date_connexion >= date_debut_obj)
            except ValueError:
                pass

        if date_fin:
            try:
                date_fin_obj = datetime.fromisoformat(date_fin)
                query = query.filter(ConnexionLog.date_connexion <= date_fin_obj)
            except ValueError:
                pass

        # Récupérer le total avant pagination
        total = query.count()

        # Appliquer la pagination et trier par date décroissante
        logs = query.order_by(ConnexionLog.date_connexion.desc()).limit(limit).offset(offset).all()

        result = {
            'total': total,
            'limit': limit,
            'offset': offset,
            'logs': [log.to_dict() for log in logs]
        }

        return jsonify(result), 200

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def get_geolocation(ip_address):
    """Récupère la géolocalisation d'une adresse IP via plusieurs APIs avec fallback"""
    try:
        # Pour les IPs locales en développement, retourner des données de test
        if ip_address in ['127.0.0.1', 'localhost', '::1'] or ip_address.startswith('192.168.') or ip_address.startswith('10.'):
            print(f"[GEOLOC] IP locale détectée: {ip_address} - Données de test retournées")
            return "Sénégal", "Dakar", "Dakar"

        # Essayer d'abord ip-api.com (gratuit, 45 requêtes/minute sans clé API)
        print(f"[GEOLOC] Tentative 1: ip-api.com pour {ip_address}")
        try:
            response = requests.get(f'http://ip-api.com/json/{ip_address}?fields=status,country,regionName,city', timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    pays = data.get('country', None)
                    ville = data.get('city', None)
                    region = data.get('regionName', None)
                    print(f"[GEOLOC] ip-api.com - Données reçues: pays={pays}, ville={ville}, region={region}")
                    return pays, ville, region
                else:
                    print(f"[GEOLOC] ip-api.com - Échec: {data.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"[GEOLOC] ip-api.com - Exception: {e}")

        # Fallback: ipapi.co (30k requêtes/mois)
        print(f"[GEOLOC] Tentative 2: ipapi.co pour {ip_address}")
        try:
            response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=3)
            if response.status_code == 200:
                data = response.json()
                # Vérifier si c'est une erreur (ipapi.co retourne parfois 200 avec un message d'erreur)
                if 'error' not in data:
                    pays = data.get('country_name', None)
                    ville = data.get('city', None)
                    region = data.get('region', None)
                    print(f"[GEOLOC] ipapi.co - Données reçues: pays={pays}, ville={ville}, region={region}")
                    return pays, ville, region
                else:
                    print(f"[GEOLOC] ipapi.co - Erreur: {data.get('reason', 'Unknown')}")
            else:
                print(f"[GEOLOC] ipapi.co - HTTP {response.status_code}")
        except Exception as e:
            print(f"[GEOLOC] ipapi.co - Exception: {e}")

        # Fallback final: identifier le pays par IP range (basique)
        # IPs sénégalaises commencent souvent par 41.x ou 197.x
        if ip_address.startswith('41.') or ip_address.startswith('197.'):
            print(f"[GEOLOC] Fallback: IP sénégalaise détectée par range")
            return "Sénégal", None, None

    except Exception as e:
        print(f"[GEOLOC] Exception générale pour {ip_address}: {e}")
        import traceback
        traceback.print_exc()

    print(f"[GEOLOC] Aucune géolocalisation trouvée pour {ip_address}")
    return None, None, None

@app.route("/api/connexion-logs", methods=["POST"])
def log_connexion():
    """Enregistrer une connexion utilisateur"""
    try:
        data = request.get_json()

        username = data.get('username', '').strip()
        if not username:
            return jsonify({"error": "Username requis"}), 400

        # Récupérer les informations de l'utilisateur
        user = User.query.filter_by(username=username).first()
        display_name = user.display_name if user and user.display_name else username
        role = data.get('role', user.role if user else '')

        # Récupérer l'adresse IP réelle (en tenant compte des proxies)
        # Priorité : X-Forwarded-For > X-Real-IP > remote_addr
        ip_address = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        if not ip_address:
            ip_address = request.headers.get('X-Real-IP', '').strip()
        if not ip_address:
            ip_address = request.remote_addr

        print(f"[CONNEXION] IP détectée: {ip_address}")

        # Vérifier si des coordonnées GPS sont fournies par le client
        gps_coords = data.get('gps_coordinates')
        latitude = None
        longitude = None
        precision_geoloc = None
        source_geoloc = None
        pays = None
        ville = None
        region = None

        if gps_coords and isinstance(gps_coords, dict):
            # Géolocalisation GPS prioritaire
            latitude = gps_coords.get('latitude')
            longitude = gps_coords.get('longitude')
            precision_geoloc = gps_coords.get('accuracy')  # Précision en mètres

            if latitude is not None and longitude is not None:
                print(f"[CONNEXION] GPS reçu: lat={latitude}, lon={longitude}, précision={precision_geoloc}m")
                source_geoloc = 'gps'

                # Reverse geocoding pour obtenir pays/département/région à partir des coordonnées
                # Utiliser une API de reverse geocoding (OpenStreetMap Nominatim gratuit)
                # Zoom 8 = niveau département (pas trop précis, adapté pour territorialisation)
                try:
                    reverse_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}&zoom=8"
                    headers = {'User-Agent': 'PLASMAP/1.0'}  # Nominatim requiert un User-Agent
                    reverse_response = requests.get(reverse_url, headers=headers, timeout=3)
                    if reverse_response.status_code == 200:
                        reverse_data = reverse_response.json()
                        address = reverse_data.get('address', {})
                        pays = address.get('country', None)
                        # Pour le Sénégal : county = département, state = région
                        ville = address.get('county') or address.get('state_district', None)  # Département
                        region = address.get('state') or address.get('region', None)  # Région
                        print(f"[CONNEXION] Reverse geocoding: Département={ville}, Région={region}, Pays={pays}")
                except Exception as e:
                    print(f"[CONNEXION] Erreur reverse geocoding: {e}")

        # Fallback sur géolocalisation IP si pas de GPS ou échec
        if not pays or not ville:
            print(f"[CONNEXION] Fallback sur géolocalisation IP")
            pays_ip, ville_ip, region_ip = get_geolocation(ip_address)

            # Utiliser les données IP si GPS n'a pas fourni de ville
            if not pays:
                pays = pays_ip
            if not ville:
                ville = ville_ip
            if not region:
                region = region_ip

            # Indiquer la source si on n'avait pas de GPS
            if source_geoloc != 'gps':
                if pays_ip or ville_ip:
                    source_geoloc = 'ip'
                else:
                    source_geoloc = 'fallback'

        # Créer le log de connexion
        log = ConnexionLog(
            username=username,
            display_name=display_name,
            role=role,
            adresse_ip=ip_address,
            pays=pays,
            ville=ville,
            region=region,
            latitude=latitude,
            longitude=longitude,
            source_geoloc=source_geoloc,
            precision_geoloc=precision_geoloc,
            user_agent=request.headers.get('User-Agent', ''),
            statut='succes'
        )

        db.session.add(log)
        db.session.commit()

        return jsonify({"message": "Connexion enregistrée", "log_id": log.id}), 201

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ============ Routes de validation des comptes ============
@app.route("/api/admin/users", methods=["GET"])
def get_all_users_admin():
    """Récupérer tous les comptes utilisateurs avec leurs informations de validation (admin/secretariatsct/presidences)"""
    try:
        # Vérifier les permissions
        role = request.args.get('role', '').lower()
        if role not in ['admin', 'secretariatsct', 'presidencecomite', 'presidencesct']:
            return jsonify({"error": "Accès non autorisé"}), 403

        # Filtrer par statut si demandé
        statut_filter = request.args.get('statut', '')

        if statut_filter:
            users = User.query.filter_by(statut_compte=statut_filter).all()
        else:
            users = User.query.all()

        result = []
        for u in users:
            result.append({
                "id": u.id,
                "username": u.username,
                "role": u.role,
                "display_name": u.display_name or u.username,
                "nom_complet": u.nom_complet if hasattr(u, 'nom_complet') else None,
                "telephone": u.telephone if hasattr(u, 'telephone') else None,
                "fonction": u.fonction if hasattr(u, 'fonction') else None,
                "type_structure": u.type_structure if hasattr(u, 'type_structure') else None,
                "type_institution": u.type_institution if hasattr(u, 'type_institution') else None,
                "nom_structure": u.nom_structure if hasattr(u, 'nom_structure') else None,
                "direction_service": u.direction_service if hasattr(u, 'direction_service') else None,
                "nom_ministere": u.nom_ministere if hasattr(u, 'nom_ministere') else None,
                "tutelle_agence": u.tutelle_agence if hasattr(u, 'tutelle_agence') else None,
                "is_point_focal": u.is_point_focal if hasattr(u, 'is_point_focal') else False,
                "point_focal_organisme": u.point_focal_organisme if hasattr(u, 'point_focal_organisme') else None,
                "point_focal_nomme_par": u.point_focal_nomme_par if hasattr(u, 'point_focal_nomme_par') else None,
                "justificatif_path": u.justificatif_path if hasattr(u, 'justificatif_path') else None,
                "statut_compte": u.statut_compte if hasattr(u, 'statut_compte') else 'non_verifie',
                "date_verification": u.date_verification.isoformat() if hasattr(u, 'date_verification') and u.date_verification else None,
                "verifie_par": u.verifie_par if hasattr(u, 'verifie_par') else None,
                "date_creation": u.date_creation.isoformat() if hasattr(u, 'date_creation') and u.date_creation else None
            })

        return jsonify(result), 200
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/users/<int:user_id>/verify", methods=["POST"])
def verify_user_account(user_id):
    """Vérifier un compte utilisateur (accessible par admin/secretariatsct/presidences)"""
    try:
        # Vérifier les permissions
        data = request.json or {}
        role = data.get('role', '').lower()
        validateur_username = data.get('validateur_username', '') or role  # Utiliser le rôle si username vide

        print(f"DEBUG verify_user: role={role}, validateur_username='{validateur_username}', data={data}")

        if role not in ['admin', 'secretariatsct', 'presidencecomite', 'presidencesct']:
            return jsonify({"error": "Accès non autorisé"}), 403

        # Récupérer l'utilisateur
        user = User.query.get_or_404(user_id)

        # Mettre à jour le statut
        user.statut_compte = 'verifie'
        user.date_verification = datetime.utcnow()
        user.verifie_par = validateur_username

        db.session.commit()

        return jsonify({
            "message": f"Compte de {user.username} vérifié avec succès",
            "user": {
                "id": user.id,
                "username": user.username,
                "statut_compte": user.statut_compte,
                "date_verification": user.date_verification.isoformat() if user.date_verification else None,
                "verifie_par": user.verifie_par
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/users/<int:user_id>/suspend", methods=["POST"])
def suspend_user_account(user_id):
    """Suspendre un compte utilisateur (accessible par admin/secretariatsct/presidences)"""
    try:
        # Vérifier les permissions
        data = request.json or {}
        role = data.get('role', '').lower()
        suspendeur_username = data.get('username', 'admin')

        if role not in ['admin', 'secretariatsct', 'presidencecomite', 'presidencesct']:
            return jsonify({"error": "Accès non autorisé"}), 403

        # Récupérer l'utilisateur
        user = User.query.get_or_404(user_id)

        # Mettre à jour le statut et enregistrer qui a suspendu
        user.statut_compte = 'suspendu'
        user.verifie_par = suspendeur_username
        user.date_verification = datetime.utcnow()

        db.session.commit()

        return jsonify({
            "message": f"Compte de {user.username} suspendu avec succès",
            "user": {
                "id": user.id,
                "username": user.username,
                "statut_compte": user.statut_compte,
                "verifie_par": user.verifie_par
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/users/<int:user_id>/reintegrate", methods=["POST"])
def reintegrate_user_account(user_id):
    """Réintégrer un compte utilisateur suspendu (accessible par admin/secretariatsct/presidences)"""
    try:
        # Vérifier les permissions
        data = request.json or {}
        role = data.get('role', '').lower()

        if role not in ['admin', 'secretariatsct', 'presidencecomite', 'presidencesct']:
            return jsonify({"error": "Accès non autorisé"}), 403

        # Récupérer l'utilisateur
        user = User.query.get_or_404(user_id)

        # Vérifier que le compte est bien suspendu
        if user.statut_compte != 'suspendu':
            return jsonify({"error": "Ce compte n'est pas suspendu"}), 400

        # Réintégrer le compte (retour au statut vérifié)
        user.statut_compte = 'verifie'

        db.session.commit()

        return jsonify({
            "message": f"Compte de {user.username} réintégré avec succès",
            "user": {
                "id": user.id,
                "username": user.username,
                "statut_compte": user.statut_compte
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/users/<int:user_id>", methods=["PUT"])
def update_user_details(user_id):
    """Modifier les détails d'un compte utilisateur (accessible par admin/secretariatsct/presidences)"""
    try:
        # Vérifier les permissions
        data = request.json or {}
        role = data.get('role', '').lower()

        if role not in ['admin', 'secretariatsct', 'presidencecomite', 'presidencesct']:
            return jsonify({"error": "Accès non autorisé"}), 403

        # Récupérer l'utilisateur
        user = User.query.get_or_404(user_id)

        # Mettre à jour les champs autorisés
        if 'display_name' in data and data['display_name'] is not None:
            user.display_name = data['display_name']

        if 'telephone' in data and data['telephone'] is not None:
            user.telephone = data['telephone']

        if 'fonction' in data and data['fonction'] is not None:
            user.fonction = data['fonction']

        if 'type_structure' in data and data['type_structure'] is not None:
            user.type_structure = data['type_structure']

        if 'type_institution' in data and data['type_institution'] is not None:
            user.type_institution = data['type_institution']

        if 'nom_structure' in data and data['nom_structure'] is not None:
            user.nom_structure = data['nom_structure']

        if 'direction_service' in data and data['direction_service'] is not None:
            user.direction_service = data['direction_service']

        # Champs ministère et tutelle agence
        if 'nom_ministere' in data:
            user.nom_ministere = data['nom_ministere']

        if 'tutelle_agence' in data:
            user.tutelle_agence = data['tutelle_agence']

        # Champs Point Focal
        if 'is_point_focal' in data:
            old_is_point_focal = user.is_point_focal if hasattr(user, 'is_point_focal') else False
            user.is_point_focal = data['is_point_focal']
            # Si on vient de cocher Point Focal, enregistrer qui l'a fait
            if data['is_point_focal'] and not old_is_point_focal:
                admin_username = data.get('admin_username', 'admin')
                user.point_focal_nomme_par = admin_username

        if 'point_focal_organisme' in data:
            user.point_focal_organisme = data['point_focal_organisme']

        db.session.commit()

        return jsonify({
            "message": f"Détails de {user.username} mis à jour avec succès",
            "user": {
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "telephone": user.telephone,
                "fonction": user.fonction,
                "type_structure": user.type_structure,
                "type_institution": user.type_institution,
                "nom_structure": user.nom_structure,
                "direction_service": user.direction_service,
                "is_point_focal": user.is_point_focal if hasattr(user, 'is_point_focal') else False,
                "point_focal_organisme": user.point_focal_organisme if hasattr(user, 'point_focal_organisme') else None,
                "point_focal_nomme_par": user.point_focal_nomme_par if hasattr(user, 'point_focal_nomme_par') else None
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/email-config", methods=["GET"])
def get_email_config():
    """Récupérer la configuration email actuelle (admin seulement)"""
    try:
        # Vérifier les permissions (admin uniquement)
        data = request.args
        role = data.get('role', '').lower()

        if role != 'admin':
            return jsonify({"error": "Accès non autorisé"}), 403

        # Récupérer la configuration depuis email_service
        config = {
            "enabled": email_service.EMAIL_ENABLED,
            "debug_mode": email_service.EMAIL_DEBUG_MODE,
            "smtp_server": email_service.SMTP_SERVER,
            "smtp_port": email_service.SMTP_PORT,
            "from_email": email_service.FROM_EMAIL,
            "from_name": email_service.FROM_NAME,
            "platform_url": email_service.PLATFORM_URL,
            "smtp_username": email_service.SMTP_USERNAME[:10] + "..." if email_service.SMTP_USERNAME else None,
            "password_configured": bool(email_service.SMTP_PASSWORD),
            "render_dashboard_url": "https://dashboard.render.com/web/srv-ctmvpttds78s73e9m78g/env",
            "documentation": {
                "guide_complet": "CONFIGURATION_EMAILS.md",
                "guide_rapide": "GUIDE_ACTIVATION_EMAILS.md",
                "status": "STATUS_EMAILS.md"
            }
        }

        return jsonify(config), 200

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/test-email", methods=["POST"])
def test_email_sending():
    """Tester l'envoi d'email (admin seulement)"""
    try:
        # Vérifier les permissions (admin uniquement)
        data = request.json or {}
        role = data.get('role', '').lower()

        if role != 'admin':
            return jsonify({"error": "Accès non autorisé"}), 403

        # Récupérer l'email de test
        test_email = data.get('test_email')
        if not test_email:
            return jsonify({"error": "Veuillez fournir une adresse email de test"}), 400

        # Vérifier que les emails sont activés
        if not email_service.EMAIL_ENABLED:
            return jsonify({
                "error": "Les emails sont désactivés",
                "hint": "Activer EMAIL_ENABLED=true dans les variables d'environnement"
            }), 400

        # Créer un email de test
        content = """
            <p>Ceci est un email de test envoyé depuis la console d'administration.</p>
            <p><strong>Configuration actuelle :</strong></p>
            <ul>
                <li>Serveur SMTP: {}</li>
                <li>Port: {}</li>
                <li>De: {} ({})</li>
                <li>Mode debug: {}</li>
            </ul>
            <p>Si vous recevez cet email, la configuration fonctionne correctement ✅</p>
        """.format(
            email_service.SMTP_SERVER,
            email_service.SMTP_PORT,
            email_service.FROM_EMAIL,
            email_service.FROM_NAME,
            "Activé" if email_service.EMAIL_DEBUG_MODE else "Désactivé"
        )

        html_content = email_service.get_email_template(
            title="Test de configuration email",
            content=content,
            cta_text="Accéder à la plateforme",
            cta_url=email_service.PLATFORM_URL
        )

        # Envoyer l'email de test
        success = email_service.send_email(
            to_email=test_email,
            subject="[DGPPE] Test de configuration email",
            html_content=html_content
        )

        if success:
            return jsonify({
                "success": True,
                "message": f"Email de test envoyé avec succès à {test_email}",
                "config": {
                    "smtp_server": email_service.SMTP_SERVER,
                    "smtp_port": email_service.SMTP_PORT,
                    "from_email": email_service.FROM_EMAIL
                }
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "L'envoi de l'email a échoué",
                "hint": "Vérifiez les logs du serveur pour plus de détails"
            }), 500

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "hint": "Erreur lors de l'envoi de l'email de test"
        }), 500

@app.route("/api/admin/email-config/save", methods=["POST"])
def save_email_config():
    """Enregistrer la configuration email"""
    try:
        # Vérifier l'authentification
        username = request.cookies.get("username")
        role = request.cookies.get("role")

        if not username:
            return jsonify({"error": "Non authentifié"}), 401

        # Vérifier les permissions (admin uniquement)
        if role != 'admin':
            return jsonify({"error": "Accès non autorisé. Seuls les administrateurs peuvent modifier la configuration email."}), 403

        # Récupérer les données
        data = request.get_json()
        if not data or 'config' not in data:
            return jsonify({"error": "Données manquantes"}), 400

        config = data['config']

        # Valider les champs requis
        required_fields = ['smtp_server', 'smtp_port', 'smtp_username', 'smtp_password', 'from_email', 'from_name', 'platform_url']
        for field in required_fields:
            if field not in config or not config[field]:
                return jsonify({"error": f"Le champ '{field}' est requis"}), 400

        # Valider le format de l'email
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, config['from_email']):
            return jsonify({"error": "Format d'email invalide pour 'from_email'"}), 400

        # Valider le port
        try:
            port = int(config['smtp_port'])
            if port < 1 or port > 65535:
                return jsonify({"error": "Le port SMTP doit être entre 1 et 65535"}), 400
        except ValueError:
            return jsonify({"error": "Le port SMTP doit être un nombre"}), 400

        # Valider l'URL de la plateforme
        if not config['platform_url'].startswith('http'):
            return jsonify({"error": "L'URL de la plateforme doit commencer par http:// ou https://"}), 400

        # Préparer les nouvelles variables d'environnement
        env_updates = {
            'EMAIL_ENABLED': 'true' if config.get('enabled', False) else 'false',
            'EMAIL_DEBUG_MODE': 'true' if config.get('debug_mode', False) else 'false',
            'SMTP_SERVER': config['smtp_server'],
            'SMTP_PORT': str(config['smtp_port']),
            'SMTP_USERNAME': config['smtp_username'],
            'SMTP_PASSWORD': config['smtp_password'],
            'FROM_EMAIL': config['from_email'],
            'FROM_NAME': config['from_name'],
            'PLATFORM_URL': config['platform_url']
        }

        # Déterminer le chemin du fichier .env
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(backend_dir, '.env')

        # Lire le fichier .env existant
        env_lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                env_lines = f.readlines()

        # Mettre à jour ou ajouter les variables
        updated_keys = set()
        new_lines = []

        for line in env_lines:
            line = line.rstrip('\n')
            # Ignorer les lignes vides et les commentaires
            if not line or line.strip().startswith('#'):
                new_lines.append(line)
                continue

            # Extraire la clé
            if '=' in line:
                key = line.split('=', 1)[0].strip()
                if key in env_updates:
                    # Mettre à jour la valeur
                    new_lines.append(f"{key}={env_updates[key]}")
                    updated_keys.add(key)
                else:
                    # Garder la ligne inchangée
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # Ajouter les nouvelles variables qui n'existaient pas
        for key, value in env_updates.items():
            if key not in updated_keys:
                new_lines.append(f"{key}={value}")

        # Écrire le fichier .env
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
            if new_lines and not new_lines[-1]:  # Ajouter newline final si nécessaire
                pass
            else:
                f.write('\n')

        print(f"[EMAIL_CONFIG] Configuration mise à jour par {username} ({role})")

        # Recharger la configuration dans email_service
        import email_service
        import importlib
        importlib.reload(email_service)

        # Mettre à jour les variables dans le module courant
        from email_service import (
            EMAIL_ENABLED, EMAIL_DEBUG_MODE, SMTP_SERVER, SMTP_PORT,
            SMTP_USERNAME, SMTP_PASSWORD, FROM_EMAIL, FROM_NAME, PLATFORM_URL
        )

        print(f"[EMAIL_CONFIG] Nouvelle configuration chargée: ENABLED={EMAIL_ENABLED}, SERVER={SMTP_SERVER}")

        return jsonify({
            "success": True,
            "message": "Configuration email enregistrée avec succès",
            "config": {
                "enabled": EMAIL_ENABLED,
                "debug_mode": EMAIL_DEBUG_MODE,
                "smtp_server": SMTP_SERVER,
                "smtp_port": SMTP_PORT,
                "from_email": FROM_EMAIL,
                "from_name": FROM_NAME,
                "platform_url": PLATFORM_URL
            }
        }), 200

    except Exception as e:
        print(f"[EMAIL_CONFIG] ❌ Erreur lors de la sauvegarde: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Erreur lors de l'enregistrement de la configuration",
            "details": str(e)
        }), 500


@app.route("/api/admin/email-templates", methods=["GET"])
def get_email_templates():
    """Récupérer tous les templates d'emails (admin uniquement)"""
    try:
        # Vérifier le rôle admin
        role = request.headers.get("X-Role")
        if role != 'admin':
            return jsonify({"error": "Accès non autorisé - réservé aux administrateurs"}), 403

        templates = EmailTemplate.query.all()
        return jsonify({
            "templates": [t.to_dict() for t in templates]
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Erreur lors de la récupération des templates",
            "details": str(e)
        }), 500


@app.route("/api/admin/email-templates/<int:template_id>", methods=["GET"])
def get_email_template(template_id):
    """Récupérer un template spécifique (admin uniquement)"""
    try:
        # Vérifier le rôle admin
        role = request.headers.get("X-Role")
        if role != 'admin':
            return jsonify({"error": "Accès non autorisé - réservé aux administrateurs"}), 403

        template = EmailTemplate.query.get(template_id)
        if not template:
            return jsonify({"error": "Template non trouvé"}), 404

        return jsonify(template.to_dict()), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Erreur lors de la récupération du template",
            "details": str(e)
        }), 500


@app.route("/api/admin/email-templates/<int:template_id>", methods=["PUT"])
def update_email_template(template_id):
    """Mettre à jour un template d'email (admin uniquement)"""
    try:
        # Vérifier le rôle admin
        role = request.headers.get("X-Role")
        username = request.headers.get("X-Username")

        if role != 'admin':
            return jsonify({"error": "Accès non autorisé - réservé aux administrateurs"}), 403

        template = EmailTemplate.query.get(template_id)
        if not template:
            return jsonify({"error": "Template non trouvé"}), 404

        data = request.get_json()

        # Mettre à jour les champs
        if 'nom' in data:
            template.nom = data['nom']
        if 'description' in data:
            template.description = data['description']
        if 'sujet' in data:
            template.sujet = data['sujet']
        if 'contenu_html' in data:
            template.contenu_html = data['contenu_html']
        if 'actif' in data:
            template.actif = data['actif']

        # Enregistrer qui a modifié
        template.modifie_par = username
        template.modifie_le = datetime.utcnow()

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Template mis à jour avec succès",
            "template": template.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Erreur lors de la mise à jour du template",
            "details": str(e)
        }), 500


@app.route("/api/admin/email-templates/preview", methods=["POST"])
def preview_email_template():
    """Prévisualiser un template avec des données de test (admin uniquement)"""
    try:
        # Vérifier le rôle admin
        role = request.headers.get("X-Role")
        if role != 'admin':
            return jsonify({"error": "Accès non autorisé - réservé aux administrateurs"}), 403

        data = request.get_json()
        contenu_html = data.get('contenu_html', '')
        sujet = data.get('sujet', '')

        # Données de test pour le remplacement
        test_vars = {
            '{user_name}': 'Jean Dupont',
            '{project_titre}': 'Construction d\'une école primaire',
            '{numero_projet}': 'DGPPE-25-001',
            '{evaluateur_nom}': 'Marie Martin',
            '{auteur_nom}': 'Jean Dupont',
            '{message_auteur}': 'Secrétariat SCT',
            '{message_complements}': 'Veuillez fournir le budget détaillé du projet.'
        }

        # Remplacer les variables dans le sujet et le contenu
        preview_sujet = sujet
        preview_html = contenu_html

        for var, value in test_vars.items():
            preview_sujet = preview_sujet.replace(var, value)
            preview_html = preview_html.replace(var, value)

        # Générer le HTML complet avec le template email
        from email_service import get_email_template
        full_html = get_email_template(
            title=preview_sujet,
            content=preview_html
        )

        return jsonify({
            "sujet": preview_sujet,
            "html": full_html
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Erreur lors de la prévisualisation",
            "details": str(e)
        }), 500


@app.route("/api/users/<username>/status", methods=["GET"])
def get_user_status(username):
    """Récupérer le statut du compte d'un utilisateur"""
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        return jsonify({
            "username": user.username,
            "statut_compte": user.statut_compte,
            "date_verification": user.date_verification.isoformat() if user.date_verification else None,
            "verifie_par": user.verifie_par
        }), 200
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/users/upload-justificatif", methods=["POST"])
def upload_justificatif():
    """Upload d'un justificatif d'identité (soumissionnaire) - ancien endpoint pour compatibilité"""
    try:
        # Récupérer l'utilisateur
        username = request.form.get('username')
        if not username:
            return jsonify({"error": "Username requis"}), 400

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        # Récupérer le fichier
        if 'file' not in request.files:
            return jsonify({"error": "Aucun fichier fourni"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Nom de fichier vide"}), 400

        # Sauvegarder le fichier
        upload_folder = app.config["UPLOAD_FOLDER"]
        justificatifs_folder = os.path.join(upload_folder, "justificatifs")
        os.makedirs(justificatifs_folder, exist_ok=True)

        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"JUSTIF_{username}_{timestamp}_{filename}"
        filepath = os.path.join(justificatifs_folder, unique_filename)

        file.save(filepath)

        # Mettre à jour le chemin du justificatif dans la base de données
        user.justificatif_path = f"justificatifs/{unique_filename}"
        db.session.commit()

        return jsonify({
            "message": "Justificatif uploadé avec succès",
            "justificatif_path": user.justificatif_path
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/users/upload-justificatifs", methods=["POST"])
def upload_justificatifs():
    """Upload de plusieurs justificatifs d'identité (soumissionnaire)"""
    try:
        # Récupérer l'utilisateur
        username = request.form.get('username')
        if not username:
            return jsonify({"error": "Username requis"}), 400

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        # Récupérer les fichiers
        if 'files' not in request.files:
            return jsonify({"error": "Aucun fichier fourni"}), 400

        files = request.files.getlist('files')
        if not files or len(files) == 0:
            return jsonify({"error": "Aucun fichier fourni"}), 400

        # Sauvegarder les fichiers
        upload_folder = app.config["UPLOAD_FOLDER"]
        justificatifs_folder = os.path.join(upload_folder, "justificatifs")
        os.makedirs(justificatifs_folder, exist_ok=True)

        uploaded_paths = []
        for file in files:
            if file.filename == '':
                continue

            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # Ajout microsecondes pour unicité
            unique_filename = f"JUSTIF_{username}_{timestamp}_{filename}"
            filepath = os.path.join(justificatifs_folder, unique_filename)

            file.save(filepath)
            uploaded_paths.append(f"justificatifs/{unique_filename}")

        # Stocker les chemins séparés par des virgules dans justificatif_path
        if uploaded_paths:
            user.justificatif_path = ",".join(uploaded_paths)
            db.session.commit()

        return jsonify({
            "message": f"{len(uploaded_paths)} justificatif(s) uploadé(s) avec succès",
            "justificatif_paths": uploaded_paths
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/users/<username>/profile", methods=["GET"])
def get_user_profile(username):
    """Récupérer les informations complètes du profil utilisateur"""
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        return jsonify({
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "email": user.email if hasattr(user, 'email') else None,
            "telephone": user.telephone if hasattr(user, 'telephone') else None,
            "fonction": user.fonction if hasattr(user, 'fonction') else None,
            "type_structure": user.type_structure if hasattr(user, 'type_structure') else None,
            "type_institution": user.type_institution if hasattr(user, 'type_institution') else None,
            "nom_structure": user.nom_structure if hasattr(user, 'nom_structure') else None,
            "direction_service": user.direction_service if hasattr(user, 'direction_service') else None,
            "nom_ministere": user.nom_ministere if hasattr(user, 'nom_ministere') else None,
            "tutelle_agence": user.tutelle_agence if hasattr(user, 'tutelle_agence') else None,
            "is_point_focal": user.is_point_focal if hasattr(user, 'is_point_focal') else False,
            "point_focal_organisme": user.point_focal_organisme if hasattr(user, 'point_focal_organisme') else None,
            "point_focal_nomme_par": user.point_focal_nomme_par if hasattr(user, 'point_focal_nomme_par') else None,
            "statut_compte": user.statut_compte if hasattr(user, 'statut_compte') else 'non_verifie'
        }), 200

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/user-projects", methods=["GET"])
def get_user_projects():
    """Récupérer les projets soumis par un utilisateur"""
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({"error": "Username requis"}), 400

        # Récupérer les projets de l'utilisateur
        projects = Project.query.filter_by(auteur_nom=username).order_by(Project.date_soumission.desc()).all()

        result = []
        for p in projects:
            result.append({
                "id": p.id,
                "numero_projet": p.numero_projet,
                "titre": p.titre,
                "statut": p.statut,
                "date_soumission": p.date_soumission.isoformat() if p.date_soumission else None
            })

        return jsonify(result), 200
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/users/<username>/profile", methods=["PUT"])
def update_user_profile(username):
    """Mettre à jour les informations du profil utilisateur (téléphone, email)"""
    try:
        data = request.get_json()

        # Récupérer l'utilisateur
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        # Mettre à jour les champs autorisés
        if 'telephone' in data:
            user.telephone = data['telephone']

        # Mettre à jour l'email (champ séparé du username)
        if 'email' in data:
            new_email = data['email'].strip()
            if new_email:
                # Vérifier que l'email n'est pas déjà utilisé par un autre utilisateur
                existing_user = User.query.filter(
                    User.email == new_email,
                    User.id != user.id
                ).first()
                if existing_user:
                    return jsonify({"error": "Cet email est déjà utilisé par un autre compte"}), 400
                user.email = new_email
                print(f"[PROFILE UPDATE] Email mis à jour pour {username}: {new_email}")
            else:
                user.email = None

        db.session.commit()

        print(f"[PROFILE UPDATE] Profil mis à jour pour {username}")
        return jsonify({
            "message": "Profil mis à jour avec succès",
            "user": {
                "username": user.username,
                "email": user.email,
                "telephone": user.telephone,
                "display_name": user.display_name
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/users/<username>/password", methods=["PUT"])
def change_user_password(username):
    """Changer le mot de passe de l'utilisateur après vérification de l'ancien"""
    try:
        data = request.get_json()

        # Vérifier les champs requis
        if not data.get('old_password') or not data.get('new_password'):
            return jsonify({"error": "Ancien et nouveau mot de passe requis"}), 400

        # Récupérer l'utilisateur
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        # Vérifier l'ancien mot de passe
        if user.password != data['old_password']:
            return jsonify({"error": "L'ancien mot de passe est incorrect"}), 401

        # Vérifier que le nouveau mot de passe est différent
        if data['old_password'] == data['new_password']:
            return jsonify({"error": "Le nouveau mot de passe doit être différent de l'ancien"}), 400

        # Mettre à jour le mot de passe
        user.password = data['new_password']
        db.session.commit()

        print(f"[PASSWORD CHANGE] Mot de passe changé pour {username}")
        return jsonify({"message": "Mot de passe changé avec succès"}), 200

    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ============ Routes pour les données territoriales et administratives ============
@app.route("/api/data/regions", methods=["GET"])
def get_regions():
    """Récupérer la liste des régions du Sénégal"""
    try:
        from data_senegal import REGIONS
        return jsonify(REGIONS), 200
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/data/departements", methods=["GET"])
def get_departements():
    """Récupérer la liste des départements (tous ou par région)"""
    try:
        from data_senegal import DEPARTEMENTS, get_all_departements, get_departements_by_region

        region = request.args.get('region', '')

        if region:
            # Retourner les départements d'une région spécifique
            result = get_departements_by_region(region)
        else:
            # Retourner tous les départements ou le dictionnaire complet
            format_type = request.args.get('format', 'list')
            if format_type == 'dict':
                result = DEPARTEMENTS
            else:
                result = get_all_departements()

        return jsonify(result), 200
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/data/communes", methods=["GET"])
def get_communes():
    """Récupérer la liste des communes (toutes ou par département)"""
    try:
        from communes_senegal import get_all_communes, search_communes, get_communes_by_departement

        query = request.args.get('q', '')
        format_type = request.args.get('format', 'list')

        if format_type == 'dict':
            # Retourner les communes organisées par département
            result = get_communes_by_departement()
        elif query:
            result = search_communes(query)
        else:
            result = get_all_communes()

        return jsonify(result), 200
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/data/ministeres", methods=["GET"])
def get_ministeres():
    """Récupérer la liste des ministères"""
    try:
        from data_senegal import MINISTERES
        return jsonify(MINISTERES), 200
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/data/agences", methods=["GET"])
def get_agences():
    """Récupérer la liste des agences et établissements publics"""
    try:
        from data_senegal import AGENCES
        return jsonify(AGENCES), 200
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Récupérer un utilisateur spécifique"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            "id": user.id,
            "username": user.username,
            "role": user.role
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route("/api/users", methods=["POST"])
@app.route("/api/register", methods=["POST"])  # Alias pour compatibilité frontend
def create_user():
    """Créer un nouvel utilisateur (inscription enrichie avec validation)"""
    try:
        data = request.json
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        role = data.get("role", "").strip()
        display_name = data.get("display_name", "").strip()

        # Nouveaux champs pour la validation des comptes (système Institution)
        email = data.get("email", "").strip()
        nom_complet = data.get("nom_complet", "").strip()
        telephone = data.get("telephone", "").strip()
        fonction = data.get("fonction", "").strip()
        type_structure = data.get("type_structure", "").strip()
        type_institution = data.get("type_institution", "").strip()
        nom_structure = data.get("nom_structure", "").strip()
        direction_service = data.get("direction_service", "").strip()
        nom_ministere = data.get("nom_ministere") or ""
        tutelle_agence = data.get("tutelle_agence") or ""
        if nom_ministere:
            nom_ministere = nom_ministere.strip()
        if tutelle_agence:
            tutelle_agence = tutelle_agence.strip()

        # Vérifier si créé par un admin (donc doit changer le mot de passe)
        created_by_admin = data.get("created_by_admin", False)

        if not username or not password or not role:
            return jsonify({"error": "Username, password et rôle sont requis"}), 400

        # Vérifier si l'utilisateur existe déjà
        existing = User.query.filter_by(username=username).first()
        if existing:
            return jsonify({"error": "Un utilisateur avec cet identifiant existe déjà"}), 400

        # Créer le nouvel utilisateur avec les nouveaux champs
        new_user = User(
            username=username,
            password=password,
            role=role,
            display_name=display_name,
            email=email if email else None,
            nom_complet=nom_complet,
            telephone=telephone,
            fonction=fonction,
            type_structure=type_structure,
            type_institution=type_institution,
            nom_structure=nom_structure,
            direction_service=direction_service,
            nom_ministere=nom_ministere if nom_ministere else None,
            tutelle_agence=tutelle_agence if tutelle_agence else None,
            statut_compte='non_verifie',
            date_creation=datetime.utcnow(),
            must_change_password=created_by_admin  # Si créé par admin, doit changer le mot de passe
        )

        db.session.add(new_user)
        db.session.commit()

        # Envoyer des notifications aux admins et secrétariat SCT pour les comptes à vérifier
        try:
            # Récupérer les admins et secrétariat SCT
            admins_and_secretariat = User.query.filter(
                User.role.in_(['admin', 'secretariatsct'])
            ).all()

            for admin_user in admins_and_secretariat:
                create_notification_for_user(
                    user_id=admin_user.id,
                    notif_type='nouveau_compte',
                    titre='Nouveau compte à vérifier',
                    message=f"L'utilisateur {nom_complet or username} a créé un compte ({role}). Veuillez vérifier ce compte.",
                    lien='/gestion-comptes',
                    priorite_email=True
                )
        except Exception as notif_error:
            print(f"Erreur lors de l'envoi des notifications: {notif_error}")
            # On ne bloque pas la création du compte si les notifications échouent

        return jsonify({
            "id": new_user.id,
            "username": new_user.username,
            "role": new_user.role,
            "statut_compte": new_user.statut_compte,
            "message": "Utilisateur créé avec succès"
        }), 201
    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """Mettre à jour un utilisateur existant"""
    try:
        user = User.query.get_or_404(user_id)
        # Récupération sécurisée du payload JSON
        data = request.get_json(silent=True) or {}
        old_username = user.username
        
        # Mise à jour des champs si fournis
        if "username" in data and data["username"].strip():
            # Vérifier que le nouveau nom n'existe pas déjà
            existing = User.query.filter(User.username == data["username"], User.id != user_id).first()
            if existing:
                return jsonify({"error": "Ce nom d'utilisateur est déjà pris"}), 400
            user.username = data["username"].strip()
        
        if "display_name" in data:
            user.display_name = data["display_name"].strip() if data["display_name"] else None
        
        if "password" in data and data["password"].strip():
            user.password = data["password"].strip()
        
        if "role" in data and data["role"].strip():
            user.role = data["role"].strip()
        
        db.session.commit()

        # Propager le changement de nom d'utilisateur dans les projets assignés
        if ("username" in data and data["username"].strip() and
            data["username"].strip() != old_username):
            try:
                Project.query.filter_by(evaluateur_nom=old_username).update({"evaluateur_nom": data["username"].strip()})
                db.session.commit()
            except Exception:
                db.session.rollback()
        
        return jsonify({
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "message": "Utilisateur mis à jour avec succès"
        }), 200
    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Supprimer un utilisateur"""
    try:
        user = User.query.get_or_404(user_id)
        username = user.username

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": f"Utilisateur '{username}' supprimé avec succès"}), 200
    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/change-password", methods=["POST"])
def change_password():
    """Changer le mot de passe (utilisé lors de la première connexion)"""
    try:
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")
        old_password = data.get("old_password", "").strip()
        new_password = data.get("new_password", "").strip()

        if not user_id or not old_password or not new_password:
            return jsonify({"error": "Tous les champs sont requis"}), 400

        # Vérifier que le nouveau mot de passe est différent
        if old_password == new_password:
            return jsonify({"error": "Le nouveau mot de passe doit être différent de l'ancien"}), 400

        # Trouver l'utilisateur
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        # Vérifier l'ancien mot de passe
        if user.password != old_password:
            return jsonify({"error": "Ancien mot de passe incorrect"}), 401

        # Mettre à jour le mot de passe et réinitialiser le flag
        user.password = new_password
        user.must_change_password = False
        db.session.commit()

        return jsonify({"message": "Mot de passe modifié avec succès"}), 200
    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def check_and_reset_db():
    import sqlite3
    db_path = app.config["DB_PATH"]
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("PRAGMA table_info(projects)")
    cols = [r[1] for r in cur.fetchall()]
    con.close()
    if "auteur_nom" not in cols:
        print("[DB] La colonne 'auteur_nom' est absente, suppression et régénération de la base...")
        os.remove(db_path)

if __name__ == "__main__":
    # check_and_reset_db()  # Désactivé pour éviter les réinitialisations automatiques
    with app.app_context():
        db.create_all()
        ensure_sqlite_columns()

        # Compter les users avec raw SQL pour éviter erreur si colonne manquante
        import sqlite3
        con = sqlite3.connect(app.config["DB_PATH"])
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        con.close()

        target_pwd = "    "
        if user_count == 0:
            # Créer les utilisateurs par défaut avec assignation d'attributs
            user_data = [
                ("soumissionnaire", "soumissionnaire"),
                ("evaluateur1", "evaluateur"),
                ("evaluateur2", "evaluateur"),
                ("secretariatsct", "secretariatsct"),
                ("presidencesct", "presidencesct"),
                ("presidencecomite", "presidencecomite"),
                ("admin", "admin"),
                ("invite", "invite")
            ]
            
            # Rôles qui doivent changer leur mot de passe à la première connexion
            roles_changement_obligatoire = ["admin", "secretariatsct", "presidencesct", "presidencecomite"]

            for username, role in user_data:
                user = User()
                user.username = username
                user.password = target_pwd
                user.role = role
                # Forcer le changement de mot de passe pour les comptes admin
                if role in roles_changement_obligatoire:
                    user.must_change_password = True
                db.session.add(user)

            db.session.commit()
            print(f"[INIT] Créé {len(user_data)} utilisateurs par défaut")

        # Appeler init_demo_data() pour créer les données complètes
        try:
            from init_demo_data import init_demo_data
            init_demo_data()
        except Exception as e:
            print(f"[INIT] Erreur lors de l'initialisation des données de démo: {e}")
            import traceback
            traceback.print_exc()

        # Initialiser la configuration du formulaire par défaut
        try:
            from init_formulaire_default import init_default_config
            init_default_config()
        except Exception as e:
            print(f"[INIT] Erreur lors de l'initialisation de la configuration du formulaire: {e}")
            import traceback
            traceback.print_exc()

        # Initialiser les ministères par défaut
        try:
            from create_ministeres_table import init_ministeres
            init_ministeres()
        except Exception as e:
            print(f"[INIT] Erreur lors de l'initialisation des ministères: {e}")
            import traceback
            traceback.print_exc()

# ===================== ROUTES STATISTIQUES =====================

@app.route('/api/stats/overview', methods=['GET'])
def get_stats_overview():
    """Statistiques générales accessibles selon le rôle"""
    role = request.args.get('role', '')
    username = request.args.get('username', '')

    # Pour les rôles internes (admin, secrétariat, présidence): montrer uniquement les projets confirmés
    # Pour les rôles externes (invite, soumissionnaire): montrer TOUS les projets qu'ils peuvent voir
    if role == 'admin':
        projects = Project.query.filter_by(decision_finale='confirme').all()
    elif role in ['secretariatsct', 'presidencesct', 'presidencecomite']:
        projects = Project.query.filter_by(decision_finale='confirme').all()
    elif role in ['invite', 'soumissionnaire']:
        # Pour invite/soumissionnaire: montrer TOUS les projets (pas seulement ceux confirmés)
        projects = Project.query.all()
    else:
        # Autres rôles (évaluateurs) - limités à leurs projets validés
        projects = Project.query.filter_by(auteur_nom=username, decision_finale='confirme').all()
    
    # Calculs statistiques
    total_projets = len(projects)
    cout_total = sum(p.cout_estimatif or 0 for p in projects)
    
    # Répartition par statut
    statuts = {}
    for project in projects:
        # Pour les projets avec décision finale confirmée, utiliser l'avis au lieu du statut
        if project.decision_finale == 'confirme' and project.avis:
            statut = project.avis  # favorable, défavorable, favorable sous conditions
        elif project.decision_finale == 'infirme':
            statut = 'en réexamen par le Secrétariat SCT'
        else:
            statut = project.statut or 'non défini'
        statuts[statut] = statuts.get(statut, 0) + 1
    
    # Répartition par secteur
    secteurs = {}
    cout_par_secteur = {}
    for project in projects:
        secteur = project.secteur or 'non défini'
        secteurs[secteur] = secteurs.get(secteur, 0) + 1
        cout_par_secteur[secteur] = cout_par_secteur.get(secteur, 0) + (project.cout_estimatif or 0)
    
    # Répartition par pôle territorial
    poles = {}
    cout_par_pole = {}
    for project in projects:
        pole = project.poles or 'non défini'
        poles[pole] = poles.get(pole, 0) + 1
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

@app.route('/api/stats/secteurs', methods=['GET'])
def get_stats_secteurs():
    """Statistiques détaillées par secteur"""
    role = request.args.get('role', '')

    # Filtrer uniquement les projets validés par presidencecomite avec décision favorable
    if role == 'admin':
        projects = Project.query.filter_by(decision_finale='confirme').all()
    elif role in ['secretariatsct', 'presidencesct', 'presidencecomite']:
        projects = Project.query.filter_by(decision_finale='confirme').all()
    else:
        projects = Project.query.filter_by(auteur_nom=request.args.get('username', ''), decision_finale='confirme').all()
    
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

@app.route('/api/stats/workflow', methods=['GET'])
def get_stats_workflow():
    """Statistiques sur le flux de travail (pour secrétariat et présidences)"""
    role = request.args.get('role', '')
    
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

@app.route('/api/stats/financial', methods=['GET'])
def get_stats_financial():
    """Statistiques financières détaillées"""
    role = request.args.get('role', '')

    if role not in ['secretariatsct', 'presidencesct', 'presidencecomite', 'admin']:
        return jsonify({'error': 'Accès non autorisé'}), 403

    # Filtrer uniquement les projets validés par presidencecomite avec décision favorable
    projects = Project.query.filter_by(decision_finale='confirme').all()
    
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

# Removed duplicate @app.route("/api/stats/poles") - now handled directly in app.py

# Stats poles function with territorial grouping
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
        'Centre (Kaolack, Fatick, Kaffrine)': 'Centre',  # Format combiné

        # Sud regroupe Ziguinchor, Sedhiou, Kolda
        'Sud (Ziguinchor)': 'Sud',
        'Sud (Sedhiou)': 'Sud',
        'Sud (Kolda)': 'Sud',
        'Sud (Ziguinchor, Sédhiou, Kolda)': 'Sud',  # Format combiné

        # Sud-Est regroupe Kedougou, Tambacounda
        'Sud-Est (Kedougou)': 'Sud-Est',
        'Sud-Est (Tambacounda)': 'Sud-Est',
        'Sud-Est (Tambacounda, Kédougou)': 'Sud-Est',  # Format combiné

        # Diourbel-Louga regroupe Diourbel, Louga
        'Diourbel-Louga (Diourbel)': 'Diourbel-Louga',
        'Diourbel-Louga (Louga)': 'Diourbel-Louga',
        'Diourbel-Louga': 'Diourbel-Louga',  # Format simple

        # Pôles mono-région
        'Dakar': 'Dakar',
        'Thiès': 'Thiès',
        'Nord (Saint-Louis)': 'Nord',
        'Nord-Est (Matam)': 'Nord-Est'
    }
    
    return pole_mapping.get(pole_db, pole_db)

@app.route('/api/stats/poles', methods=['GET'])
def stats_poles_territorial():
    """Statistiques détaillées par pôle territorial (regroupées selon la carte)"""
    try:
        role = request.args.get('role', '')
        username = request.args.get('username', '')
        status_filter = request.args.get('filter', '')  # 'favorable_avis' pour filtrer uniquement les projets avec avis favorable

        # Les rôles administratifs voient tous les projets sans filtre d'auteur
        administrative_roles = ['admin', 'secretariatsct', 'presidencesct', 'presidencecomite']

        # Filtrer les projets selon le paramètre filter
        # - 'favorable_avis' ou 'favorable' : uniquement les projets avec avis 'favorable' ou 'favorable sous conditions'
        # - 'all' ou vide : tous les projets soumis
        if status_filter in ['favorable_avis', 'favorable']:
            # Carte des projets avec avis favorable
            if username and role not in administrative_roles:
                projects = Project.query.filter(
                    Project.auteur_nom == username,
                    Project.avis.in_(['favorable', 'favorable sous conditions'])
                ).all()
            else:
                projects = Project.query.filter(
                    Project.avis.in_(['favorable', 'favorable sous conditions'])
                ).all()
        else:
            # Carte de tous les projets soumis
            if username and role not in administrative_roles:
                projects = Project.query.filter_by(auteur_nom=username).all()
            else:
                projects = Project.query.all()

        poles_stats = {}

        for project in projects:
            # Extraire tous les pôles du projet (peut être plusieurs séparés par des virgules)
            poles_raw = project.poles or 'non défini'

            # Séparer les pôles multiples en respectant les parenthèses
            # Ex: "Sud-Est (Tambacounda, Kédougou),Nord-Est (Matam)" -> ["Sud-Est (Tambacounda, Kédougou)", "Nord-Est (Matam)"]
            pole_list = []
            current_pole = ""
            paren_depth = 0

            for char in poles_raw:
                if char == '(':
                    paren_depth += 1
                    current_pole += char
                elif char == ')':
                    paren_depth -= 1
                    current_pole += char
                elif char == ',' and paren_depth == 0:
                    # Virgule en dehors des parenthèses = séparateur de pôles
                    if current_pole.strip():
                        pole_list.append(current_pole.strip())
                    current_pole = ""
                else:
                    current_pole += char

            # Ajouter le dernier pôle
            if current_pole.strip():
                pole_list.append(current_pole.strip())

            # Nombre de pôles pour ce projet (pour division équitable du coût)
            num_poles = len(pole_list)
            cout_par_pole = (project.cout_estimatif or 0) / num_poles if num_poles > 0 else 0

            # Traiter chaque pôle individuellement
            for pole_db in pole_list:
                # Convertir le pôle DB vers le pôle territorial standardisé
                pole_territorial = get_pole_territorial(pole_db)

                if pole_territorial not in poles_stats:
                    poles_stats[pole_territorial] = {
                        'nombre_projets': 0,
                        'cout_total': 0,
                        'secteurs': {},
                        'statuts': {},
                        'projets': []
                    }

                # Compter le projet une fois par pôle
                poles_stats[pole_territorial]['nombre_projets'] += 1
                # Ajouter la part proportionnelle du coût
                poles_stats[pole_territorial]['cout_total'] += cout_par_pole

                # Ajouter le projet à la liste (éviter les doublons si projet sur plusieurs pôles)
                projet_ids = [p['id'] for p in poles_stats[pole_territorial]['projets']]
                if project.id not in projet_ids:
                    poles_stats[pole_territorial]['projets'].append({
                        'id': project.id,
                        'numero_projet': project.numero_projet,
                        'titre': project.titre,
                        'cout_estimatif': project.cout_estimatif,
                        'statut': project.statut,
                        'avis': project.avis,
                        'secteur': project.secteur
                    })

                # Répartition par secteur dans ce pôle
                secteur = project.secteur or 'non défini'
                poles_stats[pole_territorial]['secteurs'][secteur] = poles_stats[pole_territorial]['secteurs'].get(secteur, 0) + 1

                # Répartition par statut/avis dans ce pôle
                # Si on filtre par avis favorable, afficher les avis au lieu des statuts
                if status_filter == 'favorable_avis':
                    avis = project.avis or 'non défini'
                    poles_stats[pole_territorial]['statuts'][avis] = poles_stats[pole_territorial]['statuts'].get(avis, 0) + 1
                else:
                    statut = project.statut or 'non défini'
                    poles_stats[pole_territorial]['statuts'][statut] = poles_stats[pole_territorial]['statuts'].get(statut, 0) + 1

        # Correction : toujours retourner un JSON valide
        return jsonify(poles_stats if poles_stats else {})
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Correction : toujours retourner un JSON valide même en cas d'erreur
        return jsonify({'error': str(e), 'poles_stats': {}}), 500

# ============ Routes de gestion des documents supplémentaires ============
@app.route("/api/projects/<int:project_id>/documents", methods=["GET"])
def get_project_documents(project_id):
    """Récupérer tous les documents supplémentaires d'un projet"""
    try:
        # Vérifier que le projet existe
        project = Project.query.get_or_404(project_id)

        # Récupérer le rôle de l'utilisateur depuis les paramètres
        user_role = request.args.get("role", "").lower()
        user_name = request.args.get("username", "")

        # Les invités ne peuvent pas accéder aux documents des projets
        if user_role == "invite":
            return jsonify({"error": "Accès refusé: Les invités ne peuvent pas accéder aux documents des projets"}), 403

        # Récupérer tous les documents du projet
        documents = DocumentProjet.query.filter_by(project_id=project_id).order_by(DocumentProjet.date_ajout.desc()).all()

        # Fonction helper pour vérifier la visibilité selon visible_pour_roles
        def is_visible_for_role(doc, role):
            import json
            if not doc.visible_pour_roles:
                # Si pas de restriction, visible par tous
                return True
            try:
                allowed_roles = json.loads(doc.visible_pour_roles)
                return role in allowed_roles
            except Exception:
                # En cas d'erreur, considérer comme visible
                return True

        # Filtrer selon le rôle et visible_pour_roles
        if user_role == "soumissionnaire":
            # Vérifier que l'utilisateur a accès à ce projet (est l'auteur ou Point Focal)
            is_author = project.auteur_nom == user_name

            # Vérifier si l'utilisateur est Point Focal pour ce projet
            is_point_focal_for_project = False
            if user_name:
                user = User.query.filter_by(username=user_name).first()
                if user and user.is_point_focal and user.point_focal_organisme:
                    # Vérifier si le projet est sous la tutelle de l'organisme du Point Focal
                    is_point_focal_for_project = project.organisme_tutelle == user.point_focal_organisme

            if is_author:
                # Voir les documents de soumissionnaire et ceux visibles pour soumissionnaire
                documents = [doc for doc in documents
                           if doc.auteur_role == "soumissionnaire" and is_visible_for_role(doc, "soumissionnaire")]
            elif is_point_focal_for_project:
                # Point Focal peut voir les documents du soumissionnaire pour les projets sous sa tutelle
                documents = [doc for doc in documents
                           if doc.auteur_role == "soumissionnaire" and is_visible_for_role(doc, "soumissionnaire")]
            else:
                # Pas d'accès à ce projet
                documents = []

        elif user_role == "secteur_territorial":
            # Voit documents du soumissionnaire et ses propres documents, selon visible_pour_roles
            documents = [doc for doc in documents
                       if doc.auteur_role in ["soumissionnaire", "secteur_territorial"]
                       and is_visible_for_role(doc, "secteur_territorial")]

        elif user_role == "secretariatsct":
            # Voit tous les documents visibles pour secretariatsct
            documents = [doc for doc in documents if is_visible_for_role(doc, "secretariatsct")]

        elif user_role == "evaluateur":
            # Voit tous les documents visibles pour evaluateur
            documents = [doc for doc in documents if is_visible_for_role(doc, "evaluateur")]

        elif user_role in ["presidencesct", "presidencecomite", "admin"]:
            # Ces rôles voient tous les documents (accès complet)
            documents = [doc for doc in documents if is_visible_for_role(doc, user_role)]

        else:
            # Rôle non reconnu, aucun accès
            documents = []

        # Ajouter les pièces jointes initiales si elles n'ont pas encore été migrées
        if project.pieces_jointes:
            pieces_jointes = []
            if isinstance(project.pieces_jointes, str):
                # Essayer de split par virgule d'abord
                if ',' in project.pieces_jointes:
                    pieces_jointes = [f.strip() for f in project.pieces_jointes.split(",") if f.strip()]
                else:
                    # Si pas de virgule, c'est un seul fichier
                    pieces_jointes = [project.pieces_jointes.strip()]
            elif isinstance(project.pieces_jointes, list):
                pieces_jointes = project.pieces_jointes

            # Vérifier si les pièces jointes sont déjà dans la documenthèque
            existing_files = {doc.nom_fichier for doc in documents}

            for piece_jointe in pieces_jointes:
                if piece_jointe not in existing_files:
                    # Créer une entrée pour la pièce jointe initiale
                    try:
                        upload_folder = app.config["UPLOAD_FOLDER"]
                        filepath = os.path.join(upload_folder, piece_jointe)
                        taille = os.path.getsize(filepath) if os.path.exists(filepath) else 0

                        doc_initial = DocumentProjet(
                            project_id=project_id,
                            nom_fichier=piece_jointe,
                            nom_original=piece_jointe,
                            description="Pièce jointe de la soumission initiale",
                            type_document="initial",
                            auteur_nom=project.auteur_nom or "soumissionnaire",
                            auteur_role="soumissionnaire",
                            date_ajout=project.date_soumission or datetime.utcnow(),
                            taille_fichier=taille
                        )
                        db.session.add(doc_initial)
                    except Exception as e:
                        print(f"Erreur lors de l'ajout de {piece_jointe}: {e}")

            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

            # Recharger les documents après migration
            documents = DocumentProjet.query.filter_by(project_id=project_id).order_by(DocumentProjet.date_ajout.desc()).all()

            # Réappliquer le filtrage après rechargement
            if user_role == "soumissionnaire":
                is_author = project.auteur_nom == user_name

                # Vérifier si l'utilisateur est Point Focal pour ce projet
                is_point_focal_for_project = False
                if user_name:
                    user = User.query.filter_by(username=user_name).first()
                    if user and user.is_point_focal and user.point_focal_organisme:
                        is_point_focal_for_project = project.organisme_tutelle == user.point_focal_organisme

                if is_author or is_point_focal_for_project:
                    documents = [doc for doc in documents
                               if doc.auteur_role == "soumissionnaire" and is_visible_for_role(doc, "soumissionnaire")]
                else:
                    documents = []
            elif user_role == "secteur_territorial":
                documents = [doc for doc in documents
                           if doc.auteur_role in ["soumissionnaire", "secteur_territorial"]
                           and is_visible_for_role(doc, "secteur_territorial")]
            elif user_role == "secretariatsct":
                documents = [doc for doc in documents if is_visible_for_role(doc, "secretariatsct")]
            elif user_role == "evaluateur":
                documents = [doc for doc in documents if is_visible_for_role(doc, "evaluateur")]
            elif user_role in ["presidencesct", "presidencecomite", "admin"]:
                documents = [doc for doc in documents if is_visible_for_role(doc, user_role)]
            else:
                documents = []

        return jsonify([doc.to_dict() for doc in documents]), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<int:project_id>/documents", methods=["POST"])
def add_project_document(project_id):
    """Ajouter un ou plusieurs documents supplémentaires à un projet"""
    try:
        # Vérifier que le projet existe
        project = Project.query.get_or_404(project_id)

        # Récupérer les informations de l'auteur
        auteur_nom = request.form.get("auteur_nom")
        auteur_role = request.form.get("auteur_role")
        description = request.form.get("description", "")
        type_document = request.form.get("type_document", "")

        if not auteur_nom or not auteur_role:
            return jsonify({"error": "L'auteur et le rôle sont requis"}), 400

        # Récupérer les fichiers
        files = request.files.getlist("files")

        if not files or len(files) == 0:
            return jsonify({"error": "Au moins un fichier est requis"}), 400

        # Sauvegarder les fichiers et créer les entrées dans la base
        upload_folder = app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        documents_ajoutes = []

        for file in files:
            if file and file.filename:
                # Sécuriser et générer un nom unique pour le fichier
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_filename = f"DOC_{timestamp}_{filename}"
                filepath = os.path.join(upload_folder, unique_filename)

                # Sauvegarder le fichier
                file.save(filepath)

                # Obtenir la taille du fichier
                taille_fichier = os.path.getsize(filepath)

                # Créer l'entrée dans la base de données
                document = DocumentProjet(
                    project_id=project_id,
                    nom_fichier=unique_filename,
                    nom_original=file.filename,
                    description=description,
                    type_document=type_document,
                    auteur_nom=auteur_nom,
                    auteur_role=auteur_role,
                    taille_fichier=taille_fichier
                )

                db.session.add(document)
                documents_ajoutes.append(document)

        db.session.commit()

        # Ajouter une entrée dans l'historique
        action = f"Document(s) ajouté(s) à la documenthèque du projet ({len(documents_ajoutes)} fichier(s))"
        hist = Historique(
            project_id=project_id,
            action=action,
            auteur=auteur_nom,
            role=auteur_role
        )
        db.session.add(hist)
        db.session.commit()

        return jsonify({
            "message": f"{len(documents_ajoutes)} document(s) ajouté(s) avec succès",
            "documents": [doc.to_dict() for doc in documents_ajoutes]
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<int:project_id>/documents/<int:document_id>", methods=["DELETE"])
def delete_project_document(project_id, document_id):
    """Supprimer un document supplémentaire (admin et auteur du document uniquement)"""
    try:
        # Récupérer le document
        document = DocumentProjet.query.filter_by(id=document_id, project_id=project_id).first_or_404()

        # Vérifier les permissions
        auteur_nom = request.args.get("auteur_nom")
        role = request.args.get("role", "").lower()

        # Seul l'admin ou l'auteur du document peut le supprimer
        if role != "admin" and auteur_nom != document.auteur_nom:
            return jsonify({"error": "Vous n'avez pas la permission de supprimer ce document"}), 403

        # Supprimer le fichier physique
        # Les fiches archivées sont dans /data/archives/, les autres dans UPLOAD_FOLDER
        if document.type_document == 'fiche_evaluation_archivee':
            # Utiliser DATA_DIR si défini (Render), sinon chemin local
            data_dir = os.environ.get('DATA_DIR', None)
            if data_dir:
                archives_dir = os.path.join(data_dir, 'archives', 'fiches_evaluation')
            else:
                backend_dir = os.path.dirname(__file__)
                archives_dir = os.path.join(backend_dir, 'archives', 'fiches_evaluation')
            filepath = os.path.join(archives_dir, document.nom_fichier)
        else:
            upload_folder = app.config["UPLOAD_FOLDER"]
            filepath = os.path.join(upload_folder, document.nom_fichier)

        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"[DELETE] Fichier supprimé: {filepath}")

        # Supprimer l'entrée de la base
        nom_original = document.nom_original
        db.session.delete(document)
        db.session.commit()

        # Ajouter une entrée dans l'historique
        hist = Historique(
            project_id=project_id,
            action=f"Document supprimé de la documenthèque: {nom_original}",
            auteur=auteur_nom,
            role=role
        )
        db.session.add(hist)
        db.session.commit()

        return jsonify({"message": "Document supprimé avec succès"}), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ============ Routes de gestion des messages de discussion ============
@app.route("/api/projects/<int:project_id>/messages", methods=["GET"])
def get_project_messages(project_id):
    """Récupérer tous les messages de discussion d'un projet"""
    try:
        # Vérifier que le projet existe
        project = Project.query.get_or_404(project_id)

        # Récupérer le rôle de l'utilisateur depuis les paramètres
        user_role = request.args.get("role", "").lower()

        # Les invités ne peuvent pas accéder aux discussions des projets
        if user_role == "invite":
            return jsonify({"error": "Accès refusé: Les invités ne peuvent pas accéder aux discussions des projets"}), 403

        # Récupérer tous les messages du projet, triés par date (plus anciens en premier)
        messages = MessageProjet.query.filter_by(project_id=project_id).order_by(MessageProjet.date_creation.asc()).all()

        return jsonify([message.to_dict() for message in messages]), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<int:project_id>/messages", methods=["POST"])
def add_project_message(project_id):
    """Ajouter un message de discussion à un projet (avec fichiers optionnels)"""
    try:
        # Vérifier que le projet existe
        project = Project.query.get_or_404(project_id)

        # Déterminer si c'est une requête avec fichiers (multipart) ou JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Requête avec fichiers
            auteur_nom = request.form.get("auteur_nom")
            auteur_role = request.form.get("auteur_role")
            contenu = request.form.get("contenu", "").strip()
        else:
            # Requête JSON simple
            data = request.get_json()
            auteur_nom = data.get("auteur_nom")
            auteur_role = data.get("auteur_role")
            contenu = data.get("contenu", "").strip()

        if not auteur_nom or not auteur_role:
            return jsonify({"error": "L'auteur et le rôle sont requis"}), 400

        # Les invités ne peuvent pas ajouter de messages
        if auteur_role.lower() == "invite":
            return jsonify({"error": "Accès refusé: Les invités ne peuvent pas ajouter de messages"}), 403

        # Vérifier qu'il y a au moins du contenu OU des fichiers
        files = request.files.getlist('files') if 'files' in request.files else []
        if not contenu and len(files) == 0:
            return jsonify({"error": "Le message doit contenir du texte ou des fichiers"}), 400

        # Créer le message
        message = MessageProjet(
            project_id=project_id,
            auteur_nom=auteur_nom,
            auteur_role=auteur_role,
            contenu=contenu or ''  # Vide si seulement des fichiers
        )

        db.session.add(message)
        db.session.flush()  # Pour obtenir l'ID du message

        # Gérer les fichiers joints s'ils existent
        fichiers_ajoutes = []
        if files:
            upload_folder = app.config["UPLOAD_FOLDER"]
            os.makedirs(upload_folder, exist_ok=True)

            for file in files:
                if file and file.filename:
                    # Sécuriser et générer un nom unique
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # Ajout de microsecondes pour unicité
                    unique_filename = f"MSG_{timestamp}_{filename}"
                    filepath = os.path.join(upload_folder, unique_filename)

                    # Sauvegarder le fichier
                    file.save(filepath)

                    # Créer l'entrée dans la table fichiers_message
                    fichier_message = FichierMessage(
                        message_id=message.id,
                        nom_fichier=unique_filename,
                        nom_original=file.filename,
                        taille_fichier=os.path.getsize(filepath)
                    )
                    db.session.add(fichier_message)
                    fichiers_ajoutes.append(file.filename)

        db.session.commit()

        # Ajouter une entrée dans l'historique
        hist_text = "Message ajouté dans la discussion"
        if len(fichiers_ajoutes) > 0:
            hist_text += f" (avec {len(fichiers_ajoutes)} fichier(s) joint(s))"

        hist = Historique(
            project_id=project_id,
            action=hist_text,
            auteur=auteur_nom,
            role=auteur_role
        )
        db.session.add(hist)
        db.session.commit()

        # ============ NOTIFICATION POUR NOUVEAU MESSAGE ============
        try:
            projet_titre = project.titre[:40] + "..." if len(project.titre) > 40 else project.titre
            lien_projet = f"/project/{project_id}"

            # Notifier selon l'auteur du message
            if auteur_role == "soumissionnaire":
                # Soumissionnaire envoie → notifier évaluateur et secrétariat
                if project.evaluateur_nom:
                    notify_user_by_username(
                        project.evaluateur_nom,
                        "nouveau_message",
                        "Nouveau message",
                        f"Nouveau message du soumissionnaire sur '{projet_titre}'.",
                        project_id,
                        lien_projet
                    )
                notify_users_by_role(
                    "secretariatsct",
                    "nouveau_message",
                    "Nouveau message",
                    f"Nouveau message du soumissionnaire sur '{projet_titre}'.",
                    project_id,
                    lien_projet
                )
            else:
                # Personnel DGPPE envoie → notifier le soumissionnaire
                notify_project_owner(
                    project,
                    "nouveau_message",
                    "Nouveau message",
                    f"Nouveau message sur votre projet '{projet_titre}'.",
                    lien_projet
                )

            db.session.commit()
        except Exception as notif_error:
            print(f"[NOTIFICATION] Erreur message: {notif_error}")

        # ============ ENVOI D'EMAIL POUR NOUVEAU MESSAGE ============
        try:
            # Envoyer un email si le personnel DGPPE envoie un message au soumissionnaire
            if auteur_role != "soumissionnaire" and project.auteur_nom:
                soumissionnaire = User.query.filter_by(username=project.auteur_nom).first()
                if soumissionnaire and soumissionnaire.email:
                    email_service.send_new_message_email(
                        project=project,
                        user_email=soumissionnaire.email,
                        user_name=soumissionnaire.nom or soumissionnaire.username,
                        message_author=auteur_nom
                    )
        except Exception as email_error:
            print(f"[EMAIL] Erreur lors de l'envoi d'email pour nouveau message: {email_error}")

        return jsonify({
            "message": "Message ajouté avec succès",
            "data": message.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<int:project_id>/messages/<int:message_id>", methods=["PUT"])
def edit_project_message(project_id, message_id):
    """Éditer un message (auteur uniquement, dans les 15 minutes)"""
    try:
        from models import MessageProjet, HistoriqueMessage
        from datetime import datetime, timedelta

        # Récupérer le message
        message = MessageProjet.query.filter_by(id=message_id, project_id=project_id).first_or_404()

        # Récupérer les données
        data = request.get_json()
        auteur_nom = data.get("auteur_nom")
        nouveau_contenu = data.get("contenu", "").strip()

        # Vérifications
        if not auteur_nom or not nouveau_contenu:
            return jsonify({"error": "Données manquantes"}), 400

        # Seul l'auteur peut éditer son message
        if auteur_nom != message.auteur_nom:
            return jsonify({"error": "Seul l'auteur peut éditer son message"}), 403

        # Vérifier que le message n'est pas masqué
        if message.masque:
            return jsonify({"error": "Impossible d'éditer un message masqué"}), 403

        # Vérifier la fenêtre de 15 minutes
        temps_ecoule = datetime.utcnow() - message.date_creation
        if temps_ecoule > timedelta(minutes=15):
            return jsonify({"error": "Vous ne pouvez plus éditer ce message (délai de 15 minutes dépassé)"}), 403

        # Sauvegarder l'historique
        historique = HistoriqueMessage(
            message_id=message.id,
            project_id=project_id,
            contenu_avant=message.contenu,
            contenu_apres=nouveau_contenu,
            modifie_par=auteur_nom,
            type_modification='edition'
        )
        db.session.add(historique)

        # Mettre à jour le message
        message.contenu = nouveau_contenu
        message.date_modification = datetime.utcnow()
        message.modifie_par = auteur_nom

        db.session.commit()

        return jsonify({
            "message": "Message modifié avec succès",
            "data": message.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<int:project_id>/messages/<int:message_id>/mask", methods=["POST"])
def mask_project_message(project_id, message_id):
    """Masquer un message (admin/secrétariat uniquement)"""
    try:
        from models import MessageProjet, HistoriqueMessage
        from datetime import datetime

        # Récupérer le message
        message = MessageProjet.query.filter_by(id=message_id, project_id=project_id).first_or_404()

        # Récupérer les données
        data = request.get_json()
        auteur_nom = data.get("auteur_nom")
        role = data.get("role", "").lower()
        raison = data.get("raison", "").strip()

        # Vérifications
        if not auteur_nom or not raison:
            return jsonify({"error": "Username et raison obligatoires"}), 400

        # Seuls les admins et le secrétariat peuvent masquer
        roles_autorises = ["admin", "secretariatsct", "secretariatcomite"]
        if role not in roles_autorises:
            return jsonify({"error": "Vous n'avez pas la permission de masquer des messages"}), 403

        # Vérifier que le message n'est pas déjà masqué
        if message.masque:
            return jsonify({"error": "Ce message est déjà masqué"}), 400

        # Sauvegarder l'historique
        historique = HistoriqueMessage(
            message_id=message.id,
            project_id=project_id,
            contenu_avant=message.contenu,
            contenu_apres="[Message masqué]",
            modifie_par=auteur_nom,
            type_modification='masquage',
            raison=raison
        )
        db.session.add(historique)

        # Masquer le message
        message.masque = True
        message.masque_par = auteur_nom
        message.masque_raison = raison
        message.date_masquage = datetime.utcnow()

        # Ajouter une entrée dans l'historique du projet
        hist = Historique(
            project_id=project_id,
            action=f"Message masqué par {role}: {raison[:100]}",
            auteur=auteur_nom,
            role=role
        )
        db.session.add(hist)

        db.session.commit()

        return jsonify({
            "message": "Message masqué avec succès",
            "data": message.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<int:project_id>/messages/<int:message_id>/unmask", methods=["POST"])
def unmask_project_message(project_id, message_id):
    """Démasquer un message (admin/secrétariat uniquement)"""
    try:
        from models import MessageProjet, HistoriqueMessage
        from datetime import datetime

        # Récupérer le message
        message = MessageProjet.query.filter_by(id=message_id, project_id=project_id).first_or_404()

        # Récupérer les données
        data = request.get_json()
        auteur_nom = data.get("auteur_nom")
        role = data.get("role", "").lower()
        raison = data.get("raison", "").strip()

        # Vérifications
        if not auteur_nom:
            return jsonify({"error": "Username obligatoire"}), 400

        # Seuls les admins et le secrétariat peuvent démasquer
        roles_autorises = ["admin", "secretariatsct", "secretariatcomite"]
        if role not in roles_autorises:
            return jsonify({"error": "Vous n'avez pas la permission de démasquer des messages"}), 403

        # Vérifier que le message est masqué
        if not message.masque:
            return jsonify({"error": "Ce message n'est pas masqué"}), 400

        # Sauvegarder l'historique
        historique = HistoriqueMessage(
            message_id=message.id,
            project_id=project_id,
            contenu_avant="[Message masqué]",
            contenu_apres=message.contenu,
            modifie_par=auteur_nom,
            type_modification='demasquage',
            raison=raison or "Démasquage par l'administration"
        )
        db.session.add(historique)

        # Démasquer le message
        message.masque = False
        message.masque_par = None
        message.masque_raison = None
        message.date_masquage = None

        # Ajouter une entrée dans l'historique du projet
        hist = Historique(
            project_id=project_id,
            action=f"Message démasqué par {role}",
            auteur=auteur_nom,
            role=role
        )
        db.session.add(hist)

        db.session.commit()

        return jsonify({
            "message": "Message démasqué avec succès",
            "data": message.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<int:project_id>/messages/<int:message_id>/history", methods=["GET"])
def get_message_history(project_id, message_id):
    """Récupérer l'historique des modifications d'un message"""
    try:
        from models import HistoriqueMessage

        # Vérifier que le message existe
        message = MessageProjet.query.filter_by(id=message_id, project_id=project_id).first_or_404()

        # Récupérer l'historique
        historique = HistoriqueMessage.query.filter_by(message_id=message_id).order_by(HistoriqueMessage.date_modification.desc()).all()

        return jsonify({
            "message": message.to_dict(),
            "historique": [h.to_dict() for h in historique]
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<int:project_id>/messages/<int:message_id>", methods=["DELETE"])
def delete_project_message(project_id, message_id):
    """Supprimer un message - OBSOLÈTE - utiliser le masquage à la place"""
    return jsonify({"error": "La suppression de messages est désactivée. Utilisez le masquage à la place."}), 403

# ============ Route des métriques de performance ============
@app.route('/api/metrics', methods=['GET'])
@app.route('/api/performance-metrics', methods=['GET'])  # Alias pour compatibilité frontend
def get_performance_metrics():
    """
    Calcule les métriques de performance basées sur les logs réels:
    - Temps moyen de traitement: du projet soumis à décision finale (ou depuis compléments fournis si applicable)
    - Taux de validation: ratio projets favorables / total évalués
    - Délai moyen d'évaluation: de l'assignation à la validation secrétariat (projets évaluables uniquement)
    """
    try:
        # 1. TEMPS MOYEN DE TRAITEMENT
        # Projets avec décision finale
        projects_with_decision = Project.query.filter(
            Project.decision_finale.in_(['confirme', 'infirme'])
        ).all()

        total_processing_days = 0
        processing_count = 0

        for projet in projects_with_decision:
            # Chercher la date de décision finale dans les logs
            decision_log = Historique.query.filter_by(
                project_id=projet.id
            ).filter(
                Historique.action.like('%décision finale%')
            ).order_by(Historique.date_action.desc()).first()

            if not decision_log:
                continue

            # Chercher la date de départ
            # Si le projet a eu des compléments, on part de la soumission des compléments
            complements_log = Historique.query.filter_by(
                project_id=projet.id
            ).filter(
                Historique.action.like('%compléments fournis%')
            ).order_by(Historique.date_action.desc()).first()

            if complements_log:
                start_date = complements_log.date_action
            elif projet.date_soumission:
                start_date = projet.date_soumission
            else:
                continue

            # Calculer la différence en jours
            if decision_log.date_action and start_date:
                delta = decision_log.date_action - start_date
                total_processing_days += delta.days
                processing_count += 1

        avg_processing_time = round(total_processing_days / processing_count) if processing_count > 0 else 0

        # 2. TAUX DE VALIDATION
        # Projets avec évaluation finale
        projects_evaluated = Project.query.filter(
            Project.decision_finale.in_(['confirme', 'infirme'])
        ).all()

        favorable_count = sum(1 for p in projects_evaluated
                             if p.decision_finale == 'confirme')
        total_evaluated = len(projects_evaluated)

        validation_rate = round((favorable_count / total_evaluated) * 100) if total_evaluated > 0 else 0

        # 3. DÉLAI MOYEN D'ÉVALUATION
        # Projets évalués (uniquement ceux jugés évaluables, pas ceux avec compléments demandés)
        projects_evaluated_direct = Project.query.filter(
            Project.statut.in_(['évalué', 'validé par secrétariat', 'en attente validation presidencesct', 'validé par presidencesct', 'approuvé'])
        ).all()

        total_evaluation_days = 0
        evaluation_count = 0

        for projet in projects_evaluated_direct:
            # Chercher la date de validation (transmission à secrétariat)
            validation_log = Historique.query.filter_by(
                project_id=projet.id
            ).filter(
                db.or_(
                    Historique.action.like('%transmis au secrétariat%'),
                    Historique.action.like('%fiche d\'évaluation validée%'),
                    Historique.action.like('%statut: évalué%')
                )
            ).order_by(Historique.date_action.asc()).first()

            # Chercher la date d'assignation
            assignation_log = Historique.query.filter_by(
                project_id=projet.id
            ).filter(
                db.or_(
                    Historique.action.like('%assigné à%'),
                    Historique.action.like('%statut: assigné%')
                )
            ).order_by(Historique.date_action.asc()).first()

            if validation_log and assignation_log and validation_log.date_action and assignation_log.date_action:
                delta = validation_log.date_action - assignation_log.date_action
                total_evaluation_days += delta.days
                evaluation_count += 1

        avg_evaluation_time = round(total_evaluation_days / evaluation_count) if evaluation_count > 0 else 0

        return jsonify({
            "averageProcessingTime": f"{avg_processing_time} jours",
            "validationRate": validation_rate,
            "averageEvaluationTime": f"{avg_evaluation_time} jours",
            "stats": {
                "projectsWithDecision": processing_count,
                "totalEvaluated": total_evaluated,
                "favorableCount": favorable_count,
                "evaluatedDirect": evaluation_count
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "averageProcessingTime": "0 jours",
            "validationRate": 0,
            "averageEvaluationTime": "0 jours"
        }), 500

@app.route('/api/stats/rapport-pdf', methods=['GET'])
def generer_rapport_statistiques():
    """Génère un rapport PDF complet des statistiques de la plateforme"""
    try:
        # Récupérer toutes les statistiques
        total_projets = Project.query.count()
        projets_soumis = Project.query.filter_by(statut='soumis').count()
        projets_en_evaluation = Project.query.filter(
            Project.statut.in_(['assigné', 'en évaluation', 'validé'])
        ).count()
        projets_approuves = Project.query.filter_by(statut='approuvé').count()
        projets_rejetes = Project.query.filter_by(statut='rejeté').count()

        # Statistiques par secteur
        from sqlalchemy import func
        stats_secteurs = db.session.query(
            Project.secteur,
            func.count(Project.id).label('count'),
            func.sum(Project.cout_estimatif).label('total_cout')
        ).group_by(Project.secteur).all()

        # Statistiques par pôle (répartition équitable pour projets multi-pôles)
        # Séparer les pôles multiples et répartir équitablement
        import re
        stats_poles_dict = {}
        all_projects = Project.query.all()

        for project in all_projects:
            poles_str = project.poles or 'Non spécifié'

            # Séparer les pôles en utilisant une regex qui split sur "),nom"
            # Cela évite de splitter les virgules à l'intérieur des parenthèses
            # Ex: "Sud (Zig, Sed),Nord (SL)" -> ["Sud (Zig, Sed)", "Nord (SL)"]
            if '),' in poles_str:
                # Utiliser regex pour splitter sur "),
                poles_list = re.split(r'\),\s*', poles_str)
                # Ajouter la parenthèse fermante manquante (sauf pour le dernier)
                poles_list = [p + ')' if not p.endswith(')') else p for p in poles_list]
            else:
                # Pas de multi-pôles, garder tel quel
                poles_list = [poles_str]

            poles_list = [p.strip() for p in poles_list if p.strip()]

            if not poles_list:
                poles_list = ['Non spécifié']

            # Répartir équitablement entre les pôles
            nb_poles = len(poles_list)
            cout_par_pole = (project.cout_estimatif or 0) / nb_poles

            for pole in poles_list:
                if pole not in stats_poles_dict:
                    stats_poles_dict[pole] = {'count': 0, 'cout': 0}

                # Compter la fraction du projet
                stats_poles_dict[pole]['count'] += 1 / nb_poles
                stats_poles_dict[pole]['cout'] += cout_par_pole

        # Convertir en liste pour le PDF
        stats_poles = [(pole, data['count'], data['cout'])
                       for pole, data in stats_poles_dict.items()]

        # Créer le PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        # Conteneur pour les éléments du PDF
        elements = []
        styles = getSampleStyleSheet()

        # Style personnalisé pour le titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=1  # Centre
        )

        # Style pour les sous-titres
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12
        )

        # En-tête avec logo (identique au site)
        logo_path = os.path.join(os.path.dirname(__file__), 'static', 'logo-dgppe.png')

        # Créer un tableau pour l'en-tête avec logo et textes
        if os.path.exists(logo_path):
            logo = RLImage(logo_path, width=1.8*cm, height=1.8*cm)

            # Styles pour les textes de l'en-tête
            ministry_style = ParagraphStyle(
                'MinistryStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#2c3e50'),
                fontName='Helvetica-Bold'
            )

            direction_style = ParagraphStyle(
                'DirectionStyle',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#5a6c7d')
            )

            platform_style = ParagraphStyle(
                'PlatformStyle',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#1e40af'),
                fontName='Helvetica-Bold'
            )

            # Tableau pour l'en-tête
            header_data = [[
                logo,
                Paragraph("Ministère de l'Économie, du Plan et de la Coopération<br/>" +
                         "<font size=9 color='#5a6c7d'>Direction Générale de la Planification des Politiques Économiques</font><br/>" +
                         "<font size=11 color='#1e40af'><b>Plateforme de Maturation des Projets Publics</b></font>",
                         ministry_style)
            ]]

            header_table = Table(header_data, colWidths=[2.2*cm, 14*cm])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))

            elements.append(header_table)
        else:
            # Fallback si le logo n'existe pas
            elements.append(Paragraph("Ministère de l'Économie, du Plan et de la Coopération", title_style))
            elements.append(Paragraph("Direction Générale de la Planification des Politiques Économiques", styles['Normal']))
            elements.append(Paragraph("Plateforme de Maturation des Projets Publics", styles['Normal']))

        elements.append(Spacer(1, 0.8*cm))

        # Ligne de séparation
        line_table = Table([['']], colWidths=[17*cm])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#1e40af')),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 0.8*cm))

        # Titre du rapport
        elements.append(Paragraph("RAPPORT DE STATISTIQUES", title_style))
        elements.append(Paragraph(f"Période : {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        elements.append(Spacer(1, 1*cm))

        # 1. Vue d'ensemble
        elements.append(Paragraph("1. VUE D'ENSEMBLE DES PROJETS", subtitle_style))

        data_overview = [
            ['Indicateur', 'Nombre', 'Pourcentage'],
            ['Total des projets', str(total_projets), '100%'],
            ['Projets soumis', str(projets_soumis), f'{round(projets_soumis/total_projets*100 if total_projets > 0 else 0, 1)}%'],
            ['Projets en évaluation', str(projets_en_evaluation), f'{round(projets_en_evaluation/total_projets*100 if total_projets > 0 else 0, 1)}%'],
            ['Projets approuvés', str(projets_approuves), f'{round(projets_approuves/total_projets*100 if total_projets > 0 else 0, 1)}%'],
            ['Projets rejetés', str(projets_rejetes), f'{round(projets_rejetes/total_projets*100 if total_projets > 0 else 0, 1)}%'],
        ]

        table_overview = Table(data_overview, colWidths=[8*cm, 3*cm, 3*cm])
        table_overview.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table_overview)
        elements.append(Spacer(1, 1*cm))

        # 2. Répartition par secteur
        elements.append(Paragraph("2. RÉPARTITION PAR SECTEUR", subtitle_style))

        data_secteurs = [['Secteur', 'Nombre de projets', 'Coût estimatif (FCFA)']]
        for secteur, count, cout in stats_secteurs:
            cout_str = f'{int(cout):,}' if cout else '0'
            data_secteurs.append([secteur or 'Non spécifié', str(count), cout_str])

        table_secteurs = Table(data_secteurs, colWidths=[7*cm, 4*cm, 5*cm])
        table_secteurs.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table_secteurs)
        elements.append(Spacer(1, 1*cm))

        # 3. Répartition par pôle territorial
        elements.append(Paragraph("3. RÉPARTITION PAR PÔLE TERRITORIAL", subtitle_style))

        data_poles = [['Pôle Territorial', 'Nombre de projets', 'Coût estimatif (FCFA)']]
        for pole, count, cout in stats_poles:
            cout_str = f'{int(cout):,}' if cout else '0'
            # Afficher le nombre avec 1 décimale si fractionnaire
            count_str = f'{count:.1f}' if count != int(count) else str(int(count))
            data_poles.append([pole or 'Non spécifié', count_str, cout_str])

        table_poles = Table(data_poles, colWidths=[7*cm, 4*cm, 5*cm])
        table_poles.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table_poles)
        elements.append(Spacer(1, 1*cm))

        # Pied de page
        elements.append(Spacer(1, 2*cm))
        elements.append(Paragraph("_______________________________________________", styles['Normal']))
        elements.append(Paragraph(f"Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles['Normal']))
        elements.append(Paragraph("Direction Générale de la Planification des Politiques Économiques (DGPPE)", styles['Normal']))

        # Construire le PDF
        doc.build(elements)

        # Préparer la réponse
        buffer.seek(0)
        filename = f"rapport_statistiques_dgppe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/rapport-elabore", methods=["GET"])
def generer_rapport_elabore():
    """Génère un rapport PDF élaboré avec analyses IA"""
    try:
        from ai_rapport_generator import (
            generer_resume_executif, analyser_tendances,
            analyser_finances, generer_insights, format_montant
        )

        # Récupérer tous les projets
        all_projects = Project.query.all()

        # Générer les analyses
        resume = generer_resume_executif(all_projects)
        tendances = analyser_tendances(all_projects)
        finances = analyser_finances(all_projects)
        insights = generer_insights(all_projects)

        # Créer le PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        elements = []
        styles = getSampleStyleSheet()

        # Styles personnalisés
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=1
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12
        )

        # En-tête avec logo
        logo_path = os.path.join(os.path.dirname(__file__), 'static', 'logo-dgppe.png')

        if os.path.exists(logo_path):
            logo = RLImage(logo_path, width=1.8*cm, height=1.8*cm)

            header_data = [[
                logo,
                Paragraph("Ministère de l'Économie, du Plan et de la Coopération<br/>" +
                         "<font size=9 color='#5a6c7d'>Direction Générale de la Planification des Politiques Économiques</font><br/>" +
                         "<font size=11 color='#1e40af'><b>Plateforme de Maturation des Projets Publics</b></font>",
                         styles['Normal'])
            ]]

            header_table = Table(header_data, colWidths=[2.2*cm, 14*cm])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            elements.append(header_table)

        elements.append(Spacer(1, 0.8*cm))

        # Ligne de séparation
        line_table = Table([['']], colWidths=[17*cm])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#1e40af')),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 0.8*cm))

        # Titre
        elements.append(Paragraph("RAPPORT ANALYTIQUE ÉLABORÉ", title_style))
        elements.append(Paragraph(f"Période : {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        elements.append(Spacer(1, 1*cm))

        # 1. RÉSUMÉ EXÉCUTIF
        elements.append(Paragraph("1. RÉSUMÉ EXÉCUTIF", subtitle_style))
        elements.append(Paragraph(resume, styles['BodyText']))
        elements.append(Spacer(1, 0.8*cm))

        # 2. ANALYSE DE TENDANCES
        elements.append(Paragraph("2. ANALYSE DE TENDANCES", subtitle_style))

        # Évolution temporelle
        if 'texte' in tendances['evolution']:
            elements.append(Paragraph(f"<b>Évolution récente :</b> {tendances['evolution']['texte']}", styles['BodyText']))

        # Secteur dominant
        if 'dominant' in tendances['secteurs_croissance']:
            dom = tendances['secteurs_croissance']['dominant']
            elements.append(Paragraph(
                f"<b>Secteur dominant :</b> {dom['nom']} avec {dom['nombre']} projet(s) " +
                f"({dom['pourcentage']}% du total), représentant {format_montant(dom['cout_total'])} FCFA.",
                styles['BodyText']
            ))

        # Pôles sous-représentés
        if tendances['poles_sous_representes']:
            poles_texte = ", ".join([f"{pole} ({count} projets)" for pole, count in tendances['poles_sous_representes']])
            elements.append(Paragraph(
                f"<b>Pôles sous-représentés :</b> {poles_texte}",
                styles['BodyText']
            ))

        elements.append(Spacer(1, 0.8*cm))

        # 3. ANALYSE FINANCIÈRE
        elements.append(Paragraph("3. ANALYSE FINANCIÈRE", subtitle_style))

        elements.append(Paragraph(
            f"<b>Coût total demandé :</b> {format_montant(finances['cout_total'])} FCFA",
            styles['BodyText']
        ))
        elements.append(Paragraph(
            f"<b>Coût moyen par projet :</b> {format_montant(finances['cout_moyen'])} FCFA",
            styles['BodyText']
        ))
        elements.append(Paragraph(
            f"<b>Coût médian :</b> {format_montant(finances['cout_median'])} FCFA",
            styles['BodyText']
        ))

        # Distribution
        elements.append(Paragraph("<b>Répartition par tranches de coûts :</b>", styles['BodyText']))
        for tranche, count in finances['distribution'].items():
            elements.append(Paragraph(f"  • {tranche} : {count} projet(s)", styles['BodyText']))

        # Concentration
        if 'top3_secteurs' in finances['concentration']:
            elements.append(Paragraph(
                f"<b>Concentration :</b> Les 3 principaux secteurs représentent {finances['concentration']['pourcentage']}% du coût total.",
                styles['BodyText']
            ))

        elements.append(Spacer(1, 0.8*cm))

        # 4. INSIGHTS STRATÉGIQUES
        elements.append(Paragraph("4. INSIGHTS STRATÉGIQUES", subtitle_style))

        for insight in insights:
            elements.append(Paragraph(f"• {insight}", styles['BodyText']))
            elements.append(Spacer(1, 0.3*cm))

        elements.append(Spacer(1, 1*cm))

        # Pied de page
        elements.append(Spacer(1, 2*cm))
        elements.append(Paragraph("_______________________________________________", styles['Normal']))
        elements.append(Paragraph(f"Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles['Normal']))
        elements.append(Paragraph("Direction Générale de la Planification des Politiques Économiques (DGPPE)", styles['Normal']))

        # Construire le PDF
        doc.build(elements)

        buffer.seek(0)
        filename = f"rapport_elabore_dgppe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/sync-project-avis", methods=["POST"])
def sync_project_avis():
    """
    Synchronise l'avis de tous les projets avec leurs fiches d'évaluation
    Route d'administration pour corriger les désynchronisations
    """
    try:
        # Sécurité : vérifier que c'est un admin (optionnel)
        # Pour l'instant, on permet l'exécution sans authentification car c'est temporaire

        synced_count = 0
        errors = []

        # Récupérer tous les projets qui ont une fiche d'évaluation
        projects = Project.query.all()

        for project in projects:
            fiche = FicheEvaluation.query.filter_by(project_id=project.id).first()

            if fiche and fiche.proposition:
                # Si l'avis du projet diffère de la proposition de la fiche
                if project.avis != fiche.proposition:
                    old_avis = project.avis
                    project.avis = fiche.proposition
                    synced_count += 1

                    print(f"[SYNC] Projet {project.numero_projet}: {old_avis} → {fiche.proposition}")

        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"{synced_count} projet(s) synchronisé(s)",
            "synced_count": synced_count
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/fix-avis-terminologie", methods=["POST"])
def fix_avis_terminology_route():
    """
    Route pour corriger la terminologie des avis en base de données
    Remplace 'favorable sous réserve' par 'favorable sous conditions'
    """
    try:
        count_projects = 0
        count_fiches = 0

        # 1. Corriger les avis des projets
        projects = Project.query.filter(
            db.or_(
                Project.avis.like('%favorable sous réserve%'),
                Project.avis.like('%favorable sous reserve%')
            )
        ).all()

        for project in projects:
            old_avis = project.avis
            if old_avis:
                new_avis = old_avis.replace('favorable sous réserve', 'favorable sous conditions')
                new_avis = new_avis.replace('favorable sous reserve', 'favorable sous conditions')
                new_avis = new_avis.replace('Favorable sous réserve', 'Favorable sous conditions')

                if new_avis != old_avis:
                    project.avis = new_avis
                    count_projects += 1

        # 2. Corriger les propositions des fiches d'évaluation
        fiches = FicheEvaluation.query.filter(
            db.or_(
                FicheEvaluation.proposition.like('%favorable sous réserve%'),
                FicheEvaluation.proposition.like('%favorable sous reserve%')
            )
        ).all()

        for fiche in fiches:
            old_prop = fiche.proposition
            if old_prop:
                new_prop = old_prop.replace('favorable sous réserve', 'favorable sous conditions')
                new_prop = new_prop.replace('favorable sous reserve', 'favorable sous conditions')
                new_prop = new_prop.replace('Favorable sous réserve', 'Favorable sous conditions')

                if new_prop != old_prop:
                    fiche.proposition = new_prop
                    count_fiches += 1

        # 3. Commit les changements
        if count_projects > 0 or count_fiches > 0:
            db.session.commit()

        return jsonify({
            "success": True,
            "projects_fixed": count_projects,
            "fiches_fixed": count_fiches,
            "message": f"{count_projects} projet(s) et {count_fiches} fiche(s) corrigé(s)"
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# Import and register evaluation routes
try:
    from routes.evaluation_routes import evaluation_bp
    app.register_blueprint(evaluation_bp, url_prefix='')
    print("Evaluation routes registered successfully")
except ImportError as e:
    print(f"Warning: Could not import evaluation routes: {e}")

# Import and register project routes
try:
    from routes.project_routes import register_project_routes
    register_project_routes(app, Project, FicheEvaluation, db, User, Historique)
    print("Project routes registered successfully")
except ImportError as e:
    print(f"Warning: Could not import project routes: {e}")

# Import and register user routes
try:
    from routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix='')
    print("User routes registered successfully")
except ImportError as e:
    print(f"Warning: Could not import user routes: {e}")

# Import and register point focal routes
try:
    from routes.point_focal_routes import point_focal_bp
    app.register_blueprint(point_focal_bp, url_prefix='')
    print("Point focal routes registered successfully")
except ImportError as e:
    print(f"Warning: Could not import point focal routes: {e}")

# Import and register formulaire config routes
try:
    from routes.formulaire_config_routes import formulaire_config_bp
    app.register_blueprint(formulaire_config_bp, url_prefix='')
    print("Formulaire config routes registered successfully")
except ImportError as e:
    print(f"Warning: Could not import formulaire config routes: {e}")

# Import and register ministere routes
try:
    from routes.ministere_routes import ministere_bp
    app.register_blueprint(ministere_bp, url_prefix='')
    print("Ministere routes registered successfully")
except ImportError as e:
    print(f"Warning: Could not import ministere routes: {e}")

# Import and register notification routes
try:
    from routes.notification_routes import notification_bp
    app.register_blueprint(notification_bp, url_prefix='')
    print("Notification routes registered successfully")
except ImportError as e:
    print(f"Warning: Could not import notification routes: {e}")

# Import and register contact routes
try:
    from routes.contact_routes import contact_bp
    app.register_blueprint(contact_bp, url_prefix='')
    print("Contact routes registered successfully")
except ImportError as e:
    print(f"Warning: Could not import contact routes: {e}")

# Import and register export routes
try:
    from routes.export_routes import export_bp
    app.register_blueprint(export_bp, url_prefix='')
    print("Export routes registered successfully")
except ImportError as e:
    print(f"Warning: Could not import export routes: {e}")

# Import and register versioning routes
try:
    from routes.versioning_routes import versioning_bp
    app.register_blueprint(versioning_bp, url_prefix='')
    print("Versioning routes registered successfully")
except ImportError as e:
    print(f"Warning: Could not import versioning routes: {e}")

# Import and register admin routes
try:
    from routes.admin_routes import register_admin_routes
    register_admin_routes(app, db)
    print("Admin routes registered successfully")
except ImportError as e:
    print(f"Warning: Could not import admin routes: {e}")

@app.route("/api/version", methods=["GET"])
def get_version():
    """Retourne la version du code backend déployé"""
    return jsonify({
        "version": "2025-12-04-recommandations-fix-v3",
        "commit": "255f5db",
        "description": "Fix recommandations avec flush stdout - FORCE RELOAD",
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/admin/reload-modules", methods=["POST"])
def reload_modules():
    """Force le rechargement des modules Python (workaround pour Gunicorn cache)"""
    try:
        import sys
        import importlib

        # Recharger le module project_routes
        if 'routes.project_routes' in sys.modules:
            importlib.reload(sys.modules['routes.project_routes'])
            return jsonify({"message": "Module project_routes rechargé avec succès!"}), 200
        else:
            return jsonify({"message": "Module project_routes pas encore chargé"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/run-migration", methods=["POST"])
def run_migration():
    """Execute the migration script to add motivation_resoumission column"""
    try:
        from sqlalchemy import text

        # Vérifier si la colonne existe déjà
        result = db.session.execute(text("PRAGMA table_info(project)"))
        columns = [row[1] for row in result.fetchall()]

        if 'motivation_resoumission' in columns:
            return jsonify({"message": "La colonne 'motivation_resoumission' existe déjà."}), 200

        # Ajouter la colonne
        db.session.execute(text(
            "ALTER TABLE project ADD COLUMN motivation_resoumission TEXT"
        ))
        db.session.commit()

        return jsonify({"message": "Colonne 'motivation_resoumission' ajoutée avec succès!"}), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/fix-stale-decision-finale", methods=["POST"])
def fix_stale_decision_finale_endpoint():
    """Endpoint temporaire pour corriger les decision_finale obsolètes"""
    try:
        # Trouver les projets concernés
        projets = Project.query.filter(
            Project.statut == 'validé par presidencesct',
            Project.avis_presidencesct == 'valide',
            Project.decision_finale.isnot(None)
        ).all()

        if not projets:
            return jsonify({"message": "Aucun projet à corriger"}), 200

        corrections = []
        for projet in projets:
            old_decision = projet.decision_finale

            # Réinitialiser decision_finale et commentaires_finaux
            projet.decision_finale = None
            projet.commentaires_finaux = None

            # Ajouter une entrée dans l'historique
            hist = Historique(
                project_id=projet.id,
                action=f"Migration: Réinitialisation de decision_finale (ancienne valeur: '{old_decision}') pour permettre nouvelle décision du Comité",
                auteur="system",
                role="admin"
            )
            db.session.add(hist)

            corrections.append({
                "id": projet.id,
                "numero_projet": projet.numero_projet,
                "titre": projet.titre,
                "old_decision_finale": old_decision
            })

        db.session.commit()

        return jsonify({
            "message": f"{len(corrections)} projet(s) corrigé(s)",
            "projets_corriges": corrections
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/run-migrations", methods=["POST"])
def run_migrations_endpoint():
    """Endpoint pour exécuter manuellement les migrations de la base de données"""
    try:
        from migrate_flask import migrate_with_flask_db

        print(f"[API] Exécution manuelle de la migration Flask-native")
        success = migrate_with_flask_db(db)

        if success:
            return jsonify({
                "message": "Migrations exécutées avec succès"
            }), 200
        else:
            return jsonify({
                "error": "Échec de la migration (voir logs serveur)"
            }), 500

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/migrate-approuve-definitif", methods=["POST"])
def migrate_approuve_definitif_endpoint():
    """Endpoint pour migrer 'approuvé définitivement' vers l'avis réel"""
    try:
        print("[API] Démarrage de la migration 'approuvé définitivement' → avis réel")

        # Compter les projets concernés
        projets = Project.query.filter_by(statut="approuvé définitivement par le Comité").all()
        count = len(projets)

        if count == 0:
            return jsonify({
                "message": "Aucun projet avec le statut 'approuvé définitivement par le Comité'",
                "migrated": 0
            }), 200

        migrated = 0
        details = []

        for p in projets:
            old_statut = p.statut
            if p.avis:
                p.statut = p.avis
                details.append({
                    "id": p.id,
                    "numero": p.numero_projet,
                    "titre": p.titre,
                    "old_statut": old_statut,
                    "new_statut": p.avis
                })
                migrated += 1
            else:
                # Fallback si pas d'avis
                p.statut = "validé par presidencecomite"
                details.append({
                    "id": p.id,
                    "numero": p.numero_projet,
                    "titre": p.titre,
                    "old_statut": old_statut,
                    "new_statut": "validé par presidencecomite (fallback)"
                })
                migrated += 1

        db.session.commit()

        print(f"[API] ✅ Migration terminée: {migrated} projet(s) migré(s)")
        for d in details:
            print(f"  - [{d['numero']}] {d['old_statut']} → {d['new_statut']}")

        return jsonify({
            "message": f"Migration réussie: {migrated} projet(s) migré(s)",
            "migrated": migrated,
            "details": details
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/fix-fiche-visible", methods=["POST"])
def fix_fiche_visible():
    """
    Endpoint pour corriger manuellement fiche_evaluation_visible
    Met à jour tous les projets avec decision_finale='confirme'
    """
    try:
        print("[ADMIN] Correction de fiche_evaluation_visible...")

        # Trouver tous les projets avec decision_finale='confirme' mais fiche_evaluation_visible=False
        projects = Project.query.filter_by(decision_finale='confirme').all()

        updated = []
        for p in projects:
            if not p.fiche_evaluation_visible:
                p.fiche_evaluation_visible = True
                updated.append({
                    'id': p.id,
                    'numero': p.numero_projet,
                    'titre': p.titre,
                    'statut': p.statut
                })

        db.session.commit()

        print(f"[ADMIN] ✅ {len(updated)} projet(s) mis à jour")
        for u in updated:
            print(f"  - [{u['numero']}] {u['titre']}")

        return jsonify({
            "message": f"{len(updated)} projet(s) mis à jour avec fiche_evaluation_visible=True",
            "updated": len(updated),
            "projects": updated
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/delete-test-projects", methods=["POST"])
def delete_test_projects():
    """
    Endpoint pour supprimer tous les projets soumis par 'soumissionnaire' sans numéro
    """
    try:
        print("[ADMIN] Suppression des projets de test (soumissionnaire sans numéro)...")

        # Trouver tous les projets soumis par 'soumissionnaire' sans numéro
        projects = Project.query.filter_by(auteur_nom='soumissionnaire').filter(
            (Project.numero_projet == None) | (Project.numero_projet == '')
        ).all()

        deleted = []
        for project in projects:
            deleted.append({
                'id': project.id,
                'numero': project.numero_projet,
                'titre': project.titre
            })

            # Supprimer les relations d'abord (fiches, historique, etc.)
            FicheEvaluation.query.filter_by(project_id=project.id).delete()
            Historique.query.filter_by(project_id=project.id).delete()
            DocumentProjet.query.filter_by(project_id=project.id).delete()
            MessageProjet.query.filter_by(project_id=project.id).delete()

            # Puis supprimer le projet
            db.session.delete(project)

        db.session.commit()

        print(f"[ADMIN] ✅ {len(deleted)} projet(s) de test supprimé(s)")
        for d in deleted:
            numero_display = d['numero'] or f"ID-{d['id']}"
            print(f"  - [{numero_display}] {d['titre']}")

        return jsonify({
            "message": f"{len(deleted)} projet(s) de test supprimé(s)",
            "deleted": len(deleted),
            "projects": deleted
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Endpoint pour créer des projets d'exemple (développement)
@app.route('/api/admin/creer-projets-exemple', methods=['POST'])
def creer_projets_exemple():
    """Créer 10 projets d'exemple pour tests"""
    try:
        from datetime import datetime

        # Liste des projets à créer (8 pôles territoriaux officiels)
        # Dakar, Thiès, Diourbel-Louga, Centre, Nord, Nord-Est, Sud-Est, Sud
        PROJETS_DATA = [
            {
                "titre": "Construction d'un centre de formation agricole moderne à Kaolack",
                "description": "Projet visant à créer un centre de formation équipé pour former 500 jeunes par an aux techniques agricoles modernes, à l'agro-écologie et à l'entrepreneuriat agricole. Le centre comprendra des salles de classe, un laboratoire, des champs d'application et un incubateur d'entreprises agricoles.",
                "secteur": "agriculture-élevage-pêche",
                "poles": "Centre",
                "cout_estimatif": 2500000000,
                "structure_soumissionnaire": "Direction Régionale du Développement Rural de Kaolack"
            },
            {
                "titre": "Aménagement hydro-agricole de la vallée du Saloum",
                "description": "Aménagement de 1000 hectares de terres agricoles avec système d'irrigation moderne, construction de digues anti-sel, et création de pistes de production. Le projet bénéficiera à 800 producteurs et permettra 3 cycles de culture par an.",
                "secteur": "agriculture-élevage-pêche",
                "poles": "Centre",
                "cout_estimatif": 8500000000,
                "structure_soumissionnaire": "Agence Nationale d'Aménagement du Territoire"
            },
            {
                "titre": "Électrification rurale par énergie solaire - Zone Nord",
                "description": "Installation de mini-centrales solaires et réseaux de distribution dans 45 villages de la zone Nord (Saint-Louis et Louga). Le projet vise à électrifier 15000 ménages et 200 équipements communautaires (écoles, centres de santé, mosquées).",
                "secteur": "énergie",
                "poles": "Nord",
                "cout_estimatif": 12000000000,
                "structure_soumissionnaire": "Agence Sénégalaise d'Électrification Rurale"
            },
            {
                "titre": "Construction de 10 collèges de proximité en zone rurale",
                "description": "Construction de 10 collèges d'enseignement moyen dans les zones rurales mal desservies de Tambacounda et Kédougou. Chaque établissement comprendra 12 salles de classe, un laboratoire, une bibliothèque, des logements pour enseignants et un terrain de sport. Capacité totale: 5000 élèves.",
                "secteur": "éducation-formation",
                "poles": "Sud-Est",
                "cout_estimatif": 15000000000,
                "structure_soumissionnaire": "Ministère de l'Éducation Nationale"
            },
            {
                "titre": "Modernisation du réseau d'adduction d'eau potable de Thiès",
                "description": "Réhabilitation et extension du réseau d'eau potable de la ville de Thiès: construction d'un nouveau réservoir de 10000m³, remplacement de 50km de canalisations vétustes, installation de 3000 nouveaux branchements sociaux, et mise en place d'un système de télégestion.",
                "secteur": "eau-assainissement",
                "poles": "Thiès",
                "cout_estimatif": 6800000000,
                "structure_soumissionnaire": "Société Nationale des Eaux du Sénégal"
            },
            {
                "titre": "Centre hospitalier régional spécialisé de Ziguinchor",
                "description": "Construction d'un centre hospitalier de 200 lits avec services de chirurgie, maternité, pédiatrie, réanimation et imagerie médicale. Le projet inclut la formation de 150 personnels de santé et l'acquisition d'équipements médicaux de pointe.",
                "secteur": "santé-action-sociale",
                "poles": "Sud",
                "cout_estimatif": 18500000000,
                "structure_soumissionnaire": "Ministère de la Santé et de l'Action Sociale"
            },
            {
                "titre": "Plateforme industrielle de transformation agroalimentaire de Diourbel",
                "description": "Création d'une zone industrielle dédiée à la transformation des produits agricoles (arachide, mil, sorgho). Infrastructure comprenant: unités de transformation, entrepôts frigorifiques, laboratoire de contrôle qualité, station de traitement des eaux, et centre de formation. Création de 800 emplois directs.",
                "secteur": "industrie-artisanat",
                "poles": "Diourbel-Louga",
                "cout_estimatif": 25000000000,
                "structure_soumissionnaire": "Agence de Promotion des Investissements et des Grands Travaux"
            },
            {
                "titre": "Bitumage de la route Tambacounda - Kédougou",
                "description": "Réhabilitation et bitumage de 150km de route nationale reliant Tambacounda à Kédougou, avec construction de 8 ponts, aménagement de passages pour le bétail, éclairage des traversées de villages, et création d'aires de repos. Durée des travaux: 24 mois.",
                "secteur": "transport-désenclavement",
                "poles": "Sud-Est",
                "cout_estimatif": 45000000000,
                "structure_soumissionnaire": "Agence des Travaux et de Gestion des Routes"
            },
            {
                "titre": "Projet d'assainissement urbain de Saint-Louis",
                "description": "Construction d'un réseau d'assainissement des eaux usées et pluviales pour 25000 ménages, réalisation d'une station d'épuration de 15000m³/jour, aménagement de caniveaux et bassins de rétention. Le projet inclut un volet sensibilisation à l'hygiène et à l'environnement.",
                "secteur": "eau-assainissement",
                "poles": "Nord",
                "cout_estimatif": 16500000000,
                "structure_soumissionnaire": "Office National de l'Assainissement du Sénégal"
            },
            {
                "titre": "Centre de formation professionnelle aux métiers du numérique",
                "description": "Construction et équipement d'un centre de formation de 400 places aux métiers du numérique (développement web, cybersécurité, data science, design graphique). Le centre disposera de salles informatiques équipées, d'espaces de coworking, d'un incubateur de startups et d'une connexion internet haut débit. Partenariats avec entreprises du secteur.",
                "secteur": "télécommunications-TIC",
                "poles": "Dakar",
                "cout_estimatif": 3200000000,
                "structure_soumissionnaire": "Agence de l'Informatique de l'État"
            },
            {
                "titre": "Programme de développement de l'aquaculture à Matam",
                "description": "Création de 50 bassins piscicoles modernes et formation de 200 pisciculteurs. Installation d'unités de transformation et de conservation du poisson. Construction d'un centre de recherche sur l'aquaculture en zone sahélienne. Impact: création de 300 emplois directs et amélioration de la sécurité alimentaire.",
                "secteur": "agriculture-élevage-pêche",
                "poles": "Nord-Est",
                "cout_estimatif": 4200000000,
                "structure_soumissionnaire": "Agence Nationale de l'Aquaculture"
            }
        ]

        projets_crees = 0

        for projet_data in PROJETS_DATA:
            # Générer un numéro de projet unique
            numero_projet = generer_numero_projet()

            projet = Project(
                titre=projet_data["titre"],
                description=projet_data["description"],
                secteur=projet_data["secteur"],
                poles=projet_data["poles"],
                cout_estimatif=projet_data["cout_estimatif"],
                structure_soumissionnaire=projet_data["structure_soumissionnaire"],
                auteur_nom="soumissionnaire",
                statut="soumis",
                numero_projet=numero_projet,
                date_soumission=datetime.utcnow(),
                niveau_priorite="standard",
                nouveaute="projet_initial"
            )

            db.session.add(projet)
            db.session.flush()  # Flush pour que le numéro soit pris en compte pour le prochain
            projets_crees += 1

        db.session.commit()

        return jsonify({
            "message": f"{projets_crees} projets d'exemple créés avec succès",
            "count": projets_crees
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    import os

    # Exécuter les migrations automatiquement au démarrage
    print("[STARTUP] Vérification et exécution des migrations...")
    try:
        from migrate_render import migrate_database
        db_path = app.config.get("DB_PATH", "maturation.db")
        success = migrate_database(db_path)
        if success:
            print("[STARTUP] ✓ Migrations terminées avec succès")
        else:
            print("[STARTUP] ⚠️ Migrations échouées (voir logs ci-dessus)")
    except Exception as e:
        print(f"[STARTUP] ⚠️ Erreur lors de l'exécution des migrations: {e}")
        import traceback
        traceback.print_exc()

    port = int(os.environ.get('PORT', 5002))
    print(f"Starting Flask app on port {port}...")
    app.run(debug=True, host="0.0.0.0", port=port, use_reloader=False)