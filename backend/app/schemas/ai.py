"""Esquemas de entrada y salida para endpoints de IA."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Mensaje del usuario para la simulacion de entrevista."""

    # Valida que el usuario siempre envie texto util y acotado.
    message: str = Field(..., min_length=1, max_length=3000)
    # Limita longitud de instrucciones para evitar prompts excesivos.
    system_prompt: str | None = Field(default=None, max_length=2000)


class ChatResponse(BaseModel):
    """Respuesta generada por el modelo local en Ollama."""

    # Identifica el modelo que produjo la respuesta.
    model: str
    # Texto final mostrado al usuario en el chat.
    reply: str


class AiStatusResponse(BaseModel):
    """Estado de disponibilidad de la integracion local."""

    # Modelo activo configurado en entorno.
    configured_model: str
    # Host donde se espera el servicio de Ollama.
    ollama_base_url: str
    # Señal booleana para habilitar o bloquear interaccion desde frontend.
    reachable: bool
