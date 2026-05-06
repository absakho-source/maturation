<template>
  <div>
    <div v-if="sortedProjects.length === 0" class="empty-state">
      <p>{{ emptyMessage || 'Aucun projet' }}</p>
    </div>

    <div v-else class="table-wrap">
      <table class="projects-table">
        <thead>
          <tr>
            <th @click="sortBy('numero_projet')" :class="{active: sortKey==='numero_projet'}">N° {{ sortIcon('numero_projet') }}</th>
            <th @click="sortBy('titre')" :class="{active: sortKey==='titre'}">Projet {{ sortIcon('titre') }}</th>
            <th v-if="cols.secteur" @click="sortBy('secteur')" :class="{active: sortKey==='secteur'}">Secteur {{ sortIcon('secteur') }}</th>
            <th v-if="cols.cout" @click="sortBy('cout_estimatif')" :class="{active: sortKey==='cout_estimatif'}" class="th-num">Coût {{ sortIcon('cout_estimatif') }}</th>
            <th v-if="cols.evaluateur" @click="sortBy('evaluateur_nom')" :class="{active: sortKey==='evaluateur_nom'}">Évaluateur {{ sortIcon('evaluateur_nom') }}</th>
            <th @click="sortBy('statut')" :class="{active: sortKey==='statut'}">Statut</th>
            <th v-if="cols.actions"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in paginatedProjects" :key="p.id" @click="onRowClick(p)" class="row-click">
            <td class="td-num">{{ p.numero_projet || '—' }}</td>
            <td class="td-titre">
              <div class="titre-cell">
                <span>{{ p.titre }}</span>
                <small>{{ p.structure_soumissionnaire || p.organisme_tutelle || p.auteur_nom || '—' }}</small>
              </div>
            </td>
            <td v-if="cols.secteur">{{ secteurLabel(p.secteur) }}</td>
            <td v-if="cols.cout" class="td-num">{{ p.cout_estimatif ? formatCurrency(p.cout_estimatif) : '—' }}</td>
            <td v-if="cols.evaluateur">{{ p.evaluateur_nom || '—' }}</td>
            <td><span class="statut-pill" :class="getStatusClass(displayStatut(p))">{{ displayStatut(p) }}</span></td>
            <td v-if="cols.actions" class="td-actions" @click.stop>
              <slot name="actions" :project="p">
                <button @click="onRowClick(p)" class="btn-view-sm" title="Détails">👁️</button>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button @click="page = Math.max(1, page-1)" :disabled="page === 1">‹</button>
      <span>Page {{ page }} / {{ totalPages }} ({{ sortedProjects.length }} projets)</span>
      <button @click="page = Math.min(totalPages, page+1)" :disabled="page === totalPages">›</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProjectTable',
  props: {
    projects: { type: Array, default: () => [] },
    columns: { type: Object, default: () => ({}) },
    perPage: { type: Number, default: 1000 },
    defaultSort: { type: String, default: 'numero_projet' },
    defaultDir: { type: String, default: 'desc' },
    emptyMessage: { type: String, default: '' },
    rowClickable: { type: Boolean, default: true },
  },
  data() {
    return {
      sortKey: this.defaultSort,
      sortDir: this.defaultDir,
      page: 1,
    };
  },
  computed: {
    cols() {
      return {
        secteur: true,
        cout: true,
        evaluateur: false,
        avis: true,
        actions: true,
        ...this.columns,
      };
    },
    sortedProjects() {
      const list = [...this.projects];
      const k = this.sortKey;
      const dir = this.sortDir === 'asc' ? 1 : -1;
      list.sort((a, b) => {
        const va = a[k] ?? '';
        const vb = b[k] ?? '';
        if (typeof va === 'number' && typeof vb === 'number') return (va - vb) * dir;
        return String(va).localeCompare(String(vb), 'fr', { sensitivity: 'base' }) * dir;
      });
      return list;
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.sortedProjects.length / this.perPage));
    },
    paginatedProjects() {
      const start = (this.page - 1) * this.perPage;
      return this.sortedProjects.slice(start, start + this.perPage);
    }
  },
  watch: {
    projects() { this.page = 1; }
  },
  methods: {
    onRowClick(p) {
      if (this.rowClickable) this.$router.push(`/project/${p.id}`);
      this.$emit('row-click', p);
    },
    sortBy(key) {
      if (this.sortKey === key) {
        this.sortDir = this.sortDir === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortKey = key;
        this.sortDir = 'asc';
      }
    },
    sortIcon(key) {
      if (this.sortKey !== key) return '';
      return this.sortDir === 'asc' ? '▲' : '▼';
    },
    secteurLabel(s) {
      if (!s) return '—';
      return s.length > 28 ? s.substring(0, 26) + '…' : s;
    },
    formatCurrency(v) {
      if (!v) return '—';
      return new Intl.NumberFormat('fr-FR').format(v) + ' F CFA';
    },
    avisShort(a) {
      if (!a) return '—';
      const map = {
        'favorable': 'Favorable',
        'favorable sous conditions': 'Sous cond.',
        'défavorable': 'Défavorable',
      };
      return map[a] || a;
    },
    getAvisClass(a) {
      if (a === 'favorable') return 'avis-favorable';
      if (a === 'favorable sous conditions') return 'avis-conditions';
      if (a === 'défavorable') return 'avis-defavorable';
      return '';
    },
    displayStatut(p) {
      // Décision finale du Comité rendue → afficher l'avis lui-même
      if (p.decision_finale === 'confirme') {
        const map = { 'favorable': 'Favorable', 'favorable sous conditions': 'Sous conditions', 'défavorable': 'Défavorable' };
        return map[p.avis] || 'Décision rendue';
      }
      // Comité a rejeté l'avis → projet à réétudier
      if (p.decision_finale === 'conteste') return 'À réétudier';
      // À l'ordre du jour
      if (p.ordre_du_jour && !p.ordre_du_jour_rejete) return 'Ordre du jour';
      // Si statut == avis (cas redondant), afficher "Évalué"
      const avisVals = ['favorable', 'favorable sous conditions', 'défavorable'];
      if (avisVals.includes(p.statut)) return 'Évalué';
      return p.statut || '—';
    },
    getStatusClass(s) {
      // Mapping étendu pour les nouveaux libellés
      const extra = {
        'Favorable': 'avis-favorable',
        'Sous conditions': 'avis-conditions',
        'Défavorable': 'avis-defavorable',
        'À réétudier': 'status-pending',
        'Ordre du jour': 'status-pending',
        'Évalué': 'status-evaluated',
        'Décision rendue': 'status-validated',
      };
      if (extra[s]) return extra[s];
      return this.getStatusClassRaw(s);
    },
    getStatusClassRaw(s) {
      const m = {
        'soumis': 'status-new',
        'assigné': 'status-assigned',
        'en évaluation': 'status-processing',
        'évalué': 'status-evaluated',
        'compléments demandés': 'status-complement',
        'compléments fournis': 'status-info',
        'rejeté': 'status-defavorable',
        'avis défavorable confirmé': 'status-defavorable',
        'en attente validation presidencesct': 'status-pending',
        'validé par presidencesct': 'status-validated-sec',
        'validé par presidencecomite': 'status-validated',
        'en réexamen par le Secrétariat SCT': 'status-processing',
      };
      return m[s] || 'status-default';
    },
  }
}
</script>

<style scoped>
.empty-state { text-align: center; padding: 3rem; color: #94a3b8; }

.table-wrap { overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 10px; background: #fff; }
.projects-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.projects-table th, .projects-table td { padding: 0.6rem 0.75rem; text-align: left; border-bottom: 1px solid #e2e8f0; vertical-align: middle; }
.projects-table th { background: #f8fafc; color: #475569; font-weight: 600; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.5px; cursor: pointer; user-select: none; white-space: nowrap; }
.projects-table th:hover { background: #f1f5f9; }
.projects-table th.active { color: #2E6B6B; }
.projects-table .th-num { text-align: right; }
.projects-table tr.row-click { cursor: pointer; transition: background 0.15s; }
.projects-table tr.row-click:hover { background: #f0fdfa; }
.projects-table .td-num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.projects-table .td-titre { max-width: 360px; }
.projects-table .td-actions { white-space: nowrap; }
.titre-cell { display: flex; flex-direction: column; line-height: 1.25; }
.titre-cell span { font-weight: 500; color: #1e293b; }
.titre-cell small { color: #64748b; font-size: 0.78rem; margin-top: 0.15rem; }

.statut-pill, .avis-pill { padding: 0.15rem 0.55rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600; white-space: nowrap; display: inline-block; }
.avis-pill.avis-favorable { background: #d1fae5; color: #065f46; }
.avis-pill.avis-conditions { background: #fef3c7; color: #92400e; }
.avis-pill.avis-defavorable { background: #fee2e2; color: #991b1b; }

.statut-pill.status-new { background: #dbeafe; color: #1e40af; }
.statut-pill.status-assigned { background: #e0e7ff; color: #3730a3; }
.statut-pill.status-processing { background: #fef9c3; color: #854d0e; }
.statut-pill.status-evaluated { background: #d1fae5; color: #065f46; }
.statut-pill.status-complement { background: #fce7f3; color: #9d174d; }
.statut-pill.status-info { background: #cffafe; color: #155e75; }
.statut-pill.status-defavorable { background: #fee2e2; color: #991b1b; }
.statut-pill.status-pending { background: #fef3c7; color: #92400e; }
.statut-pill.status-validated-sec { background: #d1fae5; color: #047857; }
.statut-pill.status-validated { background: #bbf7d0; color: #14532d; }
.statut-pill.status-default { background: #e2e8f0; color: #475569; }

/* Statut affichant l'avis lui-même (décision finale rendue) — couleurs dédiées */
.statut-pill.avis-favorable { background: #d1fae5; color: #065f46; }
.statut-pill.avis-conditions { background: #fef3c7; color: #92400e; }
.statut-pill.avis-defavorable { background: #fee2e2; color: #991b1b; }

.btn-view-sm { padding: 0.25rem 0.5rem; background: transparent; border: 1px solid #cbd5e1; border-radius: 6px; cursor: pointer; font-size: 0.95rem; }
.btn-view-sm:hover { background: #f1f5f9; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 0.75rem; margin-top: 1rem; color: #64748b; font-size: 0.9rem; }
.pagination button { padding: 0.4rem 0.7rem; border: 1px solid #cbd5e1; background: #fff; border-radius: 6px; cursor: pointer; }
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
.pagination button:hover:not(:disabled) { background: #f1f5f9; }
</style>
