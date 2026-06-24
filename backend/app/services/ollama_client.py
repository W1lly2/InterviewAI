"""Cliente HTTP para interactuar con Ollama desde FastAPI."""

import asyncio

import httpx

from app.core.settings import (
    OLLAMA_BASE_URL,
    OLLAMA_KEEP_ALIVE,
    OLLAMA_MAX_CONCURRENCY,
    OLLAMA_MAX_RETRIES,
    OLLAMA_MODEL,
    OLLAMA_NUM_CTX,
    OLLAMA_RETRY_BACKOFF_SECONDS,
    OLLAMA_TIMEOUT_SECONDS,
)


class OllamaClient:
    """Encapsula llamadas a Ollama para mantener endpoints limpios."""

    def __init__(self) -> None:
        # Guarda configuracion en memoria para reutilizarla en cada request.
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL
        self.timeout = OLLAMA_TIMEOUT_SECONDS
        self.max_retries = max(0, OLLAMA_MAX_RETRIES)
        self.retry_backoff_seconds = max(0.1, OLLAMA_RETRY_BACKOFF_SECONDS)
        self.num_ctx = max(512, OLLAMA_NUM_CTX)
        self.keep_alive = OLLAMA_KEEP_ALIVE
        self.max_concurrency = max(1, OLLAMA_MAX_CONCURRENCY)
        self._gate = asyncio.Semaphore(self.max_concurrency)

    async def is_reachable(self) -> bool:
        """Comprueba si el servicio de Ollama responde localmente."""
        try:
            # Consulta el catalogo de modelos como check de disponibilidad.
            quick_timeout = min(self.timeout, 6)
            async with httpx.AsyncClient(timeout=quick_timeout) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
            return True
        except httpx.HTTPError:
            # Cualquier error HTTP implica que el servicio no esta utilizable.
            return False

    async def generate(
        self,
        message: str,
        system_prompt: str | None = None,
        *,
        temperature: float = 0.2,
        top_p: float = 0.9,
        num_predict: int = 512,
        format: str | None = None,
    ) -> str:
        """Genera una respuesta de texto usando el modelo configurado."""
        payload = {
            "model": self.model,
            "stream": False,
            "prompt": message,
            "keep_alive": self.keep_alive,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": num_predict,
                "num_ctx": self.num_ctx,
            },
        }

        if system_prompt:
            # Solo agrega instrucciones de sistema si el caller las envia.
            payload["system"] = system_prompt

        if format:
            # Permite forzar formato JSON cuando se necesite parseo robusto.
            payload["format"] = format

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                async with self._gate:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.post(
                            f"{self.base_url}/api/generate", json=payload
                        )
                        response.raise_for_status()
                data = response.json()
                # Normaliza la salida a string no vacio para evitar None aguas abajo.
                return str(data.get("response", "")).strip()
            except (httpx.HTTPError, ValueError) as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                # Backoff exponencial suave para dar tiempo al motor local.
                await asyncio.sleep(self.retry_backoff_seconds * (2**attempt))

        raise RuntimeError("No se pudo generar respuesta de Ollama") from last_error

    async def chat(self, message: str, system_prompt: str | None = None) -> str:
        """Compatibilidad: chat simple para endpoints existentes."""
        return await self.generate(message=message, system_prompt=system_prompt)
