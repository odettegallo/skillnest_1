from datetime import date
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# Importamos desde tus módulos
from core.corpus import CASOS_EVALUACION_OFICIALES
from core.metrics import evaluar_recuperacion

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = Chroma(persist_directory="vectorstore/", embedding_function=embeddings)

def imprimir_resultados(resultados, p_prom, r_prom):
    for r in resultados:
        recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
        print(f"{r['precision']:.2f} {recall_txt}   {r['pregunta']}")
    print(f"promedio -> precision: {p_prom:.3f}  recall: {r_prom:.3f}\n")

SEPARADOR = "=" * 75

# --- PASO 1 ---
print(SEPARADOR)
print("PASO 1: tu conjunto de evaluacion (mismo corpus de siempre)")
print(SEPARADOR)
for caso in CASOS_EVALUACION_OFICIALES:
    print(f"  '{caso['pregunta']}' -> relevantes: {caso['ids_relevantes']}")
print()

# --- PASO 2: primera corrida, k=3 ---
print(SEPARADOR)
print("PASO 2: primera corrida, k=3 (Como se prueba, chequeo 1 de 2)")
print(SEPARADOR)
retriever_k3 = vectorstore.as_retriever(search_kwargs={"k": 3})
res_1, p_prom_1, r_prom_1 = evaluar_recuperacion(retriever_k3, CASOS_EVALUACION_OFICIALES, k=3)
imprimir_resultados(res_1, p_prom_1, r_prom_1)

# --- PASO 3: segunda corrida, k=3 otra vez ---
print(SEPARADOR)
print("PASO 3: segunda corrida, k=3 otra vez -- debe dar identico")
print(SEPARADOR)
res_2, p_prom_2, r_prom_2 = evaluar_recuperacion(retriever_k3, CASOS_EVALUACION_OFICIALES, k=3)
imprimir_resultados(res_2, p_prom_2, r_prom_2)

es_identico = (res_1 == res_2) and (p_prom_1 == p_prom_2) and (r_prom_1 == r_prom_2)
print(f"Identico a la primera corrida: {es_identico}\n")

# --- PASO 4: tercera corrida, k=5 ---
print(SEPARADOR)
print("PASO 4: tercera corrida, k=5 (Como se prueba, chequeo 2)")
print(SEPARADOR)
retriever_k5 = vectorstore.as_retriever(search_kwargs={"k": 5})
res_3, p_prom_3, r_prom_3 = evaluar_recuperacion(retriever_k5, CASOS_EVALUACION_OFICIALES, k=5)
imprimir_resultados(res_3, p_prom_3, r_prom_3)

print(f"recall subio o se mantuvo (k=3 -> k=5): {r_prom_3 >= r_prom_1}")
print(f"precision bajo o se mantuvo (k=3 -> k=5): {p_prom_3 <= p_prom_1}")

# --- Exportar reporte a carpeta 'reports' ---
report_dir = Path("reports")
report_dir.mkdir(parents=True, exist_ok=True)
archivo_salida = report_dir / "resultados_evaluacion.txt"

with open(archivo_salida, "w", encoding="utf-8") as archivo:
    archivo.write(f"Fecha: {date.today()}\n")
    archivo.write("Configuracion: k=3 vs k=5, chunk_size=200, chunk_overlap=30\n\n")
    for r in res_1:
        recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
        archivo.write(f"{r['precision']:.2f} {recall_txt} {r['pregunta']}\n")
    archivo.write(f"\npromedio (k=3) -> precision: {p_prom_1:.3f} recall: {r_prom_1:.3f}\n")
    archivo.write(f"promedio (k=5) -> precision: {p_prom_3:.3f} recall: {r_prom_3:.3f}\n")