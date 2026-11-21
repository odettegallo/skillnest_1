# src/pipelines/try/try_pasos_1_a_3.py
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from core.prompt_registry import RegistroDePrompts, diff_prompts
from core.prompts import PROMPT_TEMPLATE
from core.risks import evaluar_matriz_riesgos
from utils.formato_supervision import imprimir_banner, imprimir_diff


class EstadoDespliegue(TypedDict):
    huella_nueva: str
    aprobado: bool


def construir_grafo_paso_2():
    def proponer(estado: EstadoDespliegue) -> dict:
        print(f"  [nodo: proponer] proponiendo huella {estado['huella_nueva']}")
        return {}

    def supervisar(estado: EstadoDespliegue) -> dict:
        print("  [nodo: supervisar] pausando para aprobación humana...")
        decision = interrupt(
            {
                "motivo": "aprobar nueva version de prompt en produccion",
                "huella_propuesta": estado["huella_nueva"],
            }
        )
        return {"aprobado": bool(decision)}

    def aplicar(estado: EstadoDespliegue) -> dict:
        if estado["aprobado"]:
            print(f"  [nodo: aplicar] version {estado['huella_nueva']} activada")
        else:
            print(
                f"  [nodo: aplicar] version {estado['huella_nueva']} "
                "rechazada, se mantiene la anterior"
            )
        return {}

    grafo = StateGraph(EstadoDespliegue)
    grafo.add_node("proponer", proponer)
    grafo.add_node("supervisar", supervisar)
    grafo.add_node("aplicar", aplicar)

    grafo.add_edge(START, "proponer")
    grafo.add_edge("proponer", "supervisar")
    grafo.add_edge("supervisar", "aplicar")
    grafo.add_edge("aplicar", END)

    return grafo.compile(checkpointer=InMemorySaver())


def main() -> None:
    # --- PASO 1: Registro de versiones reales del prompt y diff ---
    imprimir_banner("PASO 1: REGISTRO DE VERSIONES DE PROMPT Y DIFF")
    prompt_anterior = (
        "Responde la pregunta usando SOLO el contexto de abajo. "
        "Si el contexto no alcanza, dilo.\n\n"
        "Contexto:\n{contexto}\n\nPregunta: {pregunta}\n\nRespuesta:"
    )
    prompt_actual = PROMPT_TEMPLATE

    registro = RegistroDePrompts()
    v_ant = registro.registrar(
        nombre="prompt_rag_citas",
        texto=prompt_anterior,
        autor="odette",
        nota="version anterior sin exigencia de citas numeradas [1]",
    )
    v_act = registro.registrar(
        nombre="prompt_rag_citas",
        texto=prompt_actual,
        autor="odette",
        nota="version actual exigiendo citas [1] y evitando inventar",
    )

    for v in registro.versiones:
        print(f"  {v['huella']} - {v['nota']}")
    ultima_v = registro.ultima("prompt_rag_citas")
    print(f"  ultima: {ultima_v['huella'] if ultima_v else None}\n")

    lineas_diff = diff_prompts(v_ant["texto"], v_act["texto"])
    imprimir_diff(lineas_diff)

    # --- PASO 2: Supervisión con interrupt() y Command(resume=...) ---
    imprimir_banner("PASO 2: SUPERVISIÓN HUMANA (APROBACIÓN Y RECHAZO)")
    app_despliegue = construir_grafo_paso_2()
    huella_objetivo = v_act["huella"]

    config_aprob = {"configurable": {"thread_id": "mi-despliegue-aprobar"}}
    pausa_aprob = app_despliegue.invoke(
        {"huella_nueva": huella_objetivo, "aprobado": False},
        config=config_aprob,
    )
    pendiente_aprob = app_despliegue.get_state(config_aprob).interrupts[0].value
    print("  1) tras invocar (aprobación):", list(pausa_aprob.keys()))
    print("  2) pendiente:", pendiente_aprob)
    final_aprob = app_despliegue.invoke(Command(resume=True), config=config_aprob)
    print("  3) tras aprobar:", final_aprob, "\n")

    config_rech = {"configurable": {"thread_id": "mi-despliegue-rechazar"}}
    app_despliegue.invoke(
        {"huella_nueva": huella_objetivo, "aprobado": False},
        config=config_rech,
    )
    final_rech = app_despliegue.invoke(Command(resume=False), config=config_rech)
    print("  4) tras rechazar:", final_rech)

    # --- PASO 3: Matriz de riesgos (mínimo 5 filas) ---
    imprimir_banner("PASO 3: MATRIZ DE RIESGOS")
    mis_riesgos = [
        {
            "riesgo": "Inyeccion de prompt via documento recuperado en RAG",
            "probabilidad": 4,
            "impacto": 4,
            "mitigacion": "Filtro de patrones sospechosos en security.py y delimitacion de contexto",
        },
        {
            "riesgo": "Despliegue de prompt defectuoso sin revision humana",
            "probabilidad": 2,
            "impacto": 4,
            "mitigacion": "Pausa con interrupt() y reanudacion explicita con Command(resume=...)",
        },
        {
            "riesgo": "Perdida de estado de aprobacion al reiniciar proceso",
            "probabilidad": 2,
            "impacto": 3,
            "mitigacion": "Persistencia con SqliteSaver en checkpoints/checkpoints.db",
        },
        {
            "riesgo": "Cambio silencioso de prompt sin trazabilidad",
            "probabilidad": 3,
            "impacto": 3,
            "mitigacion": "RegistroDePrompts con huella SHA-256 y diff_prompts()",
        },
        {
            "riesgo": "Sobrecosto por contexto RAG extenso en consultas frecuentes",
            "probabilidad": 3,
            "impacto": 2,
            "mitigacion": "Estimacion de tokens y costos por modelo en costs_rag.py",
        },
    ]

    evaluados = evaluar_matriz_riesgos(mis_riesgos)
    for r in sorted(evaluados, key=lambda x: -x["puntaje"]):
        etiqueta_limite = " [AL LIMITE]" if r["al_limite"] else ""
        print(
            f"  {r['categoria']:8} ({r['puntaje']:2}) - {r['riesgo']}{etiqueta_limite}"
        )
        print(f"             Mitigación: {r['mitigacion']}")


if __name__ == "__main__":
    main()