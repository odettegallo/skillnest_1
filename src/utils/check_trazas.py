import json
from collections import defaultdict
from typing import Any, Dict, List


def _extraer_sesiones(registros: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Formato previo: cada registro ya trae "session_id" y "acciones"
    if registros and "acciones" in registros[0]:
        return registros

    # Formato CallbackObservabilidad: eventos sueltos agrupados por trace_id
    agrupados: Dict[str, List[str]] = defaultdict(list)
    for ev in registros:
        if ev.get("msg") == "tool_start" and ev.get("herramienta"):
            identificador = ev.get("trace_id") or "sin-trace-id"
            agrupados[identificador].append(ev["herramienta"])

    return [
        {"session_id": sid, "acciones": [{"herramienta": h} for h in tools]}
        for sid, tools in agrupados.items()
    ]


def marcar_repeticiones_sospechosas(archivo: str = "prompts/trazas_agent.jsonl") -> None:
    """Recorre el archivo de trazas en formato JSONL y detecta herramientas repetidas consecutivamente."""
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            registros = [json.loads(linea) for linea in f if linea.strip()]
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo '{archivo}'. Ejecuta algún agente primero.")
        return

    sesiones = _extraer_sesiones(registros)
    print(f"🔍 Analizando {len(sesiones)} sesiones/trazas...\n")

    for idx, registro in enumerate(sesiones, 1):
        herramientas = [a["herramienta"] for a in registro.get("acciones", [])]
        sospechoso = False
        for i in range(1, len(herramientas)):
            if herramientas[i] == herramientas[i - 1]:
                print(
                    f"⚠️ [Traza #{idx}] Sesión '{registro['session_id']}' usó '{herramientas[i]}' dos veces seguidas."
                )
                sospechoso = True
                break

        if not sospechoso:
            print(f"✅ [Traza #{idx}] Sesión '{registro['session_id']}' sin anomalías.")


if __name__ == "__main__":
    marcar_repeticiones_sospechosas()