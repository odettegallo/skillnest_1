import os
import re
import json
import time
import requests
from dotenv import load_dotenv
from config import MODELOS_DISPONIBLES, BANCO_DE_PROMPTS

# Carga las variables del archivo .env
load_dotenv()

# --- Responsabilidad 1: Construir la petición ---
def construir_peticion(pregunta, modelo, system_instruction=None, response_schema=None):
    if not pregunta or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("No se encontró la GEMINI_API_KEY en el archivo .env.")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
    
    body = {
        "contents": [
            {
                "parts": [
                    {"text": pregunta}
                ]
            }
        ]
    }
    
    if system_instruction:
        body["systemInstruction"] = {
            "parts": [
                {"text": system_instruction}
            ]
        }
        
    generation_config = {
        "maxOutputTokens": 1000
    }
    
    if response_schema:
        generation_config["responseMimeType"] = "application/json"
        generation_config["responseSchema"] = response_schema
        
    body["generationConfig"] = generation_config
    
    return url, body

def enviar_peticion(pregunta, modelo):
    """Envía la petición a un modelo específico sin bucles infinitos."""
    url, body = construir_peticion(pregunta, modelo)
    respuesta = requests.post(url, json=body, timeout=30)
    respuesta.raise_for_status()
    return respuesta.json()

# --- Responsabilidad 2: Enviar la petición con resiliencia y Fallback ---
def enviar_peticion_con_fallback(pregunta, system_instruction=None, response_schema=None, modelos=MODELOS_DISPONIBLES, retries=2):
    for modelo in modelos:
        print(f"🔄 Intentando conectar con el modelo: {modelo}...")
        try:
            url, body = construir_peticion(pregunta, modelo, system_instruction, response_schema)
        except ValueError as ve:
            raise ve

        for intento in range(1, retries + 1):
            try:
                respuesta = requests.post(url, json=body, timeout=30)
                
                if respuesta.status_code == 429:
                    print(f"   ⚠️ Cuota excedida (429) en {modelo}. Reintento {intento}/{retries}...")
                elif respuesta.status_code == 503:
                    print(f"   ⚠️ Servicio no disponible (503) en {modelo}. Reintento {intento}/{retries}...")
                else:
                    respuesta.raise_for_status()
                    try:
                        datos = respuesta.json()
                        print(f"   ✅ ¡Conexión exitosa con {modelo}!")
                        return datos
                    except requests.exceptions.JSONDecodeError:
                        raise RuntimeError(f"El servidor de {modelo} respondió con un JSON corrupto o inválido.")

            except requests.exceptions.RequestException as e:
                print(f"   ⚠️ Error de red/conexión con {modelo} (Intento {intento}/{retries}): {e}")

            if intento < retries:
                time.sleep(2)

        print(f"❌ El modelo '{modelo}' agotó sus reintentos. Pasando al siguiente respaldo...\n")

    raise RuntimeError("⚠️ Todos los modelos fallaron o no están disponibles en este momento. Intenta más tarde.")


# --- Responsabilidad 3: Extraer el texto ---
def extraer_texto(datos_json):
    try:
        return datos_json["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"La estructura de la respuesta cambió o está incompleta (Faltó el campo: {e}).")

# --- Parsear Respuesta JSON ---
def parsear_respuesta_json(texto):
    texto_limpio = texto.strip()
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio)
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio)
    try:
        return json.loads(texto_limpio)
    except json.JSONDecodeError:
        raise ValueError("La respuesta del modelo no es un JSON válido.")

# --- Función corregida para calcular costos ---
def calcular_costo(datos_json, precio_entrada, precio_salida):
    """
    Calcula el costo aproximado de la consulta extrayendo los tokens
    desde 'usageMetadata' según la estructura oficial de la API de Gemini.
    """
    try:
        uso = datos_json["usageMetadata"]
        tokens_entrada = uso["promptTokenCount"]
        tokens_salida = uso["candidatesTokenCount"]
        
        costo_total = (tokens_entrada * precio_entrada) + (tokens_salida * precio_salida)
        return costo_total
    except KeyError as e:
        raise RuntimeError(f"No se pudo calcular el costo debido a la falta del campo en usageMetadata: {e}")

# --- Función Orquestadora del Banco de Pruebas ---
def ejecutar_banco_de_prompts():
    # Aseguramos que exista la carpeta 'prompts'
    os.makedirs("prompts", exist_ok=True)
    registro = {}

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
        registro[nombre] = {"exitos": exitos, "intentos": intentos_totales}

    # Guardar registro global en un archivo JSON
    ruta_registro = "prompts/registro_resultados.json"
    with open(ruta_registro, "w", encoding="utf-8") as archivo:
        json.dump(registro, archivo, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Registro de resultados guardado exitosamente en '{ruta_registro}'.")

# --- Función Orquestadora ---
def test_api_connection(pregunta):
    # 1 y 2 combinados con lógica de fallback y reintentos
    datos_respuesta = enviar_peticion_con_fallback(pregunta)
    
    # 3. Extraemos el resultado final
    texto_final = extraer_texto(datos_respuesta)

    try:
        # Ejemplo: $0.075 por millón de entrada ($0.000000075 por token)
        precio_ent = 0.000000075 
        # Ejemplo: $0.30 por millón de salida ($0.0000003 por token)
        precio_sal = 0.0000003    
        
        costo = calcular_costo(datos_respuesta, precio_ent, precio_sal)
        print(f" 💰 Costo estimado de la consulta: ${costo:.8f} USD")
    except Exception as ex:
        print(f" ⚠️ No se pudo calcular el costo: {ex}")
            
    return texto_final


# Ejecución del programa con un bloque try-except robusto a nivel global
if __name__ == "__main__":
    try:
        pregunta_prueba = "Responde con la frase del día"
        print(f"Enviando consulta: '{pregunta_prueba}'\n")
        
        resultado = test_api_connection(pregunta_prueba)
        
        print("\n--- RESPUESTA FINAL ---")
        print(resultado)
        
    except (ValueError, RuntimeError) as error:
        print(f"\n❌ Error crítico en la ejecución del programa: {error}")

    try:
        ejecutar_banco_de_prompts()
    except Exception as error:
        print(f"\n❌ Error crítico en la ejecución del programa: {error}")