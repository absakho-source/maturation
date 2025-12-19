"""
Middleware de validation du workflow des projets
Garantit l'intégrité du cycle de vie des projets
"""

class WorkflowValidator:
    """Validateur centralisé pour toutes les opérations sur les projets"""

    STATUTS_DEFINITIFS = [
        'favorable',
        'favorable sous conditions',
        'défavorable',
        'avis défavorable confirmé'
    ]

    @staticmethod
    def est_statut_definitif(projet):
        """Vérifie si un projet a un statut définitif"""
        return (
            projet.statut in WorkflowValidator.STATUTS_DEFINITIFS or
            projet.avis in WorkflowValidator.STATUTS_DEFINITIFS or
            projet.decision_finale == 'confirme' or
            (hasattr(projet, 'statut_comite') and projet.statut_comite == 'approuve_definitif')
        )

    @staticmethod
    def peut_etre_assigne(projet):
        """Vérifie si un projet peut être assigné/réassigné"""
        if WorkflowValidator.est_statut_definitif(projet):
            return False, "Impossible d'assigner un projet avec décision finale"

        return True, None

    @staticmethod
    def peut_etre_evalue(projet, include_prealable=False):
        """Vérifie si un projet peut recevoir une évaluation"""
        if WorkflowValidator.est_statut_definitif(projet):
            return False, "Impossible d'évaluer un projet avec décision finale"

        if not include_prealable:
            # Pour évaluation complète (avis)
            if projet.statut not in ['assigné', 'en évaluation', 'évalué']:
                return False, "Le projet doit être assigné pour être évalué"

        return True, None

    @staticmethod
    def peut_modifier_fiche_evaluation(projet, role):
        """Vérifie si une fiche d'évaluation peut être modifiée"""
        # Admin peut toujours modifier (pour corrections exceptionnelles)
        if role == 'admin':
            return True, None

        # Vérifier si le projet a un statut final
        if WorkflowValidator.est_statut_definitif(projet):
            return False, "Impossible de modifier la fiche d'un projet avec décision finale"

        return True, None

    @staticmethod
    def peut_etre_valide_par_secretariat(projet):
        """Vérifie si le Secrétariat peut valider l'avis"""
        # Autoriser la validation pour les projets évalués ou les projets rejetés (resoumission)
        statuts_autorisees = [
            'évalué',
            'rejeté',
            'rejeté par présidence SCT',
            'en réexamen par le Secrétariat SCT'
        ]

        if projet.statut not in statuts_autorisees:
            return False, "Le projet doit être évalué pour être validé"

        if projet.validation_secretariat == 'valide':
            # Si déjà validé, vérifier qu'il n'a pas été transmis plus loin
            if projet.avis_presidencesct or projet.decision_finale:
                return False, "Le projet a déjà été transmis à la Présidence SCT"

            # Vérifier le statut comité
            if hasattr(projet, 'statut_comite'):
                from app import get_statut_comite
                statut_comite = get_statut_comite(projet)
                if statut_comite in ['recommande_comite', 'approuve_definitif']:
                    return False, "Le projet a déjà été transmis au Comité"

        return True, None

    @staticmethod
    def peut_etre_valide_par_presidence_sct(projet):
        """Vérifie si la Présidence SCT peut valider"""
        if projet.statut not in ['en attente validation presidencesct', 'validé par secretariat']:
            return False, "Le projet n'est pas en attente de validation par la Présidence SCT"

        if projet.avis_presidencesct:
            # Si déjà validé, vérifier qu'il n'a pas été transmis plus loin
            if projet.decision_finale:
                return False, "Le projet a déjà été transmis à la Présidence du Comité"

            if hasattr(projet, 'statut_comite'):
                from app import get_statut_comite
                statut_comite = get_statut_comite(projet)
                if statut_comite in ['recommande_comite', 'approuve_definitif']:
                    return False, "Le projet a déjà été transmis au Comité"

        return True, None

    @staticmethod
    def peut_etre_decide_par_presidence_comite(projet):
        """Vérifie si la Présidence du Comité peut prendre une décision"""
        if projet.statut != 'validé par presidencesct':
            return False, "Le projet n'a pas été validé par la Présidence SCT"

        if projet.decision_finale:
            # Si déjà décidé, vérifier qu'il n'a pas été transmis au Comité
            if hasattr(projet, 'statut_comite'):
                from app import get_statut_comite
                statut_comite = get_statut_comite(projet)
                if statut_comite in ['recommande_comite', 'approuve_definitif']:
                    return False, "Le projet a déjà été recommandé au Comité"

        return True, None

    @staticmethod
    def peut_recevoir_decision_comite(projet):
        """Vérifie si le Comité peut prendre une décision"""
        if hasattr(projet, 'statut_comite'):
            from app import get_statut_comite
            statut_comite = get_statut_comite(projet)

            if statut_comite == 'approuve_definitif':
                return False, "Le projet a déjà été entériné par le Comité"

            if statut_comite != 'recommande_comite':
                # Compatibilité avec anciens projets
                if projet.statut != 'validé par presidencecomite':
                    return False, "Le projet n'est pas en attente de décision du Comité"

        return True, None

    @staticmethod
    def peut_recevoir_complements(projet):
        """Vérifie si un projet peut recevoir des compléments"""
        if projet.statut != 'compléments demandés':
            return False, "Le projet n'est pas en attente de compléments"

        if WorkflowValidator.est_statut_definitif(projet):
            return False, "Impossible de soumettre des compléments pour un projet avec décision finale"

        return True, None

    @staticmethod
    def peut_demander_complements(projet):
        """Vérifie si on peut demander des compléments"""
        if WorkflowValidator.est_statut_definitif(projet):
            return False, "Impossible de demander des compléments pour un projet avec décision finale"

        return True, None
