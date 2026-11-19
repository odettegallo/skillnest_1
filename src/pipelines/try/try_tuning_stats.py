# src/pipelines/try/try_tuning_stats.py
import os
from dotenv import load_dotenv
from google import genai

NOMBRE_TRABAJO = ""  # Pega aquí el trabajo.name cuando tengas uno real


def consultar_estadisticas_tuning(nombre_trabajo: str):
    load_dotenv()

    if not nombre_trabajo or not nombre_trabajo.strip() or nombre_trabajo == "NOMBRE_DE_TU_TRABAJO":
        print("ℹ️ No hay un nombre de trabajo real configurado. Se omite la consulta a la API.")
        return None

    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️ No se encontró GEMINI_API_KEY en el entorno o en .env. Se omite la consulta.")
        return None

    client = genai.Client()

    try:
        trabajo = client.tunings.get(name=nombre_trabajo)
    except Exception as error:
        print(f"⚠️ No se pudo consultar el trabajo '{nombre_trabajo}': {error}")
        return None

    tuning_stats = getattr(trabajo, "tuning_data_stats", None)
    stats = getattr(tuning_stats, "supervised_tuning_data_stats", None)

    if stats is None:
        print("⏳ El trabajo todavía no tiene estadísticas de datos. Espera a que termine y vuelve a intentarlo.")
        return None

    print("ejemplos usados:", stats.tuning_dataset_example_count)
    print("ejemplos truncados:", stats.total_truncated_example_count)
    print("tokens facturables totales:", stats.total_billable_token_count)
    print("caracteres facturables totales:", stats.total_billable_character_count)
    print("pasos de entrenamiento:", stats.tuning_step_count)
    return stats


if __name__ == "__main__":
    consultar_estadisticas_tuning(NOMBRE_TRABAJO)