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
    email = db.Column(db.String(150), nullable=True)  # Email de l'utilisateur
    nom_complet = db.Column(db.String(200), nullable=True)  # Nom complet de l'utilisateur
    fonction = db.Column(db.String(255), nullable=True)  # Fonction/Poste
    telephone = db.Column(db.String(20), nullable=True)

    # Champs pour la structure d'appartenance (nouveau système: Institution)
    type_structure = db.Column(db.String(50), nullable=True)  # Type de structure (institution, collectivite, agence, autre)
    type_institution = db.Column(db.String(50), nullable=True)  # Sous-type: presidence, primature, ministere, autre_institution
    nom_structure = db.Column(db.String(255), nullable=True)  # Nom de la structure/institution
    direction_service = db.Column(db.String(255), nullable=True)  # Direction/Service au sein de l'institution
    nom_ministere = db.Column(db.String(300), nullable=True)  # Nom du ministère (pour type_institution=ministere)
    tutelle_agence = db.Column(db.String(300), nullable=True)  # Ministère de tutelle (pour type_structure=agence)

    # Champs pour le système de validation des comptes
    justificatif_path = db.Column(db.String(500), nullable=True)  # Chemin vers le justificatif (facultatif)
    statut_compte = db.Column(db.String(50), default='non_verifie')  # Statut : 'non_verifie', 'verifie', 'suspendu'
    date_verification = db.Column(db.DateTime, nullable=True)  # Date de validation
    verifie_par = db.Column(db.String(100), nullable=True)  # Username du validateur
    date_creation = db.Column(db.DateTime, nullable=True)  # Date de création du compte
    must_change_password = db.Column(db.Boolean, default=False)  # Doit changer le mot de passe à la première connexion

    # Champs pour le système de Point Focal
    is_point_focal = db.Column(db.Boolean, default=False)  # Est-ce un point focal ?
    point_focal_organisme = db.Column(db.String(300), nullable=True)  # Organisme dont il est point focal (ministère, institution)
    point_focal_nomme_par = db.Column(db.String(100), nullable=True)  # Username de celui qui a nommé le point focal

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
    statut_comite = db.Column(db.String(50), nullable=True)  # recommande_comite, approuve_definitif, en_reevaluation
    fiche_evaluation_visible = db.Column(db.Boolean, default=False, nullable=True)  # Visibilité fiche pour soumissionnaire
    commentaires = db.Column(db.Text, nullable=True)
    commentaires_finaux = db.Column(db.Text, nullable=True)
    validation_secretariat = db.Column(db.String(100), nullable=True)
    complements_demande_message = db.Column(db.Text, nullable=True)
    complements_reponse_message = db.Column(db.Text, nullable=True)
    complements_reponse_pieces = db.Column(db.Text, nullable=True)
    date_soumission = db.Column(db.DateTime, default=datetime.utcnow)

    # Localisation de la soumission (pour mesurer la territorialisation)
    lieu_soumission_pays = db.Column(db.String(100), nullable=True)
    lieu_soumission_ville = db.Column(db.String(100), nullable=True)
    lieu_soumission_region = db.Column(db.String(100), nullable=True)

    # Coordonnées GPS du projet (localisation géographique précise)
    gps_latitude = db.Column(db.Float, nullable=True)
    gps_longitude = db.Column(db.Float, nullable=True)
    gps_accuracy = db.Column(db.Integer, nullable=True)  # Précision en mètres

    # Nouveaux champs ajoutés
    organisme_tutelle = db.Column(db.String(300), nullable=True)
    organisme_tutelle_data = db.Column(db.Text, nullable=True)  # JSON: données structurées de la hiérarchie organisme
    structure_soumissionnaire = db.Column(db.String(300), nullable=True)  # Structure soumissionnaire/maître d'ouvrage
    origine_projet = db.Column(db.Text, nullable=True)  # JSON: {maturation, offre_spontanee, autres}

    # Dimensions transversales (remplace typologie_projet)
    cc_adaptation = db.Column(db.Boolean, default=False, nullable=True)  # Changement climatique - Adaptation
    cc_attenuation = db.Column(db.Boolean, default=False, nullable=True)  # Changement climatique - Atténuation
    genre = db.Column(db.Boolean, default=False, nullable=True)  # Genre

    # Évaluation préalable (avant évaluation détaillée)
    evaluation_prealable = db.Column(db.String(50), nullable=True)  # "dossier_evaluable" ou "complements_requis"
    evaluation_prealable_date = db.Column(db.DateTime, nullable=True)
    evaluation_prealable_commentaire = db.Column(db.Text, nullable=True)
    evaluation_prealable_matrice = db.Column(db.Text, nullable=True)  # JSON: {documents: [{nom, requis, transmis}], commentaires_globaux}

    # Motivation pour la resoumission après rejet (nullable pour compatibilité)
    motivation_resoumission = db.Column(db.Text, nullable=True)

    # Nouveaux champs (Décembre 2025)
    nouveaute = db.Column(db.String(50), nullable=True)  # "projet_initial" ou "phase_2"
    projet_initial_ref = db.Column(db.String(50), nullable=True)  # Référence au projet initial si phase 2
    niveau_priorite = db.Column(db.String(50), nullable=True)  # "prioritaire_ant" ou "standard"
    type_financement = db.Column(db.Text, nullable=True)  # JSON: liste des types de financement

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

    # I - PRESENTATION DU PROJET (rempli par l'évaluateur)
    intitule_projet = db.Column(db.Text, nullable=True)
    cout_projet = db.Column(db.String(100), nullable=True)
    origine_projet = db.Column(db.Text, nullable=True)

    # Dimensions transversales
    cc_adaptation = db.Column(db.Boolean, default=False, nullable=True)
    cc_attenuation = db.Column(db.Boolean, default=False, nullable=True)
    genre = db.Column(db.Boolean, default=False, nullable=True)

    # Nouveaux champs - Tableau de présentation
    articulation = db.Column(db.Text, nullable=True)
    axes = db.Column(db.Text, nullable=True)
    objectifs_strategiques = db.Column(db.Text, nullable=True)
    odd = db.Column(db.Text, nullable=True)

    # Durées
    duree_analyse = db.Column(db.String(50), nullable=True)
    realisation = db.Column(db.String(50), nullable=True)
    exploitation = db.Column(db.String(50), nullable=True)

    # Autres informations projet
    localisation = db.Column(db.Text, nullable=True)
    parties_prenantes = db.Column(db.Text, nullable=True)
    autres_projets_connexes = db.Column(db.Text, nullable=True)
    objectif_projet = db.Column(db.Text, nullable=True)
    activites_principales = db.Column(db.Text, nullable=True)
    resultats_attendus = db.Column(db.Text, nullable=True)

    # Anciens champs (pour compatibilité)
    sous_secteur = db.Column(db.Text, nullable=True)
    organisme_tutelle = db.Column(db.Text, nullable=True)
    snd_2025_2029 = db.Column(db.Text, nullable=True)

    # II - RESULTATS DE L'EVALUATION - Critères avec barèmes exacts du formulaire réel
    
    # PERTINENCE (/5)
    pertinence_score = db.Column(db.Integer, default=0)  # 0-5
    pertinence_description = db.Column(db.Text)
    pertinence_recommandations = db.Column(db.Text)

    # ALIGNEMENT A LA DOCTRINE DE TRANSFORMATION SYSTEMIQUE (/10)
    alignement_score = db.Column(db.Integer, default=0)  # 0-10
    alignement_description = db.Column(db.Text)
    alignement_recommandations = db.Column(db.Text)

    # PERTINENCE DES ACTIVITES ET BIEN FONDE DES COUTS/PART DE FONCTIONNEMENT (/15)
    activites_couts_score = db.Column(db.Integer, default=0)  # 0-15
    activites_couts_description = db.Column(db.Text)
    activites_couts_recommandations = db.Column(db.Text)

    # ÉQUITE (SOCIALE-TERRITORIALE-GENRE) (/15)
    equite_score = db.Column(db.Integer, default=0)  # 0-15
    equite_description = db.Column(db.Text)
    equite_recommandations = db.Column(db.Text)

    # VIABILITE/RENTABILITE FINANCIERE (/5)
    viabilite_score = db.Column(db.Integer, default=0)  # 0-5
    viabilite_description = db.Column(db.Text)
    viabilite_recommandations = db.Column(db.Text)

    # RENTABILITE SOCIO-ECONOMIQUE (ACA/MPR) (/5)
    rentabilite_score = db.Column(db.Integer, default=0)  # 0-5
    rentabilite_description = db.Column(db.Text)
    rentabilite_recommandations = db.Column(db.Text)

    # BENEFICES STRATEGIQUES (SECURITE-RESILIENCE-INNOVATION-COMPETITIVITE-CONTENU LOCAL, ETC.) (/15)
    benefices_strategiques_score = db.Column(db.Integer, default=0)  # 0-15
    benefices_strategiques_description = db.Column(db.Text)
    benefices_strategiques_recommandations = db.Column(db.Text)

    # PERENNITE ET DURABILITE DES EFFETS ET IMPACTS DU PROJET (/5)
    perennite_score = db.Column(db.Integer, default=0)  # 0-5
    perennite_description = db.Column(db.Text)
    perennite_recommandations = db.Column(db.Text)

    # AVANTAGES ET COUTS INTANGIBLES (/10)
    avantages_intangibles_score = db.Column(db.Integer, default=0)  # 0-10
    avantages_intangibles_description = db.Column(db.Text)
    avantages_intangibles_recommandations = db.Column(db.Text)

    # FAISABILITE DU PROJET / RISQUES POTENTIELS (/5)
    faisabilite_score = db.Column(db.Integer, default=0)  # 0-5
    faisabilite_description = db.Column(db.Text)
    faisabilite_recommandations = db.Column(db.Text)

    # POTENTIALITE OU OPPORTUNITE DU PROJET A ETRE REALISE EN PPP (/5)
    ppp_score = db.Column(db.Integer, default=0)  # 0-5
    ppp_description = db.Column(db.Text)
    ppp_recommandations = db.Column(db.Text)

    # IMPACTS ENVIRONNEMENTAUX (/5)
    impact_environnemental_score = db.Column(db.Integer, default=0)  # 0-5
    impact_environnemental_description = db.Column(db.Text)
    impact_environnemental_recommandations = db.Column(db.Text)
    
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
        """Calcule le score total sur 100 selon le barème des 12 critères"""
        self.score_total = (
            (self.pertinence_score or 0) +                    # /5
            (self.alignement_score or 0) +                    # /10
            (self.activites_couts_score or 0) +               # /15
            (self.equite_score or 0) +                        # /15
            (self.viabilite_score or 0) +                     # /5
            (self.rentabilite_score or 0) +                   # /5
            (self.benefices_strategiques_score or 0) +        # /10
            (self.perennite_score or 0) +                     # /5
            (self.avantages_intangibles_score or 0) +         # /10
            (self.faisabilite_score or 0) +                   # /5
            (self.ppp_score or 0) +                           # /5
            (self.impact_environnemental_score or 0)          # /5
        )  # Total = 100

        return self.score_total

    def calculer_avis_depuis_score(self):
        """
        Calcule automatiquement l'avis (proposition) basé sur le score total

        Barème:
        - 80-100 points : Favorable
        - 70-79 points : Favorable sous condition
        - 0-69 points : Défavorable

        Returns:
            str: L'avis calculé
        """
        score = self.score_total or 0

        if score >= 80:
            return "favorable"
        elif score >= 70:
            return "favorable sous conditions"
        else:
            return "défavorable"
    
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
                    'description': self.pertinence_description,
                    'recommandations': self.pertinence_recommandations
                },
                'alignement': {
                    'score': self.alignement_score,
                    'description': self.alignement_description,
                    'recommandations': self.alignement_recommandations
                },
                'activites_couts': {
                    'score': self.activites_couts_score,
                    'description': self.activites_couts_description,
                    'recommandations': self.activites_couts_recommandations
                },
                'equite': {
                    'score': self.equite_score,
                    'description': self.equite_description,
                    'recommandations': self.equite_recommandations
                },
                'viabilite': {
                    'score': self.viabilite_score,
                    'description': self.viabilite_description,
                    'recommandations': self.viabilite_recommandations
                },
                'rentabilite': {
                    'score': self.rentabilite_score,
                    'description': self.rentabilite_description,
                    'recommandations': self.rentabilite_recommandations
                },
                'benefices_strategiques': {
                    'score': self.benefices_strategiques_score,
                    'description': self.benefices_strategiques_description,
                    'recommandations': self.benefices_strategiques_recommandations
                },
                'perennite': {
                    'score': self.perennite_score,
                    'description': self.perennite_description,
                    'recommandations': self.perennite_recommandations
                },
                'avantages_intangibles': {
                    'score': self.avantages_intangibles_score,
                    'description': self.avantages_intangibles_description,
                    'recommandations': self.avantages_intangibles_recommandations
                },
                'faisabilite': {
                    'score': self.faisabilite_score,
                    'description': self.faisabilite_description,
                    'recommandations': self.faisabilite_recommandations
                },
                'ppp': {
                    'score': self.ppp_score,
                    'description': self.ppp_description,
                    'recommandations': self.ppp_recommandations
                },
                'impact_environnemental': {
                    'score': self.impact_environnemental_score,
                    'description': self.impact_environnemental_description,
                    'recommandations': self.impact_environnemental_recommandations
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


class FicheEvaluationArchive(db.Model):
    """
    Archive des fiches d'évaluation pour traçabilité
    Une copie est créée à chaque modification ou réassignation
    """
    __tablename__ = "fiches_evaluation_archive"

    id = db.Column(db.Integer, primary_key=True)
    fiche_id_originale = db.Column(db.Integer, nullable=False)  # ID de la fiche source
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    # Métadonnées d'archivage
    date_archivage = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    raison_archivage = db.Column(db.String(255))  # "modification_secretariat", "reassignation", etc.
    archive_par = db.Column(db.String(100))  # Nom d'utilisateur qui a déclenché l'archivage
    version = db.Column(db.Integer, default=1)  # Numéro de version

    # Données de la fiche archivée (JSON complet)
    evaluateur_nom = db.Column(db.String(100))
    date_evaluation_originale = db.Column(db.DateTime)
    reference_fiche = db.Column(db.String(50))

    # Scores et descriptions (copie exacte de FicheEvaluation)
    pertinence_score = db.Column(db.Integer)
    pertinence_description = db.Column(db.Text)
    alignement_score = db.Column(db.Integer)
    alignement_description = db.Column(db.Text)
    activites_couts_score = db.Column(db.Integer)
    activites_couts_description = db.Column(db.Text)
    equite_score = db.Column(db.Integer)
    equite_description = db.Column(db.Text)
    viabilite_score = db.Column(db.Integer)
    viabilite_description = db.Column(db.Text)
    rentabilite_score = db.Column(db.Integer)
    rentabilite_description = db.Column(db.Text)
    benefices_strategiques_score = db.Column(db.Integer)
    benefices_strategiques_description = db.Column(db.Text)
    perennite_score = db.Column(db.Integer)
    perennite_description = db.Column(db.Text)
    avantages_intangibles_score = db.Column(db.Integer)
    avantages_intangibles_description = db.Column(db.Text)
    faisabilite_score = db.Column(db.Integer)
    faisabilite_description = db.Column(db.Text)
    ppp_score = db.Column(db.Integer)
    ppp_description = db.Column(db.Text)
    impact_environnemental_score = db.Column(db.Integer)
    impact_environnemental_description = db.Column(db.Text)

    score_total = db.Column(db.Integer)
    proposition = db.Column(db.String(100))
    recommandations = db.Column(db.Text)

    def to_dict(self):
        """Convertit l'archive en dictionnaire"""
        return {
            'id': self.id,
            'fiche_id_originale': self.fiche_id_originale,
            'project_id': self.project_id,
            'date_archivage': self.date_archivage.isoformat() if self.date_archivage else None,
            'raison_archivage': self.raison_archivage,
            'archive_par': self.archive_par,
            'version': self.version,
            'evaluateur_nom': self.evaluateur_nom,
            'date_evaluation_originale': self.date_evaluation_originale.isoformat() if self.date_evaluation_originale else None,
            'reference_fiche': self.reference_fiche,
            'score_total': self.score_total,
            'proposition': self.proposition,
            'recommandations': self.recommandations,
            'criteres': {
                'pertinence': {'score': self.pertinence_score, 'description': self.pertinence_description},
                'alignement': {'score': self.alignement_score, 'description': self.alignement_description},
                'activites_couts': {'score': self.activites_couts_score, 'description': self.activites_couts_description},
                'equite': {'score': self.equite_score, 'description': self.equite_description},
                'viabilite': {'score': self.viabilite_score, 'description': self.viabilite_description},
                'rentabilite': {'score': self.rentabilite_score, 'description': self.rentabilite_description},
                'benefices_strategiques': {'score': self.benefices_strategiques_score, 'description': self.benefices_strategiques_description},
                'perennite': {'score': self.perennite_score, 'description': self.perennite_description},
                'avantages_intangibles': {'score': self.avantages_intangibles_score, 'description': self.avantages_intangibles_description},
                'faisabilite': {'score': self.faisabilite_score, 'description': self.faisabilite_description},
                'ppp': {'score': self.ppp_score, 'description': self.ppp_description},
                'impact_environnemental': {'score': self.impact_environnemental_score, 'description': self.impact_environnemental_description}
            }
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
    visible_pour_roles = db.Column(db.Text, nullable=True)  # JSON string des rôles autorisés à voir le document

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

        # Parser les rôles autorisés depuis JSON
        import json
        visible_pour_roles = []
        if self.visible_pour_roles:
            try:
                visible_pour_roles = json.loads(self.visible_pour_roles)
            except Exception:
                pass

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
            'taille_fichier': self.taille_fichier,
            'visible_pour_roles': visible_pour_roles
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
    modifie_par = db.Column(db.String(100), nullable=True)  # Username de qui a modifié (si différent de l'auteur)

    # Masquage administratif
    masque = db.Column(db.Boolean, default=False)  # Si le message est masqué
    masque_par = db.Column(db.String(100), nullable=True)  # Username de qui a masqué
    masque_raison = db.Column(db.Text, nullable=True)  # Raison du masquage
    date_masquage = db.Column(db.DateTime, nullable=True)  # Quand le message a été masqué

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
            'date_modification': self.date_modification.isoformat() if self.date_modification else None,
            'modifie_par': self.modifie_par,
            'masque': self.masque,
            'masque_par': self.masque_par,
            'masque_raison': self.masque_raison,
            'date_masquage': self.date_masquage.isoformat() if self.date_masquage else None
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

class HistoriqueMessage(db.Model):
    """Modèle pour tracker l'historique des modifications des messages"""
    __tablename__ = "historique_messages"

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages_projet.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    # Contenu avant modification
    contenu_avant = db.Column(db.Text, nullable=True)
    contenu_apres = db.Column(db.Text, nullable=True)

    # Métadonnées
    modifie_par = db.Column(db.String(100), nullable=False)  # Username de qui a modifié
    date_modification = db.Column(db.DateTime, default=datetime.utcnow)
    type_modification = db.Column(db.String(50), nullable=False)  # 'edition', 'masquage', 'demasquage'
    raison = db.Column(db.Text, nullable=True)  # Raison de la modification (obligatoire pour masquage)

    def to_dict(self):
        return {
            'id': self.id,
            'message_id': self.message_id,
            'project_id': self.project_id,
            'contenu_avant': self.contenu_avant,
            'contenu_apres': self.contenu_apres,
            'modifie_par': self.modifie_par,
            'date_modification': self.date_modification.isoformat() if self.date_modification else None,
            'type_modification': self.type_modification,
            'raison': self.raison
        }

class FormulaireConfig(db.Model):
    """Configuration globale du formulaire d'évaluation"""
    __tablename__ = "formulaire_config"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)  # Nom de la configuration
    version = db.Column(db.String(50), nullable=False)  # Version (ex: "1.0", "2.0")
    version_affichage = db.Column(db.String(200), nullable=True)  # Texte libre pour affichage (ex: "Version 1.0 - Janvier 2025")
    description = db.Column(db.Text, nullable=True)  # Description de la configuration
    active = db.Column(db.Boolean, default=False)  # Configuration active?
    score_total_max = db.Column(db.Integer, default=100)  # Score total maximum

    # Seuils de proposition (en pourcentage)
    seuil_favorable = db.Column(db.Integer, default=80)  # >= 80%
    seuil_conditionnel = db.Column(db.Integer, default=70)  # >= 70% et < 80%
    # En dessous de seuil_conditionnel = défavorable

    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, nullable=True)
    modifie_par = db.Column(db.String(100), nullable=True)  # Username de qui a modifié

    # Relations
    sections = db.relationship('SectionFormulaire', backref='config', lazy=True, cascade='all, delete-orphan', order_by='SectionFormulaire.ordre')

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'version': self.version,
            'version_affichage': self.version_affichage,
            'description': self.description,
            'active': self.active,
            'score_total_max': self.score_total_max,
            'seuil_favorable': self.seuil_favorable,
            'seuil_conditionnel': self.seuil_conditionnel,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None,
            'date_modification': self.date_modification.isoformat() if self.date_modification else None,
            'modifie_par': self.modifie_par,
            'sections': [s.to_dict() for s in sorted(self.sections, key=lambda x: x.ordre)]
        }

class SectionFormulaire(db.Model):
    """Sections du formulaire (I, II, III, IV)"""
    __tablename__ = "section_formulaire"

    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey('formulaire_config.id'), nullable=False)
    titre = db.Column(db.String(300), nullable=False)  # Ex: "PRÉSENTATION DU PROJET"
    numero = db.Column(db.String(10), nullable=False)  # Ex: "I", "II", "III", "IV"
    ordre = db.Column(db.Integer, nullable=False)  # Ordre d'affichage
    type_section = db.Column(db.String(50), nullable=False)  # 'presentation', 'classification', 'evaluation', 'conclusion'
    editable = db.Column(db.Boolean, default=True)  # Si l'utilisateur peut éditer cette section

    # Relations
    champs = db.relationship('ChampFormulaire', backref='section', lazy=True, cascade='all, delete-orphan', order_by='ChampFormulaire.ordre')
    criteres = db.relationship('CritereEvaluation', backref='section', lazy=True, cascade='all, delete-orphan', order_by='CritereEvaluation.ordre')

    def to_dict(self):
        return {
            'id': self.id,
            'config_id': self.config_id,
            'titre': self.titre,
            'numero': self.numero,
            'ordre': self.ordre,
            'type_section': self.type_section,
            'editable': self.editable,
            'champs': [c.to_dict() for c in sorted(self.champs, key=lambda x: x.ordre)],
            'criteres': [c.to_dict() for c in sorted(self.criteres, key=lambda x: x.ordre)]
        }

class ChampFormulaire(db.Model):
    """Champs personnalisés dans une section (pour présentation et classification)"""
    __tablename__ = "champ_formulaire"

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('section_formulaire.id'), nullable=False)
    libelle = db.Column(db.String(300), nullable=False)  # Label du champ
    cle = db.Column(db.String(100), nullable=False)  # Clé technique (ex: 'origine_projet')
    type_champ = db.Column(db.String(50), nullable=False)  # 'text', 'textarea', 'number', 'select', 'checkbox_group', 'radio_group'
    ordre = db.Column(db.Integer, nullable=False)
    obligatoire = db.Column(db.Boolean, default=False)
    largeur = db.Column(db.String(20), default='full')  # 'full', 'half', 'third'
    options = db.Column(db.Text, nullable=True)  # JSON pour les options (select, checkbox, radio)
    valeur_defaut = db.Column(db.Text, nullable=True)
    aide = db.Column(db.Text, nullable=True)  # Texte d'aide
    lecture_seule = db.Column(db.Boolean, default=False)  # Si le champ est en lecture seule

    def to_dict(self):
        import json
        options_parsed = None
        if self.options:
            try:
                options_parsed = json.loads(self.options)
            except:
                pass

        return {
            'id': self.id,
            'section_id': self.section_id,
            'libelle': self.libelle,
            'cle': self.cle,
            'type_champ': self.type_champ,
            'ordre': self.ordre,
            'obligatoire': self.obligatoire,
            'largeur': self.largeur,
            'options': options_parsed,
            'valeur_defaut': self.valeur_defaut,
            'aide': self.aide,
            'lecture_seule': self.lecture_seule
        }

class CritereEvaluation(db.Model):
    """Critères d'évaluation dans la section résultats"""
    __tablename__ = "critere_evaluation"

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('section_formulaire.id'), nullable=False)
    nom = db.Column(db.String(300), nullable=False)  # Nom du critère
    cle = db.Column(db.String(100), nullable=False)  # Clé technique (ex: 'pertinence')
    description_aide = db.Column(db.Text, nullable=True)  # Description/aide pour l'évaluateur
    score_max = db.Column(db.Integer, nullable=False)  # Score maximum pour ce critère
    ordre = db.Column(db.Integer, nullable=False)
    avec_description = db.Column(db.Boolean, default=True)  # Si on demande une description textuelle
    avec_recommandations = db.Column(db.Boolean, default=False)  # Si on demande des recommandations

    def to_dict(self):
        return {
            'id': self.id,
            'section_id': self.section_id,
            'nom': self.nom,
            'cle': self.cle,
            'description_aide': self.description_aide,
            'score_max': self.score_max,
            'ordre': self.ordre,
            'avec_description': self.avec_description,
            'avec_recommandations': self.avec_recommandations
        }


class Ministere(db.Model):
    """Liste des ministères du Sénégal pour sélection dans les formulaires"""
    __tablename__ = "ministere"

    id = db.Column(db.Integer, primary_key=True)
    nom_complet = db.Column(db.String(300), nullable=False)
    abreviation = db.Column(db.String(100), nullable=True)
    actif = db.Column(db.Boolean, default=True)
    ordre = db.Column(db.Integer, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nom_complet': self.nom_complet,
            'abreviation': self.abreviation,
            'actif': self.actif,
            'ordre': self.ordre,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None,
            'date_modification': self.date_modification.isoformat() if self.date_modification else None
        }

class ConnexionLog(db.Model):
    """Modèle pour tracer les connexions des utilisateurs"""
    __tablename__ = "connexion_log"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, index=True)
    display_name = db.Column(db.String(200), nullable=True)
    role = db.Column(db.String(50), nullable=True)
    date_connexion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    adresse_ip = db.Column(db.String(45), nullable=True)  # IPv6 peut faire jusqu'à 45 caractères
    pays = db.Column(db.String(100), nullable=True)  # Pays de connexion
    ville = db.Column(db.String(100), nullable=True)  # Ville de connexion
    region = db.Column(db.String(100), nullable=True)  # Région de connexion
    latitude = db.Column(db.Float, nullable=True)  # Latitude GPS (si disponible)
    longitude = db.Column(db.Float, nullable=True)  # Longitude GPS (si disponible)
    source_geoloc = db.Column(db.String(20), nullable=True)  # 'gps', 'ip', ou 'fallback'
    precision_geoloc = db.Column(db.Integer, nullable=True)  # Précision en mètres (pour GPS)
    user_agent = db.Column(db.Text, nullable=True)
    statut = db.Column(db.String(20), nullable=False)  # 'succes' ou 'echec'
    raison_echec = db.Column(db.String(200), nullable=True)  # Motif si échec

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name,
            'role': self.role,
            'date_connexion': self.date_connexion.isoformat() if self.date_connexion else None,
            'adresse_ip': self.adresse_ip,
            'pays': self.pays,
            'ville': self.ville,
            'region': self.region,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'source_geoloc': self.source_geoloc,
            'precision_geoloc': self.precision_geoloc,
            'user_agent': self.user_agent,
            'statut': self.statut,
            'raison_echec': self.raison_echec
        }


class Notification(db.Model):
    """Modèle pour les notifications in-app"""
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True, index=True)

    # Type de notification pour filtrage et icônes
    type = db.Column(db.String(50), nullable=False)  # 'statut_change', 'nouveau_message', 'complement_requis', 'avis_rendu', 'document_ajoute', 'assignation'

    # Contenu
    titre = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)

    # Lien vers l'action (ex: /projects/123)
    lien = db.Column(db.String(300), nullable=True)

    # État
    lu = db.Column(db.Boolean, default=False, index=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    date_lecture = db.Column(db.DateTime, nullable=True)

    # Pour les emails - si cette notification doit déclencher un email
    email_envoye = db.Column(db.Boolean, default=False)
    priorite_email = db.Column(db.Boolean, default=False)  # True = envoyer email immédiat

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'type': self.type,
            'titre': self.titre,
            'message': self.message,
            'lien': self.lien,
            'lu': self.lu,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None,
            'date_lecture': self.date_lecture.isoformat() if self.date_lecture else None,
            'email_envoye': self.email_envoye,
            'priorite_email': self.priorite_email
        }


class ContactMessage(db.Model):
    """Modèle pour les messages de contact"""
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    telephone = db.Column(db.String(30), nullable=True)
    objet = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

    # Info utilisateur connecté (si applicable)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    username = db.Column(db.String(80), nullable=True)

    # Statut et traitement
    statut = db.Column(db.String(30), default='nouveau')  # nouveau, lu, traite, archive
    date_creation = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    date_lecture = db.Column(db.DateTime, nullable=True)
    traite_par = db.Column(db.String(80), nullable=True)
    reponse = db.Column(db.Text, nullable=True)

    # IP pour anti-spam
    ip_address = db.Column(db.String(50), nullable=True)

    # Pièces jointes (JSON: liste de chemins de fichiers)
    pieces_jointes = db.Column(db.Text, nullable=True)

    # Affectation à un utilisateur
    assigne_a = db.Column(db.String(100), nullable=True)  # Username de la personne assignée
    date_assignation = db.Column(db.DateTime, nullable=True)
    date_reponse = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'nom': self.nom,
            'email': self.email,
            'telephone': self.telephone,
            'objet': self.objet,
            'message': self.message,
            'user_id': self.user_id,
            'username': self.username,
            'statut': self.statut,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None,
            'date_lecture': self.date_lecture.isoformat() if self.date_lecture else None,
            'traite_par': self.traite_par,
            'reponse': self.reponse,
            'pieces_jointes': json.loads(self.pieces_jointes) if self.pieces_jointes else [],
            'assigne_a': self.assigne_a,
            'date_assignation': self.date_assignation.isoformat() if self.date_assignation else None,
            'date_reponse': self.date_reponse.isoformat() if self.date_reponse else None
        }


class ProjectVersion(db.Model):
    """Modèle pour l'historique des versions de projets"""
    __tablename__ = 'project_version'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)

    # Informations de versioning
    modified_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_by = db.Column(db.String(100))
    modification_type = db.Column(db.String(50))  # 'creation', 'update', 'status_change', etc.
    change_summary = db.Column(db.Text)

    # Snapshot complet du projet (JSON)
    project_data = db.Column(db.Text, nullable=False)

    # Métadonnées
    statut_before = db.Column(db.String(100))
    statut_after = db.Column(db.String(100))

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'project_id': self.project_id,
            'version_number': self.version_number,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None,
            'modified_by': self.modified_by,
            'modification_type': self.modification_type,
            'change_summary': self.change_summary,
            'project_data': json.loads(self.project_data) if self.project_data else {},
            'statut_before': self.statut_before,
            'statut_after': self.statut_after
        }


class EmailTemplate(db.Model):
    """Modèle pour les templates d'emails personnalisables"""
    __tablename__ = 'email_templates'

    id = db.Column(db.Integer, primary_key=True)
    template_key = db.Column(db.String(100), unique=True, nullable=False)  # Clé unique du template (ex: 'projet_assigne')
    nom = db.Column(db.String(200), nullable=False)  # Nom affiché du template
    description = db.Column(db.Text)  # Description du template
    sujet = db.Column(db.String(500), nullable=False)  # Sujet de l'email
    contenu_html = db.Column(db.Text, nullable=False)  # Contenu HTML de l'email
    variables_disponibles = db.Column(db.Text)  # JSON des variables disponibles (ex: {user_name}, {project_titre})
    actif = db.Column(db.Boolean, default=True)  # Le template est-il actif ?
    modifie_le = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modifie_par = db.Column(db.String(100))  # Username de la dernière personne qui a modifié

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'template_key': self.template_key,
            'nom': self.nom,
            'description': self.description,
            'sujet': self.sujet,
            'contenu_html': self.contenu_html,
            'variables_disponibles': json.loads(self.variables_disponibles) if self.variables_disponibles else [],
            'actif': self.actif,
            'modifie_le': self.modifie_le.isoformat() if self.modifie_le else None,
            'modifie_par': self.modifie_par
        }