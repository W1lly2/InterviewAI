"""Esquemas de sesion para entrevista orquestada por backend."""

from pydantic import BaseModel, Field


class InterviewQuestion(BaseModel):
    """Pregunta candidata a ser usada durante la entrevista."""

    category: str = Field(default="General", max_length=120)
    title: str = Field(default="Pregunta", max_length=200)
    prompt: str = Field(..., min_length=5, max_length=1200)


class InterviewConfig(BaseModel):
    """Configuracion base de la entrevista."""

    jobRole: str = Field(default="Frontend Developer", max_length=120)
    seniority: str = Field(default="Semi Senior", max_length=80)
    interviewType: str = Field(default="Mixta", max_length=80)
    stack: str = Field(default="General", max_length=500)


class InterviewStartRequest(BaseModel):
    """Entrada para iniciar una sesion orquestada."""

    config: InterviewConfig
    questions: list[InterviewQuestion] = Field(..., min_items=1, max_items=20)


class InterviewTurnRequest(BaseModel):
    """Entrada de un turno del candidato."""

    answer: str = Field(..., min_length=1, max_length=4000)


class InterviewTurnResponse(BaseModel):
    """Salida normalizada de cada turno del entrevistador."""

    interview_id: str
    turn_type: str
    source: str
    reply: str
    current_question_index: int
    total_questions: int
    follow_up_stage: int
    interview_complete: bool
    tags: list[str] = Field(default_factory=list)
    latency_ms: int = 0


class InterviewStartResponse(InterviewTurnResponse):
    """Respuesta inicial al crear una sesion."""


class InterviewSessionStatusResponse(BaseModel):
    """Estado resumido de la sesion para depuracion/UI."""

    interview_id: str
    current_question_index: int
    total_questions: int
    follow_up_stage: int
    interview_complete: bool
    transcript_items: int
