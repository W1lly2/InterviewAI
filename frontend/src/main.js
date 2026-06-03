import App from './App.svelte';
import './styles/global.css';

// Monta la aplicacion principal en el contenedor raiz.
const app = new App({
  target: document.getElementById('app')
});

export default app;
