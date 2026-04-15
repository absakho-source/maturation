<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>🔐 Nouveau mot de passe</h2>
      <p class="auth-hint" v-if="!done">
        Choisissez un nouveau mot de passe (6 caractères minimum).
      </p>

      <form @submit.prevent="submit" v-if="!done">
        <input
          v-model="password"
          type="password"
          placeholder="Nouveau mot de passe"
          minlength="6"
          required
          autofocus
        />
        <input
          v-model="passwordConfirm"
          type="password"
          placeholder="Confirmer le mot de passe"
          minlength="6"
          required
        />
        <p v-if="passwordConfirm && password !== passwordConfirm" class="field-error">
          ⚠️ Les mots de passe ne correspondent pas.
        </p>
        <p v-else-if="passwordConfirm && password === passwordConfirm && password.length >= 6" class="field-ok">
          ✅ Mots de passe identiques.
        </p>
        <button type="submit" :disabled="loading || !canSubmit">
          {{ loading ? 'Enregistrement…' : 'Enregistrer' }}
        </button>
      </form>

      <div v-else class="success-box">
        <p>✅ Votre mot de passe a été réinitialisé.</p>
        <p class="small">
          <router-link to="/login">Se connecter →</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { toast } from '../toast.js';

export default {
  name: 'ResetPassword',
  data() {
    return { password: '', passwordConfirm: '', loading: false, done: false };
  },
  computed: {
    token() { return this.$route.query.token || ''; },
    canSubmit() {
      return this.password.length >= 6 && this.password === this.passwordConfirm;
    }
  },
  mounted() {
    if (!this.token) {
      toast.error('Lien invalide : aucun token fourni.');
    }
  },
  methods: {
    async submit() {
      if (!this.canSubmit || !this.token) return;
      this.loading = true;
      try {
        const resp = await fetch('/api/auth/reset-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: this.token, password: this.password }),
        });
        if (!resp.ok) {
          const err = await resp.json().catch(() => ({}));
          throw new Error(err.error || 'Erreur');
        }
        this.done = true;
        toast.success('Mot de passe réinitialisé.');
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
  margin-bottom: 0.75rem;
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
  margin-top: 0.5rem;
}
button:hover:not(:disabled) { background: #1e4b4b; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
.field-error { color: #b91c1c; font-size: 0.85rem; margin: 0 0 0.5rem 0; }
.field-ok    { color: #065f46; font-size: 0.85rem; margin: 0 0 0.5rem 0; }
.success-box {
  background: #f0fdf4;
  border-left: 4px solid #10b981;
  padding: 1rem;
  border-radius: 8px;
  color: #065f46;
}
.success-box .small { font-size: 0.9rem; margin-top: 0.5rem; }
.success-box a { color: #047857; text-decoration: none; font-weight: 600; }
.success-box a:hover { text-decoration: underline; }
</style>
