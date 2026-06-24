"""Endpoints iniciales para probar IA local con Ollama."""

import asyncio
import json
from typing import Any

from fastapi import APIRouter, HTTPException

from app.schemas.ai import (
    AiStatusResponse,
    ChatRequest,
    ChatResponse,
    EvaluationRequest,
    EvaluationResponse,
    FeedbackItem,
)
from app.services.ollama_client import OllamaClient

router = APIRouter(tags=["ai"])
# Reutiliza un cliente unico para evitar reinstanciarlo en cada request.
ollama_client = OllamaClient()
MODEL_GATE = asyncio.Semaphore(1)

MAX_EVAL_PAIRS = 6
MAX_QUESTION_CHARS = 260
MAX_ANSWER_CHARS = 700
MAX_CHAT_CONTEXT_CHARS = 3200


def _compact_text(value: str, limit: int) -> str:
    """Compacta espacios y recorta texto para reducir tokens."""
    compact = " ".join(str(value or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: max(0, limit - 1)].rstrip() + "…"


def _extract_last_candidate_answer(raw_context: str) -> str:
    """Extrae la ultima respuesta del candidato desde el contexto de chat."""
    marker = "[Tu respuesta]:"
    idx = raw_context.rfind(marker)
    if idx == -1:
        return _compact_text(raw_context, 220)

    answer = raw_context[idx + len(marker) :].strip()
    # Corta si el bloque incluye otro marcador posterior.
    next_marker = answer.find("[")
    if next_marker > 0:
        answer = answer[:next_marker].strip()

    return _compact_text(answer, 260)


def _extract_last_interviewer_prompt(raw_context: str) -> str:
    """Obtiene el ultimo turno del entrevistador para detectar repeticiones."""
    marker = "[Entrevistador"
    idx = raw_context.rfind(marker)
    if idx == -1:
        return ""

    chunk = raw_context[idx:]
    # Toma texto despues de "]:" hasta el final del bloque.
    split_idx = chunk.find(":")
    if split_idx == -1:
        return ""
    return _compact_text(chunk[split_idx + 1 :], 300).lower()


def _fallback_stage(raw_context: str) -> int:
    """Calcula etapa de profundizacion para no repetir la misma repregunta."""
    context_lower = raw_context.lower()
    stage_signals = [
        "trade-off",
        "riesgo principal",
        "metrica concreta",
        "que pospondrias",
        "cerramos esta pregunta",
    ]
    return sum(1 for token in stage_signals if token in context_lower)


def _build_fallback_chat_reply(raw_context: str) -> str:
    """Respuesta deterministica para continuidad cuando Ollama tarda/falla."""
    answer = _extract_last_candidate_answer(raw_context)
    last_prompt = _extract_last_interviewer_prompt(raw_context)
    stage = _fallback_stage(raw_context)

    # Evita repetir exactamente la misma repregunta en cascada.
    if "trade-off" in last_prompt and "metrica" in last_prompt:
        stage = max(stage, 2)

    if stage <= 1:
        return (
            "Buen punto. Para profundizar en ese mismo caso, responde breve estas 3 cosas: "
            "1) que trade-off elegiste y por que, 2) que riesgo principal evitaste, "
            "3) que metrica concreta cambio (antes/despues). "
            f"Base: \"{answer}\""
        )

    if stage == 2:
        return (
            "Bien. Siguiente nivel de detalle: dame un mini cierre en formato STAR (situacion, tarea, accion, resultado) "
            "en 5-6 lineas, incluyendo un numero de impacto. "
            f"Apoyate en: \"{answer}\""
        )

    return (
        "Perfecto, la idea ya quedo clara y bien estructurada. Cerramos esta pregunta. "
        "Si quieres seguir, avanza a la siguiente pregunta para evaluar otro escenario tecnico en Svelte."
    )


def _extract_qa_pairs(transcript: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convierte transcript libre en pares pregunta/respuesta evaluables."""
    pairs: list[dict[str, Any]] = []
    pending_question: str | None = None

    for msg in transcript:
        role = str(msg.get("role", "")).lower()
        content = str(msg.get("content", "")).strip()
        if not content:
            continue

        if role == "interviewer":
            pending_question = content
            continue

        if role == "candidate" and pending_question:
            pairs.append(
                {
                    "question": _compact_text(pending_question, MAX_QUESTION_CHARS),
                    "answer": _compact_text(content, MAX_ANSWER_CHARS),
                }
            )
            pending_question = None

    # Limita el volumen para mantener latencia estable con modelos pequenos.
    return pairs[-MAX_EVAL_PAIRS:]


def _build_eval_prompt(context: str, pairs: list[dict[str, Any]], strict: bool) -> str:
    """Crea prompt compacto para evaluacion estructurada."""
    pairs_text = "\n".join(
        [
            f"Q{i + 1}: {pair['question']}\nA{i + 1}: {pair['answer']}"
            for i, pair in enumerate(pairs)
        ]
    )

    strict_line = (
        "Return only valid JSON. Do not include markdown, explanation, or backticks."
        if strict
        else "Return JSON if possible."
    )

    return f"""You are an interview evaluator.
Context: {context}

Evaluate each Q/A pair on:
- strengths: max 2 short bullets
- gaps: max 2 short bullets
- recommendation: 1 concrete action
- score: integer 0-100

Input pairs:
{pairs_text}

Output schema:
{{
  "feedback_items": [
    {{
      "question_number": 1,
      "question": "...",
      "answer": "...",
      "strengths": ["..."],
      "gaps": ["..."],
      "recommendation": "...",
      "score": 0
    }}
  ],
  "overall_score": 0,
  "summary": "..."
}}

Rules:
- Keep exactly {len(pairs)} feedback_items.
- Use Spanish for all text fields.
- Keep summary <= 280 chars.
{strict_line}"""


def _extract_json_object(raw: str) -> dict[str, Any]:
    """Parsea JSON tolerando texto extra alrededor del objeto."""
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end <= start:
        raise json.JSONDecodeError("No JSON object found", raw, 0)
    return json.loads(raw[start:end])


def _normalize_feedback_items(
    raw_items: Any, pairs: list[dict[str, Any]]
) -> list[FeedbackItem]:
    """Normaliza salida del modelo para garantizar contrato estable."""
    normalized: list[FeedbackItem] = []
    items = raw_items if isinstance(raw_items, list) else []

    for idx, pair in enumerate(pairs, start=1):
        item = items[idx - 1] if idx - 1 < len(items) and isinstance(items[idx - 1], dict) else {}
        strengths = item.get("strengths", [])
        gaps = item.get("gaps", [])

        if not isinstance(strengths, list):
            strengths = [str(strengths)]
        if not isinstance(gaps, list):
            gaps = [str(gaps)]

        raw_score = item.get("score", 50)
        try:
            score = int(raw_score)
        except (ValueError, TypeError):
            score = 50

        normalized.append(
            FeedbackItem(
                question_number=idx,
                question=_compact_text(str(item.get("question", pair["question"])), MAX_QUESTION_CHARS),
                answer=_compact_text(str(item.get("answer", pair["answer"])), MAX_ANSWER_CHARS),
                strengths=[_compact_text(str(s), 140) for s in strengths[:2]]
                or ["Respuesta entendible para el contexto."],
                gaps=[_compact_text(str(g), 140) for g in gaps[:2]]
                or ["Falto mayor detalle tecnico en algunos puntos."],
                recommendation=_compact_text(
                    str(item.get("recommendation", "Incluye un ejemplo concreto con metricas.")),
                    220,
                ),
                score=max(0, min(100, score)),
            )
        )

    return normalized


def _heuristic_score(answer: str) -> int:
    """Score simple para fallback cuando el modelo no devuelve JSON usable."""
    words = len(answer.split())
    score = 35
    if words >= 20:
        score += 20
    if words >= 45:
        score += 15
    if any(k in answer.lower() for k in ["ejemplo", "impacto", "resultado", "metrica"]):
        score += 15
    if any(k in answer.lower() for k in ["porque", "trade-off", "riesgo", "decision"]):
        score += 10
    return max(0, min(100, score))


def _build_fallback_evaluation(pairs: list[dict[str, Any]]) -> EvaluationResponse:
    """Genera evaluacion deterministica para no romper flujo de producto."""
    feedback_items: list[FeedbackItem] = []

    for idx, pair in enumerate(pairs, start=1):
        answer = pair["answer"]
        score = _heuristic_score(answer)
        long_enough = len(answer.split()) >= 25

        feedback_items.append(
            FeedbackItem(
                question_number=idx,
                question=pair["question"],
                answer=answer,
                strengths=[
                    "La respuesta mantiene una linea argumental clara.",
                    "Se entiende el enfoque tecnico general.",
                ],
                gaps=[
                    "Falto mas precision en decisiones tecnicas y trade-offs.",
                    "Conviene cerrar con resultados medibles del ejemplo.",
                ],
                recommendation=(
                    "Usa el marco situacion-accion-resultado e incluye una metrica final."
                    if long_enough
                    else "Amplia la respuesta con contexto, decision tecnica y resultado cuantificable."
                ),
                score=score,
            )
        )

    overall = (
        int(sum(item.score for item in feedback_items) / len(feedback_items))
        if feedback_items
        else 50
    )

    return EvaluationResponse(
        feedback_items=feedback_items,
        overall_score=overall,
        summary="Evaluacion generada con modo robusto para mantener continuidad y tiempos de respuesta.",
    )


@router.get("/status", response_model=AiStatusResponse)
async def ai_status() -> AiStatusResponse:
    """Informa si la instancia local de Ollama esta disponible."""
    # Expone configuracion activa y disponibilidad para diagnostico rapido.
    return AiStatusResponse(
        configured_model=ollama_client.model,
        ollama_base_url=ollama_client.base_url,
        reachable=await ollama_client.is_reachable(),
    )


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(payload: ChatRequest) -> ChatResponse:
    """Responde un mensaje usando el modelo local configurado."""
    compact_message = _compact_text(payload.message, MAX_CHAT_CONTEXT_CHARS)

    try:
        # Usa salida corta para reducir latencia en repreguntas.
        async with MODEL_GATE:
            reply = await ollama_client.generate(
                message=compact_message,
                system_prompt=payload.system_prompt,
                temperature=0.15,
                top_p=0.9,
                num_predict=220,
            )
    except Exception:
        try:
            # Reintento unico con salida aun mas corta para mitigar fallos transitorios.
            async with MODEL_GATE:
                reply = await ollama_client.generate(
                    message=_compact_text(compact_message, 1800),
                    system_prompt=payload.system_prompt,
                    temperature=0.1,
                    top_p=0.85,
                    num_predict=140,
                )
        except Exception:
            # No rompe el flujo: devuelve repregunta util en modo resiliente.
            reply = (
                "[modo resiliente] "
                + _build_fallback_chat_reply(compact_message)
            )

    # Devuelve texto y modelo usado para trazabilidad en UI.
    return ChatResponse(model=ollama_client.model, reply=reply)


@router.post("/evaluate", response_model=EvaluationResponse)
async def ai_evaluate(payload: EvaluationRequest) -> EvaluationResponse:
    """Evalua el transcript del chat y genera feedback estructurado por respuesta."""
    pairs = _extract_qa_pairs(payload.transcript)
    if not pairs:
        raise HTTPException(
            status_code=400,
            detail="No se detectaron pares pregunta/respuesta validos para evaluar.",
        )

    context = _compact_text(
        payload.interview_context or "General technical interview",
        220,
    )

    # Si Ollama no esta disponible, responde inmediato con fallback estable.
    if not await ollama_client.is_reachable():
        return _build_fallback_evaluation(pairs)

    # Intento 1: JSON mode con prompt estricto y salida corta (mas rapido y estable).
    try:
        async with MODEL_GATE:
            strict_reply = await ollama_client.generate(
                message=_build_eval_prompt(context, pairs, strict=True),
                format="json",
                temperature=0.1,
                top_p=0.85,
                num_predict=650,
            )
        data = _extract_json_object(strict_reply)
        feedback_items = _normalize_feedback_items(data.get("feedback_items"), pairs)
        overall_score = data.get(
            "overall_score",
            int(sum(item.score for item in feedback_items) / len(feedback_items)),
        )
        try:
            overall_score = int(overall_score)
        except (TypeError, ValueError):
            overall_score = int(sum(item.score for item in feedback_items) / len(feedback_items))

        summary = _compact_text(
            str(
                data.get(
                    "summary",
                    "Evaluacion completada con salida estructurada.",
                )
            ),
            280,
        )

        return EvaluationResponse(
            feedback_items=feedback_items,
            overall_score=max(0, min(100, overall_score)),
            summary=summary,
        )
    except Exception:
        # Intento 2: sin JSON mode pero prompt compacto para mayor tolerancia.
        try:
            async with MODEL_GATE:
                relaxed_reply = await ollama_client.generate(
                    message=_build_eval_prompt(context, pairs, strict=False),
                    temperature=0.15,
                    top_p=0.9,
                    num_predict=700,
                )
            data = _extract_json_object(relaxed_reply)
            feedback_items = _normalize_feedback_items(data.get("feedback_items"), pairs)
            overall_score = int(
                data.get(
                    "overall_score",
                    sum(item.score for item in feedback_items) / len(feedback_items),
                )
            )
            summary = _compact_text(str(data.get("summary", "Evaluacion completada.")), 280)

            return EvaluationResponse(
                feedback_items=feedback_items,
                overall_score=max(0, min(100, overall_score)),
                summary=summary,
            )
        except Exception:
            # Fallback deterministico: evita errores 5xx y mantiene UX funcional.
            return _build_fallback_evaluation(pairs)
