"""Prueba local: traduce un RateLimitError simulado sin llamar a OpenAI."""
import httpx
from openai import RateLimitError
from api.errores_http import traducir_error, cuerpo_error

request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
response = httpx.Response(429, request=request)
error_simulado = RateLimitError("Rate limit de demostración", response=response, body={})
error_http = traducir_error(error_simulado)
print("HTTP:", error_http.status_code)
print("Retry-After:", error_http.headers["Retry-After"])
print(cuerpo_error(error_http.codigo, error_http.mensaje, "demo-rate-limit-001"))
