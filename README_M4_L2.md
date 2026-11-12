# OrbitAir API · M4 L2 Deploy

Extensión de L1 para enseñar imagen Docker productiva, configuración segura, despliegue en Railway, CI con GitHub Actions, smoke tests y rollback.

## Requisitos

- Docker Desktop o Docker Engine con Docker Compose.
- Python 3.12 para ejecutar los scripts locales.
- Cuenta de OpenAI API con crédito disponible para la ejecución real.
- Repositorio GitHub y cuenta Railway para los videos 2 a 4.

## Preparación

```bash
cp .env.example .env
```

Completa `OPENAI_API_KEY` con una clave válida. No la muestres ni la publiques. Mantén `LLM_MODO_SIMULADO=false` para usar OpenAI. Para ejecutar pruebas sin costo, el CI configura `LLM_MODO_SIMULADO=true`; ese modo está prohibido en `APP_ENV=produccion`.

Instala dependencias locales si vas a ejecutar scripts Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.lock -r requirements-dev.lock
```

Para correr las pruebas localmente sin consumir API, activa el modo de test solo para ese comando:

```bash
APP_ENV=test LLM_MODO_SIMULADO=true OPENAI_API_KEY= pytest -q
```

## Video 1: Docker

```bash
bash scripts/l2_v1_imagen.sh
```

El script construye `Dockerfile.tutorial` y `Dockerfile`, compara tamaños, simula un cambio para mostrar la diferencia de cache y ejecuta el contenedor productivo con variables externas y realiza una consulta real a OpenAI. El script elimina el contenedor al terminar.

Para levantar con Compose y una clave real:

```bash
docker compose up --build
```

Abre `http://localhost:8000/docs`. Detén con `Ctrl+C`.

## Video 2: configuración y Railway

Pruebas locales de configuración:

```bash
bash scripts/l2_v2_config.sh
```

El script comprueba clave ausente, clave vacía y resumen sin revelar el secreto. Publica el repositorio en GitHub. En Railway crea un proyecto desde el repositorio y configura estas variables en el servicio:

- `APP_ENV=produccion`
- `LLM_MODO_SIMULADO=false`
- `OPENAI_API_KEY` (secreto real de OpenAI)
- `DEMO_API_KEY_WEB_LUCIA` (credencial demo para smoke test)
- `DEMO_API_KEY_WEB_ANDRES`
- `DEMO_API_KEY_KIOSCO`

Railway inyecta `PORT`. `railway.json` selecciona Dockerfile y usa `/ready` como healthcheck. Genera un dominio público desde los ajustes de Networking/Domains del servicio.

## Video 3: GitHub Actions

El workflow `.github/workflows/ci.yml` tiene tres jobs: `test`, `imagen` y `deploy`. Los dos primeros usan modo simulado y no necesitan OpenAI. Para habilitar el job de deploy agrega en GitHub → Settings → Secrets and variables → Actions:

- `RAILWAY_TOKEN`: Project Token de Railway.
- `RAILWAY_SERVICE`: nombre o ID del servicio Railway.

El job `deploy` solo corre en push a `main`, después de `test` e `imagen`.

**Importante sobre Wait for CI:** este repositorio usa el job `deploy` de GitHub Actions para ejecutar `railway up`. No habilites simultáneamente un autodeploy independiente desde GitHub en Railway con Wait for CI, porque tendrías dos mecanismos de despliegue para el mismo push. Si prefieres que Railway gestione el autodeploy, elimina/desactiva el job `deploy` del workflow y habilita Wait for CI en el servicio Railway; conserva `test` e `imagen` como checks requeridos.

## Video 4: smoke test y rollback

Instala dependencias si aún no lo hiciste:

```bash
python3 -m pip install -r requirements.lock -r requirements-dev.lock
```

Ejecuta el smoke test contra la URL pública:

```bash
python3 scripts/l2_v4_smoke.py https://TU-DOMINIO.up.railway.app
```

Usa `DEMO_API_KEY_WEB_LUCIA` del entorno o la credencial demo incluida en `.env.example`. El smoke test verifica `/health`, `/ready`, 401 sin credencial, consulta real de punta a punta y SSE. La latencia y SSE son advertencias; los cuatro primeros chequeos son críticos.

La función `decidir_promocion` se puede probar con:

```bash
python3 scripts/decidir_promocion.py
```

Devuelve `NO PROMOVER` porque el ejemplo incluye una consulta crítica fallida.

## Límites y seguridad

- No guardes `OPENAI_API_KEY` ni tokens Railway en Git, Dockerfile o imagen.
- Las API keys demo incluidas son únicamente para el laboratorio; no son credenciales de producción.
- El modo simulado sirve para CI y no valida la conectividad ni autenticación real con OpenAI.
- `/ready` valida configuración presente y archivos locales, no que la clave sea aceptada por OpenAI. El smoke test de consulta completa detecta ese tipo de fallo.
- Las sesiones siguen en memoria del proceso. No son persistentes ni aptas para varias réplicas.
- Rollback en Railway vuelve a un despliegue previo. `git revert` crea un commit nuevo que debe volver a pasar CI.
