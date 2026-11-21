# pipelines/aprobar_prompt.py
from typing import TypedDict
import uuid

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from core.prompt_registry import diff_prompts

try:
    from core.security import detectar_inyeccion
except ImportError:
    detectar_inyeccion = None


class EstadoDespliegue(TypedDict):
    nombre_prompt: str
    version_anterior_texto: str
    version_nueva_texto: str
    huella_nueva: str
    diff_lineas: list[str]
    alertas_seguridad: list[str]
    aprobado: bool
    desplegado: bool


def nuevo_thread_id(prefijo: str = "despliegue") -> str:
    return f"{prefijo}-{uuid.uuid4().hex[:8]}"


def construir_grafo(checkpointer=None, logger=None):
    def proponer_version(estado: EstadoDespliegue) -> dict:
        lineas_diff = estado.get("diff_lineas")
        if not lineas_diff:
            lineas_diff = diff_prompts(
                estado["version_anterior_texto"],
                estado["version_nueva_texto"],
            )

        alertas = (
            detectar_inyeccion(estado["version_nueva_texto"])
            if detectar_inyeccion is not None
            else []
        )

        if logger:
            logger.info(
                "propuesta_prompt_generada",
                extra={
                    "extra_data": {
                        "nombre_prompt": estado["nombre_prompt"],
                        "huella_nueva": estado["huella_nueva"],
                        "n_alertas_seguridad": len(alertas),
                    }
                },
            )

        print(
            f"[1/3 PROPUESTA] Prompt '{estado['nombre_prompt']}' | "
            f"Huella: {estado['huella_nueva']} | Alertas: {len(alertas)}"
        )
        return {
            "diff_lineas": lineas_diff,
            "alertas_seguridad": alertas,
            "desplegado": False,
        }

    def punto_de_supervision(estado: EstadoDespliegue) -> dict:
        print("[2/3 SUPERVISIÓN] Grafo en pausa esperando aprobación humana...")
        decision = interrupt(
            {
                "motivo": "aprobar despliegue de nueva version de prompt a produccion",
                "nombre_prompt": estado["nombre_prompt"],
                "huella_nueva": estado["huella_nueva"],
                "alertas_seguridad": estado.get("alertas_seguridad", []),
                "diff": estado.get("diff_lineas", []),
            }
        )
        return {"aprobado": bool(decision)}

    def desplegar(estado: EstadoDespliegue) -> dict:
        aprobado = bool(estado.get("aprobado", False))
        print(f"[3/3 DESPLIEGUE] Decisión recibida: {'APROBADO' if aprobado else 'RECHAZADO'}")
        if aprobado:
            print(f"  -> Versión {estado['huella_nueva']} marcada como DESPLEGADA.")
            return {"desplegado": True}
        print("  -> Despliegue CANCELADO. Se conserva la versión anterior.")
        return {"desplegado": False}

    grafo = StateGraph(EstadoDespliegue)
    grafo.add_node("proponer_version", proponer_version)
    grafo.add_node("punto_de_supervision", punto_de_supervision)
    grafo.add_node("desplegar", desplegar)

    grafo.add_edge(START, "proponer_version")
    grafo.add_edge("proponer_version", "punto_de_supervision")
    grafo.add_edge("punto_de_supervision", "desplegar")
    grafo.add_edge("desplegar", END)

    return grafo.compile(checkpointer=checkpointer or InMemorySaver())


def resolver(app, config: dict, aprobar: bool, logger=None):
    snapshot = app.get_state(config)
    if not snapshot.next:
        raise ValueError("este thread_id no tiene ninguna aprobacion pendiente")

    resultado = app.invoke(Command(resume=bool(aprobar)), config=config)
    if logger:
        logger.info(
            "supervision_resuelta",
            extra={
                "extra_data": {
                    "aprobado": bool(aprobar),
                    "desplegado": resultado.get("desplegado", False),
                }
            },
        )
    return resultado