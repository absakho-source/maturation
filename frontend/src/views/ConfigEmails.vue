<template>
  <PageWrapper>
    <div class="email-config-container">
      <div class="page-header">
        <h1 class="page-title">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
            <polyline points="22,6 12,13 2,6"/>
          </svg>
          Configuration des Emails
        </h1>
        <p class="subtitle">Gérer les paramètres d'envoi d'emails automatiques</p>
      </div>

      <!-- Chargement -->
      <div v-if="emailConfig.loading" class="loading-message">
        ⏳ Chargement de la configuration...
      </div>

      <!-- Erreur -->
      <div v-if="emailConfig.error" class="error-box">
        <strong>❌ Erreur:</strong> {{ emailConfig.error }}
      </div>

      <!-- Configuration -->
      <div v-if="!emailConfig.loading && emailConfig.data" class="config-sections">

        <!-- Statut global -->
        <div class="config-card">
          <h3>📊 Statut du Service Email</h3>
          <div class="status-grid">
            <div class="status-item">
              <span class="label">Service Activé:</span>
              <span :class="['badge', emailConfig.data.enabled ? 'badge-success' : 'badge-error']">
                {{ emailConfig.data.enabled ? '✅ Activé' : '❌ Désactivé' }}
              </span>
            </div>
            <div class="status-item">
              <span class="label">Mode Debug:</span>
              <span :class="['badge', emailConfig.data.debug_mode ? 'badge-warning' : 'badge-neutral']">
                {{ emailConfig.data.debug_mode ? '🔍 Activé' : 'Désactivé' }}
              </span>
            </div>
            <div class="status-item">
              <span class="label">Mot de passe:</span>
              <span :class="['badge', emailConfig.data.password_configured ? 'badge-success' : 'badge-error']">
                {{ emailConfig.data.password_configured ? '✅ Configuré' : '❌ Manquant' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Configuration SMTP -->
        <div class="config-card">
          <h3>⚙️ Paramètres SMTP</h3>
          <div class="config-grid">
            <div class="config-item">
              <span class="label">Serveur SMTP:</span>
              <code>{{ emailConfig.data.smtp_server }}</code>
            </div>
            <div class="config-item">
              <span class="label">Port:</span>
              <code>{{ emailConfig.data.smtp_port }}</code>
            </div>
            <div class="config-item">
              <span class="label">Nom d'utilisateur:</span>
              <code>{{ emailConfig.data.smtp_username }}</code>
            </div>
            <div class="config-item">
              <span class="label">Email expéditeur:</span>
              <code>{{ emailConfig.data.from_email }}</code>
            </div>
            <div class="config-item">
              <span class="label">Nom d'affichage:</span>
              <code>{{ emailConfig.data.from_name }}</code>
            </div>
            <div class="config-item">
              <span class="label">URL Plateforme:</span>
              <code>{{ emailConfig.data.platform_url }}</code>
            </div>
          </div>
        </div>

        <!-- Test d'envoi -->
        <div class="config-card">
          <h3>🧪 Test d'Envoi d'Email</h3>
          <p class="help-text">
            Envoyez un email de test pour vérifier que la configuration fonctionne correctement.
          </p>

          <div class="test-email-form">
            <input
              v-model="testEmailAddress"
              type="email"
              placeholder="votre.email@exemple.com"
              class="email-input"
            />
            <button
              @click="envoyerEmailTest"
              :disabled="testEmailLoading || !testEmailAddress"
              class="btn-test-email"
            >
              {{ testEmailLoading ? '⏳ Envoi en cours...' : '📤 Envoyer Email Test' }}
            </button>
          </div>

          <!-- Résultat du test -->
          <div v-if="testEmailResult.message" :class="['test-result', testEmailResult.success ? 'success' : 'error']">
            <strong>{{ testEmailResult.success ? '✅ Succès:' : '❌ Erreur:' }}</strong>
            {{ testEmailResult.message }}
            <div v-if="testEmailResult.hint" class="hint">
              💡 {{ testEmailResult.hint }}
            </div>
          </div>
        </div>

        <!-- Liens utiles -->
        <div class="config-card">
          <h3>🔗 Liens Utiles</h3>
          <div class="links-grid">
            <a
              :href="emailConfig.data.render_dashboard_url"
              target="_blank"
              class="link-button"
            >
              🔧 Modifier Configuration sur Render
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                <polyline points="15 3 21 3 21 9"></polyline>
                <line x1="10" y1="14" x2="21" y2="3"></line>
              </svg>
            </a>
            <button @click="rechargerConfiguration" class="link-button secondary">
              🔄 Recharger la Configuration
            </button>
          </div>

          <div class="documentation-links">
            <h4>📚 Documentation</h4>
            <ul>
              <li><code>{{ emailConfig.data.documentation.guide_complet }}</code> - Guide complet de configuration</li>
              <li><code>{{ emailConfig.data.documentation.guide_rapide }}</code> - Guide d'activation rapide</li>
              <li><code>{{ emailConfig.data.documentation.status }}</code> - Status et diagnostic</li>
            </ul>
          </div>
        </div>

        <!-- Informations importantes -->
        <div class="config-card warning">
          <h3>⚠️ Informations Importantes</h3>
          <ul class="info-list">
            <li>Les variables d'environnement sont configurées sur Render et non dans le code</li>
            <li>Toute modification nécessite un redéploiement du service backend</li>
            <li>Le mode debug affiche des logs détaillés (à désactiver en production)</li>
            <li>Les utilisateurs doivent avoir un email configuré dans leur profil pour recevoir les notifications</li>
            <li v-if="!emailConfig.data.enabled" class="error-item">
              ❌ <strong>Le service email est actuellement désactivé.</strong>
              Activez EMAIL_ENABLED=true sur Render pour activer les notifications.
            </li>
          </ul>
        </div>
      </div>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';

export default {
  name: 'ConfigEmails',
  components: {
    PageWrapper
  },
  data() {
    return {
      emailConfig: {
        loading: false,
        error: null,
        data: null
      },
      testEmailAddress: '',
      testEmailLoading: false,
      testEmailResult: {
        success: false,
        message: '',
        hint: ''
      }
    };
  },
  mounted() {
    this.loadEmailConfig();
  },
  methods: {
    async loadEmailConfig() {
      this.emailConfig.loading = true;
      this.emailConfig.error = null;

      try {
        const user = JSON.parse(localStorage.getItem('user'));
        const role = user?.role || 'guest';

        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/email-config?role=${role}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Erreur lors du chargement de la configuration');
        }

        this.emailConfig.data = await response.json();
        console.log('Configuration email chargée:', this.emailConfig.data);
      } catch (error) {
        console.error('Erreur chargement configuration email:', error);
        this.emailConfig.error = error.message || 'Impossible de charger la configuration email';
      } finally {
        this.emailConfig.loading = false;
      }
    },

    rechargerConfiguration() {
      this.loadEmailConfig();
    },

    async envoyerEmailTest() {
      if (!this.testEmailAddress) {
        alert('Veuillez entrer une adresse email');
        return;
      }

      // Validation basique de l'email
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(this.testEmailAddress)) {
        alert('Veuillez entrer une adresse email valide');
        return;
      }

      this.testEmailLoading = true;
      this.testEmailResult = { success: false, message: '', hint: '' };

      try {
        const user = JSON.parse(localStorage.getItem('user'));
        const role = user?.role || 'guest';

        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/test-email`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            role: role,
            test_email: this.testEmailAddress
          })
        });

        const data = await response.json();

        if (!response.ok) {
          this.testEmailResult = {
            success: false,
            message: data.error || 'Erreur lors de l\'envoi de l\'email',
            hint: data.hint || ''
          };
        } else {
          this.testEmailResult = {
            success: data.success,
            message: data.message || 'Email envoyé avec succès',
            hint: ''
          };

          // Effacer le champ email après succès
          if (data.success) {
            setTimeout(() => {
              this.testEmailAddress = '';
            }, 2000);
          }
        }
      } catch (error) {
        console.error('Erreur lors de l\'envoi de l\'email de test:', error);
        this.testEmailResult = {
          success: false,
          message: 'Erreur de connexion au serveur',
          hint: 'Vérifiez votre connexion internet et réessayez'
        };
      } finally {
        this.testEmailLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.email-config-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--dgppe-spacing-6);
}

.page-header {
  margin-bottom: var(--dgppe-spacing-8);
}

.page-title {
  display: flex;
  align-items: center;
  gap: var(--dgppe-spacing-3);
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 var(--dgppe-spacing-2) 0;
}

.page-title svg {
  color: #007bff;
}

.subtitle {
  color: #6c757d;
  font-size: 1.125rem;
  margin: 0;
}

.loading-message {
  padding: var(--dgppe-spacing-8);
  text-align: center;
  font-size: 1.125rem;
  color: #6c757d;
}

.error-box {
  padding: var(--dgppe-spacing-4);
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  color: #721c24;
  margin-bottom: var(--dgppe-spacing-4);
}

.config-sections {
  display: flex;
  flex-direction: column;
  gap: var(--dgppe-spacing-6);
}

.config-card {
  background: white;
  border-radius: 12px;
  padding: var(--dgppe-spacing-6);
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.config-card.warning {
  background: #fff3cd;
  border: 1px solid #ffc107;
}

.config-card h3 {
  margin: 0 0 var(--dgppe-spacing-4) 0;
  font-size: 1.25rem;
  color: #2c3e50;
}

.status-grid,
.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--dgppe-spacing-4);
  margin-top: var(--dgppe-spacing-4);
}

.status-item,
.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--dgppe-spacing-3);
  background: #f8f9fa;
  border-radius: 8px;
}

.status-item .label,
.config-item .label {
  font-weight: 600;
  color: #495057;
}

.badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.badge-success {
  background: #d4edda;
  color: #155724;
}

.badge-error {
  background: #f8d7da;
  color: #721c24;
}

.badge-warning {
  background: #fff3cd;
  color: #856404;
}

.badge-neutral {
  background: #e2e3e5;
  color: #383d41;
}

.config-item code {
  background: #e9ecef;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 0.875rem;
}

.help-text {
  color: #6c757d;
  margin-bottom: var(--dgppe-spacing-4);
}

.test-email-form {
  display: flex;
  gap: var(--dgppe-spacing-3);
  margin-top: var(--dgppe-spacing-4);
}

.email-input {
  flex: 1;
  padding: var(--dgppe-spacing-3);
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 1rem;
}

.email-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
}

.btn-test-email {
  padding: var(--dgppe-spacing-3) var(--dgppe-spacing-5);
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-test-email:hover:not(:disabled) {
  background: #0056b3;
}

.btn-test-email:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.test-result {
  margin-top: var(--dgppe-spacing-4);
  padding: var(--dgppe-spacing-4);
  border-radius: 8px;
}

.test-result.success {
  background: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
}

.test-result.error {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}

.test-result .hint {
  margin-top: var(--dgppe-spacing-2);
  font-style: italic;
  font-size: 0.875rem;
}

.links-grid {
  display: flex;
  gap: var(--dgppe-spacing-3);
  margin-top: var(--dgppe-spacing-4);
}

.link-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--dgppe-spacing-2);
  padding: var(--dgppe-spacing-3);
  background: #007bff;
  color: white;
  text-decoration: none;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.link-button:hover {
  background: #0056b3;
}

.link-button.secondary {
  background: #6c757d;
}

.link-button.secondary:hover {
  background: #545b62;
}

.documentation-links {
  margin-top: var(--dgppe-spacing-5);
}

.documentation-links h4 {
  margin: 0 0 var(--dgppe-spacing-3) 0;
  font-size: 1rem;
  color: #495057;
}

.documentation-links ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.documentation-links li {
  padding: var(--dgppe-spacing-2) 0;
  color: #6c757d;
  font-size: 0.875rem;
}

.documentation-links code {
  background: #e9ecef;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Courier New', monospace;
}

.info-list {
  list-style: none;
  padding: 0;
  margin: var(--dgppe-spacing-4) 0 0 0;
}

.info-list li {
  padding: var(--dgppe-spacing-2) 0;
  color: #856404;
  font-size: 0.938rem;
}

.info-list .error-item {
  color: #721c24;
  font-weight: 600;
}

@media (max-width: 768px) {
  .test-email-form {
    flex-direction: column;
  }

  .links-grid {
    flex-direction: column;
  }

  .status-grid,
  .config-grid {
    grid-template-columns: 1fr;
  }
}
</style>
