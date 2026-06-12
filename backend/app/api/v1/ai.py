"""Endpoints iniciales para probar IA local con Ollama."""

from fastapi import APIRouter, HTTPException

from app.schemas.ai import AiStatusResponse, ChatRequest, ChatResponse
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
