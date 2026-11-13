from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_chroma import Chroma

# --- PASO 1: Configuración del vector store con embeddings de prueba (sin gastar cuota) ---
print("=" * 150)
print("PASO 1: Creando índice con DeterministicFakeEmbedding")
print("=" * 150)

corpus = [
    "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente.",
    "Los errores de autenticacion nunca se reintentan: fallan de inmediato con un ValueError.",
    "El costo de cada llamada se calcula a partir de totalTokenCount y la tarifa vigente por cada 1000 tokens.",
    "El agente de la Unidad 2.4 decide por si mismo que herramienta usar, segun la descripcion de cada una.",
    "Las pruebas unitarias del cliente usan mocks, de forma que la suite completa corre en menos de un segundo.",
]

metadatas = [{"fuente": f"doc{i}.md"} for i in range(len(corpus))]

fake_emb = DeterministicFakeEmbedding(size=16)
vectorstore_demo = Chroma.from_texts(
    corpus, embedding=fake_emb, metadatas=metadatas, collection_name="demo_similarity"
)

# --- PASO 2: similarity_search básico ---
print("\n" + "="*150)
print("PASO 2: similarity_search básico (k=3)")
print("="*150)

resultados = vectorstore_demo.similarity_search(
    "que pasa si la conexion tarda demasiado", k=3
)

for i, r in enumerate(resultados, 1):
    print(f"{i} {r.page_content[:55]} | {r.metadata}")

# --- PASO 3: similarity_search_with_score ---
print("\n" + "="*150)
print("PASO 3: similarity_search_with_score (distancias)")
print("="*150)

resultados_con_score = vectorstore_demo.similarity_search_with_score(
    "que pasa si la conexion tarda demasiado", k=3
)

for doc_, score in resultados_con_score:
    print(f"{round(score, 4)} | {doc_.page_content[:50]}")

# --- PASO 4: as_retriever y .invoke() ---
print("\n" + "="*150)
print("PASO 4: as_retriever con search_kwargs y .invoke()")
print("="*150)

retriever = vectorstore_demo.as_retriever(search_kwargs={"k": 2})
resultados_retriever = retriever.invoke("cuanto cuesta cada llamada")

for r in resultados_retriever:
    print(f"{r.page_content} | {r.metadata}")