# --- CONSTANTES GLOBALES (Estandarizadas para todo tu proyecto) ---
# Lista de modelos en orden de respaldo (Fallback)
MODELOS_DISPONIBLES = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-3.8-flash"
]

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