# src/core/preflight.py
from importlib.metadata import PackageNotFoundError, version
import os
import sys
from dotenv import load_dotenv

PAQUETES_REQUERIDOS = [
    "google-genai",
    "langchain-google-genai",
    "langchain-chroma",
    "chromadb",
    "python-dotenv",
]


def verificar_entorno(
    paquetes: list[str] | tuple[str, ...] = PAQUETES_REQUERIDOS,
    min_python: tuple[int, int] = (3, 10),
    verbose: bool = True,
) -> None:
    """Verifica versión de Python, dependencias instaladas y GEMINI_API_KEY."""
    load_dotenv()

    if verbose:
        print("=== VERIFICACIÓN DE ENTORNO (PREFLIGHT) ===\n")
        print(f"Python {sys.version.split()[0]}")

    if sys.version_info < min_python:
        req = ".".join(map(str, min_python))
        raise SystemExit(f"[ERROR] Necesitas Python {req} o superior.")

    faltantes = []
    for paquete in paquetes:
        try:
            v = version(paquete)
            if verbose:
                print(f"[OK] {paquete} (v{v})")
        except PackageNotFoundError:
            if verbose:
                print(f"[ERROR] {paquete} NO encontrado")
            faltantes.append(paquete)

    if faltantes:
        raise SystemExit(
            f"\nFaltan librerías críticas: {', '.join(faltantes)}. "
            "Ejecuta: pip install -r requirements.txt"
        )

    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit(
            '\n[ERROR] Falta GEMINI_API_KEY. Agrégala al archivo ".env" en la raíz del proyecto.'
        )

    if verbose:
        print("[OK] GEMINI_API_KEY detectada.")
        print("\nTodo listo para ejecutar los pipelines y agentes.")


def preflight_check(
    persist_directory: str = "vectorstore/",
    gitignore_path: str = ".gitignore",
) -> list[str]:
    """Confirma, sin llamar a ninguna API, que el índice y .gitignore estén en orden."""
    problemas = []
    carpeta_limpia = persist_directory.rstrip("/")

    if not os.path.isdir(persist_directory):
        problemas.append(
            f"{persist_directory} no existe: ¿corriste la indexación?"
        )

    if os.path.exists(gitignore_path):
        with open(gitignore_path, encoding="utf-8") as archivo:
            contenido = archivo.read()
        if carpeta_limpia and carpeta_limpia not in contenido:
            problemas.append(f"{persist_directory} no está en {gitignore_path}")
    else:
        problemas.append(f"No existe {gitignore_path} en este proyecto")

    return problemas


if __name__ == "__main__":
    verificar_entorno()
    print()

    problemas_indice = preflight_check("vectorstore/")
    if problemas_indice:
        print("Preflight de índice con observaciones:")
        for problema in problemas_indice:
            print(" -", problema)
    else:
        print("[OK] Preflight de índice: la carpeta existe y está en .gitignore")