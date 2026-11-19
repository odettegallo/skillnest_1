# src/core/estrategia.py

REGLAS_PUNTUACION = [
    ("informacion_cambia_seguido", {"RAG": 3}),
    ("problema_de_formato_o_tono", {"PEFT": 2, "Fine-tuning completo": 1}),
    ("dataset_grande_y_de_calidad", {"Fine-tuning completo": 2, "PEFT": 1}),
    ("presupuesto_limitado_o_iterar_rapido", {"RAG": 2, "PEFT": 1}),
    ("necesita_multiples_variantes", {"PEFT": 2}),
]


def _calcular_puntos(respuestas: dict[str, bool]) -> dict[str, int]:
    puntos = {"RAG": 0, "Fine-tuning completo": 0, "PEFT": 0}
    for clave_respuesta, incrementos in REGLAS_PUNTUACION:
        if respuestas.get(clave_respuesta, False):
            for estrategia, suma in incrementos.items():
                puntos[estrategia] += suma
    return puntos


def recomendar_estrategia_sin_empates(respuestas: dict[str, bool]) -> tuple[dict[str, int], str]:
    """Primera versión con max(..., key=puntos.get): devuelve solo la primera ganadora."""
    puntos = _calcular_puntos(respuestas)
    ganador = max(puntos, key=puntos.get)
    return puntos, ganador


def recomendar_estrategia(respuestas: dict[str, bool]) -> tuple[dict[str, int], list[str]]:
    """Versión corregida: devuelve todas las estrategias que empatan en el puntaje máximo."""
    puntos = _calcular_puntos(respuestas)
    maximo = max(puntos.values())
    ganadoras = [tecnica for tecnica, puntaje in puntos.items() if puntaje == maximo]
    return puntos, ganadoras