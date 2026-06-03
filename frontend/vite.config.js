import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

// Configuracion base para ejecutar el frontend localmente.
export default defineConfig({
  plugins: [svelte()]
});
