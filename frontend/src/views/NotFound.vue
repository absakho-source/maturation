<template>
  <div class="notfound-page">
    <div class="notfound-card">
      <div class="code">404</div>
      <h2>Page introuvable</h2>
      <p>La page que vous cherchez n'existe pas ou a été déplacée.</p>
      <div class="actions">
        <button @click="$router.back()" class="btn-secondary">← Retour</button>
        <router-link to="/" class="btn-primary">Aller à l'accueil</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default { name: 'NotFound' }
</script>

<style scoped>
.notfound-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  padding: 2rem 1rem;
}
.notfound-card {
  background: #fff;
  max-width: 480px;
  width: 100%;
  padding: 2.5rem 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border: 1px solid #e2e8f0;
  text-align: center;
}
.code {
  font-size: 4rem;
  font-weight: 700;
  color: #2e6b6b;
  line-height: 1;
  margin-bottom: 0.5rem;
}
h2 { color: #1e293b; margin: 0 0 0.75rem 0; }
p { color: #64748b; margin-bottom: 1.5rem; }
.actions { display: flex; gap: 0.75rem; justify-content: center; flex-wrap: wrap; }
.btn-primary, .btn-secondary {
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  border: none;
  text-decoration: none;
  display: inline-block;
}
.btn-primary { background: #2e6b6b; color: #fff; }
.btn-primary:hover { background: #1e4b4b; }
.btn-secondary { background: #e2e8f0; color: #1e293b; }
.btn-secondary:hover { background: #cbd5e1; }
</style>
