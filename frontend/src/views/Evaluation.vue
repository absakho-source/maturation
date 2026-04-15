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
        <div class="stats-grid">
          <div class="stat-card stat-total">
            <div class="stat-number">{{ projetsAssignes.length }}</div>
            <div class="stat-label">Mes projets</div>
          </div>
          <div class="stat-card stat-recevabilite">
            <div class="stat-number">{{ statsEvaluateur.enRecevabilite }}</div>
            <div class="stat-label">En recevabilité</div>
          </div>
          <div class="stat-card stat-evaluabilite">
            <div class="stat-number">{{ statsEvaluateur.enEvaluabilite }}</div>
            <div class="stat-label">En évaluabilité</div>
          </div>
          <div class="stat-card stat-evaluation">
            <div class="stat-number">{{ statsEvaluateur.enEvaluation }}</div>
            <div class="stat-label">En évaluation</div>
          </div>
          <div class="stat-card stat-complements">
            <div class="stat-number">{{ statsEvaluateur.complementsEnAttente }}</div>
            <div class="stat-label">Compléments attendus</div>
          </div>
          <div class="stat-card stat-evalues">
            <div class="stat-number">{{ statsEvaluateur.evalues }}</div>
            <div class="stat-label">Avis rendus</div>
          </div>
        </div>
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
            <p><strong>Secteur de planification:</strong> {{ p.secteur }}</p>
            <p v-if="p.poles"><strong>Pôle(s) territorial(aux):</strong> {{ p.poles }}</p>
            <p v-if="p.cout_estimatif"><strong>Coût:</strong> {{ formatCurrency(p.cout_estimatif) }}</p>
            <button @click="$router.push(`/project/${p.id}`)" class="btn-view">👁️ Détails</button>
          </div>
          <!-- Bouton Évaluation simplifiée (uniquement si dossier évaluable) -->
          <div class="eval-section" v-if="peutAccederFicheEvaluation(p)">
            <div class="eval-options">
              <button @click="ouvrirModalEvaluation(p.id)" class="btn-evaluation-detaillee">
                📋 Soumettre l'évaluation
              </button>
            </div>
          </div>

          <!-- Interface d'évaluabilité (après recevabilité, avant évaluation détaillée) -->
          <div v-else-if="needsEvaluabilite(p)" class="eval-section eval-evaluabilite">
            <h4>📊 Évaluabilité du Dossier</h4>
            <p class="eval-info">
              Le dossier est recevable. Décidez de l'évaluabilité.
              La motivation est obligatoire pour « Compléments requis » ou « Rejeter ».
            </p>
            <div class="evaluabilite-form">
              <label :for="'evaluabilite-commentaire-' + p.id">
                <strong>💬 Motivation</strong>
                <span class="label-hint">(Obligatoire pour compléments requis ou rejet)</span>
              </label>
              <textarea
                :id="'evaluabilite-commentaire-' + p.id"
                v-model="evaluabiliteCommentaires[p.id]"
                rows="4"
                placeholder="Clarté des objectifs, faisabilité, cohérence du budget, documents manquants, justification du rejet..."
              ></textarea>
              <div class="eval-actions">
                <button
                  @click="decisionEvaluabilite(p.id, 'evaluable')"
                  class="btn-action btn-success"
                  :disabled="envoiEvaluabilite[p.id]"
                  title="Valider l'évaluabilité"
                >
                  ✓ Évaluable
                </button>
                <button
                  @click="decisionEvaluabilite(p.id, 'complements_requis')"
                  class="btn-action btn-warning"
                  :disabled="envoiEvaluabilite[p.id] || !evaluabiliteCommentaires[p.id]?.trim()"
                  title="Demander des compléments (motivation requise)"
                >
                  📝 Compléments requis
                </button>
                <button
                  @click="decisionEvaluabilite(p.id, 'dossier_rejete')"
                  class="btn-action btn-danger"
                  :disabled="envoiEvaluabilite[p.id] || !evaluabiliteCommentaires[p.id]?.trim()"
                  title="Rejeter le dossier (motivation requise)"
                >
                  ✕ Rejeter
                </button>
              </div>
            </div>
          </div>

          <!-- Matrice d'évaluation de la recevabilité (en modal pour avoir toute la largeur) -->
          <div v-else-if="needsEvaluationPrealable(p)" class="eval-prealable-container">
            <button
              @click="openEvalPrealableModal(p.id)"
              class="btn-toggle-eval-prealable"
            >
              📋 Ouvrir l'évaluation de la recevabilité
            </button>
          </div>

          <!-- Résultat de l'évaluation de la recevabilité (lecture seule) - Affichée uniquement si le dossier est rejeté -->
          <div class="eval-section eval-prealable-result" v-else-if="p.evaluation_prealable === 'dossier_rejete'">
            <h4>🔍 Évaluation de la Recevabilité</h4>
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
                <p><strong>Évaluateur assigné:</strong> {{ getEvaluateurDisplay(p) }}</p>
                <p><strong>Secteur de planification:</strong> {{ p.secteur }}</p>
                <p v-if="p.poles"><strong>Pôle(s) territorial(aux):</strong> {{ p.poles }}</p>
                <p v-if="p.cout_estimatif"><strong>Coût:</strong> {{ formatCurrency(p.cout_estimatif) }}</p>
                <button @click="$router.push(`/project/${p.id}`)" class="btn-view btn-view-readonly">👁️ Détails (lecture seule)</button>
              </div>
              <div class="readonly-badge">
                🔒 Lecture seule
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal pour l'évaluation de la recevabilité - Placé au niveau racine pour affichage correct -->
    <div v-if="modalEvalPrealableId" class="modal-overlay" @click="closeEvalPrealableModal">
      <div class="modal-content" @click.stop>
        <button class="modal-close" @click="closeEvalPrealableModal">✕</button>
        <MatriceEvaluationPrealable
          :projectId="modalEvalPrealableId"
          @evaluation-soumise="handleEvaluationPrealableSubmitted"
        />
      </div>
    </div>

    <!-- Modal pour l'évaluation simplifiée (upload + score + proposition + recommandations) -->
    <div v-if="modalEvalSimpleId" class="modal-overlay" @click="fermerModalEvaluation">
      <div class="modal-content" @click.stop>
        <button class="modal-close" @click="fermerModalEvaluation">✕</button>
        <div class="eval-simple-form">
          <h3>📋 Soumission de l'évaluation</h3>
          <p class="description">
            Uploadez votre fiche d'évaluation (PDF/Word) et, si besoin, des annexes.
            Renseignez ensuite le score, la proposition et la recommandation générale.
          </p>

          <div class="form-group">
            <label><strong>📎 Fichier principal d'évaluation</strong> <span class="req">*</span></label>
            <input type="file" @change="onPrincipalChange" accept=".pdf,.doc,.docx,.odt" />
            <small v-if="evalSimple.fichierPrincipal">{{ evalSimple.fichierPrincipal.name }}</small>
          </div>

          <div class="form-group">
            <label><strong>📎 Annexes</strong> <span class="label-hint">(optionnel, plusieurs fichiers)</span></label>
            <input type="file" multiple @change="onAnnexesChange" />
            <ul v-if="evalSimple.annexes.length" class="file-list">
              <li v-for="(f, i) in evalSimple.annexes" :key="i">{{ f.name }}</li>
            </ul>
          </div>

          <div class="form-group">
            <label><strong>🔢 Score total</strong> <span class="req">*</span> <span class="label-hint">(0 à 100)</span></label>
            <input type="number" min="0" max="100" step="0.5" v-model.number="evalSimple.scoreTotal" />
          </div>

          <div class="form-group">
            <label><strong>📋 Proposition</strong> <span class="req">*</span></label>
            <select v-model="evalSimple.proposition">
              <option value="">— Sélectionner —</option>
              <option value="Favorable">Favorable</option>
              <option value="Favorable sous conditions">Favorable sous conditions</option>
              <option value="Défavorable">Défavorable</option>
            </select>
          </div>

          <div class="form-group">
            <label><strong>💬 Recommandation générale</strong> <span class="req">*</span></label>
            <textarea rows="5" v-model="evalSimple.recommandations"
                      placeholder="Synthèse de la Commission et recommandations principales..."></textarea>
          </div>

          <div class="actions-section">
            <button @click="fermerModalEvaluation" class="btn-action btn-secondary" :disabled="evalSimple.enCours">
              Annuler
            </button>
            <button @click="soumettreEvaluationSimple" class="btn-action btn-success"
                    :disabled="!peutSoumettreEvalSimple || evalSimple.enCours">
              {{ evalSimple.enCours ? '⏳ Envoi...' : '✓ Soumettre l\'évaluation' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';
import MatriceEvaluationPrealable from '../components/MatriceEvaluationPrealable.vue';
import evaluationPrealableMixin from '../mixins/evaluationPrealableMixin.js';

export default {
  name: "Evaluation",
  components: { PageWrapper, MatriceEvaluationPrealable },
  mixins: [evaluationPrealableMixin],
  data() {
    return {
      projects: [],
      avis: {},
      commentaires: {},
      evaluabiliteCommentaires: {},
      envoiEvaluabilite: {},
      modalEvalSimpleId: null,
      evalSimple: {
        fichierPrincipal: null,
        annexes: [],
        scoreTotal: null,
        proposition: "",
        recommandations: "",
        enCours: false
      }
    };
  },
  computed: {
    projetsAssignes() {
      return this.projects.filter(p => p.est_assigne_a_moi);
    },
    autresProjets() {
      return this.projects.filter(p => !p.est_assigne_a_moi);
    },
    peutSoumettreEvalSimple() {
      const e = this.evalSimple;
      return !!e.fichierPrincipal
          && typeof e.scoreTotal === 'number' && e.scoreTotal >= 0 && e.scoreTotal <= 100
          && ['Favorable','Favorable sous conditions','Défavorable'].includes(e.proposition)
          && !!(e.recommandations || '').trim();
    },
    statsEvaluateur() {
      const mes = this.projetsAssignes;
      return {
        // En recevabilité : assigné mais pas encore d'évaluation préalable
        enRecevabilite: mes.filter(p =>
          !p.evaluation_prealable &&
          (p.statut === 'assigné' || p.statut === 'en évaluation')
        ).length,
        // En évaluabilité : recevable mais évaluabilité pas encore confirmée
        enEvaluabilite: mes.filter(p =>
          p.evaluation_prealable === 'dossier_evaluable' && !p.evaluabilite
        ).length,
        // En évaluation détaillée : évaluabilité confirmée, avis non encore rendu
        enEvaluation: mes.filter(p =>
          p.evaluabilite === 'evaluable' && !p.avis
        ).length,
        // Compléments en attente de réception du soumissionnaire
        complementsEnAttente: mes.filter(p =>
          p.statut === 'compléments demandés'
        ).length,
        // Avis rendus (fiche soumise)
        evalues: mes.filter(p => p.avis && p.avis !== 'compléments demandés').length
      };
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
    needsEvaluabilite(project) {
      // L'interface d'évaluabilité est affichée si:
      // - Le dossier est recevable (evaluation_prealable === "dossier_evaluable")
      // - L'évaluabilité n'a pas encore été définie (evaluabilite === null)
      // - Le statut est "en évaluation" ou "assigné"
      return project.evaluation_prealable === "dossier_evaluable" &&
             !project.evaluabilite &&
             (project.statut === "en évaluation" || project.statut === "assigné");
    },
    peutAccederFicheEvaluation(project) {
      // Le bouton "Fiche d'évaluation détaillée" est visible si:
      // - L'évaluation de la recevabilité a été positive (dossier_evaluable)
      // - L'évaluabilité a été confirmée (evaluabilite === "evaluable")
      // - Le statut est "en évaluation" OU "assigné"
      // - Mais PAS après évaluation (évalué, approuvé, rejeté, etc.)
      return project.evaluation_prealable === "dossier_evaluable" &&
             project.evaluabilite === "evaluable" &&
             (project.statut === "en évaluation" || project.statut === "assigné");
    },
    ouvrirModalEvaluation(projectId) {
      this.modalEvalSimpleId = projectId;
      this.evalSimple = {
        fichierPrincipal: null, annexes: [], scoreTotal: null,
        proposition: "", recommandations: "", enCours: false
      };
    },
    fermerModalEvaluation() {
      if (this.evalSimple.enCours) return;
      this.modalEvalSimpleId = null;
    },
    onPrincipalChange(e) {
      this.evalSimple.fichierPrincipal = e.target.files[0] || null;
    },
    onAnnexesChange(e) {
      this.evalSimple.annexes = Array.from(e.target.files || []);
    },
    async soumettreEvaluationSimple() {
      if (!this.peutSoumettreEvalSimple) return;
      const user = JSON.parse(localStorage.getItem("user") || "null") || {};
      const pid = this.modalEvalSimpleId;
      this.evalSimple.enCours = true;
      try {
        const fd = new FormData();
        fd.append("fichier_principal", this.evalSimple.fichierPrincipal);
        this.evalSimple.annexes.forEach(f => fd.append("annexes", f));
        fd.append("score_total", String(this.evalSimple.scoreTotal));
        fd.append("proposition", this.evalSimple.proposition);
        fd.append("recommandations", this.evalSimple.recommandations);
        fd.append("evaluateur_nom", user.username || "");
        fd.append("role", user.role || "");

        const resp = await fetch(`/api/projects/${pid}/evaluation-simple`, {
          method: "POST", body: fd
        });
        if (!resp.ok) {
          const err = await resp.json().catch(() => ({}));
          throw new Error(err.error || "Erreur lors de la soumission");
        }
        alert("✅ Évaluation soumise avec succès.");
        this.modalEvalSimpleId = null;
        await this.loadProjects();
      } catch (err) {
        alert("Erreur : " + err.message);
      } finally {
        this.evalSimple.enCours = false;
      }
    },
    async decisionEvaluabilite(projectId, decision) {
      const user = JSON.parse(localStorage.getItem("user") || "null") || {};
      const commentaire = (this.evaluabiliteCommentaires[projectId] || "").trim();

      if ((decision === "complements_requis" || decision === "dossier_rejete") && !commentaire) {
        alert("⚠️ La motivation est obligatoire pour cette décision.");
        return;
      }

      this.envoiEvaluabilite[projectId] = true;

      try {
        const response = await fetch(`/api/projects/${projectId}/evaluabilite`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            decision,
            commentaire,
            auteur: user.username,
            role: user.role
          })
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Erreur lors de l'enregistrement");
        }

        let message;
        if (decision === "evaluable") {
          message = "✅ Dossier évaluable. Vous pouvez soumettre votre évaluation.";
        } else if (decision === "complements_requis") {
          message = "📝 Compléments demandés. Le soumissionnaire a été notifié.";
        } else {
          message = "✕ Rejet proposé. En attente de validation par le Secrétariat SCT.";
        }
        alert(message);
        this.evaluabiliteCommentaires[projectId] = "";
        await this.loadProjects();
      } catch (error) {
        alert("Erreur: " + error.message);
      } finally {
        this.envoiEvaluabilite[projectId] = false;
      }
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
          message = "Dossier déclaré recevable. Étape suivante : évaluabilité.";
        } else if (decision === "complements_requis") {
          message = "Compléments demandés. Le soumissionnaire a été notifié.";
        } else if (decision === "dossier_rejete") {
          message = "Rejet proposé. En attente de validation par le Secrétariat SCT.";
        }
        alert(message);
        await this.loadProjects();
      } catch (error) {
        console.error("Erreur:", error);
        alert("Erreur lors de l'envoi de l'évaluation de la recevabilité: " + error.message);
      } finally {
        this.envoiEvaluationPrealable[projectId] = false;
      }
    },
    getEvaluateurDisplay(project) {
      // Si evaluateur_display_name existe, l'utiliser
      if (project.evaluateur_display_name) {
        return project.evaluateur_display_name;
      }

      // Si evaluateur_nom existe, l'utiliser
      if (project.evaluateur_nom) {
        return project.evaluateur_nom;
      }

      // Si le projet a un avis mais pas d'évaluateur assigné,
      // c'est probablement une évaluation par le Secrétariat SCT
      if (project.avis) {
        return 'Secrétariat SCT';
      }

      return 'Non assigné';
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
        "en instruction": "status-processing",
        "en évaluation": "status-processing",
        "évalué": "status-evaluated",
        "compléments demandés": "status-complement",
        "compléments fournis": "status-info",
        "en attente validation presidencesct": "status-pending",
        "validé par presidencesct": "status-validated-sec",
        "validé par presidencecomite": "status-validated",
        "favorable": "status-favorable",
        "favorable sous conditions": "status-conditions",
        "défavorable": "status-defavorable",
        "approuvé définitivement par le Comité": "status-validated",
        "rejeté": "status-defavorable",
        "avis défavorable confirmé": "status-defavorable",
        "en réexamen par le Secrétariat SCT": "status-processing"
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

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.stat-card {
  background: #f8fafc;
  border-radius: 10px;
  padding: 16px 12px;
  text-align: center;
  border-left: 4px solid #e2e8f0;
  transition: transform 0.2s;
}

.stat-card:hover { transform: translateY(-2px); }

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
}

.stat-label {
  font-size: 0.78rem;
  color: #64748b;
  margin-top: 6px;
  font-weight: 500;
}

.stat-total    { border-color: #003366; }
.stat-total    .stat-number { color: #003366; }
.stat-recevabilite  { border-color: #f59e0b; }
.stat-recevabilite  .stat-number { color: #f59e0b; }
.stat-evaluabilite  { border-color: #0ea5e9; }
.stat-evaluabilite  .stat-number { color: #0ea5e9; }
.stat-evaluation    { border-color: #8b5cf6; }
.stat-evaluation    .stat-number { color: #8b5cf6; }
.stat-complements   { border-color: #f97316; }
.stat-complements   .stat-number { color: #f97316; }
.stat-evalues       { border-color: #006633; }
.stat-evalues       .stat-number { color: #006633; }

h2 { margin-bottom: 2rem; color: #1a4d7a; font-size: 1.8rem; font-weight: 600; }
.empty-state { text-align: center; padding: 4rem 2rem; color: #7f8c8d; }
.empty-state svg { margin-bottom: 1rem; color: #bdc3c7; }
.projects-grid { display: grid; gap: 1.5rem; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); }
.project-card { background: white; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); overflow: hidden; transition: transform 0.3s, box-shadow 0.3s; }
.project-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
.card-header { padding: 1.5rem; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-bottom: 2px solid #2563eb; }
.card-header h3 { margin: 0 0 0.75rem 0; color: #1a4d7a; font-size: 1.2rem; }
.badge { display: inline-block; padding: 0.35rem 0.85rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; }
.status-new { background: #3b82f6 !important; color: white !important; }
.status-assigned { background: #f59e0b !important; color: white !important; }
.status-processing { background: #0ea5e9 !important; color: white !important; }
.status-evaluated { background: #8b5cf6 !important; color: white !important; }
.status-complement { background: #f97316 !important; color: white !important; }
.status-info { background: #3b82f6 !important; color: white !important; }
.status-pending { background: #8b5cf6 !important; color: white !important; }
.status-validated-sec { background: #22c55e !important; color: white !important; }
.status-validated { background: #10b981 !important; color: white !important; }
.status-favorable { background: #10b981 !important; color: white !important; }
.status-conditions { background: #f59e0b !important; color: white !important; }
.status-defavorable { background: #ef4444 !important; color: white !important; }
.status-confirmed { background: #06b6d4 !important; color: white !important; }
.status-default { background: #6b7280 !important; color: white !important; }
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
.avis-favorable { color: #10b981 !important; font-weight: 600 !important; }
.avis-conditions { color: #f59e0b !important; font-weight: 600 !important; }
.avis-defavorable { color: #ef4444 !important; font-weight: 600 !important; }
.avis-complement { color: #f97316 !important; font-weight: 600 !important; }

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

/* Résultat de l'évaluation de la recevabilité */
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

/* Déplacer le titre vers le bas pour éviter la superposition avec le badge */
.project-card-other .card-header h3 {
  margin-top: 1.5rem; /* Espace pour le badge au-dessus */
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
  z-index: 10;
}

.btn-view-readonly {
  background: #6b7280;
  cursor: pointer;
}

.btn-view-readonly:hover {
  background: #4b5563;
}

/* Section pour le bouton d'ouverture de l'évaluation de la recevabilité */
.eval-prealable-container {
  padding: 1.5rem;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
}

/* Styles pour l'interface d'évaluabilité */
.eval-evaluabilite {
  padding: 1.5rem;
  background: #f0f9ff;
  border-top: 1px solid #bae6fd;
  border-radius: 0 0 12px 12px;
}

.eval-evaluabilite h4 {
  color: #0369a1;
  margin: 0 0 0.75rem 0;
  font-size: 1.1rem;
}

.eval-info {
  color: #0c4a6e;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.evaluabilite-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.evaluabilite-form .eval-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.evaluabilite-form .eval-actions .btn-action {
  flex: 1;
  min-width: 180px;
}

.evaluabilite-form .label-hint {
  display: inline;
  font-weight: 400;
  font-size: 0.85rem;
  color: #64748b;
  margin-left: 0.5rem;
}

.evaluabilite-form label {
  font-weight: 600;
  color: #334155;
  font-size: 0.95rem;
}

.evaluabilite-form .required-label::after {
  content: ' *';
  color: #ef4444;
  font-weight: bold;
}

.evaluabilite-form textarea {
  padding: 0.75rem;
  border: 2px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.95rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.2s;
}

.evaluabilite-form textarea:focus {
  outline: none;
  border-color: #0ea5e9;
}

.btn-toggle-eval-prealable {
  width: 100%;
  padding: 12px 20px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.btn-toggle-eval-prealable:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

/* Modal overlay pour l'évaluation de la recevabilité */
/* Formulaire d'évaluation simplifiée (modal) */
.eval-simple-form h3 {
  color: #0369a1;
  margin-top: 0;
  margin-bottom: 0.5rem;
}
.eval-simple-form .description {
  color: #64748b;
  margin-bottom: 1.25rem;
  font-size: 0.95rem;
}
.eval-simple-form .form-group { margin-bottom: 1rem; }
.eval-simple-form label { display: block; margin-bottom: 0.35rem; color: #1e293b; font-size: 0.95rem; }
.eval-simple-form .req { color: #dc2626; }
.eval-simple-form input[type="file"],
.eval-simple-form input[type="number"],
.eval-simple-form select,
.eval-simple-form textarea {
  width: 100%;
  padding: 0.55rem 0.7rem;
  border: 2px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.9rem;
  font-family: inherit;
  box-sizing: border-box;
}
.eval-simple-form textarea { resize: vertical; }
.eval-simple-form input:focus,
.eval-simple-form select:focus,
.eval-simple-form textarea:focus { outline: none; border-color: #0ea5e9; }
.eval-simple-form .file-list { margin: 0.35rem 0 0 1.1rem; color: #334155; font-size: 0.85rem; }
.eval-simple-form .actions-section {
  display: flex; gap: 0.75rem; justify-content: flex-end; margin-top: 1.25rem;
}
.eval-simple-form .btn-secondary {
  background: #e2e8f0; color: #1e293b; border: none;
  padding: 0.6rem 1rem; border-radius: 8px; cursor: pointer; font-weight: 600;
}
.eval-simple-form .btn-secondary:hover:not(:disabled) { background: #cbd5e1; }

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
  overflow-y: auto;
  overflow-x: hidden;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 1400px;
  width: 100%;
  max-height: none;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  margin: 20px 0;
}

.modal-close {
  position: sticky;
  top: 10px;
  right: 10px;
  float: right;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.modal-close:hover {
  background: #dc2626;
  transform: scale(1.1);
}
</style>