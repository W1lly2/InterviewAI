import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

// Configuracion base para ejecutar el frontend localmente.
export default defineConfig({
  plugins: [svelte()],

  server: {
    // Reenvía /api al backend FastAPI para evitar errores de CORS en desarrollo.
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});
