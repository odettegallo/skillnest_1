from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Asistente de soporte", version="0.1.0")

PEDIDOS = {
    "PED-1001": "en transito, llega en 2 dias habiles",
    "PED-1002": "entregado",
}


class Consulta(BaseModel):
    pregunta: str


class Respuesta(BaseModel):
    respuesta: str
    fuentes: list[str]


@app.get("/salud")
def salud():
    return {"estado": "ok"}


@app.get("/envios/{pedido_id}")
def estado_envio(pedido_id: str, detalle: bool = False):
    estado = PEDIDOS.get(pedido_id, "sin informacion")
    if detalle:
        return {"pedido_id": pedido_id, "estado": estado, "simulado": True}
    return {"pedido_id": pedido_id, "estado": estado}


@app.post("/consultas", response_model=Respuesta)
def consultar(consulta: Consulta):
    if "devol" in consulta.pregunta.lower():
        return Respuesta(
            respuesta="Tienes 30 dias desde la compra para devolver.",
            fuentes=["manual.pdf"],
        )
    return Respuesta(
        respuesta="No encuentro esa informacion en el manual.",
        fuentes=[],
    )