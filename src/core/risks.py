# src/core/riesgos.py
from typing import Any


def puntaje_riesgo(probabilidad: int, impacto: int) -> int:
    return probabilidad * impacto


def categoria_riesgo(puntaje: int) -> str:
    if puntaje >= 15:
        return "CRITICO"
    if puntaje >= 9:
        return "ALTO"
    if puntaje >= 4:
        return "MEDIO"
    return "BAJO"


def esta_en_el_limite(probabilidad: int, impacto: int) -> bool:
    categoria_actual = categoria_riesgo(puntaje_riesgo(probabilidad, impacto))
    vecinos = [
        (probabilidad + 1, impacto),
        (probabilidad - 1, impacto),
        (probabilidad, impacto + 1),
        (probabilidad, impacto - 1),
    ]
    for p2, i2 in vecinos:
        if not (1 <= p2 <= 5 and 1 <= i2 <= 5):
            continue
        if categoria_riesgo(puntaje_riesgo(p2, i2)) != categoria_actual:
            return True
    return False


def evaluar_matriz_riesgos(riesgos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evaluados: list[dict[str, Any]] = []
    for fila in riesgos:
        item = dict(fila)
        puntaje = puntaje_riesgo(item["probabilidad"], item["impacto"])
        item["puntaje"] = puntaje
        item["categoria"] = categoria_riesgo(puntaje)
        item["al_limite"] = esta_en_el_limite(item["probabilidad"], item["impacto"])
        evaluados.append(item)
    return evaluados