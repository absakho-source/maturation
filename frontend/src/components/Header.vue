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
        <div v-if="user.role === 'admin' || user.role === 'secretariatsct'" class="dropdown" ref="dropdown">
          <button @click="toggleDropdown" class="nav-link dropdown-toggle">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M12 1v6m0 6v6M5.64 5.64l4.24 4.24m4.24 4.24l4.24 4.24M1 12h6m6 0h6M5.64 18.36l4.24-4.24m4.24-4.24l4.24-4.24"/>
            </svg>
            Administration
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="chevron" :class="{ 'chevron-open': dropdownOpen }">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </button>
          <div v-if="dropdownOpen" class="dropdown-menu">
            <router-link to="/mon-profil" class="dropdown-item" @click="closeDropdown">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              Mon Profil
            </router-link>
            <router-link to="/gestion-comptes" class="dropdown-item" @click="closeDropdown">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 00-3-3.87"/>
                <path d="M16 3.13a4 4 0 010 7.75"/>
              </svg>
              Gestion des comptes
            </router-link>
            <router-link to="/formulaire-editor" class="dropdown-item" @click="closeDropdown">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              Éditeur de formulaire
            </router-link>
            <router-link to="/ministeres-editor" class="dropdown-item" @click="closeDropdown">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
              Gestion des ministères
            </router-link>
          </div>
        </div>
        <router-link v-if="user.role !== 'admin' && user.role !== 'secretariatsct'" to="/mon-profil" class="nav-link">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
          Mon Profil
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
  data() {
    return {
      dropdownOpen: false
    };
  },
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
    toggleDropdown() {
      this.dropdownOpen = !this.dropdownOpen;
    },
    closeDropdown() {
      this.dropdownOpen = false;
    },
    logout() {
      localStorage.removeItem("user");
      this.$router.push("/");
    },
    handleClickOutside(event) {
      if (this.$refs.dropdown && !this.$refs.dropdown.contains(event.target)) {
        this.dropdownOpen = false;
      }
    }
  },
  mounted() {
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
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
  gap: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.8rem;
  background: transparent;
  color: var(--dgppe-text);
  text-decoration: none;
  border-radius: 6px;
  border: 1px solid var(--dgppe-gray-300);
  font-size: 0.85rem;
  font-weight: 400;
  transition: all 0.2s ease;
}

.nav-link:hover {
  background: var(--dgppe-light);
  border-color: var(--dgppe-primary);
  color: var(--dgppe-primary);
}

.nav-link svg {
  flex-shrink: 0;
}

.dropdown {
  position: relative;
}

.dropdown-toggle {
  cursor: pointer;
}

.chevron {
  transition: transform 0.2s ease;
  margin-left: 0.2rem;
}

.chevron-open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  min-width: 220px;
  background: var(--dgppe-white);
  border: 1px solid var(--dgppe-gray-300);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  overflow: hidden;
  animation: dropdownFadeIn 0.2s ease;
}

@keyframes dropdownFadeIn {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.7rem 1rem;
  color: var(--dgppe-text);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 400;
  transition: all 0.2s ease;
  border-bottom: 1px solid var(--dgppe-gray-200);
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background: var(--dgppe-light);
  color: var(--dgppe-primary);
  padding-left: 1.2rem;
}

.dropdown-item svg {
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