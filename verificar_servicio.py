from fastapi.testclient import TestClient

from servicio.main import app

cliente = TestClient(app)

PREGUNTA = (
    "Cual es el plazo para devolver un producto?"
)


def esquema():
    return cliente.get(
        "/openapi.json"
    ).json()


def docs_navegables():
    respuesta = cliente.get("/docs")

    if respuesta.status_code != 200:
        return (
            False,
            f"/docs responde {respuesta.status_code}",
        )

    return (
        True,
        f"rutas documentadas: {sorted(esquema()['paths'])}",
    )


def campos_documentados():
    esquemas = esquema()["components"]["schemas"]

    sin_descripcion = [
        f"{nombre}.{campo}"
        for nombre in (
            "Consulta",
            "Respuesta",
            "EstadoEnvio",
        )
        for campo, datos in esquemas[nombre][
            "properties"
        ].items()
        if "description" not in datos
    ]

    if sin_descripcion:
        return (
            False,
            f"sin descripcion: {sin_descripcion}",
        )

    return (
        True,
        "todos los campos tienen descripcion",
    )


def ca_01():
    respuesta = cliente.post(
        "/consultas",
        json={"pregunta": PREGUNTA},
    )

    ok = (
        respuesta.status_code == 200
        and set(respuesta.json())
        == {"respuesta", "fuentes"}
    )

    return (
        ok,
        f"estado {respuesta.status_code}, campos {sorted(respuesta.json())}",
    )


def ca_02():
    respuesta = cliente.post(
        "/consultas",
        json={"pregunta": PREGUNTA},
    )

    datos = respuesta.json()

    ok = (
        "manual.pdf" in datos["fuentes"]
        and "30 dias" in datos["respuesta"]
    )

    return (
        ok,
        f"fuentes: {datos['fuentes']}",
    )


def ca_03():
    respuesta = cliente.post(
        "/consultas",
        json={
            "pregunta": "Venden gift cards?"
        },
    )

    datos = respuesta.json()

    ok = (
        datos["fuentes"] == []
        and datos["respuesta"].startswith(
            "No encuentro"
        )
    )

    return (
        ok,
        f"fuentes: {datos['fuentes']}",
    )


def ca_04():
    respuesta = cliente.get(
        "/envios/PED-1001"
    )

    return (
        "transito"
        in respuesta.json()["estado"],
        f"estado: {respuesta.json()['estado']}",
    )


COMPROBACIONES = [
    (
        "DOC-1",
        "documentacion en /docs",
        docs_navegables,
    ),
    (
        "DOC-2",
        "campos documentados",
        campos_documentados,
    ),
    (
        "CA-01",
        "respuesta con respuesta y fuentes",
        ca_01,
    ),
    (
        "CA-02",
        "fuente manual.pdf y 30 dias",
        ca_02,
    ),
    (
        "CA-03",
        "sin informacion: no inventa",
        ca_03,
    ),
    (
        "CA-04",
        "estado del pedido simulado",
        ca_04,
    ),
]


def ejecutar(comprobaciones):
    cumplidas = 0

    for (
        identificador,
        descripcion,
        prueba,
    ) in comprobaciones:

        try:
            ok, evidencia = prueba()

        except Exception as error:
            ok = False
            evidencia = (
                f"error: {type(error).__name__}"
                f"({error})"
            )

        estado = (
            "PASA "
            if ok
            else "FALLA"
        )

        print(
            f"{estado} {identificador} "
            f"{descripcion} -> {evidencia}"
        )

        if ok:
            cumplidas += 1

    print(
        f"\n{cumplidas} de "
        f"{len(comprobaciones)} "
        "comprobaciones cumplidas"
    )

    return (
        cumplidas
        == len(comprobaciones)
    )


if __name__ == "__main__":
    raise SystemExit(
        0
        if ejecutar(COMPROBACIONES)
        else 1
    )