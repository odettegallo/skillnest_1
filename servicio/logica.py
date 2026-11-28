MANUAL = [
    {
        "fuente": "manual.pdf",
        "palabras": ("devol", "reembols"),
        "texto": "Tienes 30 dias desde la compra para devolver.",
    },
    {
        "fuente": "manual.pdf",
        "palabras": ("envio", "entrega"),
        "texto": "Los envios tardan 5 dias habiles.",
    },
]

PEDIDOS = {
    "PED-1001": "en transito, llega en 2 dias habiles",
    "PED-1002": "entregado",
}


def responder(pregunta: str) -> tuple[str, list[str]]:
    texto = pregunta.lower()

    for entrada in MANUAL:
        if any(
            palabra in texto
            for palabra in entrada["palabras"]
        ):
            return (
                entrada["texto"],
                [entrada["fuente"]],
            )

    return (
        "No encuentro esa informacion en el manual.",
        [],
    )


def estado_envio(pedido_id: str) -> str:
    return PEDIDOS.get(
        pedido_id,
        "sin informacion",
    )


# -----------------------------------------
# Ejemplo de lazy loading para una cadena RAG
# -----------------------------------------

# _cadena = None
#
# def _obtener_cadena():
#     global _cadena
#
#     if _cadena is None:
#         _cadena = construir_cadena()
#
#     return _cadena
#
#
# def responder_rag(pregunta: str):
#     resultado = _obtener_cadena().invoke(pregunta)
#
#     return (
#         resultado["respuesta"],
#         resultado["fuentes"],
#     )