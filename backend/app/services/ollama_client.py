"""Cliente HTTP para interactuar con Ollama desde FastAPI."""

import httpx

from app.core.settings import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT_SECONDS


class OllamaClient:
    """Encapsula llamadas a Ollama para mantener endpoints limpios."""

    def __init__(self) -> None:
        # Guarda configuracion en memoria para reutilizarla en cada request.
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL
        self.timeout = OLLAMA_TIMEOUT_SECONDS

    async def is_reachable(self) -> bool:
        """Comprueba si el servicio de Ollama responde localmente."""
        try:
            # Consulta el catalogo de modelos como check de disponibilidad.
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
            return True
        except httpx.HTTPError:
            # Cualquier error HTTP implica que el servicio no esta utilizable.
            return False

    async def chat(self, message: str, system_prompt: str | None = None) -> str:
        """Genera una respuesta de texto usando el modelo configurado."""
        payload = {
            "model": self.model,
            "stream": False,
            "prompt": message,
        }

        if system_prompt:
            # Solo agrega instrucciones de sistema si el caller las envia.
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()

        data = response.json()
        # Normaliza la salida a string no vacio para evitar None aguas abajo.
        return str(data.get("response", "")).strip()
