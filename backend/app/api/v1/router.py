"""Router principal versionado de la API v1.

Aqui se iran agregando los routers de entrevistas, preguntas, evaluacion y reportes.
"""

from fastapi import APIRouter

from app.api.v1.ai import router as ai_router
from app.api.v1.interviews import router as interviews_router

api_v1_router = APIRouter()
# Monta endpoints de IA bajo /api/v1/ai.
api_v1_router.include_router(ai_router, prefix="/ai")
# Monta flujo orquestado de entrevista bajo /api/v1/interviews.
api_v1_router.include_router(interviews_router, prefix="/interviews")
