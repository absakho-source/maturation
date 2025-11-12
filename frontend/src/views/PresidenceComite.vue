<template>
  <PageWrapper>
    <div class="comite-container">
      <!-- Tableau de bord -->
      <div class="dashboard-section">
        <div class="header-row">
          <h2 class="dashboard-title">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 3v5h5"/>
              <path d="M3 8s2-4 8-4 8 4 8 4"/>
              <path d="M21 21v-5h-5"/>
              <path d="M21 16s-2 4-8 4-8-4-8-4"/>
            </svg>
            Tableau de bord - Présidence Comité
          </h2>
          <button @click="telechargerRapport" class="btn-download-rapport">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            Télécharger Rapport PDF
          </button>
        </div>

      <!-- Statistiques principales -->
      <div class="stats">
        <div class="stat primary clickable" @click="filtrerParStatut(null)" :class="{ active: filtreStatut === null }">
          <span>Total projets</span><strong>{{ allProjects.length }}</strong>
        </div>
        <div class="stat info clickable" @click="filtrerParStatut('soumis')" :class="{ active: filtreStatut === 'soumis' }">
          <span>Soumis</span><strong>{{ countByStatus('soumis') }}</strong>
        </div>
        <div class="stat warning clickable" @click="filtrerParStatut('assigné')" :class="{ active: filtreStatut === 'assigné' }">
          <span>Assignés</span><strong>{{ countByStatus('assigné') }}</strong>
        </div>
        <div class="stat clickable" @click="filtrerParStatut('évalué')" :class="{ active: filtreStatut === 'évalué' }">
          <span>Évalués</span><strong>{{ countByStatus('évalué') }}</strong>
        </div>
        <div class="stat success clickable" @click="filtrerParStatut('validé par secrétariat')" :class="{ active: filtreStatut === 'validé par secrétariat' }">
          <span>Validés secrétariat</span><strong>{{ countByStatus('validé par secrétariat') }}</strong>
        </div>
        <div class="stat success clickable" @click="filtrerParStatut('validé par presidencesct')" :class="{ active: filtreStatut === 'validé par presidencesct' }">
          <span>Validés présidence</span><strong>{{ countByStatus('validé par presidencesct') }}</strong>
        </div>
        <div class="stat warning clickable" @click="filtrerParStatut('en attente validation presidencesct')" :class="{ active: filtreStatut === 'en attente validation presidencesct' }">
          <span>En attente présidence</span><strong>{{ countByStatus('en attente validation presidencesct') }}</strong>
        </div>
        <div class="stat success clickable" @click="filtrerParStatut('approuvé')" :class="{ active: filtreStatut === 'approuvé' }">
          <span>Approuvés</span><strong>{{ countByStatus('approuvé') }}</strong>
        </div>
      </div>

      <!-- Métriques de performance -->
      <div class="performance-metrics">
        <h3>Métriques de performance</h3>
        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-header">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12,6 12,12 16,14"/>
              </svg>
              Temps moyen de traitement
            </div>
            <div class="metric-value">{{ metrics.averageProcessingTime }}</div>
          </div>

          <div class="metric-card">
            <div class="metric-header">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
              Taux de validation
            </div>
            <div class="metric-value">{{ metrics.validationRate }}%</div>
          </div>

          <div class="metric-card">
            <div class="metric-header">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12,6 12,12 16,14"/>
              </svg>
              Délai moyen d'évaluation
            </div>
            <div class="metric-value">{{ metrics.averageEvaluationTime }}</div>
          </div>
        </div>
      </div>

      <!-- Volumes de financement -->
      <div class="financing-volumes">
        <h3>Volumes de financement</h3>
        <div class="financing-cards-grid">
          <div class="financing-card">
            <div class="financing-header">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              <span>Demandes soumises</span>
            </div>
            <div class="financing-amount">{{ formatCurrency(financingStats.totalSubmitted) }}</div>
            <div class="financing-count">{{ financingStats.countSubmitted }} projet(s)</div>
          </div>

          <div class="financing-card success">
            <div class="financing-header">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              <span>Décisions favorables (Comité)</span>
            </div>
            <div class="financing-amount">{{ formatCurrency(financingStats.totalApproved) }}</div>
            <div class="financing-count">{{ financingStats.countApproved }} projet(s)</div>
          </div>
        </div>
      </div>
      </div>

      <div class="tabs">
        <button @click="activeTab = 'all'" :class="{ active: activeTab === 'all' }" class="tab-btn">📋 Tous les projets</button>
        <button @click="activeTab = 'decision'" :class="{ active: activeTab === 'decision' }" class="tab-btn">⚖️ Décision finale</button>
        <button @click="activeTab = 'stats'" :class="{ active: activeTab === 'stats' }" class="tab-btn">📊 Statistiques</button>
        <button @click="activeTab = 'carte'" :class="{ active: activeTab === 'carte' }" class="tab-btn">🗺️ Carte pôles</button>
      </div>

      <!-- Tous les projets -->
      <div v-if="activeTab === 'all'" class="tab-content">
        <h2>Tous les projets (vue d'ensemble)</h2>
        <!-- Badge de filtre actif -->
        <div v-if="filtreStatut" class="filtre-actif">
          <span>Filtre actif: <strong>{{ filtreStatut }}</strong></span>
          <button @click="filtrerParStatut(null)" class="btn-clear-filter">✕ Tout afficher</button>
        </div>
        <div v-if="projetsFiltres.length === 0" class="empty-state">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          <p>Aucun projet{{ filtreStatut ? ' pour ce filtre' : '' }}</p>
        </div>
        <div v-else class="projects-grid">
          <div v-for="p in projetsFiltres" :key="p.id" class="project-card">
            <div class="card-header">
              <div class="card-title-section">
                <div class="project-number">{{ p.numero_projet || 'N/A' }}</div>
                <h3>{{ p.titre }}</h3>
              </div>
              <span class="badge" :class="getStatusClass(p.statut)">{{ p.statut }}</span>
            </div>
            <div class="card-body">
              <p><strong>Auteur:</strong> {{ p.auteur_nom }}</p>
              <p v-if="p.evaluateur_nom" class="highlight-assigned"><strong>Assigné à:</strong> {{ getEvaluateurLabel(p.evaluateur_nom) }}</p>
              <p v-if="p.avis && p.validation_secretariat === 'valide'"><strong>Avis évaluateur:</strong> <span :class="getAvisClass(p.avis)">{{ p.avis }}</span></p>
              <p v-if="p.avis_presidencesct"><strong>Validation SCT:</strong> <span class="validated">{{ p.avis_presidencesct }}</span></p>
              <p v-if="p.decision_finale"><strong>Décision finale:</strong> <span :class="p.decision_finale === 'confirme' ? 'decision-confirme' : 'decision-infirme'">{{ p.decision_finale === 'confirme' ? 'Avis confirmé' : 'Avis infirmé' }}</span></p>
              <button @click="$router.push(`/project/${p.id}`)" class="btn-view">Voir détails</button>

              <!-- Actions de décision finale pour projets validés par la présidence SCT -->
              <div v-if="p.statut === 'validé presidenceSCT' && p.avis_presidencesct === 'valide' && !p.decision_finale" class="final-section">
                <h4>Votre décision finale</h4>
                <p class="instruction">Confirmez-vous l'avis de l'évaluateur ou souhaitez-vous l'infirmer ?</p>
                <div class="decision-buttons">
                  <button @click="confirmer(p.id, 'confirme')" class="btn-success">✓ Confirmer l'avis</button>
                  <button @click="confirmer(p.id, 'infirme')" class="btn-danger">✗ Infirmer l'avis</button>
                </div>
                <label>Commentaires (optionnel):
                  <textarea v-model="commentaires[p.id]" rows="2" placeholder="Justification de votre décision (optionnel)..."></textarea>
                </label>
              </div>
              <div v-else-if="p.statut === 'validé presidenceSCT' && p.validation_secretariat !== 'valide'" class="validation-pending">
                <p style="color: #f59e0b; font-style: italic;">⏳ Avis en attente de validation par le secrétariat SCT</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Décision finale -->
      <div v-if="activeTab === 'decision'" class="tab-content">
        <h2>Projets à statuer (décision finale: confirmer ou infirmer l'avis)</h2>
        <div v-if="projectsToDecide.length === 0" class="empty-state">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          <p>Aucun projet validé en attente de décision finale</p>
        </div>
        <div v-else class="projects-grid">
          <div v-for="p in projectsToDecide" :key="p.id" class="project-card">
            <div class="card-header">
              <div class="card-title-section">
                <div class="project-number">{{ p.numero_projet || 'N/A' }}</div>
                <h3>{{ p.titre }}</h3>
              </div>
              <span class="badge status-validated">{{ p.statut }}</span>
            </div>
            <div class="card-body">
              <p><strong>Auteur:</strong> {{ p.auteur_nom }}</p>
              <p><strong>Évaluateur:</strong> {{ getEvaluateurLabel(p.evaluateur_nom) }}</p>
              <p v-if="p.validation_secretariat === 'valide'"><strong>Avis évaluateur:</strong> <span :class="getAvisClass(p.avis)">{{ p.avis }}</span></p>
              <p v-if="p.commentaires && p.validation_secretariat === 'valide'"><strong>Commentaires évaluateur:</strong> {{ p.commentaires }}</p>
              <div v-if="p.validation_secretariat !== 'valide'" class="validation-pending">
                <p style="color: #f59e0b; font-style: italic;">⏳ Avis en attente de validation par le secrétariat SCT</p>
              </div>
              <p><strong>Validation Présidence SCT:</strong> <span class="validated">{{ p.avis_presidencesct }}</span></p>
              <button @click="$router.push(`/project/${p.id}`)" class="btn-view">Voir détails complets</button>
            </div>
            <div class="final-section">
              <h4>Votre décision finale</h4>
              <p class="instruction">Confirmez-vous l'avis de l'évaluateur ou souhaitez-vous l'infirmer ?</p>
              <div class="decision-buttons">
                <button @click="confirmer(p.id, 'confirme')" class="btn-success">✓ Confirmer l'avis</button>
                <button @click="confirmer(p.id, 'infirme')" class="btn-danger">✗ Infirmer l'avis</button>
              </div>
              <label>Commentaires (optionnel):
                <textarea v-model="commentaires[p.id]" rows="2" placeholder="Justification de votre décision (optionnel)..."></textarea>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Onglet Statistiques -->
      <div v-if="activeTab === 'stats'" class="tab-content">
        <StatsDashboard 
          role="presidencecomite" 
          username="presidencecomite"
        />
      </div>

      <!-- Onglet Carte des pôles territoriaux -->
      <div v-if="activeTab === 'carte'" class="tab-content">
        <CartesPolesComparaison />
      </div>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';
import StatsDashboard from '../components/StatsDashboard.vue';
import CartesPolesComparaison from '../components/CartesPolesComparaison.vue';

export default {
  name: "PresidenceComite",
  components: {
    PageWrapper,
    StatsDashboard,
    CartesPolesComparaison
  },
  data() {
    return {
      allProjects: [],
      commentaires: {},
      activeTab: 'all',
      filtreStatut: null,
      metrics: {
        averageProcessingTime: '0 jours',
        validationRate: 0,
        averageEvaluationTime: '0 jours'
      },
      financingStats: {
        totalSubmitted: 0,
        countSubmitted: 0,
        totalApproved: 0,
        countApproved: 0
      }
    };
  },
  computed: {
    projetsFiltres() {
      if (this.filtreStatut === null) {
        return this.allProjects;
      }
      return this.allProjects.filter(p => p.statut === this.filtreStatut);
    },
    projectsToDecide() {
      return this.allProjects.filter(p => p.statut === 'validé par presidencesct' && !p.decision_finale);
    }
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem("user") || "null") || {};
    fetch(`/api/projects?role=${user.role}&username=${user.username}`)
      .then(r => r.json()).then(j => {
        this.allProjects = j;
        this.calculateFinancingStats();
      });

    // Charger les métriques de performance
    fetch('/api/metrics')
      .then(r => r.json())
      .then(data => {
        this.metrics = {
          averageProcessingTime: data.averageProcessingTime || '0 jours',
          validationRate: data.validationRate || 0,
          averageEvaluationTime: data.averageEvaluationTime || '0 jours'
        };
      })
      .catch(err => console.error('Erreur chargement métriques:', err));
  },
  methods: {
    filtrerParStatut(statut) {
      this.filtreStatut = statut;
      // Basculer vers l'onglet "Tous" si on filtre
      if (statut !== null) {
        this.activeTab = 'all';
      }
    },
    countByStatus(status) {
      return this.allProjects.filter(p => p.statut === status).length;
    },
    confirmer(id, decision) {
      // Confirmation avant décision finale pour éviter clics accidentels
      const actionMessage = decision === 'confirme'
        ? "Êtes-vous sûr de vouloir confirmer cet avis ? Cette décision est finale."
        : "Êtes-vous sûr de vouloir infirmer cet avis ? Cette décision est finale.";

      if (!confirm(actionMessage)) {
        return;
      }

      const user = JSON.parse(localStorage.getItem("user") || "null") || {};
      const com = (this.commentaires[id] || "").trim();
      fetch(`/api/projects/${id}/traiter`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          decision_finale: decision,
          commentaires: com,
          auteur: user.username,
          role: user.role
        })
      }).then(() => {
        alert(decision === 'confirme' ? 'Avis confirmé' : 'Avis infirmé');
        // Rediriger vers la même route pour forcer le rechargement
        this.$router.push('/presidencecomite').then(() => {
          window.location.reload();
        });
      }).catch(error => {
        console.error('Erreur lors de la validation:', error);
        alert('Erreur lors de la validation. Veuillez réessayer.');
      });
    },
    getEvaluateurLabel(ev) {
      const map = { 
        evaluateur1: "Évaluateur 1", 
        evaluateur2: "Évaluateur 2", 
        secretariatsct: "Secrétariat SCT" 
      };
      return map[ev] || ev;
    },
    getStatusClass(statut) {
      const map = {
        "soumis": "status-new",
        "assigné": "status-assigned",
        "évalué": "status-evaluated",
        "validé par secrétariat": "status-validated-sec",
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
    calculateFinancingStats() {
      // Tous les projets soumis
      this.financingStats.countSubmitted = this.allProjects.length;
      this.financingStats.totalSubmitted = this.allProjects.reduce((sum, p) => sum + (p.cout_estimatif || 0), 0);

      // Projets avec décision finale confirmée par la Présidence du Comité
      // Note: decision_finale = 'confirme' (et non 'favorable')
      const approvedProjects = this.allProjects.filter(p => p.decision_finale === 'confirme');
      this.financingStats.countApproved = approvedProjects.length;
      this.financingStats.totalApproved = approvedProjects.reduce((sum, p) => sum + (p.cout_estimatif || 0), 0);
    },
    formatCurrency(value) {
      if (!value) return '0 F CFA';
      return new Intl.NumberFormat('fr-FR', {
        style: 'decimal',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value) + ' F CFA';
    },
    async telechargerRapport() {
      try {
        const response = await fetch('/api/stats/rapport-pdf');
        if (!response.ok) {
          throw new Error('Erreur lors de la génération du rapport');
        }
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `rapport_statistiques_dgppe_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Erreur téléchargement rapport:', error);
        alert('Erreur lors du téléchargement du rapport PDF');
      }
    }
  }
};
</script>

<style scoped>
.comite-container { padding: 1rem; }

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.btn-download-rapport {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--dgppe-accent);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-download-rapport:hover {
  background: var(--dgppe-secondary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-download-rapport svg {
  width: 18px;
  height: 18px;
}

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
  margin-bottom: 24px;
  border-bottom: 2px solid var(--dgppe-accent);
  padding-bottom: 12px;
}

/* Statistiques - Style identique à SecretariatSCT */
.stats { display:flex; gap:.75rem; flex-wrap:wrap; margin-bottom:2rem; }
.stat { background:linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); border:1px solid #e2e8f0; border-radius:8px; padding:.75rem 1rem; transition: all 0.3s ease; }
.stat:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.stat span{color:#6b7280;font-size:.85rem;margin-right:.5rem; font-weight: 500;} .stat strong{color:#111827; font-size: 1.1rem;}
.stat.warning{background:linear-gradient(135deg, #fff3cd 0%, #fef3c7 100%);border-color:#fde68a}
.stat.info{background:linear-gradient(135deg, #d1ecf1 0%, #ecfeff 100%);border-color:#a5f3fc}
.stat.success{background:linear-gradient(135deg, #d1f2eb 0%, #ecfdf5 100%);border-color:#a7f3d0}
.stat.primary{background:linear-gradient(135deg, rgba(46, 107, 107, 0.1) 0%, rgba(72, 181, 181, 0.1) 100%);border-color:var(--dgppe-accent)}

/* Stats cliquables */
.stat.clickable { cursor: pointer; }
.stat.clickable.active {
  border: 2px solid var(--dgppe-primary);
  box-shadow: 0 0 0 3px rgba(46, 107, 107, 0.1);
  transform: scale(1.05);
}

/* Badge filtre actif */
.filtre-actif {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #e0f2fe;
  border: 1px solid #7dd3fc;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
}
.filtre-actif span { color: #0c4a6e; font-size: 0.95rem; }
.filtre-actif strong { color: #075985; }
.btn-clear-filter {
  background: #f97316;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-clear-filter:hover {
  background: #ea580c;
  transform: translateY(-1px);
}

.tabs { display: flex; gap: 0.5rem; margin-bottom: 2rem; border-bottom: 2px solid #e5e7eb; }
.tab-btn { padding: 1rem 2rem; background: transparent; border: none; border-bottom: 3px solid transparent; cursor: pointer; font-size: 1rem; font-weight: 600; color: #6b7280; transition: all 0.3s; }
.tab-btn:hover { color: #2563eb; background: #f0f9ff; }
.tab-btn.active { color: #2563eb; border-bottom-color: #2563eb; background: #f0f9ff; }
.tab-content h2 { margin-bottom: 2rem; color: #1a4d7a; font-size: 1.8rem; font-weight: 600; }
.empty-state { text-align: center; padding: 4rem 2rem; color: #7f8c8d; }
.empty-state svg { margin-bottom: 1rem; color: #bdc3c7; }
.projects-grid { display: grid; gap: 1.5rem; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); }
.project-card { background: white; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); overflow: hidden; transition: transform 0.3s, box-shadow 0.3s; }
.project-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
.card-header { padding: 1.5rem; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-bottom: 2px solid #2563eb; display: flex; justify-content: space-between; align-items: flex-start; }

.card-title-section {
  flex: 1;
  margin-right: 1rem;
}

.project-number {
  background: var(--dgppe-primary);
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
  margin-bottom: 0.5rem;
  letter-spacing: 0.5px;
}

.card-title-section h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #1a4d7a;
  line-height: 1.4;
}
.badge { display: inline-block; padding: 0.35rem 0.85rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; }
.status-new { background: #3b82f6; color: white; }
.status-assigned { background: #f59e0b; color: white; }
.status-evaluated { background: #8b5cf6; color: white; }
.status-validated-sec { background: #06b6d4; color: white; }
.status-pending { background: #8b5cf6; color: white; }
.status-validated { background: #10b981; color: white; }
.status-complement { background: #f97316; color: white; }
.status-confirmed { background: #06b6d4; color: white; }
.status-default { background: #6b7280; color: white; }
.card-body { padding: 1.5rem; }
.card-body p { margin: 0.5rem 0; color: #555; font-size: 0.95rem; }
.highlight-assigned { background: #fef3c7; padding: 0.5rem; border-radius: 6px; border-left: 3px solid #f59e0b; font-weight: 600; }
.avis-favorable { color: #10b981; font-weight: 600; }
.avis-conditions { color: #f59e0b; font-weight: 600; }
.avis-defavorable { color: #ef4444; font-weight: 600; }
.avis-complement { color: #f97316; font-weight: 600; }
.validated { color: #10b981; font-weight: 600; text-transform: capitalize; }
.decision-confirme { color: #10b981; font-weight: 600; }
.decision-infirme { color: #ef4444; font-weight: 600; }
.btn-view { width: 100%; margin-top: 1rem; padding: 0.75rem; background: #6b7280; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s; }
.btn-view:hover { background: #4b5563; }
.final-section { padding: 1.5rem; background: #f8f9fa; border-top: 1px solid #e9ecef; }
.final-section h4 { margin: 0 0 0.75rem 0; color: #1a4d7a; font-size: 1.1rem; font-weight: 600; }
.instruction { margin: 0 0 1rem 0; color: #6b7280; font-size: 0.9rem; }
.decision-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.final-section label { display: block; margin-bottom: 0.75rem; font-weight: 600; color: #2c3e50; font-size: 0.9rem; }
.final-section textarea { width: 100%; padding: 0.75rem; border: 2px solid #dfe6e9; border-radius: 8px; font-size: 0.95rem; transition: border-color 0.3s; }
.final-section textarea:focus { outline: none; border-color: #2563eb; }
.btn-success { padding: 0.85rem; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 1rem; transition: all 0.3s; }
.btn-success:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4); }
.btn-danger { padding: 0.85rem; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 1rem; transition: all 0.3s; }
.btn-danger:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4); }

/* Métriques de performance */
.performance-metrics h3 {
  color: var(--dgppe-primary);
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: 600;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.metric-card {
  background: #ffffff;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s ease;
}

.metric-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: #6c757d;
  font-size: 14px;
  font-weight: 500;
}

.metric-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--dgppe-primary);
}

/* Volumes de financement */
.financing-volumes {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 24px;
  margin-bottom: 24px;
}

.financing-volumes h3 {
  color: var(--dgppe-primary);
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 600;
}

.financing-cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.financing-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 2px solid #dee2e6;
  border-radius: 10px;
  padding: 20px;
  transition: all 0.3s ease;
}

.financing-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.financing-card.success {
  background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
  border-color: #28a745;
}

.financing-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  color: #495057;
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.financing-card.success .financing-header {
  color: #155724;
}

.financing-header svg {
  color: #6c757d;
}

.financing-card.success .financing-header svg {
  color: #28a745;
}

.financing-amount {
  font-size: 28px;
  font-weight: 700;
  color: var(--dgppe-primary);
  margin-bottom: 8px;
}

.financing-card.success .financing-amount {
  color: #28a745;
}

.financing-count {
  font-size: 14px;
  color: #6c757d;
  font-weight: 500;
}

.financing-card.success .financing-count {
  color: #155724;
}

/* Responsive financing cards */
@media (max-width: 768px) {
  .financing-cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>