# src/pipelines/try/dataset_tuning.py
import json
from dotenv import load_dotenv
from google.genai import types

# Importamos los datos propios desde core/dataset.py
from core.dataset import DATASET_EJEMPLOS_RAW
# Importamos las funciones reutilizables desde core/dataset_utils.py
from core.dataset_utils import validar_dataset, chequear_balance

# 1. Construcción del dataset en el formato requerido por la API
ejemplos_raw = DATASET_EJEMPLOS_RAW

examples = [
    types.TuningExample(text_input=texto, output=json.dumps(salida, ensure_ascii=False))
    for texto, salida in ejemplos_raw
]

print(f"=== 1. CONSTRUCCIÓN DEL DATASET ===")
print(f"{len(examples)} ejemplos construidos")
print(f"Muestra [0]: {examples[0]}\n")

# 2. Revisión del balance entre categorías/intenciones
print("=== 2. BALANCE DEL DATASET ===")
balance = chequear_balance(ejemplos_raw, clave="intencion")
for categoria, cuenta in balance.most_common():
    print(f"{categoria}: {cuenta}")
print()

# 3. Validación local antes de enviar
print("=== 3. VALIDACIÓN DEL DATASET ===")
problemas = validar_dataset(examples, claves_esperadas=("intencion", "prioridad"))
print(f"{len(examples)} ejemplos, {len(problemas)} problemas encontrados")
for p in problemas:
    print(" -", p)
print()

# 4. Comprobar que el validador detecta errores a propósito
print("=== 4. PRUEBA CON DATASET ROTO ===")
examples_rotos = examples + [
    types.TuningExample(text_input="", output='{"intencion": "acceso"}'),
    types.TuningExample(text_input=ejemplos_raw[0][0], output="no es json"),
]
problemas_rotos = validar_dataset(examples_rotos, claves_esperadas=("intencion", "prioridad"))
print(f"{len(examples_rotos)} ejemplos, {len(problemas_rotos)} problemas encontrados en dataset roto:")
for p in problemas_rotos:
    print(" -", p)
print()