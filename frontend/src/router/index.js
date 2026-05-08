import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import ForgotPassword from '../views/ForgotPassword.vue';
import ResetPassword from '../views/ResetPassword.vue';
import NotFound from '../views/NotFound.vue';
import ImportProjetHistorique from '../views/ImportProjetHistorique.vue';
import EditProjet from '../views/EditProjet.vue';
import DashboardSoumissionnaire from '../views/DashboardSoumissionnaire.vue';
import Evaluation from '../views/Evaluation.vue';
import SecretariatSCT from '../views/SecretariatSCT.vue';
import PresidenceSCT from '../views/PresidenceSCT.vue';
import PresidenceComite from '../views/PresidenceComite.vue';
import MembreComite from '../views/MembreComite.vue';
import AdminDashboard from '../views/AdminDashboard.vue';
import MinistereEconomie from '../views/MinistereEconomie.vue';

import ProjectDetail from '../views/ProjectDetail.vue';
import GestionComptes from '../views/GestionComptes.vue';
import Invite from '../views/Invite.vue';
import MinisteresEditor from '../views/MinisteresEditor.vue';
import MonProfil from '../views/MonProfil.vue';
import LogsConnexion from '../views/LogsConnexion.vue';
import ConfigEmails from '../views/ConfigEmails.vue';
import Contact from '../views/Contact.vue';
import ProjetsTutelle from '../views/ProjetsTutelle.vue';


const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/forgot-password', name: 'ForgotPassword', component: ForgotPassword },
  { path: '/reset-password', name: 'ResetPassword', component: ResetPassword },
  { path: '/contact', name: 'Contact', component: Contact },
{ path: '/mon-profil', name: 'MonProfil', component: MonProfil, meta: { requiresAuth: true } },
  { path: '/soumissionnaire', name: 'Soumissionnaire', component: DashboardSoumissionnaire, meta: { requiresAuth: true } },
  { path: '/projets-tutelle', name: 'ProjetsTutelle', component: ProjetsTutelle, meta: { requiresAuth: true } },
  { path: '/evaluateur', name: 'Evaluateur', component: Evaluation, meta: { requiresAuth: true } },
  // Redirect de l'ancienne route /evaluation/:id vers le projet (évaluation simplifiée depuis /evaluateur)
  { path: '/evaluation/:id', redirect: to => `/project/${to.params.id}` },
  // Compat: anciennes routes spécifiques aux évaluateurs
  { path: '/evaluateur1', name: 'Evaluateur1', component: Evaluation, meta: { requiresAuth: true } },
  { path: '/evaluateur2', name: 'Evaluateur2', component: Evaluation, meta: { requiresAuth: true } },
  { path: '/secretariatsct', name: 'SecretariatSCT', component: SecretariatSCT, meta: { requiresAuth: true } },
  { path: '/presidencesct', name: 'PresidenceSCT', component: PresidenceSCT, meta: { requiresAuth: true } },
  { path: '/presidencecomite', name: 'PresidenceComite', component: PresidenceComite, meta: { requiresAuth: true } },
  { path: '/membrecomite', name: 'MembreComite', component: MembreComite, meta: { requiresAuth: true } },
  { path: '/admin', name: 'Admin', component: AdminDashboard, meta: { requiresAuth: true } },
  { path: '/gestion-comptes', name: 'GestionComptes', component: GestionComptes, meta: { requiresAuth: true } },
  { path: '/ministeres-editor', name: 'MinisteresEditor', component: MinisteresEditor, meta: { requiresAuth: true } },
  { path: '/import-projet', name: 'ImportProjetHistorique', component: ImportProjetHistorique, meta: { requiresAuth: true } },
  { path: '/logs-connexion', name: 'LogsConnexion', component: LogsConnexion, meta: { requiresAuth: true } },
  { path: '/config-emails', name: 'ConfigEmails', component: ConfigEmails, meta: { requiresAuth: true } },
  { path: '/visiteur', name: 'Visiteur', component: Invite, meta: { requiresAuth: true } },
  // Compat: ancienne route /invite → /visiteur
  { path: '/invite', redirect: '/visiteur' },
  { path: '/ministre_economie', name: 'MinistereEconomie', component: MinistereEconomie, meta: { requiresAuth: true } },
  { path: '/project/:id', name: 'ProjectDetail', component: ProjectDetail, meta: { requiresAuth: true } },
  { path: '/project/:id/edit', name: 'EditProjet', component: EditProjet, meta: { requiresAuth: true } }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// Mode vitrine : pages publiques accessibles (Home, Login, Visiteur, Contact,
// Forgot password). Toute autre route (admin, secrétariat, évaluateur…) → Home.
const VITRINE_MODE = import.meta.env.VITE_VITRINE_MODE === 'true';
const VITRINE_ALLOWED = ['/', '/login', '/visiteur', '/contact', '/forgot-password', '/reset-password'];

router.beforeEach((to, from, next) => {
  if (VITRINE_MODE) {
    // /invite (legacy) → /visiteur
    if (to.path === '/invite') return next('/visiteur');
    // /project/:id autorisé en mode vitrine (consultation publique des fiches historiques)
    if (VITRINE_ALLOWED.includes(to.path) || to.path.startsWith('/project/')) {
      // Pour /visiteur, auto-login en invité si pas encore de user
      if (to.path === '/visiteur' && !localStorage.getItem('user')) {
        localStorage.setItem('user', JSON.stringify({
          id: null, username: 'invite', nom: 'Visiteur',
          role: 'invite', display_name: 'Visiteur', email: null, telephone: null,
        }));
      }
      return next();
    }
    // Toute autre route (interne) → Home
    return next('/');
  }
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  const normalizeRole = (r) => {
    if (!r) return r;
    // Normalise les anciens rôles evaluateur1/evaluateur2 -> evaluateur
    if (typeof r === 'string' && r.toLowerCase().startsWith('evaluateur')) return 'evaluateur';
    return r;
  };

  // Définir les routes accessibles par rôle
  const roleAccessMap = {
    'admin': ['admin', 'gestion-comptes', 'ministeres-editor', 'logs-connexion', 'config-emails', 'import-projet', 'mon-profil', 'project', 'evaluation'],
    'soumissionnaire': ['soumissionnaire', 'projets-tutelle', 'mon-profil', 'project'],
    'evaluateur': ['evaluateur', 'evaluateur1', 'evaluateur2', 'mon-profil', 'project', 'evaluation'],
    'secretariatsct': ['secretariatsct', 'gestion-comptes', 'ministeres-editor', 'import-projet', 'mon-profil', 'project', 'evaluation'],
    'presidencesct': ['presidencesct', 'mon-profil', 'project', 'evaluation'],
    'presidencecomite': ['presidencecomite', 'mon-profil', 'project', 'evaluation'],
    'membrecomite': ['membrecomite', 'mon-profil', 'project'],
    'ministre_economie': ['ministre_economie', 'mon-profil', 'project'],
    'invite': ['visiteur', 'mon-profil', 'project']
  };

  // Mapping rôle → home path (pour redirection après login)
  const roleHomePath = (r) => r === 'invite' ? '/visiteur' : `/${r}`;

  // Vérifier si l'utilisateur peut accéder à la route
  const canAccessRoute = (userRole, path) => {
    if (!userRole || !roleAccessMap[userRole]) return false;
    const allowedRoutes = roleAccessMap[userRole];

    // Vérifier si le chemin commence par une des routes autorisées
    return allowedRoutes.some(route => {
      if (route === 'project') return path.startsWith('/project/');
      if (route === 'evaluation') return path.startsWith('/evaluation/');
      return path.startsWith(`/${route}`);
    });
  };

  if (to.meta.requiresAuth && !user) {
    next('/login');
  } else if (to.path === '/login' && user) {
    const role = normalizeRole(user.role);
    next(roleHomePath(role));
  } else if (user && to.meta.requiresAuth && to.path !== '/mon-profil') {
    // Vérifier l'accès basé sur le rôle pour toutes les routes protégées (sauf mon-profil accessible à tous)
    const userRole = normalizeRole(user.role);

    if (!canAccessRoute(userRole, to.path)) {
      console.warn(`[Router] Accès refusé: L'utilisateur avec le rôle "${userRole}" ne peut pas accéder à "${to.path}"`);
      next(roleHomePath(userRole));
      return;
    }
    next();
  } else {
    next();
  }
});

// Route catch-all pour les pages introuvables
router.addRoute({ path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound });

export default router;