#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
echo "1) Progreso SSE: inicio, herramienta y fin"
time curl -N -sS -G "$BASE_URL/v1/consultas/stream" -H "Authorization: Bearer $KEY_LUCIA" --data-urlencode "mensaje=¿Cómo viene el vuelo OA1203?"
echo -e "\n2) Streaming de tokens: fragmentos y [DONE]"
curl -N -sS -G "$BASE_URL/v1/tokens/stream" -H "Authorization: Bearer $KEY_LUCIA" --data-urlencode "mensaje=Explica en dos frases qué es el check-in."
echo -e "\n3) Error después del primer evento: el HTTP ya fue 200"
curl -N -sS -G "$BASE_URL/v1/consultas/stream" -H "Authorization: Bearer $KEY_LUCIA" --data-urlencode "mensaje=Consulta OA1203" --data-urlencode "forzar_error=true"
