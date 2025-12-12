<template>
  <div class="matrice-readonly">
    <h4>📋 Matrice d'Évaluation Préalable</h4>
    <p class="eval-date" v-if="matrice.date_evaluation">
      Évaluée le {{ formatDate(matrice.date_evaluation) }}
      <span v-if="matrice.evaluateur"> par {{ matrice.evaluateur }}</span>
    </p>

    <!-- Tableau des documents -->
    <div class="matrice-table">
      <table>
        <thead>
          <tr>
            <th class="col-document">Documents évalués</th>
            <th class="col-checkbox">Requis</th>
            <th class="col-checkbox">Transmis</th>
            <th class="col-statut">Statut</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(doc, index) in matrice.documents" :key="index" :class="{ 'missing-doc': doc.requis && !doc.transmis }">
            <td class="doc-name">{{ doc.nom }}</td>
            <td class="checkbox-cell">
              <span class="badge-check" :class="doc.requis ? 'badge-oui' : 'badge-non'">
                {{ doc.requis ? '✓ OUI' : '✕ NON' }}
              </span>
            </td>
            <td class="checkbox-cell">
              <span class="badge-check" :class="doc.transmis ? 'badge-oui' : 'badge-non'">
                {{ doc.transmis ? '✓ OUI' : '✕ NON' }}
              </span>
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

    <!-- Résumé -->
    <div class="resume-section">
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

    <!-- Commentaires -->
    <div v-if="matrice.commentaires_globaux" class="commentaires-readonly">
      <strong>💬 Commentaires de l'évaluateur:</strong>
      <p>{{ matrice.commentaires_globaux }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MatriceEvaluationPrealableReadOnly',
  props: {
    matrice: {
      type: Object,
      required: true
    }
  },
  computed: {
    documentsRequis() {
      return this.matrice.documents.filter(d => d.requis).length
    },
    documentsTransmis() {
      return this.matrice.documents.filter(d => d.requis && d.transmis).length
    },
    documentsManquants() {
      return this.matrice.documents.filter(d => d.requis && !d.transmis).length
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date)
    }
  }
}
</script>

<style scoped>
.matrice-readonly {
  background: #f8fafc;
  border: 2px solid #0ea5e9;
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1rem 0;
}

.matrice-readonly h4 {
  color: #0369a1;
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.eval-date {
  color: #64748b;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  font-style: italic;
}

/* Table styles */
.matrice-table {
  margin-bottom: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  table-layout: fixed;
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

.col-document {
  width: 45%;
}

.col-checkbox {
  width: 17.5%;
  text-align: center;
}

.col-statut {
  width: 20%;
  text-align: center;
}

tbody tr {
  border-bottom: 1px solid #e2e8f0;
}

tbody tr:hover {
  background-color: #f8fafc;
}

tbody tr.missing-doc {
  background-color: #fef2f2;
}

td {
  padding: 0.75rem;
  word-wrap: break-word;
}

.doc-name {
  font-size: 0.9rem;
  color: #334155;
}

.checkbox-cell {
  text-align: center;
}

.badge-check {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
}

.badge-oui {
  background: #dcfce7;
  color: #166534;
}

.badge-non {
  background: #fee2e2;
  color: #991b1b;
}

.statut-cell {
  text-align: center;
}

.badge-statut {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
}

.badge-statut.conforme {
  background: #dcfce7;
  color: #166534;
}

.badge-statut.manquant {
  background: #fee2e2;
  color: #991b1b;
}

.badge-statut.non-requis {
  background: #f1f5f9;
  color: #64748b;
}

/* Résumé */
.resume-section {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  border-left: 4px solid #0ea5e9;
}

.resume-item {
  margin: 0.5rem 0;
  color: #334155;
  font-size: 0.95rem;
}

/* Commentaires */
.commentaires-readonly {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  border-left: 4px solid #f59e0b;
}

.commentaires-readonly strong {
  color: #0369a1;
  display: block;
  margin-bottom: 0.5rem;
}

.commentaires-readonly p {
  margin: 0;
  color: #334155;
  line-height: 1.6;
  white-space: pre-wrap;
}
</style>
