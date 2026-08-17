import json
import logging
import time
import uuid
from datetime import UTC, datetime

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.lecturas import router as lecturas_router
from app.errores import ErrorAPI

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("mimedidor")

app = FastAPI(title="MiMedidor API")
app.include_router(lecturas_router)


@app.get("/api/salud")
def salud() -> dict[str, str]:
    """Endpoint mínimo para que el pipeline de CI (T-05) tenga algo real que probar."""
    return {"estado": "ok"}


@app.middleware("http")
async def registrar_peticion(request: Request, call_next):
    """Logs estructurados a stdout desde el primer endpoint real (T-15) — momento, ruta, código
    de respuesta, duración e id de petición. Nunca la imagen completa ni datos personales.
    """
    id_peticion = str(uuid.uuid4())
    inicio = time.perf_counter()
    respuesta = await call_next(request)
    duracion_ms = round((time.perf_counter() - inicio) * 1000, 2)
    logger.info(
        json.dumps(
            {
                "momento": datetime.now(UTC).isoformat(),
                "ruta": request.url.path,
                "metodo": request.method,
                "codigo_respuesta": respuesta.status_code,
                "duracion_ms": duracion_ms,
                "id_peticion": id_peticion,
            }
        )
    )
    return respuesta


@app.exception_handler(ErrorAPI)
async def manejar_error_api(request: Request, exc: ErrorAPI) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"codigo": exc.codigo, "mensaje": exc.mensaje}},
    )


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "codigo": "VALIDACION",
                "mensaje": "El cuerpo de la petición no cumple el formato esperado",
            }
        },
    )


@app.exception_handler(Exception)
async def manejar_error_interno(request: Request, exc: Exception) -> JSONResponse:
    """Nunca exponer trazas internas ni detalles del motor de base de datos en la respuesta
    (CLAUDE.md §11) — el detalle completo va al log, al cliente solo el código genérico.
    """
    logger.exception("Error interno no manejado en %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "codigo": "ERROR_INTERNO",
                "mensaje": "Ocurrió un error inesperado",
            }
        },
    )
