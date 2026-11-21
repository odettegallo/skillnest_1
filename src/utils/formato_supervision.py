# src/utils/formato_supervision.py
from typing import Any


def imprimir_banner(titulo: str, ancho: int = 60) -> None:
    print("\n" + "=" * ancho)
    print(f"  {titulo}")
    print("=" * ancho)


def imprimir_diff(diff_lineas: list[str], max_lineas: int = 20) -> None:
    if not diff_lineas:
        print("  Diff: sin cambios detectados.")
        return
    print("  Diff de palabras:")
    for linea in diff_lineas[:max_lineas]:
        print(f"    {linea}")
    if len(diff_lineas) > max_lineas:
        print(f"    ... ({len(diff_lineas) - max_lineas} líneas adicionales)")


def imprimir_estado_legible(
    titulo: str,
    estado: dict[str, Any],
    siguiente_nodo: tuple = (),
) -> None:
    imprimir_banner(titulo)
    print(f"  Prompt          : {estado.get('nombre_prompt', '-')}")
    print(f"  Huella nueva    : {estado.get('huella_nueva', '-')}")
    print(f"  Aprobado        : {estado.get('aprobado', False)}")
    print(f"  Desplegado      : {estado.get('desplegado', False)}")
    alertas = estado.get("alertas_seguridad") or []
    print(f"  Alertas (regex) : {len(alertas)} -> {alertas if alertas else 'ninguna'}")
    if siguiente_nodo:
        print(f"  Nodo pendiente  : {siguiente_nodo}")
    imprimir_diff(estado.get("diff_lineas") or [])
    print("-" * 60)