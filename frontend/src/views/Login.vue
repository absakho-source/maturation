<template>
  <div class="login-page">
    <main class="login-main">
      <div class="login-container">
        <!-- Logo DGPPE officiel -->
        <div class="login-header">
          <img src="/src/assets/logo-dgppe.png" alt="Logo DGPPE" class="logo-image" @click="$router.push('/')" style="cursor: pointer;" />
          <h1 class="login-title">Connexion</h1>
          <p class="login-subtitle">Sélectionnez votre profil pour accéder à la plateforme</p>
        </div>

        <!-- Sélecteur de profils (simple: nom + profil cliquable) -->
        <div class="profiles-section">
          <div class="profiles-grid">
            <div 
              v-for="account in accounts" 
              :key="account.value"
              class="profile-card"
              @click="handleLogin(account.value)"
            >
              <div class="profile-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
              </div>
              <div class="profile-info">
                <h3 class="profile-name">{{ account.displayName }}</h3>
                <div class="profile-username">@{{ account.value }}</div>
                <span class="role-badge">{{ account.roleLabel }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Lien d'inscription -->
        <div class="inscription-section">
          <p>Vous n'avez pas encore de compte ?</p>
          <router-link to="/register" class="btn-inscription">
            Créer un compte soumissionnaire
          </router-link>
        </div>
      </div>
    </main>

    <!-- Footer harmonisé avec Home -->
    <footer class="public-footer">
      <div class="footer-container">
        <div class="footer-simple">
          <p>&copy; {{ currentYear}} Direction Générale de la Planification des Politiques Économiques (DGPPE)</p>
          <p>PLASMAP • Version 1.0 • Développée par Abou Sakho</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: "Login",
  data() {
    return {
      accounts: [],
      rolesByUsername: {}
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
          roleLabel: this.getRoleLabelByRole(u.role)
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
    async handleLogin(username) {
      const uname = username;
      if (!uname) return;
      const role = this.rolesByUsername[uname] || uname;

      // Trouver le display_name depuis la liste des accounts
      const account = this.accounts.find(acc => acc.value === uname);
      const displayName = account ? account.displayName : uname;

      const user = {
        username: uname,
        nom: uname,
        role,
        display_name: displayName
      };
      localStorage.setItem("user", JSON.stringify(user));

      // Enregistrer la connexion
      try {
        await fetch('/api/connexion-logs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: uname, role })
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

/* ==================== PROFILES SECTION ==================== */
.profiles-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 2rem;
  border: 1px solid #e2e8f0;
}

.profiles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 0;
}

.profile-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #fafbfc;
}

.profile-card:hover {
  border-color: #004080;
  box-shadow: 0 4px 12px rgba(0, 64, 128, 0.12);
  background: white;
  transform: translateY(-2px);
}

.profile-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  border-radius: 10px;
  background: #e8eef5;
  color: #004080;
  flex-shrink: 0;
}

.profile-info {
  flex: 1;
}

.profile-info h3.profile-name {
  font-size: 1.05rem;
  font-weight: 600;
  color: #1a202c;
  margin: 0 0 0.25rem 0;
}

.profile-username {
  font-size: 0.8rem;
  color: #a0aec0;
  font-family: 'Courier New', monospace;
  margin-bottom: 0.35rem;
}

.role-badge {
  display: inline-block;
  font-size: 0.75rem;
  color: #004080;
  background: #e8eef5;
  border: 1px solid #d0dce8;
  border-radius: 999px;
  padding: 3px 10px;
  font-weight: 500;
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

/* ==================== RESPONSIVE ==================== */
@media (max-width: 768px) {
  .login-page {
    padding: 1rem;
  }

  .profiles-grid {
    grid-template-columns: 1fr;
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

  .profiles-section {
    padding: 1.5rem;
  }
}

@media (max-width: 480px) {
  .profile-card {
    padding: var(--dgppe-spacing-3);
  }
  
  .profile-icon {
    width: 40px;
    height: 40px;
  }
  
  .profile-info h3 {
    font-size: 0.9rem;
  }
}
</style>