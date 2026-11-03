from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Importamos tu lista de modelos configurada previamente
from core.config import MODELOS_DISPONIBLES

def construir_cadena():
    """
    Construye una cadena de 3 pasos con resiliencia y fallback automático 
    entre los modelos definidos en config.py.
    """
    # 1. Configuramos el modelo principal y los respaldos usando LangChain
    modelo_principal_str = MODELOS_DISPONIBLES[0] # Ej: "gemini-3.5-flash"
    modelos_respaldo_strs = MODELOS_DISPONIBLES[1:] # El resto de modelos
    
    modelo_principal = ChatGoogleGenerativeAI(model=modelo_principal_str)
    modelos_respaldo = [ChatGoogleGenerativeAI(model=m) for m in modelos_respaldo_strs]
    
    # 🛡️ Aplicamos el fallback nativo de LangChain
    modelo_seguro = modelo_principal.with_fallbacks(modelos_respaldo)

    # 2. Definimos las tres plantillas (PromptTemplate)
    plantilla_traducir = PromptTemplate.from_template(
        "Traduce el siguiente texto técnico al español, manteniendo la precisión de los conceptos:\n\n{texto}"
    )
    paso_traducir = plantilla_traducir | modelo_seguro | StrOutputParser()

    plantilla_resumir = PromptTemplate.from_template(
        "Lee el siguiente texto y extrae sus 2 o 3 ideas principales, una por línea, de forma directa:\n\n{traduccion}"
    )
    paso_resumir = plantilla_resumir | modelo_seguro | StrOutputParser()

    plantilla_formato = PromptTemplate.from_template(
        "Convierte las siguientes ideas en una lista limpia de viñetas en formato markdown, sin texto introductorio ni despedidas:\n\n{ideas}"
    )
    paso_formato = plantilla_formato | modelo_seguro | StrOutputParser()

    # 3. Encadenamiento completo de punta a punta con el operador '|'
    cadena_completa = (
        paso_traducir
        | (lambda traduccion: {"traduccion": traduccion})
        | paso_resumir
        | (lambda ideas: {"ideas": ideas})
        | paso_formato
    )

    return cadena_completa


if __name__ == "__main__":
    # Carga las credenciales del archivo .env
    load_dotenv()
    
    # Construimos la cadena resiliente
    cadena = construir_cadena()

    # Caso de entrada real
    texto_entrada = (
        "Asynchronous programming allows the execution of tasks "
        "concurrently without blocking the main execution thread, "
        "significantly improving performance in I/O-bound applications."
    )

    print("🚀 Ejecutando cadena de 3 pasos con fallback automático...\n")
    try:
        resultado = cadena.invoke({"texto": texto_entrada})
        print("--- RESULTADO FINAL ---")
        print(resultado)
    except Exception as error:
        print(f"❌ Todos los modelos fallaron tras aplicar los respaldos: {error}")