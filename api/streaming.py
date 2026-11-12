import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
from typing import AsyncIterator

_EXECUTOR = ThreadPoolExecutor(max_workers=4)


def evento_sse(tipo: str, datos: dict) -> str:
    """Serializa un evento SSE: event, data y línea vacía final."""
    return f"event: {tipo}\ndata: {json.dumps(datos, ensure_ascii=False)}\n\n"


def correr_en_hilo(funcion, *args, **kwargs) -> tuple[Queue, object]:
    """Ejecuta una función síncrona y envía sus eventos a una cola."""
    cola: Queue = Queue()
    def callback(evento):
        cola.put(evento)
    def trabajo():
        try:
            resultado = funcion(*args, al_evento=callback, **kwargs)
            cola.put({"_resultado": resultado})
        except Exception as exc:
            cola.put({"_error": exc})
    futuro = _EXECUTOR.submit(trabajo)
    return cola, futuro


async def iterar_eventos(cola: Queue, futuro) -> AsyncIterator[dict]:
    """Lee la cola sin bloquear el event loop de FastAPI."""
    while True:
        try:
            elemento = await asyncio.to_thread(cola.get, True, 0.25)
        except Empty:
            if futuro.done() and cola.empty():
                break
            continue
        yield elemento
        if "_resultado" in elemento or "_error" in elemento:
            break
