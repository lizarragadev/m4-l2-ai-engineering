from api.releases import decidir_promocion


def test_critical_failure_blocks_promotion():
    decision = decidir_promocion([
        {"nombre": "health", "ok": True, "critico": True},
        {"nombre": "consulta", "ok": False, "critico": True},
        {"nombre": "latencia", "ok": False, "critico": False},
    ])
    assert decision["promover"] is False
    assert decision["decision"] == "NO PROMOVER"


def test_warning_does_not_block_promotion():
    decision = decidir_promocion([
        {"nombre": "health", "ok": True, "critico": True},
        {"nombre": "latencia", "ok": False, "critico": False},
    ])
    assert decision["promover"] is True
