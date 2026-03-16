<template>
  <PageWrapper>
    <div class="evaluation-container" :class="{ 'readonly-mode': !estAssigneAMoi }">
      <div class="header-section">
        <div class="dgppe-header">
          <div class="ministere-info">
            <h2>MINISTÈRE DE L'ÉCONOMIE, DU PLAN ET DE LA COOPÉRATION</h2>
            <h3>DIRECTION GÉNÉRALE DE LA PLANIFICATION ET DES POLITIQUES ÉCONOMIQUES</h3>
            <h4>PLATEFORME DE SUIVI DE LA MATURATION DES PROJETS</h4>
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

        <h1 class="form-title centered-title">
          FICHE D'ÉVALUATION
          <span v-if="projectInfo && projectInfo.numero_projet" class="numero-projet-badge">
            {{ projectInfo.numero_projet }}
          </span>
          <span v-if="projectInfo && projectInfo.niveau_priorite === 'prioritaire_ant'" class="badge-prioritaire-fiche">
            PROJET PRIORITAIRE
          </span>
        </h1>

        <!-- Informations sur la version du formulaire -->
        <div v-if="config && config.version_affichage" class="version-info">
          <span class="version-value">{{ config.version_affichage }}</span>
        </div>
      </div>

      <!-- Section I - PRÉSENTATION DU PROJET (Pré-remplie automatiquement) -->
      <div class="section section-presentation">
        <h2 class="section-title">I - PRÉSENTATION DU PROJET</h2>

        <div v-if="!presentationData" class="loading">
          <p>Chargement des données du projet...</p>
        </div>

        <div class="project-info" v-if="presentationData">
          <!-- Intitulé du projet - Pleine largeur en dehors de la grille -->
          <div class="intitule-section">
            <label class="intitule-label">INTITULÉ DU PROJET</label>
            <textarea v-model="presentationData.intitule" class="input-intitule-fullwidth" rows="2" placeholder="Intitulé du projet"></textarea>
          </div>

          <div class="info-grid">
            <div class="info-item-editable">
              <strong>SECTEUR DE PLANIFICATION:</strong>
              <input type="text" v-model="presentationData.secteur" class="input-text" placeholder="Secteur de planification">
            </div>

            <div class="info-item-editable">
              <strong>PÔLES TERRITORIAUX:</strong>
              <input type="text" v-model="presentationData.poles" class="input-text" placeholder="Pôles territoriaux">
            </div>

            <div class="info-item-editable">
              <strong>COÛT DU PROJET (FCFA):</strong>
              <input
                type="text"
                :value="formatCoutWithSpaces(presentationData.cout_estimatif)"
                @input="updateCout"
                class="input-text"
                placeholder="Ex: 1 000 000">
            </div>

            <div class="info-item-editable">
              <strong>ORGANISME DE TUTELLE:</strong>
              <input type="text" v-model="presentationData.organisme_tutelle" class="input-text" placeholder="Organisme de tutelle">
            </div>

            <div class="info-item-editable full-width">
              <strong>DESCRIPTION DU PROJET:</strong>
              <textarea v-model="presentationData.description" class="textarea-text" rows="4" placeholder="Description du projet"></textarea>
            </div>
          </div>
        </div>
      </div>

      <!-- Section II - CLASSIFICATION DU PROJET -->
      <div class="section section-classification">
        <h2 class="section-title">II - CLASSIFICATION DU PROJET</h2>

        <div class="project-info" v-if="presentationData">
          <!-- Grille 2 colonnes pour Origine et Dimensions -->
          <div class="classification-grid">
            <!-- Colonne 1: Origine du projet -->
            <div class="classification-section">
              <div class="classification-header">ORIGINE DU PROJET</div>
              <div class="radio-group-vertical">
                <label><input type="radio" v-model="presentationData.origine_projet_choix" value="maturation"> Maturation</label>
                <label><input type="radio" v-model="presentationData.origine_projet_choix" value="offre_spontanee"> Offre spontanée</label>
                <label><input type="radio" v-model="presentationData.origine_projet_choix" value="autres"> Autres</label>
              </div>
              <div v-if="presentationData.origine_projet_choix === 'autres'" class="autres-precisions-inline">
                <input type="text" v-model="presentationData.origine_projet_autres_precision" placeholder="Précisez..." class="input-text">
              </div>
            </div>

            <!-- Colonne 2: Dimensions transversales -->
            <div class="classification-section">
              <div class="classification-header">DIMENSIONS TRANSVERSALES</div>
              <div class="dimensions-container">
                <div class="dimension-block">
                  <div class="dimension-subtitle">Changement climatique</div>
                  <div class="checkbox-group-compact">
                    <label><input type="checkbox" v-model="presentationData.changement_climatique_adaptation"> Adaptation</label>
                    <label><input type="checkbox" v-model="presentationData.changement_climatique_attenuation"> Atténuation</label>
                  </div>
                </div>
                <div class="dimension-block">
                  <div class="dimension-subtitle">Genre</div>
                  <div class="checkbox-group-compact">
                    <label><input type="checkbox" v-model="presentationData.genre"> Prise en compte du genre</label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Tableaux de présentation détaillée du projet -->
          <div class="project-details-table">
            <table>
              <thead>
                <tr>
                  <th>ARTICULATION</th>
                  <th>AXE(S)</th>
                  <th>OBJECTIF(S) STRATÉGIQUE(S)</th>
                  <th>OBJECTIFS DE DÉVELOPPEMENT DURABLE</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><textarea v-model="presentationData.articulation" rows="2"></textarea></td>
                  <td><textarea v-model="presentationData.axes" rows="2"></textarea></td>
                  <td><textarea v-model="presentationData.objectifs_strategiques" rows="2"></textarea></td>
                  <td><textarea v-model="presentationData.odd" rows="2"></textarea></td>
                </tr>
              </tbody>
            </table>

            <table>
              <thead>
                <tr>
                  <th>DURÉE D'ANALYSE</th>
                  <th>RÉALISATION</th>
                  <th>EXPLOITATION</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><textarea v-model="presentationData.duree_analyse" rows="2"></textarea></td>
                  <td><textarea v-model="presentationData.realisation" rows="2"></textarea></td>
                  <td><textarea v-model="presentationData.exploitation" rows="2"></textarea></td>
                </tr>
              </tbody>
            </table>

            <table>
              <thead>
                <tr>
                  <th>LOCALISATION</th>
                  <th>PARTIES PRENANTES</th>
                  <th>AUTRES PROJETS/PROG. CONNEXES</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><textarea v-model="presentationData.localisation" rows="3"></textarea></td>
                  <td><textarea v-model="presentationData.parties_prenantes" rows="3"></textarea></td>
                  <td><textarea v-model="presentationData.autres_projets_connexes" rows="3"></textarea></td>
                </tr>
              </tbody>
            </table>

            <table>
              <thead>
                <tr>
                  <th>OBJECTIF DU PROJET</th>
                  <th>ACTIVITÉS PRINCIPALES</th>
                  <th>EXTRANTS / RÉSULTATS / IMPACTS ATTENDUS</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><textarea v-model="presentationData.objectif_projet" rows="4"></textarea></td>
                  <td><textarea v-model="presentationData.activites_principales" rows="4"></textarea></td>
                  <td><textarea v-model="presentationData.resultats_attendus" rows="4"></textarea></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Section III - RÉSULTATS DE L'ÉVALUATION (Formulaire à remplir) -->
      <div class="section section-evaluation">
        <h2 class="section-title">III - RÉSULTATS DE L'ÉVALUATION</h2>

        <div v-if="loadingCriteria" class="loading">
          <p>Chargement des critères d'évaluation...</p>
        </div>

        <div v-else class="evaluation-form">
          <div class="criteria-table">
            <div class="table-header">
              <div class="col-criteria">CRITÈRES</div>
              <div class="col-description">VALEUR ET/OU DESCRIPTION</div>
              <div class="col-score">SCORE</div>
              <div class="col-recommendations">RECOMMANDATIONS</div>
            </div>

            <!-- Boucle dynamique sur les critères chargés depuis la DB -->
            <div v-for="critere in criteresEvaluation" :key="critere.id" class="criteria-row">
              <div class="col-criteria">
                <strong>{{ critere.nom.toUpperCase() }}</strong>
              </div>
              <div class="col-description">
                <textarea
                  v-if="critere.avec_description && evaluationData.criteres[critere.cle]"
                  v-model="evaluationData.criteres[critere.cle].description"
                  :placeholder="`Analyser ${critere.nom.toLowerCase()}...`"
                  rows="3">
                </textarea>
                <span v-else class="no-description">—</span>
              </div>
              <div class="col-score">
                <input
                  v-if="evaluationData.criteres[critere.cle]"
                  type="number"
                  v-model.number="evaluationData.criteres[critere.cle].score"
                  min="0"
                  :max="critere.score_max"
                  step="0.5"
                  class="score-input">
                <span>/{{ critere.score_max }}</span>
              </div>
              <div class="col-recommendations">
                <textarea
                  v-if="critere.avec_recommandations && evaluationData.criteres[critere.cle]"
                  v-model="evaluationData.criteres[critere.cle].recommandations"
                  placeholder="Recommandations..."
                  rows="2">
                </textarea>
                <span v-else class="no-recommandations">—</span>
              </div>
            </div>

            <!-- Score total en fin de tableau -->
            <div class="criteria-row total-row">
              <div class="col-criteria">
                <strong>SCORE TOTAL =</strong>
              </div>
              <div class="col-description"></div>
              <div class="col-score">
                <strong class="total-score" :class="{
                  'score-acceptable': calculerScoreTotal() >= (config?.seuil_minimum || 70),
                  'score-defavorable': calculerScoreTotal() < (config?.seuil_minimum || 70)
                }">{{ calculerScoreTotal() }}/{{ config?.score_total_max || 100 }}</strong>
              </div>
              <div class="col-recommendations"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section IV - CONCLUSION -->
      <div class="section section-conclusion">
        <h2 class="section-title">IV - CONCLUSION</h2>

        <div class="conclusion-form">
          <!-- Alerte pertinence éliminatoire -->
          <div v-if="pertinenceEliminatoire" class="alert-eliminatoire">
            <strong>⚠️ CRITÈRE ÉLIMINATOIRE :</strong> Le score de pertinence est inférieur à 3/5.
            L'avis est automatiquement défavorable.
          </div>

          <div class="form-group form-group-inline">
            <label><strong>PROPOSITION:</strong></label>
            <!-- Si pertinence éliminatoire ou score < seuil: automatiquement "Défavorable" -->
            <input
              v-if="pertinenceEliminatoire || calculerScoreTotal() < (config?.seuil_minimum || 70)"
              type="text"
              value="Défavorable"
              readonly
              class="proposition-readonly proposition-defavorable">
            <!-- Sinon: l'évaluateur choisit entre "Favorable" et "Favorable sous conditions" -->
            <select
              v-else
              v-model="evaluationData.proposition"
              class="proposition-select"
              :class="{
                'proposition-favorable': evaluationData.proposition === 'Favorable',
                'proposition-conditionnel': evaluationData.proposition === 'Favorable sous conditions'
              }">
              <option value="" disabled>-- Choisir un avis --</option>
              <option value="Favorable sous conditions">Favorable sous conditions</option>
              <option value="Favorable">Favorable</option>
            </select>
          </div>
          <div class="proposition-help">
            <small class="help-text">
              <span v-if="pertinenceEliminatoire">
                Pertinence < 3/5 = Défavorable (critère éliminatoire)
              </span>
              <span v-else-if="calculerScoreTotal() < (config?.seuil_minimum || 70)">
                Score < {{ config?.seuil_minimum || 70 }} points = Défavorable (automatique)
              </span>
              <span v-else>
                Score ≥ {{ config?.seuil_minimum || 70 }} points = Vous choisissez entre "Favorable" ou "Favorable sous conditions"
              </span>
            </small>
          </div>

          <div class="form-group">
            <label>
              <strong>RECOMMANDATION GÉNÉRALE{{ recommandationObligatoire ? ' *' : '' }}:</strong>
              <span v-if="recommandationObligatoire" class="required-hint">(obligatoire pour un avis défavorable)</span>
            </label>
            <textarea
              v-model="evaluationData.recommandations"
              :placeholder="recommandationObligatoire ? 'Obligatoire — Saisir la recommandation générale...' : 'Saisir les recommandations finales...'"
              rows="5"
              class="recommendations-textarea"
              :class="{ 'field-required': recommandationObligatoire && !evaluationData.recommandations?.trim() }">
            </textarea>
          </div>

          <div class="form-group form-group-inline">
            <label><strong>NOM DE L'ÉVALUATEUR:</strong></label>
            <input
              type="text"
              v-model="evaluationData.evaluateur_nom"
              readonly
              class="evaluateur-input"
              placeholder="Nom de l'évaluateur">
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
      projectInfo: null,
      config: null, // Configuration du formulaire (critères, seuils)
      loadingCriteria: true,
      evaluationData: {
        evaluateur_nom: '',
        criteres: {}, // Sera rempli dynamiquement depuis la config
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
    criteresEvaluation() {
      if (!this.config || !this.config.sections) return []

      // Trouver la section III (évaluation)
      const sectionEval = this.config.sections.find(s => s.type_section === 'evaluation')
      return sectionEval ? sectionEval.criteres : []
    },
    estAssigneAMoi() {
      return this.projectInfo && this.projectInfo.est_assigne_a_moi === true
    },
    pertinenceEliminatoire() {
      // Si le critère "pertinence" a un score < 3/5, c'est éliminatoire
      const pertinence = this.evaluationData.criteres['pertinence'];
      if (!pertinence) return false;
      return pertinence.score > 0 && pertinence.score < 3;
    },
    propositionEffective() {
      if (this.pertinenceEliminatoire) return 'Défavorable';
      const score = this.calculerScoreTotal();
      const seuilMinimum = this.config?.seuil_minimum || 70;
      if (score < seuilMinimum) return 'Défavorable';
      return this.evaluationData.proposition;
    },
    recommandationObligatoire() {
      // Obligatoire si l'avis n'est ni "Favorable" ni "Favorable sous conditions"
      return this.propositionEffective === 'Défavorable';
    },
    peutSauvegarder() {
      if (!this.estAssigneAMoi || !this.evaluationData.evaluateur_nom || this.calculerScoreTotal() <= 0) {
        return false;
      }
      // Si recommandation obligatoire (avis défavorable), vérifier qu'elle est remplie
      if (this.recommandationObligatoire && (!this.evaluationData.recommandations || !this.evaluationData.recommandations.trim())) {
        return false;
      }
      const score = this.calculerScoreTotal();
      const seuilMinimum = this.config?.seuil_minimum || 70;
      // Pertinence éliminatoire ou score < seuil: défavorable automatique, ok
      if (this.pertinenceEliminatoire || score < seuilMinimum) return true;
      // Score >= seuil: doit avoir choisi un avis valide
      return this.evaluationData.proposition === 'Favorable' || this.evaluationData.proposition === 'Favorable sous conditions';
    }
  },
  watch: {
    'evaluationData.criteres': {
      handler() {
        const score = this.calculerScoreTotal()
        const seuilMinimum = this.config?.seuil_minimum || 70

        // Si pertinence éliminatoire ou score < seuil: automatiquement "Défavorable"
        if (this.pertinenceEliminatoire || score < seuilMinimum) {
          this.evaluationData.proposition = 'Défavorable'
        }
        // Si score >= seuil et était "Défavorable": réinitialiser pour forcer le choix
        else if (this.evaluationData.proposition === 'Défavorable') {
          this.evaluationData.proposition = ''
        }
        // Sinon, garder le choix de l'évaluateur
      },
      deep: true
    }
  },
  async mounted() {
    this.projectId = this.$route.params.id

    // Charger la configuration des critères AVANT tout
    await this.chargerConfiguration()

    // Initialiser la structure evaluationData.criteres dynamiquement
    this.initialiserCriteres()

    await this.chargerInfosProjet()
    await this.chargerDonneesProjet()
    await this.chargerEvaluationExistante()
    await this.chargerUtilisateurConnecte()
    this.chargerBrouillon()
  },
  methods: {
    async chargerConfiguration() {
      try {
        this.loadingCriteria = true
        const response = await fetch('/api/formulaire-config/active')

        if (!response.ok) {
          throw new Error('Configuration non trouvée')
        }

        this.config = await response.json()
      } catch (error) {
        console.error('Erreur chargement configuration:', error)
        alert('Erreur lors du chargement de la configuration des critères')
      } finally {
        this.loadingCriteria = false
      }
    },

    initialiserCriteres() {
      // Créer dynamiquement la structure evaluationData.criteres basée sur les critères chargés
      const criteres = {}
      const criteresEval = this.criteresEvaluation || []

      if (criteresEval.length === 0) {
        console.warn('[EvaluationDetaillee] Aucun critère trouvé dans la configuration')
      }

      criteresEval.forEach(critere => {
        if (critere && critere.cle) {
          criteres[critere.cle] = {
            score: 0,
            description: '',
            recommandations: ''
          }
        }
      })
      this.evaluationData.criteres = criteres
    },

    async chargerInfosProjet() {
      try {
        const user = JSON.parse(localStorage.getItem("user") || "null") || {}
        const response = await fetch(`/api/projects?role=${user.role}&username=${user.username}`)
        if (response.ok) {
          const allProjects = await response.json()
          this.projectInfo = allProjects.find(p => p.id === parseInt(this.projectId))

          if (this.projectInfo && !this.projectInfo.est_assigne_a_moi) {
            alert('⚠️ Ce projet est assigné à un autre évaluateur. Vous pouvez consulter les informations mais ne pouvez pas modifier l\'évaluation.')
          }
        }
      } catch (error) {
        console.error('Erreur lors du chargement des infos du projet:', error)
      }
    },

    async chargerDonneesProjet() {
      try {
        const response = await fetch(`/api/projects/${this.projectId}/presentation`)
        if (response.ok) {
          this.presentationData = await response.json()

          // Convertir l'ancien format (checkboxes multiples) vers le nouveau format (choix unique)
          if (this.presentationData.origine_projet && typeof this.presentationData.origine_projet === 'object') {
            // Ancien format avec checkboxes
            if (this.presentationData.origine_projet.maturation) {
              this.presentationData.origine_projet_choix = 'maturation'
            } else if (this.presentationData.origine_projet.offre_spontanee) {
              this.presentationData.origine_projet_choix = 'offre_spontanee'
            } else if (this.presentationData.origine_projet.autres) {
              this.presentationData.origine_projet_choix = 'autres'
            }
          }

          if (this.presentationData.typologie_projet && typeof this.presentationData.typologie_projet === 'object') {
            // Ancien format avec checkboxes
            if (this.presentationData.typologie_projet.productif) {
              this.presentationData.typologie_projet_choix = 'productif'
            } else if (this.presentationData.typologie_projet.appui_production) {
              this.presentationData.typologie_projet_choix = 'appui_production'
            } else if (this.presentationData.typologie_projet.social) {
              this.presentationData.typologie_projet_choix = 'social'
            } else if (this.presentationData.typologie_projet.environnemental) {
              this.presentationData.typologie_projet_choix = 'environnemental'
            }
          }

          // Initialiser les valeurs par défaut si non définies
          if (!this.presentationData.origine_projet_choix) {
            this.presentationData.origine_projet_choix = ''
          }
          if (!this.presentationData.typologie_projet_choix) {
            this.presentationData.typologie_projet_choix = ''
          }
          if (!this.presentationData.origine_projet_autres_precision) {
            this.presentationData.origine_projet_autres_precision = ''
          }
          if (!this.presentationData.organisme_tutelle || this.presentationData.organisme_tutelle.trim() === '') {
            this.presentationData.organisme_tutelle = "MINISTÈRE DE L'ÉCONOMIE, DU PLAN ET DE LA COOPÉRATION"
          }

          // Initialiser les champs des tableaux de présentation détaillée
          if (!this.presentationData.articulation) this.presentationData.articulation = ''
          if (!this.presentationData.axes) this.presentationData.axes = ''
          if (!this.presentationData.objectifs_strategiques) this.presentationData.objectifs_strategiques = ''
          if (!this.presentationData.odd) this.presentationData.odd = ''
          if (!this.presentationData.duree_analyse) this.presentationData.duree_analyse = ''
          if (!this.presentationData.realisation) this.presentationData.realisation = ''
          if (!this.presentationData.exploitation) this.presentationData.exploitation = ''
          if (!this.presentationData.localisation) this.presentationData.localisation = ''
          if (!this.presentationData.parties_prenantes) this.presentationData.parties_prenantes = ''
          if (!this.presentationData.autres_projets_connexes) this.presentationData.autres_projets_connexes = ''
          if (!this.presentationData.objectif_projet) this.presentationData.objectif_projet = ''
          if (!this.presentationData.activites_principales) this.presentationData.activites_principales = ''
          if (!this.presentationData.resultats_attendus) this.presentationData.resultats_attendus = ''

          // Initialiser les dimensions transversales
          if (this.presentationData.changement_climatique_adaptation === undefined) this.presentationData.changement_climatique_adaptation = false
          if (this.presentationData.changement_climatique_attenuation === undefined) this.presentationData.changement_climatique_attenuation = false
          if (this.presentationData.genre === undefined) this.presentationData.genre = false
        } else {
          console.error('Erreur lors du chargement des données du projet')
        }
      } catch (error) {
        console.error('Erreur:', error)
      }
    },

    async chargerUtilisateurConnecte() {
      try {
        const userStr = localStorage.getItem('user')
        if (userStr) {
          const user = JSON.parse(userStr)
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

          // Si c'est une fiche archivée, ne pas pré-remplir
          if (fiche.archived) {
            console.log('Fiche archivée trouvée - pas de pré-remplissage')
            return
          }

          // Si la fiche n'a pas d'ID (structure par défaut), ne pas pré-remplir
          if (!fiche.id) {
            console.log('Aucune fiche existante - formulaire vierge')
            return
          }

          console.log('[EvaluationDetaillee] Chargement fiche existante:', fiche)

          // Pré-remplir les critères d'évaluation
          if (fiche.criteres) {
            for (const [key, value] of Object.entries(fiche.criteres)) {
              if (this.evaluationData.criteres[key]) {
                this.evaluationData.criteres[key].score = value.score || 0
                this.evaluationData.criteres[key].description = value.description || ''
                this.evaluationData.criteres[key].recommandations = value.recommandations || ''
              }
            }
          }

          // Pré-remplir la proposition et recommandations
          if (fiche.proposition) {
            this.evaluationData.proposition = fiche.proposition
          }
          if (fiche.recommandations) {
            this.evaluationData.recommandations = fiche.recommandations
          }

          // Pré-remplir l'origine du projet
          if (fiche.origine_projet) {
            // Si c'est une string (ancien format ou valeur directe)
            if (typeof fiche.origine_projet === 'string') {
              this.presentationData.origine_projet_choix = fiche.origine_projet
            }
            // Si c'est un objet avec les clés maturation/offre_spontanee/autres
            else if (typeof fiche.origine_projet === 'object') {
              if (fiche.origine_projet.maturation) {
                this.presentationData.origine_projet_choix = 'maturation'
              } else if (fiche.origine_projet.offre_spontanee) {
                this.presentationData.origine_projet_choix = 'offre_spontanee'
              } else if (fiche.origine_projet.autres) {
                this.presentationData.origine_projet_choix = 'autres'
              }
            }
          }

          // Pré-remplir les dimensions transversales
          if (fiche.cc_adaptation !== undefined) {
            this.presentationData.changement_climatique_adaptation = fiche.cc_adaptation || false
          }
          if (fiche.cc_attenuation !== undefined) {
            this.presentationData.changement_climatique_attenuation = fiche.cc_attenuation || false
          }
          if (fiche.genre !== undefined) {
            this.presentationData.genre = fiche.genre || false
          }

          // Pré-remplir les champs de présentation du projet
          if (fiche.articulation) this.presentationData.articulation = fiche.articulation
          if (fiche.axes) this.presentationData.axes = fiche.axes
          if (fiche.objectifs_strategiques) this.presentationData.objectifs_strategiques = fiche.objectifs_strategiques
          if (fiche.odd) this.presentationData.odd = fiche.odd
          if (fiche.duree_analyse) this.presentationData.duree_analyse = fiche.duree_analyse
          if (fiche.realisation) this.presentationData.realisation = fiche.realisation
          if (fiche.exploitation) this.presentationData.exploitation = fiche.exploitation
          if (fiche.localisation) this.presentationData.localisation = fiche.localisation
          if (fiche.parties_prenantes) this.presentationData.parties_prenantes = fiche.parties_prenantes
          if (fiche.autres_projets_connexes) this.presentationData.autres_projets_connexes = fiche.autres_projets_connexes
          if (fiche.objectif_projet) this.presentationData.objectif_projet = fiche.objectif_projet
          if (fiche.activites_principales) this.presentationData.activites_principales = fiche.activites_principales
          if (fiche.resultats_attendus) this.presentationData.resultats_attendus = fiche.resultats_attendus

          console.log('[EvaluationDetaillee] Données pré-remplies avec succès')
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
      // Pertinence < 3/5 = éliminatoire
      if (this.pertinenceEliminatoire) return 'Défavorable'
      const score = this.calculerScoreTotal()
      const seuilMinimum = this.config?.seuil_minimum || 70
      if (score < seuilMinimum) return 'Défavorable'
      return this.evaluationData.proposition || 'Favorable'
    },

    getPropositionNom() {
      return this.getAppreciation()
    },

    getPropositionAutomatique() {
      // Cette méthode retourne la proposition basée uniquement sur le score
      // Note: avec le nouveau système, au-dessus du seuil, c'est un choix manuel
      const score = this.calculerScoreTotal()
      const seuilMinimum = this.config?.seuil_minimum || 70
      return score >= seuilMinimum ? this.evaluationData.proposition || 'Favorable' : 'Défavorable'
    },

    formatCoutWithSpaces(value) {
      if (!value) return ''
      // Convertir en string et supprimer les espaces existants
      const numStr = String(value).replace(/\s/g, '')
      // Vérifier si c'est un nombre valide
      if (!/^\d+$/.test(numStr)) return value
      // Ajouter les espaces tous les 3 chiffres de droite à gauche
      return numStr.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
    },

    updateCout(event) {
      // Récupérer la valeur sans les espaces et la stocker dans le modèle
      const value = event.target.value.replace(/\s/g, '')
      this.presentationData.cout_estimatif = value
    },

    async sauvegarder() {
      if (!this.peutSauvegarder) return

      // Demander confirmation avant de finaliser l'évaluation
      const confirmation = confirm(
        "⚠️ Confirmer la finalisation de l'évaluation ?\n\n" +
        "Une fois finalisée, l'évaluation sera soumise et un PDF sera généré.\n" +
        "Cette action est irréversible.\n\n" +
        "Voulez-vous continuer ?"
      )

      if (!confirmation) {
        return // L'utilisateur a annulé
      }

      this.loading = true
      try {
        // Inclure les données de présentation (origine, dimensions transversales et tableaux détaillés du projet)
        const dataToSend = {
          ...this.evaluationData,
          // Champs éditables de Section I
          intitule: this.presentationData?.intitule || '',
          secteur: this.presentationData?.secteur || '',
          poles: this.presentationData?.poles || '',
          cout_estimatif: this.presentationData?.cout_estimatif || '',
          organisme_tutelle: this.presentationData?.organisme_tutelle || '',
          description: this.presentationData?.description || '',
          // Classification
          origine_projet_choix: this.presentationData?.origine_projet_choix || '',
          // Dimensions transversales
          changement_climatique_adaptation: this.presentationData?.changement_climatique_adaptation || false,
          changement_climatique_attenuation: this.presentationData?.changement_climatique_attenuation || false,
          genre: this.presentationData?.genre || false,
          // Tableaux de présentation détaillée
          articulation: this.presentationData?.articulation || '',
          axes: this.presentationData?.axes || '',
          objectifs_strategiques: this.presentationData?.objectifs_strategiques || '',
          odd: this.presentationData?.odd || '',
          duree_analyse: this.presentationData?.duree_analyse || '',
          realisation: this.presentationData?.realisation || '',
          exploitation: this.presentationData?.exploitation || '',
          localisation: this.presentationData?.localisation || '',
          parties_prenantes: this.presentationData?.parties_prenantes || '',
          autres_projets_connexes: this.presentationData?.autres_projets_connexes || '',
          objectif_projet: this.presentationData?.objectif_projet || '',
          activites_principales: this.presentationData?.activites_principales || '',
          resultats_attendus: this.presentationData?.resultats_attendus || ''
        }

        const response = await fetch(`/api/projects/${this.projectId}/fiche-evaluation`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(dataToSend)
        })

        if (response.ok) {
          const result = await response.json()
          this.evaluationSauvegardee = true
          this.$emit('evaluation-saved', result)

          this.supprimerBrouillon()

          alert('Évaluation finalisée avec succès!')

          this.$router.push('/evaluateur')
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
        const API_BASE_URL = import.meta.env.VITE_API_URL || ''
        const url = `${API_BASE_URL}/api/projects/${this.projectId}/fiche-evaluation/pdf`
        window.open(url, '_blank')
      } catch (error) {
        console.error('Erreur génération PDF:', error)
        alert('Erreur lors de la génération du PDF')
      }
    },

    retour() {
      this.$router.go(-1)
    },

    retourDashboard() {
      this.$router.go(-1)
    },

    async sauvegarderBrouillon() {
      this.loading = true
      try {
        const brouillonKey = `evaluation-brouillon-${this.projectId}`
        const brouillonData = {
          ...this.evaluationData,
          derniereSauvegarde: new Date().toISOString(),
          estBrouillon: true
        }
        localStorage.setItem(brouillonKey, JSON.stringify(brouillonData))

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

          const userStr = localStorage.getItem('user')
          if (userStr) {
            const user = JSON.parse(userStr)
            const currentEvaluateurNom = user.display_name || user.username || user.nom || ''

            if (brouillonData.evaluateur_nom !== currentEvaluateurNom) {
              console.log('Brouillon d\'un autre évaluateur détecté - suppression')
              localStorage.removeItem(brouillonKey)
              return
            }
          }

          if (brouillonData.estBrouillon) {
            const restaurer = confirm(`Un brouillon d'évaluation a été trouvé (sauvegardé le ${new Date(brouillonData.derniereSauvegarde).toLocaleString()}). Voulez-vous le restaurer ?`)
            if (restaurer) {
              this.evaluationData = { ...brouillonData }
              this.estBrouillon = true
              this.derniereSauvegarde = new Date(brouillonData.derniereSauvegarde)
              alert('Brouillon restauré ! Vous pouvez continuer votre évaluation.')
            } else {
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
    },

    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      const options = { year: 'numeric', month: 'long' }
      return date.toLocaleDateString('fr-FR', options)
    }
  }
}
</script>

<style scoped>
.evaluation-container {
  position: relative;
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  min-height: 100vh;
}

.header-section {
  text-align: center;
  margin-bottom: 40px;
}

.dgppe-header {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  margin-bottom: 30px;
  padding: 25px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.ministere-info {
  text-align: center;
  width: 100%;
}

.ministere-info h2 {
  font-size: 18px;
  font-weight: bold;
  margin: 0;
  color: #1a202c;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.ministere-info h3 {
  font-size: 15px;
  font-weight: 600;
  margin: 8px 0;
  color: #2d3748;
  text-align: center;
}

.ministere-info h4 {
  font-size: 13px;
  font-weight: normal;
  margin: 8px 0 0;
  color: #718096;
  text-align: center;
}

.form-title {
  font-size: 28px;
  font-weight: bold;
  color: #1a202c;
  margin: 25px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.version-info {
  text-align: center;
  margin: 15px 0 25px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-radius: 8px;
  font-size: 13px;
  color: #1565c0;
  box-shadow: 0 2px 8px rgba(21, 101, 192, 0.15);
}

.version-label {
  font-weight: 600;
  margin-right: 5px;
}

.version-value {
  font-style: italic;
  color: #0d47a1;
  font-weight: 500;
}

.section {
  margin-bottom: 35px;
  border: none;
  border-radius: 12px;
  overflow: hidden;
  background: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.section:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.12);
}

.section-title {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  padding: 18px 20px;
  margin: 0;
  font-size: 19px;
  font-weight: bold;
  text-align: center;
}

.section-presentation {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.project-info {
  padding: 25px;
}

.project-title {
  color: #1a202c;
  margin-bottom: 25px;
  font-size: 19px;
  font-weight: 600;
  text-align: center;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.info-item {
  padding: 15px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.info-item:hover {
  border-color: #cbd5e0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.info-item strong {
  color: #2d3748;
  font-weight: 600;
  font-size: 13px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

/* Champs éditables dans la section présentation */
.info-item-editable {
  padding: 15px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.info-item-editable:hover {
  border-color: #cbd5e0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.info-item-editable strong {
  color: #2d3748;
  font-weight: 600;
  font-size: 13px;
  display: block;
  margin-bottom: 8px;
}

.info-item-editable.full-width {
  grid-column: 1 / -1;
}

.input-text {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  font-size: 13px;
  font-family: inherit;
  transition: all 0.2s ease;
  background: white;
}

.input-text:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.input-text::placeholder {
  color: #a0aec0;
  font-style: italic;
}

.textarea-text {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  font-size: 13px;
  font-family: inherit;
  line-height: 1.6;
  resize: vertical;
  transition: all 0.2s ease;
  background: white;
  min-height: 80px;
}

.textarea-text:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.textarea-text::placeholder {
  color: #a0aec0;
  font-style: italic;
}

/* Section intitulé du projet - Pleine largeur */
.intitule-section {
  margin-bottom: 20px;
  padding: 0;
  text-align: center;
}

.intitule-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #2d3748;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
  text-align: center;
}

.input-intitule-fullwidth {
  width: 100%;
  min-height: 45px;
  padding: 10px 14px;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.5;
  color: #1a202c;
  background: white;
  border: 2px solid #cbd5e0;
  border-radius: 6px;
  resize: vertical;
  font-family: inherit;
  transition: all 0.2s ease;
  text-align: center;
}

.input-intitule-fullwidth:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.input-intitule-fullwidth::placeholder {
  color: #a0aec0;
  font-style: italic;
  text-align: center;
}

.checkbox-group {
  display: flex;
  gap: 20px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.checkbox-group label {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 6px;
  transition: all 0.2s ease;
  background: #f7fafc;
}

.checkbox-group label:hover {
  background: #edf2f7;
}

.checkbox-group input[type="checkbox"] {
  margin: 0;
  cursor: pointer;
  width: 16px;
  height: 16px;
}

/* Grille de classification (Origine + Dimensions transversales) */
.classification-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 25px;
}

.classification-section {
  padding: 20px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.classification-section:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.classification-header {
  font-weight: 700;
  font-size: 14px;
  color: #2c3e50;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 3px solid #3498db;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Origine du projet - radio buttons verticaux */
.radio-group-vertical {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.radio-group-vertical label {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 10px 15px;
  border-radius: 8px;
  transition: all 0.2s ease;
  background: #f8f9fa;
  border: 2px solid transparent;
}

.radio-group-vertical label:hover {
  background: #e3f2fd;
  border-color: #90caf9;
}

.radio-group-vertical input[type="radio"] {
  margin: 0;
  cursor: pointer;
  width: 18px;
  height: 18px;
  accent-color: #3498db;
}

.autres-precisions-inline {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

/* Dimensions transversales */
.dimensions-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.dimension-block {
  padding: 12px 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.dimension-subtitle {
  font-weight: 600;
  font-size: 13px;
  color: #34495e;
  margin-bottom: 10px;
  text-transform: capitalize;
}

.checkbox-group-compact {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-group-compact label {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 6px;
  transition: all 0.2s ease;
  background: white;
}

.checkbox-group-compact label:hover {
  background: #e3f2fd;
  transform: translateX(3px);
}

.checkbox-group-compact input[type="checkbox"] {
  margin: 0;
  cursor: pointer;
  width: 18px;
  height: 18px;
  accent-color: #3498db;
}

/* Anciens styles - conservés pour compatibilité */
.dimensions-transversales-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 15px;
}

.dimension-group {
  padding: 15px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.dimension-title {
  font-weight: 600;
  font-size: 13px;
  color: #2d3748;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 2px solid #cbd5e0;
}

.dimension-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dimension-options label {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 6px;
  transition: all 0.2s ease;
  background: white;
}

.dimension-options label:hover {
  background: #e3f2fd;
  transform: translateX(3px);
}

.dimension-options input[type="checkbox"] {
  margin: 0;
  cursor: pointer;
  width: 18px;
  height: 18px;
}

.radio-group {
  display: flex;
  gap: 20px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.radio-group label {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 6px;
  transition: all 0.2s ease;
  background: #f7fafc;
}

.radio-group label:hover {
  background: #edf2f7;
}

.radio-group input[type="radio"] {
  margin: 0;
  cursor: pointer;
  width: 16px;
  height: 16px;
}

.autres-precisions {
  margin-top: 12px;
}

.autres-precisions .input-text {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 13px;
  transition: all 0.2s ease;
  background: white;
}

.autres-precisions .input-text:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.criteria-table {
  display: grid;
  grid-template-columns: 2fr 3fr 1fr 2fr;
  gap: 1px;
  background: #cbd5e0;
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  display: contents;
}

.table-header > div {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  color: white;
  padding: 18px 15px;
  font-weight: 600;
  text-align: center;
  font-size: 13px;
  letter-spacing: 0.5px;
}

.criteria-row {
  display: contents;
}

.criteria-row > div {
  background: white;
  padding: 18px 15px;
  border-bottom: 1px solid #e2e8f0;
  transition: background 0.2s ease;
}

.criteria-row:hover > div {
  background: #f8fafc;
}

.criteria-row .col-criteria {
  font-weight: 600;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%) !important;
  color: #2d3748;
}

.table-header .col-criteria {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
}

.score-max {
  font-size: 12px;
  color: #718096;
  display: block;
  margin-top: 6px;
  font-weight: 500;
}

.score-input {
  width: 85px;
  padding: 10px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  text-align: center;
  font-size: 16px;
  font-weight: 700;
  color: #2d3748;
  transition: all 0.2s ease;
  background: white;
}

.score-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.15);
  transform: scale(1.05);
}

.total-row > div {
  background: #e8f5e8 !important;
  font-weight: bold;
}

.total-score {
  color: #27ae60;
  font-size: 18px;
}

.score-acceptable {
  color: #2d7a2d !important;
}

.score-defavorable {
  color: #dc2626 !important;
}

/* Style pour le select de proposition */
.proposition-select {
  padding: 10px 15px;
  font-size: 15px;
  font-weight: 600;
  border: 2px solid #cbd5e1;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.proposition-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.no-description,
.no-recommandations {
  color: #95a5a6;
  font-style: italic;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

textarea {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  resize: vertical;
  font-family: inherit;
  font-size: 13px;
  line-height: 1.6;
  transition: all 0.2s ease;
  background: white;
}

textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

textarea::placeholder {
  color: #a0aec0;
  font-style: italic;
}

.conclusion-form, .evaluateur-info {
  background: white;
  padding: 25px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.section-evaluateur {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border: none;
  margin-top: 20px;
}

.section-evaluateur .evaluateur-info {
  background: linear-gradient(135deg, #ffffff 0%, #e3f2fd 100%);
  border: 2px solid #64b5f6;
}

.evaluateur-input[readonly] {
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  color: #4a5568;
  cursor: not-allowed;
  border: 2px solid #cbd5e0;
}

.help-text {
  color: #718096;
  font-style: italic;
  margin-top: 8px;
  font-size: 12px;
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #2d3748;
  font-size: 13px;
}

.form-group-inline {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 12px;
}

.form-group-inline label {
  flex-shrink: 0;
  margin: 0;
}

.proposition-help {
  margin-bottom: 15px;
}

.proposition-readonly {
  flex: 0 0 auto;
  width: 300px;
  padding: 10px 15px;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-weight: bold;
  font-size: 15px;
  background-color: #f8f9fa;
  cursor: not-allowed;
  text-align: center;
}

.proposition-favorable {
  border-color: #2d7a2d;
  background-color: #e8f5e9;
  color: #2d7a2d;
}

.proposition-conditionnel {
  border-color: #d97706;
  background-color: #fff7ed;
  color: #d97706;
}

.proposition-defavorable {
  border-color: #dc2626;
  background-color: #fee;
  color: #dc2626;
}

.alert-eliminatoire {
  background: #fef2f2;
  border: 2px solid #dc2626;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
  color: #991b1b;
  font-size: 14px;
}

.required-hint {
  font-weight: 400;
  font-size: 12px;
  color: #dc2626;
  margin-left: 6px;
}

.field-required {
  border-color: #dc2626 !important;
  background: #fef2f2 !important;
}

.evaluateur-input {
  width: 100%;
  max-width: 350px;
  padding: 10px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  font-size: 13px;
  transition: all 0.2s ease;
}

.evaluateur-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.recommendations-textarea {
  width: 100%;
  min-height: 100px;
}

.actions-section {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 40px;
  padding: 30px 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.actions-group {
  display: flex;
  gap: 15px;
}

.btn {
  padding: 14px 28px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  letter-spacing: 0.3px;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.btn-draft {
  background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
  color: white;
}

.btn-draft:hover:not(:disabled) {
  background: linear-gradient(135deg, #7f8c8d 0%, #6c7a7a 100%);
}

.btn-primary {
  background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #229954 0%, #1e8449 100%);
}

.btn-secondary {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: linear-gradient(135deg, #2980b9 0%, #21618c 100%);
}

.btn-outline {
  background: white;
  color: #3498db;
  border: 2px solid #3498db;
}

.btn-outline:hover:not(:disabled) {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  border-color: #3498db;
}

.btn-retour {
  background: white;
  color: #3498db;
  border: 2px solid #3498db;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn-retour:hover {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.navigation-section {
  margin-bottom: 20px;
  text-align: left;
}

.progress-indicator {
  position: fixed;
  top: 200px;
  right: 20px;
  background: white;
  padding: 15px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  border: 2px solid #3498db;
  z-index: 100;
}

.score-summary {
  text-align: center;
}

.score-current {
  font-size: 24px;
  font-weight: bold;
}

.score-total {
  font-size: 18px;
  color: #7f8c8d;
}

.score-appreciation {
  display: block;
  font-size: 12px;
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
  flex-wrap: wrap;
  gap: 12px;
}

.numero-projet-badge {
  display: inline-block;
  background: #007bff;
  color: white;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 18px;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
}

.badge-prioritaire-fiche {
  display: inline-block;
  background: #fef3c7;
  color: #d97706;
  border: 2px solid #f59e0b;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.5px;
  margin-left: 8px;
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

.readonly-mode .radio-group input[type="radio"] {
  pointer-events: none;
}

.readonly-mode .autres-precisions .input-text {
  pointer-events: none;
  background-color: #f5f5f5;
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

/* Tableaux de présentation détaillée */
.project-details-table {
  margin-top: 25px;
}

.project-details-table table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
  background: white;
  border: none;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.project-details-table th {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  color: white;
  padding: 15px 12px;
  text-align: center;
  font-weight: 600;
  font-size: 13px;
  border: none;
  letter-spacing: 0.5px;
}

.project-details-table td {
  padding: 12px;
  border: 1px solid #e2e8f0;
  vertical-align: top;
  background: white;
}

.project-details-table td:hover {
  background: #f8fafc;
}

.project-details-table textarea {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  font-family: inherit;
  font-size: 13px;
  resize: vertical;
  transition: all 0.2s ease;
  background: white;
  min-height: 60px;
}

.project-details-table textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}
</style>
