#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
echo "1) Body vacío: se espera HTTP 422"
curl -sS -i -X POST "$BASE_URL/v1/consultas" -H "Authorization: Bearer $KEY_LUCIA" -H "Content-Type: application/json" -d '{}'
echo -e "\n2) Campo no declarado: se espera HTTP 422"
curl -sS -i -X POST "$BASE_URL/v1/consultas" -H "Authorization: Bearer $KEY_LUCIA" -H "Content-Type: application/json" -d '{"mensaje":"Estado OA1203","pasajero_id":"P-1002"}'
echo -e "\n3) Consulta válida: se espera HTTP 200"
curl -sS -i -X POST "$BASE_URL/v1/consultas" -H "Authorization: Bearer $KEY_LUCIA" -H "Content-Type: application/json" -d '{"mensaje":"¿Cómo viene el vuelo OA1203?"}'
