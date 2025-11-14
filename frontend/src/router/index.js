import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import DashboardSoumissionnaire from '../views/DashboardSoumissionnaire.vue';
import Evaluation from '../views/Evaluation.vue';
import EvaluationDetaillee from '../views/EvaluationDetaillee.vue';
import SecretariatSCT from '../views/SecretariatSCT.vue';
import PresidenceSCT from '../views/PresidenceSCT.vue';
import PresidenceComite from '../views/PresidenceComite.vue';
import AdminDashboard from '../views/AdminDashboard.vue';
import ProjectDetail from '../views/ProjectDetail.vue';
import GestionComptes from '../views/GestionComptes.vue';
import Invite from '../views/Invite.vue';
import FormulaireEditor from '../views/FormulaireEditor.vue';
import MinisteresEditor from '../views/MinisteresEditor.vue';
import MonProfil from '../views/MonProfil.vue';
import EditionFichePopup from '../views/EditionFichePopup.vue';
import LogsConnexion from '../views/LogsConnexion.vue';

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/mon-profil', name: 'MonProfil', component: MonProfil, meta: { requiresAuth: true } },
  { path: '/soumissionnaire', name: 'Soumissionnaire', component: DashboardSoumissionnaire, meta: { requiresAuth: true } },
  { path: '/evaluateur', name: 'Evaluateur', component: Evaluation, meta: { requiresAuth: true } },
  { path: '/evaluation/:id', name: 'EvaluationDetaillee', component: EvaluationDetaillee },
  // Compat: anciennes routes spécifiques aux évaluateurs
  { path: '/evaluateur1', name: 'Evaluateur1', component: Evaluation, meta: { requiresAuth: true } },
  { path: '/evaluateur2', name: 'Evaluateur2', component: Evaluation, meta: { requiresAuth: true } },
  { path: '/secretariatsct', name: 'SecretariatSCT', component: SecretariatSCT, meta: { requiresAuth: true } },
  { path: '/presidencesct', name: 'PresidenceSCT', component: PresidenceSCT, meta: { requiresAuth: true } },
  { path: '/presidencecomite', name: 'PresidenceComite', component: PresidenceComite, meta: { requiresAuth: true } },
  { path: '/admin', name: 'Admin', component: AdminDashboard, meta: { requiresAuth: true } },
  { path: '/gestion-comptes', name: 'GestionComptes', component: GestionComptes, meta: { requiresAuth: true } },
  { path: '/formulaire-editor', name: 'FormulaireEditor', component: FormulaireEditor, meta: { requiresAuth: true } },
  { path: '/ministeres-editor', name: 'MinisteresEditor', component: MinisteresEditor, meta: { requiresAuth: true } },
  { path: '/logs-connexion', name: 'LogsConnexion', component: LogsConnexion, meta: { requiresAuth: true } },
  { path: '/invite', name: 'Invite', component: Invite, meta: { requiresAuth: true } },
  { path: '/project/:id', name: 'ProjectDetail', component: ProjectDetail, meta: { requiresAuth: true } },
  { path: '/edition-fiche-popup', name: 'EditionFichePopup', component: EditionFichePopup, meta: { requiresAuth: false } }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  const normalizeRole = (r) => {
    if (!r) return r;
    // Normalise les anciens rôles evaluateur1/evaluateur2 -> evaluateur
    if (typeof r === 'string' && r.toLowerCase().startsWith('evaluateur')) return 'evaluateur';
    return r;
  };

  if (to.meta.requiresAuth && !user) {
    next('/login');
  } else if (to.path === '/login' && user) {
    const role = normalizeRole(user.role);
    next(`/${role}`);
  } else {
    next();
  }
});

// Redirige toute route inconnue vers /login (évite page blanche)
router.addRoute({ path: '/:pathMatch(.*)*', redirect: '/login' });

export default router;