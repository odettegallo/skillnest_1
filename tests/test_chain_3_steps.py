from unittest.mock import MagicMock
from langchain_core.messages import AIMessage

# Importamos tu función desde la nueva estructura de paquetes
from pipelines.chains.chain_3_steps import construir_cadena


def test_cadena_conecta_los_tres_pasos():
    """
    Prueba unitaria que utiliza un mock con side_effect para simular 
    las 3 respuestas secuenciales de los modelos sin gastar tokens reales.
    """
    # 1. Creamos el modelo falso y configuramos su side_effect ordenado por pasos
    modelo_falso = MagicMock()
    modelo_falso.side_effect = [
        AIMessage(content="punto 1\npunto 2\npunto 3"),      # Respuesta del paso 1 (Traducir)
        AIMessage(content="texto simplificado"),            # Respuesta del paso 2 (Resumir)
        AIMessage(content="- viñeta 1\n- viñeta 2"),       # Respuesta del paso 3 (Formato)
    ]

    # 2. Inyectamos el modelo falso en tu función construir_cadena
    cadena = construir_cadena(modelo_falso)

    # 3. Ejecutamos la cadena con un texto de prueba
    resultado = cadena.invoke({"texto": "texto de prueba"})

    # 4. Validaciones (Assertions)
    # Verificamos que el modelo fue llamado exactamente 3 veces (una por cada paso de la cadena)
    assert modelo_falso.call_count == 3
    
    # Verificamos que el resultado final contiene el formato esperado
    assert "viñeta" in resultado