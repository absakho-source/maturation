<template>
  <div class="gestion-comptes-page">
    <div class="header-section">
      <h1>Gestion des comptes soumissionnaires</h1>
      <p class="subtitle">Validation et gestion des comptes utilisateurs</p>
    </div>

    <!-- Filtres -->
    <div class="filters-section">
      <div class="filter-group">
        <label>Filtrer par statut :</label>
        <select v-model="filtreStatut" @change="chargerComptes">
          <option value="">Tous les comptes</option>
          <option value="non_verifie">Non vérifiés</option>
          <option value="verifie">Vérifiés</option>
          <option value="suspendu">Suspendus</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Rechercher :</label>
        <input
          v-model="rechercheTexte"
          type="text"
          placeholder="Nom, structure, email..."
          @input="filtrerComptes"
        />
      </div>
    </div>

    <!-- Statistiques rapides -->
    <div class="stats-section">
      <div class="stat-card non-verifie">
        <div class="stat-icon">⚠️</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.non_verifie }}</div>
          <div class="stat-label">Non vérifiés</div>
        </div>
      </div>
      <div class="stat-card verifie">
        <div class="stat-icon">✓</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.verifie }}</div>
          <div class="stat-label">Vérifiés</div>
        </div>
      </div>
      <div class="stat-card suspendu">
        <div class="stat-icon">🔴</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.suspendu }}</div>
          <div class="stat-label">Suspendus</div>
        </div>
      </div>
    </div>

    <!-- Tableau des comptes -->
    <div class="comptes-table-container">
      <div v-if="loading" class="loading">Chargement des comptes...</div>
      <div v-else-if="error" class="error-message">{{ error }}</div>
      <div v-else-if="comptesFiltres.length === 0" class="no-data">
        Aucun compte trouvé avec ces critères
      </div>

      <table v-else class="comptes-table">
        <thead>
          <tr>
            <th>Utilisateur</th>
            <th>Structure</th>
            <th>Contact</th>
            <th>Date création</th>
            <th>Statut</th>
            <th>Justificatif</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="compte in comptesFiltres" :key="compte.id">
            <td>
              <div class="user-info">
                <div class="user-name">{{ compte.display_name || compte.username }}</div>
                <div class="user-email">{{ compte.username }}</div>
                <div v-if="compte.fonction" class="user-fonction">{{ compte.fonction }}</div>
              </div>
            </td>
            <td>
              <div class="structure-info">
                <div class="structure-type">{{ formatTypeStructure(compte.type_structure) }}</div>
                <div class="structure-nom">{{ compte.nom_structure }}</div>
              </div>
            </td>
            <td>
              <div class="contact-info">
                <div v-if="compte.telephone">📞 {{ compte.telephone }}</div>
              </div>
            </td>
            <td>
              <div class="date-info">
                {{ formatDate(compte.date_creation) }}
              </div>
            </td>
            <td>
              <span :class="['badge-statut', compte.statut_compte || 'non_verifie']">
                {{ formatStatut(compte.statut_compte) }}
              </span>
              <div v-if="compte.verifie_par" class="verif-info">
                Par {{ compte.verifie_par }}
              </div>
            </td>
            <td>
              <button
                v-if="compte.justificatif_path"
                @click="voirJustificatif(compte.justificatif_path)"
                class="btn-voir-justificatif"
              >
                📄 Voir
              </button>
              <span v-else class="no-justificatif">Non fourni</span>
            </td>
            <td>
              <div class="actions-buttons">
                <button
                  v-if="compte.statut_compte === 'non_verifie'"
                  @click="verifierCompte(compte.id)"
                  class="btn-action btn-verify"
                  :disabled="actionEnCours === compte.id"
                >
                  {{ actionEnCours === compte.id ? '...' : '✓ Vérifier' }}
                </button>
                <button
                  v-if="compte.statut_compte === 'verifie' || compte.statut_compte === 'non_verifie'"
                  @click="suspendreCompte(compte.id)"
                  class="btn-action btn-suspend"
                  :disabled="actionEnCours === compte.id"
                >
                  {{ actionEnCours === compte.id ? '...' : '🔴 Suspendre' }}
                </button>
                <button
                  @click="voirDetails(compte)"
                  class="btn-action btn-details"
                >
                  👁️ Détails
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal détails -->
    <div v-if="compteSelectionne" class="modal-overlay" @click.self="fermerDetails">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Détails du compte</h2>
          <button @click="fermerDetails" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-row">
            <span class="detail-label">Nom complet :</span>
            <span class="detail-value">{{ compteSelectionne.nom_complet || compteSelectionne.display_name || 'N/A' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Email :</span>
            <span class="detail-value">{{ compteSelectionne.username }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Téléphone :</span>
            <span class="detail-value">{{ compteSelectionne.telephone || 'N/A' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Fonction :</span>
            <span class="detail-value">{{ compteSelectionne.fonction || 'N/A' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Type de structure :</span>
            <span class="detail-value">{{ formatTypeStructure(compteSelectionne.type_structure) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Nom de la structure :</span>
            <span class="detail-value">{{ compteSelectionne.nom_structure || 'N/A' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Statut du compte :</span>
            <span :class="['badge-statut', compteSelectionne.statut_compte || 'non_verifie']">
              {{ formatStatut(compteSelectionne.statut_compte) }}
            </span>
          </div>
          <div v-if="compteSelectionne.date_verification" class="detail-row">
            <span class="detail-label">Date de vérification :</span>
            <span class="detail-value">{{ formatDate(compteSelectionne.date_verification) }}</span>
          </div>
          <div v-if="compteSelectionne.verifie_par" class="detail-row">
            <span class="detail-label">Vérifié par :</span>
            <span class="detail-value">{{ compteSelectionne.verifie_par }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Date de création :</span>
            <span class="detail-value">{{ formatDate(compteSelectionne.date_creation) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

// État
const comptes = ref([])
const comptesFiltres = ref([])
const filtreStatut = ref('')
const rechercheTexte = ref('')
const loading = ref(false)
const error = ref('')
const actionEnCours = ref(null)
const compteSelectionne = ref(null)

// Récupérer l'utilisateur connecté
const userStr = localStorage.getItem('user')
const user = userStr ? JSON.parse(userStr) : null

// Statistiques
const stats = computed(() => {
  return {
    non_verifie: comptes.value.filter(c => (c.statut_compte || 'non_verifie') === 'non_verifie').length,
    verifie: comptes.value.filter(c => c.statut_compte === 'verifie').length,
    suspendu: comptes.value.filter(c => c.statut_compte === 'suspendu').length
  }
})

// Charger les comptes au montage
onMounted(() => {
  chargerComptes()
})

async function chargerComptes() {
  loading.value = true
  error.value = ''

  try {
    const params = {
      role: user?.role
    }
    if (filtreStatut.value) {
      params.statut = filtreStatut.value
    }

    const response = await axios.get('/api/admin/users', { params })
    comptes.value = response.data.filter(u => u.role === 'soumissionnaire')
    filtrerComptes()
  } catch (err) {
    console.error('Erreur lors du chargement des comptes:', err)
    error.value = 'Erreur lors du chargement des comptes'
  } finally {
    loading.value = false
  }
}

function filtrerComptes() {
  if (!rechercheTexte.value) {
    comptesFiltres.value = comptes.value
    return
  }

  const texte = rechercheTexte.value.toLowerCase()
  comptesFiltres.value = comptes.value.filter(compte => {
    return (
      (compte.display_name || '').toLowerCase().includes(texte) ||
      (compte.username || '').toLowerCase().includes(texte) ||
      (compte.nom_structure || '').toLowerCase().includes(texte) ||
      (compte.fonction || '').toLowerCase().includes(texte)
    )
  })
}

async function verifierCompte(compteId) {
  if (!confirm('Voulez-vous vérifier ce compte ?')) return

  actionEnCours.value = compteId

  try {
    await axios.post(`/api/admin/users/${compteId}/verify`, {
      role: user?.role,
      validateur_username: user?.username
    })

    // Recharger les comptes
    await chargerComptes()
    alert('Compte vérifié avec succès')
  } catch (err) {
    console.error('Erreur lors de la vérification:', err)
    alert('Erreur lors de la vérification du compte')
  } finally {
    actionEnCours.value = null
  }
}

async function suspendreCompte(compteId) {
  if (!confirm('Voulez-vous suspendre ce compte ? Cette action empêchera l\'utilisateur de soumettre des projets.')) return

  actionEnCours.value = compteId

  try {
    await axios.post(`/api/admin/users/${compteId}/suspend`, {
      role: user?.role
    })

    // Recharger les comptes
    await chargerComptes()
    alert('Compte suspendu avec succès')
  } catch (err) {
    console.error('Erreur lors de la suspension:', err)
    alert('Erreur lors de la suspension du compte')
  } finally {
    actionEnCours.value = null
  }
}

function voirJustificatif(path) {
  // Ouvrir le justificatif dans un nouvel onglet
  window.open(`/api/uploads/${path.replace('justificatifs/', '')}`, '_blank')
}

function voirDetails(compte) {
  compteSelectionne.value = compte
}

function fermerDetails() {
  compteSelectionne.value = null
}

function formatStatut(statut) {
  const labels = {
    non_verifie: '⚠️ Non vérifié',
    verifie: '✓ Vérifié',
    suspendu: '🔴 Suspendu'
  }
  return labels[statut] || labels.non_verifie
}

function formatTypeStructure(type) {
  const labels = {
    ministere: 'Ministère',
    region: 'Région',
    departement: 'Département',
    commune: 'Commune',
    agence: 'Agence',
    autre: 'Autre'
  }
  return labels[type] || type || 'N/A'
}

function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.gestion-comptes-page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header-section {
  margin-bottom: 2rem;
}

.header-section h1 {
  font-size: 2rem;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #718096;
  font-size: 1rem;
}

/* Filtres */
.filters-section {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
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
  font-weight: 600;
  color: #4a5568;
  font-size: 0.9rem;
}

.filter-group select,
.filter-group input {
  padding: 0.75rem;
  border: 1px solid #cbd5e0;
  border-radius: 8px;
  font-size: 1rem;
}

/* Statistiques */
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-card.non-verifie {
  background: #fff3cd;
  border-left: 4px solid #ffc107;
}

.stat-card.verifie {
  background: #d4edda;
  border-left: 4px solid #28a745;
}

.stat-card.suspendu {
  background: #f8d7da;
  border-left: 4px solid #dc3545;
}

.stat-icon {
  font-size: 2rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1a202c;
}

.stat-label {
  font-size: 0.9rem;
  color: #4a5568;
}

/* Tableau */
.comptes-table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.loading,
.error-message,
.no-data {
  padding: 3rem;
  text-align: center;
  color: #718096;
}

.error-message {
  color: #e53e3e;
}

.comptes-table {
  width: 100%;
  border-collapse: collapse;
}

.comptes-table thead {
  background: #f7fafc;
}

.comptes-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #2d3748;
  border-bottom: 2px solid #e2e8f0;
  font-size: 0.9rem;
}

.comptes-table td {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  vertical-align: top;
}

.comptes-table tbody tr:hover {
  background: #f7fafc;
}

/* Cellules */
.user-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-name {
  font-weight: 600;
  color: #1a202c;
}

.user-email {
  font-size: 0.85rem;
  color: #718096;
  font-family: 'Courier New', monospace;
}

.user-fonction {
  font-size: 0.85rem;
  color: #4a5568;
  font-style: italic;
}

.structure-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.structure-type {
  font-size: 0.8rem;
  color: #718096;
  text-transform: uppercase;
  font-weight: 600;
}

.structure-nom {
  color: #2d3748;
}

.contact-info {
  font-size: 0.9rem;
  color: #4a5568;
}

.date-info {
  font-size: 0.85rem;
  color: #718096;
  white-space: nowrap;
}

.badge-statut {
  display: inline-block;
  padding: 0.4rem 0.8rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
}

.badge-statut.non_verifie {
  background: #fff3cd;
  color: #856404;
}

.badge-statut.verifie {
  background: #d4edda;
  color: #155724;
}

.badge-statut.suspendu {
  background: #f8d7da;
  color: #721c24;
}

.verif-info {
  font-size: 0.75rem;
  color: #718096;
  margin-top: 0.25rem;
}

.btn-voir-justificatif {
  background: #3182ce;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
}

.btn-voir-justificatif:hover {
  background: #2c5282;
}

.no-justificatif {
  color: #a0aec0;
  font-size: 0.85rem;
  font-style: italic;
}

.actions-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.btn-action {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-verify {
  background: #28a745;
  color: white;
}

.btn-verify:hover:not(:disabled) {
  background: #218838;
}

.btn-suspend {
  background: #dc3545;
  color: white;
}

.btn-suspend:hover:not(:disabled) {
  background: #c82333;
}

.btn-details {
  background: #6c757d;
  color: white;
}

.btn-details:hover {
  background: #5a6268;
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h2 {
  margin: 0;
  color: #1a202c;
  font-size: 1.5rem;
}

.btn-close {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #718096;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  color: #2d3748;
}

.modal-body {
  padding: 1.5rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f7fafc;
}

.detail-label {
  font-weight: 600;
  color: #4a5568;
  flex: 0 0 40%;
}

.detail-value {
  color: #1a202c;
  flex: 1;
  text-align: right;
}

@media (max-width: 1024px) {
  .comptes-table {
    font-size: 0.85rem;
  }

  .comptes-table th,
  .comptes-table td {
    padding: 0.75rem 0.5rem;
  }

  .actions-buttons {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .btn-action {
    flex: 1;
    min-width: 80px;
  }
}

@media (max-width: 768px) {
  .gestion-comptes-page {
    padding: 1rem;
  }

  .comptes-table-container {
    overflow-x: auto;
  }

  .comptes-table {
    min-width: 800px;
  }

  .stats-section {
    grid-template-columns: 1fr;
  }
}
</style>
