import csv
from openai import OpenAI
from api.configuracion import OPENAI_API_KEY, OPENAI_MODEL, DATA_FILE, settings


class ServicioOrbitAir:
    """Agrupa el cliente LLM y el acceso al pequeño conjunto de vuelos."""
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        self.model = OPENAI_MODEL
        self.data_file = DATA_FILE
        self.modo_simulado = settings.llm_modo_simulado

    def consultar_vuelo(self, codigo: str, pasajero_id: str | None) -> dict:
        """Busca un vuelo o reserva y aplica autorización antes de devolver datos."""
        with self.data_file.open("r", encoding="utf-8", newline="") as archivo:
            filas = list(csv.DictReader(archivo))
        for fila in filas:
            coincide_vuelo = fila["codigo"].upper() == codigo.upper()
            coincide_reserva = bool(fila["reserva"]) and fila["reserva"].upper() == codigo.upper()
            if coincide_vuelo or coincide_reserva:
                if coincide_reserva and fila["pasajero_id"] != pasajero_id:
                    return {"autorizado": False, "mensaje": "No tienes autorización para consultar esa reserva."}
                datos = {"autorizado": True, "vuelo": fila["codigo"], "origen": fila["origen"],
                         "destino": fila["destino"], "estado": fila["estado"],
                         "demora_minutos": int(fila["demora_minutos"] or 0),
                         "motivo": fila["motivo"], "hora_salida": fila["hora_salida"]}
                if coincide_reserva:
                    datos["reserva"] = fila["reserva"]
                return datos
        return {"autorizado": True, "encontrado": False, "mensaje": "No se encontró ese vuelo o reserva."}


def crear_servicio() -> ServicioOrbitAir:
    return ServicioOrbitAir()
