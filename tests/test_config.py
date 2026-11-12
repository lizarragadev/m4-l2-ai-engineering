from pydantic import SecretStr
from api.config import Settings, validar_secretos, resumen_seguro


def test_local_requires_key_when_not_mocked():
    cfg = Settings(app_env="local", openai_api_key=SecretStr(""), llm_modo_simulado=False)
    assert any("OPENAI_API_KEY" in p for p in validar_secretos(cfg))


def test_simulation_allowed_locally():
    cfg = Settings(app_env="test", openai_api_key=SecretStr(""), llm_modo_simulado=True)
    assert validar_secretos(cfg) == []


def test_simulation_forbidden_in_production():
    cfg = Settings(app_env="produccion", openai_api_key=SecretStr(""), llm_modo_simulado=True)
    assert any("no está permitido" in p for p in validar_secretos(cfg))


def test_safe_summary_never_contains_secret():
    cfg = Settings(app_env="produccion", openai_api_key=SecretStr("sk-secret-value"), llm_modo_simulado=False)
    resumen = str(resumen_seguro(cfg))
    assert "sk-secret-value" not in resumen
    assert "configurada" in resumen


def test_production_requires_real_key_and_disallows_mock():
    cfg = Settings(app_env="produccion", openai_api_key=SecretStr("sk-valid-placeholder"), llm_modo_simulado=True)
    assert any("no está permitido" in p for p in validar_secretos(cfg))
