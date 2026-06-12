"""Punto de entrada de FastAPI.

Por ahora se deja un endpoint de salud para validar que la API arranca.
"""

from fastapi import FastAPI

from app.api.v1.router import api_v1_router

# Crea la aplicacion HTTP base y metadatos visibles en OpenAPI.
app = FastAPI(
    title="InterviewAI API",
    version="0.1.0",
    description="API para simulador de entrevistas con IA.",
    debug = True
)

# Registro central de rutas versionadas.
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Endpoint simple para comprobar disponibilidad de la API."""
    # Devuelve un estado minimo para probes de salud y monitoreo.
    return {"status": "ok"}
