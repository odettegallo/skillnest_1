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

def _extraer_texto_respuesta(respuesta) -> str:
    contenido = getattr(respuesta, "content", "")
    if isinstance(contenido, str):
        return contenido.strip()

    if isinstance(contenido, list):
        partes = []
        for bloque in contenido:
            if isinstance(bloque, str):
                partes.append(bloque)
            elif isinstance(bloque, dict):
                if isinstance(bloque.get("text"), str):
                    partes.append(bloque["text"])
                elif isinstance(bloque.get("content"), str):
                    partes.append(bloque["content"])
            else:
                texto_attr = getattr(bloque, "text", None)
                if isinstance(texto_attr, str):
                    partes.append(texto_attr)

        texto_unido = "\n".join(p.strip() for p in partes if p and p.strip()).strip()
        if texto_unido:
            return texto_unido

    texto_final = str(contenido).strip()
    return texto_final if texto_final not in ("", "[]") else ""