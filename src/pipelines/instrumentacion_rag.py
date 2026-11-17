import os
import time
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# --- Importaciones desde tu módulo core ---
from core.prompts import PROMPT_TEMPLATE, formatear_contexto
from core.config import MODELOS_DISPONIBLES, TARIFAS_MODELOS

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

    # En config.py las tarifas están expresadas por millón de tokens
    costo_in = (tokens_in / 1_000_000) * tarifa["entrada"]
    costo_out = (tokens_out / 1_000_000) * tarifa["salida"]
    return round(costo_in + costo_out, 8)


def registrar_consulta(pregunta, persist_directory="vectorstore/", k=3):
    """Corre una consulta RAG real con fallback de modelos, midiendo tiempo, tokens reales y costo."""
    tiempos = {}
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    # 1. Fase de embedding y búsqueda vectorial
    with medir(tiempos, "embed_y_busqueda"):
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": k})
        chunks = retriever.invoke(pregunta)

    # formatear_contexto en core/prompts.py devuelve una tupla: (contexto, citas)
    contexto, citas = formatear_contexto(chunks)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)

    # 2. Fase de generación con rotación de modelos (Fallback)
    respuesta = None
    modelo_utilizado = None
    ultimo_error = None

    with medir(tiempos, "generacion"):
        for modelo in MODELOS_DISPONIBLES:
            try:
                chat_model = ChatGoogleGenerativeAI(model=modelo)
                respuesta = chat_model.invoke(prompt)
                modelo_utilizado = modelo
                break  # Si responde correctamente, salimos del ciclo de fallback
            except Exception as e:
                ultimo_error = e
                print(f"[Fallback] Falló el modelo '{modelo}' ({type(e).__name__}). Probando siguiente...")

    if respuesta is None:
        raise RuntimeError(f"Todos los modelos de respaldo fallaron. Último error: {ultimo_error}")

    # 3. Construcción del registro de telemetría
    tokens_reales = dict(respuesta.usage_metadata) if respuesta.usage_metadata else None
    costo_usd = calcular_costo_real(tokens_reales, modelo_utilizado)

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "modelo_utilizado": modelo_utilizado,
        "pregunta": pregunta,
        "respuesta": respuesta.content,
        "citas_fuentes": citas,
        "k": k,
        "tiempos_ms": {etapa: round(s * 1000, 2) for etapa, s in tiempos.items()},
        "tiempo_total_ms": round(sum(tiempos.values()) * 1000, 2),
        "tokens": tokens_reales,
        "costo_estimado_usd": costo_usd,
    }
    return registro


if __name__ == "__main__":
    # Asegura que el vectorstore exista (puedes cambiarlo por "vectorstore/" si ya tienes otro)
    ruta_vectorstore = "vectorstore/"
    if not Path(ruta_vectorstore).exists():
        print(f"Aviso: No se encontró '{ruta_vectorstore}'. Ejecuta primero 'try_indexar_corpus.py' para crearlo.")

    registro = registrar_consulta(
        pregunta="¿Qué hace el cliente si hay un TimeoutError y cómo se calcula el costo?",
        persist_directory=ruta_vectorstore,
        k=3,
    )

    print(json.dumps(registro, indent=2, ensure_ascii=False))

    # Guardado incremental en formato JSONL (ideal para trazas y auditoría)
    ruta_log = Path("reports/registros_latencia_costo.jsonl")
    ruta_log.parent.mkdir(parents=True, exist_ok=True)

    with open(ruta_log, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")

    print(f"\nRegistro guardado exitosamente en: {ruta_log}")