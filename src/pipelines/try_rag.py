# Evaluacion de la recuperacion: precision y recall promedio sobre un conjunto de casos.
# Python puro: no necesita librerias externas ni una API key.

# 1. Conjunto de evaluacion: lista de diccionarios, uno por pregunta
casos_evaluacion = [
    {
        "pregunta": "que hace el cliente si una llamada tarda demasiado",
        "ids_relevantes": {"doc0"},
    },
    {
        "pregunta": "que pasa si la clave de api es invalida",
        "ids_relevantes": {"doc1"},
    },
    {
        "pregunta": "como se calcula el costo de una llamada",
        "ids_relevantes": {"doc2"},
    },
    {
        "pregunta": "como decide el agente que herramienta usar",
        "ids_relevantes": {"doc3"},
    },
]

# 2. Metricas, con validaciones para listas vacias
def precision_at_k(ids_recuperados: list[str], ids_relevantes: set[str]) -> float:
    """Fraccion de los ids recuperados que son relevantes.
    Devuelve 0.0 si el retriever no devolvio ningun id."""
    if not ids_recuperados:
        return 0.0
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_recuperados)


def recall_at_k(ids_recuperados: list[str], ids_relevantes: set[str]) -> float | None:
    """Fraccion de los ids relevantes que se recuperaron.
    Devuelve None si el caso no tiene ids relevantes (no hay nada que recuperar)."""
    if not ids_relevantes:
        return None
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_relevantes)


def promediar(valores) -> float:
    """Promedio que ignora los None y evita dividir por cero."""
    validos = [v for v in valores if v is not None]
    return sum(validos) / len(validos) if validos else 0.0


# 3. Version simulada: reemplaza retriever.invoke por resultados fijos
ids_recuperados_por_pregunta = {
    "que hace el cliente si una llamada tarda demasiado": ["doc0", "doc4", "doc2"],
    "que pasa si la clave de api es invalida": ["doc2", "doc4", "doc3"],
    "como se calcula el costo de una llamada": ["doc2", "doc0", "doc4"],
    "como decide el agente que herramienta usar": ["doc4", "doc3", "doc1"],
}


def evaluar_recuperacion_simulada(casos, k=3):
    resultados = []
    for caso in casos:
        ids_recuperados = ids_recuperados_por_pregunta[caso["pregunta"]][:k]
        p = precision_at_k(ids_recuperados, caso["ids_relevantes"])
        r = recall_at_k(ids_recuperados, caso["ids_relevantes"])
        resultados.append({
            "pregunta": caso["pregunta"][:40],
            "precision": round(p, 3),
            "recall": r,
        })
    
    precision_promedio = promediar([x["precision"] for x in resultados])
    recall_promedio = promediar([x["recall"] for x in resultados])
    return resultados, round(precision_promedio, 3), round(recall_promedio, 3)


# Ejecución de la simulación
resultados, p_prom, r_prom = evaluar_recuperacion_simulada(casos_evaluacion)
for r in resultados:
    print(r)
print("precision promedio:", p_prom)
print("recall promedio:", r_prom)

# 4. Casos borde: ya no lanzan ZeroDivisionError
print()
print(precision_at_k([], {"doc0"}))
print(recall_at_k(["doc0"], set()))