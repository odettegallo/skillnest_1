import json
from pathlib import Path

# Ruta donde se guardó el archivo de trazas en el script anterior
ruta_log = Path("reports/registros_latencia_costo.jsonl")

if not ruta_log.exists():
    print(f"Aviso: No se encontró el archivo de registros en '{ruta_log}'.")
    print("Ejecuta primero 'instrumentacion_rag.py' para generar algunas trazas.")
else:
    print(f"=== LEYENDO HISTORIAL DE TRAZAS: {ruta_log} ===\n")
    
    with open(ruta_log, "r", encoding="utf-8") as f:
        for linea in f:
            if not linea.strip():
                continue
            r = json.loads(linea)
            
            # Extracción segura de tokens y datos con fallback por si hay campos nulos
            tokens_info = r.get("tokens")
            tokens_entrada = tokens_info.get("input_tokens") if tokens_info else "N/A"
            tokens_salida = tokens_info.get("output_tokens") if tokens_info else "N/A"
            
            modelo = r.get("modelo_utilizado", "desconocido")
            costo = r.get("costo_estimado_usd", 0.0)
            k = r.get("k", "N/A")
            tiempo_total = r.get("tiempo_total_ms", 0.0)
            pregunta = r.get("pregunta", "")[:35]
            
            print(
                f"k={k} | "
                f"modelo={modelo} | "
                f"in={tokens_entrada}, out={tokens_salida} | "
                f"costo=${costo} | "
                f"total={tiempo_total} ms | "
                f"pregunta: '{pregunta}'"
            )