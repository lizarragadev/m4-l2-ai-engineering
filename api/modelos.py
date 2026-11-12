from pydantic import BaseModel, ConfigDict, Field


class ConsultaIn(BaseModel):
    """Contrato de entrada: solo acepta los campos declarados."""
    model_config = ConfigDict(extra="forbid")

    mensaje: str = Field(min_length=3, max_length=2000)
    sesion_id: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9-]{36}$",
        description="Identificador UUID de una conversación existente",
    )


class RespuestaOut(BaseModel):
    """Contrato público de salida; no expone historial ni argumentos internos."""
    respuesta: str
    sesion_id: str
    derivado: bool = False
