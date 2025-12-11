<template>
  <div class="test-routes-container">
    <div class="header">
      <h1>Test Visualisation Routes - Sénégal</h1>
      <p class="subtitle">Affichage uniquement des routes sans les pôles territoriaux</p>
    </div>

    <div v-if="error" class="error-banner">
      <strong>❌ Erreur:</strong> {{ error }}
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Routes chargées</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Routes nationales</div>
        <div class="stat-value">{{ stats.nationale }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Routes départementales</div>
        <div class="stat-value">{{ stats.departementale }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Routes locales</div>
        <div class="stat-value">{{ stats.locale }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Points totaux</div>
        <div class="stat-value">{{ stats.points.toLocaleString() }}</div>
      </div>
    </div>

    <div class="map-container">
      <div v-if="loading" class="loading">
        Chargement des routes...
      </div>
      <svg
        v-show="!loading"
        ref="mapSvg"
        :width="mapWidth"
        :height="mapHeight"
        :viewBox="`0 0 ${mapWidth} ${mapHeight}`"
        class="map-svg"
      >
        <!-- Routes -->
        <g class="roads-layer">
          <polyline
            v-for="road in roadSegments"
            :key="road.id"
            :points="getRoadPolylinePoints(road.coordinates)"
            :stroke="getRoadColor(road.type)"
            :stroke-width="getRoadWidth(road.type)"
            :stroke-opacity="getRoadOpacity(road.type)"
            fill="none"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </g>
      </svg>
    </div>

    <div class="legend">
      <h3>Légende</h3>
      <div class="legend-items">
        <div class="legend-item">
          <div class="legend-line" style="background: #2d3748; height: 2.5px; width: 50px; opacity: 1;"></div>
          <span>Autoroutes (2.5px, opacité 100%)</span>
        </div>
        <div class="legend-item">
          <div class="legend-line" style="background: #2d3748; height: 2px; width: 50px; opacity: 0.9;"></div>
          <span>Routes nationales (2px, opacité 90%)</span>
        </div>
        <div class="legend-item">
          <div class="legend-line" style="background: #4a5568; height: 1.5px; width: 50px; opacity: 0.8;"></div>
          <span>Routes départementales (1.5px, opacité 80%)</span>
        </div>
        <div class="legend-item">
          <div class="legend-line" style="background: #718096; height: 1px; width: 50px; opacity: 0.6;"></div>
          <span>Routes locales (1px, opacité 60%)</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TestRoutes',
  data() {
    return {
      loading: true,
      error: null,
      roadSegments: [],
      mapWidth: 1200,
      mapHeight: 800,
      bounds: {
        minLon: -17.5,
        maxLon: -11.3,
        minLat: 12.3,
        maxLat: 16.7
      },
      stats: {
        total: 0,
        nationale: 0,
        departementale: 0,
        locale: 0,
        autoroute: 0,
        points: 0
      }
    }
  },
  async mounted() {
    await this.loadRoads()
  },
  methods: {
    async loadRoads() {
      try {
        this.loading = true
        this.error = null

        const response = await fetch('/senegal_roads_sample.json')
        if (!response.ok) {
          throw new Error(`Erreur HTTP ${response.status}`)
        }

        const roads = await response.json()
        this.roadSegments = [...roads]

        // Calculer les stats
        this.stats.total = roads.length
        let totalPoints = 0

        roads.forEach(road => {
          if (road.coordinates) {
            totalPoints += road.coordinates.length
          }
          if (road.type) {
            this.stats[road.type] = (this.stats[road.type] || 0) + 1
          }
        })

        this.stats.points = totalPoints

        console.log(`✅ ${roads.length} routes chargées`)
        console.log(`📊 Stats:`, this.stats)

        await this.$nextTick()
        this.loading = false

      } catch (err) {
        console.error('❌ Erreur chargement routes:', err)
        this.error = err.message
        this.loading = false
      }
    },

    lonToX(lon) {
      return ((lon - this.bounds.minLon) / (this.bounds.maxLon - this.bounds.minLon)) * this.mapWidth
    },

    latToY(lat) {
      return this.mapHeight - ((lat - this.bounds.minLat) / (this.bounds.maxLat - this.bounds.minLat)) * this.mapHeight
    },

    getRoadPolylinePoints(coordinates) {
      if (!coordinates || coordinates.length === 0) return ''
      return coordinates.map(([lon, lat]) =>
        `${this.lonToX(lon)},${this.latToY(lat)}`
      ).join(' ')
    },

    getRoadColor(type) {
      const colors = {
        'autoroute': '#2d3748',
        'nationale': '#2d3748',
        'departementale': '#4a5568',
        'locale': '#718096'
      }
      return colors[type] || '#718096'
    },

    getRoadWidth(type) {
      const widths = {
        'autoroute': 2.5,
        'nationale': 2,
        'departementale': 1.5,
        'locale': 1
      }
      return widths[type] || 1
    },

    getRoadOpacity(type) {
      const opacities = {
        'autoroute': 1,
        'nationale': 0.9,
        'departementale': 0.8,
        'locale': 0.6
      }
      return opacities[type] || 0.6
    }
  }
}
</script>

<style scoped>
.test-routes-container {
  padding: 30px;
  max-width: 1400px;
  margin: 0 auto;
  background: #f7fafc;
  min-height: 100vh;
}

.header {
  margin-bottom: 30px;
}

.header h1 {
  font-size: 28px;
  color: #2c5282;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 16px;
  color: #718096;
}

.error-banner {
  background: #fed7d7;
  color: #9b2c2c;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border-left: 4px solid #c53030;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #4299e1;
}

.stat-label {
  font-size: 12px;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #2d3748;
}

.map-container {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
  position: relative;
  min-height: 850px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #4a5568;
  font-size: 18px;
}

.map-svg {
  border: 1px solid #e2e8f0;
  background: #ffffff;
  display: block;
}

.legend {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.legend h3 {
  font-size: 18px;
  color: #2d3748;
  margin-bottom: 15px;
}

.legend-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.legend-line {
  display: block;
}

.legend-item span {
  font-size: 14px;
  color: #4a5568;
}

.roads-layer polyline {
  transition: stroke-opacity 0.2s;
}

.roads-layer polyline:hover {
  stroke-opacity: 1 !important;
  stroke-width: 3 !important;
}
</style>
