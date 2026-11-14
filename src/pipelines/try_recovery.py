from datetime import date
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# Importamos todo lo necesario desde los módulos
from core.corpus import CASOS_EVALUACION_OFICIALES
from core.metrics import evaluar_recuperacion

load_dotenv()

# Configuración inicial
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = Chroma(persist_directory="vectorstore/", embedding_function=embeddings)

print("IDs en el índice:", vectorstore.get()["ids"])

K = 3
retriever = vectorstore.as_retriever(search_kwargs={"k": K})

# Ejecución limpia de la evaluación
resultados, precision_promedio, recall_promedio = evaluar_recuperacion(
    retriever, CASOS_EVALUACION_OFICIALES, k=K
)

# Mostrar resultados en consola
for r in resultados:
    recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
    print(f"{r['precision']:.2f} {recall_txt} {r['pregunta']}")
print(f"\npromedio -> precision: {precision_promedio:.3f} recall: {recall_promedio:.3f}")

# Guardar resultados en archivo
report_dir = Path("reports")
report_dir.mkdir(parents=True, exist_ok=True)  # Crea la carpeta si no existe

archivo_salida = report_dir / "resultados_evaluacion.txt"

with open(archivo_salida, "w", encoding="utf-8") as archivo:
    archivo.write(f"Fecha: {date.today()}\n")
    archivo.write(f"Configuracion: k={K}, chunk_size=200, chunk_overlap=30\n")
    for r in resultados:
        recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
        archivo.write(f"{r['precision']:.2f} {recall_txt} {r['pregunta']}\n")
    archivo.write(f"\npromedio -> precision: {precision_promedio:.3f} recall: {recall_promedio:.3f}\n")

print("Resultados guardados en ", archivo_salida)