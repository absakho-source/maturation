<template>
  <PageWrapper>
    <div class="projets-tutelle-page">
      <div class="header-section">
        <div class="header-with-back">
          <button @click="retourDashboard" class="btn-retour">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Retour au tableau de bord
          </button>
          <div class="header-content">
            <h1>Projets sous ma tutelle</h1>
            <p class="subtitle">{{ organisme }}</p>
          </div>
        </div>
      </div>

      <!-- Statistiques -->
      <div class="stats-section">
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">Total projets</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📝</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.soumis }}</div>
            <div class="stat-label">Soumis</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⏳</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.en_evaluation }}</div>
            <div class="stat-label">En évaluation</div>
          </div>
        </div>
        <div class="stat-card favorable">
          <div class="stat-icon">✅</div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.favorables }}</div>
            <div class="stat-label">Favorables</div>
          </div>
        </div>
      </div>

      <!-- Filtres -->
      <div class="filters-section">
        <div class="filter-group">
          <label>Filtrer par statut :</label>
          <select v-model="filtreStatut">
            <option value="">Tous</option>
            <option value="soumis">Soumis</option>
            <option value="assigné">Assigné</option>
            <option value="en_evaluation">En évaluation</option>
            <option value="évalué">Évalué</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Rechercher :</label>
          <input
            v-model="rechercheTexte"
            type="text"
            placeholder="Titre, structure..."
          />
        </div>
      </div>

      <!-- Liste des projets -->
      <div class="projets-container">
        <div v-if="loading" class="loading">Chargement des projets...</div>
        <div v-else-if="error" class="error-message">{{ error }}</div>
        <div v-else-if="projetsFiltres.length === 0" class="no-data">
          Aucun projet trouvé sous votre tutelle
        </div>

        <div v-else class="projets-grid">
          <div v-for="projet in projetsFiltres" :key="projet.id" class="projet-card">
            <div class="projet-header">
              <span class="projet-numero">{{ projet.numero_projet }}</span>
              <span :class="['badge-statut', projet.statut]">{{ formatStatut(projet.statut) }}</span>
            </div>
            <h3 class="projet-titre">{{ projet.titre }}</h3>
            <div class="projet-meta">
              <div class="meta-item">
                <span class="meta-label">Structure :</span>
                <span class="meta-value">{{ projet.structure_soumissionnaire || 'N/A' }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">Auteur :</span>
                <span class="meta-value">{{ projet.auteur_nom }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">Date :</span>
                <span class="meta-value">{{ formatDate(projet.date_soumission) }}</span>
              </div>
              <div v-if="projet.cout_estimatif" class="meta-item">
                <span class="meta-label">Coût :</span>
                <span class="meta-value">{{ formatMontant(projet.cout_estimatif) }}</span>
              </div>
              <div v-if="projet.avis" class="meta-item">
                <span class="meta-label">Avis :</span>
                <span :class="['avis-badge', projet.avis]">{{ projet.avis }}</span>
              </div>
            </div>
            <div class="projet-actions">
              <button @click="voirProjet(projet.id)" class="btn-voir">
                Voir détails
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </PageWrapper>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import PageWrapper from '../components/PageWrapper.vue'

const router = useRouter()

// État
const projets = ref([])
const stats = ref({
  total: 0,
  soumis: 0,
  en_evaluation: 0,
  evalues: 0,
  favorables: 0,
  defavorables: 0
})
const organisme = ref('')
const loading = ref(false)
const error = ref('')
const filtreStatut = ref('')
const rechercheTexte = ref('')

// Récupérer l'utilisateur connecté
const userStr = localStorage.getItem('user')
const user = userStr ? JSON.parse(userStr) : null

// Projets filtrés
const projetsFiltres = computed(() => {
  let result = projets.value

  if (filtreStatut.value) {
    result = result.filter(p => p.statut === filtreStatut.value)
  }

  if (rechercheTexte.value) {
    const search = rechercheTexte.value.toLowerCase()
    result = result.filter(p =>
      p.titre?.toLowerCase().includes(search) ||
      p.structure_soumissionnaire?.toLowerCase().includes(search) ||
      p.auteur_nom?.toLowerCase().includes(search) ||
      p.numero_projet?.toLowerCase().includes(search)
    )
  }

  return result
})

onMounted(async () => {
  if (!user?.is_point_focal) {
    error.value = 'Vous n\'êtes pas un point focal'
    return
  }
  await chargerProjets()
  await chargerStats()
})

async function chargerProjets() {
  loading.value = true
  error.value = ''

  try {
    const response = await axios.get('/api/point-focal/projets', {
      params: { username: user.username }
    })
    projets.value = response.data.projets
    organisme.value = response.data.organisme
  } catch (err) {
    console.error('Erreur chargement projets:', err)
    error.value = err.response?.data?.error || 'Erreur lors du chargement des projets'
  } finally {
    loading.value = false
  }
}

async function chargerStats() {
  try {
    const response = await axios.get('/api/point-focal/stats', {
      params: { username: user.username }
    })
    stats.value = response.data
  } catch (err) {
    console.error('Erreur chargement stats:', err)
  }
}

function voirProjet(projetId) {
  router.push(`/projets/${projetId}`)
}

function retourDashboard() {
  router.push('/soumissionnaire')
}

function formatStatut(statut) {
  const labels = {
    soumis: 'Soumis',
    assigné: 'Assigné',
    en_evaluation: 'En évaluation',
    évalué: 'Évalué',
    validé: 'Validé',
    rejeté: 'Rejeté',
    compléments_requis: 'Compléments requis'
  }
  return labels[statut] || statut
}

function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

function formatMontant(montant) {
  if (!montant) return 'N/A'
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'XOF',
    maximumFractionDigits: 0
  }).format(montant)
}
</script>

<style scoped>
.projets-tutelle-page {
  padding: 1.5rem;
}

.header-section {
  margin-bottom: 1.5rem;
}

.header-with-back {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn-retour {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: var(--dgppe-primary);
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0.5rem;
  transition: color 0.2s;
}

.btn-retour:hover {
  color: var(--dgppe-primary-light);
}

.header-content h1 {
  margin: 0;
  font-size: 1.5rem;
  color: #1a202c;
}

.subtitle {
  margin: 0.5rem 0 0 0;
  color: #4a5568;
  font-size: 0.9rem;
}

/* Stats */
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-card.favorable {
  background: #f0fff4;
  border: 1px solid #9ae6b4;
}

.stat-icon {
  font-size: 1.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a202c;
}

.stat-label {
  font-size: 0.8rem;
  color: #718096;
}

/* Filtres */
.filters-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #4a5568;
}

.filter-group select,
.filter-group input {
  padding: 0.5rem;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  min-width: 150px;
}

/* Projets */
.projets-container {
  min-height: 300px;
}

.loading,
.error-message,
.no-data {
  text-align: center;
  padding: 2rem;
  color: #718096;
}

.error-message {
  color: #e53e3e;
}

.projets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1rem;
}

.projet-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.projet-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.projet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.projet-numero {
  font-size: 0.8rem;
  color: #718096;
  font-family: monospace;
}

.badge-statut {
  font-size: 0.7rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
}

.badge-statut.soumis {
  background: #bee3f8;
  color: #2c5282;
}

.badge-statut.assigné,
.badge-statut.en_evaluation {
  background: #feebc8;
  color: #c05621;
}

.badge-statut.évalué {
  background: #c6f6d5;
  color: #276749;
}

.projet-titre {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  color: #1a202c;
  line-height: 1.4;
}

.projet-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.meta-item {
  display: flex;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.meta-label {
  color: #718096;
  min-width: 80px;
}

.meta-value {
  color: #1a202c;
  flex: 1;
}

.avis-badge {
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.avis-badge.favorable {
  background: #c6f6d5;
  color: #276749;
}

.avis-badge.défavorable {
  background: #fed7d7;
  color: #c53030;
}

.projet-actions {
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.btn-voir {
  width: 100%;
  padding: 0.75rem;
  background: var(--dgppe-primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-voir:hover {
  background: var(--dgppe-primary-light);
}

@media (max-width: 768px) {
  .projets-grid {
    grid-template-columns: 1fr;
  }

  .filters-section {
    flex-direction: column;
  }
}
</style>
