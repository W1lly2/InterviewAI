"""Esquemas de entrada y salida para endpoints de IA."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Mensaje del usuario para la simulacion de entrevista."""

    # Valida que el usuario siempre envie texto util y acotado.
    message: str = Field(..., min_length=1, max_length=6000)
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


class FeedbackItem(BaseModel):
    """Evaluacion de una pregunta y su respuesta."""

    # Numero de la pregunta en la entrevista.
    question_number: int
    # Texto original de la pregunta formulada.
    question: str
    # Respuesta del candidato.
    answer: str
    # Fortalezas identificadas en la respuesta (max 3 bullets).
    strengths: list[str]
    # Areas de mejora detectadas (max 3 bullets).
    gaps: list[str]
    # Recomendacion puntual y accionable.
    recommendation: str
    # Score de 0 a 100 para esta respuesta.
    score: int


class EvaluationRequest(BaseModel):
    """Solicitud de evaluacion del transcript completo del chat."""

    # Historial del chat: lista de {role: interviewer|candidate, content: ...}
    transcript: list[dict] = Field(..., min_items=1)
    # Contexto de la entrevista (puesto, seniority, tipo).
    interview_context: str | None = Field(default=None, max_length=1000)


class EvaluationResponse(BaseModel):
    """Resultado de la evaluacion de una entrevista completa."""

    # Evaluaciones individuales por pregunta.
    feedback_items: list[FeedbackItem]
    # Score promedio de todas las respuestas.
    overall_score: int
    # Resumen ejecutivo de la sesion.
    summary: str
