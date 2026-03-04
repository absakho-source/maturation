<template>
  <PageWrapper>
    <div class="test-formulaires">
      <h2 class="page-title">Revue des Formulaires — Atelier Jour 3</h2>
      <p class="intro">Chaque lien s'ouvre dans un nouvel onglet pour faciliter la discussion.</p>

      <section v-for="cat in categories" :key="cat.id" class="form-section">
        <h3 :class="['section-title', cat.id]">{{ cat.label }}</h3>
        <div class="cards-grid">
          <a v-for="form in formsByCategory(cat.id)" :key="form.id"
             :href="'/test-formulaires/' + form.id" target="_blank" rel="noopener"
             class="form-card">
            <span class="form-number" :class="cat.id">{{ form.number }}</span>
            <div class="card-body">
              <h4>{{ form.title }}</h4>
              <p>{{ form.desc }}</p>
            </div>
            <span :class="['role-badge', cat.id]">{{ form.role }}</span>
          </a>
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
      categories: [
        { id: 'public', label: 'Formulaires publics' },
        { id: 'soumissionnaire', label: 'Formulaires Soumissionnaire' },
        { id: 'evaluateur', label: 'Formulaires Evaluateur' },
        { id: 'admin', label: 'Formulaires Administration' }
      ],
      forms: [
        { id: 'login', number: 1, title: 'Connexion', desc: 'Selection de compte et mot de passe', role: 'Public', category: 'public' },
        { id: 'register', number: 2, title: 'Inscription', desc: 'Compte soumissionnaire, structure hierarchique, justificatifs', role: 'Public', category: 'public' },
        { id: 'contact', number: 3, title: 'Contact', desc: 'Objet, message, pieces jointes, captcha', role: 'Public', category: 'public' },
        { id: 'profil', number: 4, title: 'Mon Profil', desc: 'Email, telephone, fonction, changement mot de passe', role: 'Tous', category: 'soumissionnaire' },
        { id: 'soumission', number: 5, title: 'Soumission de projet', desc: 'Titre, tutelle, point focal, poles, secteur, couts, documents', role: 'Soumissionnaire', category: 'soumissionnaire' },
        { id: 'discussion', number: 6, title: 'Discussion projet', desc: 'Messagerie avec pieces jointes', role: 'Soumissionnaire / Evaluateur', category: 'soumissionnaire' },
        { id: 'matrice', number: 7, title: 'Matrice de recevabilite', desc: 'Documents requis/transmis, commentaires, 3 decisions', role: 'Evaluateur', category: 'evaluateur' },
        { id: 'fiche-eval', number: 8, title: "Fiche d'evaluation", desc: '12 criteres /100, classification, dimensions transversales, conclusion', role: 'Evaluateur', category: 'evaluateur' },
        { id: 'gestion-comptes', number: 9, title: 'Gestion des comptes', desc: 'Verification, suspension, creation utilisateurs', role: 'Admin / SCT', category: 'admin' },
        { id: 'config-emails', number: 10, title: 'Configuration emails', desc: 'SMTP, templates, activation/desactivation', role: 'Admin', category: 'admin' },
        { id: 'ministeres', number: 11, title: 'Gestion des ministeres', desc: 'Ajout, modification, ordre, activation', role: 'Admin / SCT', category: 'admin' },
        { id: 'formulaire-editor', number: 12, title: "Configuration formulaire d'evaluation", desc: 'Criteres, scores max, seuil minimum', role: 'Admin / SCT', category: 'admin' }
      ]
    };
  },
  methods: {
    formsByCategory(catId) {
      return this.forms.filter(f => f.category === catId);
    }
  }
};
</script>

<style scoped>
.test-formulaires {
  max-width: 1000px;
  margin: 0 auto;
  padding: 1.5rem;
}
.page-title {
  font-size: 1.3rem;
  color: #003366;
  margin: 0 0 0.25rem;
}
.intro {
  color: #6c757d;
  font-size: 0.85rem;
  margin-bottom: 1.5rem;
}
.form-section { margin-bottom: 1.5rem; }
.section-title {
  font-size: 1rem;
  padding: 0.45rem 0.9rem;
  border-radius: 6px;
  margin-bottom: 0.75rem;
  color: white;
}
.section-title.public { background: #17a2b8; }
.section-title.soumissionnaire { background: #006633; }
.section-title.evaluateur { background: #e67e00; }
.section-title.admin { background: #003366; }

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.75rem;
}
.form-card {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  padding: 0.85rem 1rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  position: relative;
  transition: box-shadow 0.2s, border-color 0.2s;
}
.form-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-color: #003366;
}
.form-number {
  width: 28px; height: 28px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.8rem; flex-shrink: 0;
  color: white;
}
.form-number.public { background: #17a2b8; }
.form-number.soumissionnaire { background: #006633; }
.form-number.evaluateur { background: #e67e00; }
.form-number.admin { background: #003366; }

.card-body { flex: 1; min-width: 0; }
.card-body h4 { margin: 0 0 0.2rem; font-size: 0.9rem; color: #1a1a1a; }
.card-body p { margin: 0; font-size: 0.75rem; color: #6c757d; line-height: 1.4; }

.role-badge {
  position: absolute;
  top: 0.4rem; right: 0.5rem;
  font-size: 0.6rem;
  padding: 0.1rem 0.45rem;
  border-radius: 10px;
  font-weight: 600;
  text-transform: uppercase;
}
.role-badge.public { background: #d1ecf1; color: #0c5460; }
.role-badge.soumissionnaire { background: #d4edda; color: #155724; }
.role-badge.evaluateur { background: #fff3cd; color: #856404; }
.role-badge.admin { background: #cce5ff; color: #004085; }

@media (max-width: 768px) {
  .cards-grid { grid-template-columns: 1fr; }
}
</style>
