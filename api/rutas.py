import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from api.modelos import ConsultaIn, RespuestaOut
from api.dependencias import obtener_cliente, obtener_servicio, obtener_sesion
from api.agente import ejecutar_agente
from api.streaming import evento_sse, correr_en_hilo, iterar_eventos
from api.errores_http import ErrorHTTP, traducir_error

router = APIRouter()


@router.post("/v1/consultas", response_model=RespuestaOut)
def crear_consulta(datos: ConsultaIn, cliente: dict = Depends(obtener_cliente),
                   servicio=Depends(obtener_servicio)):
    sesion_id, historial = obtener_sesion(datos.sesion_id, cliente)
    try:
        resultado = ejecutar_agente(servicio, datos.mensaje, cliente["pasajero_id"], historial)
    except Exception as exc:
        raise traducir_error(exc) from exc
    return RespuestaOut(respuesta=resultado["respuesta"], sesion_id=sesion_id,
                        derivado=resultado["derivado"])


@router.get("/v1/consultas/stream")
async def stream_consulta(mensaje: str, sesion_id: str | None = None,
                          forzar_error: bool = False,
                          cliente: dict = Depends(obtener_cliente),
                          servicio=Depends(obtener_servicio)):
    id_sesion, historial = obtener_sesion(sesion_id, cliente)

    if forzar_error:
        async def generar_error_demo():
            yield evento_sse("inicio", {"tipo": "inicio", "mensaje": "Consulta recibida"})
            yield evento_sse("error", {"error": {"codigo": "ERROR_STREAM",
                "mensaje": "Error de demostración después del primer evento.",
                "request_id": "stream-request"}})
        return StreamingResponse(generar_error_demo(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    cola, futuro = correr_en_hilo(ejecutar_agente, servicio, mensaje,
                                  cliente["pasajero_id"], historial)

    async def generar():
        async for elemento in iterar_eventos(cola, futuro):
            if "_error" in elemento:
                error = traducir_error(elemento["_error"])
                yield evento_sse("error", {"error": {"codigo": error.codigo,
                    "mensaje": error.mensaje, "request_id": "stream-request"}})
                return
            if "_resultado" in elemento:
                resultado = elemento["_resultado"]
                yield evento_sse("fin", {"respuesta": resultado["respuesta"],
                                          "sesion_id": id_sesion,
                                          "derivado": resultado["derivado"]})
                return
            yield evento_sse(elemento["tipo"], elemento)
    return StreamingResponse(generar(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.get("/v1/tokens/stream")
def stream_tokens(mensaje: str, cliente: dict = Depends(obtener_cliente),
                        servicio=Depends(obtener_servicio)):
    if servicio.client is None:
        raise ErrorHTTP(503, "IA_NO_CONFIGURADA", "Configura OPENAI_API_KEY para usar el modelo.")
    def generar_tokens():
        try:
            respuesta = servicio.client.chat.completions.create(
                model=servicio.model,
                messages=[{"role": "system", "content": "Responde en español y de forma breve."},
                          {"role": "user", "content": mensaje}],
                stream=True,
            )
            for fragmento in respuesta:
                contenido = fragmento.choices[0].delta.content
                if contenido:
                    paquete = {"choices": [{"delta": {"content": contenido}}]}
                    yield f"data: {json.dumps(paquete, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as exc:
            error = traducir_error(exc)
            yield evento_sse("error", {"error": {"codigo": error.codigo, "mensaje": error.mensaje}})
    return StreamingResponse(generar_tokens(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
