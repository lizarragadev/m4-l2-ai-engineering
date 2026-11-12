import logging
import json
import time
from uuid import uuid4
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from api.configuracion import APP_VERSION, DATA_FILE, settings
from api.config import validar_secretos, resumen_seguro
from api.rutas import router
from api.errores_http import registrar_manejadores

logger = logging.getLogger("orbitair")


@asynccontextmanager
async def lifespan(app: FastAPI):
    problemas = validar_secretos(settings)
    if problemas:
        raise RuntimeError("Configuración inválida: " + "; ".join(problemas))
    logger.info("Configuración de arranque: %s", resumen_seguro(settings))
    yield


app = FastAPI(title="OrbitAir API", version=APP_VERSION,
              description="API de demostración: agente de vuelos con autenticación y streaming.",
              lifespan=lifespan)
registrar_manejadores(app)
app.include_router(router)


@app.middleware("http")
async def registrar_peticion(request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id
    inicio = time.perf_counter()
    response = await call_next(request)
    duracion_ms = round((time.perf_counter() - inicio) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(json.dumps({"evento": "http_request", "request_id": request_id,
                            "metodo": request.method, "ruta": request.url.path,
                            "status_code": response.status_code, "duracion_ms": duracion_ms},
                           ensure_ascii=False))
    return response


@app.get("/health", tags=["Estado"])
def health():
    return {"status": "ok"}


@app.get("/ready", tags=["Estado"])
def ready():
    problemas = validar_secretos(settings)
    if not DATA_FILE.is_file():
        problemas.append("CSV de vuelos no encontrado")
    if problemas:
        return JSONResponse(status_code=503, content={"status": "not_ready", "checks": problemas})
    return {"status": "ready", "checks": {"configuracion": "ok", "datos": "ok"}}


@app.get("/version", tags=["Estado"])
def version():
    return {"version": APP_VERSION}
