<template>
  <div class="discussion-projet">
    <div class="discussion-header">
      <h3>💬 Discussion du projet</h3>
      <p class="description">
        Espace de discussion entre le soumissionnaire et le comité d'évaluation
      </p>
    </div>

    <!-- Liste des messages -->
    <div class="messages-container">
      <div v-if="loading" class="loading-state">
        <p>Chargement des messages...</p>
      </div>

      <div v-else-if="messages.length === 0" class="empty-state">
        <p>Aucun message pour le moment. Soyez le premier à démarrer la discussion!</p>
      </div>

      <div v-else class="messages-list">
        <div
          v-for="message in messages"
          :key="message.id"
          :class="['message-card', getMessageClass(message)]"
        >
          <div class="message-header">
            <div class="message-author">
              <div class="author-avatar" :style="{ background: getRoleColor(message.auteur_role) }">
                {{ getInitials(message.auteur_nom) }}
              </div>
              <div class="author-info">
                <strong>{{ message.auteur_display_name || message.auteur_nom }}</strong>
                <span class="author-role">{{ getRoleLabel(message.auteur_role) }}</span>
              </div>
            </div>
            <div class="message-meta">
              <span class="message-date">{{ formatDate(message.date_creation) }}</span>
              <button
                v-if="canDeleteMessage(message)"
                @click="supprimerMessage(message)"
                class="btn-delete-message"
                title="Supprimer"
              >
                ×
              </button>
            </div>
          </div>
          <div class="message-content" v-if="message.contenu">
            {{ message.contenu }}
          </div>
          <!-- Fichiers joints (nouvelle version) -->
          <div v-if="message.fichiers && message.fichiers.length > 0" class="message-attachments">
            <div v-for="fichier in message.fichiers" :key="fichier.id" class="message-attachment">
              <a :href="getFileUrl(fichier.nom_fichier)" target="_blank" class="attachment-link">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
                </svg>
                {{ fichier.nom_original }}
                <span class="attachment-size">({{ formatTailleFichier(fichier.taille_fichier) }})</span>
              </a>
            </div>
          </div>
          <!-- Fichier joint ancien format (compatibilité) -->
          <div v-else-if="message.fichier_joint" class="message-attachments">
            <div class="message-attachment">
              <a :href="getFileUrl(message.fichier_joint)" target="_blank" class="attachment-link">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
                </svg>
                {{ message.fichier_joint_original }}
                <span class="attachment-size">({{ formatTailleFichier(message.fichier_joint_taille) }})</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Formulaire d'ajout de message -->
    <div v-if="canAddMessage" class="message-form">
      <textarea
        v-model="nouveauMessage"
        placeholder="Écrivez votre message ici..."
        rows="3"
        :disabled="sending"
        @keydown.ctrl.enter="envoyerMessage"
      ></textarea>

      <!-- Sélecteur de fichiers -->
      <div class="file-selector">
        <input
          type="file"
          ref="fileInput"
          multiple
          @change="selectionnerFichier"
          accept=".pdf,.doc,.docx,.xlsx,.xls,.jpg,.jpeg,.png,.txt"
          style="display: none"
        />
        <button @click="$refs.fileInput.click()" class="btn-attach" type="button" :disabled="sending">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
          </svg>
          Joindre des fichiers
        </button>
      </div>

      <!-- Liste des fichiers sélectionnés -->
      <div v-if="fichiersSelectionnes.length > 0" class="files-selected-list">
        <p><strong>{{ fichiersSelectionnes.length }} fichier(s) sélectionné(s)</strong></p>
        <ul class="files-preview">
          <li v-for="(file, idx) in fichiersSelectionnes" :key="idx" class="file-preview-item">
            <span class="file-preview-info">
              📎 {{ file.name }} ({{ formatTailleFichier(file.size) }})
            </span>
            <button @click="retirerFichier(idx)" class="btn-remove-file" type="button">×</button>
          </li>
        </ul>
      </div>

      <div class="form-actions">
        <small class="hint">{{ fichiersSelectionnes.length > 0 ? 'Fichiers prêts à envoyer' : 'Ctrl + Entrée pour envoyer rapidement' }}</small>
        <button @click="envoyerMessage" :disabled="(!nouveauMessage.trim() && fichiersSelectionnes.length === 0) || sending" class="btn-send">
          <span v-if="sending">⏳ Envoi...</span>
          <span v-else>📤 Envoyer</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DiscussionProjet',
  props: {
    projectId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      messages: [],
      loading: true,
      sending: false,
      currentUser: null,
      nouveauMessage: '',
      fichiersSelectionnes: [],
      refreshInterval: null
    };
  },
  computed: {
    canAddMessage() {
      return this.currentUser !== null;
    }
  },
  mounted() {
    // Récupérer l'utilisateur depuis localStorage
    this.currentUser = JSON.parse(localStorage.getItem("user") || "null");

    this.chargerMessages();

    // Rafraîchir les messages toutes les 10 secondes
    this.refreshInterval = setInterval(() => {
      this.chargerMessages(true); // true = silent refresh (sans loader)
    }, 10000);
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },
  methods: {
    getFileUrl(filename) {
      // En production sur Render, utiliser l'URL backend complète
      const isProduction = window.location.hostname.includes('render.com');
      const backendUrl = isProduction
        ? 'https://maturation-backend.onrender.com'
        : '';
      return `${backendUrl}/api/uploads/${filename}`;
    },

    async chargerMessages(silent = false) {
      try {
        if (!silent) {
          this.loading = true;
        }

        const response = await fetch(`/api/projects/${this.projectId}/messages`);
        if (response.ok) {
          this.messages = await response.json();

          // Auto-scroll vers le bas après chargement
          this.$nextTick(() => {
            this.scrollToBottom();
          });
        }
      } catch (error) {
        console.error('Erreur:', error);
      } finally {
        if (!silent) {
          this.loading = false;
        }
      }
    },

    selectionnerFichier(event) {
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
    },

    async envoyerMessage() {
      // Vérifier qu'il y a au moins du texte OU des fichiers
      if ((!this.nouveauMessage.trim() && this.fichiersSelectionnes.length === 0) || !this.currentUser) return;

      try {
        this.sending = true;

        // Si des fichiers sont joints, utiliser FormData
        if (this.fichiersSelectionnes.length > 0) {
          const formData = new FormData();
          formData.append('auteur_nom', this.currentUser.username);
          formData.append('auteur_role', this.currentUser.role);
          formData.append('contenu', this.nouveauMessage.trim() || ''); // Texte optionnel

          // Ajouter tous les fichiers
          this.fichiersSelectionnes.forEach(file => {
            formData.append('files', file);
          });

          const response = await fetch(`/api/projects/${this.projectId}/messages`, {
            method: 'POST',
            body: formData
          });

          if (response.ok) {
            this.nouveauMessage = '';
            this.fichiersSelectionnes = [];
            if (this.$refs.fileInput) {
              this.$refs.fileInput.value = '';
            }
            await this.chargerMessages();
          } else {
            const error = await response.json();
            alert(error.error || 'Erreur lors de l\'envoi du message');
          }
        } else {
          // Sinon, utiliser JSON (texte uniquement)
          const response = await fetch(`/api/projects/${this.projectId}/messages`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              auteur_nom: this.currentUser.username,
              auteur_role: this.currentUser.role,
              contenu: this.nouveauMessage.trim()
            })
          });

          if (response.ok) {
            this.nouveauMessage = '';
            await this.chargerMessages();
          } else {
            const error = await response.json();
            alert(error.error || 'Erreur lors de l\'envoi du message');
          }
        }
      } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur de connexion');
      } finally {
        this.sending = false;
      }
    },

    async supprimerMessage(message) {
      if (!confirm('Êtes-vous sûr de vouloir supprimer ce message ?')) return;

      try {
        const response = await fetch(
          `/api/projects/${this.projectId}/messages/${message.id}?auteur_nom=${this.currentUser.username}&role=${this.currentUser.role}`,
          { method: 'DELETE' }
        );

        if (response.ok) {
          await this.chargerMessages();
        } else {
          const error = await response.json();
          alert(error.error || 'Erreur lors de la suppression');
        }
      } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur de connexion');
      }
    },

    canDeleteMessage(message) {
      if (!this.currentUser) return false;
      return this.currentUser.role === 'admin' || this.currentUser.username === message.auteur_nom;
    },

    getMessageClass(message) {
      if (message.auteur_role === 'soumissionnaire') {
        return 'message-soumissionnaire';
      }
      return 'message-comite';
    },

    getRoleColor(role) {
      const colors = {
        'soumissionnaire': '#3b82f6',
        'evaluateur': '#8b5cf6',
        'secretariat_sct': '#10b981',
        'presidence_sct': '#f59e0b',
        'presidence_comite': '#ef4444',
        'admin': '#6366f1'
      };
      return colors[role] || '#64748b';
    },

    getInitials(name) {
      return name
        .split(' ')
        .map(n => n[0])
        .join('')
        .toUpperCase()
        .substring(0, 2);
    },

    getRoleLabel(role) {
      const labels = {
        'soumissionnaire': 'Soumissionnaire',
        'evaluateur': 'Évaluateur',
        'secretariat_sct': 'Secrétariat SCT',
        'presidence_sct': 'Présidence SCT',
        'presidence_comite': 'Présidence Comité',
        'admin': 'Administrateur'
      };
      return labels[role] || role;
    },

    formatDate(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      const now = new Date();
      const diff = now - date;
      const minutes = Math.floor(diff / 60000);
      const hours = Math.floor(diff / 3600000);
      const days = Math.floor(diff / 86400000);

      if (minutes < 1) return 'À l\'instant';
      if (minutes < 60) return `Il y a ${minutes} min`;
      if (hours < 24) return `Il y a ${hours}h`;
      if (days < 7) return `Il y a ${days}j`;

      return date.toLocaleDateString('fr-FR', {
        day: 'numeric',
        month: 'short',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
      });
    },

    scrollToBottom() {
      const container = this.$el.querySelector('.messages-list');
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    },

    formatTailleFichier(taille) {
      if (!taille) return '';
      if (taille < 1024) return `${taille} o`;
      if (taille < 1024 * 1024) return `${(taille / 1024).toFixed(1)} Ko`;
      return `${(taille / (1024 * 1024)).toFixed(1)} Mo`;
    }
  }
};
</script>

<style scoped>
.discussion-projet {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 2rem;
}

.discussion-header {
  margin-bottom: 1.5rem;
}

.discussion-header h3 {
  color: #1e293b;
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
}

.discussion-header .description {
  color: #64748b;
  font-size: 0.9rem;
  margin: 0;
}

.messages-container {
  min-height: 300px;
  max-height: 500px;
  overflow-y: auto;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 3rem;
  color: #64748b;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.2s;
}

.message-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.message-soumissionnaire {
  border-left: 3px solid #3b82f6;
}

.message-comite {
  border-left: 3px solid #8b5cf6;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.message-author {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.author-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 0.85rem;
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.author-info strong {
  color: #1e293b;
  font-size: 0.9rem;
}

.author-role {
  color: #64748b;
  font-size: 0.75rem;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.message-date {
  color: #94a3b8;
  font-size: 0.75rem;
  white-space: nowrap;
}

.btn-delete-message {
  background: #fee2e2;
  color: #dc2626;
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

.btn-delete-message:hover {
  background: #ef4444;
  color: white;
}

.message-content {
  color: #334155;
  font-size: 0.9rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.message-attachments {
  margin-top: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.message-attachment {
  padding: 0.5rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
}

.attachment-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 500;
}

.attachment-link:hover {
  color: #2563eb;
  text-decoration: underline;
}

.attachment-link svg {
  flex-shrink: 0;
}

.attachment-size {
  color: #64748b;
  font-weight: normal;
  font-size: 0.8rem;
}

.message-form {
  border-top: 1px solid #e2e8f0;
  padding-top: 1rem;
}

.message-form textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.9rem;
  font-family: inherit;
  resize: vertical;
  transition: all 0.2s;
}

.message-form textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.message-form textarea:disabled {
  background: #f1f5f9;
  cursor: not-allowed;
}

.file-selector {
  margin-top: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-attach {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-attach:hover:not(:disabled) {
  background: #e2e8f0;
  border-color: #94a3b8;
}

.btn-attach:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.files-selected-list {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 6px;
}

.files-selected-list p {
  margin: 0 0 0.5rem 0;
  color: #0c4a6e;
  font-weight: 600;
  font-size: 0.85rem;
}

.files-preview {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.file-preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: white;
  border: 1px solid #e0f2fe;
  border-radius: 4px;
}

.file-preview-info {
  flex: 1;
  font-size: 0.85rem;
  color: #0369a1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-remove-file {
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 4px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  line-height: 1;
  padding: 0;
  transition: all 0.2s;
  flex-shrink: 0;
}

.btn-remove-file:hover {
  background: #dc2626;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.75rem;
}

.hint {
  color: #94a3b8;
  font-size: 0.75rem;
}

.btn-send {
  padding: 0.5rem 1.25rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-send:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Scrollbar styling */
.messages-container::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

@media (max-width: 768px) {
  .discussion-projet {
    padding: 1rem;
  }

  .message-header {
    flex-direction: column;
    gap: 0.5rem;
  }

  .message-meta {
    align-self: flex-start;
  }

  .form-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .btn-send {
    width: 100%;
  }
}
</style>
