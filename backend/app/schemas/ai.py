"""Esquemas de entrada y salida para endpoints de IA."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Mensaje del usuario para la simulacion de entrevista."""

    message: str = Field(..., min_length=1, max_length=3000)
    system_prompt: str | None = Field(default=None, max_length=2000)


class ChatResponse(BaseModel):
    """Respuesta generada por el modelo local en Ollama."""

    model: str
    reply: str


class AiStatusResponse(BaseModel):
    """Estado de disponibilidad de la integracion local."""

    configured_model: str
    ollama_base_url: str
    reachable: bool
