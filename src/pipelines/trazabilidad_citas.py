from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Corpus: documentos de origen, cada uno con su fuente (metadata)
corpus = [
    "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente. ",
    "Los errores de autenticacion nunca se reintentan: fallan de inmediato con un ",
    "ValueError.",
    "El costo de cada llamada se calcula a partir de totalTokenCount y la tarifa ",
    "vigente por cada 1000 tokens."
]

metadatas = [
    {"fuente": "manual_cliente.md"},
    {"fuente": "manual_cliente.md"},
    {"fuente": "manual_cliente.md"},
    {"fuente": "manual_costos.md"},
    {"fuente": "manual_costos.md"}
]

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
PROMPT_TEMPLATE = """Responde la pregunta usando SOLO el contexto de abajo. Cita la \
fuente de cada afirmacion con su numero entre corchetes, como [1]. Si el contexto no \
alcanza para responder, dilo explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""

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