# M4 · L1 — Del notebook a la API
## Guiones de grabación · 4 videos

Esta guía está pensada para leerla mientras compartes pantalla. El texto bajo **Narración** se puede leer tal como está. Las indicaciones entre corchetes son acciones para quien graba y no se leen.

## Preparación única del proyecto

### Qué vamos a construir

En los cuatro videos trabajaremos sobre el mismo proyecto: OrbitAir, una aerolínea ficticia. Partimos de un agente que recibe una pregunta, decide si necesita consultar un vuelo y utiliza una herramienta llamada `consultar_vuelo`. Esa herramienta busca información en un archivo CSV.

El objetivo de esta clase no es volver a explicar cómo se construye un agente desde cero. El objetivo es mostrar qué necesitamos agregar para que ese agente pueda ser utilizado desde una aplicación web, un tótem o cualquier otro cliente. Por eso incorporaremos una API HTTP, contratos de entrada y salida, autenticación, sesiones, streaming y manejo de errores.

### Estructura del repositorio

[Antes de grabar, abre el proyecto completo en el editor. Muestra el árbol de carpetas durante unos segundos.]

**Narración:**

“Este repositorio está organizado por responsabilidades. En la raíz tenemos `app.py`, que crea la aplicación FastAPI y registra sus endpoints principales. La carpeta `api` contiene la lógica del servicio: los modelos de datos, la configuración, el agente, las dependencias, las rutas, el streaming y los errores. En `data` está el CSV con los vuelos de ejemplo. Finalmente, `scripts` contiene los comandos que vamos a ejecutar durante los cuatro videos.

No vamos a abrir todos los archivos ahora. Los iremos conociendo cuando sean necesarios. Lo importante es entender que cada archivo tiene una responsabilidad concreta y que la ruta HTTP no necesita contener toda la lógica del agente.”

### Instalación y configuración

[En una terminal, sitúate en la carpeta que contiene `orbitair-api`. Ejecuta estos comandos una sola vez.]

```bash
cd orbitair-api
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

[Abre `.env` y configura `OPENAI_API_KEY` con una clave propia. No muestres la clave en la grabación.]

**Narración:**

“Antes de ejecutar las demostraciones necesitamos preparar el entorno de Python e instalar las dependencias. Creamos un entorno virtual para mantener las librerías de este proyecto separadas de las de otros proyectos. Después instalamos lo que está declarado en `requirements.txt` y copiamos el archivo de ejemplo de configuración.

Este proyecto utiliza el SDK de OpenAI y realiza llamadas reales al modelo `gpt-4.1-mini`. Por eso necesitamos una API key válida y crédito o facturación habilitada en la plataforma de OpenAI. La suscripción de ChatGPT y el uso de la API se facturan por separado. La clave se coloca en `.env`, nunca directamente en el código. Ese archivo está excluido del repositorio mediante `.gitignore`.

Las claves que utilizaremos para representar a Lucía, Andrés y el kiosco son credenciales ficticias de esta demostración. No son claves de OpenAI ni deben utilizarse en un sistema real.”

[Deja el servidor ejecutándose en una primera terminal.]

```bash
uvicorn app:app --reload
```

**Resultado esperado:** la terminal indica que Uvicorn está ejecutándose en `http://127.0.0.1:8000`. No cierres esta terminal durante las demostraciones. Para comprobar la documentación, abre `http://127.0.0.1:8000/docs` en el navegador.

### Datos que aparecerán en los ejemplos

[Abre `data/vuelos.csv` y `api/clientes.json`.]

**Narración:**

“Los datos son deliberadamente pequeños para que podamos concentrarnos en el comportamiento de la API. Tenemos dos pasajeros: Lucía, identificada como P-1001, y Andrés, identificado como P-1002. También tenemos un cliente que representa un kiosco de aeropuerto y que no está asociado a un pasajero.

El vuelo que consultaremos varias veces es OA1203, que viaja de AEP a LIM. En el conjunto de datos figura demorado 95 minutos por una causa operativa y con salida a las 14:05. También tenemos una reserva de ejemplo, B8NN4C, que pertenece a Andrés. La utilizaremos para demostrar por qué no basta con que alguien conozca un código de reserva: el servicio también debe comprobar quién está autenticado.”

---

# Video 1 · Del agente al endpoint

**Duración objetivo: 8 minutos.**  
**Idea central:** el agente mantiene su responsabilidad; FastAPI agrega una puerta HTTP y un contrato para comunicarse con él.

## 1. Ejecutar la demostración completa primero · 0:00–1:30

[Confirma que Uvicorn está activo. Abre una segunda terminal en la raíz `orbitair-api`, activa el entorno virtual si hace falta y ejecuta:]

```bash
source .venv/bin/activate
bash scripts/l1_v1_contrato.sh
```

**Qué debe aparecer:**

- Primera petición: `HTTP/1.1 422 Unprocessable Entity`, porque el cuerpo está vacío y falta `mensaje`.
- Segunda petición: `HTTP/1.1 422 Unprocessable Entity`, porque se envía el campo no permitido `pasajero_id`.
- Tercera petición: `HTTP/1.1 200 OK` y un JSON con `respuesta`, `sesion_id` y `derivado`.

[Deja visible la salida. No hace falta leer el texto variable que genere el modelo. Señala los códigos HTTP y los nombres de los campos.]

**Narración:**

“Voy a comenzar ejecutando directamente el ejemplo para que primero veamos el comportamiento que queremos conseguir. El script realiza tres peticiones contra nuestra API. Las dos primeras deben ser rechazadas con el código 422: una porque no enviamos el mensaje obligatorio y otra porque intentamos agregar un campo que el contrato no permite. La tercera petición es válida y debe responder con el código 200.

En esa última respuesta aparecen tres datos: el texto que generó el agente, el identificador de la sesión y un booleano que indica si el agente utilizó una herramienta. El contenido exacto puede cambiar porque estamos llamando a un modelo real, pero la estructura y los códigos HTTP son los que debemos observar.

Ahora que vimos el resultado, vamos a recorrer el código para entender qué archivo valida la petición, qué archivo ejecuta el agente y cómo FastAPI conecta ambas partes.”

## 2. De dónde sale el agente · 1:30–2:30

[Abrir `scripts/agente_terminal.py`. Luego abrir `api/agente.py`, primero las líneas 5–23 y después las líneas 26–62.]

**Narración:**

“Antes de hablar de FastAPI, ubiquemos al agente. `scripts/agente_terminal.py` es un pequeño punto de entrada que permite ejecutar el agente directamente desde la terminal. Recibe el texto que escribimos como argumento, crea el servicio, prepara un historial vacío y llama a `ejecutar_agente`.

La lógica principal está en `api/agente.py`. Arriba encontramos las instrucciones que definen el comportamiento de OrbitAir. Después aparece `HERRAMIENTAS`, donde declaramos la herramienta `consultar_vuelo` y el parámetro que necesita: un código de vuelo o de reserva.

La función `ejecutar_agente` recibe el servicio, el mensaje del usuario, el identificador del pasajero y el historial. Primero prepara los mensajes que se enviarán al modelo. Luego realiza la llamada a OpenAI. Si el modelo decide utilizar una herramienta, obtenemos los argumentos, llamamos al método `consultar_vuelo` del servicio y agregamos el resultado al historial de mensajes que se envía nuevamente al modelo.

Al final devolvemos la respuesta, un indicador llamado `derivado` y el historial interno. Es decir, el agente ya sabe conversar y consultar los datos. Lo que todavía no tiene es una interfaz para que otros programas puedan utilizarlo.”

## 3. El contrato de entrada: `ConsultaIn` · 2:30–4:00

[Abrir `api/modelos.py`, líneas 1–13.]

**Narración:**

“Este archivo define los modelos que describen los datos que entran y salen de nuestra API. Empecemos por `ConsultaIn`, que representa el cuerpo de una petición para crear una consulta.

El primer campo es `mensaje`. Es obligatorio, debe ser texto y tiene una longitud mínima de tres caracteres y máxima de dos mil. Estas restricciones se declaran con `Field`. No necesitamos escribir manualmente una serie de condiciones para comprobarlas: Pydantic se encarga de validar el contenido cuando FastAPI recibe la petición.

El segundo campo es `sesion_id`. Es opcional porque en la primera consulta todavía no tenemos un identificador de conversación. Si el cliente envía uno, se comprueba que tenga el patrón esperado para un UUID.

Ahora miremos `model_config` y la opción `extra='forbid'`. Esta configuración indica que no aceptaremos propiedades adicionales. Por eso la segunda petición del demo, que intentaba enviar `pasajero_id`, terminó en 422. El cliente puede enviar un mensaje y un identificador de sesión, pero no puede decidir desde el cuerpo qué pasajero representa.

Esto es importante porque el contrato no es solamente documentación. Es una validación que se ejecuta antes de entrar en la lógica de nuestra ruta.”

[Opcional: en `/docs`, abre `POST /v1/consultas` y muestra el esquema de `ConsultaIn`.]

## 4. La ruta: conectar el contrato con el agente · 4:00–5:45

[Abrir `api/rutas.py`, líneas 1–24. Primero explica imports y router; luego enfoca las líneas 13–24.]

**Narración:**

“Ahora llegamos al archivo que conecta HTTP con nuestra lógica de negocio: `api/rutas.py`. Aquí declaramos las rutas que los clientes pueden invocar.

La primera es `POST /v1/consultas`. El decorador indica el método HTTP y la dirección de la ruta. También declaramos `response_model=RespuestaOut`, que establece el modelo que debe cumplir la respuesta.

La función recibe `datos`, que FastAPI valida utilizando `ConsultaIn`. También recibe `cliente` y `servicio`. Estos dos últimos valores se obtienen mediante `Depends`, que es el mecanismo de inyección de dependencias de FastAPI. En otras palabras, la ruta declara qué necesita y FastAPI se encarga de resolverlo.

Después recuperamos la sesión correspondiente y llamamos a `ejecutar_agente`. Observemos que la ruta no contiene el prompt, no conoce los detalles de la herramienta y tampoco lee el CSV. Su trabajo es coordinar: recibir los datos, obtener las dependencias, ejecutar el agente y devolver el resultado con el formato público.

Hay otra decisión que vale la pena mencionar. Esta ruta está declarada con `def` y no con `async def`. En este ejemplo utilizamos el cliente síncrono de OpenAI. FastAPI ejecuta las rutas síncronas en un threadpool, de modo que la espera por esa llamada bloqueante no ocupa el event loop principal.”

## 5. El contrato de salida · 5:45–7:15

[Abrir `api/modelos.py`, líneas 16–20. Volver a `api/rutas.py`, líneas 16–24.]

**Narración:**

“Ya vimos qué datos aceptamos. Ahora veamos qué datos exponemos. `RespuestaOut` tiene tres campos: `respuesta`, `sesion_id` y `derivado`.

Recordemos que el agente devuelve también un historial interno. Ese historial contiene mensajes que se enviaron al modelo, llamadas a herramientas y resultados de esas herramientas. Es información útil para la ejecución interna, pero no necesitamos entregársela al cliente.

Por eso la ruta construye explícitamente un objeto `RespuestaOut` con los tres campos públicos. Y como declaramos ese modelo en `response_model`, FastAPI valida la respuesta y la adapta al contrato definido.

Esta separación evita que la estructura interna del agente se convierta accidentalmente en parte de nuestra API. Podemos cambiar detalles internos del agente sin obligar a los clientes a cambiar su integración, siempre que mantengamos el contrato público.”

## 6. Cierre · 7:15–8:00

[Mostrar brevemente `api/modelos.py` y `api/rutas.py`.]

**Narración:**

“En este primer video vimos el cambio fundamental: el agente no necesitó convertirse en una aplicación web ni mezclarse con el código HTTP. Agregamos modelos que validan la entrada y la salida, y una ruta que conecta esos modelos con el agente.

El contrato determina qué puede enviar el consumidor y qué información recibirá. En el siguiente video vamos a resolver otro problema: qué hacemos cuando una consulta tarda varios segundos y no queremos que el usuario espere mirando una pantalla sin recibir ninguna señal.”

---

# Video 2 · Streaming con SSE: progreso y tokens

**Duración objetivo: 9 minutos.**  
**Idea central:** distinguir entre enviar eventos de progreso del proceso y enviar fragmentos del texto generado por el modelo.

## 1. Ejecutar la demostración primero · 0:00–2:00

[Con Uvicorn activo, desde otra terminal en la raíz del proyecto ejecuta:]

```bash
source .venv/bin/activate
bash scripts/l1_v2_stream.sh
```

**Qué debe aparecer:**

1. En la primera petición, eventos SSE con `event: inicio`, después `event: herramienta` y finalmente `event: fin`. La respuesta final incluye el texto generado y el `sesion_id`.
2. En la segunda petición, varias líneas `data:` con fragmentos de texto y al final `data: [DONE]`.
3. En la tercera petición, primero `event: inicio` y después `event: error`. La conexión sigue siendo una respuesta HTTP 200 porque el stream ya comenzó.

[Si el texto sale en fragmentos muy seguidos, no intentes leerlo completo. Señala el orden de los eventos y el marcador final.]

**Narración:**

“En este video vamos a observar dos tipos de streaming. El primer ejemplo envía eventos que describen el progreso del agente. El segundo envía fragmentos del texto que genera el modelo. Al final también veremos qué ocurre si aparece un error cuando el stream ya comenzó.

Ejecuté el script completo. En la primera petición vemos los eventos de inicio, herramienta y fin. En la segunda aparecen fragmentos de texto y el marcador `[DONE]`. En la tercera, el servidor alcanza a enviar un evento de inicio y luego comunica un error dentro del propio stream.

No debemos confundir estos dos mecanismos. Uno informa qué está haciendo el proceso; el otro entrega contenido generado de manera incremental. Vamos a revisar cómo se implementa cada uno.”

## 2. ¿Qué es SSE y cómo se forma un evento? · 2:00–3:00

[Abrir `api/streaming.py`, líneas 1–12.]

**Narración:**

“SSE significa Server-Sent Events. Es una forma de mantener una conexión HTTP abierta para que el servidor pueda enviar eventos al cliente a medida que ocurren.

En nuestro código, la función `evento_sse` se encarga de construir el formato. Recibe el nombre del evento y un diccionario con sus datos. Devuelve dos campos de texto: `event`, que identifica el tipo de evento, y `data`, que contiene los datos serializados como JSON.

Al final agrega dos saltos de línea. Esto no es decorativo: en el formato SSE, esa línea vacía marca el final de un evento. Si enviamos varios eventos, cada uno debe terminar de esa manera para que el cliente pueda separarlos correctamente.”

## 3. El agente emite eventos sin conocer SSE · 3:00–4:15

[Abrir `api/agente.py`, líneas 26–57. Señalar especialmente 34–38 y 43–48.]

**Narración:**

“Fijémonos ahora en `ejecutar_agente`. El agente sigue siendo una función síncrona. No sabe qué es una conexión SSE y no necesita saberlo.

Lo único que agregamos es un parámetro opcional llamado `al_evento`. Si recibimos ese callback, lo invocamos al comenzar la consulta. Y cuando el modelo solicita la herramienta, enviamos otro evento indicando qué herramienta se está ejecutando.

Esto es una separación de responsabilidades. El agente informa que ocurrió algo, pero no decide cómo se transporta esa información por HTTP. La capa de streaming será la encargada de convertir esos avisos en eventos SSE.

Así podemos reutilizar el mismo agente desde una ruta normal, desde una ejecución de terminal o desde una ruta que transmite eventos.”

## 4. Ejecutar el agente en un hilo y transportar eventos con una cola · 4:15–6:00

[Abrir `api/streaming.py`, líneas 15–41. Explicar en este orden: cola, callback, función de trabajo, executor e iterador.]

**Narración:**

“Hay un detalle técnico importante. Nuestro agente utiliza llamadas síncronas. Si lo ejecutáramos directamente dentro de una ruta asíncrona, la espera podría bloquear el event loop. Para evitarlo, `correr_en_hilo` lo ejecuta en un hilo de trabajo.

Primero crea una `Queue`, que es una cola segura para intercambiar información entre hilos. Después define un callback que recibe los eventos del agente y los coloca en esa cola.

La función interna `trabajo` ejecuta el agente. Si termina correctamente, coloca en la cola un elemento especial llamado `_resultado`. Si ocurre una excepción, coloca `_error`. Finalmente, el `ThreadPoolExecutor` ejecuta ese trabajo en segundo plano y nos devuelve un objeto que permite conocer si la tarea terminó.

La función `iterar_eventos` lee la cola de manera asíncrona. Utiliza `asyncio.to_thread` para esperar por un elemento sin bloquear el event loop. Cada elemento se entrega a la ruta. Cuando recibe el resultado final o un error, termina la iteración.

Podemos pensar en la cola como un puente: el hilo donde trabaja el agente deja mensajes y la ruta los recoge para enviarlos al cliente.”

## 5. La ruta SSE de progreso · 6:00–7:00

[Abrir `api/rutas.py`, líneas 25–59.]

**Narración:**

“La ruta `/v1/consultas/stream` es la que utiliza este mecanismo. Recibe el mensaje, obtiene el cliente autenticado y recupera la sesión. Después llama a `correr_en_hilo` para iniciar el agente.

El generador asíncrono recorre los elementos de la cola. Si recibe un evento normal, lo convierte con `evento_sse` y lo envía. Si recibe `_resultado`, construye el evento `fin` con la respuesta, el identificador de sesión y el indicador de uso de herramienta. Si recibe `_error`, traduce la excepción y envía un evento `error`.

Finalmente, `StreamingResponse` mantiene la respuesta abierta y establece el tipo de contenido `text/event-stream`. También agregamos cabeceras para evitar buffering en algunos intermediarios.

En el script usamos `curl -N`. Esa opción desactiva el buffering de salida de curl y permite observar los eventos a medida que llegan. Sin ella, el cliente podría acumular la salida y mostrarla toda junta.”

## 6. Streaming de tokens · 7:00–8:15

[Abrir `api/rutas.py`, líneas 62–85.]

**Narración:**

“Ahora pasemos al segundo tipo de streaming. La ruta `/v1/tokens/stream` realiza una llamada al modelo con `stream=True`. Esa opción hace que el SDK entregue un iterador de fragmentos en lugar de esperar a tener toda la respuesta final.

En cada fragmento revisamos `delta.content`. Si contiene texto, construimos un objeto con la estructura `choices`, `delta` y `content`, y lo enviamos como una línea `data:`. Cuando termina la generación, enviamos `[DONE]` para indicar que no habrá más fragmentos.

La diferencia con el ejemplo anterior es que aquí no estamos enviando eventos como ‘inicio’ o ‘herramienta’. Estamos reenviando partes del contenido que el modelo va generando. Es una estructura que muchos clientes que consumen streams de Chat Completions pueden interpretar.”

## 7. Error después de iniciar la respuesta · 8:15–8:45

[Volver a la tercera petición del resultado del script y señalar `HTTP 200`, `inicio` y `error`.]

**Narración:**

“En el último ejemplo forzamos un error después de enviar el primer evento. La razón por la que el cliente recibe un evento `error` y no un nuevo código HTTP 500 es que los headers y el status ya se enviaron cuando comenzó el stream. Una vez iniciada la respuesta, no podemos cambiar retroactivamente el status.

Por eso el consumidor debe manejar errores de dos maneras: errores HTTP que ocurren antes de establecer el stream y eventos `error` que pueden llegar durante la transmisión.”

## 8. Cierre · 8:45–9:00

**Narración:**

“Entonces, SSE de progreso nos permite informar qué está ocurriendo en el proceso; el streaming de tokens nos permite entregar el texto poco a poco. La latencia total puede seguir siendo la misma, pero el usuario comienza a recibir información antes. Esa es la principal mejora de experiencia que buscamos.”

---

# Video 3 · Autenticación por API key y sesiones

**Duración objetivo: 7 minutos.**  
**Idea central:** la credencial determina la identidad del cliente; el identificador de sesión permite continuar una conversación, pero no transferirla a otro cliente.

## 1. Ejecutar la demostración primero · 0:00–1:45

[Con Uvicorn activo, ejecuta desde la raíz del proyecto:]

```bash
source .venv/bin/activate
bash scripts/l1_v3_auth.sh
```

**Qué debe aparecer:**

- Petición sin API key: `HTTP 401 Unauthorized` y la cabecera `WWW-Authenticate: Bearer`.
- Lucía intenta consultar la reserva `B8NN4C`: la respuesta del agente debe indicar que no está autorizada y no mostrar los datos de la reserva.
- Aunque Lucía escriba que es P-1002, el sistema sigue autenticándola como Lucía y no debe revelar la reserva.
- La consulta válida de Lucía devuelve un `sesion_id`.
- Lucía puede enviar otra consulta con ese identificador y continuar la conversación.
- Andrés intenta utilizar el mismo `sesion_id`: debe recibir `HTTP 404 Not Found`.

**Narración:**

“Voy a comenzar con el script de autenticación y sesiones. Primero hacemos una petición sin credencial y recibimos 401. Después Lucía intenta consultar una reserva que pertenece a Andrés y el agente debe rechazar el acceso. También probamos que escribir ‘soy el pasajero P-1002’ dentro del mensaje no cambia la identidad autenticada.

Luego Lucía realiza una consulta válida y recibe un identificador de sesión. Puede utilizarlo en una segunda petición para continuar la conversación. Finalmente, Andrés intenta reutilizar el identificador de Lucía y recibe 404.

Estos resultados nos muestran dos conceptos distintos: la API key establece quién está llamando y la sesión permite recuperar el contexto de una conversación. Ahora vamos a ver dónde se implementa cada uno.”

## 2. Dónde se definen los clientes · 1:45–2:30

[Abrir `api/clientes.json`. Luego abrir `scripts/common.sh`.]

**Narración:**

“En `clientes.json` tenemos los clientes autorizados. Para cada uno guardamos un identificador, el hash SHA-256 de su clave, su rol, el canal y, cuando corresponde, el pasajero asociado.

En `scripts/common.sh` están las claves ficticias que utilizan nuestros comandos de demostración. Las mostramos separadas del archivo JSON para que se entienda la diferencia: el script necesita enviar una clave de prueba, pero el servicio almacena y compara su hash. En un sistema real estas claves deberían gestionarse como secretos y nunca quedar escritas en un repositorio.”

## 3. Validar la API key · 2:30–3:45

[Abrir `api/dependencias.py`, líneas 1–27.]

**Narración:**

“La función `obtener_cliente` es la que valida la identidad. Recibe el header `Authorization` mediante `Header`. Esperamos que tenga el formato Bearer seguido de una clave.

Si el header no existe o no tiene el formato correcto, respondemos con 401 y agregamos `WWW-Authenticate: Bearer`. Esa cabecera indica el esquema de autenticación que espera el servicio.

Cuando sí recibimos una clave, calculamos su SHA-256 con `hashlib`. Después leemos el archivo de clientes y comparamos la huella calculada con las huellas almacenadas. Para la comparación utilizamos `hmac.compare_digest`, que está diseñada para evitar comparaciones cuyo tiempo de ejecución revele información sobre cuánto coincide un valor con otro.

Si encontramos una coincidencia, devolvemos los datos del cliente autenticado. Si no, respondemos nuevamente con 401. La ruta recibe este resultado mediante `Depends(obtener_cliente)`. Por eso la identidad se determina antes de ejecutar el agente y no a partir de lo que la persona escriba en el chat.”

## 4. La autorización de una reserva no depende del modelo · 3:45–4:45

[Abrir `api/servicios.py`, líneas 14–39.]

**Narración:**

“Autenticar a una persona nos dice quién es, pero todavía debemos comprobar si puede acceder al recurso que solicita. Esa comprobación está en `consultar_vuelo`, dentro de `api/servicios.py`.

La función busca el código en el CSV. Si encuentra un vuelo, devuelve sus datos. Si encuentra una reserva, compara el pasajero asociado a esa reserva con el pasajero que llegó desde el cliente autenticado.

Si no coinciden, devuelve un resultado de no autorización y no entrega los datos de la reserva. Esta parte es fundamental: no confiamos únicamente en las instrucciones del prompt para proteger información. La comprobación de propiedad se ejecuta en nuestro código Python, antes de entregar los datos al modelo.”

## 5. Cómo funcionan las sesiones · 4:45–6:15

[Abrir `api/dependencias.py`, líneas 30–43. Después mostrar `api/rutas.py`, líneas 13–24.]

**Narración:**

“Ahora veamos `obtener_sesion`. Si la petición no trae un `sesion_id`, creamos uno nuevo con `uuid4`. En el diccionario `_SESIONES` guardamos quién es el propietario de esa sesión y el historial de mensajes.

Si la petición sí trae un identificador, buscamos la sesión. Si no existe o pertenece a otro cliente, devolvemos 404. Si existe y pertenece al cliente autenticado, devolvemos el historial para que el agente pueda continuar la conversación.

¿Por qué respondemos 404 y no 403 cuando Andrés intenta utilizar la sesión de Lucía? Porque un 403 confirmaría que ese identificador existe, aunque el usuario no tenga permiso. Al responder 404 evitamos revelar si la sesión existe o no para ese cliente.

Hay una limitación importante que debemos mencionar: las sesiones de este ejemplo viven en memoria del proceso. Si reiniciamos el servidor, se pierden. En una aplicación de producción necesitaríamos un almacenamiento persistente, por ejemplo una base de datos o Redis. Y si desplegamos varias instancias, necesitaríamos que todas compartan ese almacenamiento.”

## 6. Cierre · 6:15–7:00

**Narración:**

“Quedémonos con esta diferencia: la API key responde quién está haciendo la petición; el identificador de sesión responde qué conversación quiere continuar ese cliente. Ningún texto del chat puede cambiar la identidad autenticada y ningún cliente puede apropiarse de la sesión de otro.

En el siguiente video vamos a completar la API con respuestas de error consistentes y endpoints que permiten comprobar si el servicio está vivo y si está preparado para recibir tráfico.”

---

# Video 4 · Errores HTTP, health y ready

**Duración objetivo: 8 minutos.**  
**Idea central:** los errores deben informar al consumidor sin filtrar detalles internos; los endpoints operativos responden preguntas distintas sobre el estado del servicio.

## 1. Ejecutar la demostración primero · 0:00–1:45

[Con Uvicorn activo, ejecuta desde la raíz del proyecto:]

```bash
source .venv/bin/activate
bash scripts/l1_v4_errores.sh
```

**Qué debe aparecer:**

- `/health`: HTTP 200 y `{"status":"ok"}`.
- `/ready`: HTTP 200 y comprobaciones de configuración y datos, siempre que `.env` tenga `OPENAI_API_KEY` y exista `data/vuelos.csv`.
- `/version`: HTTP 200 y una versión, normalmente `dev` si no se configuró otra.
- Petición inválida: HTTP 422 con el formato de validación de FastAPI.
- Pruebas locales de error controlado e interno: ambas muestran un cuerpo `error` con `codigo`, `mensaje` y `request_id`. El error interno no debe mostrar la cadena de conexión falsa.
- Prueba de `RateLimitError`: muestra HTTP 503 y `Retry-After: 5`.

**Narración:**

“Voy a comenzar ejecutando las pruebas de este último video. Primero consultamos los endpoints de estado: health, ready y version. Después provocamos un error de validación, probamos los manejadores de errores de la aplicación y simulamos un límite del proveedor de IA.

Observen que no todas las respuestas de error tienen el mismo origen. El 422 es una validación automática de FastAPI. Los errores propios del servicio utilizan un formato común y la saturación del proveedor se traduce a un 503 con una cabecera Retry-After.

Ahora vamos a revisar por qué necesitamos separar estos casos y qué información conviene devolver al cliente.”

## 2. El problema de devolver el error interno · 1:45–2:45

[En el editor, abre `scripts/probar_manejador_http.py`, líneas 15–24. Señala la excepción que contiene la cadena de conexión ficticia.]

**Narración:**

“Primero pensemos en un error que no deberíamos cometer. Imaginemos que una excepción contiene una cadena de conexión a una base de datos, con usuario, contraseña y dirección del servidor. Si devolvemos directamente `str(exc)` dentro de la respuesta HTTP, podríamos exponer esos datos al consumidor.

En esta prueba local generamos una excepción cuyo mensaje incluye una contraseña ficticia. La intención no es utilizar esa información, sino demostrar el riesgo. En una aplicación real, los mensajes internos pueden contener rutas, nombres de servidores, consultas, identificadores o credenciales.

El cliente necesita saber que ocurrió un error y qué puede hacer. No necesita recibir el traceback ni los detalles de nuestra infraestructura.”

## 3. Un formato común: `ErrorHTTP` y `cuerpo_error` · 2:45–4:15

[Abrir `api/errores_http.py`, líneas 1–36.]

**Narración:**

“Para centralizar el formato definimos una excepción propia llamada `ErrorHTTP`. Guarda el código de estado HTTP, un código interno que identifica el tipo de error, un mensaje seguro para el consumidor y, opcionalmente, cabeceras adicionales.

La función `cuerpo_error` construye el cuerpo común. Dentro de `error` incluimos tres propiedades: `codigo`, `mensaje` y `request_id`. El código permite que el cliente identifique el tipo de problema sin depender de comparar frases. El mensaje está pensado para mostrarse al usuario. Y el request ID permite rastrear la petición en nuestros registros.

Después, `registrar_manejadores` registra dos manejadores en FastAPI. El primero captura los errores `ErrorHTTP` y construye la respuesta con el status y las cabeceras que definimos. El segundo captura excepciones no controladas. En ese caso registra el detalle completo mediante `logger.exception`, pero devuelve al cliente un mensaje genérico.

Así mantenemos una separación: el equipo técnico puede investigar el error utilizando los logs y el identificador de petición, mientras que el consumidor recibe una respuesta segura y consistente.”

[Volver a la salida de `probar_manejador_http.py` y comparar `/error-controlado` con `/error-interno`.]

**Narración:**

“En la salida vemos que ambos errores comparten la misma estructura. El error interno no expone la cadena de conexión que provocó la excepción. En un entorno real, el equipo de soporte buscaría el `request_id` correspondiente en el sistema de logs para localizar el detalle.”

## 4. Traducir errores del proveedor · 4:15–5:15

[Abrir `api/errores_http.py`, líneas 38–43. Luego abrir `scripts/probar_rate_limit.py`.]

**Narración:**

“También debemos distinguir los errores de nuestra API de los errores que vienen de un proveedor externo. En este ejemplo, `traducir_error` reconoce `RateLimitError`, que representa un límite alcanzado en el proveedor de IA.

Lo traducimos a HTTP 503, con el código `PROVEEDOR_NO_DISPONIBLE` y la cabecera `Retry-After: 5`. ¿Por qué no devolvemos 429? Porque el límite que se alcanzó es el del proveedor, no necesariamente el ritmo de peticiones del consumidor de OrbitAir. El 503 comunica que el servicio no puede completar temporalmente la operación y la cabecera indica cuánto esperar antes de reintentar.

El script `probar_rate_limit.py` construye un error simulado del SDK. Así podemos comprobar la traducción sin provocar realmente un límite en OpenAI ni consumir una llamada real.”

## 5. Health, ready y version · 5:15–7:15

[Abrir `app.py`, líneas 1–10. Explicar la creación de FastAPI y el registro del router y manejadores. Después mostrar líneas 13–31.]

**Narración:**

“Terminemos con tres endpoints que suelen ser importantes cuando desplegamos un servicio.

`/health` responde si el proceso está vivo y puede atender una petición HTTP. En este ejemplo devuelve `status: ok`. Lo mantenemos simple y no hacemos que dependa de OpenAI o del archivo CSV. Si este chequeo fuera demasiado exigente, podríamos reiniciar un proceso que está vivo pero que temporalmente no puede acceder a una dependencia.

`/ready` responde una pregunta distinta: ¿está preparado el servicio para recibir tráfico? Aquí comprobamos que exista la variable `OPENAI_API_KEY` y que el archivo CSV esté presente. Si falta alguno de esos requisitos, devolvemos 503 y una lista de comprobaciones fallidas. Si todo está disponible, devolvemos `status: ready`.

Hay que ser precisos sobre el alcance de esta demostración: `/ready` no realiza una llamada real a OpenAI. Comprueba que la clave esté configurada, pero no garantiza que el proveedor esté disponible ni que la clave tenga saldo.

Finalmente, `/version` devuelve el identificador de versión configurado. En un despliegue automatizado podríamos inyectar el hash del commit de Git mediante `GIT_COMMIT`. Si no configuramos nada, veremos el valor por defecto `dev`. Esto ayuda a saber qué versión del servicio está ejecutándose.”

## 6. Cierre de la clase · 7:15–8:00

[Mostrar brevemente el árbol del proyecto y luego `app.py`.]

**Narración:**

“Con esto completamos el recorrido de nuestro agente hasta convertirlo en un servicio HTTP. Primero definimos un contrato de entrada y salida. Después agregamos streaming para comunicar progreso y entregar texto de forma incremental. Luego incorporamos autenticación y sesiones para identificar al cliente y proteger el contexto de cada conversación. Finalmente, centralizamos los errores y agregamos endpoints operativos.

El agente sigue siendo el componente que interpreta la consulta y utiliza herramientas. La API es la capa que permite que otros sistemas lo consuman de una forma controlada, segura y predecible. En la siguiente parte de la clase podremos concentrarnos en empaquetar este servicio y publicarlo para que esté disponible desde una URL.”

---

## Lista de comprobación antes de grabar

- [ ] Activar el entorno virtual `.venv`.
- [ ] Verificar que `.env` contiene una API key válida de OpenAI sin mostrarla en pantalla.
- [ ] Iniciar Uvicorn en una terminal y dejarlo activo.
- [ ] Abrir una segunda terminal en la raíz `orbitair-api`.
- [ ] Ejecutar el script correspondiente al video antes de explicar el código.
- [ ] Mantener visible el resultado esperado mientras se explica qué acaba de ocurrir.
- [ ] Abrir los archivos en el orden indicado y utilizar los números de línea como referencia visual.
- [ ] Recordar que el texto del modelo puede variar; lo importante son los códigos HTTP, los campos y el orden de los eventos.
- [ ] No mostrar la API key real durante la grabación.

## Comandos de cada video

```bash
# Video 1
bash scripts/l1_v1_contrato.sh

# Video 2
bash scripts/l1_v2_stream.sh

# Video 3
bash scripts/l1_v3_auth.sh

# Video 4
bash scripts/l1_v4_errores.sh
```
