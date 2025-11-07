<!-- filepath: /Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/frontend/src/components/Footer.vue -->
<template>
  <footer class="app-footer">
    <div class="footer-content">
      <div class="footer-simple">
        <p>&copy; {{ currentYear }} Direction Générale de la Planification des Politiques Économiques (DGPPE)</p>
        <p>Plateforme de maturation • Version 1.0 • Développée par Abou Sakho</p>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: "Footer",
  computed: {
    currentYear() {
      return new Date().getFullYear();
    }
  }
};
</script>

<style scoped>
.app-footer {
  background: linear-gradient(135deg, var(--dgppe-primary) 0%, #1e40af 100%);
  color: white;
  padding: var(--dgppe-spacing-6) 0;
  margin-top: auto;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
}

.footer-content {
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
  margin: 0 0 var(--dgppe-spacing-2) 0;
  color: white;
}

.footer-simple p:last-child {
  font-size: 0.75rem;
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
}

@media (max-width: 768px) {
  .footer-content {
    text-align: center;
  }
}
</style>