<template>
  <div class="matrice-evaluation-prealable">
    <h3>📋 Matrice d'Évaluation Préalable</h3>
    <p class="description">Vérifier la recevabilité du dossier en cochant les documents requis et transmis</p>

    <!-- Tableau des documents -->
    <div class="matrice-table">
      <table>
        <thead>
          <tr>
            <th class="col-document">Documents à fournir</th>
            <th class="col-checkbox">Requis<br><span class="sub-label">(OUI/NON)</span></th>
            <th class="col-checkbox">Transmis<br><span class="sub-label">(OUI/NON)</span></th>
            <th class="col-statut">Statut</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(doc, index) in documents" :key="index" :class="{ 'missing-doc': doc.requis && !doc.transmis }">
            <td class="doc-name">
              <input
                v-if="doc.custom"
                v-model="doc.nom"
                type="text"
                class="custom-doc-input"
                placeholder="Nom du document..."
              />
              <span v-else>{{ doc.nom }}</span>
              <button
                v-if="doc.custom"
                @click="removeCustomDocument(index)"
                class="btn-remove-doc"
                title="Supprimer ce document"
              >
                ✕
              </button>
            </td>
            <td class="checkbox-cell">
              <label class="checkbox-container">
                <input type="checkbox" v-model="doc.requis" @change="updateStatut">
                <span class="checkmark"></span>
              </label>
            </td>
            <td class="checkbox-cell">
              <label class="checkbox-container">
                <input type="checkbox" v-model="doc.transmis" @change="updateStatut" :disabled="!doc.requis">
                <span class="checkmark"></span>
              </label>
            </td>
            <td class="statut-cell">
              <span v-if="!doc.requis" class="badge-statut non-requis">Non requis</span>
              <span v-else-if="doc.transmis" class="badge-statut conforme">✓ Conforme</span>
              <span v-else class="badge-statut manquant">⚠ Manquant</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Bouton ajouter document -->
    <div class="add-document-section">
      <button @click="addCustomDocument" class="btn-add-document">
        ➕ Ajouter un document supplémentaire
      </button>
    </div>

    <!-- Résumé automatique -->
    <div class="resume-automatique" :class="statutGlobal">
      <div class="resume-header">
        <strong>Résumé automatique:</strong>
      </div>
      <div class="resume-content">
        <div v-if="documentsRequis === 0" class="resume-item">
          ⚠️ Aucun document marqué comme requis
        </div>
        <div v-else>
          <div class="resume-item">
            📊 <strong>{{ documentsRequis }}</strong> document(s) requis
          </div>
          <div class="resume-item">
            ✓ <strong>{{ documentsTransmis }}</strong> document(s) transmis
          </div>
          <div class="resume-item" v-if="documentsManquants > 0">
            ⚠️ <strong>{{ documentsManquants }}</strong> document(s) manquant(s)
          </div>
        </div>
      </div>
      <div class="resume-decision">
        <span v-if="documentsRequis === 0" class="decision-badge indetermine">
          Statut indéterminé
        </span>
        <span v-else-if="documentsManquants === 0" class="decision-badge evaluable">
          ✓ Dossier évaluable
        </span>
        <span v-else class="decision-badge incomplet">
          ⚠️ Dossier incomplet
        </span>
      </div>
    </div>

    <!-- Commentaires et suite à donner -->
    <div class="commentaires-section">
      <label for="commentaires-globaux">
        <strong>💬 Commentaires et suite à donner</strong>
        <span class="label-hint">(Précisez les documents manquants et les actions attendues)</span>
      </label>
      <textarea
        id="commentaires-globaux"
        v-model="commentairesGlobaux"
        rows="4"
        placeholder="Ex: Documents manquants: Étude de faisabilité financière. L'auteur du projet doit transmettre ce document sous 15 jours..."
        class="commentaires-textarea"
      ></textarea>
    </div>

    <!-- Boutons d'action -->
    <div class="actions-section">
      <button
        @click="soumettre('dossier_evaluable')"
        class="btn-action btn-success"
        :disabled="enCours || documentsManquants > 0"
        :title="documentsManquants > 0 ? 'Des documents requis sont manquants' : 'Valider le dossier comme évaluable'"
      >
        ✓ Dossier évaluable
      </button>
      <button
        @click="soumettre('complements_requis')"
        class="btn-action btn-warning"
        :disabled="enCours || !commentairesGlobaux.trim()"
        title="Demander des compléments"
      >
        📝 Compléments requis
      </button>
      <button
        @click="soumettre('dossier_rejete')"
        class="btn-action btn-danger"
        :disabled="enCours || !commentairesGlobaux.trim()"
        title="Rejeter le dossier"
      >
        ✕ Dossier rejeté
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
      // Documents de base
      documents: [
        { nom: 'Document de formulation du projet', requis: false, transmis: false, custom: false },
        { nom: 'Étude de faisabilité technique', requis: false, transmis: false, custom: false },
        { nom: 'Étude de faisabilité économique', requis: false, transmis: false, custom: false },
        { nom: 'Étude de faisabilité financière', requis: false, transmis: false, custom: false },
        { nom: 'Étude sociale et environnementale si pertinente', requis: false, transmis: false, custom: false },
        { nom: 'Rapport d\'évaluation de la phase précédente s\'il s\'agit d\'une seconde phase', requis: false, transmis: false, custom: false }
      ],
      commentairesGlobaux: '',
      enCours: false
    }
  },
  computed: {
    documentsRequis() {
      return this.documents.filter(d => d.requis).length
    },
    documentsTransmis() {
      return this.documents.filter(d => d.requis && d.transmis).length
    },
    documentsManquants() {
      return this.documents.filter(d => d.requis && !d.transmis).length
    },
    statutGlobal() {
      if (this.documentsRequis === 0) return 'statut-indetermine'
      if (this.documentsManquants === 0) return 'statut-evaluable'
      return 'statut-incomplet'
    }
  },
  mounted() {
    // Charger les données initiales si disponibles
    if (this.matriceInitiale) {
      if (this.matriceInitiale.documents) {
        this.documents = this.matriceInitiale.documents
      }
      if (this.matriceInitiale.commentaires_globaux) {
        this.commentairesGlobaux = this.matriceInitiale.commentaires_globaux
      }
    }
  },
  methods: {
    addCustomDocument() {
      this.documents.push({
        nom: '',
        requis: false,
        transmis: false,
        custom: true
      })
    },
    removeCustomDocument(index) {
      this.documents.splice(index, 1)
      this.updateStatut()
    },
    updateStatut() {
      // Désactiver "transmis" si "requis" est décoché
      this.documents.forEach(doc => {
        if (!doc.requis) {
          doc.transmis = false
        }
      })
    },
    async soumettre(decision) {
      // Validation
      if (decision === 'dossier_evaluable' && this.documentsManquants > 0) {
        alert('Impossible de valider le dossier comme évaluable: des documents requis sont manquants')
        return
      }

      if ((decision === 'complements_requis' || decision === 'dossier_rejete') && !this.commentairesGlobaux.trim()) {
        alert('Les commentaires sont obligatoires pour cette décision')
        return
      }

      this.enCours = true

      try {
        const user = JSON.parse(localStorage.getItem('user') || '{}')

        // Préparer la matrice JSON
        const matrice = {
          documents: this.documents,
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

        alert('Évaluation préalable soumise avec succès')
        this.$emit('evaluation-soumise', { decision, matrice })

      } catch (error) {
        console.error('Erreur:', error)
        alert('Erreur lors de la soumission de l\'évaluation préalable')
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

/* Table styles */
.matrice-table {
  overflow-x: auto;
  margin-bottom: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

thead {
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: white;
}

th {
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.9rem;
}

.sub-label {
  font-size: 0.75rem;
  font-weight: 400;
  opacity: 0.9;
}

.col-document {
  width: 50%;
}

.col-checkbox {
  width: 15%;
  text-align: center;
}

.col-statut {
  width: 20%;
  text-align: center;
}

tbody tr {
  border-bottom: 1px solid #e2e8f0;
  transition: background-color 0.2s;
}

tbody tr:hover {
  background-color: #f1f5f9;
}

tbody tr.missing-doc {
  background-color: #fef2f2;
}

td {
  padding: 0.75rem;
}

.doc-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.custom-doc-input {
  flex: 1;
  padding: 0.4rem;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font-size: 0.85rem;
}

.btn-remove-doc {
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background-color 0.2s;
}

.btn-remove-doc:hover {
  background: #dc2626;
}

/* Checkbox styling */
.checkbox-cell {
  text-align: center;
}

.checkbox-container {
  display: inline-block;
  position: relative;
  padding-left: 28px;
  cursor: pointer;
  user-select: none;
}

.checkbox-container input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
}

.checkmark {
  position: absolute;
  top: 0;
  left: 0;
  height: 20px;
  width: 20px;
  background-color: #e2e8f0;
  border: 2px solid #cbd5e1;
  border-radius: 4px;
  transition: all 0.2s;
}

.checkbox-container:hover input ~ .checkmark {
  background-color: #cbd5e1;
}

.checkbox-container input:checked ~ .checkmark {
  background-color: #10b981;
  border-color: #059669;
}

.checkbox-container input:disabled ~ .checkmark {
  background-color: #f1f5f9;
  border-color: #e2e8f0;
  cursor: not-allowed;
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
}

.checkbox-container input:checked ~ .checkmark:after {
  display: block;
}

.checkbox-container .checkmark:after {
  left: 6px;
  top: 2px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

/* Statut badges */
.statut-cell {
  text-align: center;
}

.badge-statut {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.badge-statut.non-requis {
  background: #f1f5f9;
  color: #64748b;
}

.badge-statut.conforme {
  background: #d1fae5;
  color: #065f46;
}

.badge-statut.manquant {
  background: #fee2e2;
  color: #991b1b;
}

/* Add document button */
.add-document-section {
  margin: 1rem 0;
}

.btn-add-document {
  background: #f8fafc;
  color: #0369a1;
  border: 2px dashed #0ea5e9;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-add-document:hover {
  background: #e0f2fe;
  border-color: #0369a1;
}

/* Résumé automatique */
.resume-automatique {
  background: white;
  border-left: 4px solid #94a3b8;
  padding: 1rem;
  margin: 1.5rem 0;
  border-radius: 8px;
}

.resume-automatique.statut-evaluable {
  border-left-color: #10b981;
  background: #f0fdf4;
}

.resume-automatique.statut-incomplet {
  border-left-color: #f59e0b;
  background: #fffbeb;
}

.resume-automatique.statut-indetermine {
  border-left-color: #94a3b8;
}

.resume-header {
  font-size: 0.95rem;
  margin-bottom: 0.5rem;
  color: #1e293b;
}

.resume-content {
  margin: 0.75rem 0;
}

.resume-item {
  padding: 0.25rem 0;
  font-size: 0.9rem;
  color: #475569;
}

.resume-decision {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e2e8f0;
}

.decision-badge {
  display: inline-block;
  padding: 0.4rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
}

.decision-badge.evaluable {
  background: #d1fae5;
  color: #065f46;
}

.decision-badge.incomplet {
  background: #fef3c7;
  color: #92400e;
}

.decision-badge.indetermine {
  background: #f1f5f9;
  color: #475569;
}

/* Commentaires */
.commentaires-section {
  margin: 1.5rem 0;
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
}

.commentaires-textarea:focus {
  outline: none;
  border-color: #0ea5e9;
}

/* Actions */
.actions-section {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-top: 1.5rem;
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

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
}

.btn-warning {
  background: #f59e0b;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background: #d97706;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}
</style>
