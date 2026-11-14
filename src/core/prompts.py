# src/core/prompts.py

PROMPT_TEMPLATE = """Responde la pregunta usando SOLO el contexto de abajo. Cita la fuente de cada afirmacion con su numero entre corchetes, como [1]. Si el contexto no alcanza para responder, dilo explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""

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