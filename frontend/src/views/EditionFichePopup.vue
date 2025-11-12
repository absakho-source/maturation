<template>
  <div class="edition-fiche-popup">
    <div class="popup-header">
      <h2>✏️ Éditer la fiche d'évaluation</h2>
      <p class="projet-info" v-if="projet">
        <strong>{{ projet.numero_projet }}</strong> - {{ projet.titre }}
      </p>
    </div>

    <div class="popup-content" v-if="ficheEdition">
      <div class="criteres-list">
        <div v-for="critere in criteresConfig" :key="critere.key" class="critere-edit-item">
          <h4>{{ critere.label }} ({{ critere.max }} pts)</h4>
          <div class="critere-inputs">
            <label>Score:
              <input type="number" :min="0" :max="critere.max"
                v-model.number="ficheEdition.criteres[critere.key].score" class="input-score"/>
              / {{ critere.max }}
            </label>
            <label>Commentaire:
              <textarea v-model="ficheEdition.criteres[critere.key].commentaire"
                class="textarea-commentaire" rows="2"></textarea>
            </label>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label>Avis global:</label>
        <select v-model="ficheEdition.avis" class="form-control">
          <option value="favorable">Favorable</option>
          <option value="favorable sous réserve">Favorable sous réserve</option>
          <option value="défavorable">Défavorable</option>
        </select>
      </div>

      <div class="form-group">
        <label>Commentaires généraux:</label>
        <textarea v-model="ficheEdition.commentaires" class="form-control" rows="4"></textarea>
      </div>

      <div class="total-score-display">
        Score total: <strong>{{ calculerScoreTotal() }} / 100</strong>
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
        { key: 'alignement', label: 'ALIGNEMENT À LA DOCTRINE DE TRANSFORMATION SYSTÉMIQUE', max: 10 },
        { key: 'activites_couts', label: 'PERTINENCE DES ACTIVITÉS ET BIEN FONDÉ DES COÛTS/PART DE FONCTIONNEMENT', max: 15 },
        { key: 'equite', label: 'ÉQUITÉ (SOCIALE-TERRITORIALE-GENRE)', max: 15 },
        { key: 'viabilite', label: 'VIABILITÉ/RENTABILITÉ FINANCIÈRE', max: 5 },
        { key: 'rentabilite', label: 'RENTABILITÉ SOCIO-ÉCONOMIQUE (ACA/MPR)', max: 5 },
        { key: 'benefices_strategiques', label: 'BÉNÉFICES STRATÉGIQUES', max: 10 },
        { key: 'perennite', label: 'PÉRENNITÉ ET DURABILITÉ DES EFFETS ET IMPACTS DU PROJET', max: 5 },
        { key: 'avantages_intangibles', label: 'AVANTAGES ET COÛTS INTANGIBLES', max: 10 },
        { key: 'faisabilite', label: 'FAISABILITÉ DU PROJET / RISQUES POTENTIELS', max: 5 },
        { key: 'ppp', label: 'POTENTIALITÉ OU OPPORTUNITÉ DU PROJET À ÊTRE RÉALISÉ EN PPP', max: 5 },
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
    },
    calculerScoreTotal() {
      return this.criteresConfig.reduce((sum, c) => {
        return sum + (this.ficheEdition.criteres[c.key]?.score || 0);
      }, 0);
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

.criteres-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin: 1.5rem 0;
}

.critere-edit-item {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.critere-edit-item h4 {
  font-size: 0.95rem;
  color: #374151;
  margin-bottom: 1rem;
  font-weight: 600;
}

.critere-inputs {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.critere-inputs label {
  display: flex;
  flex-direction: column;
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.input-score {
  width: 100px;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
  margin-top: 0.25rem;
}

.textarea-commentaire {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  resize: vertical;
  margin-top: 0.25rem;
  font-family: inherit;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
}

.total-score-display {
  padding: 1rem;
  background: #eff6ff;
  border-left: 4px solid #3b82f6;
  border-radius: 4px;
  font-size: 1.1rem;
  text-align: center;
  margin-top: 1.5rem;
}

.total-score-display strong {
  color: #1e40af;
  font-size: 1.3rem;
}

.actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
  margin-top: 1.5rem;
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
