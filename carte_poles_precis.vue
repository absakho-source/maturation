<template>
  <div class="carte-poles-container">
    <h3>Répartition des projets par pôles territoriaux</h3>
    
    <!-- Légende dynamique -->
    <div class="legende">
      <h4>Montants des projets par pôle territorial</h4>
      <div class="legende-items">
        <div class="legende-item">
          <div class="color-box intensity-none"></div>
          <span>Aucun projet</span>
        </div>
        <div class="legende-item">
          <div class="color-box intensity-low"></div>
          <span>Faible</span>
        </div>
        <div class="legende-item">
          <div class="color-box intensity-medium"></div>
          <span>Moyen</span>
        </div>
        <div class="legende-item">
          <div class="color-box intensity-high"></div>
          <span>Élevé</span>
        </div>
        <div class="legende-item">
          <div class="color-box intensity-very-high"></div>
          <span>Très élevé</span>
        </div>
      </div>
      <div class="legende-details" v-if="Object.keys(statsParPole).length > 0">
        <small v-html="getLegendDetails()"></small>
      </div>
    </div>

    <!-- Carte interactive -->
    <div class="carte-senegal">
      <svg viewBox="0 0 800 600" class="senegal-map" v-if="!useShapefileData">
        <!-- Carte simplifiée (fallback) -->
        <g v-for="pole in polesGeometry" :key="pole.name">
          <polygon 
            :points="pole.points"
            :class="getPoleClass(pole.name)"
            @click="selectPole(pole.name)"
            @mouseover="showTooltip($event, pole.name)"
            @mouseleave="hideTooltip"
          />
          <text :x="pole.labelX" :y="pole.labelY" class="pole-label">{{ pole.displayName }}</text>
        </g>
        
        <!-- Frontières du Sénégal -->
        <path d="M 120,490 L 150,540 L 220,570 L 300,580 L 380,590 L 450,570 L 480,520 L 550,550 L 620,560 L 680,530 L 700,480 L 680,420 L 620,370 L 580,240 L 550,200 L 480,180 L 380,200 L 350,160 L 280,140 L 180,150 L 170,180 L 200,220 L 180,360 L 170,390 L 150,450 L 120,490 Z" 
              fill="none" 
              stroke="#2c3e50" 
              stroke-width="3" 
              class="country-border"/>
      </svg>
      
      <!-- Carte précise basée sur les shapefiles -->
      <svg viewBox="0 0 800 600" class="senegal-map" v-else>
        <g v-for="(shapeData, poleName) in shapefileGeometry" :key="poleName">
          <path 
            :d="shapeData.path"
            :class="getPoleClass(poleName)"
            @click="selectPole(poleName)"
            @mouseover="showTooltip($event, poleName)"
            @mouseleave="hideTooltip"
          />
          <text :x="shapeData.labelX" :y="shapeData.labelY" class="pole-label">
            {{ getDisplayName(poleName) }}
          </text>
        </g>
      </svg>
    </div>

    <!-- Tooltip -->
    <div v-if="tooltip.visible" class="tooltip" :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
      <h4>{{ tooltip.pole }}</h4>
      <div class="tooltip-stats">
        <div><strong>{{ formatAmount(getStatsPole(tooltip.pole).cout_total || 0) }}</strong></div>
        <div>{{ getStatsPole(tooltip.pole).total }} projet(s)</div>
        <div>Soumis: {{ getStatsPole(tooltip.pole).soumis }}</div>
        <div>En évaluation: {{ getStatsPole(tooltip.pole).evaluation }}</div>
        <div>Avis favorables: {{ getStatsPole(tooltip.pole).favorables }}</div>
        <div>Validés: {{ getStatsPole(tooltip.pole).valides }}</div>
      </div>
    </div>

    <!-- Détails du pôle sélectionné -->
    <div v-if="poleSelectionne" class="pole-details">
      <h4>{{ poleSelectionne }}</h4>
      
      <!-- Montant total en vedette -->
      <div class="montant-total">
        <div class="montant-value">{{ formatAmount(getStatsPole(poleSelectionne).cout_total || 0) }}</div>
        <div class="montant-label">Coût total des projets</div>
      </div>
      
      <div class="stats-grid">
        <div class="stat-card soumis">
          <div class="stat-number">{{ getStatsPole(poleSelectionne).soumis }}</div>
          <div class="stat-label">Projets soumis</div>
        </div>
        <div class="stat-card evaluation">
          <div class="stat-number">{{ getStatsPole(poleSelectionne).evaluation }}</div>
          <div class="stat-label">En évaluation</div>
        </div>
        <div class="stat-card favorables">
          <div class="stat-number">{{ getStatsPole(poleSelectionne).favorables }}</div>
          <div class="stat-label">Avis favorables</div>
        </div>
        <div class="stat-card valides">
          <div class="stat-number">{{ getStatsPole(poleSelectionne).valides }}</div>
          <div class="stat-label">Validés</div>
        </div>
      </div>
      
      <!-- Liste des projets pour ce pôle -->
      <div v-if="getProjetsPole(poleSelectionne).length > 0" class="projets-liste">
        <h5>Projets dans ce pôle:</h5>
        <div v-for="projet in getProjetsPole(poleSelectionne)" :key="projet.id" class="projet-item">
          <span class="projet-numero">{{ projet.numero_projet || 'N/A' }}</span>
          <span class="projet-titre">{{ projet.titre }}</span>
          <span :class="'projet-statut ' + getStatusClass(projet.statut)">{{ projet.statut }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CartePolesTerritoriaux',
  data() {
    return {
      projets: [],
      statsParPole: {},
      poleSelectionne: null,
      useShapefileData: false,
      shapefileGeometry: {},
      tooltip: {
        visible: false,
        x: 0,
        y: 0,
        pole: ''
      },
      poles: [
        "Dakar",
        "Thiès", 
        "Centre",
        "Diourbel-Louga",
        "Sud",
        "Sud-Est",
        "Nord",
        "Nord-Est"
      ],
      // Géométrie simplifiée de fallback
      polesGeometry: [
        {
          name: "Dakar",
          displayName: "Dakar",
          points: "200,320 250,300 280,310 290,340 270,370 240,380 210,360 195,340",
          labelX: 245,
          labelY: 340
        },
        {
          name: "Thiès",
          displayName: "Thiès",
          points: "180,360 240,380 280,370 310,390 295,420 250,430 200,420 170,390",
          labelX: 245,
          labelY: 405
        },
        {
          name: "Centre",
          displayName: "Centre",
          points: "280,310 350,300 420,320 450,360 430,420 380,450 320,440 290,390 280,350",
          labelX: 370,
          labelY: 375
        },
        {
          name: "Diourbel-Louga",
          displayName: "Diourbel-Louga",
          points: "250,250 350,230 420,250 440,290 420,320 350,300 280,280 250,270",
          labelX: 345,
          labelY: 275
        },
        {
          name: "Nord",
          displayName: "Nord",
          points: "180,150 280,140 350,160 380,200 360,240 320,260 250,250 200,220 170,180",
          labelX: 275,
          labelY: 200
        },
        {
          name: "Nord-Est",
          displayName: "Nord-Est",
          points: "380,200 480,180 550,200 580,240 570,290 530,320 460,330 420,290 380,250",
          labelX: 480,
          labelY: 255
        },
        {
          name: "Sud-Est",
          displayName: "Sud-Est",
          points: "450,360 550,340 620,370 680,420 700,480 680,530 620,560 550,550 480,520 430,470 430,420",
          labelX: 565,
          labelY: 455
        },
        {
          name: "Sud",
          displayName: "Sud",
          points: "150,450 250,430 320,440 380,450 430,470 480,520 450,570 380,590 300,580 220,570 150,540 120,490",
          labelX: 300,
          labelY: 520
        }
      ]
    }
  },
  async mounted() {
    await this.loadShapefileData()
    await this.loadStats()
  },
  methods: {
    async loadShapefileData() {
      try {
        // Tenter de charger les données SVG précises des shapefiles
        const response = await fetch('/src/assets/poles_svg_data.json')
        if (response.ok) {
          const data = await response.json()
          this.shapefileGeometry = data
          this.useShapefileData = true
          console.log('✅ Données géographiques précises chargées depuis les shapefiles')
          
          // Calculer les positions des labels pour les données shapefile
          this.calculateShapefileLabels()
        } else {
          console.log('ℹ️ Données shapefile non disponibles, utilisation de la géométrie simplifiée')
        }
      } catch (error) {
        console.log('ℹ️ Données shapefile non disponibles, utilisation de la géométrie simplifiée')
      }
    },
    
    calculateShapefileLabels() {
      // Calculer le centre approximatif pour chaque forme SVG
      for (const [poleName, shapeData] of Object.entries(this.shapefileGeometry)) {
        if (shapeData.points) {
          const points = shapeData.points.split(' ')
          let sumX = 0, sumY = 0, count = 0
          
          points.forEach(point => {
            const [x, y] = point.split(',').map(Number)
            if (!isNaN(x) && !isNaN(y)) {
              sumX += x
              sumY += y
              count++
            }
          })
          
          if (count > 0) {
            shapeData.labelX = sumX / count
            shapeData.labelY = sumY / count
          }
        }
      }
    },
    
    async loadStats() {
      try {
        // Essayer d'abord l'API spécialisée pour les pôles
        const statsResponse = await fetch('/api/stats/poles')
        if (statsResponse.ok) {
          this.statsParPole = await statsResponse.json()
          console.log('📊 Stats par pôle chargées:', this.statsParPole)
          return
        }
      } catch (error) {
        console.log('API stats/poles non disponible, fallback vers projects')
      }
      
      // Fallback: charger tous les projets et calculer les stats
      try {
        const response = await fetch('/api/projects?role=admin&username=admin')
        if (response.ok) {
          this.projets = await response.json()
          this.calculateStatsFromProjects()
        }
      } catch (error) {
        console.error('Erreur lors du chargement des projets:', error)
      }
    },
    
    calculateStatsFromProjects() {
      this.statsParPole = {}
      
      this.poles.forEach(pole => {
        const projets = this.getProjetsPole(pole)
        this.statsParPole[pole] = {
          total: projets.length,
          soumis: projets.filter(p => p.statut === 'soumis').length,
          evaluation: projets.filter(p => ['assigné', 'en instruction', 'évalué', 'compléments demandés', 'compléments fournis'].includes(p.statut)).length,
          favorables: projets.filter(p => p.avis && ['favorable', 'favorable sous conditions'].includes(p.avis) && (!p.decision_finale || p.decision_finale === 'en_attente')).length,
          valides: projets.filter(p => p.decision_finale && ['confirme', 'approuvé'].includes(p.decision_finale)).length,
          cout_total: projets.reduce((sum, p) => sum + (p.cout_estimatif || 0), 0),
          projets: projets
        }
      })
    },
    
    selectPole(pole) {
      this.poleSelectionne = this.poleSelectionne === pole ? null : pole
    },
    
    showTooltip(event, pole) {
      this.tooltip = {
        visible: true,
        x: event.clientX + 10,
        y: event.clientY - 50,
        pole: pole
      }
    },
    
    hideTooltip() {
      this.tooltip.visible = false
    },
    
    getDisplayName(poleName) {
      // Mapper les noms des shapefiles vers des noms d'affichage plus courts
      const nameMapping = {
        'Centre (Kaolack, Fatick, Kaffrine)': 'Centre',
        'Sud (Ziguinchor, Sédhiou, Kolda)': 'Sud',
        'Sud-Est (Tambacounda, Kédougou)': 'Sud-Est',
        'Nord (Saint-Louis)': 'Nord',
        'Nord-Est (Matam)': 'Nord-Est'
      }
      return nameMapping[poleName] || poleName
    },
    
    getProjetsPole(pole) {
      if (this.statsParPole[pole] && this.statsParPole[pole].projets) {
        return this.statsParPole[pole].projets
      }
      return this.projets.filter(p => p.poles === pole)
    },
    
    getStatsPole(pole) {
      if (this.statsParPole[pole]) {
        return this.statsParPole[pole]
      }
      
      // Fallback calculation si les stats ne sont pas encore chargées
      const projets = this.projets.filter(p => p.poles === pole)
      return {
        total: projets.length,
        soumis: projets.filter(p => p.statut === 'soumis').length,
        evaluation: projets.filter(p => ['assigné', 'en instruction', 'évalué', 'compléments demandés', 'compléments fournis'].includes(p.statut)).length,
        favorables: projets.filter(p => p.avis && ['favorable', 'favorable sous conditions'].includes(p.avis) && (!p.decision_finale || p.decision_finale === 'en_attente')).length,
        valides: projets.filter(p => p.decision_finale && ['confirme', 'approuvé'].includes(p.decision_finale)).length,
        cout_total: projets.reduce((sum, p) => sum + (p.cout_estimatif || 0), 0)
      }
    },
    
    getPoleClass(pole) {
      const stats = this.getStatsPole(pole)
      const intensity = this.calculateIntensity(stats.cout_total || 0)
      
      return `pole-region intensity-${intensity} ${this.poleSelectionne === pole ? 'selected' : ''}`
    },
    
    calculateIntensity(amount) {
      if (amount === 0) return 'none'
      
      // Récupérer tous les montants non-nuls pour calculer les quartiles
      const allAmounts = Object.values(this.statsParPole)
        .map(stats => stats.cout_total || 0)
        .filter(amount => amount > 0)
        .sort((a, b) => a - b)
      
      if (allAmounts.length === 0) return 'none'
      if (allAmounts.length === 1) return 'medium'
      
      // Calculer des quartiles pour 4 intervalles
      const q25Index = Math.floor(allAmounts.length * 0.25)
      const q50Index = Math.floor(allAmounts.length * 0.5)
      const q75Index = Math.floor(allAmounts.length * 0.75)
      
      const q25 = allAmounts[q25Index]
      const q50 = allAmounts[q50Index]
      const q75 = allAmounts[q75Index]
      
      // Classification basée sur les quartiles
      if (amount >= q75) return 'very-high'
      else if (amount >= q50) return 'high'
      else if (amount >= q25) return 'medium'
      else return 'low'
    },
    
    getLegendDetails() {
      // Récupérer tous les montants non-nuls pour calculer les seuils
      const allAmounts = Object.values(this.statsParPole)
        .map(stats => stats.cout_total || 0)
        .filter(amount => amount > 0)
        .sort((a, b) => a - b)
      
      if (allAmounts.length === 0) return 'Aucune donnée financière disponible'
      if (allAmounts.length === 1) return `Un seul pôle actif avec ${this.formatAmount(allAmounts[0])}`
      
      const q25Index = Math.floor(allAmounts.length * 0.25)
      const q50Index = Math.floor(allAmounts.length * 0.5)
      const q75Index = Math.floor(allAmounts.length * 0.75)
      
      const q25 = allAmounts[q25Index]
      const q50 = allAmounts[q50Index]
      const q75 = allAmounts[q75Index]
      
      return `&lt;${this.formatAmount(q25)} • ${this.formatAmount(q25)}-${this.formatAmount(q50)} • ${this.formatAmount(q50)}-${this.formatAmount(q75)} • &gt;${this.formatAmount(q75)}`
    },
    
    formatAmount(amount) {
      if (amount >= 1000000000) {
        return `${(amount / 1000000000).toFixed(1)}Md FCFA`
      } else if (amount >= 1000000) {
        return `${(amount / 1000000).toFixed(1)}M FCFA`
      } else if (amount >= 1000) {
        return `${(amount / 1000).toFixed(1)}K FCFA`
      } else {
        return `${amount} FCFA`
      }
    },
    
    getStatusClass(statut) {
      const classes = {
        'soumis': 'status-soumis',
        'assigné': 'status-evaluation',
        'en instruction': 'status-evaluation',
        'évalué': 'status-evaluation',
        'compléments demandés': 'status-evaluation',
        'compléments fournis': 'status-evaluation',
        'approuvé': 'status-favorables',
        'validé par presidencesct': 'status-favorables',
        'rejeté': 'status-rejete'
      }
      return classes[statut] || 'status-default'
    }
  }
}
</script>

<style scoped>
.carte-poles-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin: 20px 0;
}

.carte-poles-container h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  text-align: center;
}

/* Légende */
.legende {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.legende h4 {
  color: #2c3e50;
  margin: 0 0 15px 0;
  text-align: center;
  font-size: 16px;
}

.legende-items {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.legende-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.color-box {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  border: 1px solid #ddd;
}

/* Couleurs vertes pour l'intensité */
.intensity-none { background: #f8f9fa; }
.intensity-low { background: #d4edda; }
.intensity-medium { background: #a3cfbb; }
.intensity-high { background: #6c9a7f; }
.intensity-very-high { background: #28a745; }

.legende-details {
  margin-top: 10px;
  text-align: center;
  color: #7f8c8d;
  font-style: italic;
}

/* Carte SVG */
.carte-senegal {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  position: relative;
}

.senegal-map {
  width: 100%;
  height: auto;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
}

/* Régions/Pôles */
.pole-region {
  stroke: #34495e;
  stroke-width: 2;
  cursor: pointer;
  transition: all 0.3s ease;
  fill: #ecf0f1;
}

.pole-region.intensity-none {
  fill: #f8f9fa;
}

.pole-region.intensity-low {
  fill: #d4edda;
}

.pole-region.intensity-medium {
  fill: #a3cfbb;
}

.pole-region.intensity-high {
  fill: #6c9a7f;
}

.pole-region.intensity-very-high {
  fill: #28a745;
}

.pole-region:hover {
  stroke: #e74c3c;
  stroke-width: 3;
  filter: brightness(1.1);
  transform: scale(1.01);
  transform-origin: center;
}

.pole-region.selected {
  stroke: #1e8449;
  stroke-width: 3;
  filter: brightness(1.2);
}

.pole-label {
  font-size: 12px;
  font-weight: bold;
  fill: #2c3e50;
  text-anchor: middle;
  pointer-events: none;
  text-shadow: 1px 1px 1px rgba(255,255,255,0.8);
}

.country-border {
  filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3));
}

/* Tooltip */
.tooltip {
  position: fixed;
  background: rgba(0,0,0,0.9);
  color: white;
  padding: 10px;
  border-radius: 6px;
  font-size: 12px;
  z-index: 1000;
  pointer-events: none;
  box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

.tooltip h4 {
  margin: 0 0 8px 0;
  color: #3498db;
}

.tooltip-stats div {
  margin: 2px 0;
}

/* Détails du pôle */
.pole-details {
  margin-top: 30px;
  border-top: 2px solid #e9ecef;
  padding-top: 20px;
}

.pole-details h4 {
  color: #2c3e50;
  margin-bottom: 15px;
  text-align: center;
}

/* Montant total en vedette */
.montant-total {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.montant-value {
  font-size: 2.2em;
  font-weight: bold;
  margin-bottom: 5px;
}

.montant-label {
  font-size: 0.9em;
  opacity: 0.9;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  border-left: 4px solid;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.stat-card.soumis { border-left-color: #3498db; }
.stat-card.evaluation { border-left-color: #f39c12; }
.stat-card.favorables { border-left-color: #27ae60; }
.stat-card.valides { border-left-color: #8e44ad; }

.stat-number {
  font-size: 2em;
  font-weight: bold;
  color: #2c3e50;
}

.stat-label {
  color: #7f8c8d;
  font-size: 0.9em;
  margin-top: 5px;
}

/* Liste des projets */
.projets-liste {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
}

.projets-liste h5 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.projet-item {
  display: grid;
  grid-template-columns: 120px 1fr 120px;
  gap: 10px;
  padding: 8px;
  border-bottom: 1px solid #e9ecef;
  align-items: center;
}

.projet-item:last-child {
  border-bottom: none;
}

.projet-numero {
  font-weight: bold;
  color: #34495e;
  font-size: 0.9em;
}

.projet-titre {
  color: #2c3e50;
}

.projet-statut {
  font-size: 0.8em;
  padding: 4px 8px;
  border-radius: 4px;
  text-align: center;
  font-weight: bold;
}

.status-soumis { background: #3498db; color: white; }
.status-evaluation { background: #f39c12; color: white; }
.status-favorables { background: #27ae60; color: white; }
.status-rejete { background: #e74c3c; color: white; }
.status-default { background: #95a5a6; color: white; }

/* Responsive */
@media (max-width: 768px) {
  .legende-items {
    gap: 10px;
  }
  
  .legende-item {
    font-size: 12px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  
  .projet-item {
    grid-template-columns: 1fr;
    gap: 5px;
    text-align: center;
  }
  
  .pole-label {
    font-size: 10px;
  }
}

@media (max-width: 480px) {
  .carte-poles-container {
    padding: 15px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .legende-items {
    flex-direction: column;
    align-items: center;
  }
}
</style>