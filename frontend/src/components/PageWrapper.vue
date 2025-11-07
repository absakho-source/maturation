<template>
  <div class="page-wrapper">
    <Header />
    <main class="page-main">
      <slot />
    </main>
    <Footer />
  </div>
</template>

<script>
import Header from './Header.vue';
import Footer from './Footer.vue';
export default {
  name: 'PageWrapper',
  components: { Header, Footer }
}
</script>

<style scoped>
.page-main { 
  min-height: 60vh; 
  background: #f5f7fa; 
  padding: 1.5rem; 
}
</style>