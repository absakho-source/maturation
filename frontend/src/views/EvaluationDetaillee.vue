<template>
  <PageWrapper>
    <div class="evaluation-container" :class="{ 'readonly-mode': !estAssigneAMoi }">
      <div class="header-section">
        <div class="dgppe-header">
          <div class="ministere-info">
            <h2>MINISTÈRE DE L'ÉCONOMIE, DU PLAN ET DE LA COOPÉRATION</h2>
            <h3>DIRECTION GÉNÉRALE DE LA PLANIFICATION ET DES POLITIQUES ÉCONOMIQUES</h3>
            <h4>PLATEFORME DE MATURATION DES PROJETS D'INVESTISSEMENT</h4>
          </div>
          <div class="logo-dgppe">
            <!-- Logo DGPPE ici -->
          </div>
        </div>
        
        <!-- Bouton retour -->
        <div class="navigation-section">
          <button @click="retourDashboard" class="btn-retour">
            ← Retour au tableau de bord
          </button>
        </div>
        
        <h1 class="form-title centered-title">FICHE D'ÉVALUATION</h1>
      </div>

      <!-- Section I - PRÉSENTATION DU PROJET (Pré-remplie automatiquement) -->
      <div class="section section-presentation">
        <h2 class="section-title">I - PRÉSENTATION DU PROJET</h2>
        
        <div v-if="!presentationData" class="loading">
          <p>Chargement des données du projet...</p>
        </div>
        
        <div class="project-info" v-if="presentationData">
          <div class="info-row centered-row">
            <h3 class="project-title centered-title">INTITULÉ DU PROJET: {{ presentationData.intitule }}</h3>
          </div>
          
          <div class="info-grid">
            <div class="info-item">
              <strong>SECTEUR DE PLANIFICATION:</strong> {{ presentationData.secteur }}
            </div>
            
            <div class="info-item">
              <strong>PÔLES TERRITORIAUX:</strong> {{ presentationData.poles }}
            </div>
            
            <div class="info-item">
              <strong>COÛT DU PROJET:</strong> 
              {{ formatCurrency(presentationData.cout_estimatif) }}
            </div>
            
            <div class="info-item centered-row">
              <strong>ORGANISME DE TUTELLE:</strong> {{ presentationData.organisme_tutelle }}
            </div>
            
            <div class="info-item full-width">
              <strong>DESCRIPTION DU PROJET:</strong> {{ presentationData.description }}
            </div>
            
            <div class="info-item">
              <strong>ORIGINE DU PROJET:</strong>
              <div class="checkbox-group">
                <label><input type="checkbox" v-model="presentationData.origine_projet.maturation"> MATURATION</label>
                <label><input type="checkbox" v-model="presentationData.origine_projet.offre_spontanee"> OFFRE SPONTANÉE</label>
                <label><input type="checkbox" v-model="presentationData.origine_projet.autres"> AUTRES</label>
              </div>
            </div>
            
            <div class="info-item">
              <strong>TYPOLOGIE DU PROJET:</strong>
              <div class="checkbox-group">
                <label><input type="checkbox" v-model="presentationData.typologie_projet.productif"> PRODUCTIF</label>
                <label><input type="checkbox" v-model="presentationData.typologie_projet.appui_production"> APPUI À LA PRODUCTION</label>
                <label><input type="checkbox" v-model="presentationData.typologie_projet.social"> SOCIAL</label>
                <label><input type="checkbox" v-model="presentationData.typologie_projet.environnemental"> ENVIRONNEMENTAL</label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section II - RÉSULTATS DE L'ÉVALUATION (Formulaire à remplir) -->
      <div class="section section-evaluation">
        <h2 class="section-title">II - RÉSULTATS DE L'ÉVALUATION</h2>
        
        <div class="evaluation-form">
          <div class="criteria-table">
            <div class="table-header">
              <div class="col-criteria">CRITÈRES</div>
              <div class="col-description">VALEUR ET/OU DESCRIPTION</div>
              <div class="col-score">SCORE</div>
              <div class="col-recommendations">RECOMMANDATIONS</div>
            </div>
            
            <!-- PERTINENCE -->
            <div class="criteria-row">
              <div class="col-criteria">
                <strong>PERTINENCE</strong>
                <span class="score-max">(/5)</span>
              </div>
              <div class="col-description">
                <textarea 
                  v-model="evaluationData.criteres.pertinence.description"
                  placeholder="Analyser la pertinence du projet..."
                  rows="3">
                </textarea>
              </div>
              <div class="col-score">
                <input 
                  type="number" 
                  v-model.number="evaluationData.criteres.pertinence.score"
                  min="0" 
                  max="5"
                  class="score-input">
                <span>/5</span>
              </div>
              <div class="col-recommendations">
                <textarea 
                  v-model="evaluationData.criteres.pertinence.recommandations"
                  placeholder="Recommandations..."
                  rows="2">
                </textarea>
              </div>
            </div>
            
            <!-- ALIGNEMENT -->
            <div class="criteria-row">
              <div class="col-criteria">
                <strong>ALIGNEMENT À LA DOCTRINE DE TRANSFORMATION SYSTÉMIQUE</strong>
                <span class="score-max">(/10)</span>
              </div>
              <div class="col-description">
                <textarea 
                  v-model="evaluationData.criteres.alignement.description"
                  placeholder="Évaluer l'alignement à la doctrine..."
                  rows="3">
                </textarea>
              </div>
              <div class="col-score">
                <input 
                  type="number" 
                  v-model.number="evaluationData.criteres.alignement.score"
                  min="0" 
                  max="10"
                  class="score-input">
                <span>/10</span>
              </div>
              <div class="col-recommendations">
                <textarea 
                  v-model="evaluationData.criteres.alignement.recommandations"
                  placeholder="Recommandations..."
                  rows="2">
                </textarea>
              </div>
            </div>
            
            <!-- PERTINENCE DES ACTIVITÉS -->
            <div class="criteria-row">
              <div class="col-criteria">
                <strong>PERTINENCE DES ACTIVITÉS ET BIEN FONDÉ DES COÛTS/PART DE FONCTIONNEMENT</strong>
                <span class="score-max">(/15)</span>
              </div>
              <div class="col-description">
                <textarea 
                  v-model="evaluationData.criteres.activites_couts.description"
                  placeholder="Analyser la pertinence des activités et coûts..."
                  rows="3">
                </textarea>
              </div>
              <div class="col-score">
                <input 
                  type="number" 
                  v-model.number="evaluationData.criteres.activites_couts.score"
                  min="0" 
                  max="15"
                  class="score-input">
                <span>/15</span>
              </div>
              <div class="col-recommendations">
                <textarea 
                  v-model="evaluationData.criteres.activites_couts.recommandations"
                  placeholder="Recommandations..."
                  rows="2">
                </textarea>
              </div>
            </div>
            
            <!-- ÉQUITÉ -->
            <div class="criteria-row">
              <div class="col-criteria">
                <strong>ÉQUITÉ (SOCIALE-TERRITORIALE-GENRE)</strong>
                <span class="score-max">(/15)</span>
              </div>
              <div class="col-description">
                <textarea 
                  v-model="evaluationData.criteres.equite.description"
                  placeholder="Évaluer l'équité sociale, territoriale et de genre..."
                  rows="3">
                </textarea>
              </div>
              <div class="col-score">
                <input 
                  type="number" 
                  v-model.number="evaluationData.criteres.equite.score"
                  min="0" 
                  max="15"
                  class="score-input">
                <span>/15</span>
              </div>
              <div class="col-recommendations">
                <textarea 
                  v-model="evaluationData.criteres.equite.recommandations"
                  placeholder="Recommandations..."
                  rows="2">
                </textarea>
              </div>
            </div>
            
            <!-- VIABILITÉ -->
            <div class="criteria-row">
              <div class="col-criteria">
                <strong>VIABILITÉ/RENTABILITÉ FINANCIÈRE</strong>
                <span class="score-max">(/5)</span>
              </div>
              <div class="col-description">
                <textarea 
                  v-model="evaluationData.criteres.viabilite.description"
                  placeholder="Analyser la viabilité financière..."
                  rows="3">
                </textarea>
              </div>
              <div class="col-score">
                <input 
                  type="number" 
                  v-model.number="evaluationData.criteres.viabilite.score"
                  min="0" 
                  max="5"
                  class="score-input">
                <span>/5</span>
              </div>
              <div class="col-recommendations">
                <textarea 
                  v-model="evaluationData.criteres.viabilite.recommandations"
                  placeholder="Recommandations..."
                  rows="2">
                </textarea>
              </div>
            </div>
            
            <!-- RENTABILITÉ SOCIO-ÉCONOMIQUE -->
            <div class="criteria-row">
              <div class="col-criteria">
                <strong>RENTABILITÉ SOCIO-ÉCONOMIQUE (ACA/MPR)</strong>
                <span class="score-max">(/5)</span>
              </div>
              <div class="col-description">
                <textarea 
                  v-model="evaluationData.criteres.rentabilite.description"
                  placeholder="Évaluer la rentabilité socio-économique..."
                  rows="3">
                </textarea>
              </div>
              <div class="col-score">
                <input 
                  type="number" 
                  v-model.number="evaluationData.criteres.rentabilite.score"
                  min="0" 
                  max="5"
                  class="score-input">
                <span>/5</span>
              </div>
              <div class="col-recommendations">
                <textarea 
                  v-model="evaluationData.criteres.rentabilite.recommandations"
                  placeholder="Recommandations..."
                  rows="2">
                </textarea>
              </div>
            </div>
            
            <!-- BÉNÉFICES STRATÉGIQUES -->
            <div class="criteria-row">
              <div class="col-criteria">
                <strong>BÉNÉFICES STRATÉGIQUES (SÉCURITÉ-RÉSILIENCE-INNOVATION-COMPÉTITIVITÉ-CONTENU LOCAL, ETC.)</strong>
                <span class="score-max">(/10)</span>
              </div>
              <div class="col-description">
                <textarea
                  v-model="evaluationData.criteres.benefices_strategiques.description"
                  placeholder="Analyser les bénéfices stratégiques..."
                  rows="3">
                </textarea>
              </div>
              <div class="col-score">
                <input
                  type="number"
                  v-model.number="evaluationData.criteres.benefices_strategiques.score"
                  min="0"
                  max="10"
                  class="score-input">
                <span>/10</span>
              </div>
              <div class="col-recommendations">
                <textarea
                  v-model="evaluationData.criteres.benefices_strategiques.recommandations"
                  placeholder="Recommandations..."
                  rows="2">
                </textarea>
              </div>
            </div>
            
            <!-- PÉRENNITÉ -->
            <div class="criteria-row">
              <div class="col-criteria">
                <strong>PÉRENNITÉ ET DURABILITÉ DES EFFETS ET IMPACTS DU PROJET</strong>
                <span class="score-max">(/5)</span>
              </div>
              <div class="col-description">
                <textarea 
                  v-model="evaluationData.criteres.perennite.description"
                  placeholder="Évaluer la pérennité du projet..."
                  rows="3">
                </textarea>
              </div>
              <div class="col-score">
                <input 
                  type="number" 
                  v-model.number="evaluationData.criteres.perennite.score"
                  min="0" 
                  max="5"
                  class="score-input">
                <span>/5</span>
              </div>
              <div class="col-recommendations">
                <textarea 
                  v-model="evaluationData.criteres.perennite.recommandations"
                  placeholder="Recommandations..."
                  rows="2">
                </textarea>
              </div>
            </div>
            
            <!-- AVANTAGES ET COÛTS INTANGIBLES -->
            <div class="criteria-row">
              <div class="col-criteria">
                <strong>AVANTAGES ET COÛTS INTANGIBLES</strong>
                <span class="score-max">(/10)</span>
              </div>
              <div class="col-description">
                <textarea 
                  v-model="evaluationData.criteres.avantages_intangibles.description"
                  placeholder="Analyser les avantages et coûts intangibles..."
                  rows="3">
                </textarea>
              </div>
              <div class="col-score">
                <input 
                  type="number" 
                  v-model.number="evaluationData.criteres.avantages_intangibles.score"
                  min="0" 
                  max="10"
                  class="score-input">
                <span>/10</span>
              </div>
              <div class="col-recommendations">
                <textarea 
                  v-model="evaluationData.criteres.avantages_intangibles.recommandations"
                  placeholder="Recommandations..."
                  rows="2">
                </textarea>
              </div>
            </div>
            
            <!-- FAISABILITÉ -->
            <div class="criteria-row">
              <div class="col-criteria">
                <strong>FAISABILITÉ DU PROJET / RISQUES POTENTIELS</strong>
                <span class="score-max">(/5)</span>
              </div>
              <div class="col-description">
                <textarea 
                  v-model="evaluationData.criteres.faisabilite.description"
                  placeholder="Évaluer la faisabilité et les risques..."
                  rows="3">
                </textarea>
              </div>
              <div class="col-score">
                <input 
                  type="number" 
                  v-model.number="evaluationData.criteres.faisabilite.score"
                  min="0" 
                  max="5"
                  class="score-input">
                <span>/5</span>
              </div>
              <div class="col-recommendations">
                <textarea 
                  v-model="evaluationData.criteres.faisabilite.recommandations"
                  placeholder="Recommandations..."
                  rows="2">
                </textarea>
              </div>
            </div>
            
            <!-- PPP -->
            <div class="criteria-row">
              <div class="col-criteria">
                <strong>POTENTIALITÉ OU OPPORTUNITÉ DU PROJET À ÊTRE RÉALISÉ EN PPP</strong>
                <span class="score-max">(/5)</span>
              </div>
              <div class="col-description">
                <textarea 
                  v-model="evaluationData.criteres.ppp.description"
                  placeholder="Évaluer l'opportunité de réalisation en PPP..."
                  rows="3">
                </textarea>
              </div>
              <div class="col-score">
                <input 
                  type="number" 
                  v-model.number="evaluationData.criteres.ppp.score"
                  min="0" 
                  max="5"
                  class="score-input">
                <span>/5</span>
              </div>
              <div class="col-recommendations">
                <textarea 
                  v-model="evaluationData.criteres.ppp.recommandations"
                  placeholder="Recommandations..."
                  rows="2">
                </textarea>
              </div>
            </div>
            
            <!-- IMPACTS ENVIRONNEMENTAUX -->
            <div class="criteria-row">
              <div class="col-criteria">
                <strong>IMPACTS ENVIRONNEMENTAUX</strong>
                <span class="score-max">(/5)</span>
              </div>
              <div class="col-description">
                <textarea 
                  v-model="evaluationData.criteres.impact_environnemental.description"
                  placeholder="Analyser les impacts environnementaux..."
                  rows="3">
                </textarea>
              </div>
              <div class="col-score">
                <input 
                  type="number" 
                  v-model.number="evaluationData.criteres.impact_environnemental.score"
                  min="0" 
                  max="5"
                  class="score-input">
                <span>/5</span>
              </div>
              <div class="col-recommendations">
                <textarea 
                  v-model="evaluationData.criteres.impact_environnemental.recommandations"
                  placeholder="Recommandations..."
                  rows="2">
                </textarea>
              </div>
            </div>
            
            <!-- IMPACT SUR L'EMPLOI -->
            <div class="criteria-row">
              <div class="col-criteria">
                <strong>IMPACT SUR L'EMPLOI</strong>
                <span class="score-max">(/5)</span>
              </div>
              <div class="col-description">
                <textarea 
                  v-model="evaluationData.criteres.impact_emploi.description"
                  placeholder="Analyser l'impact sur l'emploi et la création d'emplois..."
                  rows="3">
                </textarea>
              </div>
              <div class="col-score">
                <input 
                  type="number" 
                  v-model.number="evaluationData.criteres.impact_emploi.score"
                  min="0" 
                  max="5"
                  class="score-input">
                <span>/5</span>
              </div>
              <div class="col-recommendations">
                <textarea 
                  v-model="evaluationData.criteres.impact_emploi.recommandations"
                  placeholder="Recommandations pour l'emploi..."
                  rows="2">
                </textarea>
              </div>
            </div>
            
            <!-- Score total en fin de tableau -->
            <div class="criteria-row total-row">
              <div class="col-criteria">
                <strong>TOTAL SCORE =</strong>
              </div>
              <div class="col-description"></div>
              <div class="col-score">
                <strong class="total-score">{{ calculerScoreTotal() }}/100</strong>
              </div>
              <div class="col-recommendations"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section III - CONCLUSION -->
      <div class="section section-conclusion">
        <h2 class="section-title">III - CONCLUSION</h2>
        
        <div class="conclusion-form">
          <div class="form-group">
            <label><strong>PROPOSITION:</strong></label>
            <select v-model="evaluationData.proposition" class="select-proposition">
              <option value="">-- Sélectionner --</option>
              <option value="Favorable">Favorable</option>
              <option value="Favorable sous condition">Favorable sous condition</option>
              <option value="Compléments demandés">Compléments demandés</option>
              <option value="Défavorable">Défavorable</option>
            </select>
          </div>
          
          <div class="form-group">
            <label><strong>RECOMMANDATIONS:</strong></label>
            <textarea 
              v-model="evaluationData.recommandations"
              placeholder="Saisir les recommandations finales..."
              rows="5"
              class="recommendations-textarea">
            </textarea>
          </div>
        </div>
      </div>

      <!-- Section Évaluateur -->
      <div class="section section-evaluateur">        
        <div class="evaluateur-info">
          <div class="form-group">
            <label><strong>ÉVALUATEUR:</strong></label>
            <input 
              v-model="evaluationData.evaluateur_nom" 
              type="text" 
              placeholder="Nom de l'évaluateur"
              class="evaluateur-input"
              readonly>
            <small class="help-text">Nom pré-rempli automatiquement</small>
          </div>
        </div>
      </div>

      <!-- Message si projet non assigné -->
      <div v-if="!estAssigneAMoi && projectInfo" class="warning-readonly">
        <div class="warning-icon">🔒</div>
        <div class="warning-content">
          <h3>Projet non assigné</h3>
          <p>Ce projet est assigné à <strong>{{ projectInfo.evaluateur_display_name || projectInfo.evaluateur_nom }}</strong>.</p>
          <p>Vous pouvez consulter cette fiche d'évaluation en lecture seule uniquement.</p>
        </div>
      </div>

      <!-- Actions -->
      <div class="actions-section">
        <div class="actions-group">
          <button @click="sauvegarderBrouillon" class="btn btn-draft" :disabled="!estAssigneAMoi" title="Sauvegarder sans finaliser l'évaluation">
            💾 Sauvegarder brouillon
          </button>

          <button @click="sauvegarder" class="btn btn-primary" :disabled="!peutSauvegarder" title="Finaliser et soumettre l'évaluation">
            ✅ Finaliser l'évaluation
          </button>

          <button @click="retour" class="btn btn-outline">
            ← Retour à la liste
          </button>
        </div>
      </div>
      
      <!-- Indicateur de progression -->
      <div class="progress-indicator">
        <div class="score-summary">
          <span class="score-current">{{ calculerScoreTotal() }}</span>
          <span class="score-total">/100</span>
          <span class="score-appreciation">({{ getAppreciation() }})</span>
        </div>
      </div>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue'

export default {
  name: 'EvaluationDetaillee',
  components: {
    PageWrapper
  },
  data() {
    return {
      projectId: null,
      presentationData: null,
      projectInfo: null, // Informations complètes du projet
      evaluationData: {
        evaluateur_nom: '',
        criteres: {
          pertinence: { score: 0, description: '', recommandations: '' },
          alignement: { score: 0, description: '', recommandations: '' },
          activites_couts: { score: 0, description: '', recommandations: '' },
          equite: { score: 0, description: '', recommandations: '' },
          viabilite: { score: 0, description: '', recommandations: '' },
          rentabilite: { score: 0, description: '', recommandations: '' },
          benefices_strategiques: { score: 0, description: '', recommandations: '' },
          perennite: { score: 0, description: '', recommandations: '' },
          avantages_intangibles: { score: 0, description: '', recommandations: '' },
          faisabilite: { score: 0, description: '', recommandations: '' },
          ppp: { score: 0, description: '', recommandations: '' },
          impact_environnemental: { score: 0, description: '', recommandations: '' },
          impact_emploi: { score: 0, description: '', recommandations: '' }
        },
        proposition: '',
        recommandations: ''
      },
      evaluationSauvegardee: false,
      estBrouillon: false,
      derniereSauvegarde: null,
      loading: false
    }
  },
  computed: {
    estAssigneAMoi() {
      // Vérifier si le projet est assigné à l'évaluateur connecté
      return this.projectInfo && this.projectInfo.est_assigne_a_moi === true;
    },
    peutSauvegarder() {
      // Sauvegarder seulement si le projet est assigné à l'évaluateur
      return this.estAssigneAMoi &&
             this.evaluationData.evaluateur_nom &&
             this.evaluationData.proposition &&
             this.calculerScoreTotal() > 0
    }
  },
  async mounted() {
    this.projectId = this.$route.params.id
    await this.chargerInfosProjet()
    await this.chargerDonneesProjet()
    await this.chargerEvaluationExistante()
    // Toujours charger le nom d'évaluateur depuis localStorage (utilisateur connecté)
    await this.chargerUtilisateurConnecte()
    // Charger le brouillon s'il existe
    this.chargerBrouillon()
  },
  methods: {
    async chargerInfosProjet() {
      try {
        const user = JSON.parse(localStorage.getItem("user") || "null") || {};
        const response = await fetch(`/api/projects?role=${user.role}&username=${user.username}`);
        if (response.ok) {
          const allProjects = await response.json();
          // Trouver le projet actuel dans la liste
          this.projectInfo = allProjects.find(p => p.id === parseInt(this.projectId));

          // Vérifier si le projet n'est pas assigné à l'évaluateur
          if (this.projectInfo && !this.projectInfo.est_assigne_a_moi) {
            alert('⚠️ Ce projet est assigné à un autre évaluateur. Vous pouvez consulter les informations mais ne pouvez pas modifier l\'évaluation.');
          }
        }
      } catch (error) {
        console.error('Erreur lors du chargement des infos du projet:', error);
      }
    },
    async chargerDonneesProjet() {
      try {
        const response = await fetch(`/api/projects/${this.projectId}/presentation`)
        if (response.ok) {
          this.presentationData = await response.json()
          // Initialiser les structures d'origine et typologie si elles n'existent pas
          if (!this.presentationData.origine_projet) {
            this.presentationData.origine_projet = {
              maturation: false,
              offre_spontanee: false,
              autres: false
            }
          }
          if (!this.presentationData.typologie_projet) {
            this.presentationData.typologie_projet = {
              productif: false,
              appui_production: false,
              social: false,
              environnemental: false
            }
          }
          // Pré-remplir organisme de tutelle si absent
          if (!this.presentationData.organisme_tutelle || this.presentationData.organisme_tutelle.trim() === '') {
            this.presentationData.organisme_tutelle = "MINISTÈRE DE L'ÉCONOMIE, DU PLAN ET DE LA COOPÉRATION";
          }
        } else {
          console.error('Erreur lors du chargement des données du projet')
        }
      } catch (error) {
        console.error('Erreur:', error)
      }
    },
      async chargerUtilisateurConnecte() {
        try {
          // Récupérer l'utilisateur depuis localStorage
          const userStr = localStorage.getItem('user')
          if (userStr) {
            const user = JSON.parse(userStr)
            // Utiliser le display_name de l'utilisateur connecté
            this.evaluationData.evaluateur_nom = user.display_name || user.username || user.nom || ''
            console.log('Nom évaluateur chargé:', this.evaluationData.evaluateur_nom)
          } else {
            this.evaluationData.evaluateur_nom = ''
            console.warn('Aucun utilisateur connecté trouvé dans localStorage')
          }
        } catch (error) {
          this.evaluationData.evaluateur_nom = ''
          console.error('Erreur lors du chargement du profil utilisateur:', error)
        }
      },
    
    async chargerEvaluationExistante() {
      try {
        const response = await fetch(`/api/projects/${this.projectId}/fiche-evaluation`)
        if (response.ok) {
          const fiche = await response.json()
          // Charger les données de la fiche si elle existe
          // Le nom de l'évaluateur sera chargé séparément dans mounted()
        }
      } catch (error) {
        console.log('Aucune fiche d\'évaluation existante - création d\'une nouvelle')
      }
    },
    
    calculerScoreTotal() {
      return Object.values(this.evaluationData.criteres)
        .reduce((total, critere) => total + (critere.score || 0), 0)
    },
    
    getAppreciation() {
      const score = this.calculerScoreTotal()
      if (score >= 80) return 'Excellent'
      if (score >= 70) return 'Très bien'
      if (score >= 60) return 'Bien'
      if (score >= 50) return 'Passable'
      return 'Insuffisant'
    },
    
    async sauvegarder() {
      if (!this.peutSauvegarder) return
      
      this.loading = true
      try {
        const response = await fetch(`/api/projects/${this.projectId}/fiche-evaluation`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.evaluationData)
        })
        
        if (response.ok) {
          const result = await response.json()
          this.evaluationSauvegardee = true
          this.$emit('evaluation-saved', result)

          // Supprimer le brouillon localStorage après finalisation réussie
          this.supprimerBrouillon()

          alert('Évaluation finalisée avec succès!')

          // Rediriger vers le dashboard
          this.$router.push('/evaluation')
        } else {
          const error = await response.json()
          alert(`Erreur: ${error.error}`)
        }
      } catch (error) {
        console.error('Erreur:', error)
        alert('Erreur lors de la sauvegarde')
      } finally {
        this.loading = false
      }
    },
    
    async genererPDF() {
      try {
        // Utiliser l'URL du backend (configurée via VITE_API_URL en production)
        const API_BASE_URL = import.meta.env.VITE_API_URL || '';
        const url = `${API_BASE_URL}/api/projects/${this.projectId}/fiche-evaluation/pdf`
        window.open(url, '_blank')
      } catch (error) {
        console.error('Erreur génération PDF:', error)
        alert('Erreur lors de la génération du PDF')
      }
    },
    
    retour() {
      this.$router.push('/evaluation')
    },
    
    retourDashboard() {
      this.$router.push('/evaluation')
    },
    
    async sauvegarderBrouillon() {
      this.loading = true
      try {
        // Sauvegarder en localStorage pour persistance locale
        const brouillonKey = `evaluation-brouillon-${this.projectId}`
        const brouillonData = {
          ...this.evaluationData,
          derniereSauvegarde: new Date().toISOString(),
          estBrouillon: true
        }
        localStorage.setItem(brouillonKey, JSON.stringify(brouillonData))
        
        // Optionnel : sauvegarder aussi sur le serveur avec un statut "brouillon"
        const response = await fetch(`/api/projects/${this.projectId}/fiche-evaluation-brouillon`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(brouillonData)
        })
        
        this.estBrouillon = true
        this.derniereSauvegarde = new Date()
        
        if (response.ok) {
          alert('Brouillon sauvegardé avec succès ! Vous pouvez continuer l\'évaluation plus tard.')
        } else {
          alert('Brouillon sauvegardé localement. Continuez votre évaluation quand vous voulez !')
        }
      } catch (error) {
        // Même en cas d'erreur serveur, la sauvegarde locale fonctionne
        this.estBrouillon = true
        this.derniereSauvegarde = new Date()
        alert('Brouillon sauvegardé localement. Vous pouvez continuer plus tard !')
      } finally {
        this.loading = false
      }
    },
    
    chargerBrouillon() {
      const brouillonKey = `evaluation-brouillon-${this.projectId}`
      const brouillonSauvegarde = localStorage.getItem(brouillonKey)

      if (brouillonSauvegarde) {
        try {
          const brouillonData = JSON.parse(brouillonSauvegarde)

          // Vérifier que le brouillon appartient bien à l'utilisateur actuel
          const userStr = localStorage.getItem('user')
          if (userStr) {
            const user = JSON.parse(userStr)
            const currentEvaluateurNom = user.display_name || user.username || user.nom || ''

            // Si le nom de l'évaluateur dans le brouillon ne correspond pas à l'utilisateur actuel, supprimer le brouillon
            if (brouillonData.evaluateur_nom !== currentEvaluateurNom) {
              console.log('Brouillon d\'un autre évaluateur détecté - suppression')
              localStorage.removeItem(brouillonKey)
              return
            }
          }

          if (brouillonData.estBrouillon) {
            // Proposer de restaurer le brouillon
            const restaurer = confirm(`Un brouillon d'évaluation a été trouvé (sauvegardé le ${new Date(brouillonData.derniereSauvegarde).toLocaleString()}). Voulez-vous le restaurer ?`)
            if (restaurer) {
              this.evaluationData = { ...brouillonData }
              this.estBrouillon = true
              this.derniereSauvegarde = new Date(brouillonData.derniereSauvegarde)
              alert('Brouillon restauré ! Vous pouvez continuer votre évaluation.')
            } else {
              // Si l'utilisateur ne veut pas restaurer, supprimer le brouillon
              localStorage.removeItem(brouillonKey)
            }
          }
        } catch (error) {
          console.error('Erreur lors du chargement du brouillon:', error)
        }
      }
    },
    
    supprimerBrouillon() {
      const brouillonKey = `evaluation-brouillon-${this.projectId}`
      localStorage.removeItem(brouillonKey)
      this.estBrouillon = false
      this.derniereSauvegarde = null
    },
    
    formatCurrency(amount) {
      if (!amount) return '0 FCFA'
      return new Intl.NumberFormat('fr-FR').format(amount) + ' FCFA'
    }
  }
}
</script>

<style scoped>
.evaluation-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Arial', sans-serif;
}

.header-section {
  text-align: center;
  margin-bottom: 30px;
}

.dgppe-header {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border: 2px solid #ddd;
  text-align: center;
}

.ministere-info {
  text-align: center;
  width: 100%;
}

.ministere-info h2 {
  font-size: 16px;
  font-weight: bold;
  margin: 0;
  color: #2c3e50;
  text-align: center;
}

.ministere-info h3 {
  font-size: 14px;
  font-weight: bold;
  margin: 5px 0;
  color: #34495e;
  text-align: center;
}

.ministere-info h4 {
  font-size: 12px;
  font-weight: normal;
  margin: 5px 0 0;
  color: #7f8c8d;
  text-align: center;
}

.form-title {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin: 20px 0;
}

.section {
  margin-bottom: 30px;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.section-title {
  background: #3498db;
  color: white;
  padding: 15px;
  margin: 0;
  font-size: 18px;
  font-weight: bold;
  text-align: center;
}

.section-presentation {
  background: #f8f9fa;
}

.project-info {
  padding: 20px;
}

.project-title {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 18px;
    text-align: center;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.info-item {
  padding: 10px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.checkbox-group {
  display: flex;
  gap: 15px;
  margin-top: 5px;
  flex-wrap: wrap;
}

.checkbox-group label {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.checkbox-group input[type="checkbox"] {
  margin: 0;
}

.criteria-table {
  display: grid;
  grid-template-columns: 2fr 3fr 1fr 2fr;
  gap: 1px;
  background: #ddd;
}

.table-header {
  display: contents;
}

.table-header > div {
  background: #34495e;
  color: white;
  padding: 15px;
  font-weight: bold;
  text-align: center;
}

.criteria-row {
  display: contents;
}

.criteria-row > div {
  background: white;
  padding: 15px;
  border-bottom: 1px solid #ddd;
}

.col-criteria {
  font-weight: 500;
  background: #f8f9fa !important;
}

.score-max {
  font-size: 12px;
  color: #7f8c8d;
  display: block;
  margin-top: 5px;
}

.score-input {
  width: 60px;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
  text-align: center;
}

.total-row > div {
  background: #e8f5e8 !important;
  font-weight: bold;
}

.total-score {
  color: #27ae60;
  font-size: 18px;
}

textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
  font-family: inherit;
}

.conclusion-form, .evaluateur-info {
  background: white;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.section-evaluateur {
  background: #f8f9fa;
  border: 2px solid #007bff;
  margin-top: 20px;
}

.section-evaluateur .evaluateur-info {
  background: #e3f2fd;
  border: 1px solid #2196f3;
}

.evaluateur-input[readonly] {
  background-color: #f5f5f5;
  color: #666;
}

.help-text {
  color: #666;
  font-style: italic;
  margin-top: 5px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.select-proposition, .evaluateur-input {
  width: 100%;
  max-width: 300px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.recommendations-textarea {
  width: 100%;
  height: 100px;
}

.actions-section {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #27ae60;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #229954;
}

.btn-primary:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.btn-secondary {
  background: #3498db;
  color: white;
}

.btn-secondary:hover {
  background: #2980b9;
}

.btn-outline {
  background: transparent;
  color: #3498db;
  border: 2px solid #3498db;
}

.btn-outline:hover {
  background: #3498db;
  color: white;
}

.progress-indicator {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: white;
  padding: 15px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  border: 2px solid #3498db;
}

.score-summary {
  text-align: center;
}

.score-current {
  font-size: 24px;
  font-weight: bold;
  color: #27ae60;
}

.score-total {
  font-size: 18px;
  color: #7f8c8d;
}

.score-appreciation {
  display: block;
  font-size: 12px;
  color: #3498db;
  margin-top: 5px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}

.centered-title {
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.centered-row {
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}

@media (max-width: 768px) {
  .criteria-table {
    grid-template-columns: 1fr;
  }
  
  .table-header {
    display: none;
  }
  
  .criteria-row > div:before {
    font-weight: bold;
    display: block;
    margin-bottom: 5px;
  }
  
  .col-criteria:before { content: "Critère: "; }
  .col-description:before { content: "Description: "; }
  .col-score:before { content: "Score: "; }
  .col-recommendations:before { content: "Recommandations: "; }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .progress-indicator {
    position: static;
    margin-top: 20px;
  }
}

/* Mode lecture seule pour projets non assignés */
.readonly-mode input,
.readonly-mode textarea,
.readonly-mode select {
  pointer-events: none;
  background-color: #f5f5f5 !important;
  color: #666 !important;
  border-color: #ddd !important;
  opacity: 0.7;
}

.readonly-mode .checkbox-group input[type="checkbox"] {
  pointer-events: none;
}

.warning-readonly {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  background: linear-gradient(135deg, #fff3cd 0%, #fff8e1 100%);
  border: 2px solid #ffc107;
  border-radius: 12px;
  padding: 1.5rem;
  margin: 2rem 0;
  box-shadow: 0 4px 12px rgba(255, 193, 7, 0.2);
}

.warning-icon {
  font-size: 3rem;
  flex-shrink: 0;
}

.warning-content h3 {
  margin: 0 0 0.5rem 0;
  color: #856404;
  font-size: 1.2rem;
}

.warning-content p {
  margin: 0.25rem 0;
  color: #856404;
  font-size: 0.95rem;
}

.warning-content strong {
  color: #664d03;
}
</style>