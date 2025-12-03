<template>
  <div class="cartes-poles-comparaison">
    <h3 class="titre-comparaison">Répartition des Projets par Pôles Territoriaux</h3>

    <div class="cartes-grid">
      <!-- Carte des projets soumis -->
      <div class="carte-wrapper">
        <CartePolesTerritoriaux
          status-filter="all"
          title="Tous les projets soumis"
        />
      </div>

      <!-- Carte des projets avec avis favorable -->
      <div class="carte-wrapper">
        <CartePolesTerritoriaux
          status-filter="favorable_avis"
          title="Projets avec avis favorable (v2.0 - Filtré par avis)"
        />
      </div>
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

.titre-comparaison {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 1.8em;
  font-weight: 600;
}

.cartes-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30px;
  margin-bottom: 20px;
}

.carte-wrapper {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  border: 2px solid #e2e8f0;
}

/* Responsive : passer en colonne sur petits écrans */
@media (max-width: 1400px) {
  .cartes-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}
</style>
