# src/core/metricas.py
from core.config import TARIFAS_MODELOS


def calcular_costo_por_tokens(
    tokens_entrada: int,
    tokens_salida: int,
    modelo: str,
    tarifas_modelos: dict = TARIFAS_MODELOS,
    redondear: int | None = None,
) -> float | None:
    """Calcula el costo en USD a partir de tokens reales y tarifa por millón."""
    if modelo not in tarifas_modelos:
        return None

    tarifas = tarifas_modelos[modelo]
    entrada_in = tokens_entrada or 0
    salida_out = tokens_salida or 0

    costo = (entrada_in / 1_000_000) * tarifas["entrada"] + (
        salida_out / 1_000_000
    ) * tarifas["salida"]
    return round(costo, redondear) if redondear is not None else costo

def precision_at_k(ids_recuperados, ids_relevantes):
    if not ids_recuperados:
        return 0.0
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_recuperados)

def recall_at_k(ids_recuperados, ids_relevantes):
    if not ids_relevantes:
        return None
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_relevantes)

def f1(precision, recall):
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)

def promediar(valores):
    validos = [v for v in valores if v is not None]
    return sum(validos) / len(validos) if validos else 0.0

def evaluar_recuperacion(retriever, casos, k=3):
    resultados = []
    for caso in casos:
        chunks = retriever.invoke(caso["pregunta"])
        ids_recuperados = [c.id for c in chunks][:k]
        p = precision_at_k(ids_recuperados, caso["ids_relevantes"])
        r = recall_at_k(ids_recuperados, caso["ids_relevantes"])
        resultados.append({"pregunta": caso["pregunta"], "precision": p, "recall": r})
    
    precision_promedio = promediar([x["precision"] for x in resultados])
    recall_promedio = promediar([x["recall"] for x in resultados])
    return resultados, precision_promedio, recall_promedio