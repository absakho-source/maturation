<template>
  <PageWrapper>
    <div class="logs-connexion-page">
      <div class="page-header">
        <h1 class="page-title">Logs de Connexion</h1>
        <p class="page-subtitle">Historique des connexions des utilisateurs à la plateforme</p>
      </div>

      <!-- Filtres -->
      <div class="filters-section">
        <div class="filter-group">
          <label>Utilisateur</label>
          <input
            v-model="filters.username"
            type="text"
            placeholder="Filtrer par nom d'utilisateur"
            class="filter-input"
          />
        </div>
        <div class="filter-group">
          <label>Rôle</label>
          <select v-model="filters.role" class="filter-select">
            <option value="">Tous les rôles</option>
            <option value="admin">Administrateur</option>
            <option value="soumissionnaire">Soumissionnaire</option>
            <option value="evaluateur">Évaluateur</option>
            <option value="secretariatsct">Secrétariat SCT</option>
            <option value="presidencesct">Présidence SCT</option>
            <option value="presidencecomite">Présidence Comité</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Période</label>
          <select v-model="filters.period" class="filter-select">
            <option value="all">Toutes les périodes</option>
            <option value="today">Aujourd'hui</option>
            <option value="week">Cette semaine</option>
            <option value="month">Ce mois</option>
          </select>
        </div>
        <button @click="resetFilters" class="btn btn-secondary">Réinitialiser</button>
      </div>

      <!-- Statistiques -->
      <div class="stats-section">
        <div class="stat-card">
          <div class="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 00-3-3.87"/>
              <path d="M16 3.13a4 4 0 010 7.75"/>
            </svg>
          </div>
          <div class="stat-content">
            <p class="stat-label">Total connexions</p>
            <p class="stat-value">{{ filteredLogs.length }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </div>
          <div class="stat-content">
            <p class="stat-label">Utilisateurs uniques</p>
            <p class="stat-value">{{ uniqueUsers }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          </div>
          <div class="stat-content">
            <p class="stat-label">Dernière connexion</p>
            <p class="stat-value-sm">{{ lastConnectionTime }}</p>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Chargement des logs...</p>
      </div>

      <!-- Table des logs -->
      <div v-else-if="filteredLogs.length > 0" class="logs-table-container">
        <table class="logs-table">
          <thead>
            <tr>
              <th>Date & Heure</th>
              <th>Utilisateur</th>
              <th>Rôle</th>
              <th>Adresse IP</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in paginatedLogs" :key="log.id">
              <td>
                <div class="date-cell">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                  {{ formatDate(log.timestamp) }}
                </div>
              </td>
              <td>
                <div class="user-cell">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                  <span class="username">{{ log.username }}</span>
                </div>
              </td>
              <td>
                <span class="role-badge" :class="`role-${log.role}`">
                  {{ getRoleLabel(log.role) }}
                </span>
              </td>
              <td>
                <span class="ip-address">{{ log.ip_address || 'N/A' }}</span>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="pagination">
          <button
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="btn btn-secondary btn-sm"
          >
            Précédent
          </button>
          <span class="page-info">Page {{ currentPage }} sur {{ totalPages }}</span>
          <button
            @click="currentPage++"
            :disabled="currentPage === totalPages"
            class="btn btn-secondary btn-sm"
          >
            Suivant
          </button>
        </div>
      </div>

      <!-- État vide -->
      <div v-else class="empty-state">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
        </svg>
        <p>Aucun log de connexion trouvé</p>
      </div>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';

export default {
  name: 'LogsConnexion',
  components: {
    PageWrapper
  },
  data() {
    return {
      logs: [],
      loading: true,
      filters: {
        username: '',
        role: '',
        period: 'all'
      },
      currentPage: 1,
      itemsPerPage: 20
    };
  },
  computed: {
    filteredLogs() {
      let filtered = [...this.logs];

      // Filtre par username
      if (this.filters.username) {
        const search = this.filters.username.toLowerCase();
        filtered = filtered.filter(log =>
          log.username.toLowerCase().includes(search)
        );
      }

      // Filtre par rôle
      if (this.filters.role) {
        filtered = filtered.filter(log => log.role === this.filters.role);
      }

      // Filtre par période
      if (this.filters.period !== 'all') {
        const now = new Date();
        filtered = filtered.filter(log => {
          const logDate = new Date(log.timestamp);
          switch(this.filters.period) {
            case 'today':
              return logDate.toDateString() === now.toDateString();
            case 'week':
              const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
              return logDate >= weekAgo;
            case 'month':
              const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
              return logDate >= monthAgo;
            default:
              return true;
          }
        });
      }

      return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    },
    paginatedLogs() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredLogs.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.filteredLogs.length / this.itemsPerPage);
    },
    uniqueUsers() {
      const users = new Set(this.filteredLogs.map(log => log.username));
      return users.size;
    },
    lastConnectionTime() {
      if (this.filteredLogs.length === 0) return 'N/A';
      const latest = this.filteredLogs[0];
      return this.formatDate(latest.timestamp);
    }
  },
  mounted() {
    this.loadLogs();
  },
  methods: {
    async loadLogs() {
      try {
        // Récupérer le rôle de l'utilisateur connecté
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        const role = user.role || 'admin';

        const response = await fetch(`/api/connexion-logs?role=${role}`);
        if (response.ok) {
          const data = await response.json();
          this.logs = data.logs || [];
        } else {
          console.error('Erreur lors du chargement des logs');
        }
      } catch (error) {
        console.error('Erreur:', error);
      } finally {
        this.loading = false;
      }
    },
    formatDate(timestamp) {
      const date = new Date(timestamp);
      return date.toLocaleString('fr-FR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    },
    getRoleLabel(role) {
      const labels = {
        admin: 'Administrateur',
        soumissionnaire: 'Soumissionnaire',
        evaluateur: 'Évaluateur',
        evaluateur1: 'Évaluateur',
        evaluateur2: 'Évaluateur',
        secretariatsct: 'Secrétariat SCT',
        presidencesct: 'Présidence SCT',
        presidencecomite: 'Présidence Comité',
        invite: 'Invité'
      };
      return labels[role] || role;
    },
    resetFilters() {
      this.filters = {
        username: '',
        role: '',
        period: 'all'
      };
      this.currentPage = 1;
    }
  }
};
</script>

<style scoped>
.logs-connexion-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: var(--dgppe-spacing-6);
}

.page-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--dgppe-text);
  margin: 0 0 var(--dgppe-spacing-2) 0;
}

.page-subtitle {
  font-size: 0.95rem;
  color: var(--dgppe-text-muted);
  margin: 0;
}

/* Filtres */
.filters-section {
  display: flex;
  gap: var(--dgppe-spacing-4);
  margin-bottom: var(--dgppe-spacing-6);
  padding: var(--dgppe-spacing-4);
  background: white;
  border-radius: 8px;
  box-shadow: var(--dgppe-shadow-sm);
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
  min-width: 200px;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--dgppe-text);
}

.filter-input,
.filter-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--dgppe-gray-300);
  border-radius: 6px;
  font-size: 0.875rem;
}

/* Statistiques */
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--dgppe-spacing-4);
  margin-bottom: var(--dgppe-spacing-6);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--dgppe-spacing-4);
  padding: var(--dgppe-spacing-4);
  background: white;
  border-radius: 8px;
  box-shadow: var(--dgppe-shadow-sm);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: var(--dgppe-light);
  color: var(--dgppe-primary);
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--dgppe-text-muted);
  margin: 0 0 0.25rem 0;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--dgppe-text);
  margin: 0;
}

.stat-value-sm {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--dgppe-text);
  margin: 0;
}

/* Loading */
.loading-state {
  text-align: center;
  padding: var(--dgppe-spacing-8);
  background: white;
  border-radius: 8px;
  box-shadow: var(--dgppe-shadow-sm);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--dgppe-gray-200);
  border-top-color: var(--dgppe-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto var(--dgppe-spacing-4) auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Table */
.logs-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: var(--dgppe-shadow-sm);
  overflow: hidden;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
}

.logs-table thead {
  background: var(--dgppe-light);
}

.logs-table th {
  padding: var(--dgppe-spacing-4);
  text-align: left;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--dgppe-text);
  border-bottom: 2px solid var(--dgppe-gray-200);
}

.logs-table td {
  padding: var(--dgppe-spacing-4);
  border-bottom: 1px solid var(--dgppe-gray-200);
  font-size: 0.875rem;
}

.logs-table tbody tr:hover {
  background: var(--dgppe-light);
}

.date-cell,
.user-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-cell svg,
.user-cell svg {
  color: var(--dgppe-text-muted);
  flex-shrink: 0;
}

.username {
  font-weight: 500;
  color: var(--dgppe-text);
}

.role-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
  background: var(--dgppe-gray-100);
  color: var(--dgppe-text);
}

.role-badge.role-admin {
  background: #fee;
  color: #c00;
}

.role-badge.role-evaluateur,
.role-badge.role-evaluateur1,
.role-badge.role-evaluateur2 {
  background: #fef3c7;
  color: #92400e;
}

.role-badge.role-soumissionnaire {
  background: #dbeafe;
  color: #1e40af;
}

.role-badge.role-secretariatsct,
.role-badge.role-presidencesct,
.role-badge.role-presidencecomite {
  background: #dcfce7;
  color: #166534;
}

.ip-address {
  font-family: 'Courier New', monospace;
  color: var(--dgppe-text-muted);
  font-size: 0.8rem;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--dgppe-spacing-4);
  padding: var(--dgppe-spacing-4);
  border-top: 1px solid var(--dgppe-gray-200);
}

.page-info {
  font-size: 0.875rem;
  color: var(--dgppe-text-muted);
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: var(--dgppe-spacing-8);
  background: white;
  border-radius: 8px;
  box-shadow: var(--dgppe-shadow-sm);
}

.empty-state svg {
  color: var(--dgppe-gray-400);
  margin-bottom: var(--dgppe-spacing-4);
}

.empty-state p {
  font-size: 1rem;
  color: var(--dgppe-text-muted);
  margin: 0;
}

@media (max-width: 768px) {
  .filters-section {
    flex-direction: column;
  }

  .logs-table {
    font-size: 0.75rem;
  }

  .logs-table th,
  .logs-table td {
    padding: var(--dgppe-spacing-2);
  }
}
</style>
