<template>
  <div class="projects-table">
    <table>
      <thead>
        <tr>
          <th>N° Projet</th>
          <th>Titre</th>
          <th>Objectif global et activités</th>
          <th>Coût estimatif (FCFA)</th>
          <th>Secteur</th>
          <th>Pôles</th>
          <th>Statut</th>
          <th>Auteur</th>
          <th>Évaluateur</th>
          <th>Décision finale</th>
          <th>Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="p in projects" :key="p.id">
          <td><strong>{{ p.numero_projet || 'N/A' }}</strong></td>
          <td>{{ p.titre }}</td>
          <td>{{ p.objectifs }}</td>
          <td>{{ p.cout_estimatif?.toLocaleString() }}</td>
          <td>{{ p.secteur }}</td>
          <td>{{ p.poles }}</td>
          <td>
            <span class="status" :class="p.statut">{{ p.statut }}</span>
          </td>
          <td>{{ p.auteur_nom }}</td>
          <td>{{ p.evaluateur_nom }}</td>
          <td>{{ p.decision_finale || '-' }}</td>
          <td>
            <button class="btn-action" @click="$emit('refresh')">↻</button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-if="!projects.length" class="empty">Aucun projet trouvé</p>
  </div>
</template>

<script>
export default {
  props: {
    projects: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style scoped>
.projects-table {
  width: 100%;
  overflow-x: auto;
  border-radius: 10px;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.1);
}

table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

th {
  background-color: #1a237e;
  color: white;
  padding: 10px;
  text-align: left;
}

td {
  border-top: 1px solid #ddd;
  padding: 8px;
  vertical-align: top;
  word-break: break-word;
}

tr:hover {
  background-color: #f5f5f5;
}

.status {
  font-weight: bold;
  padding: 3px 8px;
  border-radius: 6px;
  text-transform: capitalize;
  display: inline-block;
}

.status.en_attente {
  background: #fff3cd;
  color: #856404;
}

.status.en_traitement {
  background: #cce5ff;
  color: #004085;
}

.status.valide {
  background: #d4edda;
  color: #155724;
}

.status.rejete {
  background: #f8d7da;
  color: #721c24;
}

.btn-action {
  background: #1976d2;
  color: white;
  border: none;
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.btn-action:hover {
  background: #0d47a1;
}

.empty {
  text-align: center;
  color: gray;
  padding: 20px;
}
</style>
