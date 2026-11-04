from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnablePassthrough

# Importamos tu lista de modelos configurada previamente
from core.config import MODELOS_DISPONIBLES

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
        PromptTemplate.from_template("Responde esta pregunta técnica con precisión:\n\n{mensaje}")
        | modelo
        | StrOutputParser()
    )

    cadena_queja = (
        PromptTemplate.from_template("Responde a esta queja con empatía, reconociendo el problema antes de ofrecer una solución:\n\n{mensaje}")
        | modelo
        | StrOutputParser()
    )

    cadena_sugerencia = (
        PromptTemplate.from_template("Agradece esta sugerencia y explica cómo se evaluará dentro del producto:\n\n{mensaje}")
        | modelo
        | StrOutputParser()
    )

    cadena_elogio = (
        PromptTemplate.from_template("Agradece este elogio de manera cordial y profesional:\n\n{mensaje}")
        | modelo
        | StrOutputParser()
    )

    paso_clasificacion = construir_paso_clasificacion(modelo)
    
    return construir_cadena_con_enrutamiento(
        paso_clasificacion=paso_clasificacion,
        cadena_queja=cadena_queja,
        cadena_sugerencia=cadena_sugerencia,
        cadena_elogio=cadena_elogio,
        cadena_pregunta=cadena_pregunta,
    )


if __name__ == "__main__":
    load_dotenv()
    router_chain = construir_router()

    print("🚀 Ejecutando router de mensajes con RunnableBranch...\n")
    
    # Lista con diferentes escenarios (pregunta, queja y sugerencia)
    casos_prueba = [
        "¿Cómo cambio mi contraseña?",
        "La app se cierra cada vez que subo una foto.",
        "Estaría bueno que la app tuviera modo oscuro.",
        "¡Me encanta la nueva interfaz, está muy intuitiva!",
    ]

    try:
        for mensaje in casos_prueba:
            print(f"📥 Mensaje de entrada: \"{mensaje}\"")
            resultado = router_chain.invoke({"mensaje": mensaje})
            print(f"📤 Respuesta obtenida:\n{resultado}\n" + "-" * 50)
            
    except Exception as error:
        print(f"❌ Ocurrió un error en la ejecución: {error}")