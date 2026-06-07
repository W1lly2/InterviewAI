# Backend - FastAPI

Este backend se organiza por capas para mantener el codigo limpio y escalable.

## Carpetas

- app/api/v1: endpoints versionados.
- app/core: configuracion, seguridad y utilidades globales.
- app/models: entidades de dominio/persistencia.
- app/schemas: contratos de entrada/salida (Pydantic).
- app/services: logica de negocio (preguntas, evaluacion, reportes).

## Flujo de dominio esperado

1. Entrevista configurada por el frontend.
2. Servicio de generacion de preguntas segun puesto y seniority.
3. Conversacion guiada por IA con contexto acumulado.
4. Evaluacion por rubrica y competencias.
5. Generacion de reporte final con fortalezas y mejoras.

## IA local gratis con Ollama

El backend ya incluye una integracion inicial para empezar con un modelo ligero local.

### Modelo por defecto

- `llama3.2:1b` (ligero para comenzar en equipos modestos)

### Variables de entorno opcionales

- `OLLAMA_BASE_URL` (default: `http://localhost:11434`)
- `OLLAMA_MODEL` (default: `llama3.2:1b`)
- `OLLAMA_TIMEOUT_SECONDS` (default: `90`)

### Endpoints disponibles

- `GET /api/v1/ai/status`: estado de conexion con Ollama.
- `POST /api/v1/ai/chat`: prueba de generacion de respuesta.

### Arranque rapido

1. Instalar Ollama y ejecutarlo en local.
2. Descargar modelo ligero inicial: `ollama pull llama3.2:1b`
3. Levantar API: `uvicorn app.main:app --reload`
