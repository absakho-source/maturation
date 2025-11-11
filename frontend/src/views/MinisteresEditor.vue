<template>
  <div>
    <Header />
    <div class="ministeres-editor">
    <!-- Header avec boutons d'action -->
    <div class="editor-header">
      <div class="header-left">
        <button @click="retour" class="btn-retour">← Retour</button>
        <h1>Gestion des Ministères</h1>
      </div>
      <div class="header-actions" v-if="hasChanges">
        <button @click="annulerModifications" class="btn-cancel">Annuler</button>
        <button @click="enregistrerTout" class="btn-save">Enregistrer tout</button>
      </div>
    </div>

    <!-- Message de chargement -->
    <div v-if="loading" class="loading">Chargement...</div>

    <!-- Message d'erreur -->
    <div v-if="error" class="error-message">{{ error }}</div>

    <!-- Liste des ministères -->
    <div v-if="!loading && !error" class="ministeres-list">
      <div class="list-header">
        <h2>Liste des ministères ({{ ministeres.length }})</h2>
        <button @click="ouvrirFormulaireAjout" class="btn-add">+ Ajouter un ministère</button>
      </div>

      <div class="ministeres-container">
        <div
          v-for="(ministere, index) in ministeres"
          :key="ministere.id"
          class="ministere-card"
          :class="{ 'inactive': !ministere.actif, 'modified': pendingChanges.has(ministere.id) }"
        >
          <div class="card-header">
            <div class="ordre-controls">
              <button
                @click="deplacerHaut(index)"
                :disabled="index === 0"
                class="btn-ordre"
                title="Monter"
              >↑</button>
              <span class="ordre-numero">{{ ministere.ordre }}</span>
              <button
                @click="deplacerBas(index)"
                :disabled="index === ministeres.length - 1"
                class="btn-ordre"
                title="Descendre"
              >↓</button>
            </div>
            <div class="actif-toggle">
              <label>
                <input
                  type="checkbox"
                  v-model="ministere.actif"
                  @change="marquerModifie(ministere.id)"
                />
                Actif
              </label>
            </div>
          </div>

          <div class="card-body">
            <div class="form-group">
              <label>Nom complet du ministère:</label>
              <input
                type="text"
                v-model="ministere.nom_complet"
                @input="marquerModifie(ministere.id)"
                placeholder="Ex: Ministère de l'Éducation nationale"
              />
            </div>

          </div>

          <div class="card-footer">
            <button
              @click="sauvegarderMinistere(ministere)"
              class="btn-save-item"
              v-if="pendingChanges.has(ministere.id)"
            >
              Enregistrer
            </button>
            <button
              @click="supprimerMinistere(ministere)"
              class="btn-delete"
            >
              Supprimer
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Formulaire d'ajout de ministère -->
    <div v-if="showAjoutForm" class="modal-overlay" @click.self="fermerFormulaireAjout">
      <div class="modal-content">
        <h2>Ajouter un ministère</h2>
        <div class="form-group">
          <label>Nom complet du ministère: *</label>
          <input
            type="text"
            v-model="nouveauMinistere.nom_complet"
            placeholder="Ex: Ministère de l'Éducation nationale"
          />
        </div>
        <div class="form-group">
          <label>
            <input type="checkbox" v-model="nouveauMinistere.actif" />
            Actif
          </label>
        </div>
        <div class="modal-actions">
          <button @click="fermerFormulaireAjout" class="btn-cancel">Annuler</button>
          <button @click="ajouterMinistere" class="btn-save">Ajouter</button>
        </div>
      </div>
    </div>

    <!-- Actions du bas -->
    <div class="footer-actions" v-if="hasChanges">
      <button @click="annulerModifications" class="btn-cancel">Annuler les modifications</button>
      <button @click="enregistrerTout" class="btn-save">Enregistrer tout</button>
    </div>
    </div>
  </div>
</template>

<script>
import Header from '../components/Header.vue';

export default {
  name: 'MinisteresEditor',
  components: {
    Header
  },
  data() {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    return {
      username: user.username || localStorage.getItem('username'),
      role: user.role || localStorage.getItem('role'),
      ministeres: [],
      ministeresOriginal: [],
      loading: true,
      error: null,
      pendingChanges: new Set(),
      showAjoutForm: false,
      nouveauMinistere: {
        nom_complet: '',
        abreviation: '',
        actif: true
      }
    }
  },
  computed: {
    hasChanges() {
      return this.pendingChanges.size > 0
    }
  },
  mounted() {
    // Vérifier les permissions
    if (!['admin', 'secretariatsct'].includes(this.role)) {
      alert('Accès non autorisé')
      this.$router.push('/')
      return
    }
    this.chargerMinisteres()
  },
  methods: {
    async chargerMinisteres() {
      try {
        this.loading = true
        this.error = null

        const response = await fetch('/api/ministeres/all?role=' + this.role)
        if (!response.ok) {
          throw new Error('Erreur lors du chargement des ministères')
        }

        this.ministeres = await response.json()
        this.ministeresOriginal = JSON.parse(JSON.stringify(this.ministeres))
        this.pendingChanges.clear()

        console.log('[MINISTERES EDITOR] Ministères chargés:', this.ministeres.length)
      } catch (err) {
        console.error('[MINISTERES EDITOR] Erreur:', err)
        this.error = err.message
      } finally {
        this.loading = false
      }
    },

    marquerModifie(ministereId) {
      this.pendingChanges.add(ministereId)
    },

    async sauvegarderMinistere(ministere) {
      try {
        const response = await fetch(`/api/ministeres/${ministere.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ...ministere,
            role: this.role
          })
        })

        if (!response.ok) {
          throw new Error('Erreur lors de la sauvegarde')
        }

        this.pendingChanges.delete(ministere.id)
        console.log('[MINISTERES EDITOR] Ministère sauvegardé:', ministere.nom_complet)
      } catch (err) {
        console.error('[MINISTERES EDITOR] Erreur sauvegarde:', err)
        alert('Erreur lors de la sauvegarde: ' + err.message)
      }
    },

    async enregistrerTout() {
      const promises = []
      for (const ministereId of this.pendingChanges) {
        const ministere = this.ministeres.find(m => m.id === ministereId)
        if (ministere) {
          promises.push(this.sauvegarderMinistere(ministere))
        }
      }
      await Promise.all(promises)
      await this.chargerMinisteres()
    },

    annulerModifications() {
      if (confirm('Annuler toutes les modifications non sauvegardées ?')) {
        this.chargerMinisteres()
      }
    },

    deplacerHaut(index) {
      if (index === 0) return

      // Échanger les ordres
      const temp = this.ministeres[index].ordre
      this.ministeres[index].ordre = this.ministeres[index - 1].ordre
      this.ministeres[index - 1].ordre = temp

      // Marquer comme modifiés
      this.marquerModifie(this.ministeres[index].id)
      this.marquerModifie(this.ministeres[index - 1].id)

      // Réorganiser le tableau
      this.ministeres.sort((a, b) => a.ordre - b.ordre)
    },

    deplacerBas(index) {
      if (index === this.ministeres.length - 1) return

      // Échanger les ordres
      const temp = this.ministeres[index].ordre
      this.ministeres[index].ordre = this.ministeres[index + 1].ordre
      this.ministeres[index + 1].ordre = temp

      // Marquer comme modifiés
      this.marquerModifie(this.ministeres[index].id)
      this.marquerModifie(this.ministeres[index + 1].id)

      // Réorganiser le tableau
      this.ministeres.sort((a, b) => a.ordre - b.ordre)
    },

    ouvrirFormulaireAjout() {
      this.showAjoutForm = true
      this.nouveauMinistere = {
        nom_complet: '',
        abreviation: '',
        actif: true
      }
    },

    fermerFormulaireAjout() {
      this.showAjoutForm = false
    },

    async ajouterMinistere() {
      if (!this.nouveauMinistere.nom_complet.trim()) {
        alert('Le nom complet est requis')
        return
      }

      try {
        const response = await fetch('/api/ministeres', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ...this.nouveauMinistere,
            role: this.role
          })
        })

        if (!response.ok) {
          throw new Error('Erreur lors de l\'ajout')
        }

        console.log('[MINISTERES EDITOR] Ministère ajouté')
        this.fermerFormulaireAjout()
        await this.chargerMinisteres()
      } catch (err) {
        console.error('[MINISTERES EDITOR] Erreur ajout:', err)
        alert('Erreur lors de l\'ajout: ' + err.message)
      }
    },

    async supprimerMinistere(ministere) {
      if (!confirm(`Supprimer le ministère "${ministere.nom_complet}" ?`)) {
        return
      }

      try {
        const response = await fetch(`/api/ministeres/${ministere.id}`, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ role: this.role })
        })

        if (!response.ok) {
          throw new Error('Erreur lors de la suppression')
        }

        console.log('[MINISTERES EDITOR] Ministère supprimé')
        await this.chargerMinisteres()
      } catch (err) {
        console.error('[MINISTERES EDITOR] Erreur suppression:', err)
        alert('Erreur lors de la suppression: ' + err.message)
      }
    },

    retour() {
      if (this.hasChanges) {
        if (!confirm('Vous avez des modifications non sauvegardées. Quitter quand même ?')) {
          return
        }
      }

      if (this.role === 'admin') {
        this.$router.push('/admin')
      } else if (this.role === 'secretariatsct') {
        this.$router.push('/secretariatsct')
      } else {
        this.$router.push('/')
      }
    }
  }
}
</script>

<style scoped>
.ministeres-editor {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--dgppe-primary);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-left h1 {
  margin: 0;
  color: var(--dgppe-primary);
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.btn-retour {
  padding: 0.5rem 1rem;
  background: var(--dgppe-gray-500);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-retour:hover {
  background: var(--dgppe-gray-700);
}

.btn-save, .btn-save-item {
  padding: 0.5rem 1.5rem;
  background: var(--dgppe-success);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.btn-save:hover, .btn-save-item:hover {
  background: #27ae60;
}

.btn-cancel {
  padding: 0.5rem 1.5rem;
  background: var(--dgppe-danger);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-cancel:hover {
  background: #c0392b;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--dgppe-primary);
  font-size: 1.2rem;
}

.error-message {
  background: #fee;
  color: #c00;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.list-header h2 {
  color: var(--dgppe-primary);
  margin: 0;
}

.btn-add {
  padding: 0.75rem 1.5rem;
  background: var(--dgppe-primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.btn-add:hover {
  background: var(--dgppe-primary-dark);
}

.ministeres-container {
  display: grid;
  gap: 1rem;
}

.ministere-card {
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.75rem;
  transition: all 0.3s;
}

.ministere-card.modified {
  border-color: var(--dgppe-accent);
  background: #fff8f0;
}

.ministere-card.inactive {
  opacity: 0.6;
  background: #f5f5f5;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid #eee;
}

.ordre-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-ordre {
  background: var(--dgppe-primary);
  color: white;
  border: none;
  border-radius: 4px;
  width: 30px;
  height: 30px;
  cursor: pointer;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-ordre:hover:not(:disabled) {
  background: var(--dgppe-primary-dark);
}

.btn-ordre:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.ordre-numero {
  font-weight: bold;
  color: var(--dgppe-primary);
  min-width: 30px;
  text-align: center;
}

.actif-toggle label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.card-body {
  margin-bottom: 0.5rem;
}

.form-group {
  margin-bottom: 0.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--dgppe-primary);
}

.form-group input[type="text"] {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.form-group input[type="text"]:focus {
  outline: none;
  border-color: var(--dgppe-primary);
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #eee;
}

.btn-delete {
  padding: 0.5rem 1rem;
  background: var(--dgppe-danger);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-delete:hover {
  background: #c0392b;
}

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
  padding: 2rem;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
}

.modal-content h2 {
  margin-top: 0;
  color: var(--dgppe-primary);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.footer-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 1rem 2rem;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  z-index: 100;
}
</style>
