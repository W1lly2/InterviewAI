"""Configuracion simple de entorno para integrar Ollama localmente."""

import os

# Endpoint local por defecto de Ollama.
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Modelo ligero inicial para pruebas gratis en equipos modestos.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

# Timeout prudente para equipos sin GPU.
# Convierte a float para garantizar tipo numerico en el cliente HTTP.
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "90"))
