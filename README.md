# InterviewAI

InterviewAI es una aplicación web para practicar entrevistas técnicas y de negocio. Permite configurar una entrevista, responder preguntas en un chat guiado por IA y recibir una evaluación con fortalezas, áreas de mejora y recomendaciones.

## Funcionalidades actuales

- Configuración por puesto, seniority, tipo de entrevista y stack.
- Generación local de preguntas a partir de catálogos y plantillas del frontend; no requiere un modelo para esta etapa.
- Chat con sesiones gestionadas por la API. El entrevistador puede hacer preguntas de seguimiento según las respuestas.
- Evaluación final de la sesión y reporte por pregunta.
- Integración con Ollama para generar seguimientos y evaluaciones. Si Ollama falla durante esas generaciones, el backend dispone de respuestas y evaluación de contingencia.
- Indicador de disponibilidad del modelo configurado.

El flujo de la interfaz tiene cinco etapas: configurar, generar preguntas, conversar, evaluar y consultar el reporte. La aplicación aún no usa una base de datos: las sesiones se guardan en memoria y se pierden al reiniciar el backend. El frontend requiere que Ollama esté disponible para iniciar el chat.

## Tecnologías

- **Frontend:** Svelte 4, Vite y TypeScript.
- **Backend:** Python 3.10+, FastAPI, Pydantic y HTTPX.
- **IA local:** Ollama; el modelo predeterminado es `llama3.2:3b`.

## Requisitos

- Node.js y npm.
- Python 3.10 o posterior.
- [Ollama](https://ollama.com/) para usar el chat y la evaluación con IA.

## Ejecución local

### 1. Iniciar Ollama

Instala Ollama y descarga el modelo predeterminado:

```bash
ollama pull llama3.2:3b
```

Comprueba que Ollama esté ejecutándose en `http://localhost:11434`. Si no se inicia automáticamente, arráncalo con `ollama serve`.

### 2. Iniciar el backend

En una terminal, desde la raíz del repositorio:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

En Windows, activa el entorno con `.venv\Scripts\activate`. La API queda disponible en `http://localhost:8000`; el endpoint de salud es `http://localhost:8000/health` y la documentación interactiva de FastAPI está en `http://localhost:8000/docs`.

### 3. Iniciar el frontend

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

Abre la URL que indique Vite (normalmente `http://localhost:5173`). Durante el desarrollo, Vite reenvía las solicitudes `/api` al backend en `http://localhost:8000`.

## Configuración de Ollama

El backend lee estas variables de entorno al arrancar:

| Variable | Valor predeterminado | Descripción |
| --- | --- | --- |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL del servicio Ollama. |
| `OLLAMA_MODEL` | `llama3.2:3b` | Modelo usado para generación. |
| `OLLAMA_TIMEOUT_SECONDS` | `120` | Tiempo máximo de espera por solicitud. |
| `OLLAMA_MAX_RETRIES` | `2` | Reintentos ante errores transitorios. |
| `OLLAMA_NUM_CTX` | `2048` | Tamaño del contexto del modelo. |
| `OLLAMA_KEEP_ALIVE` | `15m` | Tiempo de residencia del modelo en memoria. |
| `OLLAMA_MAX_CONCURRENCY` | `1` | Generaciones concurrentes permitidas. |

Por ejemplo, para seleccionar otro modelo, define `OLLAMA_MODEL` antes de iniciar Uvicorn y asegúrate de haberlo descargado en Ollama.

## API principal

Todas las rutas versionadas están bajo `/api/v1`:

| Método | Ruta | Propósito |
| --- | --- | --- |
| `GET` | `/health` | Comprobar que la API está activa. |
| `GET` | `/api/v1/ai/status` | Consultar la disponibilidad de Ollama y el modelo configurado. |
| `POST` | `/api/v1/ai/chat` | Probar generación de texto con IA. |
| `POST` | `/api/v1/ai/evaluate` | Evaluar un transcript enviado por el cliente. |
| `POST` | `/api/v1/interviews/start` | Crear una sesión y obtener la primera pregunta. |
| `POST` | `/api/v1/interviews/{interview_id}/turn` | Enviar una respuesta y obtener el siguiente turno. |
| `POST` | `/api/v1/interviews/{interview_id}/evaluate` | Evaluar la sesión estructurada. |
| `GET` | `/api/v1/interviews/{interview_id}/status` | Consultar el estado de la sesión. |
| `GET` | `/api/v1/interviews/{interview_id}/transcript` | Obtener el transcript de la sesión. |

## Estructura del repositorio

```text
backend/
  app/
    api/v1/       Rutas HTTP versionadas
    core/         Configuración
    schemas/      Contratos de entrada y salida
    services/     Orquestación, entrevista, evaluación y cliente Ollama
frontend/
  src/
    components/   Pantallas y componentes Svelte
    modules/      Catálogos, estado, sesiones y cliente API
    styles/       Estilos globales
```
