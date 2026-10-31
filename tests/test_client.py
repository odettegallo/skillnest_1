from unittest.mock import patch, Mock
import pytest
import requests
import try_api
from try_api import (
    enviar_peticion_con_fallback,
    registrar_costo,
)
from client import consultar_modelo


def test_enviar_peticion_credencial_invalida():
    """Verifica que ante una credencial inválida (401/403) se lance ValueError inmediatamente sin reintentar."""
    respuesta_falsa = Mock(status_code=401)
    respuesta_falsa.json.return_value = {
        "error": {"message": "API key not valid."}
    }

    with patch("requests.post", return_value=respuesta_falsa):
        with pytest.raises(ValueError) as excinfo:
            enviar_peticion_con_fallback("Pregunta de prueba")
        assert "GEMINI_API_KEY es incorrecta" in str(excinfo.value)


def test_enviar_peticion_limite_de_uso():
    """Verifica el comportamiento ante límites de uso (429) y que intente reintentar o pasar al fallback."""
    respuesta_falsa = Mock(status_code=429)

    with patch("requests.post", return_value=respuesta_falsa):
        with pytest.raises(RuntimeError):
            enviar_peticion_con_fallback("Pregunta de prueba")


def test_enviar_peticion_exito():
    """Verifica que una respuesta exitosa (200) retorne los datos correctamente."""
    respuesta_falsa = Mock(status_code=200)
    respuesta_falsa.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "Respuesta simulada exitosa"}]
                }
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 10,
            "candidatesTokenCount": 15
        }
    }

    with patch("requests.post", return_value=respuesta_falsa):
        resultado = enviar_peticion_con_fallback("Pregunta de prueba")
        assert "candidates" in resultado


def test_con_reintento_agota_intentos():
    """Verifica que si todos los reintentos y modelos fallan, se lance un RuntimeError global."""
    respuesta_falsa = Mock(status_code=503) # Servicio no disponible

    with patch("requests.post", return_value=respuesta_falsa):
        with pytest.raises(RuntimeError) as excinfo:
            enviar_peticion_con_fallback("Pregunta de prueba")
        assert "Se agotaron todos los reintentos" in str(excinfo.value)


def test_con_reintento_no_reintenta_value_error():
    """Verifica que los errores de tipo ValueError (como credenciales) interrumpan el bucle de reintentos al instante."""
    respuesta_falsa = Mock(status_code=403)
    respuesta_falsa.json.return_value = {
        "error": {"message": "Key not valid"}
    }

    # Contamos cuántas veces se llama a requests.post para asegurar que no reintenta
    with patch("requests.post", return_value=respuesta_falsa) as mock_post:
        with pytest.raises(ValueError):
            enviar_peticion_con_fallback("Prueba", retries=3)
        # Debería llamarse solo 1 vez para el primer modelo y fallar rápido
        assert mock_post.call_count == 1


def test_registrar_costo_acumula():
    """Verifica que el registro de costos sume correctamente en la variable global de sesión."""
    # Reseteamos el estado global al inicio para evitar contaminación entre pruebas
    try_api.costo_total_sesion = 0.0
    datos_simulados = {
        "usageMetadata": {
            "promptTokenCount": 1_000,
            "candidatesTokenCount": 1_000
        }
    }
    
    costo_inicial = try_api.costo_total_sesion
    costo_operacion = registrar_costo(datos_simulados, "gemini-3.5-flash")
    
    assert costo_operacion > 0
    assert try_api.costo_total_sesion > costo_inicial


def test_consultar_modelo_convierte_error():
    """Verifica que el cliente modular (consultar_modelo) capture las excepciones técnicas y las convierta en un RuntimeError amigable."""
    
    # Parcheamos la función en el módulo 'client' que es quien llama y envuelve el error en try...except
    with patch("client.enviar_peticion_con_fallback", side_effect=Exception("Fallo crítico de red")):
        with pytest.raises(RuntimeError) as excinfo:
            consultar_modelo("Pregunta de prueba")
        
        # Validamos que contenga el mensaje amigable configurado en client.py
        assert "Error inesperado en el cliente modular" in str(excinfo.value)