# OrbitAir API · M4 L1

Repositorio autocontenido para los cuatro videos de la clase **Del notebook a la API**. Construye un servicio FastAPI para un agente de una aerolínea ficticia. El agente usa una sola herramienta (`consultar_vuelo`) que consulta `data/vuelos.csv`; la API agrega contrato HTTP, autenticación por API key, sesiones, streaming y manejo uniforme de errores.

## Requisitos

- Python 3.10 o superior.
- Una API key de OpenAI con acceso y crédito disponible. La suscripción de ChatGPT no incluye crédito de API.
- `curl` y una terminal Bash.

## Preparación desde cero

```bash
cd orbitair-api
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Abre `.env` y pega tu clave real en `OPENAI_API_KEY=`. El modelo predeterminado es `gpt-4.1-mini`. No publiques `.env`, no pegues la clave en el código ni la muestres durante la grabación. La API se factura por uso; verifica saldo y límites en la plataforma de OpenAI. Una clave de API es distinta de iniciar sesión en ChatGPT.

Las tres API keys de demostración están definidas en `api/clientes.json` mediante sus hashes SHA-256 y sus valores de prueba están en `.env.example` y `scripts/common.sh`. Son credenciales locales didácticas, no credenciales para producción. En un sistema real deben inyectarse como secretos y rotarse.

## Ejecutar

```bash
uvicorn app:app --reload
```

Abre <http://127.0.0.1:8000/docs>. Para revisar estado:

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/ready
curl -i http://127.0.0.1:8000/version
```

`/health` comprueba que el proceso responde. `/ready` comprueba que existe configuración de API y el CSV. `/version` devuelve el identificador configurado en `GIT_COMMIT` (o `APP_VERSION` como alternativa). En CI/CD se inyectaría el SHA real del commit.

## Estructura

- `app.py`: crea FastAPI, registra manejadores y publica endpoints de estado.
- `api/modelos.py`: contratos Pydantic `ConsultaIn` y `RespuestaOut`.
- `api/configuracion.py`: carga `.env`, modelo, versión y rutas de archivos.
- `api/servicios.py`: cliente OpenAI y herramienta de consulta sobre CSV; valida que una reserva pertenezca al pasajero autenticado.
- `api/agente.py`: prompt, definición de herramienta y ciclo de llamadas al modelo.
- `api/clientes.json`: clientes y hashes SHA-256 de sus API keys.
- `api/dependencias.py`: autenticación, inyección del servicio y propiedad de sesiones.
- `api/rutas.py`: endpoints síncronos, SSE de progreso y streaming de tokens.
- `api/streaming.py`: formato SSE, cola y ejecución del agente síncrono en un hilo.
- `api/errores_http.py`: `ErrorHTTP`, cuerpo uniforme y traducción de errores del proveedor.
- `data/vuelos.csv`: datos ficticios de vuelos y una reserva de ejemplo.
- `scripts/`: demostraciones reproducibles de cada video, `agente_terminal.py` para ejecutar el agente directamente sin HTTP y pruebas locales de los manejadores de errores.

## Comparar el agente de terminal con la API

Con el entorno virtual activo y `.env` configurado, puedes ejecutar el agente directamente, sin servidor HTTP:

```bash
python3 scripts/agente_terminal.py "¿Cómo viene el vuelo OA1203?"
```

## Los cuatro demos

Con el servidor ejecutándose, abre otra terminal, activa `.venv` y ejecuta:

```bash
bash scripts/l1_v1_contrato.sh
bash scripts/l1_v2_stream.sh
bash scripts/l1_v3_auth.sh
bash scripts/l1_v4_errores.sh
```

Las consultas válidas realizan llamadas reales al modelo y pueden consumir crédito. Los mensajes del modelo pueden variar; los códigos HTTP y la estructura de eventos son lo importante. En el video 2, `curl -N` evita que curl acumule el stream antes de mostrarlo.

## Datos de demostración

- `web-lucia`: pasajera `P-1001`.
- `web-andres`: pasajero `P-1002`.
- `kiosco-aep`: tótem sin pasajero asociado.
- Vuelo `OA1203`: AEP → LIM, demorado 95 minutos por causa operativa, salida 14:05.
- Reserva `B8NN4C`: pertenece a `P-1002`.

El servicio verifica la propiedad de la reserva dentro de la herramienta antes de devolver datos. El prompt también indica al modelo que no debe revelar reservas ajenas, pero la autorización efectiva está en Python, no depende de obedecer al LLM.

## Notas técnicas y límites de la demo

- `crear_consulta` es `def` porque el SDK de OpenAI usado aquí es síncrono; FastAPI ejecuta endpoints síncronos en un threadpool.
- El streaming SSE de progreso ejecuta el agente síncrono en un `ThreadPoolExecutor` y comunica eventos mediante una cola.
- El endpoint de tokens usa `stream=True` del SDK de Chat Completions y emite fragmentos con `data:` y el terminador `[DONE]`.
- Una vez iniciada una respuesta SSE, el status HTTP ya fue enviado. Los fallos posteriores se notifican con un evento `error`.
- Las sesiones viven en memoria del proceso. Se pierden al reiniciar o desplegar y no sirven para varias réplicas sin almacenamiento compartido.
- `/ready` no hace una llamada facturable al LLM. Verifica configuración y presencia del CSV, no la disponibilidad real del proveedor.
- En producción, añade almacenamiento persistente, límites de tamaño/tiempo, rotación de claves, rate limiting, observabilidad, pruebas y gestión de secretos.

## Sobre errores

Para mostrar el fallo de un manejador ingenuo, usa solo como ejemplo visual este anti-patrón (no lo incorpores al servicio): `return JSONResponse(status_code=500, content={"error": str(exc)})`. Una excepción cuyo texto contenga `postgresql://app:CLAVE-FALSA@db.interna:5432/vuelos` filtraría la contraseña. La implementación real de este repo devuelve un mensaje genérico y deja el traceback en el log.

Los errores de aplicación usan `{"error":{"codigo":"...","mensaje":"...","request_id":"..."}}`. El manejador general registra el traceback en el log y devuelve un mensaje genérico. `RateLimitError` del proveedor se traduce a `503` con `Retry-After: 5`, porque el límite afectado es el del proveedor, no el ritmo del cliente de OrbitAir.

## Extensión M4 L2 · Deploy

Los archivos adicionales de Docker, Railway, GitHub Actions, configuración tipada, smoke tests y rollback se explican en [README_M4_L2.md](README_M4_L2.md). La guía de speaker para los cuatro videos de deploy se encuentra en `GUIA_SPEAKER_L2.md`.
