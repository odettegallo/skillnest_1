import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain.agents import create_agent

# Importamos tu lista de modelos configurada previamente
from core.config import MODELOS_DISPONIBLES

# Configuración de logs
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


# 1. Definición de Herramientas (Tools)
@tool
def buscar_en_documentacion(consulta: str) -> str:
    """Busca información relevante en la documentación interna del producto.
    Usar cuando la pregunta es sobre cómo funciona algo del sistema.
    """
    documentacion = {
        "reintentos": (
            "El cliente reintenta hasta 3 veces "
            "ante un TimeoutError, con espera "
            "creciente."
        ),
        "costos": (
            "El costo se calcula a partir de "
            "totalTokenCount, según la tarifa "
            "vigente."
        ),
    }
    for clave, texto in documentacion.items():
        if clave in consulta.lower():
            return texto
    return (
        "No se encontró información sobre esa "
        "consulta en la documentación."
    )


@tool
def calcular(expresion: str) -> str:
    """Evalúa una expresión aritmética simple, como '340 + 215'.
    Usar cuando la pregunta requiere un cálculo numérico.
    """
    permitido = set("0123456789-+*/(). ")
    if not set(expresion) <= permitido:
        return "Expresión no permitida."
    try:
        return str(eval(expresion))
    except Exception as e:
        return f"Error al evaluar la expresión: {e}"


# 2. Función principal para inicializar el Agente
def construir_ejecutor_agente(modelo_personalizado=None):
    """Configura y retorna el agente con las herramientas y el modelo."""
    if modelo_personalizado is not None:
        modelo = modelo_personalizado
    else:
        modelo = ChatGoogleGenerativeAI(
            model=MODELOS_DISPONIBLES[0], temperature=0
        )

    herramientas = [buscar_en_documentacion, calcular]

    return create_agent(
        model=modelo,
        tools=herramientas,
        system_prompt=(
            "Eres un asistente que responde preguntas usando las "
            "herramientas disponibles cuando las necesites."
        ),
        debug=True,  # reemplaza a verbose=True
    )


def preguntar(agente, texto: str) -> str:
    """Envía una pregunta al agente y devuelve el texto de la respuesta final."""
    resultado = agente.invoke(
        {"messages": [{"role": "user", "content": texto}]}
    )
    return resultado["messages"][-1].text


if __name__ == "__main__":
    load_dotenv()
    print("🤖 Iniciando agente con herramientas...\n")

    agente = construir_ejecutor_agente()

    print(f"\n📤 Resultado:\n{preguntar(agente, '¿Cuánto es 340 más 215?')}")
    print(
        "\n📤 Resultado:\n"
        f"{preguntar(agente, '¿Cómo funcionan los reintentos según la documentación?')}"
    )