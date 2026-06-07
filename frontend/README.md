# Frontend - Svelte

Interfaz para configurar y ejecutar simulaciones de entrevista.

## Vista actual implementada

- Hero con propuesta de valor.
- Flujo visual de 5 etapas del proceso.
- Formulario de configuracion de entrevista.
- Segunda pantalla de "Generar preguntas" con set dinamico mock.
- Estilos responsive para desktop y mobile.

## Modularizacion aplicada

- `src/components`: vistas por fase y bloques UI reutilizables.
- `src/modules/interview/catalog.js`: catalogos y blueprints del dominio.
- `src/modules/interview/state.js`: estado inicial del formulario.
- `src/modules/interview/questionGenerator.js`: generador de preguntas mock.

Con esta estructura, `App.svelte` queda enfocado solo en orquestar el flujo y eventos.

## Proxima etapa sugerida

Conectar la generacion de preguntas con el endpoint del backend e implementar la vista de chat (paso 3).
