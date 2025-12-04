<template>
  <div class="documentheque-container">
    <div class="section-header">
      <h3>📚 Documenthèque du projet</h3>
      <p class="section-description">
        Tous les membres ayant accès au projet peuvent consulter et enrichir cette documenthèque
      </p>
    </div>

    <!-- Formulaire d'ajout simplifié -->
    <div v-if="canAddDocuments" class="add-document-section">
      <h4>➕ Ajouter un document</h4>
      <div class="upload-form">
        <div class="form-group">
          <label>Sélectionner des fichiers</label>
          <input
            type="file"
            ref="filesInput"
            multiple
            @change="selectionnerFichiers"
            accept=".pdf,.doc,.docx,.xlsx,.xls,.jpg,.jpeg,.png,.txt"
          />
          <small>Formats acceptés: PDF, DOC, DOCX, XLSX, XLS, JPG, PNG, TXT</small>
        </div>

        <div v-if="fichiersSelectionnes.length > 0" class="file-selected">
          <p><strong>{{ fichiersSelectionnes.length }} fichier(s) sélectionné(s)</strong></p>
          <ul class="files-preview-list">
            <li v-for="(file, idx) in fichiersSelectionnes" :key="idx" class="file-item">
              <span class="file-info">
                📄 {{ file.name }} ({{ formatTailleFichier(file.size) }})
              </span>
              <button @click="retirerFichier(idx)" class="btn-remove" type="button">×</button>
            </li>
          </ul>
          <button @click="envoyerFichiers" class="btn-upload" :disabled="uploading">
            <span v-if="uploading">⏳ Envoi en cours...</span>
            <span v-else>📤 Envoyer</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Liste des documents -->
    <div class="documents-list">
      <h4>📄 Documents disponibles ({{ documents.length }})</h4>

      <div v-if="loading" class="loading-state">
        <p>Chargement des documents...</p>
      </div>

      <div v-else-if="documents.length === 0" class="empty-state">
        <p>Aucun document pour ce projet</p>
      </div>

      <div v-else class="documents-grid">
        <div v-for="doc in documents" :key="doc.id" class="document-card">
          <div class="document-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14,2 14,8 20,8"/>
            </svg>
          </div>

          <div class="document-content">
            <!-- Première ligne : Nom, taille, badge et bouton supprimer -->
            <div class="document-main-row">
              <h5 class="document-name" @click="ouvrirDocument(doc)" :title="doc.nom_original">
                {{ doc.nom_original }}
              </h5>
              <div class="document-meta">
                <span class="document-size">{{ formatTailleFichier(doc.taille_fichier) }}</span>
                <span v-if="doc.type_document === 'initial'" class="document-badge initial">
                  📎 Soumission initiale
                </span>
                <span v-if="doc.type_document === 'fiche_evaluation_archivee'" class="document-badge archivee">
                  📋 Fiche d'évaluation archivée
                </span>
              </div>
              <button
                v-if="canDeleteDocument(doc)"
                @click="supprimerDocument(doc)"
                class="btn-action btn-delete"
                title="Supprimer"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
                Supprimer
              </button>
            </div>

            <!-- Deuxième ligne : Auteur et date -->
            <div class="document-info-row">
              <span class="document-author">
                {{ doc.type_document === 'fiche_evaluation_archivee' ? 'Édité par' : 'Ajouté par' }} <strong>{{ doc.auteur_display_name || doc.auteur_nom }}</strong> ({{ getRoleLabel(doc.auteur_role) }})
              </span>
              <span class="document-date">{{ formatDate(doc.date_ajout) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DocumenthequeProjet',
  props: {
    projectId: {
      type: Number,
      required: true
    },
    piecesJointesInitiales: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      documents: [],
      loading: true,
      uploading: false,
      currentUser: null,
      fichiersSelectionnes: []
    };
  },
  computed: {
    canAddDocuments() {
      if (!this.currentUser) return false;
      return true;
    }
  },
  async mounted() {
    this.currentUser = JSON.parse(localStorage.getItem('user') || 'null');
    await this.chargerDocuments();
  },
  methods: {
    async chargerDocuments() {
      try {
        this.loading = true;
        // Passer le rôle et username pour le filtrage côté serveur
        const params = new URLSearchParams();
        if (this.currentUser) {
          params.append('role', this.currentUser.role);
          params.append('username', this.currentUser.username);
        }
        const response = await fetch(`/api/projects/${this.projectId}/documents?${params.toString()}`);
        if (response.ok) {
          const allDocs = await response.json();
          // Filtrer les fiches archivées qui sont affichées dans une section séparée
          this.documents = allDocs.filter(doc => doc.type_document !== 'fiche_evaluation_archivee');
        } else {
          console.error('Erreur lors du chargement des documents');
        }
      } catch (error) {
        console.error('Erreur:', error);
      } finally {
        this.loading = false;
      }
    },

    selectionnerFichiers(event) {
      const newFiles = Array.from(event.target.files);
      if (newFiles.length > 0) {
        // Ajouter les nouveaux fichiers aux fichiers déjà sélectionnés
        // Éviter les doublons basés sur le nom et la taille
        const existing = new Set(
          this.fichiersSelectionnes.map(f => `${f.name}-${f.size}`)
        );

        const uniqueNewFiles = newFiles.filter(
          f => !existing.has(`${f.name}-${f.size}`)
        );

        this.fichiersSelectionnes = [...this.fichiersSelectionnes, ...uniqueNewFiles];
      }
    },

    retirerFichier(index) {
      this.fichiersSelectionnes.splice(index, 1);
      // Ne pas réinitialiser l'input pour permettre d'ajouter d'autres fichiers
    },

    async envoyerFichiers() {
      if (this.fichiersSelectionnes.length === 0) {
        alert('Veuillez sélectionner au moins un fichier');
        return;
      }

      if (!this.currentUser) {
        alert('Erreur: utilisateur non connecté');
        return;
      }

      try {
        this.uploading = true;

        const formData = new FormData();
        formData.append('auteur_nom', this.currentUser.username);
        formData.append('auteur_role', this.currentUser.role);
        formData.append('description', '');
        formData.append('type_document', 'document');

        // Ajouter tous les fichiers sélectionnés
        this.fichiersSelectionnes.forEach(file => {
          formData.append('files', file);
        });

        const response = await fetch(`/api/projects/${this.projectId}/documents`, {
          method: 'POST',
          body: formData
        });

        if (response.ok) {
          // Réinitialiser
          this.fichiersSelectionnes = [];
          if (this.$refs.filesInput) {
            this.$refs.filesInput.value = '';
          }

          // Recharger la liste
          await this.chargerDocuments();
        } else {
          const error = await response.json();
          alert('Erreur: ' + (error.error || 'Problème lors de l\'ajout'));
        }
      } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur de connexion');
      } finally {
        this.uploading = false;
      }
    },

    async supprimerDocument(doc) {
      if (!confirm(`Êtes-vous sûr de vouloir supprimer "${doc.nom_original}" ?`)) {
        return;
      }

      try {
        const response = await fetch(
          `/api/projects/${this.projectId}/documents/${doc.id}?auteur_nom=${this.currentUser.username}&role=${this.currentUser.role}`,
          { method: 'DELETE' }
        );

        if (response.ok) {
          await this.chargerDocuments();
        } else {
          const error = await response.json();
          alert('Erreur: ' + (error.error || 'Problème lors de la suppression'));
        }
      } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur de connexion');
      }
    },

    ouvrirDocument(doc) {
      // En production sur Render, utiliser l'URL backend complète
      const isProduction = window.location.hostname.includes('render.com');
      const backendUrl = isProduction
        ? 'https://maturation-backend.onrender.com'
        : '';

      // Les fiches archivées utilisent un endpoint différent
      if (doc.type_document === 'fiche_evaluation_archivee') {
        const url = `${backendUrl}/api/archives/fiches_evaluation/${doc.nom_fichier}`;
        window.open(url, '_blank');
      } else {
        const url = `${backendUrl}/api/uploads/${doc.nom_fichier}`;
        window.open(url, '_blank');
      }
    },

    canDeleteDocument(doc) {
      if (!this.currentUser) return false;
      // Ne pas permettre la suppression des pièces jointes initiales
      if (doc.type_document === 'initial') return false;
      // Les fiches d'évaluation archivées ne peuvent être supprimées que par un admin
      if (doc.type_document === 'fiche_evaluation_archivee') {
        return this.currentUser.role === 'admin';
      }
      // Admin ou auteur peut supprimer les autres documents
      return this.currentUser.role === 'admin' || this.currentUser.username === doc.auteur_nom;
    },

    formatTailleFichier(bytes) {
      if (!bytes) return 'N/A';
      const kb = bytes / 1024;
      if (kb < 1024) {
        return kb.toFixed(1) + ' KB';
      }
      const mb = kb / 1024;
      return mb.toFixed(1) + ' MB';
    },

    formatDate(dateStr) {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleString('fr-FR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    getRoleLabel(role) {
      const labels = {
        'soumissionnaire': 'Soumissionnaire',
        'evaluateur': 'Évaluateur',
        'evaluateur1': 'Évaluateur 1',
        'evaluateur2': 'Évaluateur 2',
        'secretariatsct': 'Secrétariat SCT',
        'presidencesct': 'Présidence SCT',
        'presidencecomite': 'Présidence Comité',
        'admin': 'Administrateur'
      };
      return labels[role] || role;
    }
  }
};
</script>

<style scoped>
.documentheque-container {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1.5rem 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.section-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e0f2fe;
}

.section-header h3 {
  color: #1e3a8a;
  margin: 0 0 0.5rem 0;
}

.section-description {
  color: #64748b;
  font-size: 0.9rem;
  margin: 0;
}

.add-document-section {
  background: #f8fafc;
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.add-document-section h4 {
  color: #1e40af;
  margin: 0 0 1rem 0;
}

.upload-form .form-group {
  margin-bottom: 0.5rem;
}

.upload-form label {
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.upload-form input[type="file"] {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.95rem;
}

.upload-form small {
  display: block;
  margin-top: 0.25rem;
  color: #64748b;
  font-size: 0.85rem;
}

.file-selected {
  margin-top: 1rem;
  padding: 1rem;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
}

.file-selected p {
  margin: 0 0 0.5rem 0;
  color: #0c4a6e;
  font-weight: 600;
}

.files-preview-list {
  margin: 0 0 1rem 0;
  padding-left: 1.5rem;
  color: #475569;
  font-size: 0.9rem;
}

.files-preview-list li {
  margin-bottom: 0.25rem;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.file-info {
  flex: 1;
}

.btn-remove {
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 4px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.2rem;
  font-weight: bold;
  line-height: 1;
  padding: 0;
  transition: all 0.2s;
}

.btn-remove:hover {
  background: #dc2626;
}

.btn-upload {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-upload:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-upload:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.documents-list h4 {
  color: #1e293b;
  margin: 0 0 1rem 0;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 3rem;
  color: #64748b;
}

.documents-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.document-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  transition: all 0.3s;
  display: flex;
  gap: 1rem;
}

.document-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-color: #3b82f6;
}

.document-icon {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  background: #dbeafe;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1e40af;
  align-self: flex-start;
}

.document-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.document-main-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.document-name {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e293b;
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 200px;
}

.document-name:hover {
  color: #3b82f6;
  text-decoration: underline;
}

.document-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.8rem;
  color: #64748b;
  flex-shrink: 0;
}

.document-size {
  white-space: nowrap;
}

.document-badge {
  padding: 0.125rem 0.5rem;
  background: #e0f2fe;
  color: #0369a1;
  border-radius: 4px;
  font-weight: 500;
  font-size: 0.75rem;
  white-space: nowrap;
}

.document-badge.initial {
  background: #fef3c7;
  color: #92400e;
}

.document-badge.archivee {
  background: #e0e7ff;
  color: #3730a3;
}

.document-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: #64748b;
  gap: 1rem;
}

.document-author {
  flex: 1;
}

.document-author strong {
  color: #1e293b;
}

.document-date {
  white-space: nowrap;
}

.btn-action {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0.35rem 0.65rem;
  border: none;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-delete {
  background: #fee2e2;
  color: #dc2626;
}

.btn-delete:hover {
  background: #ef4444;
  color: white;
}

@media (max-width: 768px) {
  .document-main-row {
    flex-wrap: wrap;
  }

  .document-name {
    flex-basis: 100%;
    margin-bottom: 0.5rem;
  }

  .document-info-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>
