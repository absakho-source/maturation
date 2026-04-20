<template>
  <PageWrapper>
    <div class="pf-container">
      <div class="dashboard-section">
        <h2 class="dashboard-title">📌 Point Focal — {{ currentUser.point_focal_organisme || currentUser.nom_structure || 'Mon organisme' }}</h2>
        <div class="info-box">
          Projets soumis par ou pour votre organisme de tutelle. Lecture seule.
        </div>

        <!-- Stats -->
        <div class="stats-grid">
          <div class="stat-card stat-card--primary">
            <div class="stat-number">{{ allProjects.length }}</div>
            <div class="stat-label">Total projets</div>
          </div>
          <div class="stat-card stat-card--warning">
            <div class="stat-number">{{ countByFilter(p => !p.avis) }}</div>
            <div class="stat-label">En cours</div>
          </div>
          <div class="stat-card stat-card--success">
            <div class="stat-number">{{ countByFilter(p => p.avis === 'favorable' || p.avis === 'favorable sous conditions') }}</div>
            <div class="stat-label">Favorable</div>
          </div>
          <div class="stat-card stat-card--danger">
            <div class="stat-number">{{ countByFilter(p => p.avis === 'défavorable') }}</div>
            <div class="stat-label">Défavorable</div>
          </div>
        </div>

        <!-- Recherche -->
        <div class="search-bar">
          <input v-model="searchQuery" type="text" placeholder="🔍 Rechercher…" class="search-input" aria-label="Rechercher" />
        </div>

        <!-- Liste projets -->
        <div v-if="filteredProjects.length === 0" class="empty-state">
          <p>Aucun projet trouvé pour votre organisme</p>
        </div>

        <div v-else class="projects-grid">
          <div v-for="p in filteredProjects" :key="p.id" class="project-card">
            <div class="card-header">
              <div>
                <span class="project-number">{{ p.numero_projet || '—' }}</span>
                <h3>{{ p.titre }}</h3>
              </div>
              <span class="badge" :class="getStatusClass(p.statut)">{{ p.statut }}</span>
            </div>
            <div class="card-body">
              <p><strong>Secteur :</strong> {{ p.secteur || '—' }}</p>
              <p v-if="p.cout_estimatif"><strong>Coût :</strong> {{ formatCurrency(p.cout_estimatif) }}</p>
              <p v-if="p.avis"><strong>Avis :</strong> <span :class="getAvisClass(p.avis)">{{ p.avis }}</span></p>
              <p v-if="p.decision_finale"><strong>Comité :</strong> {{ p.decision_finale === 'confirme' ? 'Entériné' : 'Contesté' }}</p>
              <button @click="$router.push(`/project/${p.id}`)" class="btn-view">👁️ Détails</button>
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
  name: 'PointFocalDashboard',
  components: { PageWrapper },
  data() {
    return {
      allProjects: [],
      currentUser: JSON.parse(localStorage.getItem('user') || '{}') || {},
      searchQuery: '',
    };
  },
  computed: {
    filteredProjects() {
      const q = (this.searchQuery || '').trim().toLowerCase();
      if (!q) return this.allProjects;
      return this.allProjects.filter(p =>
        (p.titre || '').toLowerCase().includes(q) ||
        (p.secteur || '').toLowerCase().includes(q) ||
        (p.numero_projet || '').toLowerCase().includes(q) ||
        (p.statut || '').toLowerCase().includes(q)
      );
    }
  },
  mounted() { this.loadProjects(); },
  methods: {
    async loadProjects() {
      try {
        const u = this.currentUser;
        const r = await fetch(`/api/projects?role=${u.role}&username=${u.username}`);
        this.allProjects = await r.json();
      } catch (e) { console.error(e); }
    },
    countByFilter(fn) { return this.allProjects.filter(fn).length; },
    getStatusClass(s) {
      const m = { 'soumis': 'status-new', 'assigné': 'status-assigned', 'en évaluation': 'status-processing', 'évalué': 'status-evaluated', 'compléments demandés': 'status-complement', 'rejeté': 'status-defavorable' };
      return m[s] || 'status-default';
    },
    getAvisClass(a) {
      if (a === 'favorable') return 'avis-favorable';
      if (a === 'favorable sous conditions') return 'avis-conditions';
      if (a === 'défavorable') return 'avis-defavorable';
      return '';
    },
    formatCurrency(v) {
      if (!v) return '—';
      return new Intl.NumberFormat('fr-FR').format(v) + ' F CFA';
    }
  }
}
</script>

<style scoped>
.pf-container { max-width: 1400px; margin: 0 auto; padding: 1.5rem; }
.dashboard-section { background: #fff; border-radius: 12px; padding: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.dashboard-title { color: #1e293b; margin: 0 0 1rem 0; }
.info-box { background: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 0.75rem 1rem; border-radius: 8px; color: #0c4a6e; margin-bottom: 1.5rem; font-size: 0.95rem; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.75rem; margin-bottom: 1.5rem; }
.search-bar { margin-bottom: 1rem; }
.search-input { width: 100%; padding: 0.6rem; border: 2px solid #cbd5e1; border-radius: 8px; font-size: 0.9rem; box-sizing: border-box; }
.search-input:focus { outline: none; border-color: #0ea5e9; }
.empty-state { text-align: center; padding: 3rem; color: #94a3b8; }
.projects-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 1rem; }
.project-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; }
.card-header { padding: 1rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; }
.card-header h3 { margin: 0; font-size: 1rem; color: #1e293b; }
.project-number { font-size: 0.8rem; color: #64748b; font-family: monospace; }
.badge { padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.78rem; font-weight: 600; background: #e2e8f0; color: #334155; }
.status-new { background: #dbeafe; color: #1e40af; }
.status-assigned { background: #e0e7ff; color: #3730a3; }
.status-processing { background: #fef9c3; color: #854d0e; }
.status-evaluated { background: #d1fae5; color: #065f46; }
.status-complement { background: #fce7f3; color: #9d174d; }
.status-defavorable { background: #fee2e2; color: #991b1b; }
.card-body { padding: 1rem; }
.card-body p { margin: 0.3rem 0; font-size: 0.9rem; color: #475569; }
.avis-favorable { color: #059669; font-weight: 600; }
.avis-conditions { color: #d97706; font-weight: 600; }
.avis-defavorable { color: #dc2626; font-weight: 600; }
.btn-view { margin-top: 0.75rem; padding: 0.45rem 0.9rem; background: #2E6B6B; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }
.btn-view:hover { background: #1e4b4b; }
@media (max-width: 768px) { .projects-grid { grid-template-columns: 1fr; } }
</style>
