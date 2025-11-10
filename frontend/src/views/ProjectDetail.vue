<!-- filepath: /Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/frontend/src/views/ProjectDetail.vue -->
<template>
  <PageWrapper>
    <div class="project-detail-container" v-if="project">
      <div class="detail-header">
        <button @click="$router.back()" class="btn-back">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          Retour
        </button>
        <span class="badge" :class="getStatusClass(project.statut)">{{ project.statut }}</span>
      </div>

      <div class="detail-content">
        <h1>{{ project.titre }}</h1>
        
        <div class="info-grid">
          <div class="info-card">
            <h3>Informations générales</h3>
            <div class="info-row">
              <span class="label">Auteur:</span>
              <span class="value">{{ project.auteur_nom }}</span>
            </div>
            <div class="info-row">
              <span class="label">Date de soumission:</span>
              <span class="value">{{ formatDateTime(project.date_soumission) }}</span>
            </div>
            <div class="info-row">
              <span class="label">Secteur de planification:</span>
              <span class="value">{{ project.secteur }}</span>
            </div>
            <div class="info-row">
              <span class="label">Zone(s) d'intervention:</span>
              <span class="value">{{ project.poles }}</span>
            </div>
            <div class="info-row" v-if="project.cout_estimatif">
              <span class="label">Coût estimatif:</span>
              <span class="value">{{ formatCurrency(project.cout_estimatif) }} FCFA</span>
            </div>
          </div>

          <div class="info-card" v-if="project.description">
            <h3>Description</h3>
            <p class="description">{{ project.description }}</p>
          </div>

          <!-- Informations sur les compléments -->
          <div class="info-card" v-if="project.complements_reponse_message || project.commentaires">
            <h3>💬 Échanges et compléments</h3>
            
            <div v-if="project.commentaires" class="complement-section">
              <h4>Demande de compléments :</h4>
              <div class="complement-message demande">{{ project.commentaires }}</div>
            </div>
            
            <div v-if="project.complements_reponse_message" class="complement-section">
              <h4>Réponse du soumissionnaire :</h4>
              <div class="complement-message reponse">{{ project.complements_reponse_message }}</div>
              <div v-if="project.complements_reponse_pieces" class="complement-files">
                <strong>📎 Nouvelles pièces jointes :</strong>
                <div class="files-list">
                  <span v-for="(fichier, index) in parseComplementsFiles(project.complements_reponse_pieces)" 
                        :key="index" 
                        class="file-link"
                        @click="ouvrirFichier(fichier)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14,2 14,8 20,8"/>
                      <line x1="16" y1="13" x2="8" y2="13"/>
                      <line x1="16" y1="17" x2="8" y2="17"/>
                      <line x1="10" y1="9" x2="8" y2="9"/>
                    </svg>
                    {{ fichier }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Section Évaluation - masquée pour les soumissionnaires -->
          <div class="info-card" v-if="project.evaluateur_nom && !isSoumissionnaire() && peutVoirEvaluation()">
            <h3>Évaluation</h3>
            <div class="info-row">
              <span class="label">Évaluateur assigné:</span>
              <span class="value">{{ project.evaluateur_display_name || project.evaluateur_nom }}</span>
            </div>
            <div class="info-row" v-if="project.avis">
              <span class="label">Avis:</span>
              <span class="value" :class="getAvisClass(project.avis)">{{ project.avis }}</span>
            </div>
            <div class="info-row" v-if="project.commentaires">
              <span class="label">Commentaires:</span>
              <span class="value">{{ project.commentaires }}</span>
            </div>
          </div>

          <!-- Section Validation Présidence SCT - masquée pour les soumissionnaires -->
          <div class="info-card" v-if="project.avis_presidencesct && !isSoumissionnaire()">
            <h3>Validation Présidence SCT</h3>
            <div class="info-row">
              <span class="label">Décision:</span>
              <span class="value validated">{{ project.avis_presidencesct }}</span>
            </div>
          </div>

          <!-- Section Décision finale - masquée pour les soumissionnaires -->
          <div class="info-card" v-if="project.decision_finale && !isSoumissionnaire()">
            <h3>Décision finale (Présidence Comité)</h3>
            <div class="info-row">
              <span class="label">Décision:</span>
              <span class="value validated">{{ project.decision_finale }}</span>
            </div>
          </div>

          <!-- Section Évaluation Préalable (lecture seule) -->
          <div class="info-card" v-if="project.evaluation_prealable">
            <h3>🔍 Évaluation Préalable</h3>
            <div class="evaluation-prealable-resultat">
              <div :class="['decision-badge', project.evaluation_prealable === 'dossier_evaluable' ? 'success' : 'warning']">
                {{ project.evaluation_prealable === 'dossier_evaluable' ? '✅ Dossier évaluable' : '📝 Compléments requis' }}
              </div>
              <p v-if="project.evaluation_prealable_commentaire" class="commentaire">
                <strong>Commentaire:</strong> {{ project.evaluation_prealable_commentaire }}
              </p>
              <p class="date-evaluation">
                Évaluation effectuée le {{ formatDateTime(project.evaluation_prealable_date) }}
              </p>
            </div>
          </div>

          <!-- Section Fiche d'évaluation PDF - masquée si projet non validé par presidencecomite -->
          <div class="info-card" v-if="ficheEvaluation && project.decision_finale">
            <h3>📋 Fiche d'évaluation</h3>
            <div class="files-list">
              <a @click.prevent="ouvrirFichePDF"
                 href="#"
                 :class="['file-link pdf-link', { 'disabled': !peutAccederFicheEvaluation() }]">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                Fiche d'évaluation détaillée (PDF)
                <span v-if="!peutAccederFicheEvaluation()" class="disabled-hint">
                  (Disponible après évaluation préalable positive)
                </span>
              </a>
            </div>
          </div>

          <!-- Section Historique - masquée pour les soumissionnaires -->
          <div class="info-card" v-if="!isSoumissionnaire()">
            <h3>📋 Historique complet du projet</h3>
            <div v-if="loadingHistorique" class="loading-state">
              <p>Chargement de l'historique...</p>
            </div>
            <div v-else-if="historique.length === 0" class="empty-state">
              <p>Aucun historique disponible</p>
            </div>
            <div v-else class="historique-timeline">
              <div v-for="entry in historique" :key="entry.id" class="timeline-item">
                <div class="timeline-date">{{ formatDateTime(entry.date) }}</div>
                <div class="timeline-content">
                  <div class="timeline-action">{{ entry.action }}</div>
                  <div class="timeline-author">{{ entry.auteur }} ({{ getRoleLabel(entry.role) }})</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Documenthèque du projet - Accessible à tous les membres -->
        <DocumenthequeProjet v-if="project" :projectId="project.id" />

        <!-- Discussion du projet - Espace d'échange entre soumissionnaire et comité -->
        <DiscussionProjet v-if="project" :projectId="project.id" />
      </div>
    </div>
    <div v-else class="loading">Chargement...</div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';
import DocumenthequeProjet from '../components/DocumenthequeProjet.vue';
import DiscussionProjet from '../components/DiscussionProjet.vue';

export default {
  name: "ProjectDetail",
  components: { PageWrapper, DocumenthequeProjet, DiscussionProjet },
  data() {
    return {
      project: null,
      historique: [],
      ficheEvaluation: null,
      loadingHistorique: true,
      currentUser: null
    };
  },
  async mounted() {
    // Récupérer l'utilisateur connecté
    this.currentUser = JSON.parse(localStorage.getItem("user") || "null");

    const id = this.$route.params.id;
    try {
      // Charger les détails du projet
      const projectRes = await fetch(`/api/projects/${id}`);
      this.project = await projectRes.json();

      // Charger l'historique
      const historiqueRes = await fetch(`/api/logs/${id}`);
      this.historique = await historiqueRes.json();

      // Charger la fiche d'évaluation si elle existe
      try {
        const ficheRes = await fetch(`/api/projects/${id}/fiche-evaluation`);
        if (ficheRes.ok) {
          this.ficheEvaluation = await ficheRes.json();
        }
      } catch (ficheErr) {
        console.log('Aucune fiche d\'évaluation disponible');
      }
    } catch (err) {
      console.error(err);
      this.$router.push('/');
    } finally {
      this.loadingHistorique = false;
    }
  },
  methods: {
    formatDate(dateStr) {
      if (!dateStr) return "";
      return new Date(dateStr).toLocaleDateString("fr-FR", {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },
    formatDateTime(dateStr) {
      if (!dateStr) return "";
      return new Date(dateStr).toLocaleString("fr-FR", {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    getRoleLabel(role) {
      const labels = {
        'evaluateur1': 'Évaluateur 1',
        'evaluateur2': 'Évaluateur 2',
        'secretariatsct': 'Secrétariat SCT',
        'presidencesct': 'Présidence SCT',
        'presidencecomite': 'Présidence Comité'
      };
      return labels[role] || role;
    },
    isSoumissionnaire() {
      // Vérification via paramètre URL (le plus fiable)
      if (this.$route.query.from === 'soumissionnaire') {
        return true;
      }

      // Vérification via rôle utilisateur
      if (!this.currentUser) return false;

      const isRoleSoumissionnaire = this.currentUser.role === 'soumissionnaire';
      const isSoumissionnaireByName = this.currentUser.username === 'soumissionnaire';

      return isRoleSoumissionnaire || isSoumissionnaireByName;
    },
    peutVoirEvaluation() {
      // L'évaluation est visible seulement si:
      // 1. L'utilisateur est admin (voit tout sans intervenir)
      // 2. L'utilisateur est évaluateur OU secrétariat SCT (ils voient toujours)
      // 3. OU le secrétariat a validé l'évaluation (pour présidence SCT et comité)
      if (!this.currentUser || !this.project) return false;

      const role = this.currentUser.role;

      // Admin peut tout voir (sans intervenir)
      if (role === 'admin') {
        return true;
      }

      // Évaluateurs et secrétariat peuvent toujours voir
      if (role === 'evaluateur' || role === 'secretariatsct') {
        return true;
      }

      // Pour présidence SCT et comité, vérifier la validation du secrétariat
      if (role === 'presidencesct' || role === 'presidencecomite') {
        return this.project.validation_secretariat === 'valide';
      }

      return false;
    },
    formatCurrency(amount) {
      return new Intl.NumberFormat('fr-FR').format(amount);
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
    },
    
    parseComplementsFiles(filesString) {
      if (!filesString) return [];
      return filesString.split(',').map(f => f.trim()).filter(f => f.length > 0);
    },
    
    ouvrirFichier(fileName) {
      // Ouvrir le fichier dans un nouvel onglet
      const url = `/api/uploads/${fileName}`;
      window.open(url, '_blank');
    },

    ouvrirFichePDF() {
      if (!this.peutAccederFicheEvaluation()) {
        alert('L\'évaluation préalable doit être positive avant d\'accéder à la fiche d\'évaluation détaillée');
        return;
      }
      // Utiliser l'URL du backend (configurée via VITE_API_URL en production)
      const API_BASE_URL = import.meta.env.VITE_API_URL || '';
      window.open(`${API_BASE_URL}/api/projects/${this.project.id}/fiche-evaluation/pdf`, '_blank');
    },

    peutAccederFicheEvaluation() {
      // Peut accéder si:
      // 1. Pas d'évaluation préalable requise (ancien système)
      // 2. OU évaluation préalable positive (dossier évaluable)
      // 3. OU statut >= "en évaluation" (déjà passé l'étape préalable)
      if (!this.project) return false;

      const statutsApres = ['en évaluation', 'évalué', 'validé par presidencesct', 'approuvé', 'rejeté'];

      return !this.project.evaluation_prealable ||
             this.project.evaluation_prealable === 'dossier_evaluable' ||
             statutsApres.includes(this.project.statut);
    }
  }
};
</script>

<style scoped>
.project-detail-container {
  padding: 1rem;
  max-width: 1000px;
  margin: 0 auto;
}
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.btn-back {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: #6b7280;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}
.btn-back:hover {
  background: #4b5563;
}
.badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
}
.status-new { background: #3b82f6; color: white; }
.status-assigned { background: #f59e0b; color: white; }
.status-pending { background: #8b5cf6; color: white; }
.status-validated { background: #10b981; color: white; }
.status-complement { background: #f97316; color: white; }
.status-confirmed { background: #06b6d4; color: white; }
.status-default { background: #6b7280; color: white; }
.detail-content h1 {
  color: #1a4d7a;
  font-size: 2rem;
  margin-bottom: 2rem;
}
.info-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.info-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.info-card h3 {
  color: #1e3a8a;
  font-size: 1.2rem;
  margin: 0 0 1rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e0f2fe;
}
.info-row {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f3f4f6;
}
.info-row:last-child {
  border-bottom: none;
}
.label {
  font-weight: 600;
  color: #374151;
}
.value {
  color: #1f2937;
}
.description {
  color: #374151;
  line-height: 1.6;
  margin: 0;
}
.avis-favorable { color: #10b981; font-weight: 600; }
.avis-conditions { color: #f59e0b; font-weight: 600; }
.avis-defavorable { color: #ef4444; font-weight: 600; }
.avis-complement { color: #f97316; font-weight: 600; }
.validated { color: #10b981; font-weight: 600; text-transform: capitalize; }
.files-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.file-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f0f9ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  color: #1e40af;
  text-decoration: none;
  transition: all 0.3s;
}
.file-link:hover {
  background: #dbeafe;
  transform: translateX(4px);
}
.file-link svg {
  flex-shrink: 0;
}
.loading {
  text-align: center;
  padding: 4rem;
  color: #6b7280;
  font-size: 1.2rem;
}

/* Styles pour l'historique */
.historique-timeline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.timeline-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-left: 4px solid #3b82f6;
  border-radius: 0 8px 8px 0;
  transition: background-color 0.2s;
}

.timeline-item:hover {
  background: #f1f5f9;
}

.timeline-date {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 600;
  white-space: nowrap;
  min-width: 140px;
}

.timeline-content {
  flex: 1;
}

.timeline-action {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.timeline-author {
  font-size: 0.9rem;
  color: #64748b;
  font-style: italic;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}

/* Styles pour les compléments */
.complement-section {
  margin-bottom: 1.5rem;
}

.complement-section h4 {
  color: #1e40af;
  margin-bottom: 0.5rem;
  font-size: 1rem;
}

.complement-message {
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid;
  margin-bottom: 0.5rem;
}

.complement-message.demande {
  background: #fef3c7;
  border-color: #f59e0b;
  color: #92400e;
}

.complement-message.reponse {
  background: #dbeafe;
  border-color: #3b82f6;
  color: #1e40af;
}

.complement-files {
  font-size: 0.9rem;
  color: #64748b;
  margin-top: 0.5rem;
}

.files-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.file-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  color: #3b82f6;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.file-link:hover {
  background: #e2e8f0;
  border-color: #3b82f6;
  color: #1d4ed8;
  transform: translateY(-1px);
}

.file-link svg {
  flex-shrink: 0;
  color: #6b7280;
}

.file-link:hover svg {
  color: #3b82f6;
}

.pdf-link {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  font-weight: 600;
  padding: 0.75rem 1rem;
}

.pdf-link:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.pdf-link svg {
  color: white;
}

.pdf-link:hover svg {
  color: white;
}

/* Évaluation préalable */
.evaluation-prealable-description {
  color: #64748b;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  font-style: italic;
}

.evaluation-prealable-form textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.9rem;
  resize: vertical;
  margin-bottom: 1rem;
}

.evaluation-prealable-buttons {
  display: flex;
  gap: 1rem;
  justify-content: flex-start;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-warning {
  background: #f59e0b;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background: #d97706;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.evaluation-prealable-resultat {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid #10b981;
}

.decision-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.decision-badge.success {
  background: #d1fae5;
  color: #065f46;
}

.decision-badge.warning {
  background: #fef3c7;
  color: #92400e;
}

.evaluation-prealable-resultat .commentaire {
  margin: 0.75rem 0;
  color: #475569;
  font-size: 0.9rem;
}

.evaluation-prealable-resultat .date-evaluation {
  margin: 0;
  color: #94a3b8;
  font-size: 0.85rem;
  font-style: italic;
}

.pdf-link.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

.disabled-hint {
  display: block;
  font-size: 0.75rem;
  color: #f59e0b;
  margin-top: 0.25rem;
}

@media (max-width: 768px) {
  .info-row {
    grid-template-columns: 1fr;
    gap: 0.25rem;
  }

  .evaluation-prealable-buttons {
    flex-direction: column;
  }
}
</style>