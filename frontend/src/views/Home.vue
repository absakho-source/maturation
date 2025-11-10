<template>
  <div class="home-page">
    <!-- En-tête public -->
    <header class="public-header">
      <div class="header-container">
        <div class="header-spacer"></div>
        <div class="header-center">
          <div class="header-info">
            <h2 class="header-title">Ministère de l'Économie, du Plan et de la Coopération</h2>
            <p class="header-subtitle">Direction Générale de la Planification des Politiques Économiques</p>
          </div>
        </div>
        <div class="header-right">
          <button @click="$router.push('/login')" class="btn btn-outline">Connexion</button>
        </div>
      </div>
    </header>

    <main class="home-main">
      <!-- Hero Section sobre -->
      <div class="hero-section">
        <div class="container">
          <div class="hero-content">
            <!-- Logo DGPPE officiel -->
            <div class="hero-logo">
              <img :src="logoUrl" alt="Logo DGPPE" class="logo-main" />
            </div>
            
            <div class="hero-text">
              <h1 class="hero-title">Plateforme de Maturation des Projets Publics</h1>
              <p class="hero-subtitle">
                Solution numérique pour la préparation et les études des projets d'investissement publics
              </p>
            </div>
            
            <div class="hero-actions">
              <button @click="$router.push('/login')" class="btn btn-primary btn-lg">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4m-5-4l5-5-5-5m5 5H3"/>
                </svg>
                Accéder à la plateforme
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Section fonctionnalités -->
      <div class="features-section">
        <div class="container">
          <div class="section-header">
            <h2>Fonctionnalités principales</h2>
            <p>Une approche structurée pour la maturation des projets publics</p>
          </div>
          
          <div class="features-grid">
            <div class="feature-card card">
              <div class="card-body">
                <div class="feature-icon">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                    <polyline points="14,2 14,8 20,8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                  </svg>
                </div>
                <h3>Soumission de projets</h3>
                <p>Interface simplifiée pour soumettre vos projets avec tous les documents requis.</p>
              </div>
            </div>
            
            <div class="feature-card card">
              <div class="card-body">
                <div class="feature-icon">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M9 12l2 2 4-4"/>
                    <circle cx="12" cy="12" r="10"/>
                  </svg>
                </div>
                <h3>Évaluation structurée</h3>
                <p>Processus d'évaluation multi-niveaux avec traçabilité complète.</p>
              </div>
            </div>
            
            <div class="feature-card card">
              <div class="card-body">
                <div class="feature-icon">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M3 3v5h5"/>
                    <path d="M3 8s2-4 8-4 8 4 8 4"/>
                    <path d="M21 21v-5h-5"/>
                    <path d="M21 16s-2 4-8 4-8-4-8-4"/>
                  </svg>
                </div>
                <h3>Suivi et reporting</h3>
                <p>Tableaux de bord pour le suivi en temps réel de l'avancement des projets.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      

    </main>

    <footer class="public-footer">
      <div class="footer-container">
        <div class="footer-simple">
          <p>&copy; {{ currentYear }} Direction Générale de la Planification des Politiques Économiques (DGPPE)</p>
          <p>Plateforme de maturation • Version 1.0 • Développée par <a href="https://www.linkedin.com/in/dr-aboubekrine-sakho-4851981b0/" target="_blank" rel="noopener noreferrer" class="footer-link">Abou Sakho</a></p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import logoUrl from '../assets/logo-dgppe.png'

export default {
  name: "Home",
  data() {
    return {
      logoUrl
    }
  },
  computed: {
    currentYear() {
      return new Date().getFullYear();
    }
  }
};
</script>

<style scoped>
.home-page {
  background: var(--dgppe-gray-50);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--dgppe-spacing-6);
}

/* ==================== HERO SECTION SOBRE ==================== */
.hero-section {
  background: var(--dgppe-white);
  padding: var(--dgppe-spacing-6) 0 var(--dgppe-spacing-8) 0;
  border-bottom: 1px solid var(--dgppe-gray-200);
}

.hero-content {
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
}

.hero-logo {
  margin-bottom: var(--dgppe-spacing-8);
}

.logo-main {
  height: 100px;
  width: auto;
}

.hero-text {
  margin-bottom: var(--dgppe-spacing-8);
}

.hero-title {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--dgppe-text);
  margin-bottom: var(--dgppe-spacing-4);
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1.125rem;
  color: var(--dgppe-text-light);
  line-height: 1.6;
  margin: 0;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: var(--dgppe-spacing-4);
}

/* ==================== FEATURES SECTION ==================== */
.features-section {
  padding: var(--dgppe-spacing-6) 0;
  background: var(--dgppe-white);
}

.section-header {
  text-align: center;
  margin-bottom: var(--dgppe-spacing-8);
}

.section-header h2 {
  font-size: 2rem;
  font-weight: 600;
  color: var(--dgppe-text);
  margin-bottom: var(--dgppe-spacing-4);
}

.section-header p {
  font-size: 1rem;
  color: var(--dgppe-text-light);
  margin: 0;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--dgppe-spacing-6);
}

.feature-card {
  transition: transform 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-2px);
}

.feature-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: rgba(46, 107, 107, 0.1);
  border-radius: var(--dgppe-radius-lg);
  color: var(--dgppe-primary);
  margin-bottom: var(--dgppe-spacing-4);
}

.feature-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--dgppe-text);
  margin-bottom: var(--dgppe-spacing-3);
}

.feature-card p {
  color: var(--dgppe-text-light);
  line-height: 1.6;
  margin: 0;
}

/* ==================== INFO SECTION ==================== */
.info-section {
  padding: var(--dgppe-spacing-10) 0;
  background: var(--dgppe-gray-50);
}

.info-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--dgppe-spacing-8);
  align-items: center;
}

.info-text h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--dgppe-text);
  margin-bottom: var(--dgppe-spacing-4);
}

.info-text p {
  color: var(--dgppe-text-light);
  line-height: 1.6;
  margin: 0;
}

.info-stats {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--dgppe-spacing-6);
}

.stat-item {
  text-align: center;
  padding: var(--dgppe-spacing-4);
  background: var(--dgppe-white);
  border-radius: var(--dgppe-radius-lg);
  box-shadow: var(--dgppe-shadow-sm);
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: var(--dgppe-primary);
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--dgppe-text-light);
  margin-top: var(--dgppe-spacing-1);
}

/* ==================== RESPONSIVE ==================== */
@media (max-width: 768px) {
  .container {
    padding: 0 var(--dgppe-spacing-4);
  }
  
  .hero-section,
  .features-section,
  .info-section {
    padding: var(--dgppe-spacing-8) 0;
  }
  
  .hero-title {
    font-size: 1.875rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .hero-actions .btn {
    width: 100%;
    max-width: 300px;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .info-content {
    grid-template-columns: 1fr;
    text-align: center;
  }
  
  .logo-main {
    height: 80px;
  }
  
  .section-header h2 {
    font-size: 1.75rem;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 1.5rem;
  }
  
  .logo-main {
    height: 60px;
  }
  
  .stat-number {
    font-size: 1.5rem;
  }
}

/* ==================== EN-TÊTE PUBLIC ==================== */
.public-header {
  background: var(--dgppe-white);
  border-bottom: 1px solid var(--dgppe-gray-200);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: var(--dgppe-spacing-4) 0;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--dgppe-spacing-6);
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: var(--dgppe-spacing-4);
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

.header-left {
  display: flex;
  align-items: center;
  gap: var(--dgppe-spacing-3);
}

.header-logo {
  height: 50px;
  width: auto;
  transition: opacity 0.2s ease;
}

.header-logo:hover {
  opacity: 0.8;
}

.header-info {
  text-align: center;
}

.header-info h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--dgppe-primary);
  margin: 0;
  line-height: 1.2;
}

.header-info p {
  font-size: 0.875rem;
  color: var(--dgppe-text-muted);
  margin: 0;
  line-height: 1.2;
}

.header-right .btn {
  padding: var(--dgppe-spacing-2) var(--dgppe-spacing-4);
  font-size: 0.875rem;
}

/* ==================== PIED DE PAGE PUBLIC ==================== */
.public-footer {
  background: linear-gradient(135deg, var(--dgppe-primary) 0%, #1e40af 100%);
  color: white;
  padding: var(--dgppe-spacing-4) 0;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--dgppe-spacing-6);
}

.footer-simple {
  text-align: center;
}

.footer-simple p:first-child {
  font-size: 0.875rem;
  font-weight: 500;
  margin: 0 0 var(--dgppe-spacing-1) 0;
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
  transition: opacity 0.2s ease;
}

.footer-link:hover {
  opacity: 0.8;
}

@media (max-width: 768px) {
  .header-container {
    grid-template-columns: 1fr;
    text-align: center;
    gap: var(--dgppe-spacing-3);
  }
  
  .header-spacer {
    display: none;
  }
  
  .header-center {
    order: 1;
  }
  
  .header-right {
    order: 2;
    justify-content: center;
  }
  
  .header-info {
    text-align: center;
  }
}
</style>