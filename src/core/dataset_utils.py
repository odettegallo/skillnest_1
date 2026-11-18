# src/core/dataset_utils.py
import json
import time
from collections import Counter
from google.genai import types

def explicar_error(error):
    """Traduce errores comunes de la API de Gemini."""
    mensaje = str(error)
    if "API key" in mensaje or "401" in mensaje or "403" in mensaje:
        return "Problema de autenticación: revisa GEMINI_API_KEY en tu archivo .env."
    if "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
        return "Cuota o límite de peticiones agotado: espera unos minutos y reintenta."
    if "Connection" in mensaje or "timed out" in mensaje:
        return "Problema de conexión: revisa tu internet y vuelve a intentarlo."
    return "Error inesperado: " + mensaje

def validar_dataset(examples, claves_esperadas=("categoria", "accion_sugerida")):
    """Valida formato, duplicados y claves JSON del dataset."""
    problemas = []
    vistos = set()
    for i, ej in enumerate(examples):
        if not ej.text_input or not ej.text_input.strip():
            problemas.append(f"ejemplo {i}: text_input vacio")
        if not ej.output or not ej.output.strip():
            problemas.append(f"ejemplo {i}: output vacio")
            continue
        if ej.text_input in vistos:
            problemas.append(f"ejemplo {i}: text_input duplicado")
        vistos.add(ej.text_input)
        try:
            salida = json.loads(ej.output)
        except json.JSONDecodeError:
            problemas.append(f"ejemplo {i}: output no es JSON valido")
            continue
        for clave in claves_esperadas:
            if clave not in salida:
                problemas.append(f'ejemplo {i}: output no tiene la clave "{clave}"')
    return problemas

def chequear_balance(ejemplos_raw, clave="categoria"):
    """Cuenta la frecuencia de cada categoría o intención."""
    return Counter(salida[clave] for _, salida in ejemplos_raw)

def esperar_a_que_termine(client, nombre_trabajo, intervalo_segundos=30):
    """Consulta periódicamente el estado de un trabajo de tuning."""
    estados_finales = {
        types.JobState.JOB_STATE_SUCCEEDED,
        types.JobState.JOB_STATE_FAILED,
        types.JobState.JOB_STATE_CANCELLED,
        types.JobState.JOB_STATE_PARTIALLY_SUCCEEDED,
    }
    while True:
        trabajo = client.tunings.get(name=nombre_trabajo)
        print(f"estado actual: {trabajo.state}")
        if trabajo.state in estados_finales:
            return trabajo
        time.sleep(intervalo_segundos)