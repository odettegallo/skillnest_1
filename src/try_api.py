import os
import time
import requests
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

# Lista de modelos en orden de respaldo (Fallback)
MODELOS_DISPONIBLES = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-3.8-flash"
]

# --- Responsabilidad 1: Construir la petición ---
def construir_peticion(pregunta, modelo):
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
        ],
        "generationConfig": {
            "maxOutputTokens": 1000 # Controlamos el consumo en pruebas
        }
    }
    return url, body

def enviar_peticion(pregunta, modelo):
    """Envía la petición a un modelo específico sin bucles infinitos."""
    url, body = construir_peticion(pregunta, modelo)
    respuesta = requests.post(url, json=body, timeout=30)
    respuesta.raise_for_status()
    return respuesta.json()

# --- Responsabilidad 2: Enviar la petición con resiliencia ---
def enviar_peticion_con_fallback(pregunta, modelos=MODELOS_DISPONIBLES, retries=2):
    """
    Intenta enviar la petición recorriendo la lista de modelos.
    Si un modelo falla por red, saturación (429) o servicio no disponible (503),
    hace reintentos y luego salta al siguiente modelo.
    """
    for modelo in modelos:
        print(f"🔄 Intentando conectar con el modelo: {modelo}...")
        
        try:
            url, body = construir_peticion(pregunta, modelo)
        except ValueError as ve:
            # Si hay un error de validación inicial, no tiene sentido probar otros modelos
            raise ve

        # Bucle de reintentos por cada modelo en caso de fallos transitorios
        for intento in range(1, retries + 1):
            try:
                respuesta = requests.post(url, json=body, timeout=30)
                
                # Manejo de códigos de estado específicos de la API
                if respuesta.status_code == 429:
                    print(f"   ⚠️ Cuota excedida (429) en {modelo}. Reintento {intento}/{retries}...")
                elif respuesta.status_code == 503:
                    print(f"   ⚠️ Servicio no disponible (503) en {modelo}. Reintento {intento}/{retries}...")
                else:
                    # Lanza excepción para otros errores HTTP graves (4xx, 5xx)
                    respuesta.raise_for_status()
                    
                    # Si el HTTP es 200 OK, intentamos parsear el JSON
                    try:
                        datos = respuesta.json()
                        print(f"   ✅ ¡Conexión exitosa con {modelo}!")
                        return datos
                    except requests.exceptions.JSONDecodeError:
                        raise RuntimeError(f"El servidor de {modelo} respondió con un JSON corrupto o inválido.")

            except requests.exceptions.RequestException as e:
                print(f"   ⚠️ Error de red/conexión con {modelo} (Intento {intento}/{retries}): {e}")

            # Espera exponencial o fija antes del siguiente reintento
            if intento < retries:
                time.sleep(2)

        print(f"❌ El modelo '{modelo}' agotó sus reintentos. Pasando al siguiente respaldo...\n")

    # Si el bucle termina y ningún modelo respondió
    raise RuntimeError("⚠️ Todos los modelos fallaron o no están disponibles en este momento. Intenta más tarde.")


# --- Responsabilidad 3: Extraer el texto ---
def extraer_texto(datos_json):
    try:
        return datos_json["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"La estructura de la respuesta cambió o está incompleta (Faltó el campo: {e}).")

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