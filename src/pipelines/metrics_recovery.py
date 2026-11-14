# metrics_recovery.py
from core.corpus import CORPUS_OFICIAL
# --- IMPORTAMOS LAS MÉTRICAS DESDE EL MÓDULO CENTRAL ---
from core.metrics import precision_at_k, recall_at_k, f1

if __name__ == "__main__":
    corpus = CORPUS_OFICIAL
    pregunta = "que hace el cliente si una llamada tarda demasiado?"
    ids_relevantes = {"doc0"} 
    ids_recuperados = ["doc2", "doc0", "doc4"] 
    ranked = ["doc2", "doc4", "doc0", "doc1", "doc3"] 

    print("precision@3:", precision_at_k(ids_recuperados, ids_relevantes))
    print("recall@3:", recall_at_k(ids_recuperados, ids_relevantes))

    print()
    for k in range(1, 6):
        sub = ranked[:k]
        p = precision_at_k(sub, ids_relevantes)
        r = recall_at_k(sub, ids_relevantes)
        print(f"k={k}: precision={p:.3f} recall={r:.3f} recuperados={sub}")

    print()
    for k in range(1, 6):
        sub = ranked[:k]
        p = precision_at_k(sub, ids_relevantes)
        r = recall_at_k(sub, ids_relevantes)
        print(f"k={k}: F1={f1(p, r):.3f}")