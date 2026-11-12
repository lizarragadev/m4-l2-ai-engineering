"""Ejecuta el mismo agente directamente desde la terminal, sin HTTP."""
import sys
from api.agente import ejecutar_agente
from api.servicios import crear_servicio

mensaje = " ".join(sys.argv[1:]) or "¿Cómo viene el vuelo OA1203?"
servicio = crear_servicio()
historial = []
resultado = ejecutar_agente(servicio, mensaje, "P-1001", historial)
print(resultado["respuesta"])
print("Derivó a herramienta:", resultado["derivado"])
