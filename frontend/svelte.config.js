import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/**
 * Configuracion del servidor de lenguaje Svelte para VS Code.
 */
const config = {
  // Habilita soporte de TypeScript y PostCSS en templates Svelte.
  preprocess: vitePreprocess()
};

export default config;
