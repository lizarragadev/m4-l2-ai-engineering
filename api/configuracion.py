"""Compatibilidad con L1 y carga centralizada de variables de entorno."""
from dotenv import load_dotenv
from api.config import BASE_DIR
load_dotenv(BASE_DIR / ".env")
from api.config import Settings  # noqa: E402
settings = Settings.desde_entorno()
OPENAI_API_KEY = settings.openai_api_key.get_secret_value()
OPENAI_MODEL = settings.openai_model
APP_VERSION = settings.git_commit if settings.git_commit != "dev" else settings.app_version
DATA_FILE = BASE_DIR / "data" / "vuelos.csv"
CLIENTS_FILE = BASE_DIR / "api" / "clientes.json"
