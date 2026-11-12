import hashlib
import hmac
import json
import os
from uuid import uuid4
from fastapi import Depends, Header, HTTPException
from api.configuracion import CLIENTS_FILE, settings
from api.servicios import ServicioOrbitAir, crear_servicio

_SESIONES: dict[str, dict] = {}


def obtener_servicio() -> ServicioOrbitAir:
    return crear_servicio()


def obtener_cliente(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Se requiere una API key Bearer",
                            headers={"WWW-Authenticate": "Bearer"})
    clave = authorization.removeprefix("Bearer ").strip()
    huella = hashlib.sha256(clave.encode()).hexdigest()
    clientes = json.loads(CLIENTS_FILE.read_text(encoding="utf-8"))
    for cliente_id, datos in clientes.items():
        variable = "DEMO_API_KEY_KIOSCO" if cliente_id == "kiosco-aep" else "DEMO_API_KEY_" + cliente_id.upper().replace("-", "_")
        clave_configurada = os.getenv(variable, "")
        if settings.app_env == "produccion" and not clave_configurada:
            continue
        huella_esperada = hashlib.sha256(clave_configurada.encode()).hexdigest() if clave_configurada else datos["key_sha256"]
        if hmac.compare_digest(huella, huella_esperada):
            return {"cliente_id": cliente_id, **datos}
    raise HTTPException(status_code=401, detail="API key inválida",
                        headers={"WWW-Authenticate": "Bearer"})


def obtener_sesion(sesion_id: str | None, cliente: dict) -> tuple[str, list[dict]]:
    if sesion_id is None:
        nuevo_id = str(uuid4())
        _SESIONES[nuevo_id] = {"cliente_id": cliente["cliente_id"], "historial": []}
        return nuevo_id, _SESIONES[nuevo_id]["historial"]
    sesion = _SESIONES.get(sesion_id)
    if sesion is None or sesion["cliente_id"] != cliente["cliente_id"]:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return sesion_id, sesion["historial"]


def limpiar_sesiones() -> None:
    """Utilidad para pruebas locales; no se expone como endpoint."""
    _SESIONES.clear()
