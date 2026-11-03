# --- CONSTANTES GLOBALES (Estandarizadas para todo tu proyecto) ---
# Lista de modelos en orden de respaldo (Fallback)
MODELOS_DISPONIBLES = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-3.8-flash"
]

# Tarifas oficiales o referenciales (Precios por millón de tokens en USD)
TARIFAS_MODELOS = {
    "gemini-3.5-flash": {"entrada": 0.075, "salida": 0.30},
    "gemini-3.5-flash-lite": {"entrada": 0.0375, "salida": 0.15},
    "gemini-2.5-flash": {"entrada": 0.075, "salida": 0.30},
    "gemini-3.8-flash": {"entrada": 0.10, "salida": 0.40},
}

# Banco de prompts estructurado para pruebas automáticas
BANCO_DE_PROMPTS = [
    {
        "nombre": "clasificar_sentimiento",
        "system_instruction": (
            "Responde únicamente con un objeto JSON con las claves 'sentimiento' "
            "('positivo', 'negativo' o 'neutro') y 'confianza' (0 a 1)."
        ),
        "ejemplo_usuario": "El servicio llegó tarde pero el producto está perfecto.",
        "claves_esperadas": ["sentimiento", "confianza"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "sentimiento": { "type": "STRING" },
                "confianza": { "type": "NUMBER" }
            },
            "required": ["sentimiento", "confianza"]
        }
    },
    {
        "nombre": "extraer_entidades_soporte",
        "system_instruction": (
            "Eres un asistente técnico. Analiza la consulta y extrae en formato JSON "
            "las claves 'departamento' y 'prioridad' ('alta', 'media', 'baja')."
        ),
        "ejemplo_usuario": "Mi aplicación se cierra sola cada vez que intento pagar la factura.",
        "claves_esperadas": ["departamento", "prioridad"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "departamento": { "type": "STRING" },
                "prioridad": { "type": "STRING" }
            },
            "required": ["departamento", "prioridad"]
        }
    }
]

# ==========================================
# CASOS DE PRUEBA PARA EVALUACIÓN (Pipeline F1)
# ==========================================
CASOS_EVALUACION = [
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
    (
        "¿Qué es una función lambda?",
        "Una función lambda es una función anónima pequeña y sin nombre definida con la palabra clave lambda."
    ),
    (
        "¿Qué es un framework?",
        "Un framework es un marco de trabajo que proporciona una estructura base para desarrollar aplicaciones de software."
    ),
    (
        "¿Qué es una API?",
        "Una API es una interfaz de programación de aplicaciones que permite la comunicación entre diferentes sistemas de software."
    ),
    (
        "¿JSON?",
        "JSON es un formato ligero de intercambio de datos basado en texto, fácil de leer y escribir para humanos y máquinas."
    ),
    (
        "¿Qué es SQL?",
        "SQL es un lenguaje de consulta estructurado diseñado para administrar y consultar bases de datos relacionales."
    ),
    (
        "¿Qué es Linux?",
        "Linux es un sistema operativo de código abierto basado en Unix, muy utilizado en servidores y desarrollo backend."
    ),
    (
        "¿Qué es la recursividad?",
        "La recursividad es una técnica de programación donde una función se llama a sí misma para resolver un problema."
    ),
    (
        "¿Qué es un bug?",
        "Es un error, fallo o defecto en un programa de software que provoca un resultado inesperado."
    )
]