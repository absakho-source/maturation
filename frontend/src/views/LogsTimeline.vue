<template>
  <div class="timeline">
    <PageWrapper>
      <div class="container">
        <h2>Historique des actions</h2>

        <div v-if="logs.length === 0" class="empty">
          Aucun log enregistré pour ce projet.
        </div>

        <ul v-else class="log-list">
          <li v-for="log in logs" :key="log.date" class="log-item">
            <div class="dot"></div>
            <div class="content">
              <h4>{{ log.action }}</h4>
            <p>
              <strong>Auteur :</strong> {{ log.auteur }} ({{ log.role }})<br />
              <strong>Statut :</strong> {{ log.statut }}<br />
              <strong>Date :</strong> {{ log.date }}
            </p>
            <p v-if="log.commentaire" class="commentaire">💬 {{ log.commentaire }}</p>
          </div>
        </li>
      </ul>

      <button @click="exportCSV" class="export-btn">Exporter en CSV</button>
      <router-link to="/" class="back-link">← Retour</router-link>
      </div>
    </PageWrapper>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import PageWrapper from '../components/PageWrapper.vue'

const route = useRoute()
const logs = ref([])

onMounted(async () => {
  const id = route.params.id
  const res = await axios.get(`/api/logs/${id}`)
  logs.value = res.data
})

function exportCSV() {
  const header = ['Auteur', 'Rôle', 'Action', 'Commentaire', 'Statut', 'Date']
  const rows = logs.value.map(l => [
    l.auteur,
    l.role,
    l.action,
    l.commentaire ? `"${l.commentaire.replace(/"/g, '""')}"` : '',
    l.statut,
    l.date
  ])
  const csv = [header, ...rows].map(r => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `logs_projet_${route.params.id}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.timeline {
  background: #f7f9fc;
  min-height: 100vh;
}
.container {
  max-width: 900px;
  margin: 40px auto;
  padding: 20px;
}
.log-list {
  list-style: none;
  position: relative;
  padding-left: 30px;
  margin-bottom: 30px;
}
.log-list::before {
  content: "";
  position: absolute;
  top: 0;
  left: 10px;
  width: 2px;
  height: 100%;
  background: #004080;
}
.log-item {
  position: relative;
  margin-bottom: 20px;
  padding-left: 20px;
}
.dot {
  position: absolute;
  left: -2px;
  top: 8px;
  width: 12px;
  height: 12px;
  background: #004080;
  border-radius: 50%;
}
.content {
  background: white;
  border-radius: 8px;
  padding: 10px 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.commentaire {
  color: #004080;
  font-style: italic;
  margin-top: 5px;
}
.export-btn {
  background: #004080;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 5px;
  cursor: pointer;
}
.export-btn:hover {
  background: #0066cc;
}
.back-link {
  display: inline-block;
  margin-top: 20px;
  color: #004080;
  text-decoration: none;
}
.empty {
  background: #fff3cd;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
}
</style>
