from pydantic import BaseModel, Field


class Consulta(BaseModel):
    pregunta: str = Field(
        description="Pregunta del usuario, en lenguaje natural.",
        examples=["Cual es el plazo para devolver un producto?"],
    )


class Respuesta(BaseModel):
    respuesta: str = Field(
        description="Texto de la respuesta."
    )
    fuentes: list[str] = Field(
        description="Documentos que respaldan la respuesta."
    )


class EstadoEnvio(BaseModel):
    pedido_id: str = Field(
        description="Identificador del pedido."
    )
    estado: str = Field(
        description="Estado según los datos simulados."
    )