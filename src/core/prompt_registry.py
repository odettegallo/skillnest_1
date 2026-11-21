# src/core/prompt_registry.py
from datetime import date
import difflib
import hashlib


def huella_prompt(texto: str) -> str:
    """Genera una huella corta SHA-256 del texto exacto del prompt."""
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:12]


class RegistroDePrompts:
    """Registra versiones inmutables de prompts con trazabilidad."""

    def __init__(self) -> None:
        self.versiones: list[dict] = []

    def registrar(
        self,
        nombre: str,
        texto: str,
        autor: str,
        nota: str,
        modelo: str | None = None,
        parametros: dict | None = None,
    ) -> dict:
        version = {
            "nombre": nombre,
            "huella": huella_prompt(texto),
            "texto": texto,
            "autor": autor,
            "fecha": str(date.today()),
            "nota": nota,
            "modelo": modelo,
            "parametros": parametros or {},
        }
        self.versiones.append(version)
        return version

    def historial(self, nombre: str) -> list[dict]:
        return [v for v in self.versiones if v["nombre"] == nombre]

    def ultima(self, nombre: str) -> dict | None:
        candidatas = self.historial(nombre)
        return candidatas[-1] if candidatas else None


def diff_prompts(anterior: str, nueva: str) -> list[str]:
    """Calcula el diff unificado palabra a palabra entre dos versiones de prompt."""
    palabras_anteriores = anterior.split()
    palabras_nuevas = nueva.split()
    return list(
        difflib.unified_diff(
            palabras_anteriores,
            palabras_nuevas,
            fromfile="version_anterior",
            tofile="version_nueva",
            lineterm="",
        )
    )