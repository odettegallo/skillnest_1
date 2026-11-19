# Decision de personalizacion

## 1. El problema
El flujo de evaluación y renovación crediticia en CredIA necesita estructurar antecedentes financieros, ratios y dictámenes de forma consistente, pero hoy no cuenta con documentación formal ni dataset histórico etiquetado.

## 2. Resultado del metodo de decision
- PEFT: 3 puntos
- RAG: 2 puntos
- Fine-tuning completo: 1 puntos

## 3. Tecnica elegida y por que
Elijo RAG para esta etapa inicial (apoyado en PEFT solo cuando exista un dataset etiquetado suficiente para estabilizar formato y tono). Al no tener datos reales ni documentación base todavía, RAG permite iterar en menos de un día y con bajo costo sobre reglas/criterios simulados sin comprometer entrenamientos pesados.

## 4. Que necesitarias para ejecutarla
Parto con 0 ejemplos reales etiquetados y 0 documentos indexados; meta inicial de 30 casos simulados/etiquetados para pruebas a 5 minutos por caso, lo que equivale a 2.5 horas de trabajo y un costo estimado de 37.50 USD a 15.00 USD/h (máximo 2 intentos de prueba en esta etapa).
