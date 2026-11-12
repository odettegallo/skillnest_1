import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnablePassthrough, RunnableLambda

# Importamos tu lista de modelos configurada previamente
from core.config import MODELOS_DISPONIBLES

# Silenciamos los logs informativos ruidosos de la API de Google (dejamos solo WARNING o ERROR)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 1. Plantilla global de clasificación
plantilla_clasificacion = PromptTemplate.from_template(
    "Clasifica el siguiente mensaje de soporte en una sola "
    "palabra: pregunta, queja o sugerencia. Responde solo "
    "con esa palabra.\n\n{mensaje}"
)

def construir_paso_clasificacion(modelo):
    """Construye el paso que clasifica el texto usando el modelo indicado."""
    return (
        plantilla_clasificacion
        | modelo
        | StrOutputParser()
        | (lambda texto: texto.strip().lower())
    )

def construir_cadena_con_enrutamiento(
    paso_clasificacion,
    cadena_queja=None,
    cadena_sugerencia=None,
    cadena_pregunta=None,
    cadena_elogio=None,
):
    """Construye la bifurcación condicional basada en RunnableBranch."""
    cadena_queja = cadena_queja or RunnablePassthrough()
    cadena_sugerencia = cadena_sugerencia or RunnablePassthrough()
    cadena_pregunta = cadena_pregunta or RunnablePassthrough()
    cadena_elogio = cadena_elogio or RunnablePassthrough()

    bifurcacion = RunnableBranch(
        (lambda x: x["categoria"] == "queja", cadena_queja),
        (lambda x: x["categoria"] == "sugerencia", cadena_sugerencia),
        (lambda x: x["categoria"] == "elogio", cadena_elogio),
        cadena_pregunta,  # Ruta por defecto (fallback)
    )

    return (
        RunnablePassthrough.assign(categoria=paso_clasificacion)
        | bifurcacion
    )

# A nivel global
respuesta_generica = RunnableLambda(
    lambda x: "Gracias por tu mensaje. Un miembro de nuestro equipo te va a responder pronto."
)

def construir_router(modelo_personalizado=None):
    """Función contenedora principal para inicializar el router completo."""
    if modelo_personalizado is not None:
        modelo = modelo_personalizado
    else:
        modelo_principal_str = MODELOS_DISPONIBLES[0]
        modelos_respaldo_strs = MODELOS_DISPONIBLES[1:]
        
        modelo_principal = ChatGoogleGenerativeAI(model=modelo_principal_str)
        modelos_respaldo = [ChatGoogleGenerativeAI(model=m) for m in modelos_respaldo_strs]
        modelo = modelo_principal.with_fallbacks(modelos_respaldo)

    # Definimos las cadenas de respuesta especializadas
    cadena_pregunta = (
        PromptTemplate.from_template("Responde esta pregunta técnica de forma muy breve y directa (máximo 2 oraciones):\n\n{mensaje}")
        | modelo
        | StrOutputParser()
    ).with_fallbacks([respuesta_generica])

    cadena_queja = (
        PromptTemplate.from_template("Responde a esta queja con empatía y brevedad (máximo 2 oraciones):\n\n{mensaje}")
        | modelo
        | StrOutputParser()
    ).with_fallbacks([respuesta_generica])

    cadena_sugerencia = (
        PromptTemplate.from_template("Agradece esta sugerencia brevemente en una sola oración:\n\n{mensaje}")
        | modelo
        | StrOutputParser()
    ).with_fallbacks([respuesta_generica])

    cadena_elogio = (
        PromptTemplate.from_template("Agradece este elogio de manera cordial en una sola oración:\n\n{mensaje}")
        | modelo
        | StrOutputParser()
    ).with_fallbacks([respuesta_generica])

    paso_clasificacion = construir_paso_clasificacion(modelo)
    
    return construir_cadena_con_enrutamiento(
        paso_clasificacion=paso_clasificacion,
        cadena_queja=cadena_queja,
        cadena_sugerencia=cadena_sugerencia,
        cadena_elogio=cadena_elogio,
        cadena_pregunta=cadena_pregunta,
    )

# Función segura que utiliza la instancia correcta del router
def procesar_mensaje_seguro(mensaje, router_chain):
    try:
        return router_chain.invoke({"mensaje": mensaje})
    except Exception as error:
        logger.error(f"Error procesando mensaje: {error}")
        return (
            "No pudimos procesar tu mensaje en este momento. "
            "Intenta de nuevo más tarde."
        )

if __name__ == "__main__":
    load_dotenv()
    router_chain = construir_router()

    print("🚀 Ejecutando router de mensajes con RunnableBranch...\n")

    # Prueba del fallback forzado
    def fallar_a_proposito(x):
        raise Exception("Error de red simulado")

    cadena_rota = RunnableLambda(fallar_a_proposito)
    cadena_rota_segura = cadena_rota.with_fallbacks([respuesta_generica])
    
    resultado_fallback = cadena_rota_segura.invoke({"mensaje": "prueba"})
    print(f"🛡️ Prueba de fallback forzado:\n{resultado_fallback}\n" + "-" * 50)

    # Lista con diferentes escenarios de prueba
    casos_prueba = [
        "¿Cómo cambio mi contraseña?",
        "La app se cierra cada vez que subo una foto.",
        "Estaría bueno que la app tuviera modo oscuro.",
        "¡Me encanta la nueva interfaz, está muy intuitiva!",
        "",
    ]

    for mensaje in casos_prueba:
        print(f"📥 Mensaje de entrada: \"{mensaje}\"")
        resultado = procesar_mensaje_seguro(mensaje, router_chain)
        print(f"📤 Respuesta obtenida:\n{resultado}\n" + "-" * 50)