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
        <p class="subtitle">Configurer les paramètres d'envoi d'emails automatiques</p>
      </div>

      <!-- Chargement -->
      <div v-if="loading" class="loading-message">
        ⏳ Chargement de la configuration...
      </div>

      <!-- Erreur -->
      <div v-if="error" class="error-box">
        <strong>❌ Erreur:</strong> {{ error }}
      </div>

      <!-- Formulaire de configuration -->
      <div v-if="!loading" class="config-sections">

        <!-- Message de succès -->
        <div v-if="saveSuccess" class="success-box">
          <strong>✅ Succès:</strong> La configuration a été enregistrée avec succès !
        </div>

        <!-- Formulaire principal -->
        <form @submit.prevent="saveConfiguration" class="config-form">

          <!-- Activation du service -->
          <div class="config-card">
            <h3>🔌 Activation du Service</h3>
            <div class="form-row">
              <div class="form-group checkbox-group">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="config.enabled" />
                  <span>Activer l'envoi d'emails automatiques</span>
                </label>
              </div>
              <div class="form-group checkbox-group">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="config.debug_mode" />
                  <span>Mode Debug (logs détaillés)</span>
                </label>
              </div>
            </div>
          </div>

          <!-- Paramètres SMTP -->
          <div class="config-card">
            <h3>⚙️ Paramètres SMTP</h3>

            <div class="form-row">
              <div class="form-group">
                <label for="smtp_server">Serveur SMTP *</label>
                <input
                  type="text"
                  id="smtp_server"
                  v-model="config.smtp_server"
                  placeholder="smtp.office365.com"
                  required
                />
                <small>Exemple: smtp.office365.com, smtp.gmail.com, mail.votre-serveur.sn</small>
              </div>

              <div class="form-group">
                <label for="smtp_port">Port SMTP *</label>
                <input
                  type="number"
                  id="smtp_port"
                  v-model.number="config.smtp_port"
                  placeholder="587"
                  required
                  min="1"
                  max="65535"
                />
                <small>Port standard: 587 (STARTTLS) ou 465 (SSL)</small>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="smtp_username">Nom d'utilisateur SMTP *</label>
                <input
                  type="text"
                  id="smtp_username"
                  v-model="config.smtp_username"
                  placeholder="votre.email@exemple.com"
                  required
                />
                <small>Généralement votre adresse email complète</small>
              </div>

              <div class="form-group">
                <label for="smtp_password">Mot de passe SMTP *</label>
                <div class="password-input-wrapper">
                  <input
                    :type="showPassword ? 'text' : 'password'"
                    id="smtp_password"
                    v-model="config.smtp_password"
                    placeholder="••••••••"
                    required
                  />
                  <button type="button" @click="showPassword = !showPassword" class="toggle-password">
                    {{ showPassword ? '👁️' : '👁️‍🗨️' }}
                  </button>
                </div>
                <small>Mot de passe de votre compte email ou mot de passe d'application</small>
              </div>
            </div>
          </div>

          <!-- Informations d'envoi -->
          <div class="config-card">
            <h3>📧 Informations d'Envoi</h3>

            <div class="form-row">
              <div class="form-group">
                <label for="from_email">Email expéditeur *</label>
                <input
                  type="email"
                  id="from_email"
                  v-model="config.from_email"
                  placeholder="noreply@exemple.com"
                  required
                />
                <small>Adresse email qui apparaîtra comme expéditeur</small>
              </div>

              <div class="form-group">
                <label for="from_name">Nom d'affichage *</label>
                <input
                  type="text"
                  id="from_name"
                  v-model="config.from_name"
                  placeholder="Maturation DGPPE"
                  required
                />
                <small>Nom qui apparaîtra comme expéditeur</small>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group full-width">
                <label for="platform_url">URL de la Plateforme *</label>
                <input
                  type="url"
                  id="platform_url"
                  v-model="config.platform_url"
                  placeholder="https://votre-plateforme.com"
                  required
                />
                <small>URL complète de la plateforme (utilisée dans les liens des emails)</small>
              </div>
            </div>
          </div>

          <!-- Boutons d'action -->
          <div class="form-actions">
            <button type="button" @click="resetForm" class="btn-secondary" :disabled="saving">
              🔄 Réinitialiser
            </button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? '⏳ Enregistrement...' : '💾 Enregistrer la Configuration' }}
            </button>
          </div>
        </form>

        <!-- Test d'envoi -->
        <div class="config-card">
          <h3>🧪 Test d'Envoi d'Email</h3>
          <p class="help-text">
            Testez votre configuration en envoyant un email de vérification.
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
              :disabled="testEmailLoading || !testEmailAddress || !config.enabled"
              class="btn-test-email"
            >
              {{ testEmailLoading ? '⏳ Envoi...' : '📤 Envoyer Test' }}
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

          <div v-if="!config.enabled" class="warning-message">
            ⚠️ Le service email est désactivé. Activez-le pour pouvoir tester l'envoi.
          </div>
        </div>

        <!-- Informations d'aide -->
        <div class="config-card info">
          <h3>ℹ️ Informations Utiles</h3>
          <div class="info-grid">
            <div class="info-item">
              <strong>📚 Configuration Office 365:</strong>
              <ul>
                <li>Serveur: smtp.office365.com</li>
                <li>Port: 587</li>
                <li>Username: votre.email@economie.gouv.sn</li>
              </ul>
            </div>
            <div class="info-item">
              <strong>📚 Configuration Gmail:</strong>
              <ul>
                <li>Serveur: smtp.gmail.com</li>
                <li>Port: 587</li>
                <li>Nécessite un mot de passe d'application</li>
              </ul>
            </div>
            <div class="info-item">
              <strong>⚠️ Important:</strong>
              <ul>
                <li>Les changements sont appliqués immédiatement</li>
                <li>Testez toujours après modification</li>
                <li>Désactivez le mode debug en production</li>
              </ul>
            </div>
          </div>
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
      loading: false,
      saving: false,
      error: null,
      saveSuccess: false,
      showPassword: false,

      config: {
        enabled: false,
        debug_mode: false,
        smtp_server: '',
        smtp_port: 587,
        smtp_username: '',
        smtp_password: '',
        from_email: '',
        from_name: '',
        platform_url: ''
      },

      originalConfig: null,

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
      this.loading = true;
      this.error = null;

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

        const data = await response.json();

        // Remplir le formulaire avec les données reçues
        this.config = {
          enabled: data.enabled || false,
          debug_mode: data.debug_mode || false,
          smtp_server: data.smtp_server || '',
          smtp_port: data.smtp_port || 587,
          smtp_username: data.smtp_username ? data.smtp_username.replace('...', '') : '',
          smtp_password: '', // Ne pas afficher le mot de passe
          from_email: data.from_email || '',
          from_name: data.from_name || '',
          platform_url: data.platform_url || ''
        };

        // Sauvegarder la config originale
        this.originalConfig = { ...this.config };

        console.log('Configuration email chargée:', data);
      } catch (error) {
        console.error('Erreur chargement configuration email:', error);
        this.error = error.message || 'Impossible de charger la configuration email';
      } finally {
        this.loading = false;
      }
    },

    async saveConfiguration() {
      this.saving = true;
      this.error = null;
      this.saveSuccess = false;

      try {
        const user = JSON.parse(localStorage.getItem('user'));
        const role = user?.role || 'guest';

        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/admin/email-config/save`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            role: role,
            config: this.config
          })
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || 'Erreur lors de l\'enregistrement');
        }

        this.saveSuccess = true;
        this.originalConfig = { ...this.config };

        // Masquer le message de succès après 5 secondes
        setTimeout(() => {
          this.saveSuccess = false;
        }, 5000);

      } catch (error) {
        console.error('Erreur sauvegarde configuration:', error);
        this.error = error.message || 'Impossible d\'enregistrer la configuration';
      } finally {
        this.saving = false;
      }
    },

    resetForm() {
      if (this.originalConfig) {
        this.config = { ...this.originalConfig };
      } else {
        this.loadEmailConfig();
      }
    },

    async envoyerEmailTest() {
      if (!this.testEmailAddress) {
        alert('Veuillez entrer une adresse email');
        return;
      }

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
  max-width: 1000px;
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
  flex-shrink: 0;
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

.success-box {
  padding: var(--dgppe-spacing-4);
  background: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 8px;
  color: #155724;
  margin-bottom: var(--dgppe-spacing-6);
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.config-sections {
  display: flex;
  flex-direction: column;
  gap: var(--dgppe-spacing-6);
}

.config-form {
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

.config-card.info {
  background: #e7f3ff;
  border: 1px solid #b3d9ff;
}

.config-card h3 {
  margin: 0 0 var(--dgppe-spacing-5) 0;
  font-size: 1.25rem;
  color: #2c3e50;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--dgppe-spacing-4);
  margin-bottom: var(--dgppe-spacing-4);
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: var(--dgppe-spacing-2);
  font-size: 0.938rem;
}

.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="url"],
.form-group input[type="number"],
.form-group input[type="password"] {
  padding: var(--dgppe-spacing-3);
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
  width: 100%;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
}

.form-group small {
  margin-top: var(--dgppe-spacing-1);
  font-size: 0.813rem;
  color: #6c757d;
  font-style: italic;
}

.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-wrapper input {
  flex: 1;
  padding-right: 45px;
}

.toggle-password {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  padding: 4px 8px;
  line-height: 1;
}

.toggle-password:hover {
  opacity: 0.7;
}

.checkbox-group {
  margin-bottom: 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--dgppe-spacing-2);
  cursor: pointer;
  font-weight: normal;
  margin-bottom: 0;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.checkbox-label span {
  font-size: 1rem;
  color: #2c3e50;
}

.form-actions {
  display: flex;
  gap: var(--dgppe-spacing-3);
  justify-content: flex-end;
  padding-top: var(--dgppe-spacing-4);
  border-top: 1px solid #e9ecef;
}

.btn-primary,
.btn-secondary {
  padding: var(--dgppe-spacing-3) var(--dgppe-spacing-5);
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-1px);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
}

.btn-primary:disabled,
.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.help-text {
  color: #6c757d;
  margin-bottom: var(--dgppe-spacing-4);
  font-size: 0.938rem;
}

.test-email-form {
  display: flex;
  gap: var(--dgppe-spacing-3);
  margin-bottom: var(--dgppe-spacing-4);
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
  background: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.btn-test-email:hover:not(:disabled) {
  background: #218838;
}

.btn-test-email:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.test-result {
  padding: var(--dgppe-spacing-4);
  border-radius: 8px;
  margin-bottom: var(--dgppe-spacing-3);
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

.warning-message {
  padding: var(--dgppe-spacing-3);
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 8px;
  color: #856404;
  font-size: 0.938rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--dgppe-spacing-4);
}

.info-item strong {
  display: block;
  margin-bottom: var(--dgppe-spacing-2);
  color: #2c3e50;
}

.info-item ul {
  margin: 0;
  padding-left: var(--dgppe-spacing-4);
  color: #495057;
  font-size: 0.938rem;
}

.info-item li {
  margin-bottom: var(--dgppe-spacing-1);
}

@media (max-width: 768px) {
  .email-config-container {
    padding: var(--dgppe-spacing-4);
  }

  .page-title {
    font-size: 1.5rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .test-email-form {
    flex-direction: column;
  }

  .form-actions {
    flex-direction: column-reverse;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
