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
          <p class="login-subtitle">Saisissez vos identifiants pour accéder à la plateforme</p>
        </div>

        <!-- Bandeau Visiteur en haut (visible avant le formulaire en mode vitrine) -->
        <div v-if="isVitrineMode" class="visiteur-banner">
          <div class="visiteur-banner-content">
            <h2>Consultez les projets publics</h2>
            <p>Accédez librement aux fiches d'évaluation des projets et programmes maturés.</p>
          </div>
          <button @click="loginAsVisiteur" class="btn-visiteur-large">
            Accéder en mode consultation →
          </button>
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
                {{ isVitrineMode ? 'Identifiant' : 'Compte utilisateur' }}
              </label>
              <!-- Mode vitrine : input libre (ANSD) -->
              <input
                v-if="isVitrineMode"
                type="text"
                id="username"
                v-model="username"
                class="form-input"
                placeholder=""
                autocomplete="username"
              />
              <!-- Mode dev : dropdown des comptes test (Render) -->
              <select
                v-else
                id="username"
                v-model="username"
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
                placeholder=""
                autocomplete="current-password"
              />
            </div>

            <div v-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </div>

            <button type="submit" class="btn-login" :disabled="isLoading || (!isVitrineMode && !username)">
              <span v-if="isLoading">⏳ Connexion en cours...</span>
              <span v-else>Se connecter</span>
            </button>

            <div class="forgot-link">
              <router-link to="/forgot-password">Mot de passe oublié ?</router-link>
            </div>
          </form>
        </div>

        <!-- Bloc d'accès secondaires (inscription + visiteur) -->
        <div class="acces-secondaires">
          <div class="acces-option">
            <p>Vous n'avez pas encore de compte ?</p>
            <router-link v-if="!isVitrineMode" to="/register" class="btn-inscription">
              Créer un compte soumissionnaire
            </router-link>
            <button v-else @click="showInscriptionMessage" class="btn-inscription">
              Créer un compte soumissionnaire
            </button>
          </div>
          <div class="acces-separator"></div>
          <div class="acces-option">
            <p>Vous êtes un visiteur ?</p>
            <button @click="loginAsVisiteur" class="btn-visiteur">
              Accéder en mode consultation
            </button>
          </div>
        </div>

        <!-- Modale d'information (stabilisation) -->
        <div v-if="showInfoModal" class="info-modal-overlay" @click.self="showInfoModal = false">
          <div class="info-modal">
            <div class="info-modal-icon">🚧</div>
            <h3>Plateforme en cours de stabilisation</h3>
            <p>L'accès complet sera disponible prochainement.</p>
            <button @click="showInfoModal = false" class="btn-info-close">D'accord</button>
          </div>
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
      username: '',
      password: '',
      errorMessage: '',
      isLoading: false,
      showInfoModal: false
    };
  },
  computed: {
    currentYear() { return new Date().getFullYear(); },
    isVitrineMode() { return import.meta.env.VITE_VITRINE_MODE === 'true'; }
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

        // Ordre souhaité des rôles dans la liste déroulante
        const roleOrder = ['soumissionnaire', 'evaluateur', 'secretariatsct', 'presidencesct', 'presidencecomite', 'membrecomite', 'ministre_economie', 'admin', 'invite'];

        // Exclure le rôle "invite" du dropdown (accessible via bouton "Mode consultation" séparé)
        const filteredUsers = users.filter(u => u.role !== 'invite');

        // Construire la liste d'accounts pour l'affichage
        this.accounts = filteredUsers.map(u => ({
          value: u.username,
          displayName: u.display_name || u.username,
          roleLabel: this.getRoleLabelByRole(u.role),
          email: u.email || null,
          telephone: u.telephone || null,
          nom_structure: u.nom_structure || null,
          point_focal_organisme: u.point_focal_organisme || null,
          id: u.id,
          role: u.role
        })).sort((a, b) => {
          const indexA = roleOrder.indexOf(a.role);
          const indexB = roleOrder.indexOf(b.role);
          return (indexA === -1 ? 999 : indexA) - (indexB === -1 ? 999 : indexB);
        });
      } catch (e) {
        console.error("Erreur de chargement des comptes:", e);
        // Fallback: liste statique si le backend est indisponible
        const fallbackUsers = [
          { username: 'soumissionnaire', role: 'soumissionnaire', display_name: 'Sectoriel' },
          { username: 'ousseynou.badiane', role: 'evaluateur', display_name: 'Ousseynou BADIANE' },
          { username: 'oumar.diedhou', role: 'evaluateur', display_name: 'Oumar DIEDHOU' },
          { username: 'serignedjibril.diene', role: 'evaluateur', display_name: 'Serigne Djibril DIENE' },
          { username: 'papedethie.diouf', role: 'evaluateur', display_name: 'Pape Déthié DIOUF' },
          { username: 'papeoumar.diouf', role: 'evaluateur', display_name: 'Pape Oumar DIOUF' },
          { username: 'fatoufaboure.djiba', role: 'evaluateur', display_name: 'Fatou Fabouré DJIBA' },
          { username: 'suleymane.haidara', role: 'evaluateur', display_name: 'Suleymane HAIDARA' },
          { username: 'amy.ka', role: 'evaluateur', display_name: 'Amy KA' },
          { username: 'richard.tendeng', role: 'evaluateur', display_name: 'Richard TENDENG' },
          { username: 'fatou.willane', role: 'evaluateur', display_name: 'Fatou WILLANE' },
          { username: 'aminata.faye', role: 'evaluateur', display_name: 'Aminata FAYE' },
          { username: 'mamesane.toure', role: 'evaluateur', display_name: 'Mame Sané TOURE' },
          { username: 'babacar.sall', role: 'evaluateur', display_name: 'Babacar SALL' },
          { username: 'mamadouibrahima.marone', role: 'evaluateur', display_name: 'Mamadou Ibrahima MARONE' },
          { username: 'sokhnamar.syll', role: 'evaluateur', display_name: 'Sokhna Mar SYLL' },
          { username: 'fatoubambabachir.mbow', role: 'evaluateur', display_name: 'Fatou Bamba Bachir MBOW' },
          { username: 'deguene.mbodj', role: 'evaluateur', display_name: 'Déguène MBODJ' },
          { username: 'moustaphadjamil.sy', role: 'evaluateur', display_name: 'Moustapha Diamil SY' },
          { username: 'abdou.sene', role: 'evaluateur', display_name: 'Abdou SENE' },
          { username: 'papasamba.lo', role: 'evaluateur', display_name: 'Papa Samba LO' },
          { username: 'thiernoibrahima.gaye', role: 'evaluateur', display_name: 'Thierno Ibrahima GAYE' },
          { username: 'agnes.thiaw', role: 'evaluateur', display_name: 'Agnès THIAW' },
          { username: 'syleymane.niang', role: 'evaluateur', display_name: 'Syleymane NIANG' },
          { username: 'mamoudououmar.kane', role: 'evaluateur', display_name: 'Mamoudou Oumar KANE' },
          { username: 'salif.signate', role: 'evaluateur', display_name: 'Salif SIGNATÉ' },
          { username: 'secretariatsct', role: 'secretariatsct', display_name: 'Chef de Division DP' },
          { username: 'presidencesct', role: 'presidencesct', display_name: 'Directeur Planification' },
          { username: 'presidencecomite', role: 'presidencecomite', display_name: 'DG DGPPE' },
          { username: 'membrecomite', role: 'membrecomite', display_name: 'Membre Comité' },
          { username: 'ministre_economie', role: 'ministre_economie', display_name: 'Cabinet du Ministre' },
          { username: 'admin', role: 'admin', display_name: 'CT DGPPE' },
          { username: 'invite', role: 'invite', display_name: 'Visiteur' }
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
        membrecomite: "Membre Comité",
        ministre_economie: "Ministre de l'Économie",
        admin: "Administrateur",
        invite: "Invité"
      };
      return labels[role] || role;
    },
    showInscriptionMessage() {
      this.showInfoModal = true;
    },
    loginAsVisiteur() {
      // Connexion automatique en tant que visiteur (rôle invite)
      const user = {
        id: null,
        username: 'invite',
        nom: 'Visiteur',
        role: 'invite',
        display_name: 'Visiteur',
        email: null,
        telephone: null,
      };
      localStorage.setItem('user', JSON.stringify(user));
      this.$router.push('/visiteur');
    },
    async handleLoginSubmit() {
      this.errorMessage = '';
      this.isLoading = true;

      // Mode vitrine : pas de vraie authentification, on affiche la même
      // modale que le bouton « Créer un compte » pour cohérence.
      if (import.meta.env.VITE_VITRINE_MODE === 'true') {
        this.isLoading = false;
        this.showInfoModal = true;
        return;
      }

      try {
        const uname = (this.username || '').trim();
        if (!uname) {
          this.errorMessage = 'Veuillez sélectionner un compte';
          return;
        }
        // Mode dev (Render) : compat avec les comptes test (admin/admin, autres = pwd libre)
        if (uname === 'admin' && this.password !== 'admin') {
          this.errorMessage = 'Mot de passe incorrect pour le compte admin';
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
          telephone: account ? account.telephone : null,
          nom_structure: account ? account.nom_structure : null,
          point_focal_organisme: account ? account.point_focal_organisme : null
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
  padding: 1rem;
}

.login-container {
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
}

/* ==================== HEADER ==================== */
.login-header {
  text-align: center;
  margin-bottom: 1rem;
  background: white;
  padding: 1.1rem 1.5rem;
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
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a202c;
  margin: 0 0 0.25rem 0;
}

.login-subtitle {
  font-size: 0.9rem;
  color: #718096;
  margin: 0;
}

/* ==================== LOGIN FORM SECTION ==================== */
.login-form-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 1.5rem 2rem;
  border: 1px solid #e2e8f0;
}

.login-form {
  max-width: 500px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 1rem;
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

.forgot-link {
  text-align: center;
  margin-top: 0.75rem;
}
.forgot-link a {
  color: var(--dgppe-primary);
  font-size: 0.9rem;
  text-decoration: none;
}
.forgot-link a:hover {
  text-decoration: underline;
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

/* ==================== BANDEAU VISITEUR (haut de page, mode vitrine) ==================== */
.visiteur-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1.1rem 1.5rem;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #2E6B6B 0%, #1e4b4b 100%);
  color: #fff;
  border-radius: 12px;
  box-shadow: 0 6px 18px rgba(46, 107, 107, 0.25);
  animation: fade-in-up 0.45s ease-out both;
}
.visiteur-banner-content { flex: 1; min-width: 0; }
.visiteur-banner-content h2 {
  margin: 0 0 0.2rem 0; font-size: 1.1rem; font-weight: 700; color: #fff;
}
.visiteur-banner-content p {
  margin: 0; font-size: 0.88rem; opacity: 0.92; line-height: 1.4;
}
.btn-visiteur-large {
  white-space: nowrap;
  padding: 0.75rem 1.5rem;
  background: #fff;
  color: #2E6B6B;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}
.btn-visiteur-large:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 14px rgba(0,0,0,0.18);
}
@media (max-width: 600px) {
  .visiteur-banner { flex-direction: column; gap: 0.85rem; text-align: center; padding: 1rem; }
  .btn-visiteur-large { width: 100%; }
}

/* ==================== SECTION INSCRIPTION ==================== */
.acces-secondaires {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
  padding: 1rem 1.25rem;
  background: white;
  border-radius: 10px;
  border: 2px solid #e2e8f0;
}
.acces-option {
  text-align: center;
}
.acces-option p {
  margin: 0 0 0.5rem 0;
  color: #4a5568;
  font-size: 0.88rem;
}
.acces-separator {
  width: 1px;
  height: 60px;
  background: #e2e8f0;
}

@media (max-width: 600px) {
  .acces-secondaires { grid-template-columns: 1fr; }
  .acces-separator { width: 100%; height: 1px; }
}

.btn-visiteur {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem 1.5rem;
  background: #fff;
  color: var(--dgppe-primary);
  border: 2px solid var(--dgppe-primary);
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.2s;
}
.btn-visiteur:hover {
  background: var(--dgppe-primary);
  color: white;
}

.inscription-section.legacy {
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

.btn-inscription:hover:not(.btn-disabled) {
  background: linear-gradient(135deg, var(--dgppe-primary-light) 0%, var(--dgppe-primary) 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 51, 102, 0.2);
}

.btn-inscription.btn-disabled {
  background: #cbd5e1;
  color: #64748b;
  cursor: not-allowed;
  box-shadow: none;
  border: none;
}

.login-form-section,
.acces-secondaires {
  animation: fade-in-up 0.4s ease-out both;
}
.acces-secondaires { animation-delay: 0.08s; }

@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ==================== MODALE D'INFORMATION ==================== */
.info-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  animation: fade-in 0.2s ease-out;
}
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }

.info-modal {
  background: white;
  border-radius: 16px;
  padding: 2rem 2.25rem;
  max-width: 420px;
  width: calc(100% - 2rem);
  text-align: center;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
  animation: pop 0.25s ease-out;
}
@keyframes pop { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }

.info-modal-icon { font-size: 3rem; margin-bottom: 0.75rem; }
.info-modal h3 {
  margin: 0 0 0.6rem 0;
  font-size: 1.25rem;
  color: #1e293b;
}
.info-modal p {
  margin: 0 0 1.5rem 0;
  color: #64748b;
  line-height: 1.5;
}
.btn-info-close {
  padding: 0.7rem 2rem;
  background: linear-gradient(135deg, var(--dgppe-primary) 0%, var(--dgppe-primary-light) 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: transform 0.15s ease;
}
.btn-info-close:hover { transform: translateY(-2px); }

/* ==================== SECTION CONTACT ==================== */
.contact-section {
  text-align: center;
  margin-top: 0.6rem;
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