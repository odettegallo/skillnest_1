# src/pipelines/try/try_estrategia.py
from core.estrategy import recomendar_estrategia, recomendar_estrategia_sin_empates

respuestas_caso1 = {
    "informacion_cambia_seguido": True,
    "problema_de_formato_o_tono": True,
    "dataset_grande_y_de_calidad": False,
    "presupuesto_limitado_o_iterar_rapido": True,
    "necesita_multiples_variantes": False,
}

respuestas_caso2 = {
    "informacion_cambia_seguido": False,
    "problema_de_formato_o_tono": True,
    "dataset_grande_y_de_calidad": True,
    "presupuesto_limitado_o_iterar_rapido": False,
    "necesita_multiples_variantes": False,
}


def mostrar_resultado(etiqueta: str, puntos: dict[str, int], ganadoras: list[str]) -> None:
    print(f"{etiqueta}: {puntos}")
    if len(ganadoras) == 1:
        print(f"ganadora: {ganadoras[0]}")
    else:
        print(f"candidatas empatadas: {ganadoras}")


def analisis_sensibilidad(caso_base: dict[str, bool], ganadoras_base: list[str]) -> None:
    for clave, valor_actual in caso_base.items():
        caso_modificado = dict(caso_base)
        nuevo_valor = not valor_actual
        caso_modificado[clave] = nuevo_valor

        _, nuevas_ganadoras = recomendar_estrategia(caso_modificado)
        estado = "[CAMBIA]" if nuevas_ganadoras != ganadoras_base else "[IGUAL]"
        print(f"{clave} -> {nuevo_valor}: {nuevas_ganadoras} {estado}")


if __name__ == "__main__":
    print("=" * 55)
    print("PASO 1: la primera version esconde el empate")
    print("=" * 55)
    puntos2_bug, ganador2_bug = recomendar_estrategia_sin_empates(respuestas_caso2)
    print(f"caso 2: {puntos2_bug} -> recomendacion: {ganador2_bug}\n")

    print("=" * 55)
    print("PASO 2: la version corregida lo reporta")
    print("=" * 55)
    puntos2, ganadoras2 = recomendar_estrategia(respuestas_caso2)
    mostrar_resultado("caso 2", puntos2, ganadoras2)
    print()

    print("=" * 55)
    print("PASO 3: analisis de sensibilidad del empate")
    print("=" * 55)
    analisis_sensibilidad(respuestas_caso2, ganadoras2)
    print()

    print("=" * 55)
    print("PASO 4: un caso sin empate")
    print("=" * 55)
    puntos1, ganadoras1 = recomendar_estrategia(respuestas_caso1)
    mostrar_resultado("caso 1", puntos1, ganadoras1)