<template>
  <PageWrapper>
    <div class="formulaire-editor">
      <div class="header">
        <div class="header-top">
          <button @click="retour" class="btn btn-outline btn-sm">← Retour</button>
          <div class="header-actions">
            <button @click="previsualiserPDF" class="btn btn-info">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                <polyline points="14,2 14,8 20,8"/>
                <path d="M12 18v-6"/>
                <path d="M9 15l3 3 3-3"/>
              </svg>
              Prévisualiser PDF
            </button>
            <template v-if="hasChanges">
              <button @click="annulerModifications" class="btn btn-secondary">Annuler</button>
              <button @click="enregistrerTout" class="btn btn-primary">Enregistrer les modifications</button>
            </template>
          </div>
        </div>
        <h1>Éditeur de Formulaire d'Évaluation</h1>
        <p class="subtitle">Gérer les critères et paramètres du formulaire</p>
      </div>

      <div v-if="loading" class="loading">Chargement...</div>

      <div v-else-if="config" class="editor-content">
        <!-- Informations de la configuration -->
        <div class="config-info">
          <h2>{{ config.nom }} (v{{ config.version }})</h2>
          <p>{{ config.description }}</p>
          <span class="badge active">Configuration active</span>
        </div>

        <!-- Paramètres généraux -->
        <div class="section-card">
          <h3>Paramètres Généraux</h3>
          <div class="param-grid">
            <div class="param-item full-width">
              <label>
                Version en cours d'affichage:
                <span class="help-text">Cette version apparaît sur tous les formulaires d'évaluation générés</span>
              </label>
              <div class="version-display">
                <span class="current-version">{{ config.version_affichage || 'v1.0 - Décembre 2025' }}</span>
                <button type="button" @click="modifierVersion" class="btn-edit-version">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                  </svg>
                  Modifier
                </button>
              </div>
            </div>
            <div class="param-item">
              <label>Score Total Maximum:</label>
              <input type="number" v-model.number="config.score_total_max" @input="marquerConfigModifiee" class="param-input">
            </div>
            <div class="param-item">
              <label>Seuil Minimum (points):</label>
              <input type="number" v-model.number="config.seuil_minimum" @input="marquerConfigModifiee" class="param-input">
              <small class="param-help">
                Score ≥ ce seuil: l'évaluateur choisit entre Favorable ou Favorable sous conditions<br>
                Score < ce seuil: automatiquement Défavorable
              </small>
            </div>
          </div>
        </div>

        <!-- Section III - Critères d'évaluation -->
        <div class="section-card">
          <div class="section-header">
            <h3>III - Critères d'Évaluation</h3>
            <button @click="ajouterCritere" class="btn btn-success">+ Ajouter un critère</button>
          </div>

          <div class="criteres-list">
            <div v-for="(critere, index) in criteresEvaluation" :key="critere.id" class="critere-item">
              <div class="critere-ordre">{{ index + 1 }}</div>
              <div class="critere-content">
                <input
                  v-model="critere.nom"
                  @input="marquerCritereModifie(critere.id)"
                  class="critere-nom-input"
                  placeholder="Nom du critère">
                <div class="critere-details">
                  <label>
                    Score max:
                    <input
                      type="number"
                      v-model.number="critere.score_max"
                      @input="marquerCritereModifie(critere.id)"
                      class="score-input"
                      min="1"
                      max="50">
                  </label>
                  <label class="checkbox-label">
                    <input
                      type="checkbox"
                      v-model="critere.avec_description"
                      @change="marquerCritereModifie(critere.id)">
                    Description requise
                  </label>
                  <label class="checkbox-label">
                    <input
                      type="checkbox"
                      v-model="critere.avec_recommandations"
                      @change="marquerCritereModifie(critere.id)">
                    Recommandations
                  </label>
                </div>
              </div>
              <div class="critere-actions">
                <button @click="monterCritere(index)" :disabled="index === 0" class="btn-icon" title="Monter">↑</button>
                <button @click="descendreCritere(index)" :disabled="index === criteresEvaluation.length - 1" class="btn-icon" title="Descendre">↓</button>
                <button @click="supprimerCritere(critere)" class="btn-icon btn-danger" title="Supprimer">×</button>
              </div>
            </div>
          </div>

          <div class="total-score" :class="{
            'score-valid': calculerScoreTotal() <= config.score_total_max,
            'score-invalid': calculerScoreTotal() > config.score_total_max
          }">
            Score total calculé: <strong>{{ calculerScoreTotal() }}/{{ config.score_total_max }}</strong>
            <span v-if="calculerScoreTotal() > config.score_total_max" class="error-message">
              ⚠️ La somme des scores dépasse le maximum autorisé !
            </span>
            <span v-else-if="calculerScoreTotal() < config.score_total_max" class="warning-message">
              ℹ️ La somme des scores est inférieure au maximum ({{ config.score_total_max - calculerScoreTotal() }} points restants)
            </span>
            <span v-else class="success-message">
              ✓ Somme des scores correcte
            </span>
          </div>
        </div>

        <div class="actions">
          <button @click="retour" class="btn btn-outline">← Retour</button>
        </div>
      </div>

      <div v-else class="error">
        Aucune configuration active trouvée.
      </div>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue'

export default {
  name: 'FormulaireEditor',
  components: {
    PageWrapper
  },
  data() {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    return {
      config: null,
      configOriginal: null,
      loading: true,
      username: user.username || localStorage.getItem('username'),
      role: user.role || localStorage.getItem('role'),
      pendingChanges: {
        config: false,
        criteres: new Set()
      }
    }
  },
  computed: {
    criteresEvaluation() {
      if (!this.config || !this.config.sections) return []

      // Trouver la section III (évaluation)
      const sectionEval = this.config.sections.find(s => s.type_section === 'evaluation')
      return sectionEval ? sectionEval.criteres : []
    },
    sectionEvaluationId() {
      if (!this.config || !this.config.sections) return null
      const sectionEval = this.config.sections.find(s => s.type_section === 'evaluation')
      return sectionEval ? sectionEval.id : null
    },
    hasChanges() {
      return this.pendingChanges.config || this.pendingChanges.criteres.size > 0
    }
  },
  async mounted() {
    // Vérifier les permissions
    if (this.role !== 'admin' && this.role !== 'secretariatsct') {
      alert('Accès non autorisé')
      this.$router.push('/')
      return
    }

    await this.chargerConfiguration()
  },
  methods: {
    async chargerConfiguration() {
      try {
        this.loading = true
        const response = await fetch('/api/formulaire-config/active')

        if (!response.ok) {
          throw new Error('Configuration non trouvée')
        }

        this.config = await response.json()
        // Sauvegarder l'original pour détecter les changements
        this.configOriginal = JSON.parse(JSON.stringify(this.config))
        // Réinitialiser les modifications en attente
        this.pendingChanges = {
          config: false,
          criteres: new Set()
        }
      } catch (error) {
        console.error('Erreur chargement configuration:', error)
        alert('Erreur lors du chargement de la configuration')
      } finally {
        this.loading = false
      }
    },

    marquerConfigModifiee() {
      this.pendingChanges.config = true
    },

    marquerCritereModifie(critereId) {
      this.pendingChanges.criteres.add(critereId)
    },

    async enregistrerTout() {
      // Validation: vérifier que la somme des scores ne dépasse pas le maximum
      const scoreTotal = this.calculerScoreTotal()
      if (scoreTotal > this.config.score_total_max) {
        alert(`❌ Erreur: La somme des scores (${scoreTotal}) dépasse le score total maximum autorisé (${this.config.score_total_max}). Veuillez ajuster les scores des critères avant d'enregistrer.`)
        return
      }

      try {
        // Sauvegarder la config si modifiée
        if (this.pendingChanges.config) {
          await this.sauvegarderConfig()
        }

        // Sauvegarder tous les critères modifiés
        for (const critereId of this.pendingChanges.criteres) {
          const critere = this.criteresEvaluation.find(c => c.id === critereId)
          if (critere) {
            await this.sauvegarderCritere(critere)
          }
        }

        // Recharger et réinitialiser
        await this.chargerConfiguration()
        alert('✅ Toutes les modifications ont été enregistrées avec succès')
      } catch (error) {
        console.error('Erreur sauvegarde globale:', error)
        alert('Erreur lors de la sauvegarde')
      }
    },

    annulerModifications() {
      if (confirm('Annuler toutes les modifications ?')) {
        this.chargerConfiguration()
      }
    },

    async sauvegarderConfig() {
      try {
        const response = await fetch(`/api/formulaire-config/${this.config.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.username,
            role: this.role,
            version_affichage: this.config.version_affichage,
            score_total_max: this.config.score_total_max,
            seuil_minimum: this.config.seuil_minimum || 70
          })
        })

        if (!response.ok) throw new Error('Erreur sauvegarde')

        const updated = await response.json()
        console.log('Configuration sauvegardée')
      } catch (error) {
        console.error('Erreur sauvegarde config:', error)
        throw error
      }
    },

    async sauvegarderCritere(critere) {
      try {
        const response = await fetch(`/api/critere/${critere.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.username,
            role: this.role,
            nom: critere.nom,
            score_max: critere.score_max,
            ordre: critere.ordre,
            avec_description: critere.avec_description,
            avec_recommandations: critere.avec_recommandations
          })
        })

        if (!response.ok) throw new Error('Erreur sauvegarde critère')

        console.log('Critère sauvegardé:', critere.nom)
      } catch (error) {
        console.error('Erreur sauvegarde critère:', error)
        alert('Erreur lors de la sauvegarde du critère')
      }
    },

    async ajouterCritere() {
      const nom = prompt('Nom du nouveau critère:')
      if (!nom) return

      const scoreMax = parseInt(prompt('Score maximum:', '5'))
      if (isNaN(scoreMax) || scoreMax < 1) return

      try {
        const ordre = this.criteresEvaluation.length + 1
        const cle = nom.toLowerCase().replace(/[^a-z0-9]/g, '_')

        const response = await fetch(`/api/section/${this.sectionEvaluationId}/criteres`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.username,
            role: this.role,
            nom,
            cle,
            score_max: scoreMax,
            ordre,
            avec_description: true,
            avec_recommandations: false
          })
        })

        if (!response.ok) throw new Error('Erreur ajout critère')

        await this.chargerConfiguration()
        alert('Critère ajouté')
      } catch (error) {
        console.error('Erreur ajout critère:', error)
        alert('Erreur lors de l\'ajout du critère')
      }
    },

    async supprimerCritere(critere) {
      if (!confirm(`Supprimer le critère "${critere.nom}" ?`)) return

      try {
        const response = await fetch(`/api/critere/${critere.id}`, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.username,
            role: this.role
          })
        })

        if (!response.ok) throw new Error('Erreur suppression')

        await this.chargerConfiguration()
        alert('Critère supprimé')
      } catch (error) {
        console.error('Erreur suppression critère:', error)
        alert('Erreur lors de la suppression')
      }
    },

    async monterCritere(index) {
      if (index === 0) return

      const criteres = this.criteresEvaluation
      const critere = criteres[index]
      const critereAvant = criteres[index - 1]

      // Échanger les ordres
      const tempOrdre = critere.ordre
      critere.ordre = critereAvant.ordre
      critereAvant.ordre = tempOrdre

      await this.sauvegarderCritere(critere)
      await this.sauvegarderCritere(critereAvant)
      await this.chargerConfiguration()
    },

    async descendreCritere(index) {
      if (index === this.criteresEvaluation.length - 1) return

      const criteres = this.criteresEvaluation
      const critere = criteres[index]
      const critereApres = criteres[index + 1]

      // Échanger les ordres
      const tempOrdre = critere.ordre
      critere.ordre = critereApres.ordre
      critereApres.ordre = tempOrdre

      await this.sauvegarderCritere(critere)
      await this.sauvegarderCritere(critereApres)
      await this.chargerConfiguration()
    },

    calculerScoreTotal() {
      return this.criteresEvaluation.reduce((sum, c) => sum + c.score_max, 0)
    },

    modifierVersion() {
      const nouvelleVersion = prompt('Entrez la nouvelle version à afficher:', this.config.version_affichage || 'v1.0 - Décembre 2025')
      if (nouvelleVersion && nouvelleVersion.trim()) {
        this.config.version_affichage = nouvelleVersion.trim()
        this.marquerConfigModifiee()
      }
    },

    async previsualiserPDF() {
      try {
        // Créer une prévisualisation du formulaire avec les paramètres actuels
        const response = await fetch('/api/formulaire-config/preview-pdf', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.username,
            role: this.role,
            config_id: this.config.id
          })
        })

        if (!response.ok) {
          throw new Error('Erreur génération PDF')
        }

        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        window.open(url, '_blank')
      } catch (error) {
        console.error('Erreur prévisualisation PDF:', error)
        alert('Erreur lors de la génération du PDF de prévisualisation')
      }
    },

    retour() {
      this.$router.go(-1)
    }
  }
}
</script>

<style scoped>
.formulaire-editor {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  margin-bottom: 30px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.header h1 {
  color: #2c3e50;
  margin-bottom: 5px;
}

.subtitle {
  color: #7f8c8d;
  font-size: 14px;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #7f8c8d;
}

.config-info {
  background: #ecf0f1;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.config-info h2 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge.active {
  background: #27ae60;
  color: white;
}

.section-card {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.section-card h3 {
  margin: 0 0 20px 0;
  color: #2c3e50;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.param-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.param-item {
  display: flex;
  flex-direction: column;
}

.param-item.full-width {
  grid-column: 1 / -1;
}

.param-item label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #34495e;
}

.param-item label .help-text {
  font-weight: 400;
  font-size: 12px;
  color: #7f8c8d;
  font-style: italic;
  margin-left: 5px;
}

.param-help {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-top: 6px;
  line-height: 1.4;
  font-style: italic;
}

.param-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.version-display {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 15px;
  background: #f8f9fa;
  border: 2px solid #3498db;
  border-radius: 8px;
}

.current-version {
  flex: 1;
  font-size: 18px;
  font-weight: 700;
  color: #2c3e50;
  font-family: 'Courier New', monospace;
}

.btn-edit-version {
  padding: 8px 16px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-edit-version:hover {
  background: #2980b9;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.criteres-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.critere-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
}

.critere-ordre {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #3498db;
  color: white;
  border-radius: 50%;
  font-weight: 700;
  font-size: 16px;
  flex-shrink: 0;
}

.critere-content {
  flex: 1;
}

.critere-nom-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 10px;
}

.critere-details {
  display: flex;
  gap: 20px;
  align-items: center;
  font-size: 13px;
}

.critere-details label {
  display: flex;
  align-items: center;
  gap: 5px;
}

.score-input {
  width: 60px;
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  text-align: center;
}

.checkbox-label {
  cursor: pointer;
}

.critere-actions {
  display: flex;
  gap: 5px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover:not(:disabled) {
  background: #ecf0f1;
}

.btn-icon:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.btn-icon.btn-danger {
  color: #e74c3c;
  font-weight: 700;
  font-size: 24px;
}

.btn-icon.btn-danger:hover:not(:disabled) {
  background: #fee;
}

.total-score {
  margin-top: 20px;
  padding: 15px;
  background: #e8f4f8;
  border-left: 4px solid #3498db;
  font-size: 16px;
  transition: all 0.3s ease;
}

.total-score.score-invalid {
  background: #fee;
  border-left-color: #e74c3c;
}

.total-score.score-valid {
  background: #e8f8f0;
  border-left-color: #27ae60;
}

.total-score strong {
  color: #2c3e50;
  font-size: 20px;
}

.total-score .error-message {
  display: block;
  margin-top: 10px;
  color: #c0392b;
  font-weight: 600;
  font-size: 14px;
}

.total-score .warning-message {
  display: block;
  margin-top: 10px;
  color: #f39c12;
  font-weight: 500;
  font-size: 13px;
}

.total-score .success-message {
  display: block;
  margin-top: 10px;
  color: #27ae60;
  font-weight: 600;
  font-size: 14px;
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 13px;
}

.btn-primary {
  background: #27ae60;
  color: white;
}

.btn-primary:hover {
  background: #229954;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

.btn-info {
  background: #3498db;
  color: white;
}

.btn-info:hover {
  background: #2980b9;
}

.btn-success {
  background: #27ae60;
  color: white;
}

.btn-success:hover {
  background: #229954;
}

.btn-outline {
  background: white;
  border: 2px solid #3498db;
  color: #3498db;
}

.btn-outline:hover {
  background: #3498db;
  color: white;
}
</style>
