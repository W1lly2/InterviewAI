"""Router principal versionado de la API v1.

Aqui se iran agregando los routers de entrevistas, preguntas, evaluacion y reportes.
"""

from fastapi import APIRouter

from app.api.v1.ai import router as ai_router

api_v1_router = APIRouter()
api_v1_router.include_router(ai_router, prefix="/ai")
