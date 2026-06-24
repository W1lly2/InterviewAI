"""Motor de evaluacion: analiza respuestas estructuradas por pregunta."""

import json
from typing import Any

from app.schemas.ai import EvaluationResponse, FeedbackItem
from app.services.ollama_client import OllamaClient


class EvaluationEngine:
    """Evalua entrevista por bloques, separado de la conversacion."""

    def __init__(self, ollama_client: OllamaClient) -> None:
        self._client = ollama_client

    @staticmethod
    def _compact_text(value: str, limit: int) -> str:
        compact = " ".join(str(value or "").split())
        if len(compact) <= limit:
            return compact
        return compact[: max(0, limit - 1)].rstrip() + "…"

    @staticmethod
    def _heuristic_score(answer: str) -> int:
        words = len(answer.split())
        score = 38
        if words >= 25:
            score += 18
        if words >= 45:
            score += 15
        if any(k in answer.lower() for k in ["trade-off", "riesgo", "decision", "arquitectura"]):
            score += 12
        if any(k in answer.lower() for k in ["metrica", "impacto", "resultado", "kpi", "p95"]):
            score += 12
        return max(0, min(100, score))

    def _fallback(self, pairs: list[dict[str, str]]) -> EvaluationResponse:
        items: list[FeedbackItem] = []
        for idx, pair in enumerate(pairs, start=1):
            score = self._heuristic_score(pair["answer"])
            items.append(
                FeedbackItem(
                    question_number=idx,
                    question=pair["question"],
                    answer=pair["answer"],
                    strengths=[
                        "La respuesta mantiene una narrativa clara.",
                        "Se aprecia criterio tecnico en el enfoque.",
                    ],
                    gaps=[
                        "Conviene explicitar mejor trade-offs y riesgos.",
                        "Falto cerrar con metrica final mas concreta.",
                    ],
                    recommendation="Cierra cada ejemplo con decision tecnica, riesgo mitigado y metrica antes/despues.",
                    score=score,
                )
            )

        overall = int(sum(item.score for item in items) / len(items)) if items else 50
        return EvaluationResponse(
            feedback_items=items,
            overall_score=overall,
            summary="Evaluacion generada en modo robusto para mantener continuidad de la sesion.",
        )

    @staticmethod
    def _extract_json(raw: str) -> dict[str, Any]:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end <= start:
            raise json.JSONDecodeError("No JSON object found", raw, 0)
        return json.loads(raw[start:end])

    async def evaluate_pairs(self, role_context: str, pairs: list[dict[str, str]]) -> EvaluationResponse:
        """Evalua pares pregunta/respuesta y retorna contrato estable."""
        if not pairs:
            return self._fallback([])

        qa_text = "\n".join(
            [
                f"Q{i + 1}: {self._compact_text(pair['question'], 260)}\n"
                f"A{i + 1}: {self._compact_text(pair['answer'], 700)}"
                for i, pair in enumerate(pairs)
            ]
        )

        prompt = f"""You are an interview evaluator for {role_context}.
Evaluate each Q/A and return ONLY valid JSON with this schema:
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
- Use Spanish text fields.
- Keep exactly {len(pairs)} feedback_items.
- strengths and gaps max 2 each.
- summary <= 280 chars.

Input:
{qa_text}
"""

        try:
            raw = await self._client.generate(
                message=prompt,
                format="json",
                temperature=0.1,
                top_p=0.85,
                num_predict=700,
            )
            data = self._extract_json(raw)
            raw_items = data.get("feedback_items", [])
            if not isinstance(raw_items, list):
                raw_items = []

            items: list[FeedbackItem] = []
            for idx, pair in enumerate(pairs, start=1):
                entry = raw_items[idx - 1] if idx - 1 < len(raw_items) and isinstance(raw_items[idx - 1], dict) else {}
                strengths = entry.get("strengths", [])
                gaps = entry.get("gaps", [])
                if not isinstance(strengths, list):
                    strengths = [str(strengths)]
                if not isinstance(gaps, list):
                    gaps = [str(gaps)]

                try:
                    score = int(entry.get("score", 50))
                except (TypeError, ValueError):
                    score = 50

                items.append(
                    FeedbackItem(
                        question_number=idx,
                        question=self._compact_text(str(entry.get("question", pair["question"])), 260),
                        answer=self._compact_text(str(entry.get("answer", pair["answer"])), 700),
                        strengths=[self._compact_text(str(s), 140) for s in strengths[:2]]
                        or ["Respuesta clara en su estructura base."],
                        gaps=[self._compact_text(str(g), 140) for g in gaps[:2]]
                        or ["Falto mayor especificidad tecnica y metrica."],
                        recommendation=self._compact_text(
                            str(entry.get("recommendation", "Incluye trade-off, riesgo y resultado cuantificable.")),
                            220,
                        ),
                        score=max(0, min(100, score)),
                    )
                )

            if not items:
                return self._fallback(pairs)

            try:
                overall = int(data.get("overall_score", sum(item.score for item in items) / len(items)))
            except (TypeError, ValueError):
                overall = int(sum(item.score for item in items) / len(items))

            if overall <= 0 and items:
                # Si el modelo devuelve 0 espurio, usa promedio real para estabilidad.
                overall = int(sum(item.score for item in items) / len(items))

            summary = self._compact_text(
                str(data.get("summary", "Evaluacion completada.")),
                280,
            )

            return EvaluationResponse(
                feedback_items=items,
                overall_score=max(0, min(100, overall)),
                summary=summary,
            )
        except Exception:
            return self._fallback(pairs)
