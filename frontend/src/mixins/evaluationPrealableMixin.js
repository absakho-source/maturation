/**
 * Mixin pour l'évaluation de la recevabilité
 * Fournit les méthodes et données nécessaires pour gérer l'évaluation de la recevabilité des projets
 * Utilisable par tous les rôles: evaluateur, secretariatsct, presidencesct, presidencecomite, admin
 */
export default {
  data() {
    return {
      // Données pour l'évaluation de la recevabilité
      evaluationPrealableCommentaires: {},
      envoiEvaluationPrealable: {},
      modalEvalPrealableId: null
    };
  },

  methods: {
    /**
     * Détermine si un projet nécessite une évaluation de la recevabilité
     * @param {Object} project - Le projet à évaluer
     * @returns {boolean} - true si le projet nécessite une évaluation de la recevabilité
     */
    needsEvaluationPrealable(project) {
      // Afficher l'interface d'évaluation de la recevabilité si:
      // - Le projet est assigné OU en évaluation, ET aucune évaluation de la recevabilité n'a été faite
      // OU
      // - Des compléments ont été demandés ET le soumissionnaire a répondu
      const statutsEligibles = ["assigné", "en évaluation"];
      const isInitialAssignment = statutsEligibles.includes(project.statut) && !project.evaluation_prealable;
      const hasReceivedComplements =
        project.evaluation_prealable === "complements_requis" &&
        project.complements_reponse_message &&
        project.complements_reponse_message.trim() !== "";

      return isInitialAssignment || hasReceivedComplements;
    },

    /**
     * Ouvre la modal d'évaluation de la recevabilité pour un projet
     * @param {number} projectId - L'ID du projet
     */
    openEvalPrealableModal(projectId) {
      this.modalEvalPrealableId = projectId;
    },

    /**
     * Ferme la modal d'évaluation de la recevabilité
     */
    closeEvalPrealableModal() {
      this.modalEvalPrealableId = null;
    },

    /**
     * Appelée après la soumission d'une évaluation de la recevabilité
     * Ferme la modal et recharge les projets
     */
    async handleEvaluationPrealableSubmitted() {
      console.log('🎯 [evaluationPrealableMixin] handleEvaluationPrealableSubmitted appelé');
      this.closeEvalPrealableModal();
      console.log('🎯 [evaluationPrealableMixin] Modal fermée');
      if (this.loadProjects) {
        console.log('🎯 [evaluationPrealableMixin] Rechargement des projets...');
        await this.loadProjects();
        console.log('🎯 [evaluationPrealableMixin] Projets rechargés');
      } else {
        console.warn('⚠️ [evaluationPrealableMixin] loadProjects n\'est pas disponible');
      }
    },

    /**
     * Retourne le texte lisible pour une décision d'évaluation de la recevabilité
     * @param {string} decision - La décision (dossier_evaluable, complements_requis, dossier_rejete)
     * @returns {string} - Le texte formaté
     */
    getEvaluationPrealableText(decision) {
      const map = {
        'dossier_evaluable': '✅ Dossier évaluable',
        'complements_requis': '📝 Compléments requis',
        'dossier_rejete': '❌ Dossier rejeté'
      };
      return map[decision] || decision;
    },

    /**
     * Retourne la classe CSS pour une décision d'évaluation de la recevabilité
     * @param {string} decision - La décision
     * @returns {string} - La classe CSS
     */
    getEvaluationPrealableClass(decision) {
      const map = {
        'dossier_evaluable': 'decision-evaluable',
        'complements_requis': 'decision-complements',
        'dossier_rejete': 'decision-rejete'
      };
      return map[decision] || '';
    },

    /**
     * Valide un rejet proposé par un évaluateur
     * @param {number} projectId - L'ID du projet
     */
    async validerRejet(projectId) {
      const commentaire = (this.evaluationPrealableCommentaires[projectId] || "").trim();

      if (!confirm("Êtes-vous sûr de vouloir valider ce rejet définitivement ? Le soumissionnaire sera notifié.")) {
        return;
      }

      this.envoiEvaluationPrealable[projectId] = true;

      try {
        const user = JSON.parse(localStorage.getItem("user") || "null") || {};
        const response = await fetch(`/api/projects/${projectId}/evaluation-prealable`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            decision: "dossier_rejete",
            commentaires: commentaire,
            auteur: user.username,
            role: user.role
          })
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Erreur lors de la validation");
        }

        alert("✅ Rejet validé. Le soumissionnaire a été notifié.");
        this.evaluationPrealableCommentaires[projectId] = "";
        if (this.loadProjects) {
          await this.loadProjects();
        }
      } catch (error) {
        alert("Erreur: " + error.message);
      } finally {
        this.envoiEvaluationPrealable[projectId] = false;
      }
    }
  }
};
