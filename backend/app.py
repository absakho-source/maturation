import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from flask import Flask, request, jsonify, send_from_directory, send_file
from db import db
from models import Project, User, FicheEvaluation, Historique, DocumentProjet, MessageProjet, FichierMessage
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-me-in-production"

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
print(f"[CONFIG] Using UPLOAD_FOLDER: {app.config['UPLOAD_FOLDER']}")

# Configuration CORS pour permettre les requêtes depuis le frontend
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://127.0.0.1:5173",  # Dev local
            "http://localhost:5173",
            "https://maturation-frontend.onrender.com"  # Production
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

db.init_app(app)

# Fonction pour générer le numéro de projet automatiquement
def generer_numero_projet():
    """Génère un numéro de projet au format DGPPE-YYYY-NNN où NNN est un compteur séquentiel annuel"""

    # Format année actuelle
    now = datetime.now()
    year = now.strftime("%Y")  # Exemple: 2025
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

# Fonction pour simplifier les statuts vus par le soumissionnaire
def get_statut_soumissionnaire(projet):
    """Convertit les statuts internes en statuts simplifiés pour le soumissionnaire"""
    statut_reel = projet.statut
    
    # Si le projet est approuvé par le comité, on affiche l'avis de l'évaluateur
    if statut_reel == "approuvé" and projet.avis:
        return projet.avis  # "favorable", "favorable sous conditions", "défavorable"
    
    # Si le projet est rejeté, il retourne vers le secrétariat → "en instruction"
    if statut_reel == "rejeté":
        return "en instruction"
    
    # Statuts simplifiés selon les étapes du workflow
    if statut_reel == "soumis":
        return "soumis"
    elif statut_reel == "compléments demandés":
        return "compléments demandés"
    elif statut_reel == "compléments fournis":
        return "compléments soumis"
    else:
        # Tous les autres statuts internes = "en instruction"
        return "en instruction"

# Migration de base de données: ajout automatique des colonnes manquantes
def ensure_sqlite_columns():
    import sqlite3
    con = sqlite3.connect(app.config["DB_PATH"])
    cur = con.cursor()
    # Si la table n'existe pas encore, on sort (create_all la créera juste après)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
    if not cur.fetchone():
        con.close()
        return
    cur.execute("PRAGMA table_info(projects)")
    cols = {r[1] for r in cur.fetchall()}
    needed = {
        "numero_projet": "TEXT",
        "validation_secretariat": "TEXT",
        "commentaires_finaux": "TEXT",
        "complements_demande_message": "TEXT",
        "complements_reponse_message": "TEXT",
        "complements_reponse_pieces": "TEXT",
        "auteur_nom": "TEXT",  # <-- Ajout ici
    }
    for c, cdef in needed.items():
        if c not in cols:
            print(f"[DB MIGRATION] Adding projects.{c}")
            cur.execute(f"ALTER TABLE projects ADD COLUMN {c} {cdef}")
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

# Routes
@app.route("/api/projects", methods=["GET", "POST"])
@app.route("/api/projets", methods=["GET", "POST"])  # Alias français
def projects():
    if request.method == "GET":
        try:
            role = request.args.get("role", "")
            username = request.args.get("username", "")
            # Ajoute ces logs pour diagnostiquer le filtrage et la base
            print("[DEBUG] role:", role, "username:", username)
            print("[DEBUG] Nombre total de projets:", Project.query.count())
            print("[DEBUG] Projets auteur_nom == username:", Project.query.filter_by(auteur_nom=username).count())
            print("[DEBUG] Tous les auteur_nom:", [p.auteur_nom for p in Project.query.all()])

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
            if role in ['secretariatsct', 'presidencesct', 'presidencecomite', 'evaluateur', 'admin']:
                # These roles should not see projects from suspended accounts in their workflow
                items = [p for p in items if p.author_id]
                # Get list of suspended user IDs
                suspended_users = User.query.filter_by(statut_compte='suspendu').all()
                suspended_ids = [u.id for u in suspended_users]
                # Filter out projects from suspended users
                items = [p for p in items if p.author_id not in suspended_ids]

            # Correction : si aucun projet, retourne explicitement une liste vide
            if not items:
                print("[DEBUG] Aucun projet trouvé pour ce filtre.")
                return jsonify([]), 200

            result = []
            for p in items:
                # Ajoute ce log pour chaque projet
                print(f"[DEBUG] Projet: id={p.id}, titre={p.titre}, pieces_jointes={p.pieces_jointes}, date_soumission={getattr(p, 'date_soumission', None)}")

                try:
                    if role == "soumissionnaire":
                        statut_affiche = get_statut_soumissionnaire(p)
                    else:
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

                    # Récupérer le display_name de l'évaluateur si applicable
                    evaluateur_display_name = ""
                    if p.evaluateur_nom:
                        evaluateur = User.query.filter_by(username=p.evaluateur_nom).first()
                        if evaluateur:
                            evaluateur_display_name = evaluateur.display_name or evaluateur.username

                    # Conversion de evaluation_prealable_date
                    evaluation_prealable_date = None
                    if hasattr(p, "evaluation_prealable_date") and p.evaluation_prealable_date:
                        try:
                            evaluation_prealable_date = p.evaluation_prealable_date.isoformat()
                        except Exception:
                            evaluation_prealable_date = str(p.evaluation_prealable_date)

                    # Vérifier si le projet est assigné à l'évaluateur connecté
                    est_assigne_a_moi = False
                    if role == "evaluateur" and username:
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
                            "date_soumission": date_soumission
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
                            "est_assigne_a_moi": est_assigne_a_moi,
                            "avis": str(p.avis) if p.avis else "",
                            "commentaires": str(p.commentaires) if p.commentaires else "",
                            "validation_secretariat": str(p.validation_secretariat) if p.validation_secretariat else "",
                            "avis_presidencesct": str(p.avis_presidencesct) if p.avis_presidencesct else "",
                            "decision_finale": str(p.decision_finale) if p.decision_finale else "",
                            "commentaires_finaux": str(p.commentaires_finaux) if p.commentaires_finaux else "",
                            "complements_demande_message": str(p.complements_demande_message) if p.complements_demande_message else "",
                            "complements_reponse_message": str(p.complements_reponse_message) if p.complements_reponse_message else "",
                            "complements_reponse_pieces": str(p.complements_reponse_pieces) if p.complements_reponse_pieces else "",
                            "evaluation_prealable": str(p.evaluation_prealable) if p.evaluation_prealable else "",
                            "evaluation_prealable_date": evaluation_prealable_date,
                            "evaluation_prealable_commentaire": str(p.evaluation_prealable_commentaire) if p.evaluation_prealable_commentaire else "",
                            "pieces_jointes": pieces_jointes,
                            "date_soumission": date_soumission
                        })
                except Exception as err:
                    import traceback
                    print(f"[ERROR] Projet id={getattr(p, 'id', None)}: {err}")
                    traceback.print_exc()
            print(f"[DEBUG] Nombre de projets retournés: {len(result)}")
            return jsonify(result), 200
        except Exception as e:
            import traceback
            print("=== ERREUR /api/projects ===")
            traceback.print_exc()
            print("Exception:", e)
            return jsonify([]), 500

    # POST: soumission d'un projet
    try:
        titre = request.form.get("titre")
        description = request.form.get("description")
        secteur = request.form.get("secteur")
        poles = request.form.get("poles")  # CSV
        cout_estimatif = request.form.get("cout_estimatif")
        organisme_tutelle = request.form.get("organisme_tutelle")
        auteur_nom = request.form.get("auteur_nom")

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

        project = Project(
            numero_projet=numero_projet,
            titre=titre,
            description=description,
            secteur=secteur,
            poles=poles,
            cout_estimatif=float(cout_estimatif) if cout_estimatif else None,
            organisme_tutelle=organisme_tutelle,
            pieces_jointes=",".join(filenames) if filenames else None,
            auteur_nom=auteur_nom  # <-- Ajout ici
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
        p = Project.query.get_or_404(project_id)

        # Récupérer le display_name de l'évaluateur si applicable
        evaluateur_display_name = ""
        if p.evaluateur_nom:
            evaluateur = User.query.filter_by(username=p.evaluateur_nom).first()
            if evaluateur:
                evaluateur_display_name = evaluateur.display_name or evaluateur.username

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
            "commentaires_finaux": p.commentaires_finaux,
            "complements_demande_message": p.complements_demande_message,
            "complements_reponse_message": p.complements_reponse_message,
            "complements_reponse_pieces": p.complements_reponse_pieces,
            "pieces_jointes": p.pieces_jointes.split(",") if p.pieces_jointes else [],
            "date_soumission": p.date_soumission.isoformat() if p.date_soumission else None
        }), 200
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    try:
        role = request.args.get('role', '').lower()
        if role != 'admin':
            return jsonify({"error": "Accès non autorisé. Seuls les administrateurs peuvent supprimer des projets."}), 403
        
        # Récupérer le projet
        project = Project.query.get_or_404(project_id)
        projet_titre = project.titre
        projet_numero = project.numero_projet
        
        # Supprimer le projet
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
        data = request.json or {}
        print(f"🔍 DEBUG traiter_project: data = {data}")
        p = Project.query.get_or_404(project_id)
        auteur = data.get("auteur", "")
        role = data.get("role", "")
        action = ""

        # Assignation (mais pas pour la réassignation de projets rejetés)
        if ("evaluateur_nom" in data and "avis" not in data and "validation_secretariat" not in data
            and data.get("statut_action") != "reassigner_rejete"):
            # Supprimer la fiche d'évaluation existante lors d'une réassignation
            fiche_existante = FicheEvaluation.query.filter_by(project_id=project_id).first()
            if fiche_existante:
                db.session.delete(fiche_existante)

            # Réinitialiser les champs d'évaluation lors de la réassignation
            p.avis = None
            p.commentaires = None

            # Réinitialiser l'évaluation préalable lors de la réassignation
            p.evaluation_prealable = None
            p.evaluation_prealable_date = None
            p.evaluation_prealable_commentaire = None

            p.evaluateur_nom = data["evaluateur_nom"]
            p.statut = "assigné"

            # Récupérer la motivation facultative
            motivation = (data.get("motivation") or "").strip()
            if motivation:
                action = f"Projet assigné à {data['evaluateur_nom']} - Motivation: {motivation}"
            else:
                action = f"Projet assigné à {data['evaluateur_nom']}"

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
                # Si c'est un évaluateur qui demande des compléments, ça doit être validé par le secrétariat d'abord
                if role in ["evaluateur1", "evaluateur2"]:
                    p.statut = "en attente validation demande compléments"
                    p.complements_demande_message = commentaires
                    action = "Demande de compléments en attente de validation secrétariat"
                else:
                    # Si c'est le secrétariat qui demande directement
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
        elif "statut_action" in data:
            statut_action = data.get("statut_action")
            if statut_action == "reevaluer_complements":
                # Supprimer la fiche d'évaluation existante pour une nouvelle évaluation
                fiche_existante = FicheEvaluation.query.filter_by(project_id=project_id).first()
                if fiche_existante:
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
            elif statut_action == "valider_demande_complements":
                p.statut = "compléments demandés"
                action = "Demande de compléments validée - transmise au soumissionnaire"
            elif statut_action == "rejeter_demande_complements":
                p.statut = "assigné"
                p.avis = None
                p.commentaires = None
                p.complements_demande_message = None

                # Réinitialiser l'évaluation préalable
                p.evaluation_prealable = None
                p.evaluation_prealable_date = None
                p.evaluation_prealable_commentaire = None

                action = "Demande de compléments rejetée - projet réassigné"
            elif statut_action == "reassigner_rejete":
                # Réassignation d'un projet avec avis rejeté avec préservation de l'historique
                if p.statut != "rejeté":
                    return jsonify({"error": "Seuls les projets avec avis rejetés peuvent être réassignés"}), 400

                to = data.get("evaluateur_nom")
                if not to:
                    return jsonify({"error": "evaluateur_nom requis pour la réassignation"}), 400

                # Supprimer la fiche d'évaluation existante lors d'une réassignation
                fiche_existante = FicheEvaluation.query.filter_by(project_id=project_id).first()
                if fiche_existante:
                    db.session.delete(fiche_existante)

                # Réinitialiser pour permettre une nouvelle évaluation
                p.evaluateur_nom = to
                p.statut = "assigné"
                p.avis = None
                p.commentaires = None

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
            if v == "valide":
                p.validation_secretariat = "valide"
                p.statut = "en attente validation presidencesct"
                action = "Avis validé par le Secrétariat SCT"
            elif v == "reassigne":
                to = data.get("evaluateur_nom")
                if not to:
                    return jsonify({"error": "evaluateur_nom requis pour la réassignation"}), 400

                # Supprimer la fiche d'évaluation existante lors d'une réassignation
                fiche_existante = FicheEvaluation.query.filter_by(project_id=project_id).first()
                if fiche_existante:
                    db.session.delete(fiche_existante)

                p.validation_secretariat = "reassigne"
                p.evaluateur_nom = to
                p.avis = None; p.commentaires = None
                p.statut = "assigné"
                action = f"Avis rejeté par le Secrétariat — réassigné à {to}"
            else:
                return jsonify({"error": "validation_secretariat invalide"}), 400

        # Validation Présidence SCT
        elif "avis_presidencesct" in data:
            p.avis_presidencesct = data["avis_presidencesct"]
            if data["avis_presidencesct"] == "valide":
                p.statut = "validé par presidencesct"
                # NE PAS mettre de decision_finale ici - c'est le rôle du Comité
                action = "Validation par Présidence SCT - transmission au Comité"
            else:
                # retour en soumission pour révision
                p.statut = "soumis"
                p.evaluateur_nom = None
                p.avis = None; p.commentaires = None
                action = "Rejeté par Présidence SCT - retour au Secrétariat"

        # Décision finale (Comité)
        elif "decision_finale" in data:
            dec = data.get("decision_finale")
            p.decision_finale = dec  # 'confirme' | 'infirme'
            if data.get("commentaires"):
                p.commentaires_finaux = data.get("commentaires")
            
            # Statuts finaux clairs
            if dec == "confirme":
                p.statut = "approuvé"
                action = "Projet approuvé par le Comité"
            else:
                p.statut = "rejeté"
                action = "Projet rejeté par le Comité"

        db.session.commit()
        if action:
            hist = Historique(project_id=project_id, action=action, auteur=auteur, role=role)
            db.session.add(hist)
            db.session.commit()

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
        auteur = data.get("auteur", "")
        role = data.get("role", "")

        decision = data.get("decision")  # "dossier_evaluable" ou "complements_requis"
        commentaire = data.get("commentaire", "").strip()

        if not decision or decision not in ["dossier_evaluable", "complements_requis"]:
            return jsonify({"error": "Décision invalide"}), 400

        # Enregistrer l'évaluation préalable
        p.evaluation_prealable = decision
        p.evaluation_prealable_date = datetime.utcnow()
        p.evaluation_prealable_commentaire = commentaire

        # Changer le statut en fonction de la décision
        action = ""
        if decision == "dossier_evaluable":
            p.statut = "en évaluation"
            action = "Évaluation préalable: dossier évaluable - passage à l'évaluation détaillée"
        else:  # complements_requis
            p.statut = "compléments demandés"
            p.complements_demande_message = commentaire
            # Réinitialiser les réponses de compléments
            p.complements_reponse_message = None
            p.complements_reponse_pieces = None
            action = f"Évaluation préalable: compléments requis - {commentaire}"

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

# Soumission des compléments par le soumissionnaire
@app.route("/api/projects/<int:project_id>/complements", methods=["POST"])
def submit_complements(project_id):
    try:
        p = Project.query.get_or_404(project_id)
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

        # Si le projet a un évaluateur assigné, retour direct à l'évaluateur
        # Sinon, retour au secrétariat pour ré-assignation
        if p.evaluateur_nom:
            p.statut = "assigné"
            action = f"Compléments soumis - réassigné à {p.evaluateur_nom} pour réévaluation"
        else:
            p.statut = "compléments fournis"
            action = "Compléments soumis - en attente de réassignation"

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

@app.route("/api/uploads/<path:filename>")
def uploaded_file(filename):
    """Serve uploaded files including those in subfolders"""
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

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
            "display_name": u.display_name or u.username
        } for u in users]
        return jsonify(result), 200
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
                "nom_structure": u.nom_structure if hasattr(u, 'nom_structure') else None,
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
        validateur_username = data.get('validateur_username', '')

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

        if role not in ['admin', 'secretariatsct', 'presidencecomite', 'presidencesct']:
            return jsonify({"error": "Accès non autorisé"}), 403

        # Récupérer l'utilisateur
        user = User.query.get_or_404(user_id)

        # Mettre à jour le statut
        user.statut_compte = 'suspendu'

        db.session.commit()

        return jsonify({
            "message": f"Compte de {user.username} suspendu avec succès",
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
def create_user():
    """Créer un nouvel utilisateur (inscription enrichie avec validation)"""
    try:
        data = request.json
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        role = data.get("role", "").strip()
        display_name = data.get("display_name", "").strip()

        # Nouveaux champs pour la validation des comptes (système Institution)
        nom_complet = data.get("nom_complet", "").strip()
        telephone = data.get("telephone", "").strip()
        fonction = data.get("fonction", "").strip()
        type_structure = data.get("type_structure", "").strip()
        type_institution = data.get("type_institution", "").strip()
        nom_structure = data.get("nom_structure", "").strip()
        direction_service = data.get("direction_service", "").strip()

        if not username or not password or not role:
            return jsonify({"error": "Username, password et rôle sont requis"}), 400

        # Vérifier si l'utilisateur existe déjà
        existing = User.query.filter_by(username=username).first()
        if existing:
            return jsonify({"error": "Un utilisateur avec ce nom existe déjà"}), 400

        # Créer le nouvel utilisateur avec les nouveaux champs
        new_user = User(
            username=username,
            password=password,
            role=role,
            display_name=display_name,
            nom_complet=nom_complet,
            telephone=telephone,
            fonction=fonction,
            type_structure=type_structure,
            type_institution=type_institution,
            nom_structure=nom_structure,
            direction_service=direction_service,
            statut_compte='non_verifie',
            date_creation=datetime.utcnow()
        )

        db.session.add(new_user)
        db.session.commit()

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
    check_and_reset_db()  # <-- Ajout ici
    with app.app_context():
        db.create_all()
        ensure_sqlite_columns()
        target_pwd = "    "
        if User.query.count() == 0:
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
            
            for username, role in user_data:
                user = User()
                user.username = username
                user.password = target_pwd
                user.role = role
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

# ===================== ROUTES STATISTIQUES =====================

@app.route('/api/stats/overview', methods=['GET'])
def get_stats_overview():
    """Statistiques générales accessibles selon le rôle"""
    role = request.args.get('role', '')
    username = request.args.get('username', '')
    
    # Tous les projets selon les permissions du rôle
    if role == 'admin':
        projects = Project.query.all()
    elif role in ['secretariatsct', 'presidencesct', 'presidencecomite']:
        projects = Project.query.all()  # Ces rôles voient tous les projets
    else:
        # Autres rôles (évaluateurs, soumissionnaires) - limités
        projects = Project.query.filter_by(auteur_nom=username).all()
    
    # Calculs statistiques
    total_projets = len(projects)
    cout_total = sum(p.cout_estimatif or 0 for p in projects)
    
    # Répartition par statut
    statuts = {}
    for project in projects:
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
    
    # Filtrer selon les permissions
    if role == 'admin':
        projects = Project.query.all()
    elif role in ['secretariatsct', 'presidencesct', 'presidencecomite']:
        projects = Project.query.all()
    else:
        projects = Project.query.filter_by(auteur_nom=request.args.get('username', '')).all()
    
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
    
    projects = Project.query.all()
    
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
        
        # Sud regroupe Ziguinchor, Sedhiou, Kolda
        'Sud (Ziguinchor)': 'Sud',
        'Sud (Sedhiou)': 'Sud', 
        'Sud (Kolda)': 'Sud',
        
        # Sud-Est regroupe Kedougou, Tambacounda
        'Sud-Est (Kedougou)': 'Sud-Est',
        'Sud-Est (Tambacounda)': 'Sud-Est',
        
        # Diourbel-Louga regroupe Diourbel, Louga
        'Diourbel-Louga (Diourbel)': 'Diourbel-Louga',
        'Diourbel-Louga (Louga)': 'Diourbel-Louga',
        
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
        status_filter = request.args.get('filter', '')  # 'approved' pour filtrer uniquement les projets approuvés

        print(f"\n{'='*80}")
        print(f"[DEBUG /api/stats/poles] Filtre reçu: '{status_filter}'")
        print(f"{'='*80}")

        # Filtrer selon les permissions - Par défaut afficher tous les projets pour la carte territoriale
        if role == 'admin' or not role:  # Si pas de rôle spécifié, afficher tous les projets
            projects = Project.query.all()
        elif role in ['secretariatsct', 'presidencesct', 'presidencecomite']:
            projects = Project.query.all()
        elif username:
            projects = Project.query.filter_by(auteur_nom=username).all()
        else:
            projects = Project.query.all()

        print(f"[DEBUG] Nombre total de projets AVANT filtrage: {len(projects)}")

        # Afficher quelques exemples de decision_finale
        print(f"[DEBUG] Exemples de valeurs decision_finale dans la DB:")
        for i, p in enumerate(projects[:10]):  # Afficher les 10 premiers
            print(f"  - Projet {p.id}: decision_finale = '{p.decision_finale}'")

        # Filtrer par statut si demandé
        if status_filter == 'approved':
            # Uniquement les projets avec décision finale confirmée par la présidence du comité
            # Note: decision_finale peut avoir les valeurs 'confirme' ou 'infirme'
            approved_decisions = ['confirme']
            print(f"[DEBUG] Filtrage par decision_finale in {approved_decisions}")

            projects_before = len(projects)
            projects = [p for p in projects if p.decision_finale in approved_decisions]
            projects_after = len(projects)

            print(f"[DEBUG] Nombre de projets APRÈS filtrage: {projects_after}")
            print(f"[DEBUG] Projets filtrés: {projects_before} -> {projects_after} ({projects_before - projects_after} exclus)")

            if projects_after > 0:
                print(f"[DEBUG] Exemples de projets approuvés:")
                for p in projects[:5]:
                    print(f"  - Projet {p.id}: decision_finale = '{p.decision_finale}', pole = '{p.poles}'")

        poles_stats = {}

        for project in projects:
            # Convertir le pôle DB vers le pôle territorial standardisé
            pole_db = project.poles or 'non défini'
            pole_territorial = get_pole_territorial(pole_db)
            print(f"DEBUG: {pole_db} -> {pole_territorial}")  # Debug
            
            if pole_territorial not in poles_stats:
                poles_stats[pole_territorial] = {
                    'nombre_projets': 0,
                    'cout_total': 0,
                    'secteurs': {},
                    'statuts': {}
                }
            
            poles_stats[pole_territorial]['nombre_projets'] += 1
            poles_stats[pole_territorial]['cout_total'] += project.cout_estimatif or 0
            
            # Répartition par secteur dans ce pôle
            secteur = project.secteur or 'non défini'
            poles_stats[pole_territorial]['secteurs'][secteur] = poles_stats[pole_territorial]['secteurs'].get(secteur, 0) + 1
            
            # Répartition par statut dans ce pôle
            statut = project.statut or 'non défini'
            poles_stats[pole_territorial]['statuts'][statut] = poles_stats[pole_territorial]['statuts'].get(statut, 0) + 1
        
        print(f"[DEBUG] Nombre de projets: {len(projects)}")
        print(f"[DEBUG] poles_stats: {poles_stats}")
        # Correction : toujours retourner un JSON valide
        return jsonify(poles_stats if poles_stats else {})
    except Exception as e:
        print(f"ERROR in stats_poles_territorial: {e}")
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

        # Récupérer tous les documents du projet
        documents = DocumentProjet.query.filter_by(project_id=project_id).order_by(DocumentProjet.date_ajout.desc()).all()

        # Filtrer selon le rôle : soumissionnaire voit tous les documents de soumissionnaire pour ce projet
        if user_role == "soumissionnaire":
            # Vérifier que l'utilisateur a accès à ce projet (est l'auteur)
            if project.auteur_nom == user_name or project.auteur == user_name:
                # Voir tous les documents avec auteur_role soumissionnaire pour ce projet
                documents = [doc for doc in documents if doc.auteur_role == "soumissionnaire"]
            else:
                # Pas d'accès à ce projet
                documents = []
        # secteur_territorial voit les documents du soumissionnaire et ses propres documents
        elif user_role == "secteur_territorial":
            documents = [doc for doc in documents if doc.auteur_role in ["soumissionnaire", "secteur_territorial"]]

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
                # Vérifier que l'utilisateur a accès à ce projet (est l'auteur)
                if project.auteur_nom == user_name or project.auteur == user_name:
                    # Voir tous les documents avec auteur_role soumissionnaire pour ce projet
                    documents = [doc for doc in documents if doc.auteur_role == "soumissionnaire"]
                else:
                    # Pas d'accès à ce projet
                    documents = []
            elif user_role == "secteur_territorial":
                documents = [doc for doc in documents if doc.auteur_role in ["soumissionnaire", "secteur_territorial"]]

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
        upload_folder = app.config["UPLOAD_FOLDER"]
        filepath = os.path.join(upload_folder, document.nom_fichier)
        if os.path.exists(filepath):
            os.remove(filepath)

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

        return jsonify({
            "message": "Message ajouté avec succès",
            "data": message.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<int:project_id>/messages/<int:message_id>", methods=["DELETE"])
def delete_project_message(project_id, message_id):
    """Supprimer un message (auteur uniquement ou admin)"""
    try:
        # Récupérer le message
        message = MessageProjet.query.filter_by(id=message_id, project_id=project_id).first_or_404()

        # Vérifier les permissions
        auteur_nom = request.args.get("auteur_nom")
        role = request.args.get("role", "").lower()

        # Seul l'admin ou l'auteur du message peut le supprimer
        if role != "admin" and auteur_nom != message.auteur_nom:
            return jsonify({"error": "Vous n'avez pas la permission de supprimer ce message"}), 403

        # Supprimer le message
        db.session.delete(message)
        db.session.commit()

        # Ajouter une entrée dans l'historique
        hist = Historique(
            project_id=project_id,
            action=f"Message supprimé de la discussion",
            auteur=auteur_nom,
            role=role
        )
        db.session.add(hist)
        db.session.commit()

        return jsonify({"message": "Message supprimé avec succès"}), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ============ Route des métriques de performance ============
@app.route('/api/metrics', methods=['GET'])
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
            Project.decision_finale.in_(['favorable', 'favorable sous réserve', 'défavorable', 'confirme', 'infirme'])
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
            Project.decision_finale.in_(['favorable', 'favorable sous réserve', 'défavorable', 'confirme', 'infirme'])
        ).all()

        favorable_count = sum(1 for p in projects_evaluated
                             if p.decision_finale in ['favorable', 'favorable sous réserve', 'confirme'])
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

        # Statistiques par pôle
        stats_poles = db.session.query(
            Project.poles,
            func.count(Project.id).label('count'),
            func.sum(Project.cout_estimatif).label('total_cout')
        ).group_by(Project.poles).all()

        # Statistiques utilisateurs
        total_users = User.query.count()
        users_by_role = db.session.query(
            User.role,
            func.count(User.id).label('count')
        ).group_by(User.role).all()

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
            data_poles.append([pole or 'Non spécifié', str(count), cout_str])

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

        # 4. Statistiques utilisateurs
        elements.append(Paragraph("4. STATISTIQUES UTILISATEURS", subtitle_style))

        role_names = {
            'admin': 'Administrateur',
            'soumissionnaire': 'Soumissionnaire',
            'evaluateur': 'Évaluateur',
            'secretariatsct': 'Secrétariat SCT',
            'presidencesct': 'Présidence SCT',
            'presidencecomite': 'Présidence Comité'
        }

        data_users = [['Rôle', 'Nombre d\'utilisateurs']]
        for role, count in users_by_role:
            role_display = role_names.get(role, role)
            data_users.append([role_display, str(count)])
        data_users.append(['Total utilisateurs', str(total_users)])

        table_users = Table(data_users, colWidths=[10*cm, 4*cm])
        table_users.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.lightcoral),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#c0392b')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table_users)
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
    register_project_routes(app, Project, FicheEvaluation, db, User)
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

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5002))
    print(f"Starting Flask app on port {port}...")
    app.run(debug=True, host="0.0.0.0", port=port, use_reloader=False)