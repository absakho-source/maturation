<template>
  <PageWrapper>
    <div class="import-page">
      <h2>📥 Importer un projet historique</h2>
      <p class="page-desc">
        Saisir un projet évalué avant l'existence de la plateforme.
        Il sera créé directement au stade choisi et marqué « Import historique ».
      </p>

      <form @submit.prevent="submit" class="import-form">

        <!-- ─── SECTION 1 : Informations du projet ─── -->
        <fieldset>
          <legend><span class="step-num">1</span> Informations du projet</legend>

          <div class="form-group">
            <label>Titre du projet <span class="req">*</span></label>
            <input v-model="form.titre" required placeholder="Ex: Programme d'irrigation du bassin du fleuve Sénégal" />
          </div>

          <div class="form-group">
            <label>Secteur de planification</label>
            <select v-model="form.secteur">
              <option value="">— Sélectionner —</option>
              <option v-for="s in secteurs" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>

          <div class="form-group">
            <label>Pôles territoriaux concernés</label>
            <div class="poles-grid">
              <label v-for="p in polesOptions" :key="p" class="pole-check">
                <input type="checkbox" :value="p" v-model="form.poles" />
                <span>{{ p }}</span>
              </label>
            </div>
            <small class="hint" v-if="form.poles.length">{{ form.poles.length }} pôle(s) sélectionné(s)</small>
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea v-model="form.description" rows="4" placeholder="Résumé du projet..."></textarea>
          </div>

          <div class="row-2">
            <div class="form-group">
              <label>Coût estimatif (FCFA)</label>
              <input v-model="form.cout_estimatif" type="number" min="0" placeholder="Ex: 5000000000" />
            </div>
            <div class="form-group">
              <label>Durée (années)</label>
              <input v-model="form.duree_annees" type="number" min="0" placeholder="Ex: 3" />
            </div>
          </div>

          <div class="form-group">
            <label>Structure soumissionnaire</label>
            <input v-model="form.structure_soumissionnaire" placeholder="Ex: Direction générale de la Santé" />
          </div>

          <div class="form-group">
            <label>Ministère de tutelle</label>
            <select v-model="form.organisme_tutelle">
              <option value="">— Sélectionner un ministère —</option>
              <option v-for="m in ministeres" :key="m.id" :value="m.nom_complet">{{ m.nom_complet }}</option>
            </select>
            <small v-if="!ministeres.length" class="hint">Liste indisponible — saisir manuellement plus bas si besoin</small>
          </div>

          <div class="form-group">
            <label>Auteur / soumissionnaire original</label>
            <input v-model="form.auteur_original" placeholder="Ex: Direction de l'Agriculture" />
          </div>
        </fieldset>

        <!-- ─── SECTION 2 : Stade d'arrivée ─── -->
        <fieldset>
          <legend><span class="step-num">2</span> Stade d'avancement</legend>

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
        </fieldset>

        <!-- ─── SECTION 3 : Évaluation ─── -->
        <fieldset>
          <legend><span class="step-num">3</span> Évaluation</legend>

          <div class="row-2">
            <div class="form-group">
              <label>Évaluateur</label>
              <input v-model="form.evaluateur_nom" placeholder="Nom de l'évaluateur" />
            </div>
            <div class="form-group">
              <label>Score total (/100) <span class="req">*</span></label>
              <input v-model.number="form.score_total" type="number" min="0" max="100" step="0.5" required />
            </div>
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

          <div class="form-group">
            <label>Recommandation générale</label>
            <textarea v-model="form.recommandations" rows="3" placeholder="Recommandations de la Commission..."></textarea>
          </div>

          <!-- Drop zone : fiche d'évaluation -->
          <div class="form-group">
            <label>Fiche d'évaluation (PDF/Word)</label>
            <div class="dropzone" :class="{ dragover: dragFiche }"
                 @click="$refs.ficheInput.click()"
                 @dragover.prevent="dragFiche = true"
                 @dragleave.prevent="dragFiche = false"
                 @drop.prevent="onFicheDrop">
              <input ref="ficheInput" type="file" accept=".pdf,.doc,.docx,.odt"
                     @change="onFicheChange" hidden />
              <template v-if="!fichierEvaluation">
                <div class="dz-icon">📄</div>
                <div class="dz-text">Glisser-déposer ici ou <strong>cliquer pour parcourir</strong></div>
                <div class="dz-hint">PDF, Word, OpenDocument</div>
              </template>
              <template v-else>
                <div class="file-row">
                  <span class="file-name">📄 {{ fichierEvaluation.name }}</span>
                  <span class="file-size">{{ formatSize(fichierEvaluation.size) }}</span>
                  <button type="button" class="btn-remove" @click.stop="fichierEvaluation = null">✕</button>
                </div>
              </template>
            </div>
          </div>

          <!-- Drop zone : annexes -->
          <div class="form-group">
            <label>Annexes (optionnel)</label>
            <div class="dropzone" :class="{ dragover: dragAnnexes }"
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
                <div class="file-row" v-for="(f, i) in annexes" :key="i">
                  <span class="file-name">📎 {{ f.name }}</span>
                  <span class="file-size">{{ formatSize(f.size) }}</span>
                  <button type="button" class="btn-remove" @click.stop="removeAnnexe(i)">✕</button>
                </div>
                <div class="dz-add" @click.stop="$refs.annexesInput.click()">+ Ajouter d'autres fichiers</div>
              </template>
            </div>
          </div>
        </fieldset>

        <!-- ─── SECTION 4 : Validations (selon stade) ─── -->
        <fieldset v-if="form.stade !== 'evalue'">
          <legend><span class="step-num">4</span> Validations hiérarchiques</legend>

          <div class="form-group" v-if="['valide_sct','valide_psct','decision_comite'].includes(form.stade)">
            <label>Validation Secrétariat SCT</label>
            <select v-model="form.validation_sct">
              <option value="valide">Validé</option>
              <option value="rejete">Rejeté</option>
            </select>
          </div>

          <div class="form-group" v-if="['valide_psct','decision_comite'].includes(form.stade)">
            <label>Avis Présidence SCT</label>
            <select v-model="form.avis_psct">
              <option value="valide">Validé</option>
              <option value="rejete">Rejeté</option>
            </select>
          </div>

          <div class="form-group" v-if="form.stade === 'decision_comite'">
            <label>Décision du Comité</label>
            <select v-model="form.decision_comite">
              <option value="confirme">Entériné (confirmé)</option>
              <option value="conteste">Contesté</option>
            </select>
          </div>
        </fieldset>

        <!-- ─── Soumission ─── -->
        <div class="form-actions">
          <button type="button" class="btn-secondary" @click="$router.back()">Annuler</button>
          <button type="submit" class="btn-primary" :disabled="loading || !canSubmit">
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
      form: {
        titre: '',
        description: '',
        secteur: '',
        poles: [],
        cout_estimatif: null,
        duree_annees: null,
        structure_soumissionnaire: '',
        organisme_tutelle: '',
        auteur_original: '',
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
  },
  methods: {
    async loadMinisteres() {
      try {
        const r = await fetch('/api/ministeres');
        if (r.ok) this.ministeres = await r.json();
      } catch (e) {
        // Liste indisponible — l'utilisateur peut taper manuellement via le placeholder
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
    removeAnnexe(i) {
      this.annexes.splice(i, 1);
    },
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

        // Champs projet
        for (const key of [
          'titre','description','secteur','cout_estimatif',
          'duree_annees','structure_soumissionnaire','organisme_tutelle',
          'auteur_original','stade','evaluateur_nom','score_total',
          'proposition','recommandations','validation_sct','avis_psct','decision_comite'
        ]) {
          if (this.form[key] !== null && this.form[key] !== undefined && this.form[key] !== '') {
            fd.append(key, String(this.form[key]));
          }
        }
        // Pôles : tableau → chaîne séparée par virgules
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
.import-page { max-width: 860px; margin: 0 auto; }
.page-desc { color: #64748b; margin-bottom: 1.5rem; line-height: 1.5; }

fieldset {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.25rem;
  background: #fff;
}
legend {
  font-weight: 600;
  color: #1e293b;
  font-size: 1.05rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0 0.5rem;
}
.step-num {
  display: inline-flex; align-items: center; justify-content: center;
  width: 26px; height: 26px; background: #2E6B6B; color: #fff;
  border-radius: 50%; font-size: 0.85rem; font-weight: 700; flex-shrink: 0;
}

.form-group { margin-bottom: 0.85rem; }
.form-group label { display: block; font-weight: 500; font-size: 0.9rem; color: #334155; margin-bottom: 0.3rem; }
.req { color: #dc2626; }
.hint { display: block; font-size: 0.8rem; color: #64748b; margin-top: 0.3rem; }

input[type="text"], input[type="number"], input[type="email"],
select, textarea {
  width: 100%; padding: 0.6rem 0.75rem;
  border: 2px solid #cbd5e1; border-radius: 8px;
  font-size: 0.9rem; font-family: inherit; box-sizing: border-box;
}
input:focus, select:focus, textarea:focus { outline: none; border-color: #0ea5e9; }
textarea { resize: vertical; }

.row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
@media (max-width: 600px) { .row-2 { grid-template-columns: 1fr; } }

/* Pôles checkbox grid */
.poles-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.4rem 0.85rem;
  padding: 0.5rem 0.75rem;
  border: 2px solid #cbd5e1;
  border-radius: 8px;
  background: #f8fafc;
}
.pole-check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.88rem;
  cursor: pointer;
  color: #334155;
}
.pole-check input[type="checkbox"] { accent-color: #2E6B6B; }
@media (max-width: 600px) { .poles-grid { grid-template-columns: 1fr; } }

/* Drop zone */
.dropzone {
  border: 2px dashed #cbd5e1;
  border-radius: 10px;
  padding: 1.5rem 1rem;
  text-align: center;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.2s;
}
.dropzone:hover { border-color: #2E6B6B; background: #f0fdfa; }
.dropzone.dragover { border-color: #2E6B6B; background: #ccfbf1; border-style: solid; }
.dz-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.dz-text { font-size: 0.95rem; color: #475569; }
.dz-text strong { color: #2E6B6B; }
.dz-hint { font-size: 0.8rem; color: #94a3b8; margin-top: 0.3rem; }
.file-row {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin-bottom: 0.4rem;
  text-align: left;
}
.file-name { flex: 1; color: #1e293b; font-size: 0.88rem; word-break: break-all; }
.file-size { color: #94a3b8; font-size: 0.78rem; }
.btn-remove {
  border: none; background: transparent; color: #dc2626;
  cursor: pointer; font-size: 1rem; padding: 0.2rem 0.4rem; border-radius: 4px;
}
.btn-remove:hover { background: #fee2e2; }
.dz-add {
  margin-top: 0.3rem; font-size: 0.85rem; color: #2E6B6B; cursor: pointer;
  padding: 0.4rem; border-top: 1px dashed #e2e8f0;
}
.dz-add:hover { background: #f0fdfa; }

/* Sélecteur de stade */
.stade-selector { display: flex; flex-direction: column; gap: 0.5rem; }
.stade-option {
  display: flex; align-items: flex-start; gap: 0.75rem;
  padding: 0.75rem 1rem; border: 2px solid #e2e8f0; border-radius: 10px;
  cursor: pointer; transition: border-color 0.2s, background 0.2s;
}
.stade-option:hover { border-color: #94a3b8; }
.stade-option.active { border-color: #2E6B6B; background: #f0fdfa; }
.stade-option input[type="radio"] { margin-top: 0.25rem; accent-color: #2E6B6B; }
.stade-label { display: flex; flex-direction: column; }
.stade-label strong { color: #1e293b; font-size: 0.95rem; }
.stade-label small { color: #64748b; font-size: 0.82rem; margin-top: 0.15rem; }

/* Actions */
.form-actions {
  display: flex; gap: 0.75rem; justify-content: flex-end;
  margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e2e8f0;
}
.btn-primary, .btn-secondary {
  padding: 0.7rem 1.3rem; border-radius: 8px;
  font-weight: 600; font-size: 0.95rem; cursor: pointer; border: none;
}
.btn-primary { background: #2E6B6B; color: #fff; }
.btn-primary:hover:not(:disabled) { background: #1e4b4b; }
.btn-primary:disabled { opacity: 0.55; cursor: not-allowed; }
.btn-secondary { background: #e2e8f0; color: #1e293b; }
.btn-secondary:hover { background: #cbd5e1; }
</style>
