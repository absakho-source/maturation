<template>
  <PageWrapper>
    <div class="evaluateur-container">
      <!-- Tableau de bord -->
      <div class="dashboard-section">
        <h2 class="dashboard-title">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 3v5h5"/>
            <path d="M3 8s2-4 8-4 8 4 8 4"/>
            <path d="M21 21v-5h-5"/>
            <path d="M21 16s-2 4-8 4-8-4-8-4"/>
          </svg>
          Tableau de bord - Évaluateur
        </h2>
      </div>

      <h2>Évaluation des projets</h2>
      <div v-if="projects.length === 0" class="empty-state">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        <p>Aucun projet disponible pour le moment</p>
      </div>
      <div v-else>
        <!-- Projets assignés -->
        <div v-if="projetsAssignes.length > 0">
          <h3 class="section-title">📋 Mes projets assignés ({{ projetsAssignes.length }})</h3>
          <div class="projects-grid">
            <div v-for="p in projetsAssignes" :key="p.id" class="project-card project-card-assigned">
          <div class="card-header">
            <h3>{{ p.titre }}</h3>
            <span class="badge" :class="getStatusClass(p.statut)">{{ p.statut }}</span>
          </div>
          <div class="card-body">
            <p><strong>Auteur:</strong> {{ p.auteur_nom }}</p>
            <p><strong>Secteur:</strong> {{ p.secteur }}</p>
            <p v-if="p.poles"><strong>Zones:</strong> {{ p.poles }}</p>
            <p v-if="p.cout_estimatif"><strong>Coût:</strong> {{ formatCurrency(p.cout_estimatif) }}</p>
            <button @click="$router.push(`/project/${p.id}`)" class="btn-view">Voir les détails complets</button>
          </div>
          <!-- Bouton Fiche d'évaluation détaillée (uniquement si dossier évaluable et en évaluation) -->
          <div class="eval-section" v-if="peutAccederFicheEvaluation(p)">
            <div class="eval-options">
              <button @click="$router.push(`/evaluation/${p.id}`)" class="btn-evaluation-detaillee">
                📋 Fiche d'évaluation détaillée
              </button>
            </div>
          </div>

          <!-- Évaluation Préalable (pour projets assignés sans évaluation préalable) -->
          <div class="eval-section eval-prealable" v-else-if="needsEvaluationPrealable(p)">
            <h4>🔍 Évaluation Préalable du Dossier</h4>
            <p class="eval-prealable-description">
              Avant de procéder à l'évaluation détaillée, veuillez vérifier si le dossier est complet et évaluable.
            </p>

            <label>Commentaires:
              <textarea
                v-model="evaluationPrealableCommentaires[p.id]"
                rows="3"
                placeholder="Commentaires (obligatoire si des compléments sont requis)"
              ></textarea>
            </label>

            <div class="eval-prealable-buttons">
              <button
                @click="soumettreEvaluationPrealable(p.id, 'dossier_evaluable')"
                class="btn-success"
                :disabled="envoiEvaluationPrealable[p.id]"
              >
                ✅ Dossier évaluable
              </button>
              <button
                @click="soumettreEvaluationPrealable(p.id, 'complements_requis')"
                class="btn-warning"
                :disabled="envoiEvaluationPrealable[p.id] || !evaluationPrealableCommentaires[p.id]?.trim()"
              >
                📝 Compléments requis
              </button>
              <button
                @click="soumettreEvaluationPrealable(p.id, 'dossier_rejete')"
                class="btn-danger"
                :disabled="envoiEvaluationPrealable[p.id] || !evaluationPrealableCommentaires[p.id]?.trim()"
              >
                ❌ Dossier rejeté
              </button>
            </div>
          </div>

          <!-- Résultat de l'évaluation préalable (lecture seule) -->
          <div class="eval-section eval-prealable-result" v-else-if="p.evaluation_prealable">
            <h4>🔍 Évaluation Préalable</h4>
            <p>
              <strong>Décision:</strong>
              <span :class="getEvaluationPrealableClass(p.evaluation_prealable)">
                {{ getEvaluationPrealableText(p.evaluation_prealable) }}
              </span>
            </p>
            <p v-if="p.evaluation_prealable_commentaire">
              <strong>Commentaires:</strong> {{ p.evaluation_prealable_commentaire }}
            </p>
            <p v-if="p.evaluation_prealable_date" class="eval-date">
              Date: {{ formatDate(p.evaluation_prealable_date) }}
            </p>
          </div>
          <div v-else-if="p.avis" class="eval-done">
            <p><strong>Avis émis:</strong> <span :class="getAvisClass(p.avis)">{{ p.avis }}</span></p>
            <p v-if="p.commentaires"><strong>Commentaires:</strong> {{ p.commentaires }}</p>
          </div>
        </div>
      </div>
        </div>

        <!-- Autres projets de l'équipe -->
        <div v-if="autresProjets.length > 0" class="autres-projets-section">
          <h3 class="section-title">👥 Autres projets de l'équipe ({{ autresProjets.length }})</h3>
          <p class="section-description">Ces projets sont assignés à d'autres évaluateurs. Vous pouvez les consulter mais ne pouvez pas intervenir.</p>
          <div class="projects-grid">
            <div v-for="p in autresProjets" :key="p.id" class="project-card project-card-other">
              <div class="card-header">
                <h3>{{ p.titre }}</h3>
                <span class="badge" :class="getStatusClass(p.statut)">{{ p.statut }}</span>
              </div>
              <div class="card-body">
                <p><strong>Auteur:</strong> {{ p.auteur_nom }}</p>
                <p><strong>Évaluateur assigné:</strong> {{ p.evaluateur_display_name || p.evaluateur_nom || 'Non assigné' }}</p>
                <p><strong>Secteur:</strong> {{ p.secteur }}</p>
                <p v-if="p.poles"><strong>Zones:</strong> {{ p.poles }}</p>
                <p v-if="p.cout_estimatif"><strong>Coût:</strong> {{ formatCurrency(p.cout_estimatif) }}</p>
                <button @click="$router.push(`/project/${p.id}`)" class="btn-view btn-view-readonly">👁️ Voir les détails (lecture seule)</button>
              </div>
              <div class="readonly-badge">
                🔒 Lecture seule
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';

export default {
  name: "Evaluation",
  components: { PageWrapper },
  data() {
    return {
      projects: [],
      avis: {},
      commentaires: {},
      evaluationPrealableCommentaires: {},
      envoiEvaluationPrealable: {}
    };
  },
  computed: {
    projetsAssignes() {
      return this.projects.filter(p => p.est_assigne_a_moi);
    },
    autresProjets() {
      return this.projects.filter(p => !p.est_assigne_a_moi);
    }
  },
  mounted() { this.loadProjects(); },
  methods: {
    async loadProjects() {
      const user = JSON.parse(localStorage.getItem("user") || "null") || {};
      try {
        const response = await fetch(`/api/projects?role=${user.role}&username=${user.username}`);
        const data = await response.json();
        // Force Vue reactivity by creating a new array
        this.projects = [...data];
      } catch (error) {
        console.error('Erreur lors du chargement des projets:', error);
      }
    },
    needsEvaluationPrealable(project) {
      // Afficher l'interface d'évaluation préalable si:
      // - Le projet est assigné ET aucune évaluation préalable n'a été faite
      // OU
      // - Des compléments ont été demandés ET le soumissionnaire a répondu (complements_reponse_message existe)
      //   Dans ce cas, l'évaluateur doit pouvoir réévaluer
      // OU
      // - Le projet est assigné ET il y a une évaluation préalable (réassignation)
      //   Dans ce cas, on ne montre PAS l'interface (on montre le résultat en lecture seule à la place)
      const isInitialAssignment = project.statut === "assigné" && !project.evaluation_prealable;
      const hasReceivedComplements = project.evaluation_prealable === "complements_requis" &&
                                     project.complements_reponse_message &&
                                     project.complements_reponse_message.trim() !== "";

      return isInitialAssignment || hasReceivedComplements;
    },
    peutAccederFicheEvaluation(project) {
      // Le bouton "Fiche d'évaluation détaillée" est visible si:
      // - L'évaluation préalable a été positive (dossier_evaluable)
      // - Le statut est "en évaluation" uniquement (pas après évaluation)
      return project.evaluation_prealable === "dossier_evaluable" &&
             project.statut === "en évaluation";
    },
    async soumettreEvaluationPrealable(projectId, decision) {
      const user = JSON.parse(localStorage.getItem("user") || "null") || {};
      const commentaire = (this.evaluationPrealableCommentaires[projectId] || "").trim();

      // Validation: commentaire obligatoire si compléments requis ou dossier rejeté
      if ((decision === "complements_requis" || decision === "dossier_rejete") && !commentaire) {
        alert("Commentaire obligatoire pour justifier la décision");
        return;
      }

      this.envoiEvaluationPrealable[projectId] = true;

      try {
        const response = await fetch(`/api/projects/${projectId}/evaluation-prealable`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            decision: decision,
            commentaire: commentaire,
            auteur: user.username,
            role: user.role
          })
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.error || "Erreur lors de l'envoi");
        }

        let message;
        if (decision === "dossier_evaluable") {
          message = "Dossier déclaré évaluable. Vous pouvez maintenant accéder à la fiche d'évaluation détaillée.";
        } else if (decision === "complements_requis") {
          message = "Compléments demandés. Le soumissionnaire a été notifié.";
        } else if (decision === "dossier_rejete") {
          message = "Rejet proposé. En attente de validation par le Secrétariat SCT.";
        }
        alert(message);

        // Recharger la page complètement pour forcer l'actualisation
        window.location.reload();
      } catch (error) {
        console.error("Erreur:", error);
        alert("Erreur lors de l'envoi de l'évaluation préalable: " + error.message);
      } finally {
        this.envoiEvaluationPrealable[projectId] = false;
      }
    },
    getEvaluationPrealableText(decision) {
      const map = {
        'dossier_evaluable': '✅ Dossier évaluable',
        'complements_requis': '📝 Compléments requis',
        'dossier_rejete': '❌ Dossier rejeté'
      };
      return map[decision] || decision;
    },
    getEvaluationPrealableClass(decision) {
      const map = {
        'dossier_evaluable': 'decision-evaluable',
        'complements_requis': 'decision-complements',
        'dossier_rejete': 'decision-rejete'
      };
      return map[decision] || '';
    },
    formatCurrency(amount) {
      return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'XOF', minimumFractionDigits: 0 }).format(amount);
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    },
    getStatusClass(statut) {
      const map = {
        "soumis": "status-new",
        "assigné": "status-assigned",
        "en attente validation presidencesct": "status-pending",
        "validé par presidencesct": "status-validated",
        "compléments demandés": "status-complement",
        "décision finale confirmée": "status-confirmed"
      };
      return map[statut] || "status-default";
    },
    getAvisClass(avis) {
      const map = {
        "favorable": "avis-favorable",
        "favorable sous conditions": "avis-conditions",
        "défavorable": "avis-defavorable",
        "compléments demandés": "avis-complement"
      };
      return map[avis] || "";
    }
  }
};
</script>

<style scoped>
.evaluateur-container { padding: 1rem; }

/* Tableau de bord */
.dashboard-section {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 24px;
  margin-bottom: 24px;
}

.dashboard-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 600;
  color: var(--dgppe-primary);
  margin: 0;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--dgppe-accent);
}

h2 { margin-bottom: 2rem; color: #1a4d7a; font-size: 1.8rem; font-weight: 600; }
.empty-state { text-align: center; padding: 4rem 2rem; color: #7f8c8d; }
.empty-state svg { margin-bottom: 1rem; color: #bdc3c7; }
.projects-grid { display: grid; gap: 1.5rem; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); }
.project-card { background: white; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); overflow: hidden; transition: transform 0.3s, box-shadow 0.3s; }
.project-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
.card-header { padding: 1.5rem; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-bottom: 2px solid #2563eb; }
.card-header h3 { margin: 0 0 0.75rem 0; color: #1a4d7a; font-size: 1.2rem; }
.badge { display: inline-block; padding: 0.35rem 0.85rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; }
.status-new { background: #3b82f6; color: white; }
.status-assigned { background: #f59e0b; color: white; }
.status-pending { background: #8b5cf6; color: white; }
.status-validated { background: #10b981; color: white; }
.status-complement { background: #f97316; color: white; }
.status-confirmed { background: #06b6d4; color: white; }
.status-default { background: #6b7280; color: white; }
.card-body { padding: 1.5rem; }
.card-body p { margin: 0.5rem 0; color: #555; font-size: 0.95rem; }
.btn-view { width: 100%; margin-top: 1rem; padding: 0.75rem; background: #6b7280; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s; }
.btn-view:hover { background: #4b5563; }
.eval-section { padding: 1.5rem; background: #f8f9fa; border-top: 1px solid #e9ecef; }

.eval-options {
  margin-bottom: 20px;
  text-align: center;
}

.btn-evaluation-detaillee {
  width: 100%;
  padding: 12px 20px;
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
}

.btn-evaluation-detaillee:hover {
  background: linear-gradient(135deg, #229954 0%, #27ae60 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(39, 174, 96, 0.4);
}

.eval-separator {
  margin: 15px 0;
  color: #7f8c8d;
  font-style: italic;
  font-size: 14px;
}

.eval-simple {
  border-top: 1px solid #ddd;
  padding-top: 15px;
}

.eval-simple h4 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 14px;
}
.eval-section label { display: block; margin-bottom: 0.75rem; font-weight: 600; color: #2c3e50; font-size: 0.9rem; }
.eval-section select, .eval-section textarea { width: 100%; padding: 0.75rem; margin-bottom: 1rem; border: 2px solid #dfe6e9; border-radius: 8px; font-size: 0.95rem; transition: border-color 0.3s; }
.eval-section select:focus, .eval-section textarea:focus { outline: none; border-color: #2563eb; }
.btn-primary { width: 100%; padding: 0.85rem; background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 1rem; transition: all 0.3s; }
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4); }
.eval-done { padding: 1.5rem; background: #f0fdf4; border-top: 1px solid #bbf7d0; }
.eval-done p { margin: 0.5rem 0; color: #166534; font-size: 0.95rem; }
.avis-favorable { color: #10b981; font-weight: 600; }
.avis-conditions { color: #f59e0b; font-weight: 600; }
.avis-defavorable { color: #ef4444; font-weight: 600; }
.avis-complement { color: #f97316; font-weight: 600; }

/* Évaluation Préalable */
.eval-prealable h4 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

.eval-prealable-description {
  margin-bottom: 15px;
  color: #555;
  font-size: 14px;
  line-height: 1.5;
}

.eval-prealable-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 15px;
}

.btn-success {
  padding: 12px 20px;
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(39, 174, 96, 0.3);
}

.btn-success:hover:not(:disabled) {
  background: linear-gradient(135deg, #229954 0%, #27ae60 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.4);
}

.btn-success:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-warning {
  padding: 12px 20px;
  background: linear-gradient(135deg, #f39c12 0%, #f1c40f 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(243, 156, 18, 0.3);
}

.btn-warning:hover:not(:disabled) {
  background: linear-gradient(135deg, #e67e22 0%, #f39c12 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(243, 156, 18, 0.4);
}

.btn-warning:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-danger {
  padding: 12px 20px;
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(231, 76, 60, 0.3);
}

.btn-danger:hover:not(:disabled) {
  background: linear-gradient(135deg, #c0392b 0%, #a93226 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.4);
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Résultat de l'évaluation préalable */
.eval-prealable-result {
  background: #f0f9ff;
  border-top: 1px solid #bfdbfe;
}

.eval-prealable-result h4 {
  margin: 0 0 12px 0;
  color: #1e40af;
  font-size: 16px;
  font-weight: 600;
}

.eval-prealable-result p {
  margin: 8px 0;
  color: #374151;
  font-size: 14px;
}

.decision-evaluable {
  color: #10b981;
  font-weight: 600;
  padding: 4px 8px;
  background: #d1fae5;
  border-radius: 4px;
}

.decision-complements {
  color: #f59e0b;
  font-weight: 600;
  padding: 4px 8px;
  background: #fef3c7;
  border-radius: 4px;
}

.decision-rejete {
  color: #dc2626;
  font-weight: 600;
  padding: 4px 8px;
  background: #fee2e2;
  border-radius: 4px;
}

.eval-date {
  font-size: 13px;
  color: #6b7280;
  font-style: italic;
}

/* Sections */
.section-title {
  margin: 2rem 0 1rem 0;
  color: #1a4d7a;
  font-size: 1.3rem;
  font-weight: 600;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e0f2fe;
}

.section-description {
  margin: 0.5rem 0 1.5rem 0;
  color: #6b7280;
  font-size: 0.95rem;
  font-style: italic;
}

.autres-projets-section {
  margin-top: 3rem;
}

/* Cartes des projets assignés */
.project-card-assigned {
  border-left: 4px solid #10b981;
}

/* Cartes des autres projets */
.project-card-other {
  border-left: 4px solid #9ca3af;
  opacity: 0.85;
  position: relative;
}

.project-card-other:hover {
  opacity: 1;
}

.project-card-other .card-header {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  border-bottom: 2px solid #9ca3af;
}

.project-card-other .card-body {
  background: #fafafa;
}

.readonly-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(107, 114, 128, 0.9);
  color: white;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  backdrop-filter: blur(4px);
}

.btn-view-readonly {
  background: #6b7280;
  cursor: pointer;
}

.btn-view-readonly:hover {
  background: #4b5563;
}
</style>