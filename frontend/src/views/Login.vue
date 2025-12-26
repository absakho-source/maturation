<template>
  <div class="login-page">
    <!-- En-tête public -->
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
            <p class="header-platform">Plateforme de Suivi de la Maturation des Projets (PLASMAP)</p>
          </div>
        </div>
        <div class="header-right"></div>
      </div>
    </header>

    <main class="login-main">
      <div class="login-container">
        <!-- Titre connexion -->
        <div class="login-header">
          <h1 class="login-title">Connexion</h1>
          <p class="login-subtitle">Sélectionnez votre compte et entrez votre mot de passe</p>
        </div>

        <!-- Formulaire de connexion -->
        <div class="login-form-section">
          <form @submit.prevent="handleLoginSubmit" class="login-form">
            <div class="form-group">
              <label for="username" class="form-label">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
                Compte utilisateur
              </label>
              <select
                id="username"
                v-model="selectedUsername"
                class="form-select"
                required
              >
                <option value="">-- Sélectionnez un compte --</option>
                <option
                  v-for="account in accounts"
                  :key="account.value"
                  :value="account.value"
                >
                  {{ account.displayName }} (@{{ account.value }}) - {{ account.roleLabel }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="password" class="form-label">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0110 0v4"/>
                </svg>
                Mot de passe
              </label>
              <input
                type="password"
                id="password"
                v-model="password"
                class="form-input"
                placeholder="Entrez votre mot de passe"
              />
            </div>

            <div v-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </div>

            <button type="submit" class="btn-login" :disabled="!selectedUsername || isLoading">
              <span v-if="isLoading">⏳ Connexion en cours...</span>
              <span v-else>Se connecter</span>
            </button>
          </form>
        </div>

        <!-- Lien d'inscription -->
        <div class="inscription-section">
          <p>Vous n'avez pas encore de compte ?</p>
          <router-link to="/register" class="btn-inscription">
            Créer un compte soumissionnaire
          </router-link>
        </div>

        <!-- Lien de contact -->
        <div class="contact-section">
          <router-link to="/contact" class="contact-link">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
              <polyline points="22,6 12,13 2,6"/>
            </svg>
            Besoin d'aide ? Contactez-nous
          </router-link>
        </div>
      </div>
    </main>

    <!-- Footer harmonisé avec Home -->
    <footer class="public-footer">
      <div class="footer-container">
        <div class="footer-simple">
          <p>&copy; {{ currentYear}} Direction Générale de la Planification des Politiques Économiques (DGPPE)</p>
          <p>PLASMAP • Version 1.0 • Développée par <a href="https://www.linkedin.com/in/dr-aboubekrine-sakho-4851981b0/" target="_blank" rel="noopener noreferrer" class="footer-link">Abou Sakho</a></p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import logoUrl from '../assets/logo-dgppe.png'

export default {
  name: "Login",
  data() {
    return {
      logoUrl,
      accounts: [],
      rolesByUsername: {},
      selectedUsername: '',
      password: '',
      errorMessage: '',
      isLoading: false
    };
  },
  computed: {
    currentYear() { return new Date().getFullYear(); }
  },
  mounted() {
    this.loadAccounts();
  },
  methods: {
    async loadAccounts() {
      try {
        const res = await fetch("/api/users");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const users = await res.json();

        // Construire la map username -> role
        const map = {};
        for (const u of users) {
          map[u.username] = u.role;
        }
        this.rolesByUsername = map;

        // Construire la liste d'accounts pour l'affichage
        this.accounts = users.map(u => ({
          value: u.username,
          displayName: u.display_name || u.username,
          roleLabel: this.getRoleLabelByRole(u.role),
          email: u.email || null,
          telephone: u.telephone || null,
          id: u.id
        }));
      } catch (e) {
        console.error("Erreur de chargement des comptes:", e);
        // Fallback: liste statique si le backend est indisponible
        const fallbackUsers = [
          { username: 'soumissionnaire', role: 'soumissionnaire', display_name: 'Sectoriel' },
          { username: 'evaluateur1', role: 'evaluateur', display_name: 'Agent DPSE 1' },
          { username: 'evaluateur2', role: 'evaluateur', display_name: 'Agent DPSE 2' },
          { username: 'secretariatsct', role: 'secretariatsct', display_name: 'Chef de Division DP' },
          { username: 'presidencesct', role: 'presidencesct', display_name: 'Directeur Planification' },
          { username: 'presidencecomite', role: 'presidencecomite', display_name: 'DG DGPPE' },
          { username: 'admin', role: 'admin', display_name: 'CT DGPPE' },
          { username: 'invite', role: 'invite', display_name: 'Invite' }
        ];
        const map = {};
        for (const u of fallbackUsers) map[u.username] = u.role;
        this.rolesByUsername = map;
        this.accounts = fallbackUsers.map(u => ({
          value: u.username,
          displayName: u.display_name || u.username,
          roleLabel: this.getRoleLabelByRole(u.role)
        }));
      }
    },
    getRoleLabelByRole(role) {
      const labels = {
        soumissionnaire: "Soumissionnaire",
        evaluateur: "Évaluateur",
        secretariatsct: "Secrétariat SCT",
        presidencesct: "Présidence SCT",
        presidencecomite: "Présidence Comité",
        admin: "Administrateur",
        invite: "Invité"
      };
      return labels[role] || role;
    },
    async handleLoginSubmit() {
      this.errorMessage = '';
      this.isLoading = true;

      try {
        const uname = this.selectedUsername;
        if (!uname) {
          this.errorMessage = 'Veuillez sélectionner un compte';
          return;
        }

        // Vérification du mot de passe
        if (uname === 'admin') {
          // Pour le compte admin, le mot de passe doit être "admin"
          if (this.password !== 'admin') {
            this.errorMessage = 'Mot de passe incorrect pour le compte admin';
            return;
          }
        } else {
          // Pour les autres comptes, accepter un mot de passe vide ou n'importe quel mot de passe
          // (pas de validation stricte pour les comptes de test)
        }

        const role = this.rolesByUsername[uname] || uname;

        // Trouver les infos depuis la liste des accounts
        const account = this.accounts.find(acc => acc.value === uname);
        const displayName = account ? account.displayName : uname;

        const user = {
          id: account ? account.id : null,
          username: uname,
          nom: uname,
          role,
          display_name: displayName,
          email: account ? account.email : null,
          telephone: account ? account.telephone : null
        };
        localStorage.setItem("user", JSON.stringify(user));

        // Enregistrer la connexion
        try {
          await fetch('/api/connexion-logs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              username: uname,
              role
            })
          });
        } catch (err) {
          console.error('Erreur lors de l\'enregistrement de la connexion:', err);
          // Ne pas bloquer la connexion si le log échoue
        }

        // Redirection vers le dashboard approprié selon le rôle
        const normalizeRole = (r) => {
          if (!r) return r;
          if (typeof r === 'string' && r.toLowerCase().startsWith('evaluateur')) return 'evaluateur';
          return r;
        };
        const normalizedRole = normalizeRole(role);
        this.$router.push(`/${normalizedRole}`);
      } catch (error) {
        this.errorMessage = 'Erreur lors de la connexion: ' + error.message;
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
}

/* ==================== EN-TÊTE PUBLIC ==================== */
.public-header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
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
  color: #2e6b6b;
  margin: 0;
  line-height: 1.2;
}

.header-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
  line-height: 1.2;
}

.header-platform {
  font-size: 0.8rem;
  color: #2e6b6b;
  margin: 0.25rem 0 0 0;
  font-weight: 500;
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
    display: none;
  }
}

.login-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 2rem 1rem;
}

.login-container {
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
}

/* ==================== HEADER ==================== */
.login-header {
  text-align: center;
  margin-bottom: 2rem;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.logo-image {
  height: 70px;
  width: auto;
  margin-bottom: 1rem;
  transition: opacity 0.2s ease;
}

.logo-image:hover {
  opacity: 0.8;
}

.login-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.login-subtitle {
  font-size: 0.95rem;
  color: #718096;
  margin: 0;
}

/* ==================== LOGIN FORM SECTION ==================== */
.login-form-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 2.5rem;
  border: 1px solid #e2e8f0;
}

.login-form {
  max-width: 500px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 1.75rem;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.form-label svg {
  color: #004080;
}

.form-select,
.form-input {
  width: 100%;
  padding: 0.875rem 1rem;
  font-size: 0.95rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.2s ease;
  background: white;
  color: #2d3748;
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: #004080;
  box-shadow: 0 0 0 3px rgba(0, 64, 128, 0.1);
}

.form-select {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23333' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  padding-right: 2.5rem;
}

.form-help {
  margin-top: 0.5rem;
  margin-bottom: 0;
}

.form-help small {
  color: #718096;
  font-size: 0.85rem;
  font-style: italic;
}

.form-help strong {
  color: #004080;
  font-weight: 600;
}

.error-message {
  padding: 0.875rem 1rem;
  background: #fee2e2;
  border: 1px solid #fca5a5;
  border-radius: 6px;
  color: #991b1b;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  text-align: center;
}

.btn-login {
  width: 100%;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, var(--dgppe-primary) 0%, var(--dgppe-primary-light) 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 8px rgba(0, 51, 102, 0.15);
}

.btn-login:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--dgppe-primary-light) 0%, var(--dgppe-primary) 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 51, 102, 0.2);
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* ==================== FOOTER ==================== */
.login-footer {
  text-align: center;
  margin-top: var(--dgppe-spacing-6);
}

.login-footer p {
  font-size: 0.875rem;
  color: var(--dgppe-text-muted);
  margin: 0;
}

.login-footer-centered {
  text-align: center;
  margin-top: var(--dgppe-spacing-6);
  padding: var(--dgppe-spacing-4) 0;
}

.login-footer-centered p {
  font-size: 0.875rem;
  color: var(--dgppe-text-muted);
  margin: 0 0 var(--dgppe-spacing-2) 0;
}

.login-footer-centered a {
  color: var(--dgppe-primary);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
}

.login-footer-centered a:hover {
  text-decoration: underline;
}

/* Footer harmonisé avec Home */
.public-footer {
  background: linear-gradient(135deg, var(--dgppe-primary) 0%, #1e40af 100%);
  color: white;
  padding: 1.5rem 0;
  margin-top: auto;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.footer-simple {
  text-align: center;
}

.footer-simple p:first-child {
  font-size: 0.875rem;
  font-weight: 500;
  margin: 0 0 0.5rem 0;
  color: white;
}

.footer-simple p:last-child {
  font-size: 0.75rem;
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
}

.footer-link {
  color: white;
  text-decoration: underline;
  font-weight: 500;
  transition: opacity 0.2s ease;
}

.footer-link:hover {
  opacity: 0.8;
}

/* ==================== SECTION INSCRIPTION ==================== */
.inscription-section {
  text-align: center;
  margin-top: 2rem;
  padding: 1.75rem;
  background: white;
  border-radius: 10px;
  border: 2px solid #e2e8f0;
}

.inscription-section p {
  margin: 0 0 1rem 0;
  color: #4a5568;
  font-size: 0.95rem;
}

.btn-inscription {
  display: inline-block;
  padding: 0.875rem 2rem;
  background: linear-gradient(135deg, var(--dgppe-primary) 0%, var(--dgppe-primary-light) 100%);
  color: white;
  text-decoration: none;
  font-weight: 600;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-size: 1rem;
  box-shadow: 0 4px 8px rgba(0, 51, 102, 0.15);
}

.btn-inscription:hover {
  background: linear-gradient(135deg, var(--dgppe-primary-light) 0%, var(--dgppe-primary) 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 51, 102, 0.2);
}

/* ==================== SECTION CONTACT ==================== */
.contact-section {
  text-align: center;
  margin-top: 1.5rem;
}

.contact-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  text-decoration: none;
  font-size: 0.875rem;
  transition: color 0.2s;
}

.contact-link:hover {
  color: var(--dgppe-primary);
}

.contact-link svg {
  opacity: 0.7;
}

/* ==================== RESPONSIVE ==================== */
@media (max-width: 768px) {
  .login-page {
    padding: 1rem;
  }

  .login-title {
    font-size: 1.5rem;
  }

  .logo-image {
    height: 60px;
  }

  .login-header {
    padding: 1.5rem;
  }

  .login-form-section {
    padding: 1.5rem;
  }

  .login-form {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .form-select,
  .form-input {
    font-size: 0.875rem;
    padding: 0.75rem;
  }

  .btn-login {
    padding: 0.875rem 1.5rem;
    font-size: 0.95rem;
  }
}
</style>