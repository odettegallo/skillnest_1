# src/core/corpus.py

# Corpus oficial unificado para todas tus pruebas y pipelines
CORPUS_OFICIAL = {
    "doc0": "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente.",
    "doc1": "Los errores de autenticacion nunca se reintentan: fallan de inmediato con un ValueError.",
    "doc2": "El costo de cada llamada se calcula a partir de totalTokenCount y la tarifa vigente por cada 1000 tokens.",
    "doc3": "El agente de la Unidad 2.4 decide por si mismo que herramienta usar, segun la descripcion de cada una.",
    "doc4": "Las pruebas unitarias del cliente usan mocks, de forma que la suite completa corre en menos de un segundo.",
}

METADATAS_CORPUS_OFICIAL = [
    {"fuente": "manual_cliente.md"},
    {"fuente": "manual_cliente.md"},
    {"fuente": "manual_costos.md"},
    {"fuente": "manual_costos.md"},
    {"fuente": "manual_pruebas.md"},
]

# Lista limpia equivalente para indexación
LISTA_CORPUS = list(CORPUS_OFICIAL.values())

# Casos de evaluación estándar centralizados
CASOS_EVALUACION_OFICIALES = [
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