<template>
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
          />
        </div>

        <div class="form-actions">
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// États
const profile = ref({
  email: '',
  telephone: ''
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

    profile.value.email = user.username
    profile.value.telephone = user.telephone || ''
  } catch (error) {
    console.error('Erreur lors du chargement du profil:', error)
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
        telephone: profile.value.telephone
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
}

.btn-primary {
  background-color: #4299e1;
  color: white;
  padding: 0.75rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
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

.alert-error {
  background-color: #fed7d7;
  color: #742a2a;
  border: 1px solid #fc8181;
}
</style>
