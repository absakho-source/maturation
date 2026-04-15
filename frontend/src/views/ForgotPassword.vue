<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>🔑 Mot de passe oublié</h2>
      <p class="auth-hint">
        Entrez votre adresse email ou votre nom d'utilisateur.
        Nous vous enverrons un lien pour réinitialiser votre mot de passe.
      </p>

      <form @submit.prevent="submit" v-if="!sent">
        <input
          v-model="identifier"
          type="text"
          placeholder="Email ou nom d'utilisateur"
          required
          autofocus
        />
        <button type="submit" :disabled="loading">
          {{ loading ? 'Envoi en cours…' : 'Envoyer le lien' }}
        </button>
      </form>

      <div v-else class="success-box">
        <p>✅ Si un compte existe pour cet identifiant, un email vient de vous être envoyé.</p>
        <p class="small">Vérifiez votre boîte de réception (et vos spams).</p>
      </div>

      <p class="auth-link">
        <router-link to="/login">← Retour à la connexion</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import { toast } from '../toast.js';

export default {
  name: 'ForgotPassword',
  data() {
    return { identifier: '', loading: false, sent: false };
  },
  methods: {
    async submit() {
      if (!this.identifier.trim()) return;
      this.loading = true;
      try {
        const body = this.identifier.includes('@')
          ? { email: this.identifier.trim() }
          : { username: this.identifier.trim() };
        const resp = await fetch('/api/auth/request-password-reset', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
        if (!resp.ok) {
          const err = await resp.json().catch(() => ({}));
          throw new Error(err.error || "Erreur lors de l'envoi");
        }
        this.sent = true;
      } catch (e) {
        toast.error(e.message);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  padding: 2rem 1rem;
}
.auth-card {
  background: #fff;
  max-width: 460px;
  width: 100%;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border: 1px solid #e2e8f0;
}
h2 { color: #2e6b6b; margin: 0 0 0.75rem 0; }
.auth-hint { color: #64748b; font-size: 0.95rem; margin-bottom: 1.25rem; line-height: 1.5; }
input {
  width: 100%;
  padding: 0.7rem;
  border: 2px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.95rem;
  box-sizing: border-box;
  margin-bottom: 1rem;
}
input:focus { outline: none; border-color: #0ea5e9; }
button {
  width: 100%;
  padding: 0.75rem;
  background: #2e6b6b;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
}
button:hover:not(:disabled) { background: #1e4b4b; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
.success-box {
  background: #f0fdf4;
  border-left: 4px solid #10b981;
  padding: 1rem;
  border-radius: 8px;
  color: #065f46;
}
.success-box .small { font-size: 0.85rem; margin-top: 0.5rem; color: #047857; }
.auth-link {
  margin-top: 1rem;
  text-align: center;
  font-size: 0.9rem;
}
.auth-link a { color: #2e6b6b; text-decoration: none; }
.auth-link a:hover { text-decoration: underline; }
</style>
