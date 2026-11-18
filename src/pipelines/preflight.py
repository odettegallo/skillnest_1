import os
from importlib.metadata import version, PackageNotFoundError

from dotenv import load_dotenv

load_dotenv()

PAQUETES_REQUERIDOS = [
    "google-genai",
    "langchain-google-genai",
    "langchain-chroma",
    "chromadb",
    "python-dotenv",
]

print("=== VERIFICACIÓN DE ENTORNO (PREFLIGHT) ===\n")

faltantes = []
for paquete in PAQUETES_REQUERIDOS:
    try:
        v = version(paquete)
        print(f"[OK] {paquete} instalado (versión {v})")
    except PackageNotFoundError:
        print(f"[ERROR] {paquete} NO encontrado")
        faltantes.append(paquete)

if faltantes:
    raise SystemExit(
        f"\nFaltan librerías críticas: {', '.join(faltantes)}. "
        "Ejecuta: pip install -r requirements.txt"
    )

print()
if os.environ.get("GEMINI_API_KEY"):
    print("[OK] GEMINI_API_KEY detectada en el entorno.")
    print("\nTodo listo para ejecutar los pipelines y agentes.")
else:
    raise SystemExit(
        '[ERROR] Falta GEMINI_API_KEY. Agrégala al archivo ".env" en la raíz de tu proyecto.'
    )

def preflight_check(persist_directory, gitignore_path=".gitignore"):
    """Confirma, sin llamar a ninguna API, que lo basico del flujo esta en orden."""
    problemas = []
    
    if not os.path.isdir(persist_directory):
        problemas.append(f"{persist_directory} no existe: corriste la indexacion?")
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, encoding="utf-8") as archivo:
            contenido = archivo.read()
            nombre_carpeta = persist_directory.rstrip("/")
            if nombre_carpeta not in contenido:
                problemas.append(f"{persist_directory} no esta en {gitignore_path}")
    else:
        problemas.append(f"no existe {gitignore_path} en este proyecto")
        
    return problemas

if __name__ == "__main__":
    problemas = preflight_check("vectorstore/")
    if problemas:
        print("Preflight con problemas:")
        for problema in problemas:
            print("-", problema)
    else:
        print("Preflight OK: la carpeta del indice existe y esta en .gitignore")