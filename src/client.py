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
    registrar_costo,
    costo_total_sesion
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
    # Aseguramos que exista la carpeta 'prompts'
    os.makedirs("prompts", exist_ok=True)
    registro = {}
    
    # Reiniciamos o tomamos el costo de sesión actual si deseas acumularlo
    global costo_total_sesion
    costo_sesion_inicial = costo_total_sesion

    for prompt in BANCO_DE_PROMPTS:
        nombre = prompt["nombre"]
        print(f"\n🚀 Evaluando prompt: '{nombre}'")
        
        exitos = 0
        intentos_totales = 3
        
        for intento in range(intentos_totales):
            try:
                # Enviamos con tu lógica de fallback y parámetros estandarizados
                datos_respuesta = enviar_peticion_con_fallback(
                    pregunta=prompt["ejemplo_usuario"],
                    system_instruction=prompt["system_instruction"],
                    response_schema=prompt.get("response_schema")
                )
                
                texto = extraer_texto(datos_respuesta)
                datos_json = parsear_respuesta_json(texto)
                
                # Validamos que estén todas las claves esperadas
                if all(clave in datos_json for clave in prompt["claves_esperadas"]):
                    exitos += 1
                    print(f"   ✨ Intento {intento + 1}: ¡Éxito! Estructura válida.")
                else:
                    print(f"   ⚠️ Intento {intento + 1}: Faltan claves esperadas en el JSON.")
                
            except (ValueError, RuntimeError, requests.exceptions.RequestException) as error:
                print(f"   ❌ Intento {intento + 1} falló: {error}")
            
            time.sleep(1)
        
        print(f"📊 Resumen '{nombre}': {exitos}/{intentos_totales} respuestas válidas.")
        registro[nombre] = {
            "exitos": exitos, 
            "intentos": intentos_totales
        }

    # Estructura final del JSON que incluirá el resumen de costos de la sesión
    resultado_final = {
        "resumen_prompts": registro,
        "costo_total_sesion_usd": round(costo_total_sesion - costo_sesion_inicial, 6)
    }

    # Guardar registro global en un archivo JSON
    ruta_registro = "prompts/registro_resultados.json"
    with open(ruta_registro, "w", encoding="utf-8") as archivo:
        json.dump(resultado_final, archivo, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Registro y costos guardados exitosamente en '{ruta_registro}'.")

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