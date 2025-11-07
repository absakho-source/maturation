import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// ✅ Import global du thème DGPPE sobre
import './assets/styles-dgppe-sobre.css'

// Configuration de l'API - Intercepte les appels fetch pour ajouter l'URL backend en production
const API_BASE_URL = import.meta.env.VITE_API_URL || ''
console.log('[API Config] API_BASE_URL:', API_BASE_URL)

// Sauvegarde de la fonction fetch originale
const originalFetch = window.fetch

// Remplacement global de fetch
window.fetch = function(url, options) {
  // Si l'URL commence par /api, ajoute l'URL de base
  if (typeof url === 'string' && url.startsWith('/api')) {
    const newUrl = `${API_BASE_URL}${url}`
    console.log('[API Fetch] Redirection:', url, '→', newUrl)
    url = newUrl
  }

  // Appelle la fonction fetch originale
  return originalFetch(url, options)
}

const app = createApp(App)
app.use(router)
app.mount('#app')
