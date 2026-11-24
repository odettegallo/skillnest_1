
# Especialización en Desarrollo con IA Generativa (Accenture)

Aplicación en Python y LangChain que se conecta a la API de Google Gemini implementando arquitecturas resilientes con múltiples modelos (Fallback), enrutamiento dinámico de mensajes mediante `RunnableBranch`, pipelines de **Retrieval-Augmented Generation (RAG)** con ChromaDB, agentes autónomos con supervisión, telemetría de latencia/costes y una suite completa de pruebas unitarias automatizadas con `pytest`.

---

## 📂 Estructura del Proyecto
```text
plantilla-repositorio-base/
│
├── checkpoints/                        # Persistencia de estados y checkpoints (SQLite / LangGraph)
│
├── docs/                               # Documentación técnica y evidencias
│   ├── decision_personalizacion.md
│   ├── diagrama_arquitectura_API.png
│   ├── eleccion_arquitectura.md
│   ├── evidencia_peticion.png
│   ├── limites_autonomía_agent.md
│   ├── limites_metrica.md
│   ├── REVISION_MANUAL.md
│   └── validacion_revisión_trazas.png
│
├── prompts/                            # Prompts y resultados experimentales
│   ├── registro_resultados.json
│   ├── resultados_metricas.json
│   └── trazas_agent.jsonl
│
├── reports/                            # Logs, trazas y resultados de ejecución
│   ├── eventos_agente.jsonl
│   ├── eventos_supervisor.jsonl
│   ├── registros_latencia_costo.jsonl
│   ├── resultados_evaluacion.txt
│   └── trazas_rag.jsonl
│
├── src/
│   ├── agents/
│   │   ├── agent.py
│   │   └── agent_supervisor.py
│   │
│   ├── core/
│   │   ├── client_api.py
│   │   ├── client.py
│   │   ├── config.py
│   │   ├── corpus.py
│   │   ├── dataset_utils.py
│   │   ├── dataset.py
│   │   ├── metrics.py
│   │   ├── preflight.py
│   │   ├── prompt_registry.py
│   │   ├── prompts.py
│   │   ├── risks.py
│   │   └── strategy.py
│   │
│   ├── pipelines/
│   │   ├── chains/
│   │   │   ├── chain_3_steps.py
│   │   │   └── router_chain.py
│   │   │
│   │   ├── try/
│   │   │   ├── try_búsquedas.py
│   │   │   ├── try_chunking.py
│   │   │   ├── try_dataset.py
│   │   │   ├── try_decision.py
│   │   │   ├── try_embeddings.py
│   │   │   ├── try_ensayo_gate2.py
│   │   │   ├── try_index.py
│   │   │   ├── try_indexar_corpus.py
│   │   │   ├── try_instrumentacion_rag.py
│   │   │   ├── try_pasos_1_a_3.py
│   │   │   ├── try_rag.py
│   │   │   ├── try_recovery.py
│   │   │   ├── try_strategy.py
│   │   │   ├── try_tuning_costs.py
│   │   │   └── try_tuning_stats.py
│   │
│   │   ├── aprobar_prompt.py
│   │   ├── costs_rag.py
│   │   ├── dataset_tuning.py
│   │   ├── demo_aprobar_prompt.py
│   │   ├── format_context.py
│   │   ├── indexar_corpus.py
│   │   ├── instrumentacion_rag.py
│   │   ├── metrics_recovery.py
│   │   ├── pipeline_clean_text.py
│   │   └── trazabilidad_citas.py
│   │
│   ├── utils/
│   │   ├── check_trazas.py
│   │   ├── formato_supervision.py
│   │   ├── generate_report_md.py
│   │   ├── latency.py
│   │   ├── leer_registro_latencia.py
│   │   ├── observability.py
│   │   └── security.py
│   │
│   └── main.py
│
├── tests/
│   ├── test_chain_3_steps.py
│   ├── test_client.py
│   ├── test_gate2.py
│   ├── test_pipeline_clean.py
│   ├── test_prompts_y_supervision.py
│   └── test_router_chain.py
│
├── vectorstore/
├── vectorstore_ejemplo/
├── .env.example
├── .gitignore
├── pyproject.toml
├── pytest.ini
├── requirements.txt
└── README.md
```

## 🚀 Guía de Instalación y Ejecución

Sigue estos pasos para configurar y ejecutar el proyecto en tu equipo.

### 1. Clonar el repositorio

Abre una terminal y ejecuta:

```bash
git clone <url-de-tu-repositorio>
cd plantilla-repositorio-base
```

### 2. Configurar el entorno virtual

#### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### macOS / Linux / WSL

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar las dependencias

Instala los paquetes definidos en `requirements.txt`:

```bash
pip install -r requirements.txt
pip install -e .
```

### 4. Configurar las credenciales (.env)

Copia la plantilla de variables de entorno:

#### Windows (PowerShell)

```powershell
Copy-Item .env.example .env
```

#### macOS / Linux / WSL

```bash
cp .env.example .env
```

Abre el archivo `.env` y agrega tu clave real de Google Gemini:

```env
GEMINI_API_KEY=tu_clave_de_api_aqui
```

### 5. Ejecutar flujos principales

```bash
# Aplicación principal
python src/main.py

# Indexar el corpus oficial en ChromaDB
python src/pipelines/indexar_corpus.py

# Ejecutar consulta RAG con instrumentación y registro de latencia/costes
python src/pipelines/instrumentacion_rag.py

# Auditar el historial de trazas de latencia y costes
python src/utils/leer_registro_latencia.py

# Ejecutar agentes y supervisión
python src/agents/agent_supervisor.py

# Ejecutar flujo de aprobación/rechazo de prompts y matriz de riesgos
python src/pipelines/demo_aprobar_prompt.py
python src/pipelines/try/try_pasos_1_a_3.py

# Ensayo integrado RAG, defensa contra prompt injection y trazabilidad
python src/pipelines/try/try_ensayo_gate2.py
```

---

# 🏗️ Arquitectura RAG y Agentes

El proyecto combina recuperación semántica con ChromaDB, embeddings de Gemini, pipelines RAG con trazabilidad de citas, agentes con supervisión, control de seguridad ante *prompt injection*, versionado de prompts con huella SHA-256 + `diff`, aprobación humana en LangGraph (`interrupt` + `Command`) y evaluación de matriz de riesgos.

### Flujo General

```text
Usuario / Propuesta de Prompt
   │
   ▼
Validación y Seguridad (security.py / preflight.py)
   │
   ▼
Retriever (ChromaDB) / Grafo de Supervisión (LangGraph)
   │
   ▼
Contexto Recuperado / Decisión Humana (Command resume)
   │
   ▼
Pipeline RAG o Despliegue Controlado
   │
   ▼
Telemetría, Logs JSONL (observability.py / reports/) y Auditoría
```

---

## 🛡️ Características Principales Implementadas

### ✅ Resiliencia, Fallback y Control de Excepciones

- Rotación y respaldo entre modelos ante errores de cuota o disponibilidad (`429` / `503`).
- Cadenas protegidas con `.with_fallbacks()` y manejo seguro de errores.

### ✅ Pipeline RAG y Trazabilidad de Citas

- Fragmentación con `RecursiveCharacterTextSplitter`.
- Embeddings con `models/gemini-embedding-001` y persistencia en `vectorstore/`.
- Citación explícita de fuentes (`[1]`, `[2]`, etc.) y análisis de costes/tiempos en `src/pipelines/costs_rag.py`.

### ✅ Pipeline RAG, Recuperación y Trazabilidad de Citas

Incluye:

- Fragmentación de documentos con `RecursiveCharacterTextSplitter`.
- Generación de embeddings usando `models/gemini-embedding-001`.
- Persistencia vectorial en `vectorstore/`.
- Recuperación semántica con ChromaDB.
- Citación estricta de fuentes (`[1]`, `[2]`, etc.).

### ✅ Agentes Autónomos y Supervisión

Implementación de agentes mediante:

- `src/agents/agent.py`
- `src/agents/agent_supervisor.py`

Características:

- Selección dinámica de herramientas.
- Límites de autonomía.
- Auditoría completa de decisiones.
- Registro de actividad en `prompts/trazas_agent.jsonl`.

### ✅ Instrumentación de Latencia y Cálculo Dinámico de Costes

Mide:

- Latencia de embeddings.
- Tiempo de recuperación.
- Tiempo de generación.
- Tokens de entrada y salida.
- Coste estimado por ejecución.

Resultados almacenados en:

```text
reports/registros_latencia_costo.jsonl
```

### ✅ Banco de Prompts, Schemas y Métricas (F1 / Retrieval)

Incluye validación estructurada de respuestas JSON y métricas como:

- Precisión
- Cobertura
- Recall
- F1 Score
- Evaluación de recuperación semántica

### ✅ Versionado de Prompts, Supervisión Humana y Matriz de Riesgos

- Huella SHA-256 corta, historial de versiones y comparación palabra a palabra con `difflib.unified_diff` en `src/core/prompt_registry.py`.
- Flujo de supervisión con `StateGraph`, `interrupt()`, `get_state()`, `Command(resume=True/False)` y persistencia en `SqliteSaver` (`src/pipelines/aprobar_prompt.py` y `src/pipelines/demo_aprobar_prompt.py`).
- Cálculo de puntaje, categoría (`CRITICO`, `ALTO`, `MEDIO`, `BAJO`) y detección de casos `[AL LIMITE]` en `src/core/risks.py` y `src/pipelines/try/try_pasos_1_a_3.py`.

### ✅ Seguridad y Observabilidad

- Detección de patrones de *prompt injection* y filtrado de documentos en `src/utils/security.py`.
- Logs estructurados en JSON con `trace_id` y callbacks en `src/utils/observability.py`, con trazas en `reports/` y `prompts/`.

### ✅ Preparación de Datasets y Tuning

- Validación de esquemas JSON, chequeo de balance entre categorías y estimación de esfuerzo/coste de etiquetado en:
  - `src/core/dataset_utils.py`
  - `src/core/dataset.py`
  - `src/pipelines/dataset_tuning.py`

---

---

## 📄 Variables de Entorno

El proyecto requiere una clave de acceso a la API de Google Gemini.

Ejemplo del archivo `.env`:

```env
GEMINI_API_KEY=tu_clave_de_api_aqui
```

> **Importante:** Nunca subas tu archivo `.env` al repositorio. Mantén este archivo incluido en `.gitignore`.

---
## 📝Verificación de Resiliencia y Ejecución en Contenedor Docker

## Comando de Montaje Utilizado

```powershell
docker run --rm -it -v ${PWD}:/app -w /app python:3.10-slim bash
```

---

## Hallazgos Durante la Ejecución

### 1. Saturación de Cuotas y Disponibilidad

Al ejecutar el banco de pruebas, el modelo primario respondió en ocasiones con códigos de error asociados a límites de capacidad y disponibilidad:

- `429 (Cuota excedida)`
- `503 (Servicio no disponible)`

Estos errores fueron observados durante los reintentos automáticos implementados por el sistema.

### 2. Aislamiento y Gestión de Credenciales

El archivo `.env` local fue leído de forma correcta y segura dentro del contenedor mediante el volumen mapeado (`-v`), sin necesidad de reinyectar secretos o credenciales dentro de la imagen Docker.

---

## Ajustes y Soluciones Aplicadas

### 1. Conmutación por Error (Fallback)

El sistema de resiliencia implementado interceptó correctamente los errores:

- `429`
- `503`

Ante estas situaciones, la aplicación conmutó automáticamente hacia los modelos secundarios de respaldo configurados, permitiendo la continuidad del procesamiento.

### 2. Validación de Estructura JSON

A pesar de los incidentes iniciales relacionados con la disponibilidad de red del modelo principal, la ejecución finalizó correctamente y los esquemas JSON fueron validados con éxito.

### 3. Persistencia de Evidencias

El resultado completo del ensayo quedó registrado automáticamente en el archivo:

```text
prompts/registro_resultados.json
```

---

## Resultado del Ensayo

✅ Ejecución validada en entorno aislado.

✅ Lectura segura de variables de entorno mediante archivo `.env`.

✅ Activación correcta de estrategias de resiliencia y fallback.

✅ Validación exitosa de esquemas JSON.

✅ Generación automática de evidencias en archivo de resultados.

---
## Registro del ensayo de rate limit y costos

- **Fecha:** 2026-10-28
- **Peticiones enviadas:** 5 solicitudes de prueba + evaluación del banco de prompts
- **Petición donde apareció el primer 429 / fallback:** En la Solicitud #1 (`gemini-3.5-flash` agotó sus reintentos por cuota excedida y aplicó fallback exitoso a `gemini-3.5-flash-lite`).
- **Esperas observadas:** 2.94s, 4.49s (backoff exponencial con jitter y memoria inteligente de modelo funcionando correctamente).
- **Costo total del ensayo:** $0.00020 USD
- **Resultado:** Las peticiones completaron su ciclo con éxito tras el respaldo, la estructura de los JSONs fue validada correctamente y el registro final se exportó de forma automatizada en `prompts/registro_resultados.json`.


## Conclusión

La prueba confirmó que la arquitectura implementada es capaz de mantener la continuidad operativa frente a errores de cuota y disponibilidad del proveedor principal. Además, se verificó la correcta gestión de credenciales, la validación de los datos generados y la persistencia automática de evidencias para auditoría y evaluación.

---

**Estado final:** ✅ Ensayo completado satisfactoriamente.

**Compatible con:**
- GitHub
- GitLab
- Azure DevOps
- Revisión de rúbrica Gate 1


## 🧪 Ejecución de Pruebas Unitarias

El proyecto incluye una suite de pruebas automatizadas con pytest ubicada en la carpeta tests/. Para ejecutarlas, asegúrate de tener tu entorno virtual activo y corre:

```bash
pytest tests/ -v
```

---

## 📚 Documentación

La carpeta `docs/` contiene:

- Diagramas de arquitectura.
- Decisiones técnicas.
- Revisiones manuales.
- Evidencias de ejecución.
- Validaciones de trazabilidad y supervisión.

---

## 👨‍💻 Autor

Proyecto desarrollado por *Odette Gallo* para la evaluación **Gate 1 - Especialización en Desarrollo con IA Generativa (Accenture)**.