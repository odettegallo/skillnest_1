import json
import os

def cargar_metricas(ruta_json="prompts/resultados_metricas.json"):
    """Carga los resultados generados por pipeline_clean_text.py"""
    if not os.path.exists(ruta_json):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_json}")
    
    with open(ruta_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def seleccionar_casos_extremos(datos):
    """Ordena los datos por F1 Score y extrae los 5 peores y 5 mejores."""
    datos_ordenados = sorted(datos, key=lambda x: x.get("f1", 0))
    
    peores = datos_ordenados[:5]
    mejores = datos_ordenados[-5:]
    
    return peores, mejores

def generar_tabla_markdown(peores, mejores):
    """Construye la tabla en sintaxis Markdown."""
    lineas = [
        "## 3. Muestra Revisada a Mano (10 Casos Extremos: 5 Peores y 5 Mejores F1)",
        "",
        "| N° | Consulta | F1 Score | Clasificación | Corrección Factual | Completitud | Contradicción | Observación Cualitativa |",
        "|:--:|:---|:---:|:---:|:---:|:---:|:---:|:---|"
    ]
    
    index = 1
    
    # Procesar los 5 peores
    for item in peores:
        consulta = item.get("consulta", "")
        f1 = f"{item.get('f1', 0):.2f}"
        clasif = item.get("clasificacion", "Bajo")
        # Campos vacíos o con valores por defecto para completar en la revisión manual
        lineas.append(f"| **{index}** | {consulta} | {f1} | {clasif} | Sí | Sí | No | [Pendiente revisión manual] |")
        index += 1
        
    # Separador visual en la tabla
    lineas.append("| ... | *[Casos intermedios evaluados]* | ... | ... | ... | ... | ... | ... |")
    
    # Procesar los 5 mejores
    for item in mejores:
        consulta = item.get("consulta", "")
        f1 = f"{item.get('f1', 0):.2f}"
        clasif = item.get("clasificacion", "Aceptable" if item.get('f1', 0) >= 0.5 else "Bajo")
        lineas.append(f"| **{index}** | {consulta} | {f1} | {clasif} | Sí | Sí | No | [Pendiente revisión manual] |")
        index += 1

    return "\n".join(lineas)

def guardar_markdown(contenido, ruta_salida="docs/REVISION_MANUAL.md"):
    """Escribe la tabla en un archivo .md"""
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(contenido)
    print(f"✅ Archivo Markdown generado exitosamente en: {ruta_salida}")

if __name__ == "__main__":
    try:
        metricas = cargar_metricas("prompts/resultados_metricas.json")
        peores, mejores = seleccionar_casos_extremos(metricas)
        tabla_md = generar_tabla_markdown(peores, mejores)
        guardar_markdown(tabla_md, "docs/REVISION_MANUAL.md")
    except Exception as e:
        print(f"❌ Error al generar el reporte: {e}")