import logging
from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import RateLimitError

logger = logging.getLogger("orbitair")


class ErrorHTTP(Exception):
    def __init__(self, status_code: int, codigo: str, mensaje: str, headers: dict | None = None):
        self.status_code = status_code
        self.codigo = codigo
        self.mensaje = mensaje
        self.headers = headers or {}


def cuerpo_error(codigo: str, mensaje: str, request_id: str) -> dict:
    return {"error": {"codigo": codigo, "mensaje": mensaje, "request_id": request_id}}


def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(ErrorHTTP)
    async def manejar_error_http(request: Request, exc: ErrorHTTP):
        request_id = getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID") or str(uuid4())
        return JSONResponse(status_code=exc.status_code,
                            content=cuerpo_error(exc.codigo, exc.mensaje, request_id),
                            headers=exc.headers)

    @app.exception_handler(Exception)
    async def manejar_error_general(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID") or str(uuid4())
        logger.exception("Error no controlado request_id=%s", request_id)
        return JSONResponse(status_code=500,
                            content=cuerpo_error("ERROR_INTERNO", "Ocurrió un error interno.", request_id))


def traducir_error(exc: Exception) -> ErrorHTTP:
    if isinstance(exc, RateLimitError):
        return ErrorHTTP(503, "PROVEEDOR_NO_DISPONIBLE",
                         "El servicio de IA está temporalmente ocupado. Intenta nuevamente.",
                         headers={"Retry-After": "5"})
    return ErrorHTTP(502, "ERROR_PROVEEDOR", "No fue posible completar la consulta con el proveedor de IA.")
