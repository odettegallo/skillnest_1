import json
import os
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from core.config import MODELOS_DISPONIBLES, TARIFAS_MODELOS
from core.prompts import PROMPT_TEMPLATE, formatear_contexto, _extraer_texto_respuesta
from utils.observability import (
    CallbackObservabilidad,
    obtener_logger_json,
    resumen_gobernado,
    trace_id_var,
)

load_dotenv()

if not os.environ.get("GEMINI_API_KEY"):
    raise SystemExit('Falta GEMINI_API_KEY. Defínela en tu archivo ".env" y vuelve a ejecutar.')


@contextmanager
def medir(tiempos, etapa):
    inicio = time.perf_counter()
    yield
    tiempos[etapa] = time.perf_counter() - inicio


def calcular_costo_real(usage_metadata, modelo):
    """Calcula el costo en USD usando los tokens reales reportados por la API y la tarifa del modelo activo."""
    if not usage_metadata or modelo not in TARIFAS_MODELOS:
        return None

    tarifa = TARIFAS_MODELOS[modelo]
    tokens_in = usage_metadata.get("input_tokens", 0)
    tokens_out = usage_metadata.get("output_tokens", 0)

    costo_in = (tokens_in / 1_000_000) * tarifa["entrada"]
    costo_out = (tokens_out / 1_000_000) * tarifa["salida"]
    return round(costo_in + costo_out, 8)


def registrar_consulta(
    pregunta,
    persist_directory="vectorstore/",
    k=3,
    archivo_trazas="reports/trazas_rag.jsonl",
):
    """Corre una consulta RAG real con fallback de modelos, trace_id y callbacks de observabilidad."""
    Path(archivo_trazas).parent.mkdir(parents=True, exist_ok=True)
    logger = obtener_logger_json("rag_observabilidad", archivo_jsonl=archivo_trazas, consola=False)
    callback = CallbackObservabilidad(logger)

    trace_id = f"trace-{uuid.uuid4().hex[:8]}"
    token_ctx = trace_id_var.set(trace_id)
    tiempos = {}

    try:
        logger.info(
            "consulta_recibida",
            extra={
                "trace_id": trace_id,
                "extra_data": {
                    "k": k,
                    "pregunta_resumen": resumen_gobernado(pregunta),
                },
            },
        )

        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        config_run = {"callbacks": [callback], "metadata": {"trace_id": trace_id}}

        with medir(tiempos, "embed_y_busqueda"):
            vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings,
            )
            retriever = vectorstore.as_retriever(search_kwargs={"k": k})
            chunks = retriever.invoke(pregunta, config=config_run)

        contexto, citas = formatear_contexto(chunks)
        prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)

        respuesta = None
        modelo_utilizado = None
        ultimo_error = None

        with medir(tiempos, "generacion"):
            for modelo in MODELOS_DISPONIBLES:
                try:
                    chat_model = ChatGoogleGenerativeAI(model=modelo)
                    respuesta = chat_model.invoke(prompt, config=config_run)
                    modelo_utilizado = modelo
                    break
                except Exception as e:
                    ultimo_error = e
                    logger.warning(
                        "fallback_modelo",
                        extra={
                            "trace_id": trace_id,
                            "extra_data": {
                                "modelo_fallido": modelo,
                                "error_tipo": type(e).__name__,
                            },
                        },
                    )

        if respuesta is None:
            raise RuntimeError(f"Todos los modelos de respaldo fallaron. Último error: {ultimo_error}")

        tokens_reales = dict(respuesta.usage_metadata) if respuesta.usage_metadata else None
        costo_usd = calcular_costo_real(tokens_reales, modelo_utilizado)

        registro = {
            "trace_id": trace_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "modelo_utilizado": modelo_utilizado,
            "pregunta_resumen": resumen_gobernado(pregunta),
            "respuesta_resumen": resumen_gobernado(respuesta.content),
            "respuesta_texto": _extraer_texto_respuesta(respuesta),
            "citas_fuentes": citas,
            "k": k,
            "tiempos_ms": {etapa: round(s * 1000, 2) for etapa, s in tiempos.items()},
            "tiempo_total_ms": round(sum(tiempos.values()) * 1000, 2),
            "tokens": tokens_reales,
            "costo_estimado_usd": costo_usd,
        }
        return registro
    finally:
        trace_id_var.reset(token_ctx)

def _extraer_texto_respuesta(respuesta) -> str:
    contenido = getattr(respuesta, "content", "")
    if isinstance(contenido, str):
        return contenido
    if isinstance(contenido, list):
        partes = []
        for bloque in contenido:
            if isinstance(bloque, dict) and bloque.get("type") == "text":
                partes.append(bloque.get("text", ""))
            elif isinstance(bloque, str):
                partes.append(bloque)
        return "\n".join(p for p in partes if p).strip()
    return str(contenido)

if __name__ == "__main__":
    ruta_vectorstore = "vectorstore/"
    if not Path(ruta_vectorstore).exists():
        print(
            f"[AVISO] No se encontró '{ruta_vectorstore}'. "
            "Ejecuta primero el script de indexación para crearlo."
        )

    pregunta = "¿Qué hace el cliente si hay un TimeoutError y cómo se calcula el costo?"

    print("=" * 60)
    print("PASO 1: EJECUCIÓN RAG Y TRAZAS (guardadas en reports/trazas_rag.jsonl)")
    print("=" * 60)
    registro = registrar_consulta(
        pregunta=pregunta,
        persist_directory=ruta_vectorstore,
        k=3,
        archivo_trazas="reports/trazas_rag.jsonl",
    )
    print(f"Trace ID : {registro['trace_id']}")
    print(f"Modelo   : {registro['modelo_utilizado']}")
    print(f"Fuentes  : {registro['citas_fuentes']}")

    print("\n" + "=" * 60)
    print("PASO 2: MÉTRICAS DE LATENCIA Y COSTO")
    print("=" * 60)
    print(f"Búsqueda (ms) : {registro['tiempos_ms'].get('embed_y_busqueda')}")
    print(f"Generación (ms) : {registro['tiempos_ms'].get('generacion')}")
    print(f"Total (ms)      : {registro['tiempo_total_ms']}")
    if registro.get("tokens"):
        tokens = registro["tokens"]
        print(
            f"Tokens          : in={tokens.get('input_tokens')} | "
            f"out={tokens.get('output_tokens')} | "
            f"total={tokens.get('total_tokens')}"
        )
    print(f"Costo est. USD  : {registro.get('costo_estimado_usd')}")

    ruta_log = Path("reports/registros_latencia_costo.jsonl")
    ruta_log.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta_log, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")

    ruta_trazas = Path("reports/trazas_rag.jsonl")

    print("\n" + "=" * 60)
    print("PASO 3: ARCHIVOS GENERADOS")
    print("=" * 60)
    print(f"- Eventos paso a paso : {ruta_trazas}")
    print(f"- Métricas y costos   : {ruta_log}")

    print("\n" + "=" * 60)
    print("RESPUESTA DEL MODELO")
    print("=" * 60)
    print(registro.get("respuesta_texto") or "(Sin contenido de texto)")