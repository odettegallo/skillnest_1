from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.corpus import LISTA_CORPUS, METADATAS_CORPUS_OFICIAL
from core.prompts import PROMPT_TEMPLATE

# 1. Corpus: documentos de origen, cada uno con su fuente (metadata)
corpus = LISTA_CORPUS

metadatas = METADATAS_CORPUS_OFICIAL

# 2. Chunking: el splitter copia la metadata del documento a cada uno de sus chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=90, chunk_overlap=10)
chunks = splitter.create_documents(corpus, metadatas=metadatas)

print("--- Chunks y su fuente ---")
for c in chunks:
    print(repr(c.page_content[:40]), "->", c.metadata)

# 3. Contexto numerado + mapa de citas {numero: fuente}
def formatear_contexto(chunks_recuperados):
    """Arma un bloque de contexto numerado para el prompt, y un mapa
    numero -> fuente para reconstruir la cita despues."""
    lineas = []
    citas = {}
    for i, doc in enumerate(chunks_recuperados, start=1):
        fuente = doc.metadata.get("fuente", "desconocida")
        lineas.append(f"[{i}] {doc.page_content}")
        citas[i] = fuente
    contexto = "\n\n".join(lineas)
    return contexto, citas

contexto, citas = formatear_contexto(chunks)
print("\n--- Contexto numerado ---")
print(contexto)
print("\n--- Mapa de citas ---")
print(citas)

# 4. Prompt que obliga al modelo a citar
PROMPT_TEMPLATE = PROMPT_TEMPLATE  # Importado desde core.prompts.py

prompt = PROMPT_TEMPLATE.format(
    contexto=contexto,
    pregunta="Que hace el cliente si hay un TimeoutError?"
)
print("\n--- Prompt final ---")
print(prompt)

# 5. Reconstruir la cita a partir de una respuesta de ejemplo del modelo
respuesta_modelo = "El cliente reintenta hasta 3 veces [1]."
print("\n--- Cita reconstruida ---")
print("La cita [1] corresponde a:", citas[1])