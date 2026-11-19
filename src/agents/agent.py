import json
import logging
import os
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from core.config import MODELOS_DISPONIBLES
from utils.observability import (
    CallbackObservabilidad,
    obtener_logger_json,
    resumen_gobernado,
    trace_id_var,
)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

historiales = {}


def obtener_historial(session_id: str):
    """Retorna o crea el historial de conversación según el session_id."""
    if session_id not in historiales:
        historiales[session_id] = InMemoryChatMessageHistory()
    return historiales[session_id]


def cerrar_sesion(session_id: str):
    """Elimina el historial de una sesión cuando finaliza la conversación."""
    historiales.pop(session_id, None)


class ArgumentosConsultaEnvio(BaseModel):
    numero_seguimiento: str = Field(
        description="Número de seguimiento del envío."
    )
    incluir_historial: bool = Field(
        default=False,
        description="Si es True, incluye el historial completo.",
    )


ESTADOS = {
    "AR12345": {
        "actual": "en tránsito, llega en 2 días",
        "historial": [
            "recibido en depósito",
            "en tránsito",
        ],
    },
}


@tool(
    "consultar_estado_envio_con_historial",
    args_schema=ArgumentosConsultaEnvio,
)
def consultar_estado_envio_detallado(
    numero_seguimiento: str,
    incluir_historial: bool = False,
) -> str:
    """Consulta el estado de un envío, con la opción de incluir su historial completo."""
    envio = ESTADOS.get(numero_seguimiento)
    if envio is None:
        return f"No se encontró un envío con el número {numero_seguimiento}."
    if not incluir_historial:
        return envio["actual"]
    historial = ", ".join(envio["historial"])
    return f"{envio['actual']} (historial: {historial})"


@tool
def calcular_costo_envio(
    peso_kg: float,
    distancia_km: float,
) -> str:
    """Calcula el costo estimado de un envío según su peso y la distancia a recorrer.
    Usar cuando el usuario pregunta cuánto va a costar enviar algo."""
    costo = 500 + (peso_kg * 120) + (distancia_km * 3)
    return f"El costo estimado es de ${costo:.2f}."


def construir_agente_con_memoria(modelo_personalizado=None):
    """Configura y retorna el agente con memoria, herramientas y fallbacks."""
    if modelo_personalizado is not None:
        modelo = modelo_personalizado
    else:
        modelo_principal = ChatGoogleGenerativeAI(
            model=MODELOS_DISPONIBLES[0], temperature=0
        )

        if len(MODELOS_DISPONIBLES) > 1:
            modelos_respaldo = [
                ChatGoogleGenerativeAI(model=m, temperature=0)
                for m in MODELOS_DISPONIBLES[1:]
            ]
            modelo = modelo_principal.with_fallbacks(modelos_respaldo)
        else:
            modelo = modelo_principal

    herramientas = [
        consultar_estado_envio_detallado,
        calcular_costo_envio,
    ]

    prompt_agente = ChatPromptTemplate.from_messages([
        (
            "system",
            "Eres un asistente que responde preguntas "
            "usando las herramientas disponibles cuando "
            "las necesites.",
        ),
        MessagesPlaceholder("chat_history"),
        ("human", "{entrada}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agente = create_tool_calling_agent(
        modelo, herramientas, prompt_agente
    )

    ejecutor_agente = AgentExecutor(
        agent=agente,
        tools=herramientas,
        verbose=True,
        return_intermediate_steps=True,
    )

    agente_con_memoria = RunnableWithMessageHistory(
        ejecutor_agente,
        obtener_historial,
        input_messages_key="entrada",
        history_messages_key="chat_history",
    )

    return agente_con_memoria


def registrar_traza(
    session_id: str,
    entrada: str,
    resultado: dict,
    archivo_salida: str = "prompts/trazas_agent.jsonl",
    trace_id: str | None = None,
) -> None:
    """Guarda una interacción del agente como una línea JSON en la carpeta indicada."""
    os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)

    registro = {
        "trace_id": trace_id or trace_id_var.get(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "entrada": entrada,
        "entrada_resumen": resumen_gobernado(entrada),
        "acciones": [
            {
                "herramienta": accion.tool,
                "argumentos": accion.tool_input,
                "observacion": observacion,
            }
            for accion, observacion in resultado.get("intermediate_steps", [])
        ],
        "respuestafinal": resultado.get("output", ""),
    }

    with open(archivo_salida, "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")


def invocar_agente_con_traza(
    agente_runnable,
    session_id: str,
    entrada_texto: str,
    archivo_eventos: str = "reports/eventos_agente.jsonl",
):
    """Invoca el agente propagando trace_id y CallbackObservabilidad."""
    os.makedirs(os.path.dirname(archivo_eventos), exist_ok=True)
    obs_logger = obtener_logger_json("agente_obs", archivo_jsonl=archivo_eventos)
    callback = CallbackObservabilidad(obs_logger)

    trace_id = f"trace-{uuid.uuid4().hex[:8]}"
    token = trace_id_var.set(trace_id)

    config = {
        "configurable": {"session_id": session_id},
        "callbacks": [callback],
        "metadata": {"trace_id": trace_id, "session_id": session_id},
    }

    try:
        obs_logger.info(
            "agente_inicio",
            extra={
                "trace_id": trace_id,
                "extra_data": {
                    "session_id": session_id,
                    "entrada_resumen": resumen_gobernado(entrada_texto),
                },
            },
        )
        resultado = agente_runnable.invoke({"entrada": entrada_texto}, config)
        obs_logger.info(
            "agente_fin",
            extra={
                "trace_id": trace_id,
                "extra_data": {
                    "session_id": session_id,
                    "n_acciones": len(resultado.get("intermediate_steps", [])),
                },
            },
        )
        return resultado, trace_id
    finally:
        trace_id_var.reset(token)


if __name__ == "__main__":
    load_dotenv()
    print("🤖 Iniciando agente con herramientas avanzadas y memoria...\n")

    agente_con_memoria = construir_agente_con_memoria()
    session_id = "cliente_456"
    entrada_texto = "¿Cuál es el estado del envío AR12345, con su historial?"

    resultado, trace_id = invocar_agente_con_traza(
        agente_con_memoria,
        session_id=session_id,
        entrada_texto=entrada_texto,
    )

    print(f"\n📤 Respuesta: {resultado['output']}")
    registrar_traza(session_id, entrada_texto, resultado, trace_id=trace_id)

    cerrar_sesion(session_id)
    print("\n🧹 Sesión cerrada e historial liberado.")