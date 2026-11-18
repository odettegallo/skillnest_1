# try_rag.py
from core.corpus import CASOS_EVALUACION_OFICIALES
# --- IMPORTAMOS LAS MÉTRICAS DESDE EL MÓDULO CENTRAL ---
from core.metrics import precision_at_k, recall_at_k, promediar

casos_evaluacion = CASOS_EVALUACION_OFICIALES

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

resultados, p_prom, r_prom = evaluar_recuperacion_simulada(casos_evaluacion)
for r in resultados:
    print(r)
print("precision promedio:", p_prom)
print("recall promedio:", r_prom)

print()
print(precision_at_k([], {"doc0"}))
print(recall_at_k(["doc0"], set()))