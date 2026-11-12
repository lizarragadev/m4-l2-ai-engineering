#!/usr/bin/env python3
"""Smoke test no destructivo para una URL OrbitAir desplegada."""
import argparse
import os
import sys
import time
from pathlib import Path
import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")
sys.path.insert(0, str(PROJECT_ROOT))
from api.releases import decidir_promocion

KEY = os.getenv("DEMO_API_KEY_WEB_LUCIA", "oa_lucia_demo_2026_key_7f3a91")


def verificar_deploy(base_url: str) -> list[dict]:
    """Ejecuta todos los checks y devuelve resultados sin detenerse al primer fallo."""
    base = base_url.rstrip("/")
    resultados: list[dict] = []

    def comprobar(nombre, funcion, critico=True):
        inicio = time.perf_counter()
        try:
            ok, detalle = funcion()
        except Exception as exc:
            ok, detalle = False, f"{type(exc).__name__}: {exc}"
        ms = (time.perf_counter() - inicio) * 1000
        resultados.append({"nombre": nombre, "ok": bool(ok), "critico": critico,
                           "detalle": f"{detalle}; {ms:.0f} ms"})

    def get_status(path, esperado, campo, valor):
        response = requests.get(base + path, timeout=15)
        try:
            body = response.json()
        except ValueError:
            body = {}
        return response.status_code == esperado and body.get(campo) == valor, f"HTTP {response.status_code}"

    comprobar("GET /health", lambda: get_status("/health", 200, "status", "ok"))
    comprobar("GET /ready", lambda: get_status("/ready", 200, "status", "ready"))

    def sin_key():
        r = requests.post(base + "/v1/consultas", json={"mensaje": "¿Cómo viene OA1203?"}, timeout=20)
        return r.status_code == 401, f"HTTP {r.status_code}"
    comprobar("401 sin API key", sin_key)

    def consulta_completa():
        r = requests.post(base + "/v1/consultas", headers={"Authorization": f"Bearer {KEY}"},
                          json={"mensaje": "¿Cómo viene el vuelo OA1203?"}, timeout=75)
        try:
            body = r.json()
        except ValueError:
            body = {}
        ok = r.status_code == 200 and "OA1203" in body.get("respuesta", "")
        return ok, f"HTTP {r.status_code}; respuesta contiene OA1203={ok}"
    comprobar("Consulta real de punta a punta", consulta_completa)

    def latencia():
        inicio = time.perf_counter(); r = requests.get(base + "/health", timeout=15)
        ms = (time.perf_counter() - inicio) * 1000
        return r.status_code == 200 and ms < 1500, f"HTTP {r.status_code}; umbral orientativo 1500 ms"
    comprobar("Latencia de /health", latencia, critico=False)

    def stream():
        with requests.get(base + "/v1/consultas/stream", params={"mensaje": "¿Cómo viene OA1203?"},
                          headers={"Authorization": f"Bearer {KEY}"}, stream=True, timeout=(15, 75)) as r:
            eventos = []
            for linea in r.iter_lines(decode_unicode=True):
                if linea and linea.startswith("event:"):
                    eventos.append(linea.removeprefix("event: "))
                    if eventos[-1] in {"fin", "error"}:
                        break
            correcto = r.status_code == 200 and len(eventos) >= 2 and eventos[0] == "inicio" and eventos[-1] == "fin"
            return correcto, f"HTTP {r.status_code}; secuencia={eventos}"
    comprobar("SSE: secuencia completa de progreso", stream, critico=False)
    return resultados


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", help="URL pública, por ejemplo https://orbitair.up.railway.app")
    args = parser.parse_args()
    resultados = verificar_deploy(args.base_url)
    print("\nRESULTADOS DEL SMOKE TEST")
    for resultado in resultados:
        nivel = "CRITICO" if resultado["critico"] else "AVISO"
        estado = "OK" if resultado["ok"] else "FALLO"
        print(f"[{nivel}] {resultado['nombre']}: {estado} · {resultado['detalle']}")
    decision = decidir_promocion(resultados)
    fallos_criticos = len(decision["fallos_criticos"])
    fallos_aviso = sum(1 for r in resultados if not r["ok"] and not r["critico"])
    print(f"\nResumen: {fallos_criticos} fallo(s) crítico(s), {fallos_aviso} aviso(s).")
    print(f"Decisión del release: {decision['decision']}")
    return 1 if not decision["promover"] else 0


if __name__ == "__main__":
    sys.exit(main())
