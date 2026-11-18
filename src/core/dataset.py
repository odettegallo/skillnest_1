# ==========================================
# DATASET DE EJEMPLO PARA FINE-TUNING (Clasificador de errores)
# ==========================================
DATASET_ERRORES_RAW = [
    ("TimeoutError: la conexion tardo mas de 10 segundos en responder.",
     {"categoria": "red", "accion_sugerida": "reintentar con backoff exponencial"}),
    ("ValueError: la clave de API no tiene el formato esperado.",
     {"categoria": "autenticacion", "accion_sugerida": "revisar GEMINI_API_KEY, no reintentar"}),
    ("429 RESOURCE_EXHAUSTED: se supero el limite de peticiones por minuto.",
     {"categoria": "cuota", "accion_sugerida": "esperar y reintentar, con backoff"}),
    ("API key not valid. Please pass a valid API key.",
     {"categoria": "autenticacion", "accion_sugerida": "revisar GEMINI_API_KEY, no reintentar"}),
    ("RuntimeError: Your system has an unsupported version of sqlite3.",
     {"categoria": "entorno", "accion_sugerida": "instalar pysqlite3-binary"}),
    ("ModuleNotFoundError: No module named langchain_chroma.",
     {"categoria": "entorno", "accion_sugerida": "instalar dependencia faltante"}),
    ("PermissionError al crear la carpeta del vector store.",
     {"categoria": "entorno", "accion_sugerida": "revisar permisos de escritura"}),
    ("InvalidArgumentError: Collection expecting embedding with dimension of 768, got 1536.",
     {"categoria": "consistencia_indice", "accion_sugerida": "reindexar con el mismo modelo de embeddings"}),
]

DATASET_EJEMPLOS_RAW = [
    (
        "No puedo iniciar sesión desde ayer: dice que mi contraseña es incorrecta aunque ya la cambié dos veces.",
        {"intencion": "acceso", "prioridad": "alta"}
    ),
    (
        "Me cobraron dos veces la suscripción de este mes, necesito el reembolso de uno de los cargos.",
        {"intencion": "facturacion", "prioridad": "alta"}
    ),
    (
        "Quisiera saber si el plan Pro incluye más de un usuario, no es urgente.",
        {"intencion": "consulta_plan", "prioridad": "baja"}
    ),
    (
        "La aplicación se cierra sola cada vez que intento subir una foto de perfil.",
        {"intencion": "falla_tecnica", "prioridad": "media"}
    ),
    (
        "Quiero dar de baja mi cuenta al terminar el mes, gracias por el servicio.",
        {"intencion": "cancelacion", "prioridad": "media"}
    ),
    (
        "No me llega el correo electrónico para restablecer la contraseña de acceso.",
        {"intencion": "acceso", "prioridad": "media"}
    ),
    (
        "Hay un cargo extraño en mi tarjeta que no reconozco y quiero que lo revisen hoy.",
        {"intencion": "facturacion", "prioridad": "alta"}
    ),
    (
        "¿Cuáles son los métodos de pago aceptados para la renovación anual?",
        {"intencion": "consulta_plan", "prioridad": "baja"}
    ),
    (
        "El botón de exportar a PDF se queda cargando infinitamente y no descarga nada.",
        {"intencion": "falla_tecnica", "prioridad": "alta"}
    ),
    (
        "¿Cómo puedo actualizar los datos de facturación de mi empresa?",
        {"intencion": "facturacion", "prioridad": "baja"}
    ),
]