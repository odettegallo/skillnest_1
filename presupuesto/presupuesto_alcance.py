# Tareas con tecnología nueva o no probada en el módulo cuestan más horas
FACTOR_NOVEDAD = 1.5
# Horas de laboratorio y evidencia disponibles en el bloque/módulo
HORAS_DISPONIBLES = 20
# Fracción reservada para pruebas (pytest), documentación y ensayo de defensa
RESERVA_PRUEBAS_DOCS = 0.30
# Fracción reservada para imprevistos
MARGEN_IMPREVISTOS = 0.20
# Capas mínimas obligatorias del MVP
CAPAS_OBLIGATORIAS = {"api", "rag", "contenedor"}

funcionalidades = [
    {
        "id": "RF-01",
        "horas": 2,
        "capa": "api",
        "nombre": "Endpoint FastAPI de evaluación crediticia simulada en JSON",
        "tipo": "imprescindible",
        "novedad": True,
        "sistema_real": False,
    },
    {
        "id": "RF-02",
        "horas": 2,
        "capa": "rag",
        "nombre": "Recuperación con citas de políticas de riesgo desde Chroma persistido",
        "tipo": "imprescindible",
        "novedad": False,
        "sistema_real": False,
    },
    {
        "id": "RF-03",
        "horas": 2,
        "capa": "contenedor",
        "nombre": "Contenedor reproducible que levanta el servicio con un comando",
        "tipo": "imprescindible",
        "novedad": True,
        "sistema_real": False,
    },
    {
        "id": "RF-04",
        "horas": 2,
        "capa": "otra",
        "nombre": "Cálculo de ratios financieros y semáforos con datos sintéticos",
        "tipo": "imprescindible",
        "novedad": False,
        "sistema_real": False,
    },
    {
        "id": "RF-05",
        "horas": 2,
        "capa": "otra",
        "nombre": "Borrador de memo de riesgo y pausa de revisión humana en AMARILLO",
        "tipo": "imprescindible",
        "novedad": True,
        "sistema_real": False,
    },
    {
        "id": "RF-06",
        "horas": 4,
        "capa": "otra",
        "nombre": "Conexión de vistas HTML CredIA (1 a 5) al endpoint local",
        "tipo": "deseable",
        "novedad": True,
        "sistema_real": False,
    },
    {
        "id": "RF-07",
        "horas": 8,
        "capa": "otra",
        "nombre": "Consulta en tiempo real a SII y burós comerciales reales",
        "tipo": "imprescindible",
        "novedad": True,
        "sistema_real": True,
    },
    {
        "id": "RF-08",
        "horas": 6,
        "capa": "otra",
        "nombre": "Integración con core bancario, CRM y autenticación corporativa",
        "tipo": "deseable",
        "novedad": True,
        "sistema_real": True,
    },
]


def horas_reales(f):
    return f["horas"] * (FACTOR_NOVEDAD if f["novedad"] else 1)


def presupuesto():
    neto = 1 - RESERVA_PRUEBAS_DOCS - MARGEN_IMPREVISTOS
    return round(HORAS_DISPONIBLES * neto, 2)


def recortar(lista):
    limite = presupuesto()
    usado = 0.0
    dentro, fuera = [], []
    orden = sorted(
        lista,
        key=lambda f: (f["tipo"] != "imprescindible", horas_reales(f)),
    )
    for f in orden:
        h = horas_reales(f)
        if f["sistema_real"]:
            fuera.append((f, "requiere datos o sistemas reales"))
        elif usado + h <= limite:
            dentro.append(f)
            usado += h
        else:
            fuera.append((f, "no cabe en el presupuesto"))
    return dentro, fuera, usado


def informe(lista):
    pedido = sum(horas_reales(f) for f in lista)
    dentro, fuera, usado = recortar(lista)
    print(
        f"Pedido: {pedido:.1f} h | Presupuesto: {presupuesto():.1f} h "
        f"({pedido / presupuesto():.1f} veces lo disponible)"
    )
    print(f"\nDENTRO DEL MVP ({usado:.1f} h):")
    for f in dentro:
        print(
            f"  {f['id']} {f['nombre']} [{f['capa']}, {horas_reales(f):.1f} h]"
        )
    print("\nFUERA DE ALCANCE:")
    for f, motivo in fuera:
        print(f"  {f['id']} {f['nombre']} -> {motivo}")
    faltantes = CAPAS_OBLIGATORIAS - {f["capa"] for f in dentro}
    if faltantes:
        print(
            "\nATENCION: capas obligatorias sin cubrir:",
            ", ".join(sorted(faltantes)),
        )
    else:
        print("\nLas tres capas obligatorias estan cubiertas.")


if __name__ == "__main__":
    informe(funcionalidades)
