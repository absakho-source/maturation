<template>
  <div class="edition-fiche-popup">
    <div class="popup-header">
      <h2>✏️ Éditer la fiche d'évaluation</h2>
      <p class="projet-info" v-if="projet">
        <strong>{{ projet.numero_projet }}</strong> - {{ projet.titre }}
      </p>
    </div>

    <div class="popup-content" v-if="ficheEdition">
      <div class="criteres-section">
        <h3>Critères d'évaluation</h3>
        <div v-for="critere in criteresConfig" :key="critere.key" class="critere-item">
          <div class="critere-header">
            <label>{{ critere.label }}</label>
            <span class="score-display">{{ ficheEdition.criteres[critere.key]?.score || 0 }}/{{ critere.max }}</span>
          </div>
          <input
            type="range"
            :min="0"
            :max="critere.max"
            v-model.number="ficheEdition.criteres[critere.key].score"
            class="score-slider"
          />
          <textarea
            v-model="ficheEdition.criteres[critere.key].commentaire"
            :placeholder="`Commentaire pour ${critere.label}`"
            rows="2"
            class="commentaire-input"
          ></textarea>
        </div>
      </div>

      <div class="avis-section">
        <h3>Avis global</h3>
        <select v-model="ficheEdition.avis" class="avis-select">
          <option value="">-- Sélectionner un avis --</option>
          <option value="favorable">Favorable</option>
          <option value="favorable sous réserve">Favorable sous réserve</option>
          <option value="défavorable">Défavorable</option>
        </select>
      </div>

      <div class="commentaires-section">
        <h3>Commentaires généraux</h3>
        <textarea
          v-model="ficheEdition.commentaires"
          placeholder="Commentaires généraux sur le projet"
          rows="5"
          class="commentaires-textarea"
        ></textarea>
      </div>

      <div class="actions">
        <button @click="enregistrer" class="btn-primary" :disabled="enregistrementEnCours">
          {{ enregistrementEnCours ? 'Enregistrement...' : 'Enregistrer' }}
        </button>
        <button @click="fermer" class="btn-secondary" :disabled="enregistrementEnCours">
          Annuler
        </button>
      </div>
    </div>

    <div v-else class="loading">
      Chargement de la fiche...
    </div>
  </div>
</template>

<script>
export default {
  name: 'EditionFichePopup',
  data() {
    return {
      projet: null,
      ficheEdition: null,
      enregistrementEnCours: false,
      criteresConfig: [
        { key: 'pertinence', label: 'PERTINENCE', max: 5 },
        { key: 'faisabilite_technique', label: 'FAISABILITÉ TECHNIQUE', max: 5 },
        { key: 'faisabilite_financiere', label: 'FAISABILITÉ FINANCIÈRE', max: 5 },
        { key: 'impact_economique', label: 'RETOMBÉES ÉCONOMIQUES', max: 5 },
        { key: 'innovation', label: 'INNOVATION', max: 5 },
        { key: 'equipe', label: 'ÉQUIPE', max: 5 },
        { key: 'partenariat', label: 'PARTENARIAT', max: 5 },
        { key: 'coherence_budget', label: 'COHÉRENCE DU BUDGET', max: 5 },
        { key: 'maturite_technologique', label: 'MATURITÉ TECHNOLOGIQUE', max: 5 },
        { key: 'impact_social', label: 'IMPACTS SOCIAUX', max: 5 },
        { key: 'strategie_commercialisation', label: 'STRATÉGIE DE COMMERCIALISATION', max: 5 },
        { key: 'impact_environnemental', label: 'IMPACTS ENVIRONNEMENTAUX', max: 5 }
      ]
    };
  },
  async mounted() {
    // Récupérer les données depuis les paramètres de l'URL
    const urlParams = new URLSearchParams(window.location.search);
    const projetId = urlParams.get('projetId');

    if (!projetId) {
      alert('Aucun projet spécifié');
      window.close();
      return;
    }

    await this.chargerDonnees(projetId);
  },
  methods: {
    async chargerDonnees(projetId) {
      try {
        // Charger les infos du projet
        const projetRes = await fetch(`/api/projects/${projetId}`);
        if (!projetRes.ok) throw new Error('Erreur lors du chargement du projet');
        this.projet = await projetRes.json();

        // Charger la fiche d'évaluation
        const ficheRes = await fetch(`/api/projects/${projetId}/fiche-evaluation`);
        if (!ficheRes.ok) throw new Error('Erreur lors du chargement de la fiche');
        const fiche = await ficheRes.json();

        // Initialiser ficheEdition
        this.ficheEdition = {
          criteres: {},
          avis: fiche.avis || '',
          commentaires: fiche.commentaires || ''
        };

        // Initialiser tous les critères
        this.criteresConfig.forEach(c => {
          this.ficheEdition.criteres[c.key] = {
            score: fiche.criteres?.[c.key]?.score || 0,
            commentaire: fiche.criteres?.[c.key]?.commentaire || ''
          };
        });
      } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors du chargement des données');
        window.close();
      }
    },
    async enregistrer() {
      if (!this.projet) return;

      this.enregistrementEnCours = true;
      try {
        const response = await fetch(`/api/projects/${this.projet.id}/fiche-evaluation`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.ficheEdition)
        });

        if (!response.ok) {
          throw new Error('Erreur lors de l\'enregistrement');
        }

        // Notifier la fenêtre parent
        if (window.opener) {
          window.opener.postMessage({
            type: 'ficheUpdated',
            projetId: this.projet.id
          }, '*');
        }

        alert('Fiche enregistrée avec succès');
        window.close();
      } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de l\'enregistrement de la fiche');
      } finally {
        this.enregistrementEnCours = false;
      }
    },
    fermer() {
      window.close();
    }
  }
};
</script>

<style scoped>
.edition-fiche-popup {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.popup-header {
  border-bottom: 2px solid #2c5282;
  padding-bottom: 15px;
  margin-bottom: 20px;
}

.popup-header h2 {
  margin: 0 0 10px 0;
  color: #2c5282;
  font-size: 24px;
}

.projet-info {
  margin: 5px 0;
  color: #555;
  font-size: 14px;
}

.popup-content {
  background: white;
}

.criteres-section,
.avis-section,
.commentaires-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.criteres-section h3,
.avis-section h3,
.commentaires-section h3 {
  margin: 0 0 15px 0;
  color: #2c5282;
  font-size: 18px;
}

.critere-item {
  margin-bottom: 20px;
  padding: 15px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.critere-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.critere-header label {
  font-weight: 600;
  color: #2d3748;
  font-size: 14px;
}

.score-display {
  font-size: 16px;
  font-weight: bold;
  color: #2c5282;
  min-width: 50px;
  text-align: right;
}

.score-slider {
  width: 100%;
  margin-bottom: 10px;
}

.commentaire-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  font-size: 13px;
  resize: vertical;
}

.avis-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  font-size: 14px;
}

.commentaires-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
}

.actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #2c5282;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1a365d;
}

.btn-primary:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #e2e8f0;
  color: #2d3748;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #cbd5e0;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #718096;
  font-size: 16px;
}
</style>
