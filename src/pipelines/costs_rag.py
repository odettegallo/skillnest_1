import time
from contextlib import contextmanager
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_chroma import Chroma

# --- Importaciones desde tu directorio core ---
from core.corpus import LISTA_CORPUS
from core.prompts import PROMPT_TEMPLATE, formatear_contexto
from core.config import MODELOS_DISPONIBLES, TARIFAS_MODELOS

# --- 1. Medición de Tiempos ---
tiempos = {}

@contextmanager
def medir(etapa):
    inicio = time.perf_counter()
    yield
    tiempos[etapa] = time.perf_counter() - inicio

pregunta = "Que hace el cliente si hay un TimeoutError?"

# --- 2. Chunking automático del Corpus Oficial (como en try_indexar_corpus.py) ---
splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=20)
chunks_generados = splitter.create_documents(LISTA_CORPUS)

# Usamos embeddings sintéticos para mantener el script rápido y autocontenido en pruebas locales
embeddings_fake = DeterministicFakeEmbedding(size=16)

# Indexamos usando los documentos generados por el splitter
vectorstore = Chroma.from_documents(
    documents=chunks_generados, 
    embedding=embeddings_fake, 
    collection_name="demo_costos"
)

tiempos.clear()

with medir("embed_query"):
    vector = embeddings_fake.embed_query(pregunta)

with medir("busqueda_vectorial"):
    # Buscamos los chunks más relevantes reales en la base vectorial
    chunks_recuperados = vectorstore.similarity_search(pregunta, k=3)

for etapa, segundos in tiempos.items():
    print(f"{etapa}: {segundos * 1000:.2f} ms")
print(f"total medido: {sum(tiempos.values()) * 1000:.2f} ms")
print()

# --- 3. Construcción del Prompt y Conteo de Tokens ---
# formatear_contexto ya acepta los chunks reales de LangChain devueltiros por similarity_search
contexto, citas = formatear_contexto(chunks_recuperados)
prompt_con_rag = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)

def aprox_tokens(texto):
    """Aproximacion habitual para espanol/ingles: ~4 caracteres por token."""
    return len(texto) // 4

tokens_sin_rag = aprox_tokens(pregunta)
tokens_con_rag = aprox_tokens(prompt_con_rag)
tokens_salida_estimados = 60

print("pregunta sola:")
print(f"  caracteres: {len(pregunta)}")
print(f"  tokens aprox: {tokens_sin_rag}")
print()
print("prompt RAG completo (con chunks reales del corpus):")
print(f"  caracteres: {len(prompt_con_rag)}")
print(f"  tokens aprox: {tokens_con_rag}")
print()
print("factor de crecimiento:", round(len(prompt_con_rag) / len(pregunta), 1), "x")
print()

# --- 4. Cálculo de Costos con Rotación de Modelos ---
def calcular_costo(tokens_entrada, tokens_salida, tarifa_entrada_1k, tarifa_salida_1k):
    costo_entrada = (tokens_entrada / 1000) * tarifa_entrada_1k
    costo_salida = (tokens_salida / 1000) * tarifa_salida_1k
    return costo_entrada + costo_salida

print("=== EVALUACIÓN DE COSTOS SEGÚN ROTACIÓN DE MODELOS ===")
print(f"Modelos configurados en orden de respaldo: {MODELOS_DISPONIBLES}\n")

for modelo in MODELOS_DISPONIBLES:
    tarifa_info = TARIFAS_MODELOS.get(modelo, {"entrada": 0.075, "salida": 0.30})
    
    # Conversión de tarifa por millón a tarifa por cada 1000 tokens
    tarifa_entrada_1k = tarifa_info["entrada"] / 1000
    tarifa_salida_1k = tarifa_info["salida"] / 1000
    
    costo_sin = calcular_costo(tokens_sin_rag, tokens_salida_estimados, tarifa_entrada_1k, tarifa_salida_1k)
    costo_con = calcular_costo(tokens_con_rag, tokens_salida_estimados, tarifa_entrada_1k, tarifa_salida_1k)
    aumento = costo_con / costo_sin if costo_sin > 0 else 0
    
    print(f"🔹 Modelo: [{modelo}]")
    print(f"   Tarifas (Entrada/Salida por M): ${tarifa_info['entrada']} / ${tarifa_info['salida']}")
    print(f"   Costo sin RAG: ${costo_sin:.6f}")
    print(f"   Costo con RAG: ${costo_con:.6f}")
    print(f"   Aumento por RAG: {aumento:.2f}x")
    print("-" * 55)