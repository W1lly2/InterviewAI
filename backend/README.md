# Backend - FastAPI

Este backend se organiza por capas para mantener el codigo limpio y escalable.

## Carpetas

- app/api/v1: endpoints versionados.
- app/core: configuracion, seguridad y utilidades globales.
- app/models: entidades de dominio/persistencia.
- app/schemas: contratos de entrada/salida (Pydantic).
- app/services: logica de negocio (preguntas, evaluacion, reportes).

## Flujo de dominio esperado

1. Entrevista configurada por el frontend.
2. Servicio de generacion de preguntas segun puesto y seniority.
3. Conversacion guiada por IA con contexto acumulado.
4. Evaluacion por rubrica y competencias.
5. Generacion de reporte final con fortalezas y mejoras.
