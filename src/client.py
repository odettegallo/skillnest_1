import json
import os
import time
import requests

# Importamos las funciones base desde try_api.py
from try_api import (
    enviar_peticion_con_fallback,
    extraer_texto,
    parsear_respuesta_json,
    calcular_costo,
)
from config import BANCO_DE_PROMPTS


# =====================================================================
# --- CLIENTE MODULAR (Único punto de entrada requerido por el curso) ---
# =====================================================================
def consultar_modelo(
    pregunta: str, system_instruction: str = None, response_schema: dict = None
) -> str:
    """Único punto de entrada: arma la petición, la envía con reintentos/fallback,
    extrae el texto y maneja los errores limpiamente para quien consume el cliente.
    """
    try:
        # 1 y 2. Envío con reintentos, manejo de límites de uso (429/503) y fallback
        datos_respuesta = enviar_peticion_con_fallback(
            pregunta=pregunta,
            system_instruction=system_instruction,
            response_schema=response_schema,
        )
        
        # 3. Extraemos el texto de la respuesta exitosa
        return extraer_texto(datos_respuesta)
        
    except ValueError as error:
        # Los errores de credenciales (ValueError) se propagan tal cual
        raise error
    except RuntimeError as error:
        # Convertimos el agotamiento total en un error amigable para el usuario final
        raise RuntimeError(f"El servicio no respondió tras varios intentos. Intenta más tarde. Detalle: {error}")
    except Exception as e:
        raise RuntimeError(f"Error inesperado en el cliente modular: {e}")


# --- Función Orquestadora del Banco de Pruebas ---
def ejecutar_banco_de_prompts():
    os.makedirs("prompts", exist_ok=True)
    registro = {}

    for prompt in BANCO_DE_PROMPTS:
        nombre = prompt["nombre"]
        print(f"\n🚀 Evaluando prompt: '{nombre}'")

        exitos = 0
        intentos_totales = 3

        for intento in range(intentos_totales):
            try:
                # Usamos nuestra interfaz modular
                texto = consultar_modelo(
                    pregunta=prompt["ejemplo_usuario"],
                    system_instruction=prompt.get("system_instruction"),
                    response_schema=prompt.get("response_schema"),
                )

                datos_json = parsear_respuesta_json(texto)

                if all(clave in datos_json for clave in prompt["claves_esperadas"]):
                    exitos += 1
                    print(f"   ✨ Intento {intento + 1}: ¡Éxito! Estructura válida.")
                else:
                    print(
                        f"   ⚠️ Intento {intento + 1}: Faltan claves esperadas en el JSON."
                    )

            except (ValueError, RuntimeError, requests.exceptions.RequestException) as error:
                print(f"   ❌ Intento {intento + 1} falló: {error}")

            time.sleep(1)

        print(
            f"📊 Resumen '{nombre}': {exitos}/{intentos_totales} respuestas válidas."
        )
        registro[nombre] = {"exitos": exitos, "intentos": intentos_totales}

    ruta_registro = "prompts/registro_resultados.json"
    with open(ruta_registro, "w", encoding="utf-8") as archivo:
        json.dump(registro, archivo, indent=2, ensure_ascii=False)

    print(
        f"\n📁 Registro de resultados guardado exitosamente en '{ruta_registro}'."
    )


# --- Función de prueba simple con cálculo de costos ---
def test_api_connection(pregunta):
    return consultar_modelo(pregunta)


# --- Bloque de Ejecución Principal ---
if __name__ == "__main__":
    try:
        pregunta_prueba = "¿Cuál es la capital de Chile?"
        print(f"Enviando consulta: '{pregunta_prueba}'\n")

        resultado = consultar_modelo(pregunta_prueba)

        print("\n--- RESPUESTA FINAL ---")
        print(resultado)

    except (ValueError, RuntimeError) as error:
        print(f"\n❌ Error en la ejecución: {error}")

    try:
        ejecutar_banco_de_prompts()
    except Exception as error:
        print(f"\n❌ Error crítico en el banco de prompts: {error}")