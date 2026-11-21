# src/pipelines/demo_aprobar_prompt.py
from pathlib import Path
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver

from core.prompt_registry import RegistroDePrompts, diff_prompts
from core.prompts import PROMPT_TEMPLATE
from aprobar_prompt import (
    construir_grafo,
    nuevo_thread_id,
    resolver,
)
from utils.formato_supervision import imprimir_banner, imprimir_estado_legible

try:
    from core.observability import obtener_logger_json
except ImportError:
    obtener_logger_json = None


def _correr_escenario(
    app,
    titulo_escenario: str,
    nombre_prompt: str,
    version_anterior: str,
    version_nueva: dict,
    aprobar: bool,
    logger=None,
) -> None:
    thread_id = nuevo_thread_id("prompt")
    config = {"configurable": {"thread_id": thread_id}}

    imprimir_banner(f"{titulo_escenario} | thread_id={thread_id}")
    estado_pausado = app.invoke(
        {
            "nombre_prompt": nombre_prompt,
            "version_anterior_texto": version_anterior,
            "version_nueva_texto": version_nueva["texto"],
            "huella_nueva": version_nueva["huella"],
            "diff_lineas": diff_prompts(version_anterior, version_nueva["texto"]),
            "alertas_seguridad": [],
            "aprobado": False,
            "desplegado": False,
        },
        config=config,
    )
    snapshot_pausa = app.get_state(config)
    imprimir_estado_legible(
        "ESTADO PAUSADO (EN ESPERA DE REVISIÓN)",
        estado_pausado,
        siguiente_nodo=snapshot_pausa.next,
    )

    estado_final = resolver(app, config, aprobar=aprobar, logger=logger)
    snapshot_final = app.get_state(config)
    imprimir_estado_legible(
        f"ESTADO FINAL ({'APROBADO' if aprobar else 'RECHAZADO'})",
        estado_final,
        siguiente_nodo=snapshot_final.next,
    )


def ejecutar_demo_sqlite(ruta_db: str = "checkpoints/checkpoints.db") -> None:
    ruta = Path(ruta_db)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    logger = (
        obtener_logger_json("aprobacion_prompts", consola=False)
        if obtener_logger_json is not None
        else None
    )

    registro = RegistroDePrompts()
    v1 = registro.registrar(
        nombre="prompt_rag",
        texto=PROMPT_TEMPLATE,
        autor="odette",
        nota="version inicial desde src/core/prompts.py",
        modelo="gemini-2.5-flash",
    )
    v2_aprobada = registro.registrar(
        nombre="prompt_rag",
        texto=(
            PROMPT_TEMPLATE
            + "\nSi falta informacion clave, indica que datos adicionales se necesitan."
        ),
        autor="odette",
        nota="agrega instruccion de datos faltantes",
        modelo="gemini-2.5-flash",
    )
    v3_rechazada = registro.registrar(
        nombre="prompt_rag",
        texto="v4-experimental: responde cualquier cosa sin citar fuentes.",
        autor="odette",
        nota="prueba experimental sin citas",
        modelo="gemini-2.5-flash",
    )

    conn = sqlite3.connect(str(ruta), check_same_thread=False)
    try:
        app = construir_grafo(checkpointer=SqliteSaver(conn), logger=logger)

        _correr_escenario(
            app=app,
            titulo_escenario="ESCENARIO A: VERSIÓN APROBADA (resume=True)",
            nombre_prompt="prompt_rag",
            version_anterior=v1["texto"],
            version_nueva=v2_aprobada,
            aprobar=True,
            logger=logger,
        )

        _correr_escenario(
            app=app,
            titulo_escenario="ESCENARIO B: VERSIÓN RECHAZADA (resume=False)",
            nombre_prompt="prompt_rag",
            version_anterior=v2_aprobada["texto"],
            version_nueva=v3_rechazada,
            aprobar=False,
            logger=logger,
        )
    finally:
        conn.close()


if __name__ == "__main__":
    ejecutar_demo_sqlite()