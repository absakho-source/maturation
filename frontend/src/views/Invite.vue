<template>
  <PageWrapper>
    <div class="visiteur-container">
      <!-- Indicateurs clés -->
      <div class="hero">
        <div class="hero-stat">
          <div class="hero-stat-value">{{ statsOverview.total_projets || 0 }}</div>
          <div class="hero-stat-label">Projets soumis</div>
        </div>
        <div class="hero-stat">
          <div class="hero-stat-value">{{ formatBig(coutTotal) }}</div>
          <div class="hero-stat-label">Investissement total</div>
        </div>
        <div class="hero-stat">
          <div class="hero-stat-value">{{ favorablesCount }}</div>
          <div class="hero-stat-label">Avis favorables</div>
        </div>
        <div class="hero-stat">
          <div class="hero-stat-value">{{ Object.keys(statsOverview.poles || {}).length }}</div>
          <div class="hero-stat-label">Pôles concernés</div>
        </div>
      </div>

      <!-- Répartitions visuelles -->
      <div class="charts-row">
        <div class="chart-card">
          <h3>📊 Par secteur d'activité</h3>
          <div class="bars-list">
            <div v-for="(count, secteur) in statsOverview.secteurs" :key="secteur" class="bar-item">
              <div class="bar-label">{{ secteurShort(secteur) }}</div>
              <div class="bar-track">
                <div class="bar-fill bar-fill--primary" :style="{ width: barWidth(count, statsOverview.secteurs) + '%' }"></div>
              </div>
              <div class="bar-count">{{ count }}</div>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <h3>🗺️ Par pôle territorial</h3>
          <div class="bars-list">
            <div v-for="(count, pole) in statsOverview.poles" :key="pole" class="bar-item">
              <div class="bar-label">{{ poleShort(pole) }}</div>
              <div class="bar-track">
                <div class="bar-fill bar-fill--info" :style="{ width: barWidth(count, statsOverview.poles) + '%' }"></div>
              </div>
              <div class="bar-count">{{ count }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Onglets -->
      <div class="tabs">
        <button @click="activeTab = 'projets'" :class="{ active: activeTab === 'projets' }" class="tab-btn">
          📋 Liste des projets
        </button>
        <button @click="activeTab = 'carte'" :class="{ active: activeTab === 'carte' }" class="tab-btn">
          🗺️ Carte des pôles
        </button>
      </div>

      <!-- Onglet Liste -->
      <div v-if="activeTab === 'projets'" class="tab-content">
        <ProjectTable :projects="projects"
                      :columns="{ evaluateur: false, actions: false }"
                      :row-clickable="false"
                      empty-message="Aucun projet disponible" />
      </div>

      <!-- Onglet Carte interactive -->
      <div v-if="activeTab === 'carte'" class="tab-content">
        <CartesPolesComparaison />
      </div>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';
import ProjectTable from '../components/ProjectTable.vue';
import CartesPolesComparaison from '../components/CartesPolesComparaison.vue';

export default {
  name: 'Invite',
  components: {
    PageWrapper, ProjectTable, CartesPolesComparaison
  },
  data() {
    return {
      projects: [],
      activeTab: 'projets',
      statsOverview: {
        total_projets: 0,
        statuts: {},
        secteurs: {},
        poles: {}
      },
    };
  },
  computed: {
    coutTotal() {
      return this.statsOverview.cout_total || 0;
    },
    favorablesCount() {
      const s = this.statsOverview.statuts || {};
      return (s['favorable'] || 0) + (s['favorable sous conditions'] || 0);
    }
  },
  mounted() {
    this.loadData();
  },
  methods: {
    formatBig(v) {
      if (!v) return '0';
      if (v >= 1_000_000_000) return (v / 1_000_000_000).toFixed(1).replace(/\.0$/, '') + ' Md F CFA';
      if (v >= 1_000_000) return (v / 1_000_000).toFixed(0) + ' M F CFA';
      return new Intl.NumberFormat('fr-FR').format(v) + ' F CFA';
    },
    barWidth(count, dict) {
      const max = Math.max(...Object.values(dict || {}), 1);
      return Math.round((count / max) * 100);
    },
    secteurShort(s) {
      if (!s) return '—';
      return s.length > 30 ? s.substring(0, 28) + '…' : s;
    },
    poleShort(p) {
      if (!p) return '—';
      return p.length > 35 ? p.substring(0, 33) + '…' : p;
    },
    statutPublic(statut) {
      // Simplifier les statuts internes pour le grand public
      const map = {
        'soumis': 'Soumis',
        'assigné': 'En instruction',
        'en instruction': 'En instruction',
        'en évaluation': 'En instruction',
        'compléments demandés': 'En instruction',
        'compléments fournis': 'En instruction',
        'en attente validation presidencesct': 'En instruction',
        'validé par presidencesct': 'En instruction',
        'validé par presidencecomite': 'En instruction',
        'en réexamen par le Secrétariat SCT': 'En instruction',
        'évalué': 'Évalué',
        'rejeté': 'Dossier non recevable',
        'avis défavorable confirmé': 'Défavorable',
      };
      return map[statut] || statut || '—';
    },
    async loadData() {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const role = user.role || 'invite';
      const username = user.username || '';

      try {
        // Charger les projets
        const resProjects = await fetch(`/api/projects?role=${role}&username=${username}`);
        if (resProjects.ok) {
          this.projects = await resProjects.json();
        }

        // Charger les statistiques
        const resStats = await fetch(`/api/stats/overview?role=${role}&username=${username}`);
        if (resStats.ok) {
          this.statsOverview = await resStats.json();
        }
      } catch (error) {
        console.error('Erreur lors du chargement des donnees:', error);
      }
    },
    formatDate(dateString) {
      if (!dateString) return '-';
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
      } catch {
        return dateString;
      }
    },
    getStatutClass(statut) {
      if (!statut) return 'default';
      const s = statut.toLowerCase();

      // Statuts spécifiques pour invité/soumissionnaire
      // Soumis
      if (s === 'soumis') return 'new';

      // Assigné
      if (s === 'assigné' || s === 'assigne') return 'assigned';

      // En instruction (statut générique pour évaluation en cours)
      if (s === 'en instruction') return 'pending';

      // Compléments demandés
      if (s === 'compléments demandés' || s === 'complements demandes') return 'complement';

      // Compléments fournis
      if (s === 'compléments fournis' || s === 'complements fournis') return 'complement-provided';

      // Avis favorable (quand projet approuvé)
      if (s === 'favorable' || s === 'avis favorable') return 'favorable';

      // Avis favorable sous conditions (quand projet approuvé)
      if (s === 'favorable sous conditions' || s === 'avis favorable sous conditions') return 'favorable-conditions';

      // Avis défavorable (quand projet approuvé)
      if (s === 'défavorable' || s === 'defavorable' || s === 'avis défavorable' || s === 'avis defavorable') return 'defavorable';

      return 'default';
    },
    applyFilters() {
      // Les filtres sont appliqués automatiquement via computed property
    },
    resetFilters() {
      this.filters.statut = '';
      this.filters.secteur = '';
      this.filters.pole = '';
    }
  }
};
</script>

<style scoped>
.visiteur-container, .invite-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem;
}

/* ==================== HERO (indicateurs clés) ==================== */
.hero {
  background: linear-gradient(135deg, #2E6B6B 0%, #1e4b4b 100%);
  color: #fff;
  border-radius: 16px;
  padding: 1.75rem 1.5rem;
  margin-bottom: 1.5rem;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  box-shadow: 0 8px 24px rgba(46, 107, 107, 0.2);
}
.hero-stat {
  background: rgba(255,255,255,0.12);
  backdrop-filter: blur(10px);
  padding: 1.25rem 1.5rem;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.18);
  text-align: center;
}
.hero-stat-value {
  font-size: 1.85rem;
  font-weight: 800;
  line-height: 1.1;
}
.hero-stat-label {
  font-size: 0.78rem;
  opacity: 0.9;
  margin-top: 0.4rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* ==================== CHARTS ==================== */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.chart-card {
  background: #fff;
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  border: 1px solid #e2e8f0;
}
.chart-card h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  color: #1e293b;
}
.bars-list {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}
.bar-item {
  display: grid;
  grid-template-columns: 180px 1fr 35px;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.85rem;
}
.bar-label {
  color: #475569;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.bar-track {
  background: #f1f5f9;
  border-radius: 6px;
  height: 18px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.4s ease;
}
.bar-fill--primary { background: linear-gradient(90deg, #2E6B6B, #4d8d8d); }
.bar-fill--info    { background: linear-gradient(90deg, #0ea5e9, #38bdf8); }
.bar-count {
  font-weight: 700;
  color: #1e293b;
  text-align: right;
}

/* ==================== TABS ==================== */
.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  border-bottom: 2px solid #e2e8f0;
}
.tab-btn {
  padding: 0.7rem 1.2rem;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  color: #64748b;
  transition: all 0.2s;
}
.tab-btn:hover { color: #2E6B6B; }
.tab-btn.active {
  color: #2E6B6B;
  border-bottom-color: #2E6B6B;
}
.tab-content {
  background: #fff;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.info-message {
  background: #f0f9ff;
  border-left: 4px solid #0ea5e9;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  color: #0c4a6e;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

/* ==================== HEADER (legacy) ==================== */
@media (max-width: 900px) {
  .hero { grid-template-columns: repeat(2, 1fr); padding: 1.25rem; gap: 0.75rem; }
  .hero-stat-value { font-size: 1.5rem; }
  .charts-row { grid-template-columns: 1fr; }
  .bar-item { grid-template-columns: 130px 1fr 30px; }
}
.invite-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

/* ==================== HEADER ==================== */
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.75rem;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.page-title svg {
  color: #004080;
}

.badge-readonly {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #fbbf24;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
}

/* ==================== STATS SECTION ==================== */
.stats-section {
  margin-bottom: 2rem;
}

.stats-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: #e8eef5;
  color: #004080;
  border-radius: 10px;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #718096;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #004080;
}

.stat-mini-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
  padding-right: 8px;
}

/* Scrollbar visible pour indiquer qu'il y a plus d'éléments */
.stat-mini-list::-webkit-scrollbar {
  width: 6px;
}

.stat-mini-list::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.stat-mini-list::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.stat-mini-list::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.stat-mini-item {
  font-size: 0.875rem;
  color: #4a5568;
}

.mini-badge {
  display: inline-block;
  padding: 2px 8px;
  background: #e8eef5;
  color: #004080;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

/* ==================== PROJECTS SECTION ==================== */
.projects-section {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.projects-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
}

.info-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #e0f2fe;
  color: #075985;
  border: 1px solid #7dd3fc;
  border-radius: 8px;
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
}

/* ==================== FILTERS SECTION ==================== */
.filters-section {
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.filters-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #4a5568;
}

.filter-select {
  padding: 0.625rem 0.875rem;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  background: white;
  color: #2d3748;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-select:hover {
  border-color: #004080;
}

.filter-select:focus {
  outline: none;
  border-color: #004080;
  box-shadow: 0 0 0 3px rgba(0, 64, 128, 0.1);
}

.btn-reset-filters {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  background: white;
  color: #64748b;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  align-self: flex-end;
}

.btn-reset-filters:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
  color: #475569;
}

.filter-summary {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.filter-count {
  font-size: 0.875rem;
  color: #4a5568;
  font-weight: 500;
}

.filter-active-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  background: #dbeafe;
  color: #1e40af;
  border: 1px solid #93c5fd;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #718096;
}

.empty-state svg {
  margin: 0 auto 1rem;
  color: #cbd5e0;
}

.empty-state p {
  font-size: 1rem;
  margin: 0;
}

/* ==================== TABLE ==================== */
.table-container {
  overflow-x: auto;
}

.projects-table {
  width: 100%;
  border-collapse: collapse;
}

.projects-table thead {
  background: #f7fafc;
  border-bottom: 2px solid #e2e8f0;
}

.projects-table th {
  padding: 0.875rem 1rem;
  text-align: left;
  font-size: 0.875rem;
  font-weight: 600;
  color: #4a5568;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.projects-table tbody tr {
  border-bottom: 1px solid #e2e8f0;
  transition: background-color 0.2s ease;
}

.projects-table tbody tr:hover {
  background-color: #f7fafc;
}

.projects-table td {
  padding: 1rem;
  font-size: 0.875rem;
  color: #2d3748;
}

.td-numero {
  font-weight: 600;
  color: #004080;
  font-family: 'Courier New', monospace;
}

.td-titre {
  font-weight: 500;
  max-width: 300px;
}

.badge-secteur {
  display: inline-block;
  padding: 4px 10px;
  background: #e8eef5;
  color: #004080;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
}

.td-pole {
  color: #4a5568;
  font-size: 0.8rem;
}

.badge-statut {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
}

/* Status badges - harmonisées avec AdminDashboard */
.statut-new {
  background: #3b82f6 !important;
  color: white !important;
}

.statut-assigned {
  background: #f59e0b !important;
  color: white !important;
}

.statut-pending {
  background: #8b5cf6 !important;
  color: white !important;
}

.statut-validated {
  background: #10b981 !important;
  color: white !important;
}

.statut-complement {
  background: #f97316 !important;
  color: white !important;
}

.statut-complement-provided {
  background: #06b6d4 !important;
  color: white !important;
}

.statut-confirmed {
  background: #06b6d4 !important;
  color: white !important;
}

.statut-favorable {
  background: #10b981 !important;
  color: white !important;
}

.statut-favorable-conditions {
  background: #eab308 !important;
  color: white !important;
}

.statut-defavorable {
  background: #ef4444 !important;
  color: white !important;
}

.statut-rejected {
  background: #dc2626 !important;
  color: white !important;
}

.statut-default {
  background: #6b7280 !important;
  color: white !important;
}

.td-date {
  color: #718096;
  font-size: 0.8rem;
}

/* ==================== RESPONSIVE ==================== */
@media (max-width: 768px) {
  .invite-container {
    padding: 1rem;
  }

  .header-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters-row {
    grid-template-columns: 1fr;
  }

  .btn-reset-filters {
    align-self: stretch;
  }

  .filter-summary {
    flex-direction: column;
    align-items: flex-start;
  }

  .table-container {
    overflow-x: scroll;
  }

  .projects-table {
    min-width: 800px;
  }
}
</style>
