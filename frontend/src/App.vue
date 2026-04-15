<!-- filepath: /Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/frontend/src/App.vue -->
<template>
  <router-view />
  <ToastContainer />
</template>

<script>
import ToastContainer from './components/ToastContainer.vue';

export default {
  name: 'App',
  components: { ToastContainer }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: #f5f7fa;
}

#app {
  min-height: 100vh;
}
</style>