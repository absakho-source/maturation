<template>
  <PageWrapper>
    <div class="comite-container">
      <!-- Tableau de bord -->
      <div class="dashboard-section">
        <div class="header-row">
          <h2 class="dashboard-title">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 00-3-3.87"/>
              <path d="M16 3.13a4 4 0 010 7.75"/>
            </svg>
            Tableau de bord - Membre du Comité
          </h2>
        </div>

        <!-- Info box -->
        <div class="info-box">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          <span>Vue consultative : vous pouvez consulter les projets soumis au Comité de Maturation ainsi que leurs fiches d'évaluation.</span>
        </div>

        <!-- Statistiques principales -->
        <div class="stats">
          <div class="stat primary">
            <span>Projets au Comité</span><strong>{{ projectsComite.length }}</strong>
          </div>
          <div class="stat success">
            <span>Avis favorable</span><strong>{{ countAvisFavorable }}</strong>
          </div>
          <div class="stat warning">
            <span>Sous conditions</span><strong>{{ countAvisSousConditions }}</strong>
          </div>
          <div class="stat danger">
            <span>Défavorable</span><strong>{{ countAvisDefavorable }}</strong>
          </div>
        </div>

        <div class="tabs">
          <button @click="activeTab = 'projets'" :class="{ active: activeTab === 'projets' }" class="tab-btn">
            🏛️ Projets au Comité
          </button>
          <button @click="activeTab = 'stats'" :class="{ active: activeTab === 'stats' }" class="tab-btn">
            📊 Statistiques
          </button>
          <button @click="activeTab = 'carte'" :class="{ active: activeTab === 'carte' }" class="tab-btn">
            🗺️ Carte pôles
          </button>
        </div>

        <!-- Onglet Projets au Comité -->
        <div v-if="activeTab === 'projets'" class="tab-content">
          <h2>🏛️ Projets soumis au Comité de Maturation</h2>

          <div v-if="projectsComite.length === 0" class="empty-state">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            <p>Aucun projet soumis au Comité pour le moment</p>
          </div>

          <div v-else class="projects-grid">
            <div v-for="p in projectsComite" :key="p.id" class="project-card">
              <div class="card-header">
                <div class="card-title-section">
                  <div class="project-number">{{ p.numero_projet || 'N/A' }}</div>
                  <h3>{{ p.titre }}</h3>
                </div>
                <span class="badge status-comite">🟡 En attente décision</span>
              </div>
              <div class="card-body">
                <p><strong>Structure:</strong> {{ p.structure_soumissionnaire || p.organisme_tutelle || p.auteur_nom || 'N/A' }}</p>
                <p><strong>Secteur:</strong> {{ p.secteur || 'N/A' }}</p>
                <p><strong>Évaluateur:</strong> {{ getEvaluateurLabel(p.evaluateur_nom) }}</p>
                <p v-if="p.avis"><strong>Avis évaluateur:</strong> <span :class="getAvisClass(p.avis)">{{ p.avis }}</span></p>
                <p v-if="p.avis_presidencesct"><strong>Validation SCT:</strong> <span class="validated">{{ p.avis_presidencesct }}</span></p>
                <p v-if="p.montant_global"><strong>Montant:</strong> {{ formatMontant(p.montant_global) }}</p>

                <button @click="$router.push(`/project/${p.id}`)" class="btn-view">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  Voir détails et fiche d'évaluation
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Onglet Statistiques -->
        <div v-if="activeTab === 'stats'" class="tab-content">
          <StatsDashboard
            role="membrecomite"
            :username="currentUser.username || 'membrecomite'"
          />
        </div>

        <!-- Onglet Carte des pôles territoriaux -->
        <div v-if="activeTab === 'carte'" class="tab-content">
          <CartesPolesComparaison />
        </div>
      </div>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';
import StatsDashboard from '../components/StatsDashboard.vue';
import CartesPolesComparaison from '../components/CartesPolesComparaison.vue';

export default {
  name: "MembreComite",
  components: { PageWrapper, StatsDashboard, CartesPolesComparaison },
  data() {
    return {
      allProjects: [],
      currentUser: JSON.parse(localStorage.getItem("user") || "{}") || {},
      activeTab: 'projets'
    };
  },
  computed: {
    projectsComite() {
      // Projets recommandés au Comité (statut_comite = 'recommande_comite')
      // ou anciens projets "validé par presidencecomite" sans decision_finale (compatibilité)
      return this.allProjects.filter(p =>
        p.statut_comite === 'recommande_comite' ||
        (p.statut === 'validé par presidencecomite' && !p.decision_finale)
      );
    },
    countAvisFavorable() {
      return this.projectsComite.filter(p => p.avis === 'favorable').length;
    },
    countAvisSousConditions() {
      return this.projectsComite.filter(p => p.avis === 'favorable sous conditions').length;
    },
    countAvisDefavorable() {
      return this.projectsComite.filter(p => p.avis === 'défavorable').length;
    }
  },
  mounted() {
    const user = JSON.parse(localStorage.getItem("user") || "null") || {};
    fetch(`/api/projects?role=${user.role}&username=${user.username}`)
      .then(r => r.json())
      .then(j => {
        this.allProjects = j;
      });
  },
  methods: {
    getEvaluateurLabel(nom) {
      if (!nom) return 'Non assigné';
      const labels = {
        'evaluateur1': 'Évaluateur 1',
        'evaluateur2': 'Évaluateur 2'
      };
      return labels[nom] || nom;
    },
    getAvisClass(avis) {
      if (!avis) return '';
      const lower = avis.toLowerCase();
      if (lower === 'favorable') return 'avis-favorable';
      if (lower === 'favorable sous conditions') return 'avis-conditions';
      if (lower === 'défavorable') return 'avis-defavorable';
      return '';
    },
    formatMontant(montant) {
      if (!montant) return 'N/A';
      return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'XOF',
        maximumFractionDigits: 0
      }).format(montant);
    }
  }
};
</script>

<style scoped>
.comite-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.dashboard-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.5rem;
  color: #1e293b;
  margin: 0;
}

.dashboard-title svg {
  color: #6366f1;
}

.info-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
  margin-bottom: 1.5rem;
  color: #1e40af;
  font-size: 0.95rem;
}

.info-box svg {
  flex-shrink: 0;
  color: #3b82f6;
}

/* Statistiques */
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat {
  background: #f8fafc;
  border-radius: 10px;
  padding: 1.25rem;
  text-align: center;
  border: 1px solid #e2e8f0;
}

.stat span {
  display: block;
  font-size: 0.85rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.stat strong {
  font-size: 1.75rem;
  color: #1e293b;
}

.stat.primary { background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border-color: #93c5fd; }
.stat.primary strong { color: #1d4ed8; }
.stat.success { background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border-color: #6ee7b7; }
.stat.success strong { color: #059669; }
.stat.warning { background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); border-color: #fcd34d; }
.stat.warning strong { color: #d97706; }
.stat.danger { background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border-color: #fca5a5; }
.stat.danger strong { color: #dc2626; }

/* Onglets */
.tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid #e2e8f0;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  color: #64748b;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #3b82f6;
}

.tab-btn.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}

/* Contenu des onglets */
.tab-content h2 {
  font-size: 1.25rem;
  color: #1e293b;
  margin-bottom: 1.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #94a3b8;
}

.empty-state svg {
  margin-bottom: 1rem;
  opacity: 0.5;
}

/* Grille de projets */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.project-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  transition: all 0.3s;
}

.project-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.card-header {
  padding: 1rem 1.25rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.card-title-section {
  flex: 1;
  min-width: 0;
}

.project-number {
  font-size: 0.8rem;
  font-weight: 600;
  color: #6366f1;
  background: #eef2ff;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
  margin-bottom: 0.5rem;
}

.card-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #1e293b;
  line-height: 1.4;
}

.badge {
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.status-comite {
  background: #fef3c7;
  color: #92400e;
}

.card-body {
  padding: 1.25rem;
}

.card-body p {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  color: #475569;
}

.card-body p strong {
  color: #1e293b;
}

/* Classes d'avis */
.avis-favorable { color: #10b981 !important; font-weight: 600 !important; }
.avis-conditions { color: #f59e0b !important; font-weight: 600 !important; }
.avis-defavorable { color: #ef4444 !important; font-weight: 600 !important; }
.validated { color: #10b981; font-weight: 600; }

/* Bouton voir détails */
.btn-view {
  width: 100%;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-view:hover {
  background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .comite-container {
    padding: 1rem;
  }

  .dashboard-section {
    padding: 1rem;
  }

  .stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .projects-grid {
    grid-template-columns: 1fr;
  }
}
</style>
