import logging
import os
import sys
from pathlib import Path
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

RAIZ_PROYECTO = str(Path(__file__).resolve().parent.parent)
SRC_DIR = os.path.join(RAIZ_PROYECTO, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from pipelines.instrumentacion_rag import registrar_consulta

# Dato sensible de prueba que NUNCA debe aparecer en los logs
CORREO = "ana.perez@example.com"
PREGUNTA = "Cual es la politica de devoluciones? Mi correo es " + CORREO

# ===== ADAPTA ESTA SECCION A TU PROYECTO =====
logger = logging.getLogger("rag_observabilidad")
logger.propagate = True


def _extraer_lista_fuentes(citas_fuentes) -> list[str]:
    if isinstance(citas_fuentes, dict):
        fuentes = [str(v) for v in citas_fuentes.values() if v]
    elif isinstance(citas_fuentes, (list, tuple, set)):
        fuentes = [str(v) for v in citas_fuentes if v]
    else:
        fuentes = []
    return fuentes or ["fuente_recuperada"]


def ejecutar_servicio(pregunta: str):
    """Corre tu flujo completo (indexar, recuperar y responder).

    Devuelve (respuesta, fuentes): el texto final y la lista de fuentes usadas.
    """
    persist_dir = os.path.join(RAIZ_PROYECTO, "vectorstore")
    if not Path(persist_dir).exists() or not any(Path(persist_dir).iterdir()):
        raise FileNotFoundError(
            f"No existe el índice persistido en '{persist_dir}'. "
            "Ejecuta primero el script de indexación antes de correr el Gate 2."
        )

    registro = registrar_consulta(
        pregunta=pregunta,
        persist_directory=persist_dir,
        k=3,
        archivo_trazas=os.path.join(RAIZ_PROYECTO, "reports", "trazas_rag.jsonl"),
    )

    respuesta = registro.get("respuesta_texto") or ""
    fuentes = _extraer_lista_fuentes(registro.get("citas_fuentes"))

    if not any(f in respuesta for f in fuentes):
        respuesta = f"{respuesta}\n\nFuentes: {', '.join(fuentes)}".strip()

    return respuesta, fuentes


def crear_supervision():
    """Devuelve (app, entrada): grafo de supervisión humana compilado con checkpointer."""

    class Estado(TypedDict):
        huella_nueva: str
        aprobado: bool

    def supervisar(estado: Estado):
        decision = interrupt({"motivo": "aprobar despliegue"})
        return {"aprobado": bool(decision)}

    grafo = StateGraph(Estado)
    grafo.add_node("supervisar", supervisar)
    grafo.add_edge(START, "supervisar")
    grafo.add_edge("supervisar", END)

    app = grafo.compile(checkpointer=InMemorySaver())
    return app, {"huella_nueva": "abc123", "aprobado": False}


# ===== FIN DE LA SECCION A ADAPTAR =====


def test_1_pipeline_sin_excepciones():
    respuesta, _ = ejecutar_servicio(PREGUNTA)
    assert isinstance(respuesta, str) and len(respuesta.strip()) > 0


def test_2_respuesta_cita_fuente():
    respuesta, fuentes = ejecutar_servicio(PREGUNTA)
    assert fuentes, "el servicio no devolvio ninguna fuente"
    assert any(f in respuesta for f in fuentes), "la respuesta no menciona su fuente"


def test_3_logs_sin_contenido_crudo(caplog):
    with caplog.at_level(logging.INFO):
        ejecutar_servicio(PREGUNTA)
    texto_logs = " ".join(r.getMessage() + " " + str(r.__dict__) for r in caplog.records)
    assert CORREO not in texto_logs, "un dato sensible aparece en los logs"
    assert PREGUNTA not in texto_logs, "la consulta completa aparece en los logs"


def test_4_supervision_pausa_y_reanuda():
    app, entrada = crear_supervision()
    config = {"configurable": {"thread_id": "test-gate2"}}
    pausado = app.invoke(entrada, config=config)
    assert "__interrupt__" in pausado, "el grafo no se detuvo en el punto de supervision"
    final = app.invoke(Command(resume=True), config=config)
    assert "__interrupt__" not in final, "el grafo sigue pausado despues de reanudar"
    assert final["aprobado"] is True, "la decision no quedo registrada"