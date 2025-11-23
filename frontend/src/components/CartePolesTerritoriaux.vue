<template>
  <div class="carte-poles-container">
    <h3 class="titre-carte">{{ title }}</h3>
    
    <div class="carte-wrapper">
      <!-- Légende des investissements avec seuils dynamiques -->
      <div class="legende-investissement">
        <h4>Investissement Total</h4>
        <div class="legende-items">
          <div class="legende-item">
            <div class="couleur-box" style="background: #1a4d1a"></div>
            <span>Très élevé (>{{ formatAmount(intensityThresholds.q80) }})</span>
          </div>
          <div class="legende-item">
            <div class="couleur-box" style="background: #2d6b2d"></div>
            <span>Élevé ({{ formatAmount(intensityThresholds.q60) }}-{{ formatAmount(intensityThresholds.q80) }})</span>
          </div>
          <div class="legende-item">
            <div class="couleur-box" style="background: #4a8a4a"></div>
            <span>Moyen ({{ formatAmount(intensityThresholds.q40) }}-{{ formatAmount(intensityThresholds.q60) }})</span>
          </div>
          <div class="legende-item">
            <div class="couleur-box" style="background: #66aa66"></div>
            <span>Bas ({{ formatAmount(intensityThresholds.q20) }}-{{ formatAmount(intensityThresholds.q40) }})</span>
          </div>
          <div class="legende-item">
            <div class="couleur-box" style="background: #99cc99"></div>
            <span>Très bas (<{{ formatAmount(intensityThresholds.q20) }})</span>
          </div>
          <div class="legende-item">
            <div class="couleur-box" style="background: #f0f0f0"></div>
            <span>Aucun projet</span>
          </div>
        </div>
      </div>

      <!-- SVG de la carte avec vraies coordonnées GeoJSON -->
      <svg 
        ref="mapSvg"
        class="carte-svg" 
        :viewBox="`0 0 ${mapWidth} ${mapHeight}`"
        @mouseleave="clearTooltip"
      >
        <!-- COUCHE 1: Régions individuelles (fond avec contours pointillés) -->
        <g class="regions-layer">
          <g 
            v-for="region in regionsWithGeometry" 
            :key="region.name"
            class="region-group"
          >
            <path
              v-for="(pathData, index) in region.paths"
              :key="index"
              :d="pathData"
              :fill="getRegionColor(region.poleName)"
              fill-opacity="0.3"
              stroke="#e8e8e8"
              stroke-width="0.5"
              stroke-dasharray="1,4"
              class="region-path"
            />
            <!-- Arrière-plan pour le texte -->
            <text
              v-if="!shouldHideRegionLabel(region.name)"
              :x="lonToX(getAdjustedLabelPosition(region.name, region.center)[0])"
              :y="latToY(getAdjustedLabelPosition(region.name, region.center)[1])"
              class="region-label-bg"
              text-anchor="middle"
              dominant-baseline="middle"
            >
              {{ getRegionDisplayName(region.name) }}
            </text>
            <!-- Texte principal -->
            <text
              v-if="!shouldHideRegionLabel(region.name)"
              :x="lonToX(getAdjustedLabelPosition(region.name, region.center)[0])"
              :y="latToY(getAdjustedLabelPosition(region.name, region.center)[1])"
              class="region-label"
              text-anchor="middle"
              dominant-baseline="middle"
            >
              {{ getRegionDisplayName(region.name) }}
            </text>
          </g>
        </g>

        <!-- COUCHE 2: Pôles territoriaux (au-dessus avec contours gras) -->
        <g class="poles-layer">
          <g
            v-for="pole in polesWithGeometry"
            :key="pole.name"
            class="pole-group"
            @mouseenter="showTooltip($event, pole)"
            @mousemove="updateTooltip($event)"
            @mouseleave="clearTooltip"
            @click="selectPole(pole)"
          >
            <!-- Remplissage du pôle -->
            <path
              v-for="(pathData, index) in pole.paths"
              :key="'fill-' + index"
              :d="pathData"
              :fill="getPoleColor(pole)"
              fill-opacity="0.7"
              stroke="none"
              class="pole-fill"
            />

            <!-- Contour normal du pôle (toujours affiché, même si sélectionné) -->
            <path
              v-for="(pathData, index) in pole.paths"
              :key="'stroke-' + index"
              :d="pathData"
              fill="none"
              stroke="#2c3e50"
              stroke-width="3"
              stroke-linejoin="round"
              stroke-linecap="round"
              class="pole-stroke"
            />

            <!-- Label du pôle (seulement si plusieurs régions ou nom différent) -->
            <text
              v-if="shouldShowPoleLabel(pole)"
              :x="lonToX(getPoleAdjustedPosition(pole.name, pole.center)[0])"
              :y="latToY(getPoleAdjustedPosition(pole.name, pole.center)[1])"
              class="pole-label"
              text-anchor="middle"
              dominant-baseline="middle"
            >
              {{ pole.name }}
            </text>
          </g>
        </g>

        <!-- COUCHE 3: Contour orange du pôle sélectionné (toujours au-dessus) -->
        <g v-if="selectedPole" class="selected-pole-layer">
          <path
            v-for="(pathData, index) in getSelectedPolePaths()"
            :key="'selected-' + index"
            :d="pathData"
            fill="none"
            stroke="#ff6b35"
            stroke-width="5"
            stroke-linejoin="round"
            stroke-linecap="round"
            class="pole-selected-stroke"
          />
        </g>
      </svg>

      <!-- Tooltip -->
      <div 
        v-if="tooltip.visible" 
        class="tooltip"
        :style="{
          left: tooltip.x + 'px',
          top: tooltip.y + 'px'
        }"
      >
        <div class="tooltip-header">
          <strong>{{ tooltip.pole?.name }}</strong>
        </div>
        <div class="tooltip-content">
          <div><strong>Projets:</strong> {{ getPoleStats(tooltip.pole?.name)?.nombre_projets || 0 }}</div>
          <div><strong>Investissement:</strong> {{ formatAmount(getPoleStats(tooltip.pole?.name)?.cout_total || 0) }}</div>
          <div v-if="getPoleStats(tooltip.pole?.name)?.statuts" class="statuts-list">
            <strong>Statuts:</strong>
            <div v-for="(count, statut) in getPoleStats(tooltip.pole?.name)?.statuts" :key="statut" style="padding-left: 10px;">
              • {{ statut }}: {{ count }}
            </div>
          </div>
          <div v-if="tooltip.pole?.regions" class="regions-list">
            <small>Régions: {{ tooltip.pole.regions.join(', ') }}</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Panneau d'informations détaillées -->
    <div v-if="selectedPole" class="info-panel">
      <h4>{{ selectedPole }}</h4>
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-label">Total Projets</span>
          <span class="stat-value">{{ getPoleStats(selectedPole)?.nombre_projets || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Investissement Total</span>
          <span class="stat-value">{{ formatAmount(getPoleStats(selectedPole)?.cout_total || 0) }}</span>
        </div>
        <div v-if="getPoleStats(selectedPole)?.statuts" class="stat-item stat-item-full">
          <span class="stat-label">Statuts des Projets</span>
          <div class="statuts-details">
            <div v-for="(count, statut) in getPoleStats(selectedPole)?.statuts" :key="statut" class="statut-row">
              <span>{{ statut }}</span>
              <span class="stat-value">{{ count }}</span>
            </div>
          </div>
        </div>
        <div v-if="getPoleStats(selectedPole)?.projets?.length" class="stat-item stat-item-full projets-list-section">
          <span class="stat-label">Liste des Projets</span>
          <div class="projets-list">
            <div
              v-for="projet in getPoleStats(selectedPole)?.projets"
              :key="projet.id"
              class="projet-item"
              @click="goToProject(projet.id)"
            >
              <div class="projet-numero">{{ projet.numero_projet }}</div>
              <div class="projet-titre">{{ projet.titre }}</div>
              <div class="projet-meta-row">
                <span class="projet-cout">{{ formatAmount(projet.cout_estimatif || 0) }}</span>
                <span :class="['projet-statut', projet.statut]">{{ projet.statut }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as turf from '@turf/turf'

export default {
  name: 'CartePolesTerritoriaux',
  props: {
    statusFilter: {
      type: String,
      default: 'all', // 'all' ou 'approved'
      validator: (value) => ['all', 'approved'].includes(value)
    },
    title: {
      type: String,
      default: 'Répartition des Projets par Pôles Territoriaux'
    }
  },
  data() {
    return {
      mapWidth: 800,
      mapHeight: 600,
      selectedPole: null,
      polesData: null,
      statsParPole: {},
      tooltip: {
        visible: false,
        x: 0,
        y: 0,
        pole: null
      },
      intensityThresholds: {
        q20: 0,
        q40: 0,
        q60: 0,
        q80: 0
      }
    }
  },
  computed: {
    polesWithGeometry() {
      if (!this.polesData) return []

      return Object.entries(this.polesData.poles).map(([name, poleData]) => {
        // Générer les paths normaux (pour le remplissage)
        const paths = this.generateSVGPaths(poleData.geometry)

        // Calculer le contour externe fusionné pour le pôle
        let externalBoundaryPath = null
        try {
          console.log(`🔄 Fusion du pôle ${name}:`, {
            type: poleData.geometry.type,
            nbPolygons: poleData.geometry.coordinates?.length,
            regions: poleData.properties?.regions
          })

          // Fusionner toutes les géométries des régions du pôle
          const mergedGeometry = this.mergePolePaths(poleData.geometry)
          if (mergedGeometry) {
            console.log(`✅ Fusion réussie pour ${name}:`, mergedGeometry.type)
            externalBoundaryPath = this.generateSVGPaths(mergedGeometry)
          } else {
            console.warn(`⚠️ Pas de géométrie fusionnée pour ${name}, utilisation des paths normaux`)
            externalBoundaryPath = paths
          }
        } catch (error) {
          console.error(`❌ Erreur lors de la fusion du pôle ${name}:`, error)
          // Fallback sur les paths normaux
          externalBoundaryPath = paths
        }

        return {
          name,
          geometry: poleData.geometry,
          center: this.polesData.centers[name] || [0, 0],
          regions: poleData.properties?.regions || [],
          paths: paths,
          externalBoundaryPath: externalBoundaryPath
        }
      })
    },

    regionsWithGeometry() {
      if (!this.polesData?.regions) return []
      
      return Object.entries(this.polesData.regions).map(([name, regionData]) => {
        // Trouver à quel pôle appartient cette région
        const poleName = this.findPoleForRegion(name)
        
        // Utiliser les centres des régions individuelles
        const center = this.polesData.region_centers?.[name] || [0, 0]
        
        return {
          name,
          geometry: regionData.geometry,
          center: center,
          poleName,
          paths: this.generateSVGPaths(regionData.geometry),
          showLabel: true // Afficher tous les noms de régions
        }
      })
    },
    
    bounds() {
      return this.polesData?.bounds || {
        minLon: -17.53,
        maxLon: -11.34,
        minLat: 12.31,
        maxLat: 16.69
      }
    }
  },
  
  async mounted() {
    await this.loadGeojsonData()
    await this.loadStats()
  },
  
  methods: {
    async loadGeojsonData() {
      try {
        const response = await fetch('/poles_geojson.json')
        this.polesData = await response.json()
        console.log('✅ Données GeoJSON chargées:', this.polesData)
      } catch (error) {
        console.error('❌ Erreur chargement GeoJSON:', error)
        // Fallback avec les anciennes données si nécessaire
      }
    },
    
    async loadStats() {
      try {
        // Construire l'URL avec le filtre de statut si nécessaire
        let url = '/api/stats/poles'
        if (this.statusFilter === 'approved') {
          url += '?filter=approved'
        }

        console.log(`\n${'='.repeat(80)}`)
        console.log(`[CartePolesTerritoriaux] Chargement des stats`)
        console.log(`  - statusFilter prop: "${this.statusFilter}"`)
        console.log(`  - title prop: "${this.title}"`)
        console.log(`  - URL appelée: ${url}`)
        console.log('='.repeat(80))

        const response = await fetch(url)
        const newStats = await response.json()

        console.log(`[CartePolesTerritoriaux] Réponse reçue:`)
        console.log(`  - Nombre de pôles: ${Object.keys(newStats).length}`)
        const totalProjets = Object.values(newStats).reduce((sum, pole) => sum + pole.nombre_projets, 0)
        console.log(`  - Total projets: ${totalProjets}`)
        console.log(`  - Données:`, newStats)

        // Vérifier si les données ont changé
        const hasChanged = JSON.stringify(this.statsParPole) !== JSON.stringify(newStats)

        this.statsParPole = newStats
        this.calculateIntensityThresholds()

        if (hasChanged) {
          console.log('✅ Stats des pôles mises à jour:', this.statsParPole)
        }
      } catch (error) {
        console.error('❌ Erreur chargement stats:', error)
      }
    },
    
    calculateIntensityThresholds() {
      const amounts = Object.values(this.statsParPole)
        .map(stats => stats.cout_total)
        .filter(amount => amount > 0)
        .sort((a, b) => a - b)
      
      if (amounts.length > 0) {
        const n = amounts.length
        this.intensityThresholds = {
          q20: amounts[Math.floor(n * 0.2)],
          q40: amounts[Math.floor(n * 0.4)],
          q60: amounts[Math.floor(n * 0.6)],
          q80: amounts[Math.floor(n * 0.8)]
        }
      }
    },

    // Ajustements spécifiques pour certains labels
    getAdjustedLabelPosition(regionName, center) {
      const adjustments = {
        'FATICK': [-0.05, 0],  // Décaler Fatick vers la gauche
        'MATAM': [0, 0.02],    // Décaler Matam légèrement vers le bas
        'KAOLACK': [0.03, 0],  // Décaler Kaolack vers la droite pour éviter le chevauchement avec Fatick
      }
      
      const adjustment = adjustments[regionName] || [0, 0]
      return [
        center[0] + adjustment[0],
        center[1] + adjustment[1]
      ]
    },
    
    generateSVGPaths(geometry) {
      if (!geometry || !geometry.coordinates) return []
      
      const paths = []
      
      if (geometry.type === 'MultiPolygon') {
        for (const polygon of geometry.coordinates) {
          for (const ring of polygon) {
            paths.push(this.coordinatesToPath(ring))
          }
        }
      } else if (geometry.type === 'Polygon') {
        for (const ring of geometry.coordinates) {
          paths.push(this.coordinatesToPath(ring))
        }
      }
      
      return paths
    },
    
    coordinatesToPath(coordinates) {
      if (!coordinates || coordinates.length === 0) return ''
      
      let path = `M ${this.lonToX(coordinates[0][0])} ${this.latToY(coordinates[0][1])}`
      
      for (let i = 1; i < coordinates.length; i++) {
        const x = this.lonToX(coordinates[i][0])
        const y = this.latToY(coordinates[i][1])
        path += ` L ${x} ${y}`
      }
      
      path += ' Z'
      return path
    },
    
    lonToX(lon) {
      const { minLon, maxLon } = this.bounds
      return ((lon - minLon) / (maxLon - minLon)) * this.mapWidth
    },
    
    latToY(lat) {
      const { minLat, maxLat } = this.bounds
      return this.mapHeight - ((lat - minLat) / (maxLat - minLat)) * this.mapHeight
    },
    
    getPoleColor(pole) {
      const stats = this.getPoleStats(pole.name)
      if (!stats || stats.cout_total === 0) return '#f0f0f0'
      
      const amount = stats.cout_total
      const { q20, q40, q60, q80 } = this.intensityThresholds
      
      if (amount >= q80) return '#1a4d1a'      // Très élevé
      if (amount >= q60) return '#2d6b2d'      // Élevé
      if (amount >= q40) return '#4a8a4a'      // Moyen
      if (amount >= q20) return '#66aa66'      // Bas
      return '#99cc99'                         // Très bas
    },

    getRegionColor(poleName) {
      // Les régions utilisent la même couleur que leur pôle mais plus claire
      const stats = this.getPoleStats(poleName)
      if (!stats || stats.cout_total === 0) return '#f8f8f8'
      
      const amount = stats.cout_total
      const { q20, q40, q60, q80 } = this.intensityThresholds
      
      if (amount >= q80) return '#4d804d'      // Très élevé (plus clair)
      if (amount >= q60) return '#5a8a5a'      // Élevé (plus clair)
      if (amount >= q40) return '#739973'      // Moyen (plus clair)
      if (amount >= q20) return '#8cb38c'      // Bas (plus clair)
      return '#b3d9b3'                         // Très bas (plus clair)
    },

    findPoleForRegion(regionName) {
      // Chercher dans les données des pôles pour trouver à quel pôle appartient cette région
      if (!this.polesData?.regions_per_pole) return null
      
      for (const [poleName, regions] of Object.entries(this.polesData.regions_per_pole)) {
        if (regions.includes(regionName.toUpperCase())) {
          return poleName
        }
      }
      return null
    },


    
    getPoleStats(poleName) {
      return this.statsParPole[poleName] || { nombre_projets: 0, cout_total: 0, statuts: {}, projets: [] }
    },

    goToProject(projectId) {
      this.$router.push(`/project/${projectId}`)
    },
    
    showTooltip(event, pole) {
      this.tooltip = {
        visible: true,
        x: event.clientX + 10,
        y: event.clientY - 10,
        pole
      }
    },
    
    updateTooltip(event) {
      if (this.tooltip.visible) {
        this.tooltip.x = event.clientX + 10
        this.tooltip.y = event.clientY - 10
      }
    },
    
    clearTooltip() {
      this.tooltip.visible = false
    },
    
    selectPole(pole) {
      this.selectedPole = this.selectedPole === pole.name ? null : pole.name
    },

    getSelectedPolePaths() {
      if (!this.selectedPole) return []
      const pole = this.polesWithGeometry.find(p => p.name === this.selectedPole)
      return pole ? pole.externalBoundaryPath : []
    },

    /**
     * Fusionne toutes les géométries d'un pôle pour obtenir uniquement le contour externe
     * Utilise Turf.js pour faire l'union des polygones
     */
    mergePolePaths(geometry) {
      if (!geometry || !geometry.coordinates || geometry.coordinates.length === 0) {
        return null
      }

      try {
        // Si c'est un MultiPolygon
        if (geometry.type === 'MultiPolygon') {
          console.log(`  📐 MultiPolygon avec ${geometry.coordinates.length} polygones`)

          // Convertir chaque polygone en feature Turf
          const polygons = geometry.coordinates.map((coords, idx) => {
            console.log(`    - Polygone ${idx}: ${coords.length} rings, premier ring a ${coords[0].length} points`)
            return turf.polygon(coords)
          })

          if (polygons.length === 0) return null
          if (polygons.length === 1) {
            console.log('  ℹ️ Un seul polygone, pas de fusion nécessaire')
            return polygons[0].geometry
          }

          // Fusionner tous les polygones en utilisant turf.union avec featureCollection
          // Note: Turf v7+ utilise turf.union(featureCollection) au lieu de turf.union(poly1, poly2)
          console.log(`  🔗 Fusion de ${polygons.length} polygones avec FeatureCollection...`)

          try {
            const featureCollection = turf.featureCollection(polygons)
            const merged = turf.union(featureCollection)

            if (merged) {
              console.log(`  ✅ Fusion réussie, type final: ${merged.geometry.type}`)
              return merged.geometry
            } else {
              console.warn(`  ⚠️ Fusion retourne null`)
              return null
            }
          } catch (err) {
            console.error(`  ❌ Erreur lors de la fusion:`, err.message)
            return null
          }
        }
        // Si c'est un Polygon simple
        else if (geometry.type === 'Polygon') {
          console.log('  ℹ️ Polygon simple, pas de fusion nécessaire')
          return geometry
        }

        return null
      } catch (error) {
        console.error('❌ Erreur dans mergePolePaths:', error)
        return null
      }
    },

    formatAmount(amount) {
      if (!amount || amount === 0) return '0 FCFA'
      if (amount >= 1000000000) {
        return `${(amount / 1000000000).toFixed(1)} Md FCFA`
      } else if (amount >= 1000000) {
        return `${(amount / 1000000).toFixed(0)} M FCFA`
      }
      return `${amount.toLocaleString()} FCFA`
    },

    shouldShowPoleLabel(pole) {
      // Afficher les étiquettes des pôles pour :
      // - Les pôles multi-régions (comme avant)
      // - Saint-Louis (Nord) et Matam (Nord-Est) car leurs noms diffèrent des régions
      const specialPoles = ['Nord', 'Nord-Est']
      return (pole.regions && pole.regions.length > 1) || specialPoles.includes(pole.name)
    },

    shouldHideRegionLabel(regionName) {
      // Masquer les étiquettes des régions pour certaines régions 
      // où on préfère afficher l'étiquette du pôle
      const regionsToHide = ['Saint-Louis', 'Matam', 'Dakar', 'Thiès']
      return regionsToHide.includes(regionName)
    },

    getRegionDisplayName(regionName) {
      // Remplacer certains noms de région par leurs noms de pôle
      const regionToPoleMapping = {
        'Dakar': 'Dakar',
        'Thiès': 'Thiès'
      }
      return regionToPoleMapping[regionName] || regionName
    },

    getAdjustedLabelPosition(regionName, originalCenter) {
      // Ajustements spécifiques pour certaines régions
      const adjustments = {
        'FATICK': [-0.05, 0], // Décaler légèrement vers la gauche
        // Ajouter d'autres ajustements si nécessaire
      }

      const adjustment = adjustments[regionName] || [0, 0]
      return [
        originalCenter[0] + adjustment[0],
        originalCenter[1] + adjustment[1]
      ]
    },

    getPoleAdjustedPosition(poleName, originalCenter) {
      // Ajustements spécifiques pour les étiquettes des pôles afin d'éviter les superpositions
      const poleAdjustments = {
        'Nord': [0.08, 0.03], // Décaler Nord (Saint-Louis) légèrement vers la droite et le bas
        'Nord-Est': [-0.06, 0.04] // Décaler Nord-Est (Matam) légèrement vers la gauche et le bas
      }

      const adjustment = poleAdjustments[poleName] || [0, 0]
      return [
        originalCenter[0] + adjustment[0],
        originalCenter[1] + adjustment[1]
      ]
    }
  }
}
</script>

<style scoped>
.carte-poles-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.titre-carte {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.5em;
  font-weight: 600;
}

.carte-wrapper {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.legende-investissement {
  flex: 0 0 250px;
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.legende-investissement h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 1.1em;
}

.legende-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legende-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9em;
}

.couleur-box {
  width: 20px;
  height: 15px;
  border-radius: 3px;
  border: 1px solid #ccc;
}

.carte-svg {
  flex: 1;
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
}

/* Couche des régions (fond) */
.regions-layer {
  opacity: 1;
}

.region-group {
  pointer-events: none; /* Désactiver les interactions sur les régions */
}

.region-path {
  transition: none; /* Pas de transition pour les régions */
  pointer-events: none;
}

.region-label-bg {
  font-size: 12px;
  font-weight: 600;
  fill: white;
  stroke: white;
  stroke-width: 3;
  pointer-events: none;
  opacity: 0.9;
}

.region-label {
  font-size: 12px;
  font-weight: 600;
  fill: #2c3e50;
  pointer-events: none;
  opacity: 1;
}

/* Couche des pôles (au-dessus) */
.poles-layer {
  opacity: 1;
}

.pole-group {
  transition: all 0.3s ease;
  cursor: pointer;
}

.pole-group:hover .pole-fill {
  fill-opacity: 0.8;
  filter: brightness(1.1);
}

.pole-group:hover .pole-stroke {
  stroke-width: 4;
}

.pole-fill {
  transition: all 0.2s ease;
  cursor: pointer;
}

.pole-stroke {
  transition: all 0.2s ease;
  cursor: pointer;
  filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.2));
}

.pole-label {
  font-size: 13px;
  font-weight: 700;
  fill: #1a1a1a;
  pointer-events: none;
  text-shadow: 2px 2px 4px rgba(255,255,255,0.9), 
               -1px -1px 2px rgba(255,255,255,0.9);
}

.tooltip {
  position: fixed;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 10px;
  border-radius: 6px;
  font-size: 12px;
  z-index: 1000;
  max-width: 200px;
  pointer-events: none;
}

.tooltip-header {
  margin-bottom: 5px;
  font-size: 13px;
}

.tooltip-content div {
  margin: 2px 0;
}

.regions-list {
  margin-top: 5px;
  padding-top: 5px;
  border-top: 1px solid rgba(255,255,255,0.3);
}

.info-panel {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.info-panel h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 1.2em;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.stat-label {
  font-size: 0.9em;
  color: #6c757d;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 1.2em;
  font-weight: 600;
  color: #2c3e50;
}

.stat-item-full {
  grid-column: 1 / -1;
}

.statuts-details {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.statut-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #4a8a4a;
}

.statuts-list {
  margin-top: 5px;
}

/* Liste des projets */
.projets-list-section {
  margin-top: 10px;
}

.projets-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.projet-item {
  padding: 10px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #0ea5e9;
  cursor: pointer;
  transition: all 0.2s ease;
}

.projet-item:hover {
  background: #e2e8f0;
  transform: translateX(3px);
}

.projet-numero {
  font-size: 0.75rem;
  color: #64748b;
  font-family: monospace;
}

.projet-titre {
  font-weight: 600;
  font-size: 0.85rem;
  color: #1e293b;
  margin: 4px 0;
  line-height: 1.3;
}

.projet-meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
}

.projet-cout {
  font-size: 0.75rem;
  color: #059669;
  font-weight: 600;
}

.projet-statut {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 500;
  text-transform: capitalize;
}

.projet-statut.soumis {
  background: #dbeafe;
  color: #1e40af;
}

.projet-statut.assigné,
.projet-statut.en_evaluation {
  background: #fef3c7;
  color: #92400e;
}

.projet-statut.évalué,
.projet-statut.approuvé {
  background: #d1fae5;
  color: #065f46;
}

@media (max-width: 768px) {
  .carte-wrapper {
    flex-direction: column;
  }

  .legende-investissement {
    flex: none;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>