# src/pipelines/try/try_decision.py
import argparse
from pathlib import Path
from core.dataset_utils import estimar_costo_de_etiquetar
from core.strategy import recomendar_estrategia

RUTA_DECISION_MD = Path("docs") / "decision_personalizacion.md"


def construir_documento_decision(
    problema: str,
    puntos: dict[str, int],
    ganadoras: list[str],
    justificacion: str,
    requisitos: str,
) -> str:
    empate = len(ganadoras) > 1
    lineas = [
        "# Decision de personalizacion",
        "",
        "## 1. El problema",
        problema.strip(),
        "",
        "## 2. Resultado del metodo de decision",
    ]
    for tecnica, puntaje in sorted(puntos.items(), key=lambda item: -item[1]):
        lineas.append(f"- {tecnica}: {puntaje} puntos")

    if empate:
        lineas.extend([
            "",
            f"**Empate entre: {', '.join(ganadoras)}**",
        ])

    lineas.extend([
        "",
        "## 3. Tecnica elegida y por que",
        justificacion.strip(),
        "",
        "## 4. Que necesitarias para ejecutarla",
        requisitos.strip(),
    ])
    return "\n".join(lineas) + "\n"


def guardar_si_corresponde(contenido: str, destino: Path, sobrescribir: bool) -> bool:
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and not sobrescribir:
        return False
    destino.write_text(contenido, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Ejecuta método de decisión y genera el .md en docs/")
    parser.add_argument(
        "--sobrescribir",
        action="store_true",
        help="Sobrescribe docs/decision_personalizacion.md si ya existe.",
    )
    args = parser.parse_args()

    respuestas_mi_caso = {
        "informacion_cambia_seguido": False,          # 0 fuentes reales del proyecto cambiaron en los últimos 3 meses (base en maqueta/simulación)
        "problema_de_formato_o_tono": True,           # Sin dataset calibrado aún: se requiere validar formato/estructura en >=3 de 20 casos de prueba
        "dataset_grande_y_de_calidad": False,         # 0 ejemplos reales etiquetados hoy (<200 requeridos y sin muestra de 20 auditada)
        "presupuesto_limitado_o_iterar_rapido": True, # Iteración rápida en <1 día y máximo 1-2 intentos de prueba en esta etapa
        "necesita_multiples_variantes": False,        # 1 flujo principal de evaluación crediticia en el MVP inicial
    }

    if any(valor is None for valor in respuestas_mi_caso.values()):
        raise SystemExit("Completa las cinco respuestas con True o False antes de continuar.")

    print("=" * 58)
    print("PASO 1: el metodo corre sobre mi caso")
    print("=" * 58)
    puntos, ganadoras = recomendar_estrategia(respuestas_mi_caso)
    print(puntos)
    print("candidatas:" if len(ganadoras) > 1 else "ganadora:", ganadoras)
    print()

    # Estimación cuantitativa usando estimar_costo_de_etiquetar de core.dataset_utils
    ejemplos_piloto = 30
    minutos_por_ejemplo = 5.0
    costo_por_hora = 15.0  # USD/hora de referencia
    moneda = "USD"
    horas_piloto, costo_piloto = estimar_costo_de_etiquetar(
        ejemplos_piloto, minutos_por_ejemplo, costo_por_hora
    )

    problema_texto = (
        "El flujo de evaluación y renovación crediticia en CredIA necesita estructurar "
        "antecedentes financieros, ratios y dictámenes de forma consistente, pero hoy "
        "no cuenta con documentación formal ni dataset histórico etiquetado."
    )

    justificacion_texto = (
        "Elijo RAG para esta etapa inicial (apoyado en PEFT solo cuando exista un dataset "
        "etiquetado suficiente para estabilizar formato y tono). Al no tener datos reales "
        "ni documentación base todavía, RAG permite iterar en menos de un día y con bajo "
        "costo sobre reglas/criterios simulados sin comprometer entrenamientos pesados."
    )

    requisitos_texto = (
        f"Parto con 0 ejemplos reales etiquetados y 0 documentos indexados; meta inicial de "
        f"{ejemplos_piloto} casos simulados/etiquetados para pruebas a {minutos_por_ejemplo:.0f} "
        f"minutos por caso, lo que equivale a {horas_piloto:.1f} horas de trabajo y un costo "
        f"estimado de {costo_piloto:.2f} {moneda} a {costo_por_hora:.2f} {moneda}/h "
        f"(máximo 2 intentos de prueba en esta etapa)."
    )

    documento = construir_documento_decision(
        problema=problema_texto,
        puntos=puntos,
        ganadoras=ganadoras,
        justificacion=justificacion_texto,
        requisitos=requisitos_texto,
    )

    guardado = guardar_si_corresponde(documento, RUTA_DECISION_MD, sobrescribir=args.sobrescribir)

    print("=" * 58)
    print(f"PASO 2: $ cat {RUTA_DECISION_MD.as_posix()} (ya completado)")
    print("=" * 58)
    print(documento.rstrip())

    if not guardado:
        print(
            f"\n[Aviso] {RUTA_DECISION_MD} ya existía y no se sobrescribió. "
            "Usa --sobrescribir si quieres regenerarlo desde este script."
        )


if __name__ == "__main__":
    main()