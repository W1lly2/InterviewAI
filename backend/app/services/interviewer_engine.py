"""Motor de entrevista: genera solo la siguiente intervencion del entrevistador."""

from app.services.ollama_client import OllamaClient


def _compact_text(value: str, limit: int) -> str:
    compact = " ".join(str(value or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: max(0, limit - 1)].rstrip() + "…"


def _build_fallback_follow_up(missing: list[str], last_answer: str, stage: int) -> str:
    base = _compact_text(last_answer, 180)
    if stage == 0:
        focus = []
        if "tradeoff_missing" in missing:
            focus.append("trade-off elegido")
        if "risk_missing" in missing:
            focus.append("riesgo mitigado")
        if "metric_missing" in missing:
            focus.append("metrica mejorada")
        if "example_missing" in missing:
            focus.append("ejemplo concreto")

        if not focus:
            focus = ["decision tecnica", "riesgo", "resultado medible"]

        return (
            "[contingencia] Para profundizar en tu respuesta, explicame brevemente: "
            + ", ".join(focus)
            + f". Base: \"{base}\""
        )

    if stage == 1:
        return (
            "[contingencia] Dame un cierre STAR en 4-5 lineas: situacion, accion, resultado "
            "y una metrica final."
        )

    return "[contingencia] Tu respuesta ya es suficiente para esta pregunta. Avancemos a la siguiente."


class InterviewerEngine:
    """Encapsula la generacion de repreguntas del entrevistador."""

    def __init__(self, ollama_client: OllamaClient) -> None:
        self._client = ollama_client

    async def generate_follow_up(
        self,
        *,
        question: str,
        last_answer: str,
        context_summary: str,
        missing_dimensions: list[str],
        stage: int,
        role_context: str,
    ) -> tuple[str, str, int]:
        """Genera una repregunta puntual. Retorna (texto, source, latencia_ms)."""
        import time

        dims = ", ".join(missing_dimensions) if missing_dimensions else "none"
        prompt = f"""You are a technical interviewer for {role_context}.
Current question:
{_compact_text(question, 300)}

Candidate last answer:
{_compact_text(last_answer, 600)}

Interview summary:
{_compact_text(context_summary, 300)}

Stage: {stage}
Missing dimensions: {dims}

Task:
- Ask ONE concise follow-up question in Spanish.
- Focus only on missing dimensions.
- Keep under 45 words.
- Do not explain evaluation, only ask the question.
"""

        started = time.perf_counter()
        try:
            reply = await self._client.generate(
                message=prompt,
                system_prompt="Entrevistador tecnico. Salida breve y concreta.",
                temperature=0.1,
                top_p=0.85,
                num_predict=120,
            )
            latency_ms = int((time.perf_counter() - started) * 1000)
            return (_compact_text(reply, 380), "ai", latency_ms)
        except Exception:
            latency_ms = int((time.perf_counter() - started) * 1000)
            return (
                _build_fallback_follow_up(missing_dimensions, last_answer, stage),
                "fallback",
                latency_ms,
            )
