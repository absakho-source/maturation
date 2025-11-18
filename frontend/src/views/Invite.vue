<template>
  <PageWrapper>
    <div class="invite-container">
      <!-- Header -->
      <div class="header-row">
        <h2 class="page-title">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 16v-4"/>
            <path d="M12 8h.01"/>
          </svg>
          Tableau de bord - Invite
        </h2>
        <div class="badge-readonly">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          Lecture seule
        </div>
      </div>

      <!-- Statistiques générales -->
      <div class="stats-section">
        <h3>Statistiques generales</h3>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 3v18h18"/>
                <path d="M18 17V9"/>
                <path d="M13 17V5"/>
                <path d="M8 17v-3"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-label">Total projets</div>
              <div class="stat-value">{{ statsOverview.total_projets || 0 }}</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-label">Par statut</div>
              <div class="stat-mini-list">
                <div v-for="(count, statut) in statsOverview.statuts" :key="statut" class="stat-mini-item">
                  <span class="mini-badge">{{ statut }}</span>: {{ count }}
                </div>
              </div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-label">Par secteur</div>
              <div class="stat-mini-list">
                <div v-for="(count, secteur) in statsOverview.secteurs" :key="secteur" class="stat-mini-item">
                  <span class="mini-badge">{{ secteur }}</span>: {{ count }}
                </div>
              </div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-label">Par pole territorial</div>
              <div class="stat-mini-list">
                <div v-for="(count, pole) in statsOverview.poles" :key="pole" class="stat-mini-item">
                  <span class="mini-badge">{{ pole }}</span>: {{ count }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Liste des projets -->
      <div class="projects-section">
        <h3>Liste des projets soumis</h3>
        <div class="info-message">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 16v-4"/>
            <path d="M12 8h.01"/>
          </svg>
          En tant qu'invite, vous pouvez consulter uniquement la liste des projets sans acces aux details.
        </div>

        <!-- Filtres -->
        <div class="filters-section">
          <div class="filters-row">
            <div class="filter-group">
              <label class="filter-label">Statut</label>
              <select v-model="filters.statut" @change="applyFilters" class="filter-select">
                <option value="">Tous les statuts</option>
                <option v-for="statut in availableStatuts" :key="statut" :value="statut">{{ statut }}</option>
              </select>
            </div>

            <div class="filter-group">
              <label class="filter-label">Secteur</label>
              <select v-model="filters.secteur" @change="applyFilters" class="filter-select">
                <option value="">Tous les secteurs</option>
                <option v-for="secteur in availableSecteurs" :key="secteur" :value="secteur">{{ secteur }}</option>
              </select>
            </div>

            <div class="filter-group">
              <label class="filter-label">Pole territorial</label>
              <select v-model="filters.pole" @change="applyFilters" class="filter-select">
                <option value="">Tous les poles</option>
                <option v-for="pole in availablePoles" :key="pole" :value="pole">{{ pole }}</option>
              </select>
            </div>

            <button @click="resetFilters" class="btn-reset-filters">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 6h18M3 12h18M3 18h18"/>
              </svg>
              Réinitialiser
            </button>
          </div>

          <div class="filter-summary">
            <span class="filter-count">{{ filteredProjects.length }} projet(s) affiché(s)</span>
            <span v-if="hasActiveFilters" class="filter-active-badge">Filtres actifs</span>
          </div>
        </div>

        <div v-if="filteredProjects.length === 0" class="empty-state">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M9 11l3 3L22 4"/>
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
          </svg>
          <p v-if="hasActiveFilters">Aucun projet ne correspond aux filtres sélectionnés</p>
          <p v-else>Aucun projet disponible pour le moment</p>
        </div>

        <div v-else class="table-container">
          <table class="projects-table">
            <thead>
              <tr>
                <th>Numero</th>
                <th>Titre</th>
                <th>Secteur</th>
                <th>Pole territorial</th>
                <th>Statut</th>
                <th>Date de soumission</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="project in filteredProjects" :key="project.id">
                <td class="td-numero">{{ project.numero_projet }}</td>
                <td class="td-titre">{{ project.titre }}</td>
                <td class="td-secteur">
                  <span class="badge-secteur">{{ project.secteur || '-' }}</span>
                </td>
                <td class="td-pole">{{ project.poles || '-' }}</td>
                <td class="td-statut">
                  <span class="badge-statut" :class="'statut-' + getStatutClass(project.statut)">
                    {{ project.statut || '-' }}
                  </span>
                </td>
                <td class="td-date">{{ formatDate(project.date_soumission) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';

export default {
  name: 'Invite',
  components: {
    PageWrapper
  },
  data() {
    return {
      projects: [],
      statsOverview: {
        total_projets: 0,
        statuts: {},
        secteurs: {},
        poles: {}
      },
      filters: {
        statut: '',
        secteur: '',
        pole: ''
      }
    };
  },
  computed: {
    availableStatuts() {
      return [...new Set(this.projects.map(p => p.statut).filter(Boolean))].sort();
    },
    availableSecteurs() {
      return [...new Set(this.projects.map(p => p.secteur).filter(Boolean))].sort();
    },
    availablePoles() {
      return [...new Set(this.projects.map(p => p.poles).filter(Boolean))].sort();
    },
    filteredProjects() {
      return this.projects.filter(project => {
        if (this.filters.statut && project.statut !== this.filters.statut) return false;
        if (this.filters.secteur && project.secteur !== this.filters.secteur) return false;
        if (this.filters.pole && project.poles !== this.filters.pole) return false;
        return true;
      });
    },
    hasActiveFilters() {
      return this.filters.statut || this.filters.secteur || this.filters.pole;
    }
  },
  mounted() {
    this.loadData();
  },
  methods: {
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
