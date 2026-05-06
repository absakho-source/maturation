<template>
  <PageWrapper>
    <div class="dashboard-container" v-if="project">
      <div class="dashboard-section">
        <h2 class="dashboard-title">✏️ Modifier le projet</h2>
        <p class="page-desc">
          {{ project.numero_projet || '—' }} — {{ project.titre }}
        </p>
      </div>

      <form @submit.prevent="submit" class="submit-form-wrapper">
        <div class="section">
          <div class="section-header"><h3>Informations du projet</h3></div>

          <div class="submit-form">
            <div class="form-row">
              <div class="form-group full-width">
                <label>Intitulé du projet <span class="req">*</span></label>
                <input v-model="form.titre" type="text" required />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group full-width">
                <label>Structure soumissionnaire</label>
                <input v-model="form.structure_soumissionnaire" type="text" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group full-width">
                <label>Ministère de tutelle</label>
                <select v-model="form.organisme_tutelle">
                  <option value="">— Sélectionner un ministère —</option>
                  <option v-for="m in ministeres" :key="m.id" :value="m.nom_complet">{{ m.nom_complet }}</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Pôles territoriaux</label>
                <div class="checkbox-group-poles">
                  <label v-for="pole in polesOptions" :key="pole" class="checkbox-label-pole">
                    <input type="checkbox" :value="pole" v-model="form.poles" />
                    <span class="checkbox-text">{{ pole }}</span>
                  </label>
                </div>
              </div>
              <div class="form-group">
                <label>Secteur de planification</label>
                <select v-model="form.secteur">
                  <option value="">— Sélectionner —</option>
                  <option v-for="s in secteurs" :key="s" :value="s">{{ s }}</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group full-width">
                <label>Description</label>
                <textarea v-model="form.description" rows="4"></textarea>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Coût estimatif (FCFA)</label>
                <input v-model="form.cout_estimatif" type="number" min="0" />
              </div>
              <div class="form-group">
                <label>Durée (années)</label>
                <input v-model="form.duree_annees" type="number" min="0" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group full-width">
                <label>Évaluateur</label>
                <input v-model="form.evaluateur_nom" type="text" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group full-width">
                <label>Recommandation / commentaire</label>
                <textarea v-model="form.commentaires" rows="3"></textarea>
              </div>
            </div>
          </div>
        </div>

        <div class="submit-button-wrapper">
          <button type="button" class="btn-cancel" @click="$router.back()">✖️ Annuler</button>
          <button type="submit" class="btn-submit" :disabled="saving">
            {{ saving ? '⏳ Enregistrement…' : '💾 Enregistrer les modifications' }}
          </button>
        </div>
      </form>
    </div>
    <div v-else class="loading">Chargement…</div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';

export default {
  name: 'EditProjet',
  components: { PageWrapper },
  data() {
    return {
      project: null,
      saving: false,
      ministeres: [],
      form: {
        titre: '', description: '',
        secteur: '', poles: [],
        cout_estimatif: null, duree_annees: null,
        structure_soumissionnaire: '',
        organisme_tutelle: '',
        evaluateur_nom: '',
        commentaires: '',
      },
      secteurs: [
        'agriculture-élevage-pêche',
        'environnement-eau-assainissement',
        'énergies-mines',
        'industrie-artisanat',
        'économie-finances-commerce',
        'tourisme-culture',
        'transports-infrastructures',
        'postes-communication-télécommunications-économie numérique',
        'population-jeunesse-emploi-travail-fonction publique',
        'habitat-urbanisme',
        'éducation-formation-recherche',
        'gouvernance-justice-défense-sécurité',
        'santé-action sociale',
        'sports-loisirs',
        'aménagement-développement territorial-décentralisation',
        'affaires étrangères-intégration',
      ],
      polesOptions: [
        'Dakar', 'Thiès', 'Diourbel-Louga',
        'Centre (Kaolack, Fatick, Kaffrine)',
        'Nord (Saint-Louis)', 'Nord-Est (Matam)',
        'Sud (Ziguinchor, Sédhiou, Kolda)',
        'Sud-Est (Tambacounda, Kédougou)',
      ],
    };
  },
  mounted() {
    this.loadProject();
    this.loadMinisteres();
  },
  methods: {
    async loadProject() {
      const id = this.$route.params.id;
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const r = await fetch(`/api/projects/${id}?role=${user.role}&username=${user.username}`);
      if (!r.ok) {
        this.$toast.error('Projet introuvable');
        return;
      }
      this.project = await r.json();
      const polesArr = (this.project.poles || '').split(',').map(s => s.trim()).filter(Boolean);
      this.form = {
        titre: this.project.titre || '',
        description: this.project.description || '',
        secteur: this.project.secteur || '',
        poles: polesArr,
        cout_estimatif: this.project.cout_estimatif || null,
        duree_annees: this.project.duree_annees || null,
        structure_soumissionnaire: this.project.structure_soumissionnaire || '',
        organisme_tutelle: this.project.organisme_tutelle || '',
        evaluateur_nom: this.project.evaluateur_nom || '',
        commentaires: this.project.commentaires || '',
      };
    },
    async loadMinisteres() {
      try {
        const r = await fetch('/api/ministeres');
        if (r.ok) this.ministeres = await r.json();
      } catch (e) { /* noop */ }
    },
    async submit() {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (!['admin', 'secretariatsct'].includes(user.role)) {
        this.$toast.error('Action non autorisée');
        return;
      }
      this.saving = true;
      try {
        const payload = {
          ...this.form,
          poles: this.form.poles.join(', '),
          auteur_nom: this.form.structure_soumissionnaire || this.form.organisme_tutelle || undefined,
        };
        const r = await fetch(`/api/projects/${this.project.id}?role=${user.role}&username=${user.username}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!r.ok) {
          const err = await r.json().catch(() => ({}));
          throw new Error(err.error || 'Erreur lors de la sauvegarde');
        }
        this.$toast.success('Modifications enregistrées');
        this.$router.push(`/project/${this.project.id}`);
      } catch (e) {
        this.$toast.error(e.message);
      } finally {
        this.saving = false;
      }
    }
  }
};
</script>

<style scoped>
.dashboard-container { max-width: 1100px; margin: 0 auto; padding: 2rem; }
.loading { padding: 3rem; text-align: center; color: #64748b; }

.dashboard-section, .section {
  background: white; border-radius: 12px;
  padding: 2rem; margin-bottom: 2rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.dashboard-section { padding: 1.5rem 2rem; }
.dashboard-title { margin: 0 0 0.5rem; font-size: 1.5rem; font-weight: 700; color: #1e293b; }
.page-desc { margin: 0; color: #64748b; font-size: 0.95rem; }

.section-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 1.5rem; padding-bottom: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}
.section-header h3 { margin: 0; font-size: 1.15rem; font-weight: 600; color: #1e293b; }

.submit-form { display: flex; flex-direction: column; gap: 1.2rem; }
.form-row { display: grid; gap: 1.2rem; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }
.form-group { display: flex; flex-direction: column; }
.form-group.full-width { grid-column: 1 / -1; }
.form-group label { margin-bottom: 0.5rem; font-weight: 600; color: #2c3e50; font-size: 0.92rem; }
.form-group input, .form-group select, .form-group textarea {
  padding: 0.75rem; border: 2px solid #e5e7eb; border-radius: 8px;
  font-size: 0.95rem; font-family: inherit;
}
.form-group input:focus, .form-group select:focus, .form-group textarea:focus {
  outline: none; border-color: #2563eb;
}
.form-group textarea { resize: vertical; }
.req { color: #dc2626; }

.checkbox-group-poles {
  display: flex; flex-direction: column; gap: 0.5rem;
  padding: 1rem; background: #f8fafc;
  border: 2px solid #e5e7eb; border-radius: 8px;
  max-height: 300px; overflow-y: auto;
}
.checkbox-label-pole {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  background: white; border: 1px solid #e2e8f0; border-radius: 6px;
  cursor: pointer; transition: all 0.2s;
}
.checkbox-label-pole:hover { background: #f0f9ff; border-color: #3b82f6; }
.checkbox-label-pole input[type="checkbox"] {
  width: 18px; height: 18px; accent-color: #2563eb;
}
.checkbox-label-pole:has(input:checked) { background: #eff6ff; border-color: #3b82f6; }
.checkbox-text { flex: 1; font-size: 0.92rem; color: #374151; }

.submit-button-wrapper {
  display: flex; gap: 1rem; justify-content: center;
  margin-top: 2rem; padding: 1rem 0;
}
.btn-submit {
  padding: 1rem 3rem;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  color: white; border: none; border-radius: 8px;
  font-size: 1.05rem; font-weight: 600; cursor: pointer;
  box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
  min-width: 280px; transition: all 0.3s;
}
.btn-submit:hover:not(:disabled) {
  background: linear-gradient(135deg, #047857 0%, #065f46 100%);
  transform: translateY(-2px);
}
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-cancel {
  padding: 1rem 2rem;
  background: #e2e8f0; color: #475569;
  border: none; border-radius: 8px;
  font-size: 1rem; font-weight: 600; cursor: pointer;
}
.btn-cancel:hover { background: #cbd5e1; color: #1e293b; }

@media (max-width: 768px) {
  .dashboard-container { padding: 1rem; }
  .section { padding: 1.25rem; }
  .submit-button-wrapper { flex-direction: column-reverse; }
  .btn-submit, .btn-cancel { width: 100%; min-width: 0; }
}
</style>
