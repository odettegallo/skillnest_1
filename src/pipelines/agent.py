import logging
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)

# Importamos tu lista de modelos configurada previamente
from core.config import MODELOS_DISPONIBLES

# Configuración de logs
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


# Paso 1. Herramientas: el docstring explica CUÁNDO usarlas
@tool
def buscar_en_documentacion(consulta: str) -> str:
    """Busca información en la documentación interna del producto.

    Usar solo cuando la pregunta es sobre cómo funcionan los reintentos
    del cliente o el cálculo de costos. No usar para preguntas generales
    (contacto, soporte, saludos). Pasar como consulta la palabra clave
    del tema (ej. 'reintentos', 'costos')."""
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

    Usar cuando la pregunta requiere un cálculo numérico (sumas,
    restas, multiplicaciones o divisiones). No usar para preguntas
    sobre la documentación."""
    permitido = set("0123456789-+*/(). ")
    if not set(expresion) <= permitido or "**" in expresion:
        return "Expresión no permitida."  # '**' bloqueado: evita 9**9**9
    try:
        return str(eval(expresion))
    except Exception as e:
        return f"Error al evaluar la expresión: {e}"


# Paso 2. Agente + AgentExecutor con return_intermediate_steps=True
def construir_ejecutor_agente(modelo_personalizado=None):
    """Configura y retorna el AgentExecutor con las herramientas, el modelo y sus fallbacks."""
    if modelo_personalizado is not None:
        modelo = modelo_personalizado
    else:
        # Modelo principal
        modelo_principal = ChatGoogleGenerativeAI(
            model=MODELOS_DISPONIBLES[0], temperature=0
        )
        
        # Si tienes más modelos en la lista, creamos los fallbacks automáticamente
        if len(MODELOS_DISPONIBLES) > 1:
            modelos_respaldo = [
                ChatGoogleGenerativeAI(model=m, temperature=0)
                for m in MODELOS_DISPONIBLES[1:]
            ]
            # Configuramos el fallback: si el principal falla (ej. por cuota 429), usa los siguientes
            modelo = modelo_principal.with_fallbacks(modelos_respaldo)
        else:
            modelo = modelo_principal

    herramientas = [buscar_en_documentacion, calcular]

    prompt_agente = ChatPromptTemplate.from_messages([
        (
            "system",
            "Eres un asistente que responde preguntas "
            "usando las herramientas disponibles cuando "
            "las necesites.",
        ),
        ("human", "{entrada}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agente = create_tool_calling_agent(
        modelo, herramientas, prompt_agente
    )

    return AgentExecutor(
        agent=agente,
        tools=herramientas,
        verbose=True,
        return_intermediate_steps=True,
    )

# Paso 3. Validación con intermediate_steps
def herramientas_usadas(resultado) -> list[str]:
    """Devuelve los nombres de las tools que el agente eligió."""
    return [accion.tool for accion, _ in resultado["intermediate_steps"]]


def probar(ejecutor, entrada: str) -> list[str]:
    """Invoca al agente, muestra su camino y devuelve las tools usadas."""
    resultado = ejecutor.invoke({"entrada": entrada})

    print(f"\n📥 Entrada: {entrada}")
    for accion, observacion in resultado["intermediate_steps"]:
        print(f"🔧 Tool: {accion.tool} | Input: {accion.tool_input}")
        print(f"   Observación: {observacion}")
    print(f"📤 Respuesta: {resultado['output']}")

    return herramientas_usadas(resultado)


if __name__ == "__main__":
    load_dotenv()
    print("🤖 Iniciando agente con herramientas...\n")

    ejecutor_agente = construir_ejecutor_agente()

    # Prueba 1: debe disparar 'calcular'
    usadas = probar(ejecutor_agente, "¿Cuánto es 340 más 215?")
    assert usadas and usadas[0] == "calcular", f"Usó: {usadas}"
    print(f"✅ Prueba 1 OK: {usadas}")

    # Prueba 2: debe disparar 'buscar_en_documentacion'
    usadas = probar(
        ejecutor_agente,
        "¿Cómo funcionan los reintentos según la documentación?",
    )
    assert usadas and usadas[0] == "buscar_en_documentacion", f"Usó: {usadas}"
    print(f"✅ Prueba 2 OK: {usadas}")

    # Prueba 3: pregunta general, no debe usar ninguna tool
    usadas = probar(ejecutor_agente, "¿Cómo puedo contactar a soporte?")
    assert usadas == [], (
        f"El agente usó {usadas}: la descripción de esa tool es muy amplia"
    )
    print("✅ Prueba 3 OK: no usó ninguna herramienta")