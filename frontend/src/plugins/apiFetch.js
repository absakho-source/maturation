// Plugin pour intercepter les appels fetch et ajouter l'URL de base de l'API
import { API_BASE_URL } from '../config/api'

// Sauvegarde la fonction fetch originale
const originalFetch = window.fetch

// Remplace fetch globalement
window.fetch = function(url, options) {
  // Si l'URL commence par /api, ajoute l'URL de base
  if (typeof url === 'string' && url.startsWith('/api')) {
    url = `${API_BASE_URL}${url}`
  }

  // Appelle la fonction fetch originale
  return originalFetch(url, options)
}

export default {
  install(app) {
    // Plugin vide, la logique est dans le remplacement global de fetch
  }
}
