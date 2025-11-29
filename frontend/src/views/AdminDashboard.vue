<template>
  <PageWrapper>
    <div class="admin-container">
      <div class="header-row">
        <h2 class="page-title">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 3v5h5"/>
            <path d="M3 8s2-4 8-4 8 4 8 4"/>
            <path d="M21 21v-5h-5"/>
            <path d="M21 16s-2 4-8 4-8-4-8-4"/>
          </svg>
          Tableau de bord - Administrateur
        </h2>
        <div class="header-buttons">
          <button @click="telechargerRapport" class="btn-download-rapport">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            Télécharger Rapport
          </button>
          <button @click="telechargerRapportElabore" class="btn-download-rapport elabore">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
            Générer Rapport Élaboré
          </button>
        </div>
      </div>

      <!-- Métriques de performance -->
      <div class="performance-metrics">
        <h3>Métriques de performance</h3>
        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-header">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12,6 12,12 16,14"/>
              </svg>
              Temps moyen de traitement
            </div>
            <div class="metric-value">{{ metrics.averageProcessingTime }}</div>
          </div>

          <div class="metric-card">
            <div class="metric-header">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
              Taux de validation
            </div>
            <div class="metric-value">{{ metrics.validationRate }}%</div>
          </div>

          <div class="metric-card">
            <div class="metric-header">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12,6 12,12 16,14"/>
              </svg>
              Délai moyen d'évaluation
            </div>
            <div class="metric-value">{{ metrics.averageEvaluationTime }}</div>
          </div>
        </div>
      </div>

      <!-- Volumes de financement -->
      <div class="financing-volumes">
        <h3>Volumes de financement</h3>
        <div class="financing-cards-grid">
          <div class="financing-card">
            <div class="financing-header">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              <span>Demandes soumises</span>
            </div>
            <div class="financing-amount">{{ formatCurrency(financingStats.totalSubmitted) }}</div>
            <div class="financing-count">{{ financingStats.countSubmitted }} projet(s)</div>
          </div>

          <div class="financing-card success">
            <div class="financing-header">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              <span>Décisions favorables (Comité)</span>
            </div>
            <div class="financing-amount">{{ formatCurrency(financingStats.totalApproved) }}</div>
            <div class="financing-count">{{ financingStats.countApproved }} projet(s)</div>
          </div>
        </div>
      </div>

      <!-- Onglets -->
      <div class="tabs">
        <button @click="activeTab = 'projects'" :class="{ active: activeTab === 'projects' }" class="tab-btn">
          📋 Tous les projets
        </button>
        <button @click="activeTab = 'stats'" :class="{ active: activeTab === 'stats' }" class="tab-btn">
          📊 Statistiques des projets
        </button>
        <button @click="activeTab = 'carte'" :class="{ active: activeTab === 'carte' }" class="tab-btn">
          🗺️ Carte des pôles territoriaux
        </button>
        <button @click="activeTab = 'users'" :class="{ active: activeTab === 'users' }" class="tab-btn">
          👥 Gestion des utilisateurs
        </button>
      </div>

      <!-- ============ ONGLET: GESTION DES UTILISATEURS ============ -->
      <div v-if="activeTab === 'users'" class="tab-content">
        <div class="users-section">
          <div class="section-header">
            <h3>Liste des utilisateurs</h3>
            <button @click="openCreateModal" class="btn-primary">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="16"/>
                <line x1="8" y1="12" x2="16" y2="12"/>
              </svg>
              Créer un utilisateur
            </button>
          </div>

          <div class="users-grid">
            <div v-for="user in users" :key="user.id" class="user-card">
              <div class="user-header">
                <div class="user-avatar" :class="'role-' + user.role">
                  {{ (user.display_name || user.username).charAt(0).toUpperCase() }}
                </div>
                <div class="user-info">
                  <h4>{{ user.display_name || user.username }}</h4>
                  <div class="user-username">@{{ user.username }}</div>
                  <span class="user-role" :class="'badge-' + user.role">{{ getRoleLabel(user.role) }}</span>
                </div>
              </div>
              <div class="user-actions">
                <button @click="openEditModal(user)" class="btn-edit">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                  </svg>
                  Modifier
                </button>
                <button @click="deleteUser(user)" class="btn-delete">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3,6 5,6 21,6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                  Supprimer
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ============ ONGLET: TOUS LES PROJETS ============ -->
      <div v-if="activeTab === 'projects'" class="tab-content">
        <div class="projects-section">
          <div class="section-header">
            <h2>📋 Tous les projets</h2>
            <div class="project-stats">
              <span class="stat-item">Total: <strong>{{ allProjects.length }}</strong></span>
              <span class="stat-item">En cours: <strong>{{ countByStatus(['soumis', 'assigné', 'évalué positivement']) }}</strong></span>
              <span class="stat-item">Validés: <strong>{{ countByStatus(['validé par presidencesct']) }}</strong></span>
            </div>
          </div>

          <!-- Barre de recherche -->
          <div class="search-bar">
            <input
              type="text"
              v-model="searchQuery"
              @input="applyFilters"
              placeholder="🔍 Rechercher par titre, numéro de projet, auteur, secteur..."
              class="search-input"
            />
          </div>

          <!-- Filtres compacts -->
          <div class="filters-compact">
            <button @click="toggleFilters" class="btn-toggle-filters">
              {{ showFilters ? '▲ Masquer les filtres' : '▼ Afficher les filtres' }}
            </button>
          </div>

          <div v-if="showFilters" class="filters-container">
            <div class="filter-group">
              <label>Année:</label>
              <select v-model="selectedYear" @change="applyFilters">
                <option value="">Toutes les années</option>
                <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
              </select>
            </div>
            <div class="filter-group">
              <label>Secteur:</label>
              <select v-model="selectedSecteur" @change="applyFilters">
                <option value="">Tous les secteurs</option>
                <option v-for="secteur in secteurs" :key="secteur" :value="secteur">{{ secteur }}</option>
              </select>
            </div>
            <div class="filter-group">
              <label>Statut:</label>
              <select v-model="selectedStatut" @change="applyFilters">
                <option value="">Tous les statuts</option>
                <option value="soumis">Soumis</option>
                <option value="assigné">Assigné</option>
                <option value="évalué positivement">Évalué positivement</option>
                <option value="évalué négativement">Évalué négativement</option>
                <option value="validé par presidencesct">Validé par présidence SCT</option>
                <option value="rejeté">Rejeté</option>
              </select>
            </div>
            <div class="filter-group">
              <label>Pôle:</label>
              <select v-model="selectedPole" @change="applyFilters">
                <option value="">Tous les pôles</option>
                <option v-for="pole in polesList" :key="pole" :value="pole">{{ pole }}</option>
              </select>
            </div>
            <button @click="resetFilters" class="btn-reset">Réinitialiser</button>
          </div>

          <!-- Vue cards pour mobile, tableau pour desktop -->
          <div class="projects-list-container">
            <!-- Vue en cartes (mobile) -->
            <div class="projects-cards mobile-only">
              <div v-for="project in paginatedProjects" :key="project.id" class="project-card">
                <div class="card-header">
                  <div class="card-title-row">
                    <strong class="project-number">{{ project.numero_projet || 'N/A' }}</strong>
                    <span class="badge" :class="getStatusClass(project.statut)">{{ project.statut }}</span>
                  </div>
                  <h3 class="card-title">{{ project.titre }}</h3>
                </div>
                <div class="card-body">
                  <div class="card-info-row">
                    <span class="info-label">Auteur:</span>
                    <span class="info-value">{{ project.auteur_nom || 'N/A' }}</span>
                  </div>
                  <div class="card-info-row">
                    <span class="info-label">Secteur:</span>
                    <span class="info-value">{{ project.secteur || 'N/A' }}</span>
                  </div>
                  <div class="card-info-row">
                    <span class="info-label">Coût:</span>
                    <span class="info-value">{{ formatCurrency(project.cout_estimatif) }}</span>
                  </div>
                  <div class="card-info-row">
                    <span class="info-label">Évaluateur:</span>
                    <span class="info-value">{{ project.evaluateur_nom || '-' }}</span>
                  </div>
                  <div class="card-info-row">
                    <span class="info-label">Date:</span>
                    <span class="info-value">{{ formatDate(project.date_soumission) }}</span>
                  </div>
                </div>
                <div class="card-actions">
                  <button @click="viewProject(project.id)" class="btn-view">👁️ Voir</button>
                  <button @click="deleteProject(project)" class="btn-delete">🗑️ Supprimer</button>
                </div>
              </div>
            </div>

            <!-- Vue en tableau (desktop) -->
            <div class="projects-table-container desktop-only">
              <table class="projects-table">
                <thead>
                  <tr>
                    <th>N° Projet</th>
                    <th>Titre</th>
                    <th>Auteur</th>
                    <th>Secteur</th>
                    <th>Coût (FCFA)</th>
                    <th>Statut</th>
                    <th>Évaluateur</th>
                    <th>Date</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="project in paginatedProjects" :key="project.id">
                    <td><strong class="project-number-table">{{ project.numero_projet || 'N/A' }}</strong></td>
                    <td class="project-title">{{ project.titre }}</td>
                    <td>{{ project.auteur_nom || 'N/A' }}</td>
                    <td>{{ project.secteur || 'N/A' }}</td>
                    <td class="project-cost">{{ formatCurrency(project.cout_estimatif) }}</td>
                    <td>
                      <span class="badge" :class="getStatusClass(project.statut)">{{ project.statut }}</span>
                    </td>
                    <td>{{ project.evaluateur_nom || '-' }}</td>
                    <td>{{ formatDate(project.date_soumission) }}</td>
                    <td>
                      <button @click="viewProject(project.id)" class="btn-view-small">👁️</button>
                      <button @click="deleteProject(project)" class="btn-delete-small">🗑️</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div v-if="filteredProjects.length === 0" class="empty-state">
              <p>Aucun projet trouvé avec les filtres sélectionnés</p>
            </div>
          </div>

          <!-- Pagination -->
          <div v-if="filteredProjects.length > 0" class="pagination">
            <div class="pagination-info">
              Affichage {{ ((currentPage - 1) * itemsPerPage) + 1 }} à {{ Math.min(currentPage * itemsPerPage, filteredProjects.length) }} sur {{ filteredProjects.length }} projets
            </div>
            <div class="pagination-controls">
              <button @click="previousPage" :disabled="currentPage === 1" class="btn-page">← Précédent</button>
              <span class="page-numbers">
                <button
                  v-for="page in visiblePages"
                  :key="page"
                  @click="goToPage(page)"
                  :class="['btn-page-number', { active: page === currentPage }]"
                >
                  {{ page }}
                </button>
              </span>
              <button @click="nextPage" :disabled="currentPage === totalPages" class="btn-page">Suivant →</button>
            </div>
            <div class="items-per-page">
              <label>Par page:</label>
              <select v-model="itemsPerPage" @change="resetPagination">
                <option :value="10">10</option>
                <option :value="25">25</option>
                <option :value="50">50</option>
                <option :value="100">100</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- ============ ONGLET: STATISTIQUES DES PROJETS ============ -->
      <div v-if="activeTab === 'stats'" class="tab-content">
        <StatsDashboard 
          role="admin" 
          username="admin"
        />
      </div>

      <!-- ============ ONGLET: CARTE DES PÔLES TERRITORIAUX ============ -->
      <div v-if="activeTab === 'carte'" class="tab-content">
        <CartesPolesComparaison />
      </div>

      <!-- ============ MODAL: CRÉER/ÉDITER UTILISATEUR ============ -->
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>{{ isEditing ? 'Modifier l\'utilisateur' : 'Créer un utilisateur' }}</h3>
            <button @click="closeModal" class="btn-close">×</button>
          </div>
          
          <div class="modal-body">
            <div class="form-row">
              <div class="form-group">
                <label>Nom d'utilisateur *</label>
                <input
                  v-model="formUser.username"
                  type="text"
                  placeholder="Entrez le nom d'utilisateur"
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label>Nom complet</label>
                <input
                  v-model="formUser.display_name"
                  type="text"
                  placeholder="Entrez le nom complet (ex: Agent DPSE)"
                  class="form-input"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Email</label>
                <input
                  v-model="formUser.email"
                  type="email"
                  placeholder="exemple@domaine.com"
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label>Téléphone</label>
                <input
                  v-model="formUser.telephone"
                  type="tel"
                  placeholder="+221 XX XXX XX XX"
                  class="form-input"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Fonction / Poste</label>
                <input
                  v-model="formUser.fonction"
                  type="text"
                  placeholder="Ex: Chef de service, Directeur, etc."
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label>Structure d'appartenance</label>
                <input
                  v-model="formUser.nom_structure"
                  type="text"
                  placeholder="Ex: DPSE, DGPPE, etc."
                  class="form-input"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Mot de passe {{ isEditing ? '(laisser vide pour conserver)' : '*' }}</label>
                <input
                  v-model="formUser.password"
                  type="password"
                  placeholder="Entrez le mot de passe"
                  class="form-input"
                />
              </div>

              <div class="form-group">
                <label>Rôle *</label>
                <select v-model="formUser.role" class="form-select">
                  <option value="">-- Choisir un rôle --</option>
                  <option value="soumissionnaire">Soumissionnaire</option>
                  <option value="evaluateur">Évaluateur</option>
                  <option value="secretariatsct">Secrétariat SCT</option>
                  <option value="presidencesct">Présidence SCT</option>
                  <option value="presidencecomite">Présidence du Comité</option>
                  <option value="admin">Administrateur</option>
                </select>
              </div>
            </div>

            <div v-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </div>
          </div>

          <div class="modal-footer">
            <button @click="closeModal" class="btn-secondary">Annuler</button>
            <button @click="saveUser" class="btn-primary">
              {{ isEditing ? 'Mettre à jour' : 'Créer' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';
import StatsDashboard from '../components/StatsDashboard.vue';
import CartesPolesComparaison from '../components/CartesPolesComparaison.vue';

export default {
  components: {
    PageWrapper,
    StatsDashboard,
    CartesPolesComparaison
  },
  data() {
    return {
      activeTab: 'projects', // 'users', 'projects', 'stats' ou 'carte'

      // Métriques de performance
      metrics: {
        averageProcessingTime: '0 jours',
        validationRate: 0,
        averageEvaluationTime: '0 jours'
      },

      // Volumes de financement
      financingStats: {
        totalSubmitted: 0,
        countSubmitted: 0,
        totalApproved: 0,
        countApproved: 0
      },

      // Gestion des utilisateurs
      users: [],
      showModal: false,
      isEditing: false,
      formUser: {
        id: null,
        username: '',
        display_name: '',
        email: '',
        telephone: '',
        fonction: '',
        nom_structure: '',
        password: '',
        role: ''
      },
      errorMessage: '',

      // Gestion des projets (onglet admin)
      allProjects: [],
      filteredProjects: [],
      availableYears: [],

      // Statistiques des projets
      projects: [],
      stats: { total: 0, attente: 0, traitement: 0, valides: 0, rejetes: 0 },
      selectedYear: "",
      selectedSecteur: "",
      selectedStatut: "",
      selectedPole: "",

      secteurs: [
        "agriculture-élevage-pêche",
        "environnement-eau-assainissement",
        "énergies-mines",
        "industrie-artisanat",
        "économie-finances-commerce",
        "tourisme-culture",
        "transports-infrastructures",
        "postes-communication-télécommunications-économie numérique",
        "population-jeunesse-emploi-travail-fonction publique",
        "habitat-urbanisme",
        "éducation-formation-recherche",
        "gouvernance-justice-défense-sécurité",
        "santé-action sociale",
        "sports-loisirs",
        "aménagement-développement territorial-décentralisation",
        "affaires étrangères-intégration",
      ],

      polesList: [
        "Dakar",
        "Thiès",
        "Centre (Kaolack, Fatick, Kaffrine)",
        "Diourbel-Louga",
        "Sud (Ziguinchor, Sédhiou, Kolda)",
        "Sud-Est (Tambacounda, Kédougou)",
        "Nord (Saint-Louis)",
        "Nord-Est (Matam)",
      ],

      // Recherche et pagination
      searchQuery: '',
      showFilters: false,
      currentPage: 1,
      itemsPerPage: 25,
    };
  },

  computed: {
    paginatedProjects() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredProjects.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.filteredProjects.length / this.itemsPerPage);
    },
    visiblePages() {
      const pages = [];
      const maxVisible = 5;
      let start = Math.max(1, this.currentPage - 2);
      let end = Math.min(this.totalPages, start + maxVisible - 1);

      if (end - start < maxVisible - 1) {
        start = Math.max(1, end - maxVisible + 1);
      }

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      return pages;
    }
  },

  mounted() {
    this.loadUsers();
    this.loadAllProjects();
    this.loadProjects();
    this.loadMetrics();
  },

  methods: {
    // ============ Gestion des utilisateurs ============
    async loadUsers() {
      try {
        const res = await fetch("/api/users");
        if (res.ok) {
          this.users = await res.json();
        } else {
          console.error("Erreur HTTP:", res.status);
        }
      } catch (error) {
        console.error("Erreur lors du chargement des utilisateurs:", error);
      }
    },
    
    openCreateModal() {
      this.isEditing = false;
      this.formUser = {
        id: null,
        username: '',
        display_name: '',
        email: '',
        telephone: '',
        fonction: '',
        nom_structure: '',
        password: '',
        role: ''
      };
      this.errorMessage = '';
      this.showModal = true;
    },

    openEditModal(user) {
      this.isEditing = true;
      this.formUser = {
        id: user.id,
        username: user.username,
        display_name: user.display_name || '',
        email: user.email || '',
        telephone: user.telephone || '',
        fonction: user.fonction || '',
        nom_structure: user.nom_structure || '',
        password: '', // Ne pas afficher le mot de passe
        role: user.role
      };
      this.errorMessage = '';
      this.showModal = true;
    },
    
    closeModal() {
      this.showModal = false;
      this.errorMessage = '';
    },
    
    async saveUser() {
      this.errorMessage = '';
      
      // Validation
      if (!this.formUser.username.trim()) {
        this.errorMessage = "Le nom d'utilisateur est requis";
        return;
      }
      
      if (!this.isEditing && !this.formUser.password.trim()) {
        this.errorMessage = "Le mot de passe est requis pour un nouvel utilisateur";
        return;
      }
      
      if (!this.formUser.role) {
        this.errorMessage = "Le rôle est requis";
        return;
      }
      
      try {
        let res;
        if (this.isEditing) {
          // Mise à jour
          const payload = {
            username: this.formUser.username,
            display_name: this.formUser.display_name,
            role: this.formUser.role
          };
          // Ajouter le mot de passe seulement s'il est fourni
          if (this.formUser.password.trim()) {
            payload.password = this.formUser.password;
          }

          res = await fetch(`/api/users/${this.formUser.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
        } else {
          // Création
          res = await fetch('/api/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              username: this.formUser.username,
              display_name: this.formUser.display_name,
              email: this.formUser.email,
              telephone: this.formUser.telephone,
              fonction: this.formUser.fonction,
              nom_structure: this.formUser.nom_structure,
              password: this.formUser.password,
              role: this.formUser.role,
              created_by_admin: true  // Indique que le compte est créé par l'admin
            })
          });
        }
        
        if (res.ok) {
          await this.loadUsers();
          this.closeModal();
          alert(this.isEditing ? 'Utilisateur mis à jour avec succès' : 'Utilisateur créé avec succès');
        } else {
          const error = await res.json();
          this.errorMessage = error.error || 'Une erreur est survenue';
        }
      } catch (error) {
        console.error("Erreur lors de la sauvegarde:", error);
        this.errorMessage = "Erreur de connexion au serveur";
      }
    },
    
    async deleteUser(user) {
      if (!confirm(`Êtes-vous sûr de vouloir supprimer l'utilisateur "${user.username}" ?`)) {
        return;
      }
      
      try {
        const res = await fetch(`/api/users/${user.id}`, {
          method: 'DELETE'
        });
        
        if (res.ok) {
          await this.loadUsers();
          alert('Utilisateur supprimé avec succès');
        } else {
          const error = await res.json();
          alert(error.error || 'Erreur lors de la suppression');
        }
      } catch (error) {
        console.error("Erreur lors de la suppression:", error);
        alert("Erreur de connexion au serveur");
      }
    },
    
    getRoleLabel(role) {
      const labels = {
        'soumissionnaire': 'Soumissionnaire',
        'evaluateur': 'Évaluateur',
        'secretariatsct': 'Secrétariat SCT',
        'presidencesct': 'Présidence SCT',
        'presidencecomite': 'Présidence du Comité',
        'admin': 'Administrateur'
      };
      return labels[role] || role;
    },
    
    // ============ Gestion des projets (admin) ============
    async loadAllProjects() {
      try {
        const res = await fetch("/api/projects?role=admin&username=admin");
        if (res.ok) {
          this.allProjects = await res.json();
          this.filteredProjects = [...this.allProjects];
          console.log("Projets admin chargés:", this.allProjects.length);

          // Calculer les statistiques de financement
          this.calculateFinancingStats();

          // Extraire les années disponibles
          this.extractAvailableYears();
        } else {
          console.error("Erreur HTTP:", res.status);
        }
      } catch (error) {
        console.error("Erreur lors du chargement des projets admin:", error);
      }
    },

    calculateFinancingStats() {
      // Tous les projets soumis
      this.financingStats.countSubmitted = this.allProjects.length;
      this.financingStats.totalSubmitted = this.allProjects.reduce((sum, p) => sum + (p.cout_estimatif || 0), 0);

      // Projets avec décision finale confirmée par la Présidence du Comité
      // ET avec avis favorable ou favorable sous conditions uniquement
      const approvedProjects = this.allProjects.filter(p =>
        p.decision_finale === 'confirme' &&
        (p.avis === 'favorable' || p.avis === 'favorable sous conditions')
      );
      this.financingStats.countApproved = approvedProjects.length;
      this.financingStats.totalApproved = approvedProjects.reduce((sum, p) => sum + (p.cout_estimatif || 0), 0);
    },

    extractAvailableYears() {
      const yearsSet = new Set();
      this.allProjects.forEach(project => {
        if (project.date_soumission) {
          const year = new Date(project.date_soumission).getFullYear();
          yearsSet.add(year);
        }
      });
      this.availableYears = Array.from(yearsSet).sort((a, b) => b - a); // Tri décroissant
    },

    applyFilters() {
      this.filteredProjects = this.allProjects.filter(project => {
        // Filtre par recherche textuelle
        let searchMatch = true;
        if (this.searchQuery && this.searchQuery.trim()) {
          const query = this.searchQuery.trim().toLowerCase();
          searchMatch = (
            (project.titre && project.titre.toLowerCase().includes(query)) ||
            (project.numero_projet && project.numero_projet.toLowerCase().includes(query)) ||
            (project.auteur_nom && project.auteur_nom.toLowerCase().includes(query)) ||
            (project.secteur && project.secteur.toLowerCase().includes(query)) ||
            (project.evaluateur_nom && project.evaluateur_nom.toLowerCase().includes(query))
          );
        }

        // Filtre par année
        let yearMatch = true;
        if (this.selectedYear) {
          if (project.date_soumission) {
            const projectYear = new Date(project.date_soumission).getFullYear();
            yearMatch = projectYear === parseInt(this.selectedYear);
          } else {
            yearMatch = false;
          }
        }

        const secteurMatch = !this.selectedSecteur || project.secteur === this.selectedSecteur;
        const statutMatch = !this.selectedStatut || project.statut === this.selectedStatut;
        const poleMatch = !this.selectedPole || (project.poles && project.poles.includes(this.selectedPole));

        return searchMatch && yearMatch && secteurMatch && statutMatch && poleMatch;
      });

      // Réinitialiser à la première page après filtrage
      this.currentPage = 1;
    },

    resetFilters() {
      this.selectedYear = "";
      this.selectedSecteur = "";
      this.selectedStatut = "";
      this.selectedPole = "";
      this.searchQuery = "";
      this.currentPage = 1;
      this.filteredProjects = [...this.allProjects];
    },

    toggleFilters() {
      this.showFilters = !this.showFilters;
    },

    // Pagination methods
    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
      }
    },

    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
      }
    },

    goToPage(page) {
      this.currentPage = page;
    },

    resetPagination() {
      this.currentPage = 1;
    },

    countByStatus(statuses) {
      if (Array.isArray(statuses)) {
        return this.allProjects.filter(p => statuses.includes(p.statut)).length;
      }
      return this.allProjects.filter(p => p.statut === statuses).length;
    },

    viewProject(projectId) {
      this.$router.push(`/project/${projectId}`);
    },

    async deleteProject(project) {
      const confirmation = confirm(
        `Êtes-vous sûr de vouloir supprimer le projet "${project.titre}" ?\n\nCette action est irréversible.`
      );

      if (!confirmation) return;

      try {
        const res = await fetch(`/api/projects/${project.id}?role=admin`, {
          method: 'DELETE'
        });
        
        if (res.ok) {
          await this.loadAllProjects(); // Recharger la liste
          alert('Projet supprimé avec succès');
        } else {
          const error = await res.json();
          alert(error.error || 'Erreur lors de la suppression');
        }
      } catch (error) {
        console.error("Erreur lors de la suppression:", error);
        alert("Erreur de connexion au serveur");
      }
    },

    getStatusClass(statut) {
      const map = {
        "soumis": "status-new",
        "assigné": "status-assigned",
        "en évaluation": "status-assigned",
        "en_evaluation": "status-assigned",
        "évalué": "status-pending",
        "en attente validation presidencesct": "status-pending",
        "validé par presidencesct": "status-validated",
        "valide_sct": "status-validated",
        "approuvé": "status-confirmed",
        "compléments demandés": "status-complement",
        "décision finale confirmée": "status-confirmed",
        "décision finale infirmée": "status-rejected",
        "rejeté par le Comité": "status-rejected",
        // Avis finaux (affichés quand decision_finale = 'confirme')
        "favorable": "status-favorable",
        "favorable sous conditions": "status-favorable-conditions",
        "défavorable": "status-defavorable",
        "évalué positivement": "status-favorable",
        "évalué négativement": "status-defavorable",
        "rejeté": "status-rejected"
      };
      return map[statut] || "status-default";
    },

    formatCurrency(amount) {
      if (!amount) return '-';
      return new Intl.NumberFormat('fr-FR').format(amount);
    },

    formatDate(dateStr) {
      if (!dateStr) return '-';
      return new Date(dateStr).toLocaleDateString('fr-FR');
    },
    
    // ============ Gestion des projets/statistiques ============
    async loadProjects() {
      try {
        const res = await fetch("/api/projects?role=admin&username=admin");
        if (res.ok) {
          this.projects = await res.json();
          this.filteredProjects = [...this.projects];
          this.computeStats();
          console.log("Projets chargés:", this.projects.length);
        } else {
          console.error("Erreur HTTP:", res.status);
        }
      } catch (error) {
        console.error("Erreur lors du chargement des projets:", error);
      }
    },
    
    computeStats() {
      const total = this.projects.length;
      const attente = this.projects.filter((p) => ["soumis", "en attente"].includes(p.statut)).length;
      const assignes = this.projects.filter((p) => p.statut === "assigné").length;
      const evalues = this.projects.filter((p) => ["évalué positivement", "évalué négativement", "complété et réévalué"].includes(p.statut)).length;
      const valides_secretariat = this.projects.filter((p) => p.statut === "validé par le secrétariat").length;
      const valides_presidencesct = this.projects.filter((p) => p.statut === "validé par presidencesct").length;
      const rejetes = this.projects.filter((p) => ["rejeté", "évalué négativement"].includes(p.statut)).length;

      this.stats = { 
        total, 
        attente, 
        traitement: assignes + evalues, 
        valides: valides_secretariat + valides_presidencesct, 
        rejetes 
      };
    },
    
    filterProjects() {
      this.filteredProjects = this.projects.filter((p) => {
        return (
          (!this.selectedSecteur || p.secteur.includes(this.selectedSecteur)) &&
          (!this.selectedStatut || p.statut === this.selectedStatut) &&
          (!this.selectedPole || p.poles.includes(this.selectedPole))
        );
      });
    },
    
    resetFilters() {
      this.selectedSecteur = "";
      this.selectedStatut = "";
      this.selectedPole = "";
      this.filteredProjects = [...this.projects];
    },
    
    formatCFA(val) {
      return val ? parseInt(val).toLocaleString("fr-FR") + " F CFA" : "—";
    },

    // ============ Métriques de performance ============
    async loadMetrics() {
      try {
        const response = await fetch('/api/metrics');
        if (response.ok) {
          const data = await response.json();
          this.metrics = {
            averageProcessingTime: data.averageProcessingTime || '0 jours',
            validationRate: data.validationRate || 0,
            averageEvaluationTime: data.averageEvaluationTime || '0 jours'
          };
        }
      } catch (error) {
        console.error('Erreur chargement métriques:', error);
      }
    },

    // ============ Téléchargement du rapport ============
    async telechargerRapport() {
      try {
        const response = await fetch('/api/stats/rapport-pdf');

        if (!response.ok) {
          throw new Error('Erreur lors de la génération du rapport');
        }

        // Récupérer le blob du PDF
        const blob = await response.blob();

        // Créer un lien de téléchargement temporaire
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `rapport_statistiques_dgppe_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(link);
        link.click();

        // Nettoyer
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Erreur téléchargement rapport:', error);
        alert('Erreur lors du téléchargement du rapport PDF');
      }
    },

    async telechargerRapportElabore() {
      try {
        const response = await fetch('/api/admin/rapport-elabore');

        if (!response.ok) {
          throw new Error('Erreur lors de la génération du rapport élaboré');
        }

        // Récupérer le blob du PDF
        const blob = await response.blob();

        // Créer un lien de téléchargement temporaire
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `rapport_elabore_dgppe_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(link);
        link.click();

        // Nettoyer
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Erreur téléchargement rapport élaboré:', error);
        alert('Erreur lors du téléchargement du rapport élaboré');
      }
    }
  },
};
</script>

<style scoped>
.admin-container {
  padding: 24px;
}

/* En-tête de page */
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-buttons {
  display: flex;
  gap: 12px;
}

.btn-download-rapport {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--dgppe-accent);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-download-rapport.elabore {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.btn-download-rapport:hover {
  background: var(--dgppe-secondary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-download-rapport.elabore:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.btn-download-rapport svg {
  width: 18px;
  height: 18px;
}

/* En-tête de page */
.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 28px;
  font-weight: 600;
  color: var(--dgppe-primary);
  margin-bottom: 24px;
  border-bottom: 2px solid var(--dgppe-accent);
  padding-bottom: 12px;
}

/* Onglets */
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 2px solid #e5e7eb;
}

.tab-btn {
  padding: 12px 24px;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  color: #6b7280;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  color: var(--dgppe-primary);
  background: rgba(46, 107, 107, 0.05);
}

.tab-btn.active {
  color: var(--dgppe-primary);
  border-bottom-color: var(--dgppe-accent);
  background: rgba(46, 107, 107, 0.1);
}

/* Section utilisateurs */
.users-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--dgppe-primary);
  margin: 0;
}

/* Grille des utilisateurs */
.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.user-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.user-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

.user-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.user-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.role-soumissionnaire { background: #3b82f6; }
.role-evaluateur { background: #f59e0b; }
.role-secretariatsct { background: var(--dgppe-primary); }
.role-presidencesct { background: var(--dgppe-secondary); }
.role-presidencecomite { background: #8b5cf6; }
.role-admin { background: #ef4444; }

.user-info {
  flex: 1;
}

.user-info h4 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.user-username {
  font-size: 13px;
  color: #6b7280;
  font-family: 'Courier New', monospace;
  margin-bottom: 6px;
}

.user-role {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-soumissionnaire { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }
.badge-evaluateur { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
.badge-secretariatsct { background: rgba(46, 107, 107, 0.1); color: var(--dgppe-primary); }
.badge-presidencesct { background: rgba(72, 181, 181, 0.1); color: var(--dgppe-secondary); }
.badge-presidencecomite { background: rgba(139, 92, 246, 0.1); color: #8b5cf6; }
.badge-admin { background: rgba(239, 68, 68, 0.1); color: #ef4444; }

.user-actions {
  display: flex;
  gap: 8px;
}

.btn-edit,
.btn-delete {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-edit {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.btn-edit:hover {
  background: #3b82f6;
  color: white;
}

.btn-delete {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.btn-delete:hover {
  background: #ef4444;
  color: white;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--dgppe-primary);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background: var(--dgppe-secondary);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(46, 107, 107, 0.3);
}

/* Cartes de statistiques */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-left: 4px solid;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.stat-card.primary { border-left-color: var(--dgppe-primary); }
.stat-card.info { border-left-color: #3b82f6; }
.stat-card.warning { border-left-color: #f59e0b; }
.stat-card.success { border-left-color: #10b981; }
.stat-card.danger { border-left-color: #ef4444; }

.stat-icon {
  font-size: 32px;
}

.stat-content {
  flex: 1;
}

.stat-label {
  display: block;
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
  margin-bottom: 4px;
}

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #111827;
}

/* Filtres */
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.filter-select {
  flex: 1;
  min-width: 200px;
  padding: 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.btn-filter,
.btn-reset {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-filter {
  background: var(--dgppe-primary);
  color: white;
}

.btn-filter:hover {
  background: var(--dgppe-secondary);
}

.btn-reset {
  background: #9e9e9e;
  color: white;
}

.btn-reset:hover {
  background: #757575;
}

/* Onglet Projets */
.projects-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e5e7eb;
}

.project-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  background: #f8fafc;
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  font-size: 14px;
}

.stat-item strong {
  color: var(--dgppe-primary);
}

.filters-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-group label {
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.btn-reset {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #9e9e9e;
  color: white;
  align-self: end;
}

.btn-reset:hover {
  background: #757575;
}

.btn-view-small, .btn-delete-small {
  padding: 6px 8px;
  margin: 0 2px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
}

.btn-view-small {
  background: #3b82f6;
  color: white;
}

.btn-view-small:hover {
  background: #2563eb;
}

.btn-delete-small {
  background: #ef4444;
  color: white;
}

.btn-delete-small:hover {
  background: #dc2626;
}

.project-number-table {
  background: var(--dgppe-primary);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 700;
  display: inline-block;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #6b7280;
}

/* Status badges */
.status-new { background: #3b82f6 !important; color: white !important; }
.status-assigned { background: #f59e0b !important; color: white !important; }
.status-pending { background: #8b5cf6 !important; color: white !important; }
.status-validated { background: #10b981 !important; color: white !important; }
.status-complement { background: #f97316 !important; color: white !important; }
.status-confirmed { background: #06b6d4 !important; color: white !important; }
.status-favorable { background: #10b981 !important; color: white !important; }
.status-defavorable { background: #ef4444 !important; color: white !important; }
.status-rejected { background: #dc2626 !important; color: white !important; }
.status-default { background: #6b7280 !important; color: white !important; }

/* Tableau des projets */
.projects-table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.projects-table {
  width: 100%;
  border-collapse: collapse;
}

.projects-table thead {
  background: var(--dgppe-primary);
  color: white;
}

.projects-table th {
  padding: 16px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.projects-table td {
  padding: 14px 16px;
  border-top: 1px solid #e5e7eb;
  font-size: 14px;
}

.projects-table tbody tr:hover {
  background: #f9fafb;
}

.project-title {
  font-weight: 600;
  color: var(--dgppe-primary);
}

.project-cost {
  font-weight: 600;
  color: #059669;
}

.badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
}

/* ==================== RECHERCHE ET FILTRES ==================== */
.search-bar {
  margin-bottom: 16px;
}

.search-input {
  width: 100%;
  padding: 14px 20px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 16px;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.search-input:focus {
  outline: none;
  border-color: var(--dgppe-primary);
  box-shadow: 0 0 0 3px rgba(0, 64, 128, 0.1);
}

.filters-compact {
  margin-bottom: 16px;
}

.btn-toggle-filters {
  padding: 10px 20px;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.btn-toggle-filters:hover {
  background: #e5e7eb;
}

/* ==================== VUE EN CARTES (MOBILE) ==================== */
.mobile-only {
  display: none;
}

.desktop-only {
  display: block;
}

.projects-cards {
  display: grid;
  gap: 16px;
}

.project-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.project-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.card-header {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.card-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.project-number {
  font-size: 14px;
  color: var(--dgppe-primary);
  font-weight: 700;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  line-height: 1.4;
}

.card-body {
  margin-bottom: 12px;
}

.card-info-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 14px;
}

.info-label {
  font-weight: 600;
  color: #6b7280;
}

.info-value {
  color: #1f2937;
  text-align: right;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.btn-view,
.btn-delete {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.btn-view {
  background: var(--dgppe-primary);
  color: white;
}

.btn-view:hover {
  background: var(--dgppe-primary-light);
}

.btn-delete {
  background: #ef4444;
  color: white;
}

.btn-delete:hover {
  background: #dc2626;
}

/* ==================== PAGINATION ==================== */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding: 16px 0;
  gap: 16px;
  flex-wrap: wrap;
}

.pagination-info {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.pagination-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-page {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.btn-page:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: var(--dgppe-primary);
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 4px;
}

.btn-page-number {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 40px;
  font-size: 14px;
}

.btn-page-number.active {
  background: var(--dgppe-primary);
  color: white;
  border-color: var(--dgppe-primary);
}

.btn-page-number:hover:not(.active) {
  background: #f3f4f6;
}

.items-per-page {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.items-per-page label {
  font-weight: 600;
  color: #374151;
}

.items-per-page select {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
  from {
    transform: translateY(-50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--dgppe-primary);
}

.btn-close {
  background: none;
  border: none;
  font-size: 32px;
  color: #6b7280;
  cursor: pointer;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.btn-close:hover {
  background: #f3f4f6;
  color: #111827;
}

.modal-body {
  padding: 24px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  font-size: 14px;
}

.form-input,
.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--dgppe-primary);
  box-shadow: 0 0 0 3px rgba(46, 107, 107, 0.1);
}

.error-message {
  background: #fee2e2;
  color: #991b1b;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  margin-top: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 24px;
  border-top: 1px solid #e5e7eb;
}

.btn-secondary {
  padding: 10px 20px;
  background: #f3f4f6;
  color: #374151;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

/* Responsive */
@media (max-width: 1024px) {
  .admin-container {
    padding: var(--dgppe-spacing-4);
  }

  .header-row {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--dgppe-spacing-4);
  }

  .header-buttons {
    width: 100%;
    flex-direction: column;
  }

  .btn-download-rapport {
    width: 100%;
    justify-content: center;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .financing-cards-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .admin-container {
    padding: var(--dgppe-spacing-3);
  }

  .page-title {
    font-size: 1.375rem;
  }

  .stats-cards {
    grid-template-columns: 1fr;
  }

  .users-grid {
    grid-template-columns: 1fr;
  }

  .filters {
    flex-direction: column;
  }

  .filter-select {
    width: 100%;
  }

  .modal-content {
    width: 95%;
    margin: 20px;
  }

  .projects-table {
    font-size: 12px;
  }

  .projects-table th,
  .projects-table td {
    padding: 8px;
  }

  .tabs {
    flex-wrap: wrap;
    gap: var(--dgppe-spacing-2);
  }

  .tab-btn {
    padding: var(--dgppe-spacing-2) var(--dgppe-spacing-3);
    font-size: 0.813rem;
    flex: 1 1 auto;
    min-width: 120px;
  }

  .performance-metrics,
  .financing-volumes,
  .users-section {
    padding: var(--dgppe-spacing-4);
  }

  .metric-value,
  .financing-amount {
    font-size: 1.5rem;
  }

  /* Responsive pour la page projets */
  .mobile-only {
    display: block !important;
  }

  .desktop-only {
    display: none !important;
  }

  .project-stats {
    flex-direction: column;
    gap: 8px;
  }

  .stat-item {
    width: 100%;
  }

  .pagination {
    flex-direction: column;
    gap: 12px;
  }

  .pagination-controls {
    order: 2;
  }

  .pagination-info {
    order: 1;
    text-align: center;
  }

  .items-per-page {
    order: 3;
    justify-content: center;
  }

  .page-numbers {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .admin-container {
    padding: var(--dgppe-spacing-2);
  }

  .page-title {
    font-size: 1.25rem;
    flex-direction: column;
    align-items: flex-start;
    gap: var(--dgppe-spacing-2);
  }

  .tab-btn {
    min-width: auto;
    font-size: 0.75rem;
    padding: var(--dgppe-spacing-2);
  }

  .performance-metrics,
  .financing-volumes,
  .users-section {
    padding: var(--dgppe-spacing-3);
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--dgppe-spacing-3);
  }

  .section-header .btn-primary {
    width: 100%;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  /* Responsive supplémentaire pour pagination */
  .btn-page,
  .btn-page-number {
    padding: 6px 10px;
    font-size: 12px;
    min-width: 32px;
  }

  .pagination-info {
    font-size: 12px;
  }

  .filters-container {
    grid-template-columns: 1fr;
    padding: 16px;
  }
}

.actions-cell {
  text-align: center;
  white-space: nowrap;
}

.actions-cell .btn-outline {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  font-size: 0.75rem;
  border: 1px solid #ddd;
  background: #f8f9fa;
  color: #333;
  border-radius: 3px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.actions-cell .btn-outline:hover {
  background: #e9ecef;
  border-color: #adb5bd;
  color: #000;
}

.actions-cell .btn-outline svg {
  width: 12px;
  height: 12px;
}

/* Métriques de performance */
.performance-metrics {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 24px;
  margin-bottom: 24px;
}

.performance-metrics h3 {
  color: var(--dgppe-primary);
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: 600;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 0;
}

.metric-card {
  background: #ffffff;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s ease;
}

.metric-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: #6c757d;
  font-size: 14px;
  font-weight: 500;
}

.metric-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--dgppe-primary);
}

/* Volumes de financement */
.financing-volumes {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 24px;
  margin-bottom: 24px;
}

.financing-volumes h3 {
  color: var(--dgppe-primary);
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 600;
}

.financing-cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.financing-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 2px solid #dee2e6;
  border-radius: 10px;
  padding: 20px;
  transition: all 0.3s ease;
}

.financing-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.financing-card.success {
  background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
  border-color: #28a745;
}

.financing-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  color: #495057;
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.financing-card.success .financing-header {
  color: #155724;
}

.financing-header svg {
  color: #6c757d;
}

.financing-card.success .financing-header svg {
  color: #28a745;
}

.financing-amount {
  font-size: 28px;
  font-weight: 700;
  color: var(--dgppe-primary);
  margin-bottom: 8px;
}

.financing-card.success .financing-amount {
  color: #28a745;
}

.financing-count {
  font-size: 14px;
  color: #6c757d;
  font-weight: 500;
}

.financing-card.success .financing-count {
  color: #155724;
}

/* Responsive financing cards */
@media (max-width: 768px) {
  .financing-cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
