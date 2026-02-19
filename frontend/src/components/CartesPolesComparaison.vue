<template>
  <div class="cartes-poles-comparaison">
    <div class="titre-section">
      <h3 class="titre-comparaison">Répartition Géographique des Projets Entérinés</h3>
      <p class="sous-titre">Projets ayant reçu l'aval définitif du Comité de Maturation (avis favorable ou favorable sous conditions)</p>
    </div>

    <div class="carte-unique-wrapper">
      <CartePolesTerritoriaux
        status-filter="enterine"
        title="Projets entérinés par le Comité de Maturation"
      />
    </div>
  </div>
</template>

<script>
import CartePolesTerritoriaux from './CartePolesTerritoriaux.vue'

export default {
  name: 'CartesPolesComparaison',
  components: {
    CartePolesTerritoriaux
  }
}
</script>

<style scoped>
.cartes-poles-comparaison {
  max-width: 100%;
  margin: 0 auto;
  padding: 20px;
}

.titre-section {
  text-align: center;
  margin-bottom: 30px;
}

.titre-comparaison {
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 1.8em;
  font-weight: 600;
}

.sous-titre {
  color: #6c757d;
  font-size: 0.95em;
  margin: 0;
}

.carte-unique-wrapper {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  border: 2px solid #e2e8f0;
}
</style>
