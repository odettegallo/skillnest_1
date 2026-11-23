import os
import sys
from pathlib import Path

# Aseguramos que 'src' esté en el path de Python
RAIZ_PROYECTO = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.join(RAIZ_PROYECTO, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from pipelines.instrumentacion_rag import registrar_consulta


def ejecutar_gate2_demo(
    pregunta: str = "¿Qué hace el cliente si hay un TimeoutError y cómo se calcula el costo?",
    persist_directory: str = "vectorstore/",
    k: int = 3,
):
    if not Path(persist_directory).exists():
        raise FileNotFoundError(
            f"No existe el índice persistido en '{persist_directory}'. "
            "Genera o verifica vectorstore/ antes de ejecutar el servicio."
        )

    return registrar_consulta(
        pregunta=pregunta,
        persist_directory=persist_directory,
        k=k,
        archivo_trazas="reports/trazas_rag.jsonl",
    )

# Aseguramos que la carpeta 'src' esté en el path de Python para importar sin problemas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from pipelines.pipeline_clean_text import ejecutar_pruebas

if __name__ == "__main__":
    print("==================================================")
    print("🚀 EJECUTANDO DEMOSTRACIÓN COMPLETA - GATE 1")
    print("==================================================\n")
    
    try:
        # Ejecuta todo el flujo de 20 casos, métricas y guardado en JSON
        ejecutar_pruebas()
        
        print("\n==================================================")
        print("✅ ¡Demostración completada exitosamente!")
        print("==================================================")
    except Exception as error:
        print(f"\n❌ Error durante la ejecución del flujo: {error}")

    print("=" * 50)
    print("🚀 EJECUTANDO SERVICIO RAG - GATE 2")
    print("=" * 50 + "\n")

    try:
        registro = ejecutar_gate2_demo()
        print(f"Trace ID       : {registro['trace_id']}")
        print(f"Modelo         : {registro['modelo_utilizado']}")
        print(f"Fuentes        : {registro['citas_fuentes']}")
        print(f"Tiempo total   : {registro['tiempo_total_ms']} ms")
        print(f"Costo est. USD : {registro['costo_estimado_usd']}")
        print("\n" + "=" * 50)
        print("✅ ¡Ejecución completada sin excepciones!")
        print("=" * 50)
    except Exception as error:
        print(f"\n❌ Error durante la ejecución del flujo: {error}")