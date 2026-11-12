"""Configuración tipada y validación de secretos para OrbitAir."""
import os
from pathlib import Path
from pydantic import BaseModel, SecretStr

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseModel):
    app_env: str = "local"
    openai_api_key: SecretStr = SecretStr("")
    openai_model: str = "gpt-4.1-mini"
    llm_modo_simulado: bool = False
    app_version: str = "1.0.0"
    git_commit: str = "dev"
    port: int = 8000

    @classmethod
    def desde_entorno(cls) -> "Settings":
        """Construye Settings desde variables de entorno ya cargadas."""
        return cls(
            app_env=os.getenv("APP_ENV", "local").strip().lower(),
            openai_api_key=SecretStr(os.getenv("OPENAI_API_KEY", "").strip()),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip(),
            llm_modo_simulado=os.getenv("LLM_MODO_SIMULADO", "false").strip().lower() in {"1", "true", "yes", "si"},
            app_version=os.getenv("APP_VERSION", "1.0.0").strip(),
            git_commit=os.getenv("GIT_COMMIT", "dev").strip(),
            port=int(os.getenv("PORT", "8000")),
        )


def validar_secretos(config: Settings) -> list[str]:
    """Devuelve problemas de configuración sin imprimir valores secretos."""
    problemas: list[str] = []
    clave = config.openai_api_key.get_secret_value().strip()
    if config.app_env == "produccion" and config.llm_modo_simulado:
        problemas.append("LLM_MODO_SIMULADO no está permitido en producción")
    if not config.llm_modo_simulado and not clave:
        problemas.append("OPENAI_API_KEY es obligatoria cuando el modo simulado está desactivado")
    if config.app_env not in {"local", "test", "produccion"}:
        problemas.append("APP_ENV debe ser local, test o produccion")
    return problemas


def resumen_seguro(config: Settings) -> dict:
    """Resumen apto para logs: informa presencia, nunca revela el secreto."""
    clave = config.openai_api_key.get_secret_value().strip()
    return {
        "app_env": config.app_env,
        "openai_model": config.openai_model,
        "openai_api_key": "configurada" if clave else "ausente",
        "llm_modo_simulado": config.llm_modo_simulado,
        "git_commit": config.git_commit,
    }

