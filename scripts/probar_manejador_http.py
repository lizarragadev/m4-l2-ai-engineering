"""Prueba los manejadores HTTP sin iniciar el servidor ni llamar a OpenAI."""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.errores_http import ErrorHTTP, registrar_manejadores

app_demo = FastAPI()
registrar_manejadores(app_demo)


@app_demo.get("/error-controlado")
def error_controlado():
    raise ErrorHTTP(503, "DEMO_CONTROLADO", "Mensaje seguro para el consumidor.")


@app_demo.get("/error-interno")
def error_interno():
    raise RuntimeError("Fallo de conexión postgresql://app:CLAVE-FALSA@db.interna:5432/vuelos")


cliente = TestClient(app_demo, raise_server_exceptions=False)
for ruta in ("/error-controlado", "/error-interno"):
    respuesta = cliente.get(ruta, headers={"X-Request-ID": "demo-request-001"})
    print(ruta, "HTTP", respuesta.status_code)
    print(respuesta.json())
