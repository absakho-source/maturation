<template>
  <div class="register-page">
    <!-- En-tête harmonisé -->
    <header class="public-header">
      <div class="header-container">
        <div class="header-spacer"></div>
        <div class="header-center">
          <img :src="logo" alt="Logo DGPPE" class="header-logo" @click="$router.push('/')" style="cursor: pointer;" />
          <div class="header-info">
            <h2 class="header-title">Ministère de l'Économie, du Plan et de la Coopération</h2>
            <p class="header-subtitle">Direction Générale de la Planification des Politiques Économiques</p>
          </div>
        </div>
        <div class="header-spacer"></div>
      </div>
    </header>

    <main class="register-main">
      <div class="register-container">
        <div class="register-card">
          <h3 class="register-title">Création de compte soumissionnaire</h3>
          <form @submit.prevent="register">
        <!-- Informations personnelles -->
        <div class="form-section">
          <h3>Informations personnelles</h3>
          <input v-model="nomComplet" placeholder="Nom complet *" required />
          <div class="phone-input-group">
            <input v-model="indicatifTel" class="indicatif-input" placeholder="+221" pattern="\+\d{1,4}" required />
            <input v-model="telephone" class="telephone-input" placeholder="77 123 45 67" type="tel" required />
          </div>
          <input v-model="fonction" placeholder="Fonction/Poste *" required />
        </div>

        <!-- Type de structure -->
        <div class="form-section">
          <h3>Structure d'appartenance</h3>
          <label for="type-structure">Type de structure *</label>
          <select id="type-structure" v-model="typeStructure" @change="onTypeStructureChange" required>
            <option value="">-- Sélectionnez --</option>
            <option value="ministere">Ministère / Direction nationale</option>
            <option value="collectivite">Collectivité territoriale</option>
            <option value="agence">Agence / Établissement public</option>
            <option value="autre">Autre (ONG, Association, Cabinet, etc.)</option>
          </select>

          <!-- Ministère - deux champs séparés -->
          <div v-if="typeStructure === 'ministere'">
            <label for="nom-direction">Direction / Service *</label>
            <input
              id="nom-direction"
              v-model="nomDirection"
              placeholder="Ex: Direction Générale de la Planification des Politiques Économiques (DGPPE)"
              required
            />
            <label for="nom-ministere">Ministère de tutelle *</label>
            <select id="nom-ministere" v-model="nomMinistere" required>
              <option value="">-- Sélectionnez l'autorité de tutelle --</option>
              <option value="Primature">Primature</option>
              <option value="Présidence de la République">Présidence de la République</option>
              <option value="__ministere__">Ministère sectoriel</option>
            </select>

            <!-- Champ libre si ministère sectoriel sélectionné -->
            <div v-if="nomMinistere === '__ministere__'">
              <label for="nom-ministere-libre">Nom du ministère *</label>
              <input
                id="nom-ministere-libre"
                v-model="nomMinistereLibre"
                placeholder="Ex: Ministère de l'Économie, du Plan et de la Coopération"
                required
              />
            </div>
          </div>

          <!-- Collectivité territoriale - sélection en cascade -->
          <div v-else-if="typeStructure === 'collectivite'">
            <label for="niveau-collectivite">Niveau *</label>
            <select id="niveau-collectivite" v-model="niveauCollectivite" @change="onNiveauCollectiviteChange" required>
              <option value="">-- Sélectionnez le niveau --</option>
              <option value="region">Région</option>
              <option value="departement">Département</option>
              <option value="commune">Commune</option>
            </select>

            <!-- Si région sélectionnée -->
            <div v-if="niveauCollectivite === 'region'">
              <label for="nom-structure">Région *</label>
              <select id="nom-structure" v-model="nomStructure" required>
                <option value="">-- Sélectionnez une région --</option>
                <option v-for="region in regions" :key="region" :value="`Région de ${region}`">
                  Région de {{ region }}
                </option>
              </select>
            </div>

            <!-- Si département sélectionné -->
            <div v-if="niveauCollectivite === 'departement'">
              <label for="region-parent">Région *</label>
              <select id="region-parent" v-model="regionParente" @change="onRegionChange" required>
                <option value="">-- Sélectionnez une région --</option>
                <option v-for="region in regions" :key="region" :value="region">
                  {{ region }}
                </option>
              </select>
              <label for="nom-structure">Département *</label>
              <select id="nom-structure" v-model="nomStructure" :disabled="!regionParente" required>
                <option value="">-- Sélectionnez un département --</option>
                <option v-for="dept in departementsFiltered" :key="dept" :value="`Département de ${dept}`">
                  Département de {{ dept }}
                </option>
              </select>
            </div>

            <!-- Si commune sélectionnée -->
            <div v-if="niveauCollectivite === 'commune'">
              <label for="region-parent">Région *</label>
              <select id="region-parent" v-model="regionParente" @change="onRegionChangeCommunes" required>
                <option value="">-- Sélectionnez une région --</option>
                <option v-for="region in regions" :key="region" :value="region">
                  {{ region }}
                </option>
              </select>

              <label for="departement-parent">Département *</label>
              <select id="departement-parent" v-model="departementParent" @change="onDepartementChangeCommunes" :disabled="!regionParente" required>
                <option value="">-- Sélectionnez un département --</option>
                <option v-for="dept in departementsFiltered" :key="dept" :value="dept">
                  {{ dept }}
                </option>
              </select>

              <label for="commune-select">Commune *</label>
              <select id="commune-select" v-model="communeSelectionnee" @change="onCommuneChange" :disabled="!departementParent" required>
                <option value="">-- Sélectionnez une commune --</option>
                <option v-for="commune in communesFiltered" :key="commune" :value="commune">
                  {{ commune }}
                </option>
                <option value="__autre__">Autre commune (non listée)</option>
              </select>

              <!-- Champ de saisie libre si "Autre commune" est sélectionnée -->
              <div v-if="communeSelectionnee === '__autre__'">
                <label for="nom-structure">Nom de la commune *</label>
                <input
                  id="nom-structure"
                  v-model="nomStructure"
                  placeholder="Ex: Commune de Dar Salam"
                  required
                />
              </div>
            </div>
          </div>

          <!-- Agence - champ libre + autorité de tutelle -->
          <div v-else-if="typeStructure === 'agence'">
            <label for="nom-agence">Nom de l'agence / établissement *</label>
            <input
              id="nom-agence"
              v-model="nomAgence"
              placeholder="Ex: APIX SA, SENELEC, etc."
              required
            />

            <label for="tutelle-agence">Autorité de tutelle *</label>
            <select id="tutelle-agence" v-model="tutelleAgence" required>
              <option value="">-- Sélectionnez l'autorité de tutelle --</option>
              <option value="Primature">Primature</option>
              <option value="Présidence de la République">Présidence de la République</option>
              <option value="__ministere__">Ministère sectoriel</option>
            </select>

            <!-- Champ libre si ministère sectoriel sélectionné -->
            <div v-if="tutelleAgence === '__ministere__'">
              <label for="tutelle-agence-libre">Nom du ministère de tutelle *</label>
              <input
                id="tutelle-agence-libre"
                v-model="tutelleAgenceLibre"
                placeholder="Ex: Ministère de l'Économie, du Plan et de la Coopération"
                required
              />
            </div>
          </div>

          <!-- Autre - champ libre -->
          <div v-else-if="typeStructure === 'autre'">
            <label for="nom-structure">Nom de la structure *</label>
            <input
              id="nom-structure"
              v-model="nomStructure"
              placeholder="Ex: ONG XYZ, Cabinet ABC, etc."
              required
            />
          </div>
        </div>

        <!-- Justificatifs (facultatif) -->
        <div class="form-section">
          <h3>Justificatifs</h3>
          <p class="info-text">
            Upload facultatif mais recommandé pour une validation rapide de votre compte
            (carte professionnelle, attestation, etc.)
          </p>
          <div class="file-upload-zone" @click="$refs.fileInput.click()">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <span v-if="justificatifFiles.length === 0">Cliquez pour choisir un ou plusieurs fichiers</span>
            <span v-else class="file-selected">{{ justificatifFiles.length }} fichier(s) sélectionné(s)</span>
          </div>
          <input
            ref="fileInput"
            type="file"
            @change="onFileChange"
            accept=".pdf,.jpg,.jpeg,.png"
            multiple
            style="display: none;"
          />
          <!-- Liste des fichiers sélectionnés -->
          <div v-if="justificatifFiles.length > 0" class="selected-files">
            <div v-for="(file, index) in justificatifFiles" :key="index" class="file-item">
              <span class="file-name">{{ file.name }}</span>
              <button type="button" @click="removeFile(index)" class="remove-file-btn">×</button>
            </div>
          </div>
        </div>

        <!-- Identifiants de connexion -->
        <div class="form-section">
          <h3>Identifiants de connexion</h3>
          <input v-model="username" placeholder="Adresse email *" type="email" required />
          <input v-model="password" placeholder="Mot de passe *" type="password" required minlength="6" />
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? 'Création en cours...' : 'Créer mon compte' }}
        </button>
      </form>

      <div v-if="message" class="message-box success">
        <p>{{ message }}</p>
        <p class="small-text">Votre compte a été créé avec le statut "Non vérifié". Vous pouvez déjà soumettre des projets en attendant la validation par un administrateur.</p>
      </div>
      <p v-if="error" class="message-box error">{{ error }}</p>

      <p class="link">
        Déjà un compte ? <router-link to="/login">Se connecter</router-link>
      </p>
        </div>
      </div>
    </main>

    <!-- Footer harmonisé -->
    <footer class="public-footer">
      <div class="footer-container">
        <div class="footer-simple">
          <p>&copy; {{ currentYear }} Direction Générale de la Planification des Politiques Économiques (DGPPE)</p>
          <p>Plateforme de maturation • Version 1.0 • Développée par Abou Sakho</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import logo from '../assets/logo-dgppe.png'

// Données du formulaire
const nomComplet = ref('')
const indicatifTel = ref('+221')
const telephone = ref('')
const fonction = ref('')
const typeStructure = ref('')
const niveauCollectivite = ref('') // Nouveau: pour gérer le niveau de collectivité
const nomDirection = ref('') // Pour les ministères
const nomMinistere = ref('') // Pour les ministères - select (Primature, Présidence, __ministere__)
const nomMinistereLibre = ref('') // Pour le nom du ministère si ministère sectoriel sélectionné
const nomAgence = ref('') // Pour les agences
const tutelleAgence = ref('') // Tutelle agence - select
const tutelleAgenceLibre = ref('') // Nom ministère si ministère sectoriel sélectionné
const nomStructure = ref('')
const regionParente = ref('')
const departementParent = ref('') // Pour la sélection de commune
const communeSelectionnee = ref('') // Track commune dropdown selection
const justificatifFiles = ref([]) // Changé en tableau pour multi-fichiers
const username = ref('')
const password = ref('')
const loading = ref(false)
const message = ref('')
const error = ref('')

// Listes de données
const regions = ref([])
const departements = ref({}) // Format: { region: [dept1, dept2, ...] }
const communes = ref({}) // Format: { departement: [commune1, commune2, ...] }
const ministeres = ref([])
const agences = ref([])

// Départements filtrés selon la région sélectionnée
const departementsFiltered = computed(() => {
  if (!regionParente.value) return []
  return departements.value[regionParente.value] || []
})

// Communes filtrées selon le département sélectionné
const communesFiltered = computed(() => {
  if (!departementParent.value) return []
  return communes.value[departementParent.value] || []
})

// Année actuelle pour le footer
const currentYear = computed(() => new Date().getFullYear())

// Charger les données au montage
onMounted(async () => {
  await loadDataLists()
})

async function loadDataLists() {
  try {
    // Charger les régions
    const resRegions = await axios.get('/api/data/regions')
    regions.value = resRegions.data

    // Charger les départements (format dictionnaire)
    const resDept = await axios.get('/api/data/departements?format=dict')
    departements.value = resDept.data

    // Charger les communes (format dictionnaire par département)
    const resCommunes = await axios.get('/api/data/communes?format=dict')
    communes.value = resCommunes.data

    // Charger les ministères
    const resMinisteres = await axios.get('/api/data/ministeres')
    ministeres.value = resMinisteres.data

    // Charger les agences
    const resAgences = await axios.get('/api/data/agences')
    agences.value = resAgences.data

  } catch (err) {
    console.error('Erreur lors du chargement des données:', err)
    // Pas d'affichage d'erreur pour ne pas bloquer l'utilisateur
    // Les listes seront chargées au besoin
  }
}

function onTypeStructureChange() {
  // Réinitialiser tous les champs quand le type change
  nomDirection.value = ''
  nomMinistere.value = ''
  nomMinistereLibre.value = ''
  nomAgence.value = ''
  tutelleAgence.value = ''
  tutelleAgenceLibre.value = ''
  nomStructure.value = ''
  niveauCollectivite.value = ''
  regionParente.value = ''
}

function onNiveauCollectiviteChange() {
  // Réinitialiser le nom de structure et la région parente quand le niveau change
  nomStructure.value = ''
  regionParente.value = ''
  departementParent.value = ''
  communeSelectionnee.value = ''
}

function onRegionChange() {
  // Réinitialiser le département quand la région change (pour les départements)
  nomStructure.value = ''
}

function onRegionChangeCommunes() {
  // Réinitialiser le département et la commune quand la région change (pour les communes)
  departementParent.value = ''
  communeSelectionnee.value = ''
  nomStructure.value = ''
}

function onDepartementChangeCommunes() {
  // Réinitialiser la commune quand le département change
  nomStructure.value = ''
  communeSelectionnee.value = ''
}

function onCommuneChange() {
  if (communeSelectionnee.value !== '__autre__') {
    nomStructure.value = communeSelectionnee.value
  } else {
    nomStructure.value = ''
  }
}

function onFileChange(event) {
  const files = Array.from(event.target.files)

  // Vérifier chaque fichier
  for (const file of files) {
    // Vérifier la taille (max 5MB par fichier)
    if (file.size > 5 * 1024 * 1024) {
      error.value = `Le fichier ${file.name} est trop volumineux (max 5MB par fichier)`
      return
    }
  }

  // Ajouter les nouveaux fichiers à la liste
  justificatifFiles.value = [...justificatifFiles.value, ...files]

  // Réinitialiser l'input pour permettre de sélectionner les mêmes fichiers à nouveau
  event.target.value = ''
}

function removeFile(index) {
  justificatifFiles.value.splice(index, 1)
}

async function register() {
  message.value = ''
  error.value = ''
  loading.value = true

  try {
    // 1. Créer le compte utilisateur
    const displayName = nomComplet.value.trim()
    const telephoneComplet = `${indicatifTel.value} ${telephone.value}`.trim()

    // Pour les ministères, combiner direction et tutelle
    let structureFinal = nomStructure.value
    if (typeStructure.value === 'ministere' && nomDirection.value && nomMinistere.value) {
      const tutelleFinal = nomMinistere.value === '__ministere__' ? nomMinistereLibre.value : nomMinistere.value
      structureFinal = `${nomDirection.value} - ${tutelleFinal}`
    }

    // Pour les agences, combiner nom agence et tutelle
    if (typeStructure.value === 'agence' && nomAgence.value && tutelleAgence.value) {
      const tutelleFinal = tutelleAgence.value === '__ministere__' ? tutelleAgenceLibre.value : tutelleAgence.value
      structureFinal = `${nomAgence.value} - ${tutelleFinal}`
    }

    const userData = {
      username: username.value,
      password: password.value,
      role: 'soumissionnaire', // Tous les comptes créés via ce formulaire sont soumissionnaires
      display_name: displayName,
      nom_complet: nomComplet.value,
      telephone: telephoneComplet,
      fonction: fonction.value,
      type_structure: typeStructure.value,
      nom_structure: structureFinal
    }

    const response = await axios.post('/api/users', userData)

    // 2. Si des justificatifs ont été fournis, les uploader
    if (justificatifFiles.value.length > 0) {
      try {
        const formData = new FormData()

        // Ajouter tous les fichiers
        justificatifFiles.value.forEach((file, index) => {
          formData.append('files', file)
        })
        formData.append('username', username.value)

        await axios.post('/api/users/upload-justificatifs', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
      } catch (uploadErr) {
        console.error('Erreur upload justificatifs:', uploadErr)
        // Ne pas bloquer l'inscription si l'upload échoue
      }
    }

    message.value = 'Compte créé avec succès ! Vous pouvez maintenant vous connecter.'

    // Réinitialiser le formulaire
    nomComplet.value = ''
    indicatifTel.value = '+221'
    telephone.value = ''
    fonction.value = ''
    typeStructure.value = ''
    niveauCollectivite.value = ''
    nomDirection.value = ''
    nomMinistere.value = ''
    nomMinistereLibre.value = ''
    nomAgence.value = ''
    tutelleAgence.value = ''
    tutelleAgenceLibre.value = ''
    nomStructure.value = ''
    regionParente.value = ''
    departementParent.value = ''
    communeSelectionnee.value = ''
    justificatifFiles.value = []
    username.value = ''
    password.value = ''

  } catch (err) {
    console.error('Erreur lors de la création du compte:', err)
    error.value = err.response?.data?.error || 'Erreur lors de la création du compte. Vérifiez les informations et réessayez.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ====================  PAGE STRUCTURE ==================== */
.register-page {
  min-height: 100vh;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
}

/* ==================== HEADER HARMONISÉ ==================== */
.public-header {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 1.5rem;
}

.header-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.header-logo {
  height: 60px;
  width: auto;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.header-logo:hover {
  opacity: 0.9;
}

.header-info {
  text-align: center;
}

.header-title {
  font-size: 1.1rem;
  margin: 0;
  font-weight: 600;
  color: #1a202c;
}

.header-subtitle {
  font-size: 0.85rem;
  margin: 0.25rem 0 0 0;
  color: #4a5568;
}

/* ==================== MAIN CONTENT ==================== */
.register-main {
  flex: 1;
  display: flex;
  justify-content: center;
  padding: 1rem 1rem;
}

.register-container {
  width: 100%;
  max-width: 800px;
}

.register-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.register-title {
  text-align: center;
  color: #1a202c;
  margin: 0 0 1.5rem 0;
  font-size: 1.4rem;
  font-weight: 600;
}

/* Compatibilité: cacher les anciens éléments */
.auth-page,
.auth-header-fixed {
  display: none !important;
}

.auth-container {
  max-width: 1000px;
  width: 100%;
  margin: 0 auto;
  padding: 0 1rem;
}

.auth-card {
  background: white;
  color: #001f3f;
  border-radius: 12px;
  padding: 2.5rem;
  width: 100%;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  margin-bottom: 1rem;
}

.logo {
  width: 60px;
  margin-bottom: 8px;
  transition: opacity 0.2s ease;
  filter: brightness(0) invert(1);
}

.logo:hover {
  opacity: 0.85;
}

/* Styles pour l'en-tête fixe */
.auth-header-fixed h2 {
  font-size: 1.3rem;
  margin: 6px 0 4px 0;
  color: white;
  font-weight: 600;
}

.auth-header-fixed .subtitle {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 3px 0;
  font-weight: 400;
}

.auth-header-fixed .subtitle-direction {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 3px 0;
}

.auth-header-fixed .subtitle-dgppe {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 1);
  margin: 0;
  font-weight: 500;
}

h2 {
  margin: 10px 0;
  font-size: 1.6rem;
}

.subtitle {
  font-size: 0.95rem;
  color: #444;
  margin-bottom: 5px;
}

.subtitle-direction {
  font-size: 0.875rem;
  color: #666;
  margin-bottom: 5px;
}

.subtitle-dgppe {
  font-size: 0.95rem;
  color: #444;
  margin-bottom: 25px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  text-align: left;
}

.form-section {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.form-section h3 {
  margin: 0 0 12px 0;
  font-size: 1rem;
  color: #004080;
  text-align: left;
}

label {
  display: block;
  margin: 8px 0 4px 0;
  font-weight: 500;
  font-size: 0.9rem;
  color: #333;
}

input, select {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 1rem;
  box-sizing: border-box;
}

input:focus, select:focus {
  outline: none;
  border-color: #004080;
  box-shadow: 0 0 0 3px rgba(0, 64, 128, 0.1);
}

.phone-input-group {
  display: flex;
  gap: 10px;
}

.indicatif-input {
  flex: 0 0 100px;
  width: 100px;
}

.telephone-input {
  flex: 1;
}

.info-text {
  font-size: 0.85rem;
  color: #666;
  margin: 5px 0;
  font-style: italic;
}

.file-upload-zone {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 10px;
}

.file-upload-zone:hover {
  border-color: #004080;
  background: #f0f8ff;
}

.file-upload-zone svg {
  margin-bottom: 10px;
  color: #666;
}

.file-selected {
  color: #004080;
  font-weight: 600;
}

.selected-files {
  margin-top: 15px;
  max-height: 200px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  margin-bottom: 8px;
}

.file-name {
  flex: 1;
  font-size: 0.9rem;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 10px;
}

.remove-file-btn {
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  font-size: 1.2rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background-color 0.2s;
}

.remove-file-btn:hover {
  background: #c82333;
}

button {
  background: linear-gradient(135deg, var(--dgppe-primary) 0%, var(--dgppe-primary-light) 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  font-size: 1rem;
  margin-top: 10px;
  box-shadow: 0 4px 8px rgba(0, 51, 102, 0.15);
}

button:hover {
  background: linear-gradient(135deg, var(--dgppe-primary-light) 0%, var(--dgppe-primary) 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 51, 102, 0.2);
}

button:disabled {
  background-color: #999;
  cursor: not-allowed;
}

.message-box {
  margin-top: 15px;
  padding: 15px;
  border-radius: 8px;
  text-align: left;
}

.message-box.success {
  background: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
}

.message-box.error {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}

.message-box p {
  margin: 0 0 5px 0;
}

.small-text {
  font-size: 0.85rem;
  opacity: 0.9;
}

.link {
  margin-top: 20px;
  font-size: 0.9rem;
}

.link a {
  color: #004080;
  text-decoration: none;
  font-weight: 600;
}

.link a:hover {
  text-decoration: underline;
}

/* ==================== FOOTER HARMONISÉ ==================== */
.public-footer {
  background: linear-gradient(135deg, var(--dgppe-primary) 0%, #1e40af 100%);
  color: white;
  padding: 1.5rem 0;
  margin-top: auto;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.footer-simple {
  text-align: center;
}

.footer-simple p:first-child {
  font-size: 0.875rem;
  font-weight: 500;
  margin: 0 0 0.5rem 0;
  color: white;
}

.footer-simple p:last-child {
  font-size: 0.75rem;
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
}

/* ==================== RESPONSIVE ==================== */
@media (max-width: 768px) {
  .header-container {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 1rem;
  }

  .header-spacer {
    display: none;
  }

  .header-title {
    font-size: 1rem;
  }

  .header-subtitle {
    font-size: 0.8rem;
  }

  .header-logo {
    height: 50px;
  }

  .register-title {
    font-size: 1.3rem;
  }

  .auth-card,
  .register-card {
    padding: 1.5rem;
  }

  h2 {
    font-size: 1.3rem;
  }

  .form-section {
    padding: 15px;
  }
}
</style>
