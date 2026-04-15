<template>
  <div class="matrice-evaluation-prealable">
    <h3>📋 Évaluation de la Recevabilité</h3>
    <p class="description">
      Choisissez une décision. Pour « Compléments requis » ou « Rejeter »,
      la motivation est obligatoire.
    </p>

    <!-- Motivation -->
    <div class="commentaires-section">
      <label for="commentaires-globaux">
        <strong>💬 Motivation</strong>
        <span class="label-hint">
          (Obligatoire pour compléments requis ou rejet)
        </span>
      </label>
      <textarea
        id="commentaires-globaux"
        v-model="commentairesGlobaux"
        rows="4"
        placeholder="Ex: Documents manquants, justification du rejet, précisions attendues..."
        class="commentaires-textarea"
      ></textarea>
    </div>

    <!-- Boutons d'action -->
    <div class="actions-section">
      <button
        @click="soumettre('dossier_evaluable')"
        class="btn-action btn-success"
        :disabled="enCours"
        title="Valider le dossier comme recevable"
      >
        ✓ Recevable
      </button>
      <button
        @click="soumettre('complements_requis')"
        class="btn-action btn-warning"
        :disabled="enCours || !commentairesGlobaux.trim()"
        title="Demander des compléments (motivation requise)"
      >
        📝 Compléments requis
      </button>
      <button
        @click="soumettre('dossier_rejete')"
        class="btn-action btn-danger"
        :disabled="enCours || !commentairesGlobaux.trim()"
        title="Rejeter le dossier (motivation requise)"
      >
        ✕ Rejeter
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MatriceEvaluationPrealable',
  props: {
    projectId: {
      type: [Number, String],
      required: true
    },
    matriceInitiale: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      commentairesGlobaux: '',
      enCours: false
    }
  },
  mounted() {
    if (this.matriceInitiale && this.matriceInitiale.commentaires_globaux) {
      this.commentairesGlobaux = this.matriceInitiale.commentaires_globaux
    }
  },
  methods: {
    async soumettre(decision) {
      if ((decision === 'complements_requis' || decision === 'dossier_rejete') && !this.commentairesGlobaux.trim()) {
        alert('La motivation est obligatoire pour cette décision')
        return
      }

      this.enCours = true

      try {
        const user = JSON.parse(localStorage.getItem('user') || '{}')

        const matrice = {
          commentaires_globaux: this.commentairesGlobaux,
          date_evaluation: new Date().toISOString(),
          evaluateur: user.username
        }

        const response = await fetch(`/api/projects/${this.projectId}/evaluation-prealable`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            decision,
            commentaires: this.commentairesGlobaux,
            matrice: JSON.stringify(matrice),
            evaluateur: user.username,
            role: user.role
          })
        })

        if (!response.ok) {
          throw new Error('Erreur lors de la soumission')
        }

        alert('Évaluation de la recevabilité soumise avec succès')
        this.$emit('evaluation-soumise', { decision, matrice })
      } catch (error) {
        console.error('Erreur:', error)
        alert('Erreur lors de la soumission de l\'évaluation de la recevabilité')
      } finally {
        this.enCours = false
      }
    }
  }
}
</script>

<style scoped>
.matrice-evaluation-prealable {
  background: #f8fafc;
  border: 2px solid #0ea5e9;
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1rem 0;
  width: 100%;
  box-sizing: border-box;
}

.matrice-evaluation-prealable h3 {
  color: #0369a1;
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-size: 1.25rem;
}

.description {
  color: #64748b;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.commentaires-section {
  margin: 1rem 0 1.5rem 0;
}

.commentaires-section label {
  display: block;
  margin-bottom: 0.5rem;
  color: #1e293b;
  font-size: 0.95rem;
}

.label-hint {
  display: block;
  font-weight: 400;
  font-size: 0.85rem;
  color: #64748b;
  margin-top: 0.25rem;
}

.commentaires-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.9rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.commentaires-textarea:focus {
  outline: none;
  border-color: #0ea5e9;
}

.actions-section {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.btn-action {
  flex: 1;
  min-width: 180px;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-success { background: #10b981; color: white; }
.btn-success:hover:not(:disabled) { background: #059669; }

.btn-warning { background: #f59e0b; color: white; }
.btn-warning:hover:not(:disabled) { background: #d97706; }

.btn-danger { background: #ef4444; color: white; }
.btn-danger:hover:not(:disabled) { background: #dc2626; }
</style>
