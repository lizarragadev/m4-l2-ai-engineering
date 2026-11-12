#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
validacion='from api.config import Settings, validar_secretos; c=Settings.desde_entorno(); p=validar_secretos(c); print("ERROR:", "; ".join(p)) if p else print("Configuración válida"); raise SystemExit(1 if p else 0)'
echo '== Sin OPENAI_API_KEY: debe rechazarse =='
if env -u OPENAI_API_KEY APP_ENV=local LLM_MODO_SIMULADO=false python3 -c "$validacion"; then
  echo 'ERROR: la configuración sin clave fue aceptada.'; exit 1
else
  echo 'Correcto: el arranque se rechazaría porque falta la clave.'
fi
echo '== OPENAI_API_KEY vacía: también debe rechazarse =='
if OPENAI_API_KEY='' APP_ENV=local LLM_MODO_SIMULADO=false python3 -c "$validacion"; then
  echo 'ERROR: la clave vacía fue aceptada.'; exit 1
else
  echo 'Correcto: una cadena vacía se trata como secreto ausente.'
fi
echo '== Resumen seguro: muestra presencia, nunca el valor =='
OPENAI_API_KEY='sk-ESTA-CLAVE-NO-DEBE-APARECER' APP_ENV=local python3 -c 'from api.config import Settings, resumen_seguro; print(resumen_seguro(Settings.desde_entorno()))'
if command -v docker >/dev/null 2>&1; then
  echo '== Anti-patrón: secreto embebido en una capa de imagen =='
  docker build -f Dockerfile.secreto-demo -t orbitair:secreto-demo .
  docker history --no-trunc orbitair:secreto-demo | head -n 8
  docker image rm orbitair:secreto-demo >/dev/null
else
  echo 'Docker no está disponible; ejecuta manualmente Dockerfile.secreto-demo y docker history.'
fi
