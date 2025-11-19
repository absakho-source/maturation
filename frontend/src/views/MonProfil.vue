<template>
  <PageWrapper>
    <div class="mon-profil-container">
    <div class="profile-header">
      <h1>Mon Profil</h1>
      <p class="subtitle">Gérer mes informations personnelles</p>
    </div>

    <!-- Section : Informations du profil -->
    <div class="profile-section">
      <h2>Informations personnelles</h2>
      <form @submit.prevent="updateProfile" class="profile-form">
        <div class="form-group">
          <label for="email">Email *</label>
          <input
            type="email"
            id="email"
            v-model="profile.email"
            required
            placeholder="votre.email@exemple.com"
          />
        </div>

        <div class="form-group">
          <label for="telephone">Téléphone</label>
          <input
            type="tel"
            id="telephone"
            v-model="profile.telephone"
            placeholder="+221 XX XXX XX XX"
            @focus="initTelephone"
          />
        </div>

        <div class="form-group">
          <label for="fonction">Fonction / Poste</label>
          <input
            type="text"
            id="fonction"
            v-model="profile.fonction"
            placeholder="Ex: Chef de service, Directeur, etc."
          />
        </div>

        <!-- Structure d'appartenance - Affichage hiérarchique -->
        <div class="form-group">
          <label>Structure d'appartenance</label>
          <div class="structure-hierarchy readonly-field">
            <div v-if="profile.type_structure" class="hierarchy-item">
              <span class="hierarchy-label">Type de structure :</span>
              <span class="hierarchy-value">{{ getTypeStructureLabel(profile.type_structure) }}</span>
            </div>
            <div v-if="profile.type_institution" class="hierarchy-item">
              <span class="hierarchy-label">Type d'institution :</span>
              <span class="hierarchy-value">{{ getTypeInstitutionLabel(profile.type_institution) }}</span>
            </div>
            <div v-if="profile.nom_structure" class="hierarchy-item">
              <span class="hierarchy-label">Nom :</span>
              <span class="hierarchy-value">{{ profile.nom_structure }}</span>
            </div>
            <div v-if="profile.direction_service" class="hierarchy-item">
              <span class="hierarchy-label">Direction / Service :</span>
              <span class="hierarchy-value">{{ profile.direction_service }}</span>
            </div>
            <div v-if="!profile.type_structure && !profile.nom_structure" class="hierarchy-item empty">
              <span class="hierarchy-value">Non renseigné</span>
            </div>
          </div>
          <small class="form-hint">Ces champs ne peuvent être modifiés que par un administrateur</small>
        </div>

        <div class="form-actions">
          <button type="button" @click="goBack" class="btn-secondary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Retour
          </button>
          <button type="button" @click="cancelProfileChanges" class="btn-cancel">
            Annuler
          </button>
          <button type="submit" class="btn-primary" :disabled="updating">
            {{ updating ? 'Mise à jour...' : 'Mettre à jour' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Section : Changement de mot de passe -->
    <div class="profile-section">
      <h2>Changer le mot de passe</h2>
      <form @submit.prevent="changePassword" class="password-form">
        <div class="form-group">
          <label for="old-password">Ancien mot de passe *</label>
          <input
            type="password"
            id="old-password"
            v-model="passwordForm.oldPassword"
            required
            placeholder="Votre mot de passe actuel"
          />
        </div>

        <div class="form-group">
          <label for="new-password">Nouveau mot de passe *</label>
          <input
            type="password"
            id="new-password"
            v-model="passwordForm.newPassword"
            required
            placeholder="Votre nouveau mot de passe"
          />
        </div>

        <div class="form-group">
          <label for="confirm-password">Confirmer le nouveau mot de passe *</label>
          <input
            type="password"
            id="confirm-password"
            v-model="passwordForm.confirmPassword"
            required
            placeholder="Retapez le nouveau mot de passe"
          />
        </div>

        <div class="form-actions">
          <button type="button" @click="cancelPasswordChanges" class="btn-cancel">
            Annuler
          </button>
          <button type="submit" class="btn-primary" :disabled="changingPassword">
            {{ changingPassword ? 'Changement...' : 'Changer le mot de passe' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Messages de succès/erreur -->
    <div v-if="successMessage" class="alert alert-success">
      {{ successMessage }}
    </div>
    <div v-if="errorMessage" class="alert alert-error">
      {{ errorMessage }}
    </div>
    </div>
  </PageWrapper>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PageWrapper from '../components/PageWrapper.vue'

const router = useRouter()

// États
const profile = ref({
  email: '',
  telephone: '',
  fonction: '',
  type_structure: '',
  type_institution: '',
  nom_structure: '',
  direction_service: ''
})

const originalProfile = ref({
  email: '',
  telephone: '',
  fonction: '',
  type_structure: '',
  type_institution: '',
  nom_structure: '',
  direction_service: ''
})

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const updating = ref(false)
const changingPassword = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

// Charger les données du profil
onMounted(async () => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user) {
      router.push('/login')
      return
    }

    // Charger le profil depuis l'API backend
    const response = await fetch(`/api/users/${user.username}/profile`)
    if (response.ok) {
      const data = await response.json()
      profile.value.email = data.email
      profile.value.telephone = data.telephone || ''
      profile.value.fonction = data.fonction || ''
      profile.value.type_structure = data.type_structure || ''
      profile.value.type_institution = data.type_institution || ''
      profile.value.nom_structure = data.nom_structure || ''
      profile.value.direction_service = data.direction_service || ''
      // Sauvegarder les valeurs originales
      originalProfile.value.email = data.email
      originalProfile.value.telephone = data.telephone || ''
      originalProfile.value.fonction = data.fonction || ''
      originalProfile.value.type_structure = data.type_structure || ''
      originalProfile.value.type_institution = data.type_institution || ''
      originalProfile.value.nom_structure = data.nom_structure || ''
      originalProfile.value.direction_service = data.direction_service || ''
    } else {
      // En cas d'erreur, utiliser les données du localStorage comme fallback
      profile.value.email = user.username
      profile.value.telephone = user.telephone || ''
      profile.value.fonction = user.fonction || ''
      profile.value.type_structure = user.type_structure || ''
      profile.value.type_institution = user.type_institution || ''
      profile.value.nom_structure = user.nom_structure || ''
      profile.value.direction_service = user.direction_service || ''
      // Sauvegarder les valeurs originales
      originalProfile.value.email = user.username
      originalProfile.value.telephone = user.telephone || ''
      originalProfile.value.fonction = user.fonction || ''
      originalProfile.value.type_structure = user.type_structure || ''
      originalProfile.value.type_institution = user.type_institution || ''
      originalProfile.value.nom_structure = user.nom_structure || ''
      originalProfile.value.direction_service = user.direction_service || ''
    }
  } catch (error) {
    console.error('Erreur lors du chargement du profil:', error)
    // En cas d'erreur, utiliser les données du localStorage comme fallback
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (user) {
      profile.value.email = user.username
      profile.value.telephone = user.telephone || ''
      profile.value.fonction = user.fonction || ''
      profile.value.type_structure = user.type_structure || ''
      profile.value.type_institution = user.type_institution || ''
      profile.value.nom_structure = user.nom_structure || ''
      profile.value.direction_service = user.direction_service || ''
      // Sauvegarder les valeurs originales
      originalProfile.value.email = user.username
      originalProfile.value.telephone = user.telephone || ''
      originalProfile.value.fonction = user.fonction || ''
      originalProfile.value.type_structure = user.type_structure || ''
      originalProfile.value.type_institution = user.type_institution || ''
      originalProfile.value.nom_structure = user.nom_structure || ''
      originalProfile.value.direction_service = user.direction_service || ''
    }
    errorMessage.value = 'Erreur lors du chargement du profil'
  }
})

// Mettre à jour le profil
async function updateProfile() {
  try {
    updating.value = true
    successMessage.value = ''
    errorMessage.value = ''

    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user) {
      router.push('/login')
      return
    }

    const response = await fetch(`/api/users/${user.username}/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: profile.value.email,
        telephone: profile.value.telephone,
        fonction: profile.value.fonction
      })
    })

    const data = await response.json()

    if (response.ok) {
      successMessage.value = 'Profil mis à jour avec succès!'

      // Mettre à jour le localStorage avec les nouvelles données
      const updatedUser = {
        ...user,
        username: data.user.username,
        telephone: data.user.telephone
      }
      localStorage.setItem('user', JSON.stringify(updatedUser))

      // Effacer le message après 5 secondes
      setTimeout(() => {
        successMessage.value = ''
      }, 5000)
    } else {
      errorMessage.value = data.error || 'Erreur lors de la mise à jour du profil'
    }
  } catch (error) {
    console.error('Erreur:', error)
    errorMessage.value = 'Erreur lors de la mise à jour du profil'
  } finally {
    updating.value = false
  }
}

// Annuler les modifications du profil
function cancelProfileChanges() {
  profile.value.email = originalProfile.value.email
  profile.value.telephone = originalProfile.value.telephone
  profile.value.fonction = originalProfile.value.fonction
  profile.value.nom_structure = originalProfile.value.nom_structure
  profile.value.direction_service = originalProfile.value.direction_service
  successMessage.value = ''
  errorMessage.value = ''
}

// Annuler le changement de mot de passe
function cancelPasswordChanges() {
  passwordForm.value.oldPassword = ''
  passwordForm.value.newPassword = ''
  passwordForm.value.confirmPassword = ''
  successMessage.value = ''
  errorMessage.value = ''
}

// Fonctions helper pour les labels
function getTypeStructureLabel(type) {
  const labels = {
    'institution': 'Institution',
    'collectivite': 'Collectivité territoriale',
    'agence': 'Agence / Établissement public',
    'autre': 'Autre (ONG, Association, Cabinet, etc.)'
  }
  return labels[type] || type
}

function getTypeInstitutionLabel(type) {
  const labels = {
    'presidence': 'Présidence de la République',
    'primature': 'Primature',
    'ministere': 'Ministère',
    'autre_institution': 'Autre Institution'
  }
  return labels[type] || type
}

// Retour à la page précédente
function goBack() {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (user) {
    // Rediriger vers le dashboard approprié selon le rôle
    const dashboardRoutes = {
      'soumissionnaire': '/dashboard-soumissionnaire',
      'evaluateur1': '/evaluateur',
      'evaluateur2': '/evaluateur',
      'secretariatsct': '/secretariat-sct',
      'presidencesct': '/presidence-sct',
      'presidencecomite': '/presidence-comite',
      'admin': '/gestion-comptes'
    }
    const route = dashboardRoutes[user.role] || '/'
    router.push(route)
  } else {
    router.push('/')
  }
}

// Initialiser le téléphone avec +221 si vide
function initTelephone() {
  if (!profile.value.telephone || profile.value.telephone.trim() === '') {
    profile.value.telephone = '+221 '
  }
}

// Changer le mot de passe
async function changePassword() {
  try {
    changingPassword.value = true
    successMessage.value = ''
    errorMessage.value = ''

    // Vérifier que les mots de passe correspondent
    if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
      errorMessage.value = 'Les nouveaux mots de passe ne correspondent pas'
      return
    }

    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user) {
      router.push('/login')
      return
    }

    const response = await fetch(`/api/users/${user.username}/password`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        old_password: passwordForm.value.oldPassword,
        new_password: passwordForm.value.newPassword
      })
    })

    const data = await response.json()

    if (response.ok) {
      successMessage.value = 'Mot de passe changé avec succès!'

      // Réinitialiser le formulaire
      passwordForm.value.oldPassword = ''
      passwordForm.value.newPassword = ''
      passwordForm.value.confirmPassword = ''

      // Effacer le message après 5 secondes
      setTimeout(() => {
        successMessage.value = ''
      }, 5000)
    } else {
      errorMessage.value = data.error || 'Erreur lors du changement de mot de passe'
    }
  } catch (error) {
    console.error('Erreur:', error)
    errorMessage.value = 'Erreur lors du changement de mot de passe'
  } finally {
    changingPassword.value = false
  }
}
</script>

<style scoped>
.mon-profil-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.profile-header {
  margin-bottom: 3rem;
  text-align: center;
}

.profile-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1rem;
  color: #718096;
}

.profile-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-bottom: 2rem;
}

.profile-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e2e8f0;
}

.profile-form,
.password-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.95rem;
  font-weight: 600;
  color: #4a5568;
}

.form-group input {
  padding: 0.75rem;
  font-size: 1rem;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  transition: all 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.form-actions {
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-primary,
.btn-secondary,
.btn-cancel {
  padding: 0.75rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background-color: #4299e1;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #3182ce;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(50, 50, 93, 0.11), 0 1px 3px rgba(0, 0, 0, 0.08);
}

.btn-primary:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-secondary {
  background-color: #718096;
  color: white;
}

.btn-secondary:hover {
  background-color: #4a5568;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(50, 50, 93, 0.11), 0 1px 3px rgba(0, 0, 0, 0.08);
}

.btn-cancel {
  background-color: transparent;
  color: #e53e3e;
  border: 1px solid #e53e3e;
}

.btn-cancel:hover {
  background-color: #fff5f5;
  transform: translateY(-1px);
}

.alert {
  padding: 1rem;
  border-radius: 6px;
  margin-top: 1rem;
  font-weight: 500;
}

.alert-success {
  background-color: #c6f6d5;
  color: #22543d;
  border: 1px solid #9ae6b4;
}

/* Structure hiérarchique */
.structure-hierarchy {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
}

.readonly-field {
  background: #f7fafc;
  cursor: not-allowed;
}

.hierarchy-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e2e8f0;
}

.hierarchy-item:last-child {
  border-bottom: none;
}

.hierarchy-item.empty {
  justify-content: center;
  color: #a0aec0;
  font-style: italic;
}

.hierarchy-label {
  font-weight: 600;
  color: #4a5568;
  min-width: 150px;
  flex-shrink: 0;
}

.hierarchy-value {
  color: #2d3748;
  flex: 1;
}

.alert-error {
  background-color: #fed7d7;
  color: #742a2a;
  border: 1px solid #fc8181;
}

.readonly-input {
  background-color: #f7fafc;
  cursor: not-allowed;
  color: #718096;
}

.form-hint {
  font-size: 0.85rem;
  color: #718096;
  font-style: italic;
  margin-top: 0.25rem;
}
</style>
