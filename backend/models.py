# ...existing code...

from datetime import datetime
from db import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50))
    display_name = db.Column(db.String(100), nullable=True)
    nom_complet = db.Column(db.String(200), nullable=True)  # Nom complet de l'utilisateur
    fonction = db.Column(db.String(255), nullable=True)  # Fonction/Poste
    telephone = db.Column(db.String(20), nullable=True)

    # Champs pour la structure d'appartenance (nouveau système: Institution)
    type_structure = db.Column(db.String(50), nullable=True)  # Type de structure (institution, collectivite, agence, autre)
    type_institution = db.Column(db.String(50), nullable=True)  # Sous-type: presidence, primature, ministere, autre_institution
    nom_structure = db.Column(db.String(255), nullable=True)  # Nom de la structure/institution
    direction_service = db.Column(db.String(255), nullable=True)  # Direction/Service au sein de l'institution

    # Champs pour le système de validation des comptes
    justificatif_path = db.Column(db.String(500), nullable=True)  # Chemin vers le justificatif (facultatif)
    statut_compte = db.Column(db.String(50), default='non_verifie')  # Statut : 'non_verifie', 'verifie', 'suspendu'
    date_verification = db.Column(db.DateTime, nullable=True)  # Date de validation
    verifie_par = db.Column(db.String(100), nullable=True)  # Username du validateur
    date_creation = db.Column(db.DateTime, nullable=True)  # Date de création du compte

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_projet = db.Column(db.String(20), unique=True, nullable=True)  # Format: YYYYMMDD
    titre = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    secteur = db.Column(db.String(150), nullable=True)
    poles = db.Column(db.String(150), nullable=True)
    cout_estimatif = db.Column(db.Float, nullable=True)
    budget = db.Column(db.Float, nullable=True)
    pieces_jointes = db.Column(db.Text, nullable=True)
    fichiers = db.Column(db.Text, nullable=True)
    statut = db.Column(db.String(100), default="soumis", nullable=False)
    auteur_nom = db.Column(db.String(100), nullable=True)  # Réajouté pour compatibilité
    soumissionnaire_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    evaluateur_nom = db.Column(db.String(100), nullable=True)
    avis = db.Column(db.String(100), nullable=True)  # favorable, favorable sous conditions, défavorable, compléments demandés
    avis_presidencesct = db.Column(db.String(100), nullable=True)
    decision_finale = db.Column(db.String(100), nullable=True)
    commentaires = db.Column(db.Text, nullable=True)
    commentaires_finaux = db.Column(db.Text, nullable=True)
    validation_secretariat = db.Column(db.String(100), nullable=True)
    complements_demande_message = db.Column(db.Text, nullable=True)
    complements_reponse_message = db.Column(db.Text, nullable=True)
    complements_reponse_pieces = db.Column(db.Text, nullable=True)
    date_soumission = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Nouveaux champs ajoutés
    organisme_tutelle = db.Column(db.String(300), nullable=True)
    origine_projet = db.Column(db.Text, nullable=True)  # JSON: {maturation, offre_spontanee, autres}
    typologie_projet = db.Column(db.Text, nullable=True)  # JSON: {productif, appui_production, social, environnemental}

    # Évaluation préalable (avant évaluation détaillée)
    evaluation_prealable = db.Column(db.String(50), nullable=True)  # "dossier_evaluable" ou "complements_requis"
    evaluation_prealable_date = db.Column(db.DateTime, nullable=True)
    evaluation_prealable_commentaire = db.Column(db.Text, nullable=True)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auteur = db.Column(db.String(100))
    role = db.Column(db.String(50))
    action = db.Column(db.String(255))
    commentaire = db.Column(db.Text)
    statut = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    projet_id = db.Column(db.Integer, db.ForeignKey('project.id'))

class Historique(db.Model):
    __tablename__ = "historique"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))
    action = db.Column(db.String(500))
    auteur = db.Column(db.String(200))
    role = db.Column(db.String(50))
    date_action = db.Column(db.DateTime, default=datetime.utcnow)

class FicheEvaluation(db.Model):
    """Modèle pour les fiches d'évaluation conformes au format réel DGPPE"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    evaluateur_nom = db.Column(db.String(100), nullable=False)
    date_evaluation = db.Column(db.DateTime, default=datetime.utcnow)
    reference_fiche = db.Column(db.String(50), nullable=False)
    
    # II - RESULTATS DE L'EVALUATION - Critères avec barèmes exacts du formulaire réel
    
    # PERTINENCE (/5)
    pertinence_score = db.Column(db.Integer, default=0)  # 0-5
    pertinence_description = db.Column(db.Text)
    
    # ALIGNEMENT A LA DOCTRINE DE TRANSFORMATION SYSTEMIQUE (/10)  
    alignement_score = db.Column(db.Integer, default=0)  # 0-10
    alignement_description = db.Column(db.Text)
    
    # PERTINENCE DES ACTIVITES ET BIEN FONDE DES COUTS/PART DE FONCTIONNEMENT (/15)
    activites_couts_score = db.Column(db.Integer, default=0)  # 0-15
    activites_couts_description = db.Column(db.Text)
    
    # ÉQUITE (SOCIALE-TERRITORIALE-GENRE) (/15)
    equite_score = db.Column(db.Integer, default=0)  # 0-15
    equite_description = db.Column(db.Text)
    
    # VIABILITE/RENTABILITE FINANCIERE (/5)
    viabilite_score = db.Column(db.Integer, default=0)  # 0-5
    viabilite_description = db.Column(db.Text)
    
    # RENTABILITE SOCIO-ECONOMIQUE (ACA/MPR) (/5)
    rentabilite_score = db.Column(db.Integer, default=0)  # 0-5
    rentabilite_description = db.Column(db.Text)
    
    # BENEFICES STRATEGIQUES (SECURITE-RESILIENCE-INNOVATION-COMPETITIVITE-CONTENU LOCAL, ETC.) (/15)
    benefices_strategiques_score = db.Column(db.Integer, default=0)  # 0-15
    benefices_strategiques_description = db.Column(db.Text)
    
    # PERENNITE ET DURABILITE DES EFFETS ET IMPACTS DU PROJET (/5)
    perennite_score = db.Column(db.Integer, default=0)  # 0-5
    perennite_description = db.Column(db.Text)
    
    # AVANTAGES ET COUTS INTANGIBLES (/10)
    avantages_intangibles_score = db.Column(db.Integer, default=0)  # 0-10
    avantages_intangibles_description = db.Column(db.Text)
    
    # FAISABILITE DU PROJET / RISQUES POTENTIELS (/5)
    faisabilite_score = db.Column(db.Integer, default=0)  # 0-5
    faisabilite_description = db.Column(db.Text)
    
    # POTENTIALITE OU OPPORTUNITE DU PROJET A ETRE REALISE EN PPP (/5)
    ppp_score = db.Column(db.Integer, default=0)  # 0-5
    ppp_description = db.Column(db.Text)
    
    # IMPACTS ENVIRONNEMENTAUX (/5)
    impact_environnemental_score = db.Column(db.Integer, default=0)  # 0-5
    impact_environnemental_description = db.Column(db.Text)
    
    # IMPACT SUR L'EMPLOI (/5) - Ajouté selon demande utilisateur
    impact_emploi_score = db.Column(db.Integer, default=0)  # 0-5
    impact_emploi_description = db.Column(db.Text)
    impact_emploi_recommandations = db.Column(db.Text)  # Recommandations spécifiques pour l'emploi
    
    # Score total sur 105 (avec l'ajout de l'impact emploi)
    score_total = db.Column(db.Integer, default=0)  # Somme de tous les scores
    
    # III - CONCLUSION
    proposition = db.Column(db.String(50))  # "Favorable", "Favorable sous condition", "Défavorable", "Compléments demandés"
    recommandations = db.Column(db.Text)  # Recommandations finales
    
    # Fichier PDF généré
    fichier_pdf = db.Column(db.String(200))  # chemin vers le PDF
    
    # Relations
    project = db.relationship('Project', backref=db.backref('fiche_evaluation', uselist=False))
    
    def __init__(self, **kwargs):
        super(FicheEvaluation, self).__init__(**kwargs)
        if not self.reference_fiche and self.project_id:
            # Générer référence automatique : EVAL-NUMERO_PROJET-YYYYMMDD
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            self.reference_fiche = f"EVAL-{self.project_id}-{date_str}"
    
    def calculer_score_total(self):
        """Calcule le score total sur 105 selon le barème réel + impact emploi"""
        self.score_total = (
            self.pertinence_score +              # /5
            self.alignement_score +              # /10
            self.activites_couts_score +         # /15
            self.equite_score +                  # /15
            self.viabilite_score +               # /5
            self.rentabilite_score +             # /5
            self.benefices_strategiques_score +  # /15
            self.perennite_score +               # /5
            self.avantages_intangibles_score +   # /10
            self.faisabilite_score +             # /5
            self.ppp_score +                     # /5
            self.impact_environnemental_score +  # /5
            self.impact_emploi_score             # /5 (nouveau)
        )  # Total = 105
        
        return self.score_total
    
    def get_appreciation_globale(self):
        """Retourne l'appréciation basée sur le score total sur 105"""
        # Calcul en pourcentage pour garder les mêmes seuils
        pourcentage = (self.score_total / 105) * 100
        if pourcentage >= 80:
            return "Excellent"
        elif pourcentage >= 70:
            return "Très bien"
        elif pourcentage >= 60:
            return "Bien"
        elif pourcentage >= 50:
            return "Passable"
        else:
            return "Insuffisant"
        
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'evaluateur_nom': self.evaluateur_nom,
            'date_evaluation': self.date_evaluation.isoformat() if self.date_evaluation else None,
            'reference_fiche': self.reference_fiche,

            # Critères d'évaluation au format structuré
            'criteres': {
                'pertinence': {
                    'score': self.pertinence_score,
                    'description': self.pertinence_description
                },
                'alignement': {
                    'score': self.alignement_score,
                    'description': self.alignement_description
                },
                'activites_couts': {
                    'score': self.activites_couts_score,
                    'description': self.activites_couts_description
                },
                'equite': {
                    'score': self.equite_score,
                    'description': self.equite_description
                },
                'viabilite': {
                    'score': self.viabilite_score,
                    'description': self.viabilite_description
                },
                'rentabilite': {
                    'score': self.rentabilite_score,
                    'description': self.rentabilite_description
                },
                'benefices_strategiques': {
                    'score': self.benefices_strategiques_score,
                    'description': self.benefices_strategiques_description
                },
                'perennite': {
                    'score': self.perennite_score,
                    'description': self.perennite_description
                },
                'avantages_intangibles': {
                    'score': self.avantages_intangibles_score,
                    'description': self.avantages_intangibles_description
                },
                'faisabilite': {
                    'score': self.faisabilite_score,
                    'description': self.faisabilite_description
                },
                'ppp': {
                    'score': self.ppp_score,
                    'description': self.ppp_description
                },
                'impact_environnemental': {
                    'score': self.impact_environnemental_score,
                    'description': self.impact_environnemental_description
                },
                'impact_emploi': {
                    'score': self.impact_emploi_score,
                    'description': self.impact_emploi_description,
                    'recommandations': self.impact_emploi_recommandations
                }
            },

            # Conclusion
            'score_total': self.score_total,
            'appreciation_globale': self.get_appreciation_globale(),
            'proposition': self.proposition,
            'recommandations': self.recommandations,
            'fichier_pdf': self.fichier_pdf
        }

class DocumentProjet(db.Model):
    """Modèle pour gérer les documents supplémentaires ajoutés à un projet après sa soumission"""
    __tablename__ = "documents_projet"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    nom_fichier = db.Column(db.String(500), nullable=False)  # Nom du fichier stocké
    nom_original = db.Column(db.String(500), nullable=False)  # Nom original du fichier
    description = db.Column(db.Text, nullable=True)  # Description optionnelle du document
    type_document = db.Column(db.String(100), nullable=True)  # Type/catégorie du document
    auteur_nom = db.Column(db.String(100), nullable=False)  # Qui a ajouté le document
    auteur_role = db.Column(db.String(50), nullable=False)  # Rôle de la personne qui a ajouté
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)
    taille_fichier = db.Column(db.Integer, nullable=True)  # Taille en octets

    # Relation avec le projet
    project = db.relationship('Project', backref=db.backref('documents_supplementaires', lazy=True))

    def to_dict(self):
        # Chercher le display_name de l'auteur
        auteur_display_name = self.auteur_nom
        try:
            auteur = User.query.filter_by(username=self.auteur_nom).first()
            if auteur and auteur.display_name:
                auteur_display_name = auteur.display_name
        except Exception:
            pass  # Garder le username si erreur

        return {
            'id': self.id,
            'project_id': self.project_id,
            'nom_fichier': self.nom_fichier,
            'nom_original': self.nom_original,
            'description': self.description,
            'type_document': self.type_document,
            'auteur_nom': self.auteur_nom,
            'auteur_display_name': auteur_display_name,
            'auteur_role': self.auteur_role,
            'date_ajout': self.date_ajout.isoformat() if self.date_ajout else None,
            'taille_fichier': self.taille_fichier
        }

class MessageProjet(db.Model):
    """Modèle pour gérer les messages de discussion sur un projet"""
    __tablename__ = "messages_projet"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    auteur_nom = db.Column(db.String(100), nullable=False)  # Qui a écrit le message
    auteur_role = db.Column(db.String(50), nullable=False)  # Rôle de la personne
    contenu = db.Column(db.Text, nullable=True)  # Contenu du message (optionnel si fichiers joints)
    fichier_joint = db.Column(db.String(500), nullable=True)  # Nom du fichier joint (optionnel) - DEPRECATED pour compatibilité
    fichier_joint_original = db.Column(db.String(500), nullable=True)  # Nom original du fichier - DEPRECATED
    fichier_joint_taille = db.Column(db.Integer, nullable=True)  # Taille du fichier - DEPRECATED
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, nullable=True)  # Si le message est modifié

    # Relation avec le projet
    project = db.relationship('Project', backref=db.backref('messages_discussion', lazy=True))

    # Relation avec les fichiers joints
    fichiers = db.relationship('FichierMessage', backref='message', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        # Chercher le display_name de l'auteur
        auteur_display_name = self.auteur_nom
        try:
            auteur = User.query.filter_by(username=self.auteur_nom).first()
            if auteur and auteur.display_name:
                auteur_display_name = auteur.display_name
        except Exception:
            pass  # Garder le username si erreur

        return {
            'id': self.id,
            'project_id': self.project_id,
            'auteur_nom': self.auteur_nom,
            'auteur_display_name': auteur_display_name,
            'auteur_role': self.auteur_role,
            'contenu': self.contenu or '',
            'fichier_joint': self.fichier_joint,
            'fichier_joint_original': self.fichier_joint_original,
            'fichier_joint_taille': self.fichier_joint_taille,
            'fichiers': [f.to_dict() for f in self.fichiers] if self.fichiers else [],
            'date_creation': self.date_creation.isoformat() if self.date_creation else None,
            'date_modification': self.date_modification.isoformat() if self.date_modification else None
        }

class FichierMessage(db.Model):
    """Modèle pour gérer plusieurs fichiers joints à un message"""
    __tablename__ = "fichiers_message"

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages_projet.id'), nullable=False)
    nom_fichier = db.Column(db.String(500), nullable=False)  # Nom sur le serveur
    nom_original = db.Column(db.String(500), nullable=False)  # Nom original
    taille_fichier = db.Column(db.Integer, nullable=False)  # Taille en octets
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'message_id': self.message_id,
            'nom_fichier': self.nom_fichier,
            'nom_original': self.nom_original,
            'taille_fichier': self.taille_fichier,
            'date_ajout': self.date_ajout.isoformat() if self.date_ajout else None
        }