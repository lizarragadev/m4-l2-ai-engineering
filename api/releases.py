"""Reglas de promoción de releases a partir de resultados de smoke tests."""


def decidir_promocion(resultados: list[dict]) -> dict:
    """No promueve si al menos una comprobación crítica falla."""
    fallos = [r for r in resultados if r.get("critico", True) and not r.get("ok", False)]
    return {
        "promover": not fallos,
        "fallos_criticos": fallos,
        "decision": "PROMOVER" if not fallos else "NO PROMOVER",
    }
