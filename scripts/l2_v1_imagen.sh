#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -f .env ]]; then
  echo 'Falta .env. Ejecuta cp .env.example .env y configura OPENAI_API_KEY.' >&2
  exit 1
fi
if ! grep -Eq '^OPENAI_API_KEY=[^[:space:]]+' .env; then
  echo 'OPENAI_API_KEY está vacía en .env. Se necesita una clave real para esta demo.' >&2
  exit 1
fi
IMAGE_TUTORIAL="orbitair:tutorial"
IMAGE_PROD="orbitair:prod"
echo '== Construcción didáctica =='
docker build -f Dockerfile.tutorial -t "$IMAGE_TUTORIAL" .
echo '== Construcción productiva =='
docker build -f Dockerfile -t "$IMAGE_PROD" .
echo '== Cambio de código simulado para observar la cache =='
MARKER=.cache-demo-marker
trap 'rm -f "$MARKER"' EXIT
date > "$MARKER"
echo 'Reconstrucción tutorial: COPY . . invalida también la capa de pip install.'
time docker build -f Dockerfile.tutorial -t "$IMAGE_TUTORIAL" .
echo 'Reconstrucción productiva: requirements.lock no cambió; la capa de dependencias se conserva.'
time docker build -f Dockerfile -t "$IMAGE_PROD" .
rm -f "$MARKER"
trap - EXIT
echo '== Tamaños comparables =='
docker image ls orbitair --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}'
echo '== Ejecutar la imagen productiva con configuración externa =='
docker rm -f orbitair-demo >/dev/null 2>&1 || true
docker run -d --name orbitair-demo -p 8000:8000 --env-file .env \
  -e APP_ENV=local -e LLM_MODO_SIMULADO=false -e PORT=8000 "$IMAGE_PROD"
trap 'docker rm -f orbitair-demo >/dev/null 2>&1 || true' EXIT
for i in $(seq 1 30); do
  if docker inspect --format='{{.State.Health.Status}}' orbitair-demo 2>/dev/null | grep -q healthy; then break; fi
  sleep 2
done
ESTADO=$(docker inspect --format='{{.State.Health.Status}}' orbitair-demo)
if [[ "$ESTADO" != "healthy" ]]; then
  docker logs orbitair-demo
  echo "El contenedor no alcanzó estado healthy: $ESTADO" >&2
  exit 1
fi
docker ps --filter name=orbitair-demo --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
echo '== Healthcheck =='
curl --fail-with-body -i http://127.0.0.1:8000/health
echo '== Consulta real al agente =='
KEY_LUCIA="$(grep -m1 '^DEMO_API_KEY_WEB_LUCIA=' .env | cut -d= -f2-)"
KEY_LUCIA="${KEY_LUCIA:-oa_lucia_demo_2026_key_7f3a91}"
curl --fail-with-body -i -X POST http://127.0.0.1:8000/v1/consultas \
  -H "Authorization: Bearer ${KEY_LUCIA}" \
  -H 'Content-Type: application/json' \
  -d '{"mensaje":"¿Cómo viene el vuelo OA1203?"}'
docker rm -f orbitair-demo >/dev/null
trap - EXIT
