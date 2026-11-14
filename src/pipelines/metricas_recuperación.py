# Metricas de recuperacion: precision@k, recall@k y F1.
# Solo Python estandar: no necesita instalar ninguna libreria ni una API key.

def precision_at_k(ids_recuperados, ids_relevantes):
    """Fraccion de los ids recuperados que de verdad son relevantes."""
    if not ids_recuperados:
        return 0.0
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_recuperados)

def recall_at_k(ids_recuperados, ids_relevantes):
    """Fraccion de los ids relevantes que efectivamente se recuperaron."""
    if not ids_relevantes:
        return 0.0
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_relevantes)

def f1(precision, recall):
    """Media harmonica de precision y recall."""
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


if __name__ == "__main__":
    # Datos de partida: corpus de 5 documentos, un chunk por documento
    corpus = {
        "doc0": "El cliente reintenta hasta 3 veces ante un TimeOutError, con espera creciente.",
        "doc1": "Los errores de autenticacion nunca se reintentan: fallan de inmediato con un ValueError.",
        "doc2": "El costo de cada llamada se calcula a partir de totalTokenCount y la tarifa vigente por cada 1000 tokens.",
        "doc3": "El agente de la Unidad 2.4 decide por si mismo que herramienta usar, segun la descripcion de cada una.",
        "doc4": "Las pruebas unitarias del cliente usan mocks, de forma que la suite completa corre en menos de un segundo.",
    }
    
    pregunta = "que hace el cliente si una llamada tarda demasiado?"
    ids_relevantes = {"doc0"} # etiquetado a mano: solo doc0 responde la pregunta
    ids_recuperados = ["doc2", "doc0", "doc4"] # lo que devolvio el retriever con k=3
    ranked = ["doc2", "doc4", "doc0", "doc1", "doc3"] # ranking completo, de mas a menos parecido

    # 1. Precision y recall con k=3
    print("precision@3:", precision_at_k(ids_recuperados, ids_relevantes))
    print("recall@3:", recall_at_k(ids_recuperados, ids_relevantes))

    # 2. El trade-off al variar k
    print()
    for k in range(1, 6):
        sub = ranked[:k]
        p = precision_at_k(sub, ids_relevantes)
        r = recall_at_k(sub, ids_relevantes)
        print(f"k={k}: precision={p:.3f} recall={r:.3f} recuperados={sub}")

    # 3. F1 para cada k
    print()
    for k in range(1, 6):
        sub = ranked[:k]
        p = precision_at_k(sub, ids_relevantes)
        r = recall_at_k(sub, ids_relevantes)
        print(f"k={k}: F1={f1(p, r):.3f}")