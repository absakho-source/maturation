<template>
  <PageWrapper>
    <div class="dashboard-container">

      <!-- En-tête -->
      <div class="dashboard-section">
        <h2 class="dashboard-title">📥 Importer un projet historique</h2>
        <p class="page-desc">
          Saisir un projet évalué avant l'existence de la plateforme.
          Il sera créé directement au stade choisi et marqué « Import historique ».
        </p>
      </div>

      <form @submit.prevent="submit" class="submit-form-wrapper">

        <!-- ─── 1. Informations du projet ─── -->
        <div class="section">
          <div class="section-header">
            <h3><span class="step-num">1</span> Informations du projet</h3>
          </div>

          <div class="submit-form">
            <!-- Titre -->
            <div class="form-row">
              <div class="form-group full-width">
                <label>Intitulé du projet <span class="req">*</span></label>
                <input v-model="form.titre" type="text" required placeholder="Ex: Construction d'un centre de santé" />
              </div>
            </div>

            <!-- Structure soumissionnaire -->
            <div class="form-row">
              <div class="form-group full-width">
                <label>Structure soumissionnaire</label>
                <input v-model="form.structure_soumissionnaire" type="text" placeholder="Ex: Direction générale de la Santé" />
              </div>
            </div>

            <!-- Ministère de tutelle -->
            <div class="form-row">
              <div class="form-group full-width">
                <label>Ministère de tutelle</label>
                <select v-model="form.organisme_tutelle">
                  <option value="">— Sélectionner un ministère —</option>
                  <option v-for="m in ministeres" :key="m.id" :value="m.nom_complet">{{ m.nom_complet }}</option>
                </select>
                <small v-if="!ministeres.length" class="hint">Liste des ministères indisponible</small>
              </div>
            </div>

            <!-- Pôles + Secteur -->
            <div class="form-row">
              <div class="form-group">
                <label>Pôles territoriaux concernés</label>
                <div class="checkbox-group-poles">
                  <div class="poles-actions">
                    <button type="button" @click="toggleAllPoles" class="btn-toggle-poles">
                      {{ form.poles.length === polesOptions.length ? '✕ Désélectionner tout' : '✓ Sélectionner tous les pôles' }}
                    </button>
                  </div>
                  <label v-for="pole in polesOptions" :key="pole" class="checkbox-label-pole">
                    <input type="checkbox" :value="pole" v-model="form.poles" />
                    <span class="checkbox-text">{{ pole }}</span>
                  </label>
                </div>
                <small class="hint hint-success" v-if="form.poles.length">
                  {{ form.poles.length }} pôle(s) sélectionné(s)
                </small>
              </div>
              <div class="form-group">
                <label>Secteur de planification</label>
                <select v-model="form.secteur">
                  <option value="" disabled>— Sélectionner —</option>
                  <option v-for="s in secteurs" :key="s" :value="s">{{ s }}</option>
                </select>
              </div>
            </div>

            <!-- Description -->
            <div class="form-row">
              <div class="form-group full-width">
                <label>Description</label>
                <textarea v-model="form.description" rows="4" placeholder="Résumé du projet…"></textarea>
              </div>
            </div>

            <!-- Coût + Durée -->
            <div class="form-row">
              <div class="form-group">
                <label>Coût estimatif (FCFA)</label>
                <input v-model="form.cout_estimatif" type="number" min="0" placeholder="Ex: 5 000 000 000" />
              </div>
              <div class="form-group">
                <label>Durée (années)</label>
                <input v-model="form.duree_annees" type="number" min="0" placeholder="Ex: 3" />
              </div>
            </div>
          </div>
        </div>

        <!-- ─── 2. Stade d'avancement ─── -->
        <div class="section">
          <div class="section-header">
            <h3><span class="step-num">2</span> Stade d'avancement</h3>
          </div>

          <div class="stade-selector">
            <label v-for="s in stades" :key="s.value" class="stade-option"
                   :class="{ active: form.stade === s.value }">
              <input type="radio" v-model="form.stade" :value="s.value" />
              <div class="stade-label">
                <strong>{{ s.label }}</strong>
                <small>{{ s.desc }}</small>
              </div>
            </label>
          </div>
        </div>

        <!-- ─── 3. Évaluation ─── -->
        <div class="section">
          <div class="section-header">
            <h3><span class="step-num">3</span> Évaluation</h3>
          </div>

          <div class="submit-form">
            <div class="form-row">
              <div class="form-group">
                <label>Évaluateur</label>
                <select v-model="form.evaluateur_nom">
                  <option value="">— Sélectionner un évaluateur —</option>
                  <option v-for="u in evaluateurs" :key="u.id" :value="u.display_name">{{ u.display_name }}</option>
                </select>
                <small v-if="!evaluateurs.length" class="hint">Aucun évaluateur trouvé dans la plateforme</small>
              </div>
              <div class="form-group">
                <label>Date d'évaluation</label>
                <input v-model="form.date_evaluation" type="date" />
                <small class="hint">Détermine le préfixe AAAAMM du numéro</small>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Score total (/100) <span class="req">*</span></label>
                <input v-model.number="form.score_total" type="number" min="0" max="100" step="0.5" required />
              </div>
              <div class="form-group">
                <label>Proposition <span class="req">*</span></label>
                <select v-model="form.proposition" required>
                  <option value="">— Sélectionner —</option>
                  <option value="Favorable">Favorable</option>
                  <option value="Favorable sous conditions">Favorable sous conditions</option>
                  <option value="Défavorable">Défavorable</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group full-width">
                <label>Recommandation générale</label>
                <textarea v-model="form.recommandations" rows="3" placeholder="Recommandations de la Commission…"></textarea>
              </div>
            </div>

            <!-- Drop zone : fiche d'évaluation -->
            <div class="form-row">
              <div class="form-group full-width">
                <label>📎 Fiche d'évaluation (PDF / Word)</label>
                <div class="drop-zone" :class="{ 'drop-zone-active': dragFiche }"
                     @click="$refs.ficheInput.click()"
                     @dragover.prevent="dragFiche = true"
                     @dragleave.prevent="dragFiche = false"
                     @drop.prevent="onFicheDrop">
                  <input ref="ficheInput" type="file" accept=".pdf,.doc,.docx,.odt"
                         @change="onFicheChange" hidden />
                  <template v-if="!fichierEvaluation">
                    <div class="dz-icon">📄</div>
                    <div class="dz-text">Glisser-déposer la fiche ici ou <strong>cliquer pour parcourir</strong></div>
                    <div class="dz-hint">PDF, Word, OpenDocument</div>
                  </template>
                  <ul v-else class="file-list" @click.stop>
                    <li>
                      <span class="file-name">📄 {{ fichierEvaluation.name }}</span>
                      <span class="file-size">{{ formatSize(fichierEvaluation.size) }}</span>
                      <button type="button" class="btn-link" @click="fichierEvaluation = null">Retirer</button>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Drop zone : annexes -->
            <div class="form-row">
              <div class="form-group full-width">
                <label>📎 Annexes (optionnel — plusieurs fichiers acceptés)</label>
                <div class="drop-zone" :class="{ 'drop-zone-active': dragAnnexes }"
                     @click="$refs.annexesInput.click()"
                     @dragover.prevent="dragAnnexes = true"
                     @dragleave.prevent="dragAnnexes = false"
                     @drop.prevent="onAnnexesDrop">
                  <input ref="annexesInput" type="file" multiple
                         @change="onAnnexesChange" hidden />
                  <template v-if="!annexes.length">
                    <div class="dz-icon">📎</div>
                    <div class="dz-text">Glisser-déposer un ou plusieurs fichiers</div>
                    <div class="dz-hint">Tous types acceptés</div>
                  </template>
                  <template v-else>
                    <ul class="file-list" @click.stop>
                      <li v-for="(f, i) in annexes" :key="i">
                        <span class="file-name">📎 {{ f.name }}</span>
                        <span class="file-size">{{ formatSize(f.size) }}</span>
                        <button type="button" class="btn-link" @click="removeAnnexe(i)">Retirer</button>
                      </li>
                    </ul>
                    <div class="dz-add" @click.stop="$refs.annexesInput.click()">+ Ajouter d'autres fichiers</div>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ─── 4. Validations hiérarchiques ─── -->
        <div v-if="form.stade !== 'evalue'" class="section">
          <div class="section-header">
            <h3><span class="step-num">4</span> Validations hiérarchiques</h3>
          </div>

          <div class="submit-form">
            <div class="form-row" v-if="['valide_sct','valide_psct','decision_comite'].includes(form.stade)">
              <div class="form-group full-width">
                <label>Validation Secrétariat SCT</label>
                <select v-model="form.validation_sct">
                  <option value="valide">Validé</option>
                  <option value="rejete">Rejeté</option>
                </select>
              </div>
            </div>

            <div class="form-row" v-if="['valide_psct','decision_comite'].includes(form.stade)">
              <div class="form-group full-width">
                <label>Avis Présidence SCT</label>
                <select v-model="form.avis_psct">
                  <option value="valide">Validé</option>
                  <option value="rejete">Rejeté</option>
                </select>
              </div>
            </div>

            <div class="form-row" v-if="form.stade === 'decision_comite'">
              <div class="form-group full-width">
                <label>Décision du Comité</label>
                <select v-model="form.decision_comite">
                  <option value="confirme">Entériné (confirmé)</option>
                  <option value="conteste">Contesté</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- ─── Boutons ─── -->
        <div class="submit-button-wrapper">
          <button type="button" class="btn-cancel" @click="$router.back()">✖️ Annuler</button>
          <button type="submit" class="btn-submit" :disabled="loading || !canSubmit">
            {{ loading ? '⏳ Import en cours…' : '📥 Importer le projet' }}
          </button>
        </div>
      </form>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';

export default {
  name: 'ImportProjetHistorique',
  components: { PageWrapper },
  data() {
    return {
      loading: false,
      fichierEvaluation: null,
      annexes: [],
      dragFiche: false,
      dragAnnexes: false,
      ministeres: [],
      evaluateurs: [],
      form: {
        titre: '',
        description: '',
        secteur: '',
        poles: [],
        cout_estimatif: null,
        duree_annees: null,
        structure_soumissionnaire: '',
        organisme_tutelle: '',
        date_evaluation: '',
        stade: 'evalue',
        evaluateur_nom: '',
        score_total: null,
        proposition: '',
        recommandations: '',
        validation_sct: 'valide',
        avis_psct: 'valide',
        decision_comite: 'confirme',
      },
      // 16 secteurs de planification
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
      // 8 pôles territoriaux officiels
      polesOptions: [
        'Dakar',
        'Thiès',
        'Diourbel-Louga',
        'Centre (Kaolack, Fatick, Kaffrine)',
        'Nord (Saint-Louis)',
        'Nord-Est (Matam)',
        'Sud (Ziguinchor, Sédhiou, Kolda)',
        'Sud-Est (Tambacounda, Kédougou)',
      ],
      stades: [
        { value: 'evalue',          label: 'Évalué',                 desc: 'Score et proposition rendus' },
        { value: 'valide_sct',      label: 'Validé par le SCT',      desc: 'Le Secrétariat SCT a validé l\'avis' },
        { value: 'valide_psct',     label: 'Validé par Présidence SCT', desc: 'La Présidence SCT a transmis au Comité' },
        { value: 'decision_comite', label: 'Décision Comité rendue', desc: 'Le Comité a entériné ou contesté' },
      ],
    };
  },
  computed: {
    canSubmit() {
      return this.form.titre.trim()
          && this.form.proposition
          && typeof this.form.score_total === 'number'
          && this.form.score_total >= 0
          && this.form.score_total <= 100;
    }
  },
  mounted() {
    this.loadMinisteres();
    this.loadEvaluateurs();
  },
  methods: {
    async loadMinisteres() {
      try {
        const r = await fetch('/api/ministeres');
        if (r.ok) this.ministeres = await r.json();
      } catch (e) { /* fallback : champ vide, pas critique */ }
    },
    async loadEvaluateurs() {
      try {
        const r = await fetch('/api/users');
        if (!r.ok) return;
        const all = await r.json();
        const isEval = u => (u.role || '').startsWith('evaluateur');
        this.evaluateurs = all.filter(isEval).sort((a, b) =>
          (a.display_name || '').localeCompare(b.display_name || '', 'fr', { sensitivity: 'base' })
        );
      } catch (e) { /* idem */ }
    },
    toggleAllPoles() {
      if (this.form.poles.length === this.polesOptions.length) {
        this.form.poles = [];
      } else {
        this.form.poles = [...this.polesOptions];
      }
    },
    onFicheChange(e) { this.fichierEvaluation = e.target.files[0] || null; },
    onAnnexesChange(e) {
      const incoming = Array.from(e.target.files || []);
      this.annexes = [...this.annexes, ...incoming];
      e.target.value = '';
    },
    onFicheDrop(e) {
      this.dragFiche = false;
      const f = e.dataTransfer.files[0];
      if (f) this.fichierEvaluation = f;
    },
    onAnnexesDrop(e) {
      this.dragAnnexes = false;
      const files = Array.from(e.dataTransfer.files || []);
      this.annexes = [...this.annexes, ...files];
    },
    removeAnnexe(i) { this.annexes.splice(i, 1); },
    formatSize(bytes) {
      if (!bytes) return '';
      if (bytes < 1024) return bytes + ' o';
      if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' Ko';
      return (bytes / 1048576).toFixed(1) + ' Mo';
    },

    async submit() {
      if (!this.canSubmit) return;
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      this.loading = true;

      try {
        const fd = new FormData();
        fd.append('role', user.role);
        fd.append('auteur_import', user.username);

        for (const key of [
          'titre','description','secteur','cout_estimatif',
          'duree_annees','structure_soumissionnaire','organisme_tutelle',
          'date_evaluation','stade','evaluateur_nom',
          'score_total','proposition','recommandations',
          'validation_sct','avis_psct','decision_comite'
        ]) {
          if (this.form[key] !== null && this.form[key] !== undefined && this.form[key] !== '') {
            fd.append(key, String(this.form[key]));
          }
        }
        if (this.form.poles.length) {
          fd.append('poles', this.form.poles.join(', '));
        }

        if (this.fichierEvaluation) {
          fd.append('fichier_evaluation', this.fichierEvaluation);
        }
        this.annexes.forEach(f => fd.append('annexes', f));

        const resp = await fetch('/api/admin/import-projet-historique', {
          method: 'POST',
          body: fd,
        });

        if (!resp.ok) {
          const err = await resp.json().catch(() => ({}));
          throw new Error(err.error || "Erreur lors de l'import");
        }

        const result = await resp.json();
        this.$toast.success(result.message || 'Projet importé');
        this.$router.push(`/project/${result.project_id}`);
      } catch (e) {
        this.$toast.error(e.message);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem;
}

/* En-tête */
.dashboard-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.dashboard-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}
.page-desc {
  margin: 0;
  color: #64748b;
  font-size: 0.95rem;
  line-height: 1.55;
}

/* Sections (alignées sur DashboardSoumissionnaire) */
.section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}
.section-header h3 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.step-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, #2E6B6B 0%, #1e4b4b 100%);
  color: #fff;
  border-radius: 50%;
  font-size: 0.9rem;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(46, 107, 107, 0.3);
}

/* Form (réplique de DashboardSoumissionnaire) */
.submit-form { display: flex; flex-direction: column; gap: 1.2rem; }
.form-row { display: grid; gap: 1.2rem; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }
.form-group { display: flex; flex-direction: column; }
.form-group.full-width { grid-column: 1 / -1; }
.form-group label { margin-bottom: 0.5rem; font-weight: 600; color: #2c3e50; font-size: 0.92rem; }
.form-group input,
.form-group textarea,
.form-group select {
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.95rem;
  font-family: inherit;
}
.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus { outline: none; border-color: #2563eb; }
.form-group textarea { resize: vertical; }
.req { color: #dc2626; }
.hint { color: #6b7280; font-size: 0.82rem; margin-top: 0.4rem; }
.hint-success { color: #059669; font-weight: 500; }

/* Pôles checkbox group (repris à l'identique) */
.checkbox-group-poles {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background: #f8fafc;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  max-height: 300px;
  overflow-y: auto;
}
.poles-actions { margin-bottom: 0.5rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e2e8f0; }
.btn-toggle-poles {
  width: 100%; padding: 0.6rem 1rem;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white; border: none; border-radius: 6px;
  font-size: 0.88rem; font-weight: 600; cursor: pointer;
  transition: all 0.2s;
}
.btn-toggle-poles:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}
.checkbox-label-pole {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  background: white; border: 1px solid #e2e8f0; border-radius: 6px;
  cursor: pointer; transition: all 0.2s; font-weight: normal;
}
.checkbox-label-pole:hover { background: #f0f9ff; border-color: #3b82f6; }
.checkbox-label-pole input[type="checkbox"] {
  width: 18px; height: 18px; cursor: pointer; accent-color: #2563eb;
}
.checkbox-label-pole:has(input:checked) { background: #eff6ff; border-color: #3b82f6; }
.checkbox-label-pole input[type="checkbox"]:checked + .checkbox-text {
  color: #1d4ed8; font-weight: 600;
}
.checkbox-text { flex: 1; font-size: 0.92rem; color: #374151; }

/* Drop zone (repris du soumissionnaire, raffiné) */
.drop-zone {
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  padding: 1.75rem 1rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  color: #64748b;
  background: #f8fafc;
}
.drop-zone:hover { border-color: #2563eb; background: #f0f7ff; }
.drop-zone-active { border-color: #2563eb; background: #eff6ff; border-style: solid; }
.dz-icon { font-size: 2.2rem; margin-bottom: 0.4rem; }
.dz-text { font-size: 0.95rem; color: #475569; }
.dz-text strong { color: #2563eb; }
.dz-hint { font-size: 0.8rem; color: #94a3b8; margin-top: 0.3rem; }
.file-list { list-style: none; padding-left: 0; margin: 0.25rem 0 0; text-align: left; }
.file-list li {
  display: flex; align-items: center; justify-content: space-between; gap: 0.75rem;
  padding: 0.5rem 0.75rem; background: white;
  border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 0.4rem;
}
.file-name { flex: 1; font-weight: 500; color: #374151; word-break: break-all; font-size: 0.88rem; }
.file-size { color: #6b7280; font-size: 0.82rem; white-space: nowrap; }
.btn-link {
  background: transparent; border: none; color: #dc2626; cursor: pointer;
  padding: 0.2rem 0.5rem; font-size: 0.85rem; font-weight: 500; border-radius: 4px;
}
.btn-link:hover { background: #fee2e2; }
.dz-add {
  margin-top: 0.5rem; font-size: 0.88rem; color: #2563eb;
  cursor: pointer; padding: 0.4rem; border-top: 1px dashed #e2e8f0; font-weight: 500;
}
.dz-add:hover { color: #1d4ed8; }

/* Sélecteur de stade */
.stade-selector { display: flex; flex-direction: column; gap: 0.6rem; }
.stade-option {
  display: flex; align-items: flex-start; gap: 0.75rem;
  padding: 0.85rem 1rem;
  border: 2px solid #e5e7eb; border-radius: 10px;
  cursor: pointer; transition: all 0.2s;
  background: #fff;
}
.stade-option:hover { border-color: #93c5fd; background: #f0f9ff; }
.stade-option.active {
  border-color: #2563eb;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
}
.stade-option input[type="radio"] { margin-top: 0.25rem; accent-color: #2563eb; }
.stade-label { display: flex; flex-direction: column; }
.stade-label strong { color: #1e293b; font-size: 0.95rem; }
.stade-label small { color: #64748b; font-size: 0.83rem; margin-top: 0.2rem; }

/* Boutons (alignés sur DashboardSoumissionnaire) */
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
  box-shadow: 0 6px 16px rgba(5, 150, 105, 0.4);
}
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-cancel {
  padding: 1rem 2rem;
  background: #e2e8f0; color: #475569;
  border: none; border-radius: 8px;
  font-size: 1rem; font-weight: 600; cursor: pointer;
  transition: all 0.2s;
}
.btn-cancel:hover { background: #cbd5e1; color: #1e293b; }

@media (max-width: 768px) {
  .dashboard-container { padding: 1rem; }
  .section { padding: 1.25rem; }
  .submit-button-wrapper { flex-direction: column-reverse; }
  .btn-submit, .btn-cancel { width: 100%; min-width: 0; }
}
</style>
