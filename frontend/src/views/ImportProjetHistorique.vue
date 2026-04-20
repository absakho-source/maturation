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

          <div class="row-2">
            <div class="form-group">
              <label>Secteur</label>
              <select v-model="form.secteur">
                <option value="">— Sélectionner —</option>
                <option v-for="s in secteurs" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Pôle(s) territorial(aux)</label>
              <input v-model="form.poles" placeholder="Ex: Centre (Dakar, Diourbel, Thiès)" />
            </div>
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

          <div class="row-2">
            <div class="form-group">
              <label>Structure soumissionnaire</label>
              <input v-model="form.structure_soumissionnaire" placeholder="Ex: Ministère de l'Agriculture" />
            </div>
            <div class="form-group">
              <label>Organisme de tutelle</label>
              <input v-model="form.organisme_tutelle" placeholder="Ex: Ministère de l'Économie" />
            </div>
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

          <div class="form-group">
            <label>📎 Fichier d'évaluation (PDF/Word)</label>
            <input type="file" @change="onFichierChange" accept=".pdf,.doc,.docx,.odt" />
          </div>
          <div class="form-group">
            <label>📎 Annexes (optionnel)</label>
            <input type="file" multiple @change="onAnnexesChange" />
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
      form: {
        titre: '',
        description: '',
        secteur: '',
        poles: '',
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
      secteurs: [
        'agriculture-elevage-peche',
        'industrie-mines',
        'energie',
        'transport-infrastructure',
        'eau-assainissement',
        'sante',
        'education-formation',
        'tourisme-culture',
        'environnement-changement-climatique',
        'numerique-innovation',
        'gouvernance-institutions',
        'urbanisme-habitat',
        'protection-sociale',
        'emploi-jeunesse',
        'commerce-secteur-prive',
        'autre',
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
  methods: {
    onFichierChange(e) { this.fichierEvaluation = e.target.files[0] || null; },
    onAnnexesChange(e) { this.annexes = Array.from(e.target.files || []); },

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
          'titre','description','secteur','poles','cout_estimatif',
          'duree_annees','structure_soumissionnaire','organisme_tutelle',
          'auteur_original','stade','evaluateur_nom','score_total',
          'proposition','recommandations','validation_sct','avis_psct','decision_comite'
        ]) {
          if (this.form[key] !== null && this.form[key] !== undefined && this.form[key] !== '') {
            fd.append(key, String(this.form[key]));
          }
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
