import re
import json
import client
from collections import Counter
from client import consultar_modelo 

# ==========================================
# 1. FUNCIONES DEL PIPELINE DE TEXTO
# ==========================================
def limpiar_texto(texto: str) -> str:
    """Normaliza el texto: minúsculas y sin puntuación."""
    if not isinstance(texto, str):
        tipo = type(texto).__name__
        raise TypeError(f"limpiar_texto espera str, no {tipo}")

    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def tokenizar(texto_limpio: str) -> list[str]:
    """Convierte texto limpio en una lista de tokens."""
    return texto_limpio.split()


def vectorizar(tokens: list[str]) -> Counter:
    """Cuenta cuántas veces aparece cada token."""
    return Counter(tokens)


def procesar_texto(texto: str) -> list[str]:
    """Pipeline completo: limpia el texto y lo tokeniza en una sola llamada."""
    texto_limpio = limpiar_texto(texto)
    return tokenizar(texto_limpio)


def contar_coincidencias(tokens_referencia: list[str], tokens_respuesta: list[str]) -> int:
    """Cuenta cuántos tokens coinciden entre la referencia y la respuesta."""
    vec_ref = vectorizar(tokens_referencia)
    vec_resp = vectorizar(tokens_respuesta)
    interseccion = vec_ref & vec_resp
    return sum(interseccion.values())


def calcular_precision_cobertura_f1(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> dict[str, float]:
    """Calcula precisión, cobertura y F1 de dos listas de tokens."""
    coincidencias = contar_coincidencias(tokens_referencia, tokens_respuesta)

    if not tokens_respuesta or not tokens_referencia:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    precision = coincidencias / len(tokens_respuesta)
    cobertura = coincidencias / len(tokens_referencia)

    if precision + cobertura == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * cobertura / (precision + cobertura)

    return {
        "precision": precision,
        "cobertura": cobertura,
        "f1": f1,
    }


def calcular_metricas(texto_referencia: str, texto_respuesta: str) -> dict[str, float]:
    """Procesa ambos textos y calcula sus métricas directamente."""
    tokens_referencia = procesar_texto(texto_referencia)
    tokens_respuesta = procesar_texto(texto_respuesta)
    return calcular_precision_cobertura_f1(tokens_referencia, tokens_respuesta)


def obtener_estado_f1(f1: float) -> str:
    """Retorna un indicador visual y estado según la puntuación F1."""
    if f1 >= 0.70:
        return "🟢 [Excelente]"
    elif f1 >= 0.40:
        return "🟡 [Aceptable]"
    else:
        return "🔴 [Bajo]"


# ==========================================
# 2. FUNCIÓN ORQUESTADORA (EJECUCIÓN)
# ==========================================
def ejecutar_pruebas():
    print("🚀 Iniciando evaluación masiva de métricas con el modelo (12 casos)...\n")

    # Banco ampliado de 12 casos de prueba sobre Python y tecnología
    casos = [
        (
            "¿Qué es Python?",
            "Python es un lenguaje de programación de alto nivel, interpretado, de código abierto y multiparadigma. "
            "Es reconocido por su sintaxis clara y legible, ideal para desarrollo web, análisis de datos, "
            "inteligencia artificial y automatización de procesos."
        ),
        (
            "¿Cuándo se creó Python?",
            "Python fue creado a finales de los años 80 por Guido van Rossum en los Países Bajos, "
            "y su primera versión oficial (0.9.0) fue publicada en febrero de 1991."
        ),
        (
            "¿Qué es una lista en Python?",
            "En Python, una lista es una estructura de datos integrada que permite almacenar "
            "una colección ordenada y mutable de elementos entre corchetes."
        ),
        (
            "¿Qué es un diccionario en Python?",
            "Un diccionario es una estructura de datos mutable que almacena pares de clave y valor, "
            "permitiendo búsquedas rápidas mediante claves únicas."
        ),
        (
            "¿Qué es una tupla en Python?",
            "Una tupla es una estructura de datos similar a una lista pero inmutable, es decir, "
            "sus elementos no pueden ser modificados una vez creada la tupla."
        ),
        (
            "¿Para qué sirve la función print en Python?",
            "La función print se utiliza para mostrar mensajes o valores de variables en la consola "
            "o salida estándar."
        ),
        (
            "¿Qué es pip en Python?",
            "Pip es el sistema de gestión de paquetes estándar para Python, utilizado para instalar "
            "y administrar bibliotecas de terceros que no vienen en la biblioteca estándar."
        ),
        (
            "¿Qué es un entorno virtual en Python?",
            "Un entorno virtual es un directorio aislado que contiene una instalación de Python "
            "y las dependencias específicas de un proyecto, evitando conflictos entre versiones."
        ),
        (
            "¿Qué es el tipado dinámico en Python?",
            "El tipado dinámico significa que el tipo de una variable se determina en tiempo de ejecución "
            "y no es necesario declararlo explícitamente al escribir el código."
        ),
        (
            "¿Qué es la programación orientada a objetos?",
        "Es un paradigma de programación basado en el concepto de clases y objetos, que agrupan "
            "datos y comportamientos relacionados."
        ),
        (
            "¿Qué es Git?",
            "Git es un sistema de control de versiones distribuido diseñado para rastrear cambios "
            "en el código fuente durante el desarrollo de software."
        ),
        (
            "¿Qué es Docker?",
            "Docker es una plataforma de código abierto que permite empaquetar aplicaciones y sus dependencias "
            "en contenedores ligeros y portables."
        ),
    ]

    resultados = []

    for consulta, referencia in casos:
        print(f"🔍 Consultando: '{consulta}'")
        respuesta = consultar_modelo(consulta)
        
        metricas = calcular_metricas(referencia, respuesta)
        
        resultados.append({
            "consulta": consulta,
            "respuesta": respuesta,
            "referencia": referencia,
            **metricas
        })
        print(f"   ✨ F1 obtenido: {metricas['f1']:.2f}\n")

    # Guardamos los resultados completos en el archivo JSON
    ruta_salida = "prompts/resultados_metricas.json"
    with open(ruta_salida, "w", encoding="utf-8") as archivo:
        json.dump(resultados, archivo, indent=2, ensure_ascii=False)

    print(f"📁 Resultados y métricas guardados exitosamente en '{ruta_salida}'.\n")

    # --- Análisis de la muestra solicitada por el curso (5 peores y 5 mejores) ---
    print("📊 Muestra para revisión a mano (5 peores y 5 mejores F1):")
    peores_casos = sorted(resultados, key=lambda r: r["f1"])
    
    # Combinamos los 5 peores con los 5 mejores (tal como indica la lección)
    muestra_para_revisar = peores_casos[:5] + peores_casos[-5:]

    for caso in muestra_para_revisar:
        estado = obtener_estado_f1(caso["f1"])
        print(f"   {estado} F1: {caso['f1']:.2f} | Consulta: '{caso['consulta']}'")


# ==========================================
# 3. BLOQUE PRINCIPAL
# ==========================================
if __name__ == "__main__":
    ejecutar_pruebas()