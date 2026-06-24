"""Orquestador de entrevista con estado: decide flujo y delega subtareas a motores."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from fastapi import HTTPException

from app.schemas.ai import EvaluationResponse
from app.schemas.interview import (
    InterviewConfig,
    InterviewQuestion,
    InterviewSessionStatusResponse,
    InterviewStartResponse,
    InterviewTurnResponse,
)
from app.services.evaluation_engine import EvaluationEngine
from app.services.interviewer_engine import InterviewerEngine

MAX_FOLLOW_UPS_PER_QUESTION = 2


@dataclass
class QuestionRecord:
    """Registro estructurado por pregunta para evaluar sin inferir transcript libre."""

    question_number: int
    question: str
    category: str
    candidate_answers: list[str] = field(default_factory=list)
    follow_ups: list[str] = field(default_factory=list)
    follow_up_answers: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class InterviewSession:
    """Estado completo de una sesion en memoria."""

    interview_id: str
    config: InterviewConfig
    questions: list[InterviewQuestion]
    current_question_index: int = 0
    follow_up_stage: int = 0
    interview_complete: bool = False
    history_summary: str = ""
    transcript: list[dict[str, str]] = field(default_factory=list)
    records: list[QuestionRecord] = field(default_factory=list)


class InterviewOrchestrator:
    """Coordina sesiones y separa motores de conversacion/evaluacion."""

    def __init__(self, interviewer_engine: InterviewerEngine, evaluation_engine: EvaluationEngine) -> None:
        self._interviewer_engine = interviewer_engine
        self._evaluation_engine = evaluation_engine
        self._sessions: dict[str, InterviewSession] = {}

    @staticmethod
    def _compact_text(value: str, limit: int) -> str:
        compact = " ".join(str(value or "").split())
        if len(compact) <= limit:
            return compact
        return compact[: max(0, limit - 1)].rstrip() + "…"

    @staticmethod
    def _role_context(config: InterviewConfig) -> str:
        return (
            f"{config.jobRole} nivel {config.seniority}, tipo {config.interviewType}, "
            f"stack {config.stack or 'general'}"
        )

    @staticmethod
    def _missing_dimensions(answer: str, stage: int) -> list[str]:
        lower = answer.lower()
        missing: list[str] = []

        if not any(k in lower for k in ["trade-off", "tradeoff", "costo", "beneficio", "contra"]):
            missing.append("tradeoff_missing")

        if not any(k in lower for k in ["riesgo", "mitig", "fall", "impacto negativo"]):
            missing.append("risk_missing")

        if not any(k in lower for k in ["metrica", "kpi", "p95", "resultado", "porcentaje", "tiempo", "%"]):
            missing.append("metric_missing")

        words = len(answer.split())
        if words < 40 and stage == 0:
            missing.append("example_missing")

        return missing

    def _get_session(self, interview_id: str) -> InterviewSession:
        session = self._sessions.get(interview_id)
        if not session:
            raise HTTPException(status_code=404, detail="Sesion de entrevista no encontrada.")
        return session

    @staticmethod
    def _question_text(index: int, q: InterviewQuestion) -> str:
        return f"Pregunta {index + 1} · {q.category}\n{q.prompt}"

    def start_session(
        self,
        *,
        config: InterviewConfig,
        questions: list[InterviewQuestion],
    ) -> InterviewStartResponse:
        """Inicia sesion y devuelve primera pregunta."""
        if not questions:
            raise HTTPException(status_code=400, detail="Se requiere al menos una pregunta.")

        interview_id = str(uuid4())
        session = InterviewSession(
            interview_id=interview_id,
            config=config,
            questions=questions,
        )

        first = questions[0]
        first_text = self._question_text(0, first)
        session.transcript.append(
            {
                "role": "interviewer",
                "source": "system",
                "content": first_text,
            }
        )
        session.records.append(
            QuestionRecord(
                question_number=1,
                question=first.prompt,
                category=first.category,
            )
        )

        self._sessions[interview_id] = session

        return InterviewStartResponse(
            interview_id=interview_id,
            turn_type="ask_question",
            source="system",
            reply=first_text,
            current_question_index=0,
            total_questions=len(questions),
            follow_up_stage=0,
            interview_complete=False,
            tags=[],
            latency_ms=0,
        )

    async def submit_turn(self, *, interview_id: str, answer: str) -> InterviewTurnResponse:
        """Procesa turno candidato y decide follow-up, avance o cierre."""
        session = self._get_session(interview_id)
        if session.interview_complete:
            raise HTTPException(status_code=400, detail="La sesion ya fue completada.")

        clean_answer = self._compact_text(answer, 2000)
        session.transcript.append(
            {
                "role": "candidate",
                "source": "user",
                "content": clean_answer,
            }
        )

        record = session.records[session.current_question_index]
        if session.follow_up_stage == 0:
            record.candidate_answers.append(clean_answer)
        else:
            record.follow_up_answers.append(clean_answer)

        missing = self._missing_dimensions(clean_answer, session.follow_up_stage)
        role_context = self._role_context(session.config)
        question_prompt = session.questions[session.current_question_index].prompt

        if missing and session.follow_up_stage < MAX_FOLLOW_UPS_PER_QUESTION:
            follow_up, source, latency_ms = await self._interviewer_engine.generate_follow_up(
                question=question_prompt,
                last_answer=clean_answer,
                context_summary=session.history_summary,
                missing_dimensions=missing,
                stage=session.follow_up_stage,
                role_context=role_context,
            )

            session.follow_up_stage += 1
            record.tags = list(dict.fromkeys(record.tags + missing))
            record.follow_ups.append(follow_up)
            session.transcript.append(
                {
                    "role": "interviewer",
                    "source": source,
                    "content": follow_up,
                }
            )

            return InterviewTurnResponse(
                interview_id=interview_id,
                turn_type="follow_up",
                source=source,
                reply=follow_up,
                current_question_index=session.current_question_index,
                total_questions=len(session.questions),
                follow_up_stage=session.follow_up_stage,
                interview_complete=False,
                tags=missing,
                latency_ms=latency_ms,
            )

        # Cierra pregunta actual y avanza.
        answer_snippet = self._compact_text(clean_answer, 220)
        session.history_summary = self._compact_text(
            f"{session.history_summary} Q{session.current_question_index + 1}: {answer_snippet}",
            900,
        )

        if session.current_question_index + 1 < len(session.questions):
            session.current_question_index += 1
            session.follow_up_stage = 0
            next_q = session.questions[session.current_question_index]
            next_text = self._question_text(session.current_question_index, next_q)
            session.records.append(
                QuestionRecord(
                    question_number=session.current_question_index + 1,
                    question=next_q.prompt,
                    category=next_q.category,
                )
            )
            session.transcript.append(
                {
                    "role": "interviewer",
                    "source": "system",
                    "content": next_text,
                }
            )

            return InterviewTurnResponse(
                interview_id=interview_id,
                turn_type="move_next",
                source="system",
                reply=next_text,
                current_question_index=session.current_question_index,
                total_questions=len(session.questions),
                follow_up_stage=0,
                interview_complete=False,
                tags=[],
                latency_ms=0,
            )

        session.interview_complete = True
        closing = "Excelente. Hemos cerrado todas las preguntas de la entrevista."
        session.transcript.append(
            {
                "role": "interviewer",
                "source": "system",
                "content": closing,
            }
        )

        return InterviewTurnResponse(
            interview_id=interview_id,
            turn_type="close_interview",
            source="system",
            reply=closing,
            current_question_index=session.current_question_index,
            total_questions=len(session.questions),
            follow_up_stage=session.follow_up_stage,
            interview_complete=True,
            tags=[],
            latency_ms=0,
        )

    async def evaluate_session(self, *, interview_id: str) -> EvaluationResponse:
        """Evalua la sesion usando registros estructurados por pregunta."""
        session = self._get_session(interview_id)

        pairs: list[dict[str, str]] = []
        for record in session.records:
            main_answer = record.candidate_answers[0] if record.candidate_answers else ""
            followups_block = " ".join(record.follow_up_answers[:2]) if record.follow_up_answers else ""
            merged_answer = self._compact_text(f"{main_answer} {followups_block}".strip(), 900)
            if not merged_answer:
                continue
            pairs.append(
                {
                    "question": record.question,
                    "answer": merged_answer,
                }
            )

        return await self._evaluation_engine.evaluate_pairs(
            role_context=self._role_context(session.config),
            pairs=pairs,
        )

    def get_status(self, *, interview_id: str) -> InterviewSessionStatusResponse:
        """Devuelve estado resumido de la sesion."""
        session = self._get_session(interview_id)
        return InterviewSessionStatusResponse(
            interview_id=interview_id,
            current_question_index=session.current_question_index,
            total_questions=len(session.questions),
            follow_up_stage=session.follow_up_stage,
            interview_complete=session.interview_complete,
            transcript_items=len(session.transcript),
        )

    def get_transcript(self, *, interview_id: str) -> list[dict[str, Any]]:
        """Entrega transcript para frontend sin recalcular prompts."""
        session = self._get_session(interview_id)
        return session.transcript
