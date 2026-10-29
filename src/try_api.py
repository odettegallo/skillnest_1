import os
import re
import json
import time
import random
import requests
from dotenv import load_dotenv
from config import MODELOS_DISPONIBLES, BANCO_DE_PROMPTS, TARIFAS_MODELOS

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
# Variable global para recordar el índice del último modelo que tuvo éxito
_indice_modelo_exitoso = 0

def enviar_peticion_con_fallback(pregunta, system_instruction=None, response_schema=None, modelos=MODELOS_DISPONIBLES, retries=3):
    global _indice_modelo_exitoso
    
    # Reordenamos la lista de modelos para poner al principio el que funcionó la última vez
    modelos_ordenados = list(modelos)
    if _indice_modelo_exitoso > 0 and _indice_modelo_exitoso < len(modelos_ordenados):
        modelo_favorito = modelos_ordenados.pop(_indice_modelo_exitoso)
        modelos_ordenados.insert(0, modelo_favorito)
        
    for modelo in modelos_ordenados:
        print(f"🔄 Intentando conectar con el modelo: {modelo}...")
        
        try:
            url, body = construir_peticion(pregunta, modelo, system_instruction, response_schema)
        except ValueError as ve:
            raise ve

        for intento in range(1, retries + 1):
            try:
                respuesta = requests.post(url, json=body, timeout=30)

                if 400 <= respuesta.status_code <= 403:
                    try:
                        error_json = respuesta.json()
                        error_mensaje = error_json.get("error", {}).get("message", "").lower()
                        if "api key" in error_mensaje or "key not valid" in error_mensaje or respuesta.status_code in (401, 403):
                            raise ValueError(f"La GEMINI_API_KEY es incorrecta o no es válida: {error_json.get('error', {}).get('message')}")
                    except json.JSONDecodeError:
                        pass
                    respuesta.raise_for_status()

                if respuesta.status_code == 429:
                    print(f"   ⚠️ Cuota excedida (429) en {modelo}. Reintento {intento}/{retries}...")
                elif respuesta.status_code == 503:
                    print(f"   ⚠️ Servicio no disponible (503) en {modelo}. Reintento {intento}/{retries}...")
                else:
                    respuesta.raise_for_status()
                    
                    try:
                        datos = respuesta.json()
                        print(f"   ✅ ¡Conexión exitosa con {modelo}!")
                        
                        # MEMORIA INTELIGENTE: Guardamos la posición real de este modelo exitoso 
                        # para que sea el primero en ser consultado en la próxima solicitud.
                        if modelo in MODELOS_DISPONIBLES:
                            _indice_modelo_exitoso = MODELOS_DISPONIBLES.index(modelo)
                        
                        # Registramos el costo de inmediato
                        registrar_costo(datos, modelo)
                        
                        return datos
                    except requests.exceptions.JSONDecodeError:
                        raise RuntimeError(f"El servidor de {modelo} respondió con un JSON corrupto o inválido.")

            except requests.exceptions.RequestException as e:
                print(f"   ⚠️ Error de red/conexión con {modelo} (Intento {intento}/{retries}): {e}")

            if intento < retries:
                tiempo_base = 2 ** intento
                jitter = random.uniform(0, 1.5)
                espera = tiempo_base + jitter
                print(f"   ⏳ Esperando {espera:.2f} segundos antes del próximo reintento (con jitter)...")
                time.sleep(espera)

        print(f"❌ El modelo '{modelo}' agotó sus reintentos. Pasando al siguiente respaldo...\n")

    raise RuntimeError("⚠️ Se agotaron todos los reintentos en todos los modelos disponibles sin obtener respuesta.")
    
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

# Variable global para acumular el costo de la sesión actual
costo_total_sesion = 0.0

def registrar_costo(datos_json: dict, modelo: str) -> float:
    """Extrae el conteo de tokens de usageMetadata, busca la tarifa por millón 
    del modelo correspondiente en TARIFAS_MODELOS y acumula el costo de la sesión.
    """
    global costo_total_sesion
    try:
        uso = datos_json.get("usageMetadata", {})
        tokens_entrada = uso.get("promptTokenCount", 0)
        tokens_salida = uso.get("candidatesTokenCount", 0)
        
        # Obtenemos las tarifas del modelo (por defecto usamos gemini-2.5-flash si no se encuentra)
        tarifas = TARIFAS_MODELOS.get(modelo, {"entrada": 0.075, "salida": 0.30})
        
        precio_entrada_por_token = tarifas["entrada"] / 1_000_000
        precio_salida_por_token = tarifas["salida"] / 1_000_000
        
        costo_estimado = (tokens_entrada * precio_entrada_por_token) + (tokens_salida * precio_salida_por_token)
        costo_total_sesion += costo_estimado
        
        print(f"   📊 [{modelo}] Tokens -> Entrada: {tokens_entrada}, Salida: {tokens_salida}")
        print(f"      Costo operación: ${costo_estimado:.6f} USD (Acumulado sesión: ${costo_total_sesion:.6f} USD)")
        
        return costo_estimado
    except Exception as e:
        print(f"   ⚠️ No se pudo registrar el costo: {e}")
        return 0.0

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
    # La función ya se encarga de enviar, aplicar fallback y registrar el costo automáticamente
    datos_respuesta = enviar_peticion_con_fallback(pregunta)
    
    # 3. Extraemos el resultado final
    texto_final = extraer_texto(datos_respuesta)
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