<template>
  <header class="app-header">
    <div class="header-content">
      <div class="logo-section" @click="$router.push('/')" style="cursor: pointer;">
        <img src="/src/assets/logo-dgppe.png" alt="Logo DGPPE" class="logo-dgppe" />
        <div class="header-title">
          <span class="ministry-name">Ministère de l'Économie, du Plan et de la Coopération</span>
          <span class="direction-name">Direction Générale de la Planification des Politiques Économiques</span>
          <span class="platform-name">Plateforme de Maturation des Projets Publics</span>
        </div>
      </div>
      <nav v-if="user" class="nav-section">
        <router-link
          v-if="user.role === 'admin' || user.role === 'secretariatsct'"
          to="/gestion-comptes"
          class="nav-link"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 00-3-3.87"/>
            <path d="M16 3.13a4 4 0 010 7.75"/>
          </svg>
          Gestion des comptes
        </router-link>
        <div class="user-info">
          <div class="user-details">
            <span class="user-display-name">{{ user.display_name || user.username }}</span>
            <span class="user-username">@{{ user.username }}</span>
            <span class="user-role">{{ roleLabel }}</span>
          </div>
          <button @click="logout" class="btn btn-secondary btn-sm logout-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
              <polyline points="16,17 21,12 16,7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            Déconnexion
          </button>
        </div>
      </nav>
    </div>
  </header>
</template>

<script>
export default {
  name: "Header",
  computed: {
    user() {
      return JSON.parse(localStorage.getItem("user") || "null");
    },
    roleLabel() {
      const labels = {
        soumissionnaire: "Soumissionnaire",
        evaluateur1: "Évaluateur",
        evaluateur2: "Évaluateur",
        secretariatsct: "Secrétariat SCT",
        presidencesct: "Présidence SCT",
        presidencecomite: "Présidence Comité",
        admin: "Administrateur"
      };
      return labels[this.user?.role] || this.user?.role || "";
    }
  },
  methods: {
    logout() {
      localStorage.removeItem("user");
      this.$router.push("/");
    }
  }
};
</script>

<style scoped>
.app-header {
  background: var(--dgppe-white);
  border-bottom: 1px solid var(--dgppe-gray-200);
  box-shadow: var(--dgppe-shadow-sm);
  padding: var(--dgppe-spacing-4) var(--dgppe-spacing-6);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--dgppe-spacing-6);
}

.logo-section {
  display: flex;
  align-items: center;
  gap: var(--dgppe-spacing-4);
  transition: opacity 0.2s ease;
}

.logo-section:hover {
  opacity: 0.8;
}

.logo-dgppe {
  height: 50px;
  width: auto;
}

.header-title {
  display: flex;
  flex-direction: column;
}

.ministry-name {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--dgppe-text);
  line-height: 1.2;
}

.direction-name {
  font-size: 0.875rem;
  font-weight: 400;
  color: var(--dgppe-text-muted);
  line-height: 1.2;
  margin-top: 1px;
}

.platform-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--dgppe-primary);
  line-height: 1.2;
  margin-top: 2px;
}

.nav-section {
  display: flex;
  align-items: center;
  gap: var(--dgppe-spacing-4);
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  background: var(--dgppe-primary);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.nav-link:hover {
  background: var(--dgppe-primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 64, 128, 0.2);
}

.nav-link svg {
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--dgppe-spacing-4);
}

.user-details {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  text-align: right;
}

.user-display-name {
  font-weight: 600;
  color: var(--dgppe-text);
  font-size: 0.875rem;
  line-height: 1.2;
}

.user-username {
  font-size: 0.75rem;
  color: var(--dgppe-text-muted);
  font-family: 'Courier New', monospace;
  margin-top: 1px;
}

.user-role {
  font-size: 0.75rem;
  color: var(--dgppe-text-muted);
  margin-top: 1px;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: var(--dgppe-spacing-2);
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: var(--dgppe-spacing-4);
  }
  
  .user-info {
    width: 100%;
    justify-content: space-between;
  }
  
  .user-details {
    align-items: flex-start;
    text-align: left;
  }
  
  .logo-dgppe {
    height: 40px;
  }
  
  .platform-name {
    font-size: 1rem;
  }
}
</style>