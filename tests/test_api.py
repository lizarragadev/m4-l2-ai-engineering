import os
from fastapi.testclient import TestClient

# El workflow configura LLM_MODO_SIMULADO=true antes de importar app.
from app import app

KEY = "oa_lucia_demo_2026_key_7f3a91"


def test_health_and_ready():
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/ready").status_code == 200


def test_auth_required():
    with TestClient(app) as client:
        response = client.post("/v1/consultas", json={"mensaje": "¿Cómo viene OA1203?"})
        assert response.status_code == 401
        assert response.headers.get("www-authenticate") == "Bearer"


def test_consulta_end_to_end_mock():
    with TestClient(app) as client:
        response = client.post("/v1/consultas", headers={"Authorization": f"Bearer {KEY}"},
                               json={"mensaje": "¿Cómo viene el vuelo OA1203?"})
        assert response.status_code == 200
        assert response.json()["derivado"] is True
        assert "OA1203" in response.json()["respuesta"]
