"""Configuracion simple de entorno para integrar Ollama localmente."""

import os

# Endpoint local por defecto de Ollama.
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Modelo ligero inicial para pruebas gratis en equipos modestos.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# Timeout prudente para equipos sin GPU.
# Convierte a float para garantizar tipo numerico en el cliente HTTP.
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))

# Reintentos para amortiguar fallos transitorios del motor local.
OLLAMA_MAX_RETRIES = int(os.getenv("OLLAMA_MAX_RETRIES", "2"))
OLLAMA_RETRY_BACKOFF_SECONDS = float(os.getenv("OLLAMA_RETRY_BACKOFF_SECONDS", "1.2"))

# Control de contexto y residencia del modelo en memoria.
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "2048"))
OLLAMA_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "15m")
OLLAMA_MAX_CONCURRENCY = int(os.getenv("OLLAMA_MAX_CONCURRENCY", "1"))
