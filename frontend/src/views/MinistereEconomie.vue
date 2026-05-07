<template>
  <PageWrapper>
    <div class="ministre-container">
      <div class="dashboard-section">
        <h2 class="dashboard-title">🏛️ Tableau de bord — Ministre de l'Économie</h2>
        <div class="info-box">
          Vue d'ensemble de tous les projets soumis à la maturation. Lecture seule.
        </div>

        <!-- Stats -->
        <div class="stats-grid">
          <div class="stat-card stat-card--primary">
            <div class="stat-number">{{ allProjects.length }}</div>
            <div class="stat-label">Total projets</div>
          </div>
          <div class="stat-card stat-card--info">
            <div class="stat-number">{{ countByStatut('en évaluation') + countByStatut('assigné') }}</div>
            <div class="stat-label">En instruction</div>
          </div>
          <div class="stat-card stat-card--success">
            <div class="stat-number">{{ countByAvis('favorable') + countByAvis('favorable sous conditions') }}</div>
            <div class="stat-label">Avis favorable</div>
          </div>
          <div class="stat-card stat-card--danger">
            <div class="stat-number">{{ countByAvis('défavorable') }}</div>
            <div class="stat-label">Avis défavorable</div>
          </div>
          <div class="stat-card stat-card--warning">
            <div class="stat-number">{{ countDecisionComite }}</div>
            <div class="stat-label">Décision Comité</div>
          </div>
        </div>

        <!-- Onglets -->
        <div class="tabs">
          <button @click="activeTab = 'projets'" :class="{ active: activeTab === 'projets' }" class="tab-btn">
            📋 Tous les projets
          </button>
          <button @click="activeTab = 'stats'" :class="{ active: activeTab === 'stats' }" class="tab-btn">
            📊 Statistiques
          </button>
          <button @click="activeTab = 'carte'" :class="{ active: activeTab === 'carte' }" class="tab-btn">
            🗺️ Carte pôles
          </button>
        </div>

        <!-- Onglet Projets -->
        <div v-if="activeTab === 'projets'" class="tab-content">
          <div class="search-bar">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="🔍 Rechercher par titre, secteur, structure, statut…"
              class="search-input"
              aria-label="Rechercher un projet"
            />
          </div>
          <div class="filters-bar">
            <select v-model="filterAnnee" class="filter-select">
              <option value="">Toutes années</option>
              <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
            </select>
            <select v-model="filterSecteur" class="filter-select">
              <option value="">Tous secteurs de planification</option>
              <option v-for="s in secteursList" :key="s" :value="s">{{ s }}</option>
            </select>
            <select v-model="filterPole" class="filter-select">
              <option value="">Tous pôles territoriaux</option>
              <option v-for="p in polesList" :key="p" :value="p">{{ p }}</option>
            </select>
            <select v-model="filterAvis" class="filter-select">
              <option value="">Tous avis</option>
              <option value="favorable">Favorable</option>
              <option value="favorable sous conditions">Favorable sous conditions</option>
              <option value="défavorable">Défavorable</option>
            </select>
            <button v-if="hasActiveFilters" @click="resetFilters" class="btn-reset">↺ Réinitialiser</button>
            <span class="filter-count">{{ filteredProjects.length }} / {{ allProjects.length }}</span>
          </div>

          <ProjectTable :projects="filteredProjects" empty-message="Aucun projet trouvé" />
        </div>

        <!-- Statistiques -->
        <div v-if="activeTab === 'stats'" class="tab-content">
          <StatsDashboard role="ministre_economie" :username="currentUser.username || 'ministre'" />
        </div>

        <!-- Carte -->
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
import ProjectTable from '../components/ProjectTable.vue';

export default {
  name: 'MinistereEconomie',
  components: { PageWrapper, StatsDashboard, CartesPolesComparaison, ProjectTable },
  data() {
    return {
      allProjects: [],
      currentUser: JSON.parse(localStorage.getItem('user') || '{}') || {},
      activeTab: 'projets',
      searchQuery: '',
      filterAnnee: '',
      filterSecteur: '',
      filterPole: '',
      filterAvis: '',
    };
  },
  computed: {
    years() {
      const set = new Set();
      this.allProjects.forEach(p => {
        const yr = (p.numero_projet || '').toString().substring(0, 4);
        if (/^\d{4}$/.test(yr)) set.add(yr);
        else if ((p.numero_projet || '').startsWith('25-')) set.add('2025');
      });
      return [...set].sort().reverse();
    },
    secteursList() {
      return [...new Set(this.allProjects.map(p => p.secteur).filter(Boolean))].sort();
    },
    polesList() {
      const set = new Set();
      this.allProjects.forEach(p => {
        if (!p.poles) return;
        // split parens-aware
        const out = []; let depth = 0; let cur = '';
        for (const c of p.poles) {
          if (c === '(') depth++; else if (c === ')') depth--;
          if (c === ',' && depth === 0) { if (cur.trim()) out.push(cur.trim()); cur = ''; }
          else cur += c;
        }
        if (cur.trim()) out.push(cur.trim());
        out.forEach(po => set.add(po));
      });
      const priority = { 'Dakar': 0, 'Thiès': 1, 'Thies': 1 };
      return [...set].sort((a, b) => {
        const pa = priority[a] ?? 99, pb = priority[b] ?? 99;
        if (pa !== pb) return pa - pb;
        return a.localeCompare(b, 'fr', { sensitivity: 'base' });
      });
    },
    hasActiveFilters() {
      return !!(this.filterAnnee || this.filterSecteur || this.filterPole || this.filterAvis);
    },
    filteredProjects() {
      let list = this.allProjects;
      if (this.filterAnnee) {
        list = list.filter(p => {
          const num = (p.numero_projet || '').toString();
          return num.startsWith(this.filterAnnee) || (this.filterAnnee === '2025' && num.startsWith('25-'));
        });
      }
      if (this.filterSecteur) list = list.filter(p => p.secteur === this.filterSecteur);
      if (this.filterPole) {
        list = list.filter(p => (p.poles || '').includes(this.filterPole));
      }
      if (this.filterAvis) list = list.filter(p => (p.avis || '').toLowerCase() === this.filterAvis);
      const q = (this.searchQuery || '').trim().toLowerCase();
      if (q) {
        list = list.filter(p =>
          (p.titre || '').toLowerCase().includes(q) ||
          (p.secteur || '').toLowerCase().includes(q) ||
          (p.structure_soumissionnaire || '').toLowerCase().includes(q) ||
          (p.organisme_tutelle || '').toLowerCase().includes(q) ||
          (p.statut || '').toLowerCase().includes(q) ||
          (p.numero_projet || '').toLowerCase().includes(q)
        );
      }
      return list;
    },
    countDecisionComite() {
      return this.allProjects.filter(p => p.decision_finale).length;
    },
  },
  mounted() {
    this.loadProjects();
  },
  methods: {
    resetFilters() {
      this.filterAnnee = ''; this.filterSecteur = '';
      this.filterPole = ''; this.filterAvis = '';
    },
    async loadProjects() {
      try {
        const u = this.currentUser;
        const r = await fetch(`/api/projects?role=${u.role}&username=${u.username}`);
        this.allProjects = await r.json();
      } catch (e) { console.error(e); }
    },
    countByStatut(s) { return this.allProjects.filter(p => p.statut === s).length; },
    countByAvis(a) { return this.allProjects.filter(p => p.avis === a).length; },
    getStatusClass(s) {
      const m = {
        'soumis': 'status-new', 'assigné': 'status-assigned',
        'en évaluation': 'status-processing', 'évalué': 'status-evaluated',
        'compléments demandés': 'status-complement', 'rejeté': 'status-defavorable',
      };
      return m[s] || 'status-default';
    },
    getAvisClass(a) {
      if (a === 'favorable') return 'avis-favorable';
      if (a === 'favorable sous conditions') return 'avis-conditions';
      if (a === 'défavorable') return 'avis-defavorable';
      return '';
    },
  }
}
</script>

<style scoped>
.ministre-container { max-width: 1400px; margin: 0 auto; padding: 1.5rem; }
.dashboard-section { background: #fff; border-radius: 12px; padding: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.dashboard-title { color: #1e293b; margin: 0 0 1rem 0; }
.info-box { background: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 0.75rem 1rem; border-radius: 8px; color: #0c4a6e; margin-bottom: 1.5rem; font-size: 0.95rem; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.75rem; margin-bottom: 1.5rem; }
.tabs { display: flex; gap: 0.5rem; margin-bottom: 1.25rem; flex-wrap: wrap; }
.tab-btn { padding: 0.5rem 1rem; border: 2px solid #e2e8f0; border-radius: 8px; background: #fff; cursor: pointer; font-weight: 500; font-size: 0.9rem; }
.tab-btn.active { border-color: #2E6B6B; background: #f0fdfa; color: #2E6B6B; }

.search-bar { display: flex; gap: 0.75rem; margin-bottom: 0.75rem; flex-wrap: wrap; }
.search-input { flex: 1; min-width: 200px; padding: 0.6rem; border: 2px solid #cbd5e1; border-radius: 8px; font-size: 0.9rem; }
.search-input:focus { outline: none; border-color: #0ea5e9; }

.filters-bar {
  display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center;
  margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #e2e8f0;
}
.filters-bar .filter-select {
  padding: 0.5rem 0.75rem; border: 1px solid #cbd5e1; border-radius: 8px;
  background: #fff; color: #1e293b; font-size: 0.875rem; cursor: pointer; min-width: 160px;
}
.filters-bar .filter-select:focus { outline: none; border-color: #2E6B6B; box-shadow: 0 0 0 3px rgba(46, 107, 107, 0.12); }
.filters-bar .btn-reset {
  padding: 0.5rem 0.85rem; background: #fff; border: 1px solid #cbd5e1;
  border-radius: 8px; color: #64748b; font-size: 0.85rem; cursor: pointer;
}
.filters-bar .btn-reset:hover { background: #f1f5f9; color: #2E6B6B; border-color: #2E6B6B; }
.filters-bar .filter-count { margin-left: auto; color: #64748b; font-size: 0.85rem; font-weight: 500; }

.empty-state { text-align: center; padding: 3rem; color: #94a3b8; }

/* Tableau optimisé */
.table-wrap { overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 10px; background: #fff; }
.projects-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.projects-table th, .projects-table td { padding: 0.6rem 0.75rem; text-align: left; border-bottom: 1px solid #e2e8f0; vertical-align: middle; }
.projects-table th { background: #f8fafc; color: #475569; font-weight: 600; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer; user-select: none; white-space: nowrap; }
.projects-table th:hover { background: #f1f5f9; }
.projects-table th.active { color: #2E6B6B; }
.projects-table .th-num { text-align: right; }
.projects-table tr.row-click { cursor: pointer; transition: background 0.15s; }
.projects-table tr.row-click:hover { background: #f0fdfa; }
.projects-table .td-num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.projects-table .td-titre { max-width: 320px; }
.titre-cell { display: flex; flex-direction: column; line-height: 1.25; }
.titre-cell span { font-weight: 500; color: #1e293b; }
.titre-cell small { color: #64748b; font-size: 0.78rem; margin-top: 0.15rem; }

.statut-pill, .avis-pill { padding: 0.15rem 0.55rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600; white-space: nowrap; display: inline-block; }
.avis-pill.avis-favorable { background: #d1fae5; color: #065f46; }
.avis-pill.avis-conditions { background: #fef3c7; color: #92400e; }
.avis-pill.avis-defavorable { background: #fee2e2; color: #991b1b; }

.btn-view-sm { padding: 0.25rem 0.5rem; background: transparent; border: 1px solid #cbd5e1; border-radius: 6px; cursor: pointer; font-size: 0.95rem; }
.btn-view-sm:hover { background: #f1f5f9; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 0.75rem; margin-top: 1rem; color: #64748b; font-size: 0.9rem; }
.pagination button { padding: 0.4rem 0.7rem; border: 1px solid #cbd5e1; background: #fff; border-radius: 6px; cursor: pointer; }
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
.pagination button:hover:not(:disabled) { background: #f1f5f9; }

/* Anciens styles cards conservés (utilisés ailleurs) */
.projects-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 1rem; }
.project-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden; }
.card-header { padding: 1rem; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; }
.card-header h3 { margin: 0; font-size: 1rem; color: #1e293b; }
.project-number { font-size: 0.8rem; color: #64748b; font-family: monospace; }
.badges { display: flex; gap: 0.35rem; flex-wrap: wrap; }
.badge { padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.78rem; font-weight: 600; background: #e2e8f0; color: #334155; white-space: nowrap; }
.badge-import { background: #fef3c7; color: #92400e; }
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

.btn-view { margin-top: 0.75rem; padding: 0.45rem 0.9rem; background: #2E6B6B; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 0.85rem; font-weight: 500; }
.btn-view:hover { background: #1e4b4b; }

@media (max-width: 768px) {
  .projects-grid { grid-template-columns: 1fr; }
  .stats-grid { grid-template-columns: 1fr 1fr; }
}
</style>
