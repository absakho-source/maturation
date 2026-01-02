<template>
  <div class="stats-dashboard">
    <h2 class="stats-title">📊 Statistiques</h2>

    <!-- Navigation des onglets statistiques -->
    <div class="stats-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="['tab-btn', { active: activeTab === tab.id }]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Vue d'ensemble -->
    <div v-if="activeTab === 'overview'" class="stats-section">
      <div class="stats-cards">
        <div class="stat-card">
          <h3>📋 Total Projets</h3>
          <div class="stat-value">{{ stats.overview?.total_projets || 0 }}</div>
        </div>
        <div class="stat-card">
          <h3>💰 Coût Total</h3>
          <div class="stat-value">{{ formatCurrency(stats.overview?.cout_total || 0) }}</div>
        </div>
        <div class="stat-card">
          <h3>📊 Coût Moyen</h3>
          <div class="stat-value">{{ formatCurrency(stats.overview?.cout_moyen || 0) }}</div>
        </div>
      </div>

      <!-- Graphique répartition par statut -->
      <div class="chart-container">
        <h3>Répartition par Statut</h3>
        <div class="chart-placeholder" v-if="stats.overview?.statuts">
          <div 
            v-for="(count, statut) in stats.overview.statuts" 
            :key="statut"
            class="bar-item"
          >
            <div class="bar-label">{{ statut }}</div>
            <div class="bar">
              <div 
                class="bar-fill" 
                :style="{ width: (count / stats.overview.total_projets * 100) + '%' }"
              ></div>
              <span class="bar-value">{{ count }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Graphique secteurs -->
      <div class="chart-container">
        <h3>Projets par Secteur</h3>
        <div class="chart-placeholder" v-if="stats.overview?.secteurs">
          <div 
            v-for="(count, secteur) in stats.overview.secteurs" 
            :key="secteur"
            class="bar-item"
          >
            <div class="bar-label">{{ secteur }}</div>
            <div class="bar">
              <div 
                class="bar-fill secteur" 
                :style="{ width: (count / stats.overview.total_projets * 100) + '%' }"
              ></div>
              <span class="bar-value">{{ count }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistiques par secteur -->
    <div v-if="activeTab === 'secteurs'" class="stats-section">
      <h3>Analyse Détaillée par Secteur</h3>

      <!-- Message de chargement -->
      <div v-if="loading" class="loading-message-inline">
        ⏳ Chargement des statistiques par secteur...
      </div>

      <!-- Message si aucune donnée -->
      <div v-else-if="!stats.secteurs || Object.keys(stats.secteurs).length === 0" class="no-data-message">
        Aucune donnée disponible pour les secteurs
      </div>

      <!-- Données des secteurs -->
      <div v-else class="secteurs-grid">
        <div 
          v-for="(data, secteur) in stats.secteurs" 
          :key="secteur"
          class="secteur-card"
        >
          <h4>{{ secteur }}</h4>
          <div class="secteur-metrics">
            <p><strong>Projets:</strong> {{ data.nombre_projets }}</p>
            <p><strong>Coût total:</strong> {{ formatCurrency(data.cout_total) }}</p>
            <p><strong>Coût moyen:</strong> {{ formatCurrency(data.cout_total / data.nombre_projets) }}</p>
          </div>
          
          <div class="mini-chart">
            <h5>Statuts dans ce secteur:</h5>
            <div v-for="(count, statut) in data.statuts" :key="statut" class="mini-bar">
              <span>{{ statut }}: </span>
              <div class="mini-bar-fill" :style="{ width: (count / data.nombre_projets * 100) + '%' }"></div>
              <span>{{ count }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistiques par pôle territorial -->
    <div v-if="activeTab === 'poles'" class="stats-section">
      <h3>Analyse par Pôle Territorial</h3>

      <!-- Message de chargement -->
      <div v-if="loading" class="loading-message-inline">
        ⏳ Chargement des statistiques par pôle...
      </div>

      <!-- Section 1: Tous les projets soumis -->
      <div v-else class="poles-comparison">
        <div class="poles-subsection">
          <h4 class="subsection-title">📋 Tous les projets soumis</h4>

          <!-- Message si aucune donnée -->
          <div v-if="!stats.polesAll || Object.keys(stats.polesAll).length === 0" class="no-data-message">
            Aucune donnée disponible
          </div>

          <!-- Données des pôles (tous projets) -->
          <div v-else class="poles-grid">
            <div
              v-for="(data, pole) in stats.polesAll"
              :key="'all-' + pole"
              class="pole-card"
            >
              <h5>{{ pole }}</h5>
              <div class="pole-metrics">
                <p><strong>Projets:</strong> {{ data.nombre_projets }}</p>
                <p><strong>Coût total:</strong> {{ formatCurrency(data.cout_total) }}</p>
                <p><strong>Coût moyen:</strong> {{ formatCurrency(data.cout_total / data.nombre_projets) }}</p>
              </div>

              <div class="mini-chart">
                <h6>Secteurs dans ce pôle:</h6>
                <div v-for="(count, secteur) in data.secteurs" :key="secteur" class="mini-bar">
                  <span>{{ secteur }}: </span>
                  <div class="mini-bar-fill pole" :style="{ width: (count / data.nombre_projets * 100) + '%' }"></div>
                  <span>{{ count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="poles-divider"></div>

        <!-- Section 2: Projets avec avis favorable -->
        <div class="poles-subsection">
          <h4 class="subsection-title">✅ Projets avec avis favorable ou favorable sous conditions</h4>

          <!-- Message si aucune donnée -->
          <div v-if="!stats.polesFavorable || Object.keys(stats.polesFavorable).length === 0" class="no-data-message">
            Aucun projet avec avis favorable
          </div>

          <!-- Données des pôles (favorables) -->
          <div v-else class="poles-grid">
            <div
              v-for="(data, pole) in stats.polesFavorable"
              :key="'fav-' + pole"
              class="pole-card favorable"
            >
              <h5>{{ pole }}</h5>
              <div class="pole-metrics">
                <p><strong>Projets:</strong> {{ data.nombre_projets }}</p>
                <p><strong>Coût total:</strong> {{ formatCurrency(data.cout_total) }}</p>
                <p><strong>Coût moyen:</strong> {{ formatCurrency(data.cout_total / data.nombre_projets) }}</p>
              </div>

              <div class="mini-chart">
                <h6>Secteurs dans ce pôle:</h6>
                <div v-for="(count, secteur) in data.secteurs" :key="secteur" class="mini-bar">
                  <span>{{ secteur }}: </span>
                  <div class="mini-bar-fill pole" :style="{ width: (count / data.nombre_projets * 100) + '%' }"></div>
                  <span>{{ count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="loading-state">
      <p>⏳ Chargement des statistiques...</p>
    </div>

    <!-- Error state -->
    <div v-if="error" class="error-state">
      <p>❌ Erreur lors du chargement: {{ error }}</p>
      <button @click="loadStats" class="retry-btn">🔄 Réessayer</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatsDashboard',
  props: {
    role: {
      type: String,
      required: true
    },
    username: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      activeTab: 'overview',
      loading: false,
      error: null,
      stats: {
        overview: null,
        secteurs: null,
        polesAll: null,
        polesFavorable: null
      }
    }
  },
  computed: {
    tabs() {
      return [
        { id: 'overview', label: '📊 Vue d\'ensemble' },
        { id: 'secteurs', label: '🏭 Secteurs' },
        { id: 'poles', label: '🗺️ Pôles Territoriaux' }
      ];
    }
  },
  mounted() {
    this.loadStats();
  },
  methods: {
    async loadStats() {
      this.loading = true;
      this.error = null;

      try {
        await Promise.all([
          this.loadOverviewStats(),
          this.loadSecteursStats(),
          this.loadPolesStats()
        ]);
      } catch (error) {
        console.error('Erreur chargement statistiques:', error);
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },

    async loadOverviewStats() {
      const response = await fetch(`/api/stats/overview?role=${this.role}&username=${this.username}`);
      if (!response.ok) throw new Error('Erreur chargement vue d\'ensemble');
      this.stats.overview = await response.json();
    },

    async loadSecteursStats() {
      const response = await fetch(`/api/stats/secteurs?role=${this.role}&username=${this.username}`);
      if (!response.ok) throw new Error('Erreur chargement secteurs');
      this.stats.secteurs = await response.json();
    },

    async loadPolesStats() {
      // Charger les deux jeux de données en parallèle
      const [responseAll, responseFavorable] = await Promise.all([
        fetch(`/api/stats/poles?role=${this.role}&username=${this.username}`),
        fetch(`/api/stats/poles?role=${this.role}&username=${this.username}&filter=favorable`)
      ]);

      if (!responseAll.ok) throw new Error('Erreur chargement pôles (tous projets)');
      if (!responseFavorable.ok) throw new Error('Erreur chargement pôles (favorables)');

      this.stats.polesAll = await responseAll.json();
      this.stats.polesFavorable = await responseFavorable.json();

      console.log('[StatsDashboard] Pôles (tous) chargés:', this.stats.polesAll);
      console.log('[StatsDashboard] Nombre de pôles (tous):', Object.keys(this.stats.polesAll || {}).length);
      console.log('[StatsDashboard] Pôles (favorables) chargés:', this.stats.polesFavorable);
      console.log('[StatsDashboard] Nombre de pôles (favorables):', Object.keys(this.stats.polesFavorable || {}).length);
    },

    formatCurrency(amount) {
      if (!amount) return '0 FCFA';
      
      // Convertir en milliards si > 1 milliard
      if (amount >= 1000000000) {
        return `${(amount / 1000000000).toFixed(1)} Md FCFA`;
      }
      
      // Convertir en millions si > 1 million
      if (amount >= 1000000) {
        return `${(amount / 1000000).toFixed(1)} M FCFA`;
      }
      
      // Formatage avec espaces pour les milliers
      return new Intl.NumberFormat('fr-FR').format(amount) + ' FCFA';
    }
  }
}
</script>

<style scoped>
.stats-dashboard {
  padding: 20px;
  background: #f8f9fa;
  min-height: 100vh;
}

.stats-title {
  color: #2c3e50;
  margin-bottom: 30px;
  text-align: center;
}

/* Onglets */
.stats-tabs {
  display: flex;
  margin-bottom: 30px;
  border-bottom: 2px solid #dee2e6;
  overflow-x: auto;
}

.tab-btn {
  padding: 12px 24px;
  border: none;
  background: transparent;
  color: #6c757d;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
  white-space: nowrap;
}

.tab-btn:hover {
  color: #495057;
  background: #e9ecef;
}

.tab-btn.active {
  color: #007bff;
  border-bottom-color: #007bff;
  background: white;
}

/* Cartes statistiques */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-card h3 {
  color: #6c757d;
  font-size: 14px;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #007bff;
}

/* Graphiques */
.chart-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.chart-container h3 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.bar-item {
  margin-bottom: 15px;
}

.bar-label {
  font-weight: 500;
  margin-bottom: 5px;
  color: #495057;
  font-size: 14px;
}

.bar {
  display: flex;
  align-items: center;
  height: 30px;
  background: #e9ecef;
  border-radius: 15px;
  position: relative;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #007bff, #0056b3);
  border-radius: 15px;
  transition: width 0.8s ease;
  min-width: 20px;
}

.bar-fill.secteur {
  background: linear-gradient(90deg, #28a745, #1e7e34);
}

.bar-fill.pole {
  background: linear-gradient(90deg, #fd7e14, #e55100);
}

.bar-value {
  position: absolute;
  right: 10px;
  font-weight: bold;
  color: #495057;
  font-size: 12px;
}

/* Comparaison des pôles */
.poles-comparison {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.poles-subsection {
  background: #f8f9fa;
  padding: 25px;
  border-radius: 12px;
  border: 2px solid #e9ecef;
}

.subsection-title {
  color: #2c3e50;
  font-size: 1.3em;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 3px solid #007bff;
}

.poles-divider {
  height: 2px;
  background: linear-gradient(to right, transparent, #dee2e6, transparent);
  margin: 20px 0;
}

/* Grilles secteurs/pôles */
.secteurs-grid, .poles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.secteur-card, .pole-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.pole-card.favorable {
  border-left: 4px solid #28a745;
}

.pole-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}

.secteur-card h4, .pole-card h4, .pole-card h5 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.pole-card h5 {
  font-size: 1.1em;
  font-weight: 600;
}

.secteur-metrics, .pole-metrics {
  margin-bottom: 15px;
}

.secteur-metrics p, .pole-metrics p {
  margin: 5px 0;
  color: #6c757d;
}

.mini-chart h5, .mini-chart h6 {
  color: #495057;
  font-size: 14px;
  margin-bottom: 10px;
  font-weight: 600;
}

.mini-bar {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
  font-size: 12px;
}

.mini-bar span:first-child {
  width: 120px;
  color: #6c757d;
}

.mini-bar-fill {
  height: 15px;
  background: #007bff;
  margin: 0 10px;
  border-radius: 8px;
  min-width: 10px;
}

/* États loading/error */
.loading-state, .error-state {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.loading-message-inline,
.no-data-message {
  text-align: center;
  padding: 2rem;
  border-radius: 8px;
  margin: 1rem 0;
  font-size: 1rem;
}

.loading-message-inline {
  background: #f0f9ff;
  color: #0369a1;
  border: 2px solid #bae6fd;
}

.no-data-message {
  background: #fef3c7;
  color: #92400e;
  border: 2px solid #fde68a;
}

.retry-btn {
  margin-top: 15px;
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.retry-btn:hover {
  background: #0056b3;
}

/* Responsive */
@media (max-width: 768px) {
  .stats-dashboard {
    padding: 10px;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .tab-btn {
    padding: 8px 16px;
    font-size: 14px;
  }
}
</style>