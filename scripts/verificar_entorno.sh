#!/usr/bin/env bash
set -euo pipefail
python3 --version
python3 -c 'from api.agente import HERRAMIENTAS; print("Herramienta registrada:", HERRAMIENTAS[0]["function"]["name"])'
python3 -c 'from api.dependencias import obtener_cliente; print("Módulos de OrbitAir importados correctamente")'
