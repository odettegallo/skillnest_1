import os
import sys
import json
import threading
from datetime import datetime, timezone
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)

from core.config import MODELOS_DISPONIBLES

# Importamos lo reutilizable desde agent.py
from agent import (
    obtener_historial,
    cerrar_sesion,
    calcular_costo_envio,
)

# --- Sistema de Supervisión Humana (Compatible con Windows) ---
registro_aprobaciones = []

# Importación condicional según el sistema operativo
if sys.platform != "win32":
    import select

registro_aprobaciones = []

def esperar_aprobacion(mensaje: str, tiempo_limite_segundos: int = 300) -> bool:
    print(mensaje, end="", flush=True)

    # Si es Linux o macOS, usamos select (nativo y limpio)
    if sys.platform != "win32":
        listo, _, _ = select.select([sys.stdin], [], [], tiempo_limite_segundos)
        if not listo:
            return False
        respuesta = sys.stdin.readline()
    
    # Si es Windows, usamos el método por hilos que no da error
    else:
        resultado_input = {"respuesta": None}
        def leer_entrada():
            try:
                resultado_input["respuesta"] = sys.stdin.readline()
            except Exception:
                pass

        hilo = threading.Thread(target=leer_entrada)
        hilo.daemon = True
        hilo.start()
        hilo.join(timeout=tiempo_limite_segundos)
        
        if hilo.is_alive():
            print("\n[⏰ Tiempo agotado]")
            return False
        respuesta = resultado_input["respuesta"]

    if respuesta is None:
        return False
    return respuesta.strip().lower() == "s"

def registrar_aprobacion(herramienta: str, arguments: dict, aprobado: bool):
    registro_aprobaciones.append({
        "herramienta": herramienta,
        "argumentos": arguments,
        "aprobado": aprobado,
        "momento": datetime.now().isoformat(),
    })


# --- Herramienta Protegida con Aprobación ---
class ArgumentosReembolso(BaseModel):
    numero_pedido: str = Field(description="Número de pedido a reembolsar.")
    monto: float = Field(description="Monto monetario del reembolso.")

@tool("generar_reembolso", args_schema=ArgumentosReembolso)
def generar_reembolso(numero_pedido: str, monto: float) -> str:
    """Genera un reembolso para un pedido. Requiere aprobación humana previa."""
    mensaje = f"\n⚠️ El agente quiere reembolsar ${monto} para el pedido {numero_pedido}. ¿Aprobar? (s/n): "
    aprobado = esperar_aprobacion(mensaje)
    
    registrar_aprobacion(
        herramienta="generar_reembolso",
        arguments={"numero_pedido": numero_pedido, "monto": monto},
        aprobado=aprobado,
    )
    
    if not aprobado:
        return "Reembolso no aprobado por el supervisor humano."
    return f"Reembolso de ${monto} generado para el pedido {numero_pedido}."


# --- Ensamblaje del Agente Supervisor ---
def construir_agente_supervisor():
    modelo = ChatGoogleGenerativeAI(model=MODELOS_DISPONIBLES[0], temperature=0)
    
    herramientas = [
        generar_reembolso,
        calcular_costo_envio,
    ]

    prompt_agente = ChatPromptTemplate.from_messages([
        ("system", "Eres un asistente operativo con capacidad de ejecutar acciones críticas bajo supervisión."),
        MessagesPlaceholder("chat_history"),
        ("human", "{entrada}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agente = create_tool_calling_agent(modelo, herramientas, prompt_agente)
    ejecutor = AgentExecutor(agent=agente, tools=herramientas, verbose=True, return_intermediate_steps=True)

    return RunnableWithMessageHistory(
        ejecutor,
        obtener_historial,
        input_messages_key="entrada",
        history_messages_key="chat_history",
    )

def registrar_traza(session_id: str, entrada: str, resultado: dict, archivo_salida: str = "prompts/trazas_agent.jsonl") -> None:
    """Guarda una interacción del agente como una línea JSON en la carpeta indicada."""
    # Asegurar que la carpeta 'prompt/' exista
    os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)
    
    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "entrada": entrada,
        "acciones": [
            {
                "herramienta": accion.tool,
                "argumentos": accion.tool_input,
                "observacion": observacion,
            }
            for accion, observacion in resultado.get("intermediate_steps", [])
        ],
        "respuestafinal": resultado.get("output", "")
    }
    
    with open(archivo_salida, "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    load_dotenv()
    print("🤖 Iniciando agente supervisor modular...\n")

    agente_sup = construir_agente_supervisor()
    session_id = "supervisor_modular"
    config = {"configurable": {"session_id": session_id}}

    entrada_texto = "Por favor genera un reembolso de 1500.0 para el pedido PED789."
    resultado = agente_sup.invoke({"entrada": entrada_texto}, config)

    print(f"\n📤 Respuesta final: {resultado['output']}")

    # 📌 Guardamos la traza en la carpeta prompt/ también
    registrar_traza(session_id, entrada_texto, resultado)

    cerrar_sesion(session_id)
    print("\n🧹 Sesión cerrada.")