<template>
  <div class="fiche-evaluation-dgppe">
    <!-- En-tête officiel DGPPE -->
    <div class="header-section">
      <div class="official-header">
        <div class="header-text">
          <h1 class="republic-title">RÉPUBLIQUE DU SÉNÉGAL</h1>
          <h2 class="ministry-title">Ministère de l'Économie, du Plan et de la Coopération</h2>
          <h3 class="direction-title">Direction Générale de la Planification des Politiques Économiques</h3>
          <h4 class="platform-title">Plateforme de Maturation des Projets et Programmes Publics</h4>
        </div>
        <div class="header-logo">
          <img src="/logo-dgppe.png" alt="Logo DGPPE" class="logo-dgppe">
        </div>
      </div>
      <div class="document-title">
        <h1 class="main-title">FICHE D'ÉVALUATION DE PROJET</h1>
        <p class="reference-number">Référence: {{ fiche.reference_fiche || 'En attente' }}</p>
        <p class="project-number" v-if="project && project.numero_projet">Numéro de projet: {{ project.numero_projet }}</p>
      </div>
    </div>

    <form @submit.prevent="soumettreEvaluation" class="evaluation-form">
      <!-- Section I - PRÉSENTATION DU PROJET -->
      <div class="section-header section-i">
        <h3>I - PRÉSENTATION DU PROJET</h3>
      </div>

      <div class="presentation-grid">
        <div class="form-row">
          <div class="form-group">
            <label>COÛT DU PROJET</label>
            <input v-model="fiche.cout_projet" type="text" placeholder="ex: 3,982 Milliards FCFA">
          </div>
          <div class="form-group">
            <label>ORIGINE DU PROJET</label>
            <div class="checkbox-group">
              <label><input type="radio" v-model="fiche.origine_projet" value="MATURATION"> MATURATION</label>
              <label><input type="radio" v-model="fiche.origine_projet" value="OFFRE SPONTANÉE"> OFFRE SPONTANÉE</label>
              <label><input type="radio" v-model="fiche.origine_projet" value="AUTRES"> AUTRES</label>
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>TYPOLOGIE DU PROJET</label>
            <div class="checkbox-group">
              <label><input type="radio" v-model="fiche.typologie_projet" value="PRODUCTIF"> PRODUCTIF</label>
              <label><input type="radio" v-model="fiche.typologie_projet" value="APPUI À LA PRODUCTION"> APPUI À LA PRODUCTION</label>
              <label><input type="radio" v-model="fiche.typologie_projet" value="SOCIAL"> SOCIAL</label>
              <label><input type="radio" v-model="fiche.typologie_projet" value="ENVIRONNEMENTAL"> ENVIRONNEMENTAL</label>
            </div>
          </div>
          <div class="form-group">
            <label>CHANGEMENT CLIMATIQUE</label>
            <div class="checkbox-group">
              <label><input type="radio" v-model="fiche.changement_climatique" value="ADAPTATION"> ADAPTATION</label>
              <label><input type="radio" v-model="fiche.changement_climatique" value="ATTÉNUATION"> ATTÉNUATION</label>
              <label><input type="radio" v-model="fiche.changement_climatique" value="GENRE"> GENRE</label>
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>SOUS SECTEUR</label>
            <input v-model="fiche.sous_secteur" type="text" placeholder="Développement social">
          </div>
          <div class="form-group">
            <label>ORGANISME DE TUTELLE OU AUTEUR DE L'OFFRE</label>
            <input v-model="fiche.organisme_tutelle" type="text" placeholder="Ministère de la Famille et des Solidarités">
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>SND 2025-2029</label>
            <input v-model="fiche.snd_2025_2029" type="text" placeholder="AXES">
          </div>
          <div class="form-group">
            <label>OBJECTIFS STRATÉGIQUES</label>
            <input v-model="fiche.objectifs_strategiques" type="text" placeholder="OSA">
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>DURÉE D'ANALYSE</label>
            <input v-model="fiche.duree_analyse" type="text" placeholder="25 ans">
          </div>
          <div class="form-group">
            <label>RÉALISATION</label>
            <input v-model="fiche.realisation" type="text" placeholder="02 ans">
          </div>
          <div class="form-group">
            <label>EXPLOITATION</label>
            <input v-model="fiche.exploitation" type="text" placeholder="20 ans">
          </div>
        </div>

        <div class="form-row">
          <div class="form-group full-width">
            <label>LOCALISATION</label>
            <input v-model="fiche.localisation" type="text" placeholder="Territoire national">
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>PARTIES PRENANTES</label>
            <textarea v-model="fiche.parties_prenantes" rows="4" placeholder="Ministères sectoriels, Partenaires au développement, etc."></textarea>
          </div>
          <div class="form-group">
            <label>AUTRES PROJETS/PROG. CONNEXES</label>
            <textarea v-model="fiche.autres_projets_connexes" rows="4" placeholder="Projets liés ou complémentaires"></textarea>
          </div>
        </div>

        <div class="form-group full-width">
          <label>OBJECTIF DU PROJET</label>
          <textarea v-model="fiche.objectif_projet" rows="3" placeholder="Description de l'objectif principal"></textarea>
        </div>

        <div class="form-group full-width">
          <label>ACTIVITÉS PRINCIPALES</label>
          <textarea v-model="fiche.activites_principales" rows="4" placeholder="Liste des principales activités"></textarea>
        </div>

        <div class="form-group full-width">
          <label>RÉSULTATS/IMPACTS ATTENDUS</label>
          <textarea v-model="fiche.resultats_attendus" rows="4" placeholder="Résultats et impacts prévus"></textarea>
        </div>
      </div>

      <!-- Section II - RÉSULTATS DE L'ÉVALUATION -->
      <div class="section-header section-ii">
        <h3>II - RÉSULTATS DE L'ÉVALUATION</h3>
      </div>

      <div class="evaluation-criteria">
        <!-- Critère 1: PERTINENCE -->
        <div class="criterion">
          <div class="criterion-header">
            <h4>PERTINENCE</h4>
            <div class="score-display">{{ fiche.pertinence_score }}/5</div>
          </div>
          <div class="criterion-content">
            <div class="score-input">
              <label>SCORE</label>
              <input type="range" v-model.number="fiche.pertinence_score" min="0" max="5" step="1">
              <span class="score-value">{{ fiche.pertinence_score }}/5</span>
            </div>
            <div class="text-inputs">
              <div class="form-group">
                <label>APPRÉCIATION</label>
                <textarea v-model="fiche.pertinence_appreciation" rows="3" placeholder="Votre appréciation..."></textarea>
              </div>
              <div class="form-group">
                <label>RECOMMANDATIONS</label>
                <textarea v-model="fiche.pertinence_recommandations" rows="2" placeholder="Vos recommandations..."></textarea>
              </div>
            </div>
          </div>
        </div>

        <!-- Critère 2: ALIGNEMENT -->
        <div class="criterion">
          <div class="criterion-header">
            <h4>ALIGNEMENT À LA DOCTRINE DE TRANSFORMATION SYSTÉMIQUE</h4>
            <div class="score-display">{{ fiche.alignement_score }}/10</div>
          </div>
          <div class="criterion-content">
            <div class="score-input">
              <label>SCORE</label>
              <input type="range" v-model.number="fiche.alignement_score" min="0" max="10" step="1">
              <span class="score-value">{{ fiche.alignement_score }}/10</span>
            </div>
            <div class="text-inputs">
              <div class="form-group">
                <label>APPRÉCIATION</label>
                <textarea v-model="fiche.alignement_appreciation" rows="3" placeholder="Votre appréciation..."></textarea>
              </div>
              <div class="form-group">
                <label>RECOMMANDATIONS</label>
                <textarea v-model="fiche.alignement_recommandations" rows="2" placeholder="Vos recommandations..."></textarea>
              </div>
            </div>
          </div>
        </div>

        <!-- Critère 3: PERTINENCE DES ACTIVITÉS -->
        <div class="criterion">
          <div class="criterion-header">
            <h4>PERTINENCE DES ACTIVITÉS EN FONCTION DES COÛTS, PART DE FONCTIONNEMENT</h4>
            <div class="score-display">{{ fiche.pertinence_activites_score }}/15</div>
          </div>
          <div class="criterion-content">
            <div class="score-input">
              <label>SCORE</label>
              <input type="range" v-model.number="fiche.pertinence_activites_score" min="0" max="15" step="1">
              <span class="score-value">{{ fiche.pertinence_activites_score }}/15</span>
            </div>
            <div class="text-inputs">
              <div class="form-group">
                <label>APPRÉCIATION</label>
                <textarea v-model="fiche.pertinence_activites_appreciation" rows="3" placeholder="Votre appréciation..."></textarea>
              </div>
              <div class="form-group">
                <label>RECOMMANDATIONS</label>
                <textarea v-model="fiche.pertinence_activites_recommandations" rows="2" placeholder="Vos recommandations..."></textarea>
              </div>
            </div>
          </div>
        </div>

        <!-- Critère 4: ÉQUITÉ -->
        <div class="criterion">
          <div class="criterion-header">
            <h4>ÉQUITÉ (SOCIALE-TERRITORIALE-GENRE)</h4>
            <div class="score-display">{{ fiche.equite_score }}/15</div>
          </div>
          <div class="criterion-content">
            <div class="score-input">
              <label>SCORE</label>
              <input type="range" v-model.number="fiche.equite_score" min="0" max="15" step="1">
              <span class="score-value">{{ fiche.equite_score }}/15</span>
            </div>
            <div class="text-inputs">
              <div class="form-group">
                <label>APPRÉCIATION</label>
                <textarea v-model="fiche.equite_appreciation" rows="3" placeholder="Votre appréciation..."></textarea>
              </div>
              <div class="form-group">
                <label>RECOMMANDATIONS</label>
                <textarea v-model="fiche.equite_recommandations" rows="2" placeholder="Vos recommandations..."></textarea>
              </div>
            </div>
          </div>
        </div>

        <!-- Critères supplémentaires... -->
        <!-- Je vais ajouter les autres critères de la même manière -->
        
        <!-- TOTAL SCORE -->
        <div class="total-score">
          <h3>TOTAL SCORE = {{ scoreTotal }}/100</h3>
          <div class="appreciation-globale">
            <strong>Appréciation: {{ appreciationGlobale }}</strong>
          </div>
        </div>
      </div>

      <!-- Section III - CONCLUSION -->
      <div class="section-header section-iii">
        <h3>III - CONCLUSION</h3>
      </div>

      <div class="conclusion-section">
        <div class="form-group">
          <label>PROPOSITION</label>
          <textarea v-model="fiche.proposition" rows="3" placeholder="Votre proposition..."></textarea>
        </div>
        <div class="form-group">
          <label>RECOMMANDATIONS</label>
          <textarea v-model="fiche.recommandations_generales" rows="4" placeholder="Vos recommandations générales..."></textarea>
        </div>
        <div class="form-group">
          <label>IMPACT SUR L'EMPLOI</label>
          <select v-model="fiche.impact_sur_emploi">
            <option value="">Sélectionner...</option>
            <option value="Favorable">Favorable</option>
            <option value="Très conditionnel">Très conditionnel</option>
            <option value="D'exécution techniques pour déterminer les coûts">D'exécution techniques pour déterminer les coûts</option>
          </select>
        </div>
      </div>

      <!-- Section IV - DOCUMENTS ANNEXES -->
      <div class="section-header section-iv">
        <h3>IV - DOCUMENTS ANNEXES</h3>
      </div>

      <div class="annexes-section">
        <div class="form-group">
          <label>ÉVALUATEUR</label>
          <input v-model="fiche.evaluateur_signature" type="text" placeholder="ex: SOD">
        </div>
      </div>

      <!-- Actions -->
      <div class="form-actions">
        <button type="button" @click="sauvegarder" class="btn-secondary">Sauvegarder</button>
        <button type="button" @click="genererPDF" class="btn-primary">Générer PDF</button>
        <button type="submit" class="btn-success">Finaliser l'évaluation</button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  name: 'FicheEvaluationDGPPE',
  props: {
    projectId: {
      type: Number,
      required: true
    },
    evaluateurNom: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      fiche: {
        project_id: this.projectId,
        evaluateur_nom: this.evaluateurNom,
        reference_fiche: '',
        
        // Section I
        intitule_projet: '',
        cout_projet: '',
        origine_projet: '',
        typologie_projet: '',
        changement_climatique: '',
        sous_secteur: '',
        organisme_tutelle: '',
        snd_2025_2029: '',
        objectifs_strategiques: '',
        duree_analyse: '',
        realisation: '',
        exploitation: '',
        localisation: '',
        parties_prenantes: '',
        autres_projets_connexes: '',
        objectif_projet: '',
        activites_principales: '',
        resultats_attendus: '',
        
        // Section II - Scores
        pertinence_score: 0,
        pertinence_appreciation: '',
        pertinence_recommandations: '',
        alignement_score: 0,
        alignement_appreciation: '',
        alignement_recommandations: '',
        pertinence_activites_score: 0,
        pertinence_activites_appreciation: '',
        pertinence_activites_recommandations: '',
        equite_score: 0,
        equite_appreciation: '',
        equite_recommandations: '',
        
        // Section III
        proposition: '',
        recommandations_generales: '',
        impact_sur_emploi: '',
        
        // Section IV
        evaluateur_signature: ''
      }
    }
  },
  computed: {
    scoreTotal() {
      return (this.fiche.pertinence_score || 0) +
             (this.fiche.alignement_score || 0) +
             (this.fiche.pertinence_activites_score || 0) +
             (this.fiche.equite_score || 0);
      // Note: J'ajoute seulement les 4 premiers critères ici
      // Il faudra ajouter tous les autres critères
    },
    appreciationGlobale() {
      if (this.scoreTotal >= 85) return 'Excellent';
      if (this.scoreTotal >= 75) return 'Très bien';
      if (this.scoreTotal >= 65) return 'Bien';
      if (this.scoreTotal >= 50) return 'Passable';
      return 'Insuffisant';
    }
  },
  mounted() {
    this.genererReference();
  },
  methods: {
    genererReference() {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      this.fiche.reference_fiche = `FICHE-${year}${month}${day}-${this.projectId}`;
    },
    
    async sauvegarder() {
      try {
        const response = await fetch('/api/evaluations', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.fiche)
        });
        
        if (response.ok) {
          this.$emit('sauvegarde-succes');
          alert('Fiche sauvegardée avec succès');
        } else {
          throw new Error('Erreur lors de la sauvegarde');
        }
      } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la sauvegarde');
      }
    },
    
    async genererPDF() {
      try {
        // Utiliser l'URL complète du backend car window.open ne passe pas par le proxy Vite
        const url = `http://127.0.0.1:5002/api/projects/${this.project.id}/fiche-evaluation/pdf`;
        window.open(url, '_blank');
      } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la génération du PDF');
      }
    },
    
    async soumettreEvaluation() {
      if (this.scoreTotal === 0) {
        alert('Veuillez attribuer au moins un score avant de finaliser');
        return;
      }
      
      await this.sauvegarder();
      this.$emit('evaluation-finalisee', this.fiche);
    }
  }
}
</script>

<style scoped>
.fiche-evaluation-dgppe {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
  background: white;
}

.header-section {
  text-align: center;
  margin-bottom: 30px;
  padding: 0;
  background: white;
  border: 2px solid #2d7a2d;
  border-radius: 8px;
}


.official-header {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-bottom: 1px solid #2d7a2d;
}

.header-text {
  flex: none;
  text-align: center;
}

.header-text {
  flex: 1;
  text-align: center;
}

.republic-title {
  font-size: 16px;
  font-weight: bold;
  color: #2d7a2d;
  margin: 0 0 5px 0;
}

.ministry-title {
  font-size: 14px;
  font-weight: bold;
  color: #2d7a2d;
  margin: 0 0 5px 0;
}

.direction-title {
  font-size: 13px;
  font-weight: bold;
  color: #2d7a2d;
  margin: 0 0 5px 0;
}

.platform-title {
  font-size: 12px;
  font-weight: bold;
  color: #2d7a2d;
  margin: 0;
}

.header-logo {
  flex-shrink: 0;
  margin-left: 20px;
}

.logo-dgppe {
  width: 80px;
  height: 80px;
  object-fit: contain;
}

.document-title {
  padding: 20px;
  background: white;
}

.main-title {
  font-size: 20px;
  font-weight: bold;
  color: #2d7a2d;
  margin: 0 0 10px 0;
}

.reference-number {
  font-size: 12px;
  color: #666;
  margin: 0;
}

.project-number {
  font-size: 12px;
  color: #2c3e50;
  font-weight: 600;
  margin: 5px 0 0 0;
}

.sub-title {
  font-size: 18px;
  font-weight: normal;
}

.section-header {
  background: #2d7a2d;
  color: white;
  padding: 12px 20px;
  margin: 30px 0 20px 0;
  border-radius: 5px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: bold;
}

.presentation-grid {
  display: grid;
  gap: 20px;
  margin-bottom: 30px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  align-items: start;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-weight: bold;
  margin-bottom: 5px;
  color: #333;
  font-size: 12px;
}

.form-group input,
.form-group textarea,
.form-group select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.checkbox-group {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  font-weight: normal;
  font-size: 12px;
}

.checkbox-group input {
  margin-right: 5px;
}

.evaluation-criteria {
  margin-bottom: 30px;
}

.criterion {
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 20px;
  overflow: hidden;
}

.criterion-header {
  background: #f8f9fa;
  padding: 15px 20px;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.criterion-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: bold;
  color: #2d7a2d;
}

.score-display {
  background: #2d7a2d;
  color: white;
  padding: 5px 10px;
  border-radius: 15px;
  font-weight: bold;
  font-size: 14px;
}

.criterion-content {
  padding: 20px;
}

.score-input {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.score-input label {
  font-weight: bold;
  min-width: 60px;
}

.score-input input[type="range"] {
  flex: 1;
  margin: 0 10px;
}

.score-value {
  font-weight: bold;
  color: #2d7a2d;
  min-width: 40px;
}

.text-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.total-score {
  text-align: center;
  padding: 30px;
  background: linear-gradient(135deg, #2d7a2d, #4a9a4a);
  color: white;
  border-radius: 10px;
  margin: 30px 0;
}

.total-score h3 {
  font-size: 24px;
  margin-bottom: 10px;
}

.appreciation-globale {
  font-size: 18px;
}

.conclusion-section,
.annexes-section {
  margin-bottom: 30px;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  padding: 20px 0;
  border-top: 1px solid #ddd;
}

.btn-secondary,
.btn-primary,
.btn-success {
  padding: 12px 24px;
  border: none;
  border-radius: 5px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-success {
  background: #2d7a2d;
  color: white;
}

.btn-secondary:hover,
.btn-primary:hover,
.btn-success:hover {
  opacity: 0.9;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .text-inputs {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>