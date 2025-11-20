<template>
  <div class="contact-wrapper">
    <!-- En-tête public (même style que Home) -->
    <header class="public-header">
      <div class="header-container">
        <div class="header-left">
          <router-link to="/">
            <img :src="logoUrl" alt="Logo DGPPE" class="header-logo" />
          </router-link>
        </div>
        <div class="header-center">
          <div class="header-info">
            <h2 class="header-title">Ministère de l'Économie, du Plan et de la Coopération</h2>
            <p class="header-subtitle">Direction Générale de la Planification des Politiques Économiques</p>
          </div>
        </div>
        <div class="header-right">
          <button @click="$router.push('/login')" class="btn btn-outline">Connexion</button>
        </div>
      </div>
    </header>

    <div class="contact-page">
      <div class="contact-container">
      <div class="contact-header">
        <div class="back-links">
          <router-link to="/login" class="back-link">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Retour à la connexion
          </router-link>
        </div>
        <h1>Contactez-nous</h1>
        <p class="subtitle">Une question sur la plateforme PLASMAP ? Nous sommes là pour vous aider.</p>
      </div>

      <div v-if="submitted" class="success-message">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
        <h2>Message envoyé !</h2>
        <p>Nous vous répondrons dans les plus brefs délais à l'adresse {{ form.email }}.</p>
        <router-link to="/" class="btn btn-primary">Retour à l'accueil</router-link>
      </div>

      <form v-else @submit.prevent="submitForm" class="contact-form">
        <div class="form-row">
          <div class="form-group">
            <label for="nom">Nom complet <span class="required">*</span></label>
            <input
              type="text"
              id="nom"
              v-model="form.nom"
              required
              placeholder="Votre nom et prénom"
            />
          </div>

          <div class="form-group">
            <label for="email">Email <span class="required">*</span></label>
            <input
              type="email"
              id="email"
              v-model="form.email"
              required
              placeholder="votre@email.com"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="telephone">Téléphone</label>
            <input
              type="tel"
              id="telephone"
              v-model="form.telephone"
              placeholder="+221 XX XXX XX XX"
            />
          </div>

          <div class="form-group">
            <label for="objet">Objet <span class="required">*</span></label>
            <select id="objet" v-model="form.objet" required>
              <option value="">Sélectionnez un objet</option>
              <option value="Demande d'information">Demande d'information</option>
              <option value="Problème technique">Problème technique</option>
              <option value="Question sur la soumission">Question sur la soumission</option>
              <option value="Demande de compte">Demande de compte</option>
              <option value="Autre">Autre</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="message">Message <span class="required">*</span></label>
          <textarea
            id="message"
            v-model="form.message"
            required
            rows="6"
            placeholder="Décrivez votre demande en détail..."
          ></textarea>
        </div>

        <div class="form-group captcha-group">
          <label>Vérification <span class="required">*</span></label>
          <div class="captcha-question">
            <span>{{ captcha.num1 }} + {{ captcha.num2 }} = </span>
            <input
              type="number"
              v-model.number="captchaAnswer"
              required
              placeholder="?"
              class="captcha-input"
            />
          </div>
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button type="submit" class="btn btn-primary btn-lg" :disabled="loading">
          <span v-if="loading">Envoi en cours...</span>
          <span v-else>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
            Envoyer le message
          </span>
        </button>
      </form>

      <div class="contact-info">
        <h3>Autres moyens de contact</h3>
        <div class="info-items">
          <div class="info-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
              <polyline points="22,6 12,13 2,6"/>
            </svg>
            <span>contact@dgppe.sn</span>
          </div>
          <div class="info-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
            </svg>
            <span>+221 33 XXX XX XX</span>
          </div>
          <div class="info-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
            <span>DGPPE, Dakar, Sénégal</span>
          </div>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<script>
import logoUrl from '../assets/logo-dgppe.png'

export default {
  name: 'Contact',
  data() {
    return {
      logoUrl,
      form: {
        nom: '',
        email: '',
        telephone: '',
        objet: '',
        message: ''
      },
      captcha: {
        num1: 0,
        num2: 0
      },
      captchaAnswer: null,
      loading: false,
      error: null,
      submitted: false
    };
  },
  created() {
    this.generateCaptcha();
    this.prefillUserData();
  },
  methods: {
    generateCaptcha() {
      this.captcha.num1 = Math.floor(Math.random() * 10) + 1;
      this.captcha.num2 = Math.floor(Math.random() * 10) + 1;
    },
    prefillUserData() {
      const user = JSON.parse(localStorage.getItem('user') || 'null');
      if (user) {
        this.form.nom = user.display_name || user.username || '';
        this.form.email = user.email || '';
        this.form.telephone = user.telephone || '';
      }
    },
    async submitForm() {
      this.error = null;

      // Vérifier captcha
      if (this.captchaAnswer !== this.captcha.num1 + this.captcha.num2) {
        this.error = 'Réponse au captcha incorrecte';
        this.generateCaptcha();
        this.captchaAnswer = null;
        return;
      }

      this.loading = true;

      try {
        const user = JSON.parse(localStorage.getItem('user') || 'null');

        const response = await fetch('/api/contact', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ...this.form,
            user_id: user?.id || null,
            username: user?.username || null,
            captcha_reponse: this.captchaAnswer,
            captcha_attendu: this.captcha.num1 + this.captcha.num2
          })
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || 'Erreur lors de l\'envoi');
        }

        this.submitted = true;
      } catch (err) {
        this.error = err.message;
        this.generateCaptcha();
        this.captchaAnswer = null;
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
/* ==================== EN-TÊTE PUBLIC ==================== */
.contact-wrapper {
  min-height: 100vh;
  background: var(--dgppe-gray-50, #f8fafc);
}

.public-header {
  background: var(--dgppe-white, white);
  border-bottom: 1px solid var(--dgppe-gray-200, #e5e7eb);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 1rem 0;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-logo {
  height: 50px;
  width: auto;
  transition: opacity 0.2s ease;
}

.header-logo:hover {
  opacity: 0.8;
}

.header-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

.header-right {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.header-info {
  text-align: center;
}

.header-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--dgppe-primary, #2e6b6b);
  margin: 0;
  line-height: 1.2;
}

.header-subtitle {
  font-size: 0.875rem;
  color: var(--dgppe-text-muted, #6b7280);
  margin: 0;
  line-height: 1.2;
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--dgppe-primary, #2e6b6b);
  color: var(--dgppe-primary, #2e6b6b);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-outline:hover {
  background: var(--dgppe-primary, #2e6b6b);
  color: white;
}

/* ==================== CONTACT PAGE ==================== */
.contact-page {
  min-height: calc(100vh - 80px);
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

@media (max-width: 768px) {
  .header-container {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 0.75rem;
  }

  .header-left {
    justify-content: center;
  }

  .header-right {
    justify-content: center;
  }
}

.back-links {
  margin-bottom: 1rem;
}

.contact-container {
  max-width: 700px;
  width: 100%;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  padding: 2.5rem;
  margin-top: 2rem;
}

.contact-header {
  text-align: center;
  margin-bottom: 2rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  text-decoration: none;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  transition: color 0.2s;
}

.back-link:hover {
  color: #111827;
}

.contact-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 0.5rem;
}

.subtitle {
  color: #6b7280;
  margin: 0;
  font-size: 0.95rem;
}

.contact-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  font-size: 0.875rem;
  color: #374151;
}

.required {
  color: #ef4444;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 120px;
}

.captcha-group {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 8px;
}

.captcha-question {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
}

.captcha-input {
  width: 80px;
  text-align: center;
}

.error-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-primary:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}

.btn-lg {
  padding: 1rem 2rem;
  font-size: 1rem;
}

.success-message {
  text-align: center;
  padding: 2rem;
}

.success-message svg {
  color: #059669;
  margin-bottom: 1rem;
}

.success-message h2 {
  font-size: 1.5rem;
  color: #111827;
  margin: 0 0 0.5rem;
}

.success-message p {
  color: #6b7280;
  margin: 0 0 1.5rem;
}

.contact-info {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.contact-info h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 1rem;
}

.info-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.info-item svg {
  color: #9ca3af;
}

@media (max-width: 640px) {
  .contact-page {
    padding: 1rem;
  }

  .contact-container {
    padding: 1.5rem;
    margin-top: 0;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
