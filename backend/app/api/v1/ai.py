"""Endpoints iniciales para probar IA local con Ollama."""

import json

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
    try:
        # Delega la generacion al cliente de infraestructura.
        reply = await ollama_client.chat(
            message=payload.message,
            system_prompt=payload.system_prompt,
        )
    except Exception as exc:  # pragma: no cover
        # Traduce fallos de proveedor a un error HTTP entendible por frontend.
        raise HTTPException(
            status_code=503,
            detail=(
                "No se pudo obtener respuesta de Ollama. "
                "Verifica que este activo y que el modelo este descargado."
            ),
        ) from exc

    # Devuelve texto y modelo usado para trazabilidad en UI.
    return ChatResponse(model=ollama_client.model, reply=reply)


@router.post("/evaluate", response_model=EvaluationResponse)
async def ai_evaluate(payload: EvaluationRequest) -> EvaluationResponse:
    """Evalua el transcript del chat y genera feedback estructurado por respuesta."""
    try:
        # Construye contexto del transcript para el evaluador IA.
        transcript_text = "\n".join(
            [f"[{msg['role']}]: {msg['content']}" for msg in payload.transcript]
        )

        # Prompt que pide a Ollama analizar y devolver JSON con evaluaciones.
        eval_prompt = f"""Evaluate the following interview transcript and provide structured feedback for each Q&A pair.
Context: {payload.interview_context or "General technical interview"}

Transcript:
{transcript_text}

For each question-answer pair, analyze:
1. Strengths (max 3 key points)
2. Gaps or areas for improvement (max 3 key points)
3. A specific, actionable recommendation
4. A score from 0-100

Return a JSON object with:
- "feedback_items": array of objects with: question_number, question, answer, strengths, gaps, recommendation, score
- "overall_score": average score (0-100)
- "summary": brief executive summary

Return ONLY valid JSON, no markdown or extra text."""

        # Solicita análisis a Ollama.
        reply = await ollama_client.chat(message=eval_prompt, system_prompt=None)

        # Intenta parsear JSON de la respuesta.
        # Extrae JSON del response (Ollama a veces agrega texto extra).
        json_start = reply.find("{")
        json_end = reply.rfind("}") + 1
        if json_start == -1 or json_end <= json_start:
            raise ValueError("No se encontro JSON en la respuesta del modelo")

        json_str = reply[json_start:json_end]
        data = json.loads(json_str)

        # Extrae feedback items de la respuesta.
        feedback_items = []
        for item in data.get("feedback_items", data.get("items", [])):
            feedback_items.append(
                FeedbackItem(
                    question_number=item.get("question_number", 0),
                    question=item.get("question", ""),
                    answer=item.get("answer", ""),
                    strengths=item.get("strengths", []),
                    gaps=item.get("gaps", []),
                    recommendation=item.get("recommendation", ""),
                    score=max(0, min(100, item.get("score", 50))),
                )
            )

        # Calcula overall score si no viene en la respuesta.
        overall_score = data.get(
            "overall_score",
            int(sum(f.score for f in feedback_items) / len(feedback_items))
            if feedback_items
            else 50,
        )

    except json.JSONDecodeError as exc:
        # Si falla el parseo, devuelve error clara.
        raise HTTPException(
            status_code=400,
            detail="El modelo no retorno un JSON valido. Intenta de nuevo.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Error al evaluar: {str(exc)}",
        ) from exc

    return EvaluationResponse(
        feedback_items=feedback_items,
        overall_score=overall_score,
        summary=data.get("summary", "Evaluacion completada."),
    )
