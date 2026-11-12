# M4 · L2 — Deploy
## Guiones de grabación · 4 videos independientes

Esta guía está escrita para leerla mientras compartes pantalla. Los párrafos bajo **Narración** están redactados para decirse en voz alta. Las instrucciones entre corchetes son acciones de grabación y no se leen. Los números de línea son referencias para localizar el código; no hace falta pronunciarlos.

## Preparación general del repositorio

### Qué contiene esta extensión

Trabajaremos sobre el mismo servicio FastAPI de OrbitAir. El código de la API continúa en `app.py` y en la carpeta `api`. Para esta parte se agregan los archivos de Docker, la configuración para Railway, un workflow de GitHub Actions, pruebas automáticas y un script que comprueba un despliegue público.

[Abre el árbol del repositorio y muestra estas carpetas y archivos.]

```text
orbitair-api/
├── .github/
│   └── workflows/
│       └── ci.yml
├── api/
│   ├── config.py
│   ├── configuracion.py
│   └── releases.py
├── data/
│   └── vuelos.csv
├── scripts/
│   ├── l2_v1_imagen.sh
│   ├── l2_v2_config.sh
│   ├── l2_v4_smoke.py
│   └── decidir_promocion.py
├── tests/
│   ├── test_api.py
│   ├── test_config.py
│   └── test_releases.py
├── .dockerignore
├── Dockerfile
├── Dockerfile.tutorial
├── Dockerfile.secreto-demo
├── docker-compose.yml
├── railway.json
├── requirements.lock
└── README_M4_L2.md
```

**Narración:**

“Esta extensión incorpora todo lo necesario para empaquetar y desplegar OrbitAir. Los archivos `Dockerfile.tutorial` y `Dockerfile` nos permiten comparar una imagen sencilla con una imagen preparada para producción. `docker-compose.yml` describe cómo ejecutar el servicio localmente como contenedor. `api/config.py` centraliza la configuración y la validación de secretos. `railway.json` declara cómo construir y comprobar el servicio en Railway. Dentro de `.github/workflows` está el pipeline de integración y despliegue continuo. Finalmente, `tests` contiene las pruebas automáticas y `scripts` reúne las demostraciones que ejecutaremos.

Cada video comienza ejecutando su demostración. Después vamos a abrir los archivos responsables del resultado y a entenderlos con calma. Los ejemplos de despliegue sí requieren una cuenta de GitHub y otra de Railway.”

### Preparación local

[En una terminal, desde la raíz `orbitair-api`, ejecuta una sola vez:]

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.lock -r requirements-dev.lock
```

[Para ejecutar pruebas locales sin consumir API, utiliza: `APP_ENV=test LLM_MODO_SIMULADO=true OPENAI_API_KEY= pytest -q`. El CI ya establece estas variables automáticamente.]

[Abre `.env` y configura `OPENAI_API_KEY` con una clave real. No muestres su valor en la grabación. Mantén `APP_ENV=local` y `LLM_MODO_SIMULADO=false`.]

**Narración:**

“Antes de ejecutar los ejemplos necesitamos crear nuestro archivo local de variables de entorno e instalar las dependencias. La aplicación utiliza `gpt-4.1-mini`, por lo que necesitamos una API key de OpenAI con facturación o crédito habilitado. La suscripción de ChatGPT no incluye el consumo de la API.

La clave se guarda en `.env`. No se escribe dentro de Python, no se copia al Dockerfile y no se sube a GitHub. El archivo `.env` está excluido tanto del repositorio como del contexto de construcción de Docker. En los ejemplos que utilizan el modo real, las llamadas al modelo pueden consumir crédito.”

### Publicar el repositorio

[Si el repositorio de L1 ya está publicado, utiliza ese mismo repositorio. Comprueba que los archivos nuevos estén incluidos en el commit. No crees un segundo repositorio para esta extensión.]

```bash
git status
git add .
git commit -m "Add deployment and CI pipeline"
git push origin main
```

[En los videos que utilizan Railway, crea o selecciona un proyecto Railway y conecta el repositorio de GitHub. Los nombres de algunos botones pueden variar con las actualizaciones del panel.]

### Datos de las demostraciones

- Vuelo: `OA1203`, de AEP a LIM.
- Cliente de prueba: `web-lucia`, pasajera `P-1001`.
- La API key de demostración de Lucía está en `.env.example`. Es una credencial didáctica; no la uses como credencial real de una aplicación.
- En Railway se deben guardar las credenciales demo como variables de entorno, ya que en `APP_ENV=produccion` el servicio no acepta las claves locales de respaldo del archivo JSON.

---

# Video 1 · De un Dockerfile de tutorial a una imagen productiva

**Duración objetivo: 7 minutos.**  
**Objetivo:** comparar dos imágenes Docker y explicar qué aporta cada práctica del Dockerfile productivo: cache, tamaño, seguridad, proceso y healthcheck.

## 1. Ejecutar el demo completo · 0:00–1:30

[Confirma que Docker Desktop o Docker Engine está iniciado y que el puerto 8000 está libre. Comprueba que `.env` contiene una `OPENAI_API_KEY` real. Desde la raíz `orbitair-api`, ejecuta:]

```bash
bash scripts/l2_v1_imagen.sh
```

**Qué debe aparecer:**

- Dos construcciones: `orbitair:tutorial` y `orbitair:prod`.
- Una segunda construcción de cada imagen después de crear un archivo marcador. Los tiempos pueden variar; lo importante es que la reconstrucción productiva conserve la capa de dependencias.
- Una tabla con los tamaños de ambas imágenes. No memorices un tamaño concreto: depende de la versión de las dependencias y de la plataforma.
- Un contenedor llamado `orbitair-demo` con estado `Up ... (healthy)`.
- Una respuesta `HTTP/1.1 200 OK` para `/health`.
- Una respuesta `HTTP/1.1 200 OK` de `POST /v1/consultas`, con `respuesta`, `sesion_id` y `derivado`.

[Deja la terminal visible. Señala primero los tamaños, luego el estado `healthy` y finalmente la respuesta HTTP. El script elimina el contenedor al terminar.]

**Narración:**

“Voy a empezar construyendo y ejecutando las dos imágenes para ver la diferencia en un caso concreto. El script construye primero una imagen didáctica y después una imagen productiva. Luego crea un pequeño archivo marcador y vuelve a construir ambas. Ese cambio nos permite observar cómo está organizada la cache de Docker.

Al terminar, el script muestra los tamaños de las imágenes y ejecuta la imagen productiva. El contenedor debe alcanzar el estado `healthy`, que significa que su comprobación de salud está respondiendo correctamente. Después realiza una consulta real a OrbitAir con el vuelo OA1203. Debemos recibir un HTTP 200 y un JSON con la respuesta del agente.

El texto que genera el modelo puede variar. Lo que nos interesa comprobar es que la imagen arranca, supera su healthcheck y puede atender una petición autenticada. Ahora voy a abrir los dos Dockerfiles para entender por qué sus resultados son distintos.”

## 2. El Dockerfile de tutorial y el problema de la cache · 1:30–2:40

[Abre `Dockerfile.tutorial`, líneas 1–7. Después abre `scripts/l2_v1_imagen.sh`, líneas 18–27.]

**Narración:**

“Este primer archivo representa el Dockerfile típico de un tutorial. Parte de una imagen completa de Python 3.12, define el directorio de trabajo, copia todo el proyecto y después instala las dependencias.

La instrucción que nos interesa es `COPY . .`, porque copia el proyecto completo antes de ejecutar `pip install`. Docker construye la imagen por capas y reutiliza una capa cuando las instrucciones y sus archivos de entrada no han cambiado. Pero si modificamos cualquier archivo que forme parte de esa copia, Docker invalida esa capa. Como la instalación de dependencias está después, también tiene que ejecutarla otra vez.

El script demuestra esto creando un archivo marcador. No cambia la aplicación ni sus dependencias; simplemente modifica el contenido que recibe `COPY . .`. En la reconstrucción de tutorial, esa modificación invalida la capa anterior y obliga a repetir la instalación.

En un proyecto real, cambiar una etiqueta, corregir una función o actualizar un archivo de documentación no debería obligarnos a reinstalar todas las librerías. Por eso vamos a ordenar las instrucciones de otra manera.”

## 3. Construcción por etapas y cache de dependencias · 2:40–4:40

[Abre `Dockerfile`, líneas 1–16. Explica primero las líneas 1–6 y luego las 8–16.]

**Narración:**

“Este es el Dockerfile productivo. La primera diferencia es que utiliza `python:3.12-slim`, una imagen base más pequeña que la imagen completa. No significa que automáticamente cualquier aplicación vaya a ocupar la mitad, pero sí evita cargar herramientas y componentes que no necesitamos en ejecución.

La construcción está dividida en dos etapas. La etapa `build` se encarga de instalar las dependencias. Primero copia únicamente `requirements.lock` y después ejecuta `pip install`. Si modificamos el código de la aplicación, pero no cambiamos ese archivo de dependencias, Docker puede reutilizar la capa donde instaló los paquetes.

La segunda etapa se llama `runtime`. Parte otra vez de una imagen slim limpia y copia desde la etapa anterior únicamente las dependencias instaladas. Después copia de manera explícita `app.py`, la carpeta `api` y los datos. No copiamos indiscriminadamente todo el repositorio.

Esta separación tiene dos ventajas. La primera es que la imagen final no necesita incluir herramientas de construcción ni archivos temporales. La segunda es que reducimos la cantidad de archivos que terminan dentro del contenedor.

También creamos un usuario llamado `app` y cambiamos a ese usuario con la instrucción `USER app`. Así, el servidor no se ejecuta como root. Si el proceso tuviera una vulnerabilidad, evitamos concederle privilegios administrativos innecesarios dentro del contenedor.”

## 4. Healthcheck, puerto y señales de apagado · 4:40–5:50

[Continúa en `Dockerfile`, líneas 17–22. Después abre `.dockerignore`, líneas 1–11.]

**Narración:**

“Después de definir el usuario, declaramos el puerto de referencia y el `HEALTHCHECK`. Docker ejecuta periódicamente una petición local a `/health`. Si el endpoint responde correctamente, el contenedor aparece como `healthy`. Si deja de responder, Docker marca el estado como `unhealthy`. Este healthcheck informa del estado del contenedor; no reemplaza las comprobaciones funcionales del servicio.

Miremos ahora el comando de arranque. Está escrito en formato JSON, pero el proceso se inicia mediante `sh -c`. Esto es intencional porque necesitamos que el shell expanda la variable `PORT`, que Railway inyecta al ejecutar el servicio. El valor `8000` queda como alternativa para la ejecución local.

Dentro del comando aparece `exec`. Esa palabra reemplaza el proceso del shell por Uvicorn. De esta manera, Uvicorn recibe directamente las señales de apagado del contenedor y puede cerrar el servidor correctamente. Si quitáramos `exec`, el shell podría quedarse como proceso principal y complicar la entrega de señales.

Finalmente, `.dockerignore` evita enviar archivos que no necesitamos en la construcción. Ahí excluimos `.env`, entornos virtuales, cachés y archivos temporales. Esto es especialmente importante: aunque el Dockerfile productivo copie archivos explícitos, el archivo de secretos nunca debe formar parte del contexto de build.”

## 5. Ejecutar con Docker Compose y cerrar · 5:50–7:00

[Abre `docker-compose.yml`, líneas 1–13. Explica `build`, `env_file`, `environment`, `ports` y `restart`. Luego ejecuta:]

```bash
docker compose up --build
```

[Cuando termine el build, abre `http://localhost:8000/docs`. Para detenerlo, vuelve a la terminal y presiona `Ctrl+C`.]

**Narración:**

“Docker Compose nos permite describir cómo queremos ejecutar el servicio sin escribir cada vez un comando largo de `docker run`. En este archivo indicamos que la imagen se construye usando nuestro Dockerfile productivo, que las variables se leen desde `.env`, que el puerto interno es el 8000 y que publicaremos ese puerto en nuestra máquina.

La opción `restart` indica que Docker debe intentar reiniciar el servicio si se detiene de manera inesperada. No sustituye la supervisión de la plataforma, pero define el comportamiento local del contenedor.

Con `docker compose up --build` construimos la imagen si hace falta y levantamos el servicio. Al abrir la documentación de FastAPI podemos comprobar que la aplicación está respondiendo desde el contenedor.

La conclusión es que un Dockerfile productivo no consiste solamente en conseguir que Python arranque. También debemos pensar en la cache de dependencias, el tamaño de la imagen, los permisos del proceso, la gestión de secretos, las señales de apagado y las comprobaciones de salud. Cada una de estas decisiones tiene un efecto operativo.”

---

# Video 2 · Configuración, secretos y primer deploy en Railway

**Duración objetivo: 9 minutos.**  
**Objetivo:** validar la configuración antes de iniciar el servicio, evitar filtrar secretos en una imagen y publicar OrbitAir en una URL de Railway.

## 1. Ejecutar la demostración local de configuración · 0:00–1:15

[Desde la raíz del proyecto, con el entorno virtual activo, ejecuta:]

```bash
bash scripts/l2_v2_config.sh
```

**Qué debe aparecer:**

- El primer caso informa que la configuración se rechaza porque falta `OPENAI_API_KEY`.
- El segundo caso informa que una clave vacía también se rechaza.
- El resumen seguro muestra `openai_api_key: configurada`, pero nunca imprime el valor `sk-ESTA-CLAVE-NO-DEBE-APARECER`.
- Si Docker está instalado, se construye una imagen didáctica con una clave falsa y `docker history` muestra ese valor en el historial de capas. Al final se elimina la imagen.

**Narración:**

“Voy a ejecutar primero las comprobaciones de configuración. El script prueba tres situaciones. En las dos primeras intenta validar la aplicación sin una clave y después con una cadena vacía. En ambos casos esperamos un rechazo. No queremos que el servidor arranque con una configuración incompleta y descubra el problema cuando reciba su primera petición.

Después probamos el resumen seguro. En ese caso simulamos que existe una clave, pero el resultado solamente informa que está configurada. No muestra su contenido.

Por último, si Docker está disponible, construimos una imagen de demostración que contiene deliberadamente una clave falsa dentro de una instrucción `ENV`. El comando `docker history` permite ver que ese valor quedó registrado en el historial de la imagen. Esta última parte es un ejemplo de lo que no debemos hacer. Ahora vamos a revisar cómo se implementan las validaciones y cómo se configura Railway.”

## 2. El objeto Settings y la validación fail fast · 1:15–3:40

[Abre `api/config.py`, líneas 1–29. Después muestra las líneas 32–54.]

**Narración:**

“Este archivo centraliza la configuración de la aplicación. En lugar de leer variables de entorno de forma dispersa por distintos módulos, definimos un objeto llamado `Settings`.

La clase contiene el entorno de ejecución, la clave de OpenAI, el modelo, el modo simulado, la versión y el puerto. La clave está declarada como `SecretStr`, un tipo de Pydantic pensado para manejar valores sensibles. Cuando representamos el objeto, Pydantic evita mostrar el contenido del secreto como si fuera un texto normal.

El método `desde_entorno` construye el objeto leyendo las variables del proceso. Por ejemplo, `APP_ENV` determina si estamos ejecutando en local, en pruebas o en producción. `OPENAI_API_KEY` contiene la credencial del proveedor y `LLM_MODO_SIMULADO` indica si estamos utilizando la respuesta de prueba en lugar de realizar una llamada real al modelo.

La función `validar_secretos` concentra las reglas. Primero obtiene el valor interno de la clave y comprueba si está vacío. Si el modo simulado está desactivado, la clave es obligatoria. Además, cuando `APP_ENV` es `produccion`, el modo simulado está prohibido. También se comprueba que el nombre del entorno pertenezca a los valores admitidos.

Esto es lo que llamamos fail fast: detectar una configuración inválida al inicio, en vez de permitir que el servicio arranque y falle más tarde durante una operación real.

La función `resumen_seguro` tiene otra responsabilidad. Construye un resumen útil para los logs, pero reemplaza el contenido de la clave por las palabras `configurada` o `ausente`. Así podemos diagnosticar la configuración sin escribir el secreto en la consola.”

## 3. Cómo se aplica la validación al iniciar · 3:40–4:40

[Abre `api/configuracion.py`, líneas 1–11. Luego abre `app.py`, líneas 16–22 y 52–60.]

**Narración:**

“`api/configuracion.py` mantiene la compatibilidad con los módulos que ya existían en el servicio. Primero carga el archivo `.env` y después crea el objeto `Settings` a partir de las variables disponibles. También expone nombres como `OPENAI_API_KEY`, `OPENAI_MODEL` y `DATA_FILE`, que siguen utilizando otros módulos.

En `app.py` definimos el ciclo de vida de FastAPI mediante `lifespan`. Antes de que la aplicación empiece a atender peticiones, llamamos a `validar_secretos`. Si hay problemas, lanzamos una excepción y el proceso no completa el arranque. Si todo está correcto, escribimos el resumen seguro en el log.

El endpoint `/ready` comprueba la configuración y verifica que el CSV de vuelos exista. Si falta alguna condición, devuelve HTTP 503. Si está todo disponible, responde con `status: ready`.

Hay una diferencia importante: `/ready` comprueba que la clave esté presente, no que OpenAI la haya aceptado. No hacemos una llamada al modelo cada vez que Railway consulta el healthcheck, porque eso generaría consumo y añadiría una dependencia externa a una comprobación de infraestructura. La validez real de la credencial se comprueba con una consulta funcional.”

## 4. El secreto no debe formar parte de la imagen · 4:40–5:30

[Abre `Dockerfile.secreto-demo`, líneas 1–4. Después muestra el `.dockerignore` y `.env.example`.]

**Narración:**

“Este archivo contiene un ejemplo intencionalmente inseguro. La instrucción `ENV` incorpora una clave falsa directamente a la imagen. Aunque después elimináramos la variable del contenedor, el valor puede seguir siendo visible en el historial de capas.

Por eso no ponemos claves en el Dockerfile, no las pasamos como argumentos de construcción y no copiamos `.env` a la imagen. El archivo `.env.example` contiene nombres y valores de ejemplo, pero no debe contener una credencial real. El archivo `.gitignore` evita que nuestro `.env` local termine en el repositorio y `.dockerignore` evita que entre en el contexto de construcción.

La forma correcta es inyectar el secreto en tiempo de ejecución. En nuestra máquina lo hacemos mediante el archivo `.env`. En Railway lo configuraremos como una variable protegida del servicio.”

## 5. Crear el proyecto y configurar Railway · 5:30–8:20

[Abre el navegador y entra al dashboard de Railway. Crea un proyecto desde el repositorio GitHub. Cuando aparezca la opción para configurar variables antes del despliegue, utilízala.]

Configura estas variables en el servicio:

```text
APP_ENV=produccion
LLM_MODO_SIMULADO=false
OPENAI_API_KEY=<tu clave real de OpenAI>
DEMO_API_KEY_WEB_LUCIA=<clave demo de Lucía>
DEMO_API_KEY_WEB_ANDRES=<clave demo de Andrés>
DEMO_API_KEY_KIOSCO=<clave demo del kiosco>
APP_VERSION=1.0.0
```

[No muestres los valores de las claves en pantalla. No configures manualmente `PORT`; Railway lo inyecta. Muestra `railway.json`.]

**Narración:**

“Ahora vamos a crear el servicio público. En Railway seleccionamos la opción para desplegar desde un repositorio de GitHub y elegimos el repositorio de OrbitAir. Antes de iniciar el primer despliegue, entramos a la configuración de variables.

La primera variable es `APP_ENV`, que establecemos en `produccion`. Desactivamos el modo simulado y configuramos una clave real de OpenAI. También agregamos las credenciales de los tres clientes de demostración. Estas claves se utilizan para autenticar las peticiones de nuestra API. En producción, el código espera recibirlas mediante variables de entorno y no acepta las claves locales de respaldo del archivo JSON.

No necesitamos definir `PORT`. Railway asigna ese puerto y lo entrega al contenedor. Nuestro Dockerfile ya está preparado para leer esa variable cuando inicia Uvicorn.

Veamos ahora `railway.json`. Este archivo le indica a Railway que debe construir utilizando nuestro Dockerfile. También define `/ready` como healthcheck y establece un tiempo máximo de espera. Railway inicia el contenedor y espera que la aplicación esté lista antes de marcar el despliegue como activo.

Cuando las variables estén guardadas, iniciamos el despliegue. La primera construcción puede tardar varios minutos porque Railway tiene que descargar la imagen base, instalar dependencias y preparar el contenedor. El tiempo exacto depende de la cache y de la infraestructura.”

## 6. Obtener una URL y comprobar el servicio · 8:20–9:00

[En el servicio, abre la configuración de Networking o Public Networking y genera un dominio. Cuando esté activo, utiliza la URL asignada.]

```bash
BASE_URL="https://TU-DOMINIO.up.railway.app"
curl -i "$BASE_URL/health"
curl -i "$BASE_URL/ready"
curl -i "$BASE_URL/version"
```

[Realiza una petición sin credencial y luego otra autenticada. No muestres el valor de la API key.]

```bash
curl -i -X POST "$BASE_URL/v1/consultas" \
  -H 'Content-Type: application/json' \
  -d '{"mensaje":"¿Cómo viene el vuelo OA1203?"}'
```

```bash
curl -i -X POST "$BASE_URL/v1/consultas" \
  -H "Authorization: Bearer $DEMO_API_KEY_WEB_LUCIA" \
  -H 'X-Request-ID: demo-railway-001' \
  -H 'Content-Type: application/json' \
  -d '{"mensaje":"¿Cómo viene el vuelo OA1203?"}'
```

[Si la variable no está disponible en esa terminal, pega la credencial demo sin dejarla visible en la grabación. Muestra el `401` de la primera petición y el `200` de la segunda. Después muestra los logs del servicio.]

**Narración:**

“Con el dominio generado ya podemos comprobar el servicio desde fuera de nuestra computadora. `/health` debe responder 200, `/ready` debe responder 200 y `/version` debe mostrar la versión configurada.

La petición sin credencial debe devolver 401. La petición autenticada debe devolver 200 y una respuesta del agente. En esta última envié también un encabezado `X-Request-ID` de demostración. La aplicación lo devuelve en la respuesta y lo registra en una línea JSON con el método, la ruta, el código HTTP y la duración.

Ya tenemos OrbitAir publicado en una URL pública, con la configuración separada del código y con secretos inyectados en tiempo de ejecución. Si utilizas un plan de prueba, revisa la fecha de vencimiento y los créditos disponibles en el panel de facturación de Railway; no asumas que el periodo o los límites son iguales para todas las cuentas.”

---

# Video 3 · CI con GitHub Actions

**Duración objetivo: 5 minutos.**  
**Objetivo:** mostrar cómo GitHub Actions ejecuta pruebas, valida la imagen y permite desplegar solamente cuando las comprobaciones anteriores terminan correctamente.

## 1. Ejecutar el pipeline · 0:00–1:00

[Confirma que el repositorio está en GitHub y que el archivo `.github/workflows/ci.yml` ya está en la rama principal. Comprueba que agregaste los secretos `RAILWAY_TOKEN` y `RAILWAY_SERVICE` en GitHub. Haz un commit pequeño y súbelo a `main`:]

```bash
git add .
git commit -m "Run OrbitAir deployment pipeline"
git push origin main
```

[Abre GitHub → Actions y selecciona la ejecución más reciente.]

**Qué debe aparecer:**

- Un job `test` que instala dependencias y ejecuta pytest. La salida esperada es `10 passed`.
- Un job `imagen` que espera a `test`, construye Docker, levanta el contenedor y realiza una consulta simulada.
- Un job `deploy` que espera a los dos anteriores y se ejecuta únicamente para un push a `main`.
- Si falta `RAILWAY_TOKEN` o `RAILWAY_SERVICE`, el job de deploy termina con un mensaje explícito indicando qué secreto falta.

**Narración:**

“Voy a comenzar provocando una ejecución del pipeline con un push a la rama principal. En GitHub abro la pestaña Actions y selecciono la ejecución más reciente.

Aquí vemos tres trabajos. El primero se llama `test`, el segundo `imagen` y el tercero `deploy`. No son tres nombres decorativos: cada uno tiene una responsabilidad y existen dependencias entre ellos. El job de imagen espera a que las pruebas terminen correctamente. El job de deploy espera a que tanto las pruebas como la imagen hayan sido validadas.

Si alguno de los trabajos requeridos falla, GitHub no ejecuta los trabajos que dependen de él. De esa manera, un cambio que no supera las comprobaciones no llega al paso de despliegue.”

## 2. El job test · 1:00–2:00

[Abre `.github/workflows/ci.yml`, líneas 1–34.]

**Narración:**

“Empecemos por el archivo del workflow. La sección `on` define cuándo se ejecuta: cuando hay un push a `main` o cuando se crea o actualiza un pull request.

El primer job se llama `test` y utiliza un runner de Ubuntu. Antes de ejecutar las pruebas, descarga el repositorio, configura Python 3.12 e instala las dependencias fijadas en `requirements.lock` y `requirements-dev.lock`.

Hay una decisión importante en las variables de entorno. El workflow establece `APP_ENV=test`, activa `LLM_MODO_SIMULADO` y deja la clave de OpenAI vacía. Esto es intencional. Las pruebas del pipeline no deben consumir tokens ni depender de una API externa. Tampoco debemos entregar secretos a un pull request que podría venir de un fork.

Cuando ejecutamos `pytest -q`, se comprueban las reglas de configuración, los endpoints principales, la autenticación y la decisión de promoción. En una ejecución correcta esperamos diez pruebas aprobadas.”

## 3. El job imagen y la limpieza · 2:00–3:30

[Abre `.github/workflows/ci.yml`, líneas 36–65.]

**Narración:**

“El segundo trabajo se llama `imagen` y tiene `needs: test`. Esa propiedad expresa que necesita que el job de pruebas termine correctamente. Si las pruebas fallan, este trabajo no se ejecuta.

Dentro de este job primero construimos la imagen con el Dockerfile productivo. Después iniciamos un contenedor en el runner de GitHub, con el modo simulado activado. Esperamos a que `/ready` responda y realizamos una petición autenticada para consultar el vuelo OA1203.

Esto comprueba algo diferente de las pruebas unitarias. No solamente verificamos funciones aisladas: también construimos la imagen real, iniciamos el servidor dentro de ella y hacemos una petición HTTP de punta a punta.

Al final aparece un paso con `if: always()`. Esa condición es importante. Indica que queremos ejecutar la limpieza incluso si un paso anterior falla. Por eso mostramos los logs del contenedor y después lo eliminamos. Si la consulta falla, los logs quedan disponibles para diagnosticar el problema y no dejamos el contenedor abandonado en el runner.”

## 4. El job deploy y la protección de la rama principal · 3:30–4:30

[Abre `.github/workflows/ci.yml`, líneas 67–90.]

**Narración:**

“El tercer job se llama `deploy`. Tiene una dependencia de los dos trabajos anteriores, así que solamente puede comenzar cuando las pruebas y la construcción de la imagen han terminado correctamente.

También tiene una condición: se ejecuta cuando el evento es un push y la rama es `main`. Por eso un pull request puede ejecutar las pruebas y la construcción de la imagen, pero no despliega directamente a producción.

Para conectarse con Railway utilizamos el CLI oficial. El workflow instala la herramienta y ejecuta `railway up --ci`. La autenticación se realiza con el secreto `RAILWAY_TOKEN`, y `RAILWAY_SERVICE` identifica el servicio al que vamos a desplegar. Esos valores se guardan en GitHub, en Settings, Secrets and variables, Actions. No se escriben en el YAML ni se imprimen en los logs.

En esta configuración GitHub Actions es quien realiza el despliegue mediante Railway CLI. Por eso no debemos activar al mismo tiempo un segundo autodeploy del mismo repositorio desde Railway con `Wait for CI`: estaríamos habilitando dos mecanismos de despliegue para el mismo cambio. Si prefieres que Railway gestione el autodeploy desde GitHub, puedes desactivar el job `deploy` de este workflow y activar `Wait for CI` en Railway. Debe quedar un único mecanismo responsable de desplegar.”

## 5. Demostrar que el pipeline frena un cambio roto · 4:30–5:00

[Para la demostración, crea una rama temporal y cambia intencionalmente una aserción de `tests/test_config.py` para que falle. No dejes ese cambio en `main`.]

```bash
git switch -c demo-ci-falla
git add tests/test_config.py
git commit -m "Demonstrate failing test"
git push -u origin demo-ci-falla
```

[Abre un pull request. Muestra el job `test` en rojo y los jobs dependientes sin ejecutar. Después descarta o revierte el cambio de demostración.]

**Narración:**

“Para comprobar que esta protección funciona, voy a crear una rama temporal con una prueba que falla intencionalmente y abrir un pull request. El job `test` queda en rojo. Como `imagen` depende de `test`, no se ejecuta. Y como `deploy` depende de ambos y además está limitado a la rama principal, no se despliega nada.

Ese es el objetivo del pipeline: detectar el error durante la integración, antes de que llegue a los usuarios. Una vez corregida la prueba, el pull request puede volver a pasar las comprobaciones y el cambio se integra siguiendo las reglas del repositorio.”

---

# Video 4 · Smoke test y rollback en Railway

**Duración objetivo: 7 minutos.**  
**Objetivo:** mostrar por qué un healthcheck correcto no garantiza que el servicio funcione de punta a punta, cómo ejecutar un smoke test y cómo volver a un despliegue sano.

## 1. Provocar el fallo sin detener el servicio · 0:00–1:30

[En Railway, abre las variables del servicio. Cambia temporalmente `OPENAI_API_KEY` por el texto falso `sk-ESTA-ES-UNA-CLAVE-FALSA`. No uses ni revoques una clave real para esta demostración. Aplica los cambios y espera a que termine el nuevo despliegue.]

[Cuando el servicio aparezca activo, ejecuta:]

```bash
BASE_URL="https://TU-DOMINIO.up.railway.app"
curl -i "$BASE_URL/health"
curl -i "$BASE_URL/ready"
```

**Qué debe aparecer:** ambos endpoints responden HTTP 200. `/ready` indica `status: ready`, porque la variable existe y no está vacía. La clave es falsa, pero el healthcheck no realiza una llamada al modelo.

**Narración:**

“Voy a comenzar con un escenario que puede ocurrir en producción. El servicio tiene una clave de OpenAI que está presente, pero no es válida. Para reproducirlo no voy a revocar una credencial real: simplemente voy a sustituirla temporalmente por un texto falso.

Después de aplicar la variable, Railway vuelve a desplegar el servicio. Cuando termina, consulto `/health` y `/ready`. Los dos responden 200. Esto puede parecer extraño, pero es el comportamiento esperado con el diseño actual.

`/health` comprueba que el proceso responde. `/ready` comprueba que la configuración requerida está presente y que el archivo de vuelos existe. Ninguno de los dos realiza una llamada facturable al proveedor de IA. La aplicación ve que `OPENAI_API_KEY` tiene un valor y por eso supera la validación de presencia.

Pero una clave presente no necesariamente es una clave válida. Para descubrir ese problema necesitamos ejecutar una operación real de la aplicación.”

## 2. Ejecutar el smoke test · 1:30–3:30

[Desde la raíz del proyecto, con el entorno virtual activo y las dependencias instaladas, ejecuta el smoke test contra el dominio real.]

```bash
python3 scripts/l2_v4_smoke.py https://TU-DOMINIO.up.railway.app
```

**Qué debe aparecer con la clave falsa:**

- `GET /health`: crítico, OK, HTTP 200.
- `GET /ready`: crítico, OK, HTTP 200.
- `401 sin API key`: crítico, OK, HTTP 401.
- `Consulta real de punta a punta`: crítico, FALLO, normalmente HTTP 502 por el rechazo del proveedor.
- `Latencia de /health`: advertencia; puede quedar OK o FALLO según el tiempo medido.
- `SSE: secuencia completa de progreso`: advertencia; puede variar según el tiempo y la respuesta del proveedor.
- La decisión final debe ser `NO PROMOVER`, porque existe al menos un fallo crítico.

[Deja la salida completa visible. Señala que el script continúa después de la consulta fallida y ejecuta el resto de las comprobaciones.]

**Narración:**

“Ahora ejecuto el smoke test. Este script está pensado para comprobar el servicio desplegado desde fuera, usando su URL pública.

La primera comprobación consulta `/health`. La segunda consulta `/ready`. La tercera envía una petición sin API key y espera recibir 401. Estas tres comprobaciones nos dicen si el servicio responde, si declara estar listo y si protege correctamente el endpoint.

La cuarta prueba es la más importante: realiza una consulta autenticada para preguntar por el vuelo OA1203. Esta operación sí llega al proveedor de IA. Como la clave que configuramos es falsa, esperamos que la petición no pueda completarse y que la API devuelva un error controlado, normalmente 502.

Después se miden dos aspectos adicionales: la latencia de `/health` y la recepción del primer evento del endpoint SSE. Estos dos resultados son advertencias, no condiciones críticas para promover la versión en este ejemplo.

Fijémonos en algo importante: el script no termina cuando encuentra el primer error. Ejecuta todas las comprobaciones y nos entrega un diagnóstico completo. Además, no modifica reservas ni datos de negocio. La consulta únicamente lee el vuelo de demostración.”

## 3. Cómo está implementado verificar_deploy · 3:30–4:45

[Abre `scripts/l2_v4_smoke.py`, líneas 1–19, después 21–45 y finalmente 47–74.]

**Narración:**

“La función principal de este script se llama `verificar_deploy`. Recibe la URL base del servicio y prepara una lista de resultados.

Dentro definimos una función auxiliar llamada `comprobar`. Esta función recibe el nombre de una prueba, la operación que debe ejecutar y un indicador que determina si el resultado es crítico. Ejecuta la operación dentro de un bloque `try`. Si la petición genera una excepción, la captura y la registra como fallo. Después calcula cuánto tardó y agrega el resultado a la lista.

Esta estructura es la que permite continuar con el diagnóstico. Cada comprobación está aislada. Si falla la consulta al modelo, todavía podemos medir la latencia y probar el primer evento del stream.

Las comprobaciones de `/health`, `/ready`, la respuesta 401 y la consulta completa están marcadas como críticas. La latencia y el primer evento SSE están marcados como advertencias. Esa distinción evita que una medición orientativa bloquee automáticamente una versión cuando los servicios esenciales sí funcionan.”

## 4. La decisión de promoción · 4:45–5:30

[Abre `api/releases.py`, líneas 1–11.]

**Narración:**

“Después de ejecutar las comprobaciones necesitamos decidir si la versión puede promoverse. Esa regla está en `api/releases.py`, dentro de `decidir_promocion`.

La función recibe la lista de resultados y filtra aquellos que están marcados como críticos y que no fueron aprobados. Si la lista de fallos críticos queda vacía, la decisión es `PROMOVER`. Si existe al menos uno, la decisión es `NO PROMOVER`.

Esto significa que una advertencia de latencia puede aparecer en el informe sin bloquear por sí sola el release. En cambio, una consulta real que falla sí bloquea la promoción. La regla queda expresada en código, así que no depende de que una persona interprete manualmente cada línea de salida.”

## 5. Hacer rollback en Railway · 5:30–6:30

[En Railway abre el servicio y entra a la pestaña `Deployments`. Localiza el despliegue anterior que sabes que funcionaba. Abre el menú de tres puntos de ese despliegue y selecciona `Rollback`. Confirma la operación.]

[Espera a que el despliegue anterior vuelva a quedar activo. Luego ejecuta otra vez:]

```bash
python3 scripts/l2_v4_smoke.py https://TU-DOMINIO.up.railway.app
```

**Qué debe aparecer:** las cuatro comprobaciones críticas en OK. El stream debería completar la secuencia `inicio`, `herramienta`, `fin`. La latencia y el streaming son advertencias y pueden variar. La decisión debe ser `PROMOVER`.

**Narración:**

“Como el smoke test detectó un fallo crítico, no debemos mantener esta versión como release válido. Voy a volver a Railway y abrir la pestaña Deployments.

Busco el despliegue anterior que ya había funcionado. En su menú de tres puntos selecciono `Rollback` y confirmo. Railway vuelve a activar ese despliegue anterior. En este proceso se recuperan la imagen y las variables asociadas a ese despliegue, de modo que no estamos intentando reparar la clave manualmente sobre una versión defectuosa.

Cuando el rollback termina, ejecuto el smoke test otra vez. Ahora esperamos que la consulta real vuelva a responder correctamente y que la decisión sea `PROMOVER`.

Rollback no significa modificar el código que falló. Significa volver a una versión desplegada que ya conocemos y que podemos recuperar rápidamente.”

## 6. Alternativa reproducible con Git · 6:30–7:00

[En una terminal muestra el comando como alternativa, sin ejecutarlo si ya hiciste el rollback desde Railway.]

```bash
git revert <SHA-DEL-COMMIT>
git push origin main
```

**Narración:**

“También existe una alternativa cuando el problema proviene de un cambio de código. Podemos utilizar `git revert` indicando el commit que introdujo el error y subir ese nuevo commit a la rama principal.

A diferencia de un rollback de plataforma, `git revert` crea un commit nuevo que deshace los cambios anteriores. Ese commit vuelve a pasar por el pipeline de GitHub Actions y, si supera las comprobaciones, se despliega como una nueva versión.

La idea central es sencilla: el healthcheck nos dice si el proceso está vivo y listo según sus comprobaciones básicas; el smoke test nos dice si las operaciones importantes funcionan de verdad; y el rollback nos permite recuperar una versión sana cuando detectamos un fallo crítico.”

---

## Referencias oficiales para el speaker

Estas páginas sirven para verificar la interfaz y los comandos de Railway antes de grabar, porque el panel puede cambiar:

- Railway, despliegue desde GitHub: https://docs.railway.com/quick-start
- Railway, configuración de servicios: https://docs.railway.com/services
- Railway CLI, despliegue desde CI: https://docs.railway.com/cli/deploying
- Railway, acciones de despliegue y rollback: https://docs.railway.com/deployments/deployment-actions
- Railway, referencia de despliegues y healthchecks: https://docs.railway.com/deployments/reference
- GitHub Actions, sintaxis de workflows y dependencias `needs`: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

## Comprobaciones antes de grabar

- [ ] `.env` existe y contiene una API key real de OpenAI.
- [ ] Docker está iniciado y puede construir imágenes.
- [ ] `bash scripts/l2_v1_imagen.sh` completa la consulta real y elimina el contenedor.
- [ ] `bash scripts/l2_v2_config.sh` muestra los rechazos y el resumen seguro.
- [ ] El repositorio está publicado en GitHub con `.github/workflows/ci.yml`.
- [ ] Railway tiene configuradas las variables de producción y las credenciales demo.
- [ ] El dominio público responde en `/health`, `/ready` y `/version`.
- [ ] GitHub tiene los secretos `RAILWAY_TOKEN` y `RAILWAY_SERVICE` si se utilizará el job `deploy` del workflow.
- [ ] El smoke test se probó con una clave válida y con la clave falsa de demostración.
- [ ] Existe al menos un despliegue anterior exitoso disponible para demostrar el rollback.

**Nota de ejecución:** no pude ejecutar Docker ni llamadas reales a OpenAI/Railway desde este entorno. El código Python y Bash sí se revisó estáticamente; antes de grabar, ejecuta los comandos de esta lista en tu máquina y confirma la salida real de tus cuentas y servicios.
