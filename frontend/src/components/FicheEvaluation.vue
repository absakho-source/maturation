<template>
  <div class="fiche-evaluation">
    <div class="header-fiche">
      <div class="logo-header">
        <img src="/logo-dgppe.png" alt="DGPPE" class="logo-dgppe">
        <div class="header-text">
          <h2>FICHE D'ÉVALUATION DE PROJET</h2>
          <p class="sous-titre">Direction Générale de la Planification, des Politiques Économiques et des Programmes</p>
        </div>
      </div>
    </div>

    <form @submit.prevent="soumettreEvaluation" class="evaluation-form">
      <!-- 1. INFORMATIONS GÉNÉRALES -->
      <section class="section-info">
        <h3><i class="fas fa-info-circle"></i> 1. INFORMATIONS GÉNÉRALES</h3>
        <div class="info-grid">
          <div class="info-item">
            <label>Numéro du projet :</label>
            <span class="info-value">{{ project.numero_projet || 'En attente' }}</span>
          </div>
          <div class="info-item">
            <label>Titre du projet :</label>
            <span class="info-value">{{ project.titre }}</span>
          </div>
          <div class="info-item">
            <label>Soumissionnaire :</label>
            <span class="info-value">{{ project.auteur_nom }}</span>
          </div>
          <div class="info-item">
            <label>Pôle territorial :</label>
            <span class="info-value">{{ project.poles }}</span>
          </div>
          <div class="info-item">
            <label>Secteur d'activité :</label>
            <span class="info-value">{{ project.secteur }}</span>
          </div>
          <div class="info-item">
            <label>Coût estimatif :</label>
            <span class="info-value">{{ formatMoney(project.cout_estimatif) }}</span>
          </div>
        </div>
      </section>

      <!-- 2. ÉVALUATEUR -->
      <section class="section-evaluateur">
        <h3><i class="fas fa-user-check"></i> 2. ÉVALUATEUR</h3>
        <div class="info-grid">
          <div class="info-item">
            <label>Nom de l'évaluateur :</label>
            <span class="info-value">{{ fiche.evaluateur_nom }}</span>
          </div>
          <div class="info-item">
            <label>Date d'évaluation :</label>
            <span class="info-value">{{ formatDate(new Date()) }}</span>
          </div>
          <div class="info-item">
            <label>Référence de la fiche :</label>
            <span class="info-value">{{ fiche.reference_fiche }}</span>
          </div>
        </div>
      </section>

      <!-- 3. CRITÈRES D'ÉVALUATION -->
      <section class="section-criteres">
        <h3><i class="fas fa-clipboard-check"></i> 3. CRITÈRES D'ÉVALUATION</h3>

        <!-- A. Pertinence et alignement stratégique -->
        <div class="critere-section">
          <h4>A. PERTINENCE ET ALIGNEMENT STRATÉGIQUE (20 points)</h4>
          
          <div class="critere-item">
            <label>3.1. Alignement avec les priorités nationales (0-5 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="5" v-model.number="fiche.alignement_national" class="slider">
              <span class="score">{{ fiche.alignement_national }}/5</span>
            </div>
            <p class="critere-desc">Cohérence avec les plans de développement nationaux et contribution aux ODD</p>
          </div>

          <div class="critere-item">
            <label>3.2. Pertinence territoriale (0-5 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="5" v-model.number="fiche.pertinence_territoriale" class="slider">
              <span class="score">{{ fiche.pertinence_territoriale }}/5</span>
            </div>
            <p class="critere-desc">Adéquation avec les besoins du pôle territorial et impact sur le développement local</p>
          </div>

          <div class="critere-item">
            <label>3.3. Innovation et valeur ajoutée (0-5 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="5" v-model.number="fiche.innovation_valeur" class="slider">
              <span class="score">{{ fiche.innovation_valeur }}/5</span>
            </div>
            <p class="critere-desc">Caractère innovant de l'approche et différenciation par rapport aux projets existants</p>
          </div>

          <div class="critere-item">
            <label>3.4. Urgence et priorité (0-5 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="5" v-model.number="fiche.urgence_priorite" class="slider">
              <span class="score">{{ fiche.urgence_priorite }}/5</span>
            </div>
            <p class="critere-desc">Caractère urgent du besoin et niveau de priorité pour la population cible</p>
          </div>

          <div class="sous-total">
            <strong>Sous-total A: {{ sousTotal.pertinence }}/20 points</strong>
          </div>
        </div>

        <!-- B. Faisabilité technique -->
        <div class="critere-section">
          <h4>B. FAISABILITÉ TECHNIQUE (20 points)</h4>
          
          <div class="critere-item">
            <label>3.5. Solidité technique (0-10 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="10" v-model.number="fiche.solidite_technique" class="slider">
              <span class="score">{{ fiche.solidite_technique }}/10</span>
            </div>
            <p class="critere-desc">Qualité de l'approche technique et maîtrise des technologies proposées</p>
          </div>

          <div class="critere-item">
            <label>3.6. Capacités de mise en œuvre (0-5 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="5" v-model.number="fiche.capacites_mise_oeuvre" class="slider">
              <span class="score">{{ fiche.capacites_mise_oeuvre }}/5</span>
            </div>
            <p class="critere-desc">Compétences de l'équipe projet et expérience similaire du soumissionnaire</p>
          </div>

          <div class="critere-item">
            <label>3.7. Gestion des risques (0-5 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="5" v-model.number="fiche.gestion_risques" class="slider">
              <span class="score">{{ fiche.gestion_risques }}/5</span>
            </div>
            <p class="critere-desc">Identification des risques et stratégies d'atténuation</p>
          </div>

          <div class="sous-total">
            <strong>Sous-total B: {{ sousTotal.technique }}/20 points</strong>
          </div>
        </div>

        <!-- C. Viabilité financière -->
        <div class="critere-section">
          <h4>C. VIABILITÉ FINANCIÈRE (20 points)</h4>
          
          <div class="critere-item">
            <label>3.8. Réalisme du budget (0-10 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="10" v-model.number="fiche.realisme_budget" class="slider">
              <span class="score">{{ fiche.realisme_budget }}/10</span>
            </div>
            <p class="critere-desc">Cohérence des coûts et justification des postes budgétaires</p>
          </div>

          <div class="critere-item">
            <label>3.9. Rapport coût/bénéfice (0-5 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="5" v-model.number="fiche.rapport_cout_benefice" class="slider">
              <span class="score">{{ fiche.rapport_cout_benefice }}/5</span>
            </div>
            <p class="critere-desc">Efficience économique et retour sur investissement</p>
          </div>

          <div class="critere-item">
            <label>3.10. Durabilité financière (0-5 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="5" v-model.number="fiche.durabilite_financiere" class="slider">
              <span class="score">{{ fiche.durabilite_financiere }}/5</span>
            </div>
            <p class="critere-desc">Modèle de financement et pérennité des ressources</p>
          </div>

          <div class="sous-total">
            <strong>Sous-total C: {{ sousTotal.financiere }}/20 points</strong>
          </div>
        </div>

        <!-- D. Impact et bénéfices -->
        <div class="critere-section">
          <h4>D. IMPACT ET BÉNÉFICES (20 points)</h4>
          
          <div class="critere-item">
            <label>3.11. Impact social (0-5 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="5" v-model.number="fiche.impact_social" class="slider">
              <span class="score">{{ fiche.impact_social }}/5</span>
            </div>
            <p class="critere-desc">Nombre de bénéficiaires directs/indirects et amélioration des conditions de vie</p>
          </div>

          <div class="critere-item">
            <label>3.12. Impact économique (0-5 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="5" v-model.number="fiche.impact_economique" class="slider">
              <span class="score">{{ fiche.impact_economique }}/5</span>
            </div>
            <p class="critere-desc">Création d'emplois et dynamisation de l'économie locale</p>
          </div>

          <div class="critere-item">
            <label>3.13. Impact environnemental (0-5 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="5" v-model.number="fiche.impact_environnemental" class="slider">
              <span class="score">{{ fiche.impact_environnemental }}/5</span>
            </div>
            <p class="critere-desc">Respect de l'environnement et contribution au développement durable</p>
          </div>

          <div class="critere-item">
            <label>3.14. Effet multiplicateur (0-5 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="5" v-model.number="fiche.effet_multiplicateur" class="slider">
              <span class="score">{{ fiche.effet_multiplicateur }}/5</span>
            </div>
            <p class="critere-desc">Potentiel de réplication et effet d'entraînement</p>
          </div>

          <div class="sous-total">
            <strong>Sous-total D: {{ sousTotal.impact }}/20 points</strong>
          </div>
        </div>

        <!-- E. Gestion et gouvernance -->
        <div class="critere-section">
          <h4>E. GESTION ET GOUVERNANCE (20 points)</h4>
          
          <div class="critere-item">
            <label>3.15. Organisation du projet (0-5 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="5" v-model.number="fiche.organisation_projet" class="slider">
              <span class="score">{{ fiche.organisation_projet }}/5</span>
            </div>
            <p class="critere-desc">Structure de gouvernance et mécanismes de pilotage</p>
          </div>

          <div class="critere-item">
            <label>3.16. Planification (0-5 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="5" v-model.number="fiche.planification" class="slider">
              <span class="score">{{ fiche.planification }}/5</span>
            </div>
            <p class="critere-desc">Chronogramme réaliste et jalons et livrables clairs</p>
          </div>

          <div class="critere-item">
            <label>3.17. Suivi-évaluation (0-5 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="5" v-model.number="fiche.suivi_evaluation" class="slider">
              <span class="score">{{ fiche.suivi_evaluation }}/5</span>
            </div>
            <p class="critere-desc">Indicateurs de performance et mécanismes de suivi</p>
          </div>

          <div class="critere-item">
            <label>3.18. Transparence et redevabilité (0-5 points)</label>
            <div class="slider-container">
              <input type="range" min="0" max="5" v-model.number="fiche.transparence_redevabilite" class="slider">
              <span class="score">{{ fiche.transparence_redevabilite }}/5</span>
            </div>
            <p class="critere-desc">Mécanismes de transparence et reddition de comptes</p>
          </div>

          <div class="sous-total">
            <strong>Sous-total E: {{ sousTotal.gouvernance }}/20 points</strong>
          </div>
        </div>
      </section>

      <!-- 4. ÉVALUATION DÉTAILLÉE -->
      <section class="section-evaluation">
        <h3><i class="fas fa-edit"></i> 4. ÉVALUATION DÉTAILLÉE</h3>
        
        <div class="textarea-group">
          <label for="points_forts">Points forts identifiés :</label>
          <textarea 
            id="points_forts"
            v-model="fiche.points_forts" 
            maxlength="500" 
            placeholder="Décrivez les principaux atouts du projet..."
            rows="3"
          ></textarea>
          <small>{{ fiche.points_forts?.length || 0 }}/500 caractères</small>
        </div>

        <div class="textarea-group">
          <label for="points_faibles">Points faibles et risques :</label>
          <textarea 
            id="points_faibles"
            v-model="fiche.points_faibles" 
            maxlength="500" 
            placeholder="Identifiez les faiblesses et risques potentiels..."
            rows="3"
          ></textarea>
          <small>{{ fiche.points_faibles?.length || 0 }}/500 caractères</small>
        </div>

        <div class="textarea-group">
          <label for="recommandations">Recommandations d'amélioration :</label>
          <textarea 
            id="recommandations"
            v-model="fiche.recommandations" 
            maxlength="500" 
            placeholder="Suggérez des améliorations spécifiques..."
            rows="3"
          ></textarea>
          <small>{{ fiche.recommandations?.length || 0 }}/500 caractères</small>
        </div>

        <div class="textarea-group">
          <label for="conditions_particulieres">Conditions particulières (si applicable) :</label>
          <textarea 
            id="conditions_particulieres"
            v-model="fiche.conditions_particulieres" 
            maxlength="300" 
            placeholder="Conditions spéciales à respecter..."
            rows="2"
          ></textarea>
          <small>{{ fiche.conditions_particulieres?.length || 0 }}/300 caractères</small>
        </div>
      </section>

      <!-- 5. SYNTHÈSE -->
      <section class="section-synthese">
        <h3><i class="fas fa-chart-line"></i> 5. SYNTHÈSE</h3>
        
        <div class="score-total">
          <h4>Score total : <span class="score-highlight">{{ scoreTotal }}/100 points</span></h4>
          <div class="score-bar">
            <div class="score-fill" :style="{ width: scoreTotal + '%' }"></div>
          </div>
        </div>

        <div class="appreciation-globale">
          <h4>Appréciation globale :</h4>
          <div class="radio-group">
            <label class="radio-item" :class="{ active: appreciationGlobale === 'excellent' }">
              <input type="radio" value="excellent" v-model="fiche.appreciation_globale" disabled>
              <span class="radio-label">Excellent (90-100 points) - Projet remarquable, prêt pour validation</span>
            </label>
            <label class="radio-item" :class="{ active: appreciationGlobale === 'tres_bien' }">
              <input type="radio" value="tres_bien" v-model="fiche.appreciation_globale" disabled>
              <span class="radio-label">Très bien (80-89 points) - Projet de qualité, recommandé avec réserves mineures</span>
            </label>
            <label class="radio-item" :class="{ active: appreciationGlobale === 'bien' }">
              <input type="radio" value="bien" v-model="fiche.appreciation_globale" disabled>
              <span class="radio-label">Bien (70-79 points) - Projet acceptable, nécessite des améliorations</span>
            </label>
            <label class="radio-item" :class="{ active: appreciationGlobale === 'passable' }">
              <input type="radio" value="passable" v-model="fiche.appreciation_globale" disabled>
              <span class="radio-label">Passable (60-69 points) - Projet acceptable avec réserves importantes</span>
            </label>
            <label class="radio-item" :class="{ active: appreciationGlobale === 'insuffisant' }">
              <input type="radio" value="insuffisant" v-model="fiche.appreciation_globale" disabled>
              <span class="radio-label">Insuffisant (< 60 points) - Projet non recommandé en l'état</span>
            </label>
          </div>
        </div>

        <div class="avis-final">
          <h4>Avis final de l'évaluateur :</h4>
          <div class="radio-group">
            <label class="radio-item">
              <input type="radio" value="favorable" v-model="fiche.avis_final" required>
              <span class="radio-label favorable">Favorable - Le projet est recommandé pour validation</span>
            </label>
            <label class="radio-item">
              <input type="radio" value="favorable_sous_conditions" v-model="fiche.avis_final" required>
              <span class="radio-label conditionnel">Favorable sous conditions - Le projet est recommandé sous réserve des améliorations suggérées</span>
            </label>
            <label class="radio-item">
              <input type="radio" value="defavorable" v-model="fiche.avis_final" required>
              <span class="radio-label defavorable">Défavorable - Le projet n'est pas recommandé pour validation</span>
            </label>
          </div>
        </div>

        <div class="textarea-group">
          <label for="commentaires_finaux">Commentaires finaux :</label>
          <textarea 
            id="commentaires_finaux"
            v-model="fiche.commentaires_finaux" 
            maxlength="1000" 
            placeholder="Ajoutez vos commentaires finaux et recommandations générales..."
            rows="4"
            required
          ></textarea>
          <small>{{ fiche.commentaires_finaux?.length || 0 }}/1000 caractères</small>
        </div>
      </section>

      <!-- ACTIONS -->
      <div class="actions-section">
        <button type="button" @click="sauvegarderBrouillon" class="btn btn-secondary">
          <i class="fas fa-save"></i> Sauvegarder le brouillon
        </button>
        <button type="submit" class="btn btn-primary" :disabled="!formulaireValide">
          <i class="fas fa-file-pdf"></i> Finaliser et générer le PDF
        </button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  name: 'FicheEvaluation',
  props: {
    project: {
      type: Object,
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
        project_id: this.project.id,
        evaluateur_nom: this.evaluateurNom,
        reference_fiche: '',
        // Critères d'évaluation
        alignement_national: 0,
        pertinence_territoriale: 0,
        innovation_valeur: 0,
        urgence_priorite: 0,
        solidite_technique: 0,
        capacites_mise_oeuvre: 0,
        gestion_risques: 0,
        realisme_budget: 0,
        rapport_cout_benefice: 0,
        durabilite_financiere: 0,
        impact_social: 0,
        impact_economique: 0,
        impact_environnemental: 0,
        effet_multiplicateur: 0,
        organisation_projet: 0,
        planification: 0,
        suivi_evaluation: 0,
        transparence_redevabilite: 0,
        // Évaluation détaillée
        points_forts: '',
        points_faibles: '',
        recommandations: '',
        conditions_particulieres: '',
        // Synthèse
        score_total: 0,
        appreciation_globale: '',
        avis_final: '',
        commentaires_finaux: ''
      }
    }
  },
  computed: {
    sousTotal() {
      return {
        pertinence: this.fiche.alignement_national + this.fiche.pertinence_territoriale +
                   this.fiche.innovation_valeur + this.fiche.urgence_priorite,
        technique: this.fiche.solidite_technique + this.fiche.capacites_mise_oeuvre +
                  this.fiche.gestion_risques,
        financiere: this.fiche.realisme_budget + this.fiche.rapport_cout_benefice +
                   this.fiche.durabilite_financiere,
        impact: this.fiche.impact_social + this.fiche.impact_economique +
               this.fiche.impact_environnemental + this.fiche.effet_multiplicateur,
        gouvernance: this.fiche.organisation_projet + this.fiche.planification +
                    this.fiche.suivi_evaluation + this.fiche.transparence_redevabilite
      }
    },
    scoreTotal() {
      return Object.values(this.sousTotal).reduce((sum, val) => sum + val, 0)
    },
    appreciationGlobale() {
      if (this.scoreTotal >= 90) return 'excellent'
      if (this.scoreTotal >= 80) return 'tres_bien'
      if (this.scoreTotal >= 70) return 'bien'
      if (this.scoreTotal >= 60) return 'passable'
      return 'insuffisant'
    },
    avisAutomatique() {
      // Calcul automatique de l'avis selon les seuils définis
      // Score 0-69: Avis défavorable
      // Score 70-79: Avis favorable sous réserves
      // Score 80-105: Avis favorable
      if (this.scoreTotal >= 80) return 'favorable'
      if (this.scoreTotal >= 70) return 'favorable_sous_conditions'
      return 'defavorable'
    },
    formulaireValide() {
      // Le bouton est actif dès qu'au moins une note est donnée
      return this.scoreTotal > 0;
    }
  },
  watch: {
    scoreTotal: {
      handler(newScore) {
        this.fiche.score_total = newScore
        this.fiche.appreciation_globale = this.appreciationGlobale
        // Mise à jour automatique de l'avis final selon le score
        this.fiche.avis_final = this.avisAutomatique
      },
      immediate: true
    }
  },
  mounted() {
    this.genererReference()
    this.chargerFicheSiExiste()
  },
  methods: {
    genererReference() {
      const date = new Date().toISOString().slice(0, 10).replace(/-/g, '')
      this.fiche.reference_fiche = `EVAL-${this.project.numero_projet || this.project.id}-${date}`
    },
    
    async chargerFicheSiExiste() {
      try {
        const response = await fetch(`/api/projects/${this.project.id}/fiche-evaluation`)
        if (response.ok) {
          const ficheExistante = await response.json()
          // Charger les données existantes
          Object.assign(this.fiche, ficheExistante)
        }
      } catch (error) {
        console.log('Aucune fiche existante trouvée, création d\'une nouvelle fiche')
      }
    },
    
    async sauvegarderBrouillon() {
      try {
        const response = await fetch(`/api/projects/${this.project.id}/fiche-evaluation`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            ...this.fiche,
            statut: 'brouillon'
          })
        })
        
        if (response.ok) {
          this.$toast.success('Brouillon sauvegardé avec succès')
        } else {
          throw new Error('Erreur lors de la sauvegarde')
        }
      } catch (error) {
        this.$toast.error('Erreur lors de la sauvegarde du brouillon')
        console.error(error)
      }
    },
    
    async soumettreEvaluation() {
      if (!this.formulaireValide) {
        this.$toast.error('Veuillez compléter tous les champs obligatoires')
        return
      }
      
      try {
        // Sauvegarder la fiche d'évaluation
        const response = await fetch(`/api/projects/${this.project.id}/fiche-evaluation`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            ...this.fiche,
            statut: 'finalise'
          })
        })
        
        if (!response.ok) {
          throw new Error('Erreur lors de la sauvegarde de la fiche')
        }
        
        // Générer le PDF
        const pdfResponse = await fetch(`/api/projects/${this.project.id}/fiche-evaluation/pdf`, {
          method: 'POST'
        })
        
        if (!pdfResponse.ok) {
          throw new Error('Erreur lors de la génération du PDF')
        }
        
        // Télécharger le PDF
        const blob = await pdfResponse.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${this.fiche.reference_fiche}.pdf`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
        
        this.$toast.success('Fiche d\'évaluation finalisée et PDF généré avec succès')
        this.$emit('evaluation-terminee', this.fiche)
        
      } catch (error) {
        this.$toast.error('Erreur lors de la finalisation de l\'évaluation')
        console.error(error)
      }
    },
    
    formatMoney(amount) {
      if (!amount) return '0 FCFA'
      return new Intl.NumberFormat('fr-FR').format(amount) + ' FCFA'
    },
    
    formatDate(date) {
      return new Intl.DateTimeFormat('fr-FR').format(date)
    }
  }
}
</script>

<style scoped>
.fiche-evaluation {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.header-fiche {
  border-bottom: 3px solid #1e40af;
  padding-bottom: 20px;
  margin-bottom: 30px;
}

.logo-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo-dgppe {
  height: 80px;
  width: auto;
}

.header-text h2 {
  color: #1e40af;
  margin: 0;
  font-size: 24px;
  font-weight: bold;
}

.sous-titre {
  color: #666;
  margin: 5px 0 0 0;
  font-style: italic;
}

.evaluation-form section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.evaluation-form section h3 {
  color: #1e40af;
  margin-top: 0;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e5e7eb;
}

.evaluation-form section h3 i {
  margin-right: 10px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #f9fafb;
  border-radius: 5px;
}

.info-item label {
  font-weight: 600;
  color: #374151;
}

.info-value {
  color: #1f2937;
  font-weight: 500;
}

.critere-section {
  margin-bottom: 25px;
  padding: 15px;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

.critere-section h4 {
  color: #1e40af;
  margin-top: 0;
  margin-bottom: 20px;
}

.critere-item {
  margin-bottom: 20px;
  padding: 15px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.critere-item label {
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 10px;
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 5px;
}

.slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #e5e7eb;
  outline: none;
  -webkit-appearance: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
}

.slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: none;
}

.score {
  min-width: 50px;
  font-weight: bold;
  color: #1e40af;
  text-align: center;
}

.critere-desc {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
  font-style: italic;
}

.sous-total {
  margin-top: 15px;
  padding: 10px;
  background: #dbeafe;
  border-radius: 5px;
  text-align: center;
}

.textarea-group {
  margin-bottom: 20px;
}

.textarea-group label {
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.textarea-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-family: inherit;
  font-size: 14px;
  resize: vertical;
  min-height: 80px;
}

.textarea-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.textarea-group small {
  display: block;
  color: #6b7280;
  margin-top: 5px;
  text-align: right;
}

.score-total {
  text-align: center;
  margin-bottom: 25px;
}

.score-highlight {
  color: #059669;
  font-size: 32px;
}

.score-bar {
  width: 100%;
  height: 20px;
  background: #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  margin-top: 10px;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #ef4444, #f59e0b, #059669);
  transition: width 0.3s ease;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.radio-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.radio-item:hover {
  background: #f9fafb;
  border-color: #3b82f6;
}

.radio-item.active {
  background: #dbeafe;
  border-color: #3b82f6;
}

.radio-item input[type="radio"] {
  margin-right: 10px;
}

.radio-label {
  flex: 1;
}

.radio-label.favorable {
  color: #059669;
}

.radio-label.conditionnel {
  color: #d97706;
}

.radio-label.defavorable {
  color: #dc2626;
}

.actions-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
  margin-top: 30px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #4b5563;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

@media (max-width: 768px) {
  .fiche-evaluation {
    padding: 10px;
  }
  
  .logo-header {
    flex-direction: column;
    text-align: center;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-section {
    flex-direction: column;
    gap: 15px;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>