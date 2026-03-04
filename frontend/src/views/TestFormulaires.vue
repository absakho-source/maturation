<template>
  <PageWrapper>
    <div class="test-formulaires">
      <div class="header-row">
        <h2 class="page-title">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 11l3 3L22 4" /><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
          </svg>
          Test des Formulaires — Atelier Jour 3
        </h2>
        <div class="header-buttons">
          <span class="user-badge" v-if="currentUser">
            Connecte : <strong>{{ currentUser.display_name || currentUser.username }}</strong> ({{ currentUser.role }})
          </span>
          <span class="user-badge disconnected" v-else>Non connecte</span>
          <button class="btn-reconnect" @click="goLogin">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/>
            </svg>
            Changer de role
          </button>
        </div>
      </div>

      <p class="intro">
        Cliquez sur un formulaire pour y acceder directement. Certains formulaires necessitent d'etre connecte avec un role specifique — utilisez "Changer de role" pour vous reconnecter.
      </p>

      <!-- FORMULAIRES PUBLICS -->
      <section class="form-section">
        <h3 class="section-title public">Formulaires publics</h3>
        <div class="cards-grid">
          <div class="form-card" @click="navigate('/login')">
            <div class="card-icon">🔑</div>
            <div class="card-body">
              <h4>Connexion</h4>
              <p>Authentification avec selection de compte et mot de passe</p>
            </div>
            <span class="role-badge public">Public</span>
          </div>

          <div class="form-card" @click="navigate('/register')">
            <div class="card-icon">📝</div>
            <div class="card-body">
              <h4>Inscription</h4>
              <p>Creation de compte soumissionnaire avec structure hierarchique et justificatifs</p>
            </div>
            <span class="role-badge public">Public</span>
          </div>

          <div class="form-card" @click="navigate('/contact')">
            <div class="card-icon">✉️</div>
            <div class="card-body">
              <h4>Contact</h4>
              <p>Formulaire de contact avec objet, message, pieces jointes et captcha</p>
            </div>
            <span class="role-badge public">Public</span>
          </div>
        </div>
      </section>

      <!-- FORMULAIRES SOUMISSIONNAIRE -->
      <section class="form-section">
        <h3 class="section-title soumissionnaire">Formulaires Soumissionnaire</h3>
        <div class="cards-grid">
          <div class="form-card" :class="{ disabled: !hasRole('soumissionnaire') }" @click="navigate('/mon-profil')">
            <div class="card-icon">👤</div>
            <div class="card-body">
              <h4>Mon Profil</h4>
              <p>Modification email, telephone, fonction et changement de mot de passe</p>
            </div>
            <span class="role-badge all">Tous les roles</span>
          </div>

          <div class="form-card" :class="{ disabled: !hasRole('soumissionnaire') }" @click="navigate('/soumissionnaire')">
            <div class="card-icon">📋</div>
            <div class="card-body">
              <h4>Soumission de projet</h4>
              <p>Formulaire complet : titre, structure, organisme de tutelle, secteur, pole, documents</p>
            </div>
            <span class="role-badge soumissionnaire">soumissionnaire</span>
          </div>

          <div class="form-card" :class="{ disabled: !hasRole('soumissionnaire') }" @click="navigate('/soumissionnaire')">
            <div class="card-icon">💬</div>
            <div class="card-body">
              <h4>Discussion projet</h4>
              <p>Messagerie avec pieces jointes (accessible quand des complements sont demandes)</p>
            </div>
            <span class="role-badge soumissionnaire">soumissionnaire</span>
          </div>
        </div>
      </section>

      <!-- FORMULAIRES EVALUATEUR -->
      <section class="form-section">
        <h3 class="section-title evaluateur">Formulaires Evaluateur</h3>
        <div class="cards-grid">
          <div class="form-card" :class="{ disabled: !hasRole('evaluateur') }" @click="navigate('/evaluateur')">
            <div class="card-icon">✅</div>
            <div class="card-body">
              <h4>Matrice de recevabilite</h4>
              <p>Verification des documents : requis/transmis, commentaires, 3 decisions possibles</p>
            </div>
            <span class="role-badge evaluateur">evaluateur</span>
          </div>

          <div class="form-card" :class="{ disabled: !hasRole('evaluateur') }" @click="navigate('/evaluateur')">
            <div class="card-icon">📊</div>
            <div class="card-body">
              <h4>Fiche d'evaluation</h4>
              <p>Notation par criteres avec curseurs (0-5, 0-10), sous-totaux et total automatiques</p>
            </div>
            <span class="role-badge evaluateur">evaluateur</span>
          </div>

          <div class="form-card" :class="{ disabled: !hasRole('evaluateur') }" @click="navigate('/evaluateur')">
            <div class="card-icon">📄</div>
            <div class="card-body">
              <h4>Fiche DGPPE</h4>
              <p>Cout, origine, dimensions transversales, articulation, axes strategiques, ODD</p>
            </div>
            <span class="role-badge evaluateur">evaluateur</span>
          </div>

          <div class="form-card" :class="{ disabled: !hasRole('evaluateur') }" @click="navigate('/evaluateur')">
            <div class="card-icon">🔍</div>
            <div class="card-body">
              <h4>Evaluation detaillee</h4>
              <p>Vue complete : presentation projet, classification, notation detaillee</p>
            </div>
            <span class="role-badge evaluateur">evaluateur</span>
          </div>
        </div>
      </section>

      <!-- FORMULAIRES ADMINISTRATION -->
      <section class="form-section">
        <h3 class="section-title admin">Formulaires Administration</h3>
        <div class="cards-grid">
          <div class="form-card" :class="{ disabled: !hasRole('admin', 'secretariatsct') }" @click="navigate('/gestion-comptes')">
            <div class="card-icon">👥</div>
            <div class="card-body">
              <h4>Gestion des comptes</h4>
              <p>Verification, suspension, creation d'utilisateurs internes, modification structure</p>
            </div>
            <span class="role-badge admin">admin / secretariatsct</span>
          </div>

          <div class="form-card" :class="{ disabled: !hasRole('admin') }" @click="navigate('/config-emails')">
            <div class="card-icon">📧</div>
            <div class="card-body">
              <h4>Configuration emails</h4>
              <p>Activation/desactivation des notifications automatiques par email</p>
            </div>
            <span class="role-badge admin">admin</span>
          </div>

          <div class="form-card" :class="{ disabled: !hasRole('admin', 'secretariatsct') }" @click="navigate('/ministeres-editor')">
            <div class="card-icon">🏛️</div>
            <div class="card-body">
              <h4>Gestion des ministeres</h4>
              <p>Ajout, modification, reordonnancement et activation/desactivation des ministeres</p>
            </div>
            <span class="role-badge admin">admin / secretariatsct</span>
          </div>

          <div class="form-card" :class="{ disabled: !hasRole('admin', 'secretariatsct') }" @click="navigate('/formulaire-editor')">
            <div class="card-icon">⚙️</div>
            <div class="card-body">
              <h4>Configuration formulaire d'evaluation</h4>
              <p>Criteres, scores max, seuil minimum, version d'affichage</p>
            </div>
            <span class="role-badge admin">admin / secretariatsct</span>
          </div>
        </div>
      </section>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';

export default {
  name: 'TestFormulaires',
  components: { PageWrapper },
  data() {
    return {
      currentUser: null
    };
  },
  created() {
    this.currentUser = JSON.parse(localStorage.getItem('user') || 'null');
  },
  methods: {
    hasRole(...roles) {
      if (!this.currentUser) return false;
      return roles.includes(this.currentUser.role);
    },
    navigate(path) {
      this.$router.push(path);
    },
    goLogin() {
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
.test-formulaires {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.5rem;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.4rem;
  color: #003366;
  margin: 0;
}

.header-buttons {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-badge {
  font-size: 0.85rem;
  color: #495057;
  background: #e9ecef;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
}

.user-badge.disconnected {
  color: #856404;
  background: #fff3cd;
}

.btn-reconnect {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 1rem;
  background: #003366;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.2s;
}

.btn-reconnect:hover {
  background: #004080;
}

.intro {
  color: #6c757d;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.form-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.1rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  color: white;
}

.section-title.public { background: #17a2b8; }
.section-title.soumissionnaire { background: #006633; }
.section-title.evaluateur { background: #e67e00; }
.section-title.admin { background: #003366; }

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.form-card {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: box-shadow 0.2s, border-color 0.2s;
  position: relative;
}

.form-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-color: #003366;
}

.form-card.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-card.disabled:hover {
  box-shadow: none;
  border-color: #e2e8f0;
}

.card-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  width: 2.5rem;
  text-align: center;
}

.card-body {
  flex: 1;
  min-width: 0;
}

.card-body h4 {
  margin: 0 0 0.25rem;
  font-size: 0.95rem;
  color: #1a1a1a;
}

.card-body p {
  margin: 0;
  font-size: 0.8rem;
  color: #6c757d;
  line-height: 1.4;
}

.role-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  font-size: 0.65rem;
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.role-badge.public { background: #d1ecf1; color: #0c5460; }
.role-badge.all { background: #d4edda; color: #155724; }
.role-badge.soumissionnaire { background: #d4edda; color: #155724; }
.role-badge.evaluateur { background: #fff3cd; color: #856404; }
.role-badge.admin { background: #cce5ff; color: #004085; }

@media (max-width: 768px) {
  .header-row {
    flex-direction: column;
    align-items: flex-start;
  }
  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
