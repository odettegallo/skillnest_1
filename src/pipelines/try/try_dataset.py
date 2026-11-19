# src/pipelines/try/try_dataset.py
from dotenv import load_dotenv
from google import genai
from google.genai import types
import json

# Importamos los datos y las funciones reutilizables
from core.dataset import DATASET_ERRORES_RAW
from core.dataset_utils import (
    explicar_error,
    validar_dataset,
    chequear_balance,
    esperar_a_que_termine,
)

# ==============================================================================
# 1. INSPECCIÓN PREVIA DE TIPOS Y CONFIGURACIONES DISPONIBLES EN EL SDK
# ==============================================================================
print("=== 1. INSPECCIÓN DE TIPOS DEL SDK ===")
try:
    print("Modos de tuning disponibles:")
    for modo in types.TuningMode:
        print(" ", modo)

    print("\nTamaños de adapter disponibles (solo aplica a PEFT):")
    for tamano in types.AdapterSize:
        print(" ", tamano)
except AttributeError as e:
    raise SystemExit(f"Tu versión del SDK no expone este tipo: {e}. Actualiza con: pip install -U google-genai")

print("\n--- Campos de control de tiempo y costos ---")
for campo in ["epoch_count", "learning_rate_multiplier", "batch_size"]:
    try:
        descripcion = types.CreateTuningJobConfig.model_fields[campo].description
        print(campo, "->", descripcion)
    except KeyError:
        print(campo, "-> este campo no existe en tu versión del SDK")
print()


# ==============================================================================
# 2. PRUEBA DEL MANEJADOR DE ERRORES (Usando la función de core)
# ==============================================================================
print("=== 2. PRUEBA DEL MANEJADOR DE ERRORES ===")
ejemplos_errores = [
    Exception("400 INVALID_ARGUMENT. API key not valid. Please pass a valid API key."),
    Exception("429 RESOURCE_EXHAUSTED. Quota exceeded for this project."),
    Exception("Connection reset by peer"),
]
for ejemplo in ejemplos_errores:
    print(explicar_error(ejemplo))
print()


# ==============================================================================
# 3. CONSTRUCCIÓN DEL DATASET EN EL FORMATO REAL DE TUNING
# ==============================================================================
ejemplos_raw = DATASET_ERRORES_RAW

examples = [
    types.TuningExample(text_input=texto, output=json.dumps(salida, ensure_ascii=False))
    for texto, salida in ejemplos_raw
]

print("=== 3. CONSTRUCCIÓN DEL DATASET ===")
print(len(examples), "ejemplos construidos")
print(examples[0])
print()


# ==============================================================================
# 4. VALIDACIÓN LOCAL DEL DATASET (Usando la función de core)
# ==============================================================================
print("=== 4. VALIDACIÓN DEL DATASET ===")
problemas = validar_dataset(examples, claves_esperadas=("categoria", "accion_sugerida"))
print(f"{len(examples)} ejemplos, {len(problemas)} problemas encontrados")
for p in problemas:
    print(" -", p)
print()


# ==============================================================================
# 5. PRUEBA DEL VALIDADOR CONTRA UN DATASET ROTO A PROPÓSITO
# ==============================================================================
print("=== 5. PRUEBA CON DATASET ROTO ===")
examples_rotos = examples + [
    types.TuningExample(text_input="", output='{"categoria": "red"}'),
    types.TuningExample(text_input=ejemplos_raw[0][0], output="no es json"),
]
problemas2 = validar_dataset(examples_rotos, claves_esperadas=("categoria", "accion_sugerida"))
print(f"{len(examples_rotos)} ejemplos, {len(problemas2)} problemas encontrados")
for p in problemas2:
    print(" -", p)
print()


# ==============================================================================
# 6. CHEQUEO DE BALANCE ENTRE CATEGORÍAS (Usando la función de core)
# ==============================================================================
print("=== 6. BALANCE DEL DATASET ===")
balance = chequear_balance(ejemplos_raw, clave="categoria")
for categoria, cuenta in balance.most_common():
    print(f"{categoria}: {cuenta}")

maximo = max(balance.values())
minimo = min(balance.values())
print()
print(f"categoria mas representada: {maximo} ejemplos")
print(f"categoria menos representada: {minimo} ejemplos")
print(f"razon max/min: {maximo / minimo:.1f}x")
print()


# ==============================================================================
# 7. ESTADOS DEL SDK Y ESPERA ASÍNCRONA DE TUNING
# ==============================================================================
print("=== 7. ESTADOS POSIBLES DE TUNING EN EL SDK ===")
print("Estados posibles de un trabajo de tuning:")
for estado in types.JobState:
    print(" ", estado)
print()


# ==============================================================================
# 8. ARMADO DEL TRABAJO DE TUNING (BLOQUE DEMOSTRATIVO SEGURO)
# ==============================================================================
def lanzar_tuning_demostrativo(examples):
    """Construye los objetos reales del SDK y muestra la configuración armada sin envío real."""
    load_dotenv()
    
    dataset = types.TuningDataset(examples=examples)

    config = types.CreateTuningJobConfig(
        tuning_mode=types.TuningMode.TUNING_MODE_PEFT_ADAPTER,
        adapter_size=types.AdapterSize.ADAPTER_SIZE_FOUR,
        epoch_count=5,
        tuned_model_display_name="clasificador-errores-cliente",
    )

    print("=== 8. CONFIGURACIÓN ARMADA ===")
    print(f"tuning_mode: {config.tuning_mode}")
    print(f"adapter_size: {config.adapter_size}")
    print(f"epoch_count: {config.epoch_count}")
    print("(configuración armada; no se envió ningún trabajo)")

# Ejemplo de referencia (500 ejemplos base + 20% de revisión)
horas_base, costo_base = estimar_costo_de_etiquetar(500, 4, 20)
horas_rev, costo_rev = estimar_costo_de_etiquetar(500 * 0.20, 2, 20)

total_horas = horas_base + horas_rev
total_costo = costo_base + costo_rev
jornadas = total_horas / 8

print(f"etiquetado base: {horas_base:.2f} horas, aprox ${costo_base:.2f}")
print(f"segunda revision: {horas_rev:.2f} horas, aprox ${costo_rev:.2f}")
print(f"total: {total_horas:.2f} horas, aprox ${total_costo:.2f}")
print(f"jornadas de 8 horas: {jornadas:.1f}")


if __name__ == "__main__":
    lanzar_tuning_demostrativo(examples)