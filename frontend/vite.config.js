import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// Build version: 1.0.13 - 2025-12-10 11:20 - Amélioration layout badge lecture seule
export default defineConfig({
  plugins: [vue()],
  publicDir: 'public',
  build: {
    // Force complete rebuild from source
    emptyOutDir: true
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 5173,
    host: '127.0.0.1',
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5002',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
