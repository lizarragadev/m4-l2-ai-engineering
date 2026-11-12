#!/usr/bin/env python3
"""Ejecuta un ejemplo de la regla de promoción de releases."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api.releases import decidir_promocion

if __name__ == "__main__":
    ejemplo = [
        {"nombre": "/health", "ok": True, "critico": True},
        {"nombre": "/ready", "ok": True, "critico": True},
        {"nombre": "401 sin key", "ok": True, "critico": True},
        {"nombre": "consulta real", "ok": False, "critico": True},
        {"nombre": "latencia", "ok": True, "critico": False},
    ]
    decision = decidir_promocion(ejemplo)
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    sys.exit(0 if decision["promover"] else 1)
