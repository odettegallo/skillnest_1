import json

def marcar_repeticiones_sospechosas(archivo: str = "prompt/trazas_agent.jsonl") -> None:
    """Recorre el archivo de trazas en formato JSONL y detecta herramientas repetidas consecutivamente."""
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            registros = [json.loads(linea) for linea in f]
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo '{archivo}'. Ejecuta algún agente primero.")
        return

    print(f"🔍 Analizando {len(registros)} registros de traza...\n")

    for idx, registro in enumerate(registros, 1):
        herramientas = [
            a["herramienta"] for a in registro.get("acciones", [])
        ]
        
        # Verificar repeticiones consecutivas
        sospechoso = False
        for i in range(1, len(herramientas)):
            if herramientas[i] == herramientas[i - 1]:
                print(f"⚠️ [Traza #{idx}] Sesión '{registro['session_id']}' usó '{herramientas[i]}' dos veces seguidas.")
                sospechoso = True
                break
        
        if not sospechoso:
            print(f"✅ [Traza #{idx}] Sesión '{registro['session_id']}' sin anomalías.")

if __name__ == "__main__":
    marcar_repeticiones_sospechosas()