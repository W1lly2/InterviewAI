"""Endpoints de entrevista orquestada con estado y SLA interno."""

from fastapi import APIRouter

from app.schemas.ai import EvaluationResponse
from app.schemas.interview import (
    InterviewSessionStatusResponse,
    InterviewStartRequest,
    InterviewStartResponse,
    InterviewTurnRequest,
    InterviewTurnResponse,
)
from app.services.evaluation_engine import EvaluationEngine
from app.services.interviewer_engine import InterviewerEngine
from app.services.interview_orchestrator import InterviewOrchestrator
from app.services.ollama_client import OllamaClient

router = APIRouter(tags=["interviews"])

# Instancias compartidas para toda la API.
_ollama_client = OllamaClient()
_interviewer_engine = InterviewerEngine(_ollama_client)
_evaluation_engine = EvaluationEngine(_ollama_client)
_orchestrator = InterviewOrchestrator(_interviewer_engine, _evaluation_engine)


@router.post("/start", response_model=InterviewStartResponse)
async def start_interview(payload: InterviewStartRequest) -> InterviewStartResponse:
    """Crea una sesion y retorna la primera pregunta."""
    return _orchestrator.start_session(config=payload.config, questions=payload.questions)


@router.post("/{interview_id}/turn", response_model=InterviewTurnResponse)
async def submit_turn(interview_id: str, payload: InterviewTurnRequest) -> InterviewTurnResponse:
    """Recibe respuesta del candidato y retorna siguiente intervencion."""
    return await _orchestrator.submit_turn(interview_id=interview_id, answer=payload.answer)


@router.post("/{interview_id}/evaluate", response_model=EvaluationResponse)
async def evaluate_interview(interview_id: str) -> EvaluationResponse:
    """Evalua la sesion completa desde registros estructurados."""
    return await _orchestrator.evaluate_session(interview_id=interview_id)


@router.get("/{interview_id}/status", response_model=InterviewSessionStatusResponse)
async def interview_status(interview_id: str) -> InterviewSessionStatusResponse:
    """Expone estado de la sesion para UI y debug."""
    return _orchestrator.get_status(interview_id=interview_id)


@router.get("/{interview_id}/transcript")
async def interview_transcript(interview_id: str) -> list[dict]:
    """Devuelve transcript estructurado almacenado en backend."""
    return _orchestrator.get_transcript(interview_id=interview_id)
