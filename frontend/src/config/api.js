// Configuration de l'URL de l'API
// En développement: utilise le proxy Vite (vide ou '')
// En production: utilise l'URL complète du backend
export const API_BASE_URL = import.meta.env.VITE_API_URL || ''

// Helper pour construire les URLs d'API
export function apiUrl(path) {
  // S'assure que le path commence par /
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${API_BASE_URL}${normalizedPath}`
}

// Helper pour fetch avec l'URL complète
export async function apiFetch(path, options = {}) {
  const url = apiUrl(path)
  return fetch(url, options)
}
