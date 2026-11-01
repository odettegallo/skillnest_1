# 📊 Reporte de Evaluación y Métricas de Modelos (Gate 1)

Este documento registra los resultados obtenidos tras ejecutar el pipeline de evaluación automatizada (`pipeline_clean_text.py`), comparando las respuestas generadas por la API de Google Gemini frente a textos de referencia mediante el cálculo de **Precisión**, **Cobertura** y **F1 Score**.

## 1. ¿Qué mide la métrica?
La métrica implementada evalúa la **coincidencia léxica exacta de tokens (palabras)** entre la respuesta generada por el modelo de lenguaje y una respuesta de referencia previamente escrita por el desarrollador. Se compone de tres indicadores clave:
- **Precisión:** Qué porcentaje de las palabras en la respuesta del modelo pertenecen realmente a la referencia.
- **Cobertura (Recall):** Qué porcentaje de las palabras clave de la referencia fueron cubiertas por el modelo.
- **F1 Score:** La media armónica entre precisión y cobertura, entregando un puntaje global de alineación de 0 a 1.

---

## 2. Modos de Falla Identificados
Durante la evaluación masiva de los 20 casos, se detectaron los siguientes patrones de fallo donde la métrica matemática discrepa de la calidad real de la respuesta:
- **Disparidad de Longitud y Explicaciones Extensas:** Los modelos tienden a redactar explicaciones más completas o párrafos introductorios. Esto diluye la precisión matemática porque introduce muchos tokens nuevos ajenos a la referencia estática.
- **Sinónimos y Variaciones Léxicas:** Conceptos respondidos correctamente por el modelo utilizando sinónimos válidos (por ejemplo, *"creado por"* en vez de *"diseñado e implementado por"*) reciben un puntaje de F1 bajo debido a la falta de coincidencia estricta de cadenas de texto.
- **Respuestas Concisas vs. Descriptivas:** En preguntas directas, si la referencia es muy breve y el modelo responde detalladamente, la cobertura sube pero la precisión cae drásticamente.

---

## 📋 Resumen de la Muestra Analizada (Extremos) 01/11/2026

A continuación se muestra la muestra combinada obtenida tras ordenar los casos evaluados por su puntaje F1 (enfocándose en los casos con menor rendimiento y los mejores desempeños):

| N° | Consulta | F1 Score | Clasificación | Corrección Factual | Completitud | Contradicción | Observación Cualitativa |
|:--:|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **1** | ¿Qué es la programación orientada a objetos? | 0.05 | Bajo | Sí | Sí | No | Concepto abordado correctamente de forma teórica, pero con vocabulario ajeno a la referencia breve. |
| **2** | ¿Qué es Docker? | 0.06 | Bajo | Sí | Sí | No | Excelente respuesta técnica sobre contenedores, penalizada por el exceso de tokens descriptivos. |
| **3** | ¿Qué es un framework? | 0.07 | Bajo | Sí | Sí | No | Explicación funcional correcta; difiere léxicamente de la definición estática de referencia. |
| **4** | ¿Qué es Linux? | 0.07 | Bajo | Sí | Sí | No | Definición acertada de sistema operativo / núcleo, pero redactada con sinónimos e introducciones. |
| **5** | ¿Qué es SQL? | 0.08 | Bajo | Sí | Sí | No | Respuesta precisa respecto al lenguaje de consulta estructurado, penalizada por disparidad de tokens. |
| ... | *[Casos intermedios evaluados en pipeline]* | ... | ... | ... | ... | ... | ... |
| **6** | ¿Qué es una lista en Python? | 0.12 | Bajo | Sí | Sí | No | Comienza a aumentar la coincidencia léxica por uso de términos específicos (corchetes, mutabilidad). |
| **7** | ¿Qué es pip en Python? | 0.14 | Bajo | Sí | Sí | No | Explicación correcta del gestor de paquetes con coincidencia parcial de palabras clave. |
| **8** | ¿JSON? | 0.17 | Bajo | Sí | Sí | No | Alta precisión cualitativa al tratar el formato de intercambio de datos, pero F1 restringido. |
| **9** | ¿Qué es Python? | 0.20 | Bajo | Sí | Sí | No | Coincidencia moderada gracias a conceptos compartidos sobre lenguajes interpretados/multiparadigma. |
| **10** | ¿Cuándo se creó Python? | 0.56 | Aceptable | Sí | Sí | No | F1 significativamente más alto debido a la concisión de la pregunta y la coincidencia directa en fechas y datos puntuales. |

---
---

## 🔍 Análisis Cualitativo de los Resultados

### 1. ¿Por qué se obtuvieron valores bajos (F1 < 0.20) en la mayoría de los casos?
El puntaje F1 mide la **coincidencia estricta de tokens (palabras)** entre la respuesta generada por el modelo y la referencia escrita. Las principales razones de la brecha en estos casos son:
- **Amplitud en las respuestas del modelo:** El modelo tiende a redactar explicaciones estructuradas, párrafos introductorios o detalles de implementación que introducen muchos tokens nuevos ajenos a la referencia estática.
- **Variación en el vocabulario (Sinónimos):** En consultas de definición teórica como *¿Qué es la programación orientada a objetos?* (`0.05`), *¿Qué es Docker?* (`0.06`), *¿Qué es un framework?* (`0.07`), *¿Qué es Linux?* (`0.07`) o *¿Qué es SQL?* (`0.08`), el modelo responde con precisión conceptual, pero la métrica disminuye drásticamente al no coincidir exactamente la redacción.

### 2. Casos con mejor desempeño (F1 0.12 - 0.56)
- **Coincidencias en vocabulario técnico (F1 0.12 - 0.20):** Consultas como *¿Qué es una lista en Python?* (`0.12`), *¿Qué es pip en Python?* (`0.14`), *¿JSON?* (`0.17`) y *¿Qué es Python?* (`0.20`) lograron mayor solapamiento de tokens gracias a términos técnicos específicos que comparten tanto el modelo como la referencia.
- **Consultas concisas y puntuales (F1 0.56):** La pregunta *¿Cuándo se creó Python?* alcanzó el puntaje más alto (clasificado como `[Aceptable]`) debido a que la respuesta requiere datos fácticos breves y fechas específicas donde la variabilidad léxica es mínima.

---

## 🛠️ Conclusiones y Próximos Pasos (Prompt Engineering y Evaluación)

1. **No confiar ciegamente en el F1 léxico:** Un puntaje F1 bajo (por ejemplo, `< 0.30`) no implica que el modelo alucine o entregue respuestas erróneas; en la mayoría de los casos analizados, la respuesta es factual y cualitativamente correcta, pero expresada con diferente redacción.
2. **Complementar con Juez LLM (LLM-as-a-Judge):** Para futuras iteraciones, se recomienda incorporar una evaluación cualitativa automatizada basada en rúbricas (*Corrección factual, Completitud y Contradicción*) utilizando un LLM como evaluador.
3. **Ajuste y Calibración de Referencias:** Las respuestas de referencia estáticas deben flexibilizarse o diseñarse imitando el tono y extensión natural de salida del modelo para evitar penalizar injustamente respuestas de alta calidad.
4. **Restricción de Longitud vía Prompt:** Se evaluará incorporar restricciones en el `system_instruction` (por ejemplo, exigir respuestas concisas de máximo 30 palabras u oraciones directas) para controlar la dispersión de tokens y alinear el comportamiento del modelo con la referencia.