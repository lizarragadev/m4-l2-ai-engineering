#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
echo "1) Health: proceso vivo"
curl -sS -i "$BASE_URL/health"
echo -e "\n2) Ready: configuración y CSV disponibles"
curl -sS -i "$BASE_URL/ready"
echo -e "\n3) Version de la aplicación"
curl -sS -i "$BASE_URL/version"
echo -e "\n4) Error de validación: FastAPI responde 422 con su formato detail"
curl -sS -i -X POST "$BASE_URL/v1/consultas" -H "Authorization: Bearer $KEY_LUCIA" -H "Content-Type: application/json" -d '{}'
echo -e "\n5) Manejadores ErrorHTTP y excepción general, sin iniciar otro servidor"
python3 scripts/probar_manejador_http.py
echo -e "\n6) RateLimitError simulado localmente, sin consumir API"
python3 scripts/probar_rate_limit.py
