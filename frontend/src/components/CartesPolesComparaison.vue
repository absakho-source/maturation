<template>
  <div class="cartes-poles-comparaison">
    <div class="titre-section">
      <h3 class="titre-comparaison">Répartition Géographique des Projets</h3>
      <div class="filtre-carte">
        <label>Afficher :</label>
        <select v-model="filtre">
          <option value="all">Tous les projets soumis</option>
          <option value="favorable">Avis favorable</option>
          <option value="enterine">Entérinés par le Comité</option>
        </select>
      </div>
    </div>

    <div class="carte-unique-wrapper">
      <CartePolesTerritoriaux
        :status-filter="filtre"
        :title="titresCarte[filtre]"
        :key="filtre"
      />
    </div>
  </div>
</template>

<script>
import CartePolesTerritoriaux from './CartePolesTerritoriaux.vue'

export default {
  name: 'CartesPolesComparaison',
  components: { CartePolesTerritoriaux },
  data() {
    return {
      filtre: 'all',
      titresCarte: {
        'all': 'Tous les projets soumis',
        'favorable': 'Projets avec avis favorable',
        'enterine': 'Projets entérinés par le Comité',
      }
    }
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

.filtre-carte {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.75rem;
}
.filtre-carte label { font-weight: 500; color: #475569; font-size: 0.9rem; }
.filtre-carte select {
  padding: 0.4rem 0.75rem;
  border: 2px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.9rem;
}
.filtre-carte select:focus { outline: none; border-color: #2E6B6B; }

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
