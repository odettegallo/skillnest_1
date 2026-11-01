# 📊 Reporte de Evaluación y Métricas de Modelos (Gate 1)

Este documento registra los resultados obtenidos tras ejecutar el pipeline de evaluación automatizada (`pipeline_clean_text.py`), comparando las respuestas generadas por la API de Google Gemini frente a textos de referencia mediante el cálculo de **Precisión**, **Cobertura** y **F1 Score**.

---

## 📋 Resumen de la Muestra Analizada (Extremos)

A continuación se muestra la muestra combinada obtenida tras ordenar los casos evaluados por su puntaje F1 (enfocándose en los casos con menor rendimiento y los mejores desempeños):

| Estado Visual | F1 Score | Consulta Evaluada |
| :--- | :---: | :--- |
| 🔴 **[Bajo]** | `0.07` | ¿Qué es Docker? |
| 🔴 **[Bajo]** | `0.08` | ¿Qué es la programación orientada a objetos? |
| 🔴 **[Bajo]** | `0.11` | ¿Qué es el tipado dinámico en Python? |
| 🔴 **[Bajo]** | `0.11` | ¿Qué es un entorno virtual en Python? |
| 🔴 **[Bajo]** | `0.11` | ¿Qué es Git? |
| 🔴 **[Bajo]** | `0.26` | ¿Qué es pip en Python? |
| 🔴 **[Bajo]** | `0.28` | ¿Cuándo se creó Python? |
| 🔴 **[Bajo]** | `0.30` | ¿Qué es una tupla en Python? |
| 🟡 **[Aceptable]** | `0.41` | ¿Qué es Python? |
| 🟡 **[Aceptable]** | `0.55` | ¿Qué es una lista en Python? |

---

## 🔍 Análisis Cualitativo de los Resultados

### 1. ¿Por qué se obtuvieron valores bajos (F1 < 0.40) en la mayoría de los casos?
El puntaje F1 mide la **coincidencia estricta de tokens (palabras)** entre la respuesta generada por el modelo y la referencia escrita. Las principales razones de la brecha en estos casos son:
* **Amplitud en las respuestas del modelo:** El modelo tiende a redactar explicaciones estructuradas, párrafos introductorios o conclusiones largas que introducen muchos tokens nuevos que no estaban en la referencia original.
* **Variación en el vocabulario (Sinónimos):** Si la referencia define un concepto usando términos técnicos específicos y el modelo explica el mismo concepto utilizando sinónimos o una redacción distinta, la intersección de tokens disminuye drásticamente aunque conceptualmente la respuesta sea correcta.

### 2. Casos con mejor desempeño (F1 0.41 - 0.55)
* Consultas generales como **¿Qué es Python?** o **¿Qué es una lista en Python?** lograron puntajes más altos (`0.41` y `0.55`) porque el volumen de vocabulario compartido entre la respuesta del modelo y la referencia fue significativamente mayor.

---

## 🛠️ Conclusiones y Próximos Pasos (Prompt Engineering)

1. **Ajuste de Referencias:** Las referencias actuales son muy detalladas y estrictas; para alinear mejor las métricas automáticas, conviene ajustar los textos de referencia para que imiten el estilo y extensión natural de salida de un LLM.
2. **Restricción de Longitud vía Prompt:** Se evaluará incorporar restricciones en el `system_instruction` (por ejemplo, exigir respuestas de una sola oración o máximo 30 palabras) para controlar la dispersión de tokens y elevar el puntaje de Precisión y F1.