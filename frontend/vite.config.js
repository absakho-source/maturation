import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// Build version: 1.0.39 - 2025-12-11 - Move Fatick left x: -0.15, y: -0.30
export default defineConfig({
  plugins: [vue()],
  publicDir: 'public',
  build: {
    // Force complete rebuild from source
    emptyOutDir: true,
    // Increase chunk size warning limit for large JSON files
    chunkSizeWarningLimit: 10000
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
