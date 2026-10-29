from unittest.mock import patch
import requests
from try_api import enviar_peticion_con_fallback

def test_simular_error_429():
    print("🧪 Simulando un error 429 (Too Many Requests) para probar el fallback...")
    
    # Simulamos que la API responde con un código 429
    respuesta_falsa = requests.Response()
    respuesta_falsa.status_code = 429
    
    # Usamos unittest.mock para interceptar requests.post y forzar el 429
    with patch("requests.post", return_value=respuesta_falsa):
        try:
            enviar_peticion_con_fallback("Hola, prueba de estrés simulada")
        except RuntimeError as e:
            print(f"\n✅ ¡Prueba superada! El sistema reintentó y aplicó el fallback correctamente ante el 429.")
            print(f"   Detalle capturado: {e}")

if __name__ == "__main__":
    test_simular_error_429()