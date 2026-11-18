
# Especialización en Desarrollo con IA Generativa (Accenture)

Aplicación en Python y LangChain que se conecta a la API de Google Gemini implementando arquitecturas resilientes con múltiples modelos (Fallback), enrutamiento dinámico de mensajes mediante `RunnableBranch`, pipelines de **Retrieval-Augmented Generation (RAG)** con ChromaDB, agentes autónomos con supervisión, telemetría de latencia/costes y una suite completa de pruebas unitarias automatizadas con `pytest`.

---

## 📂 Estructura del Proyecto

plantilla-repositorio-base/
│
├── docs/                               # Documentación técnica y evidencias
│   ├── diagrama_arquitectura_API.png
│   ├── eleccion_arquitectura.md
│   ├── evidencia_peticion.png
│   ├── limites_autonomia_agent.md
│   ├── limites_metrica.md
|   ├── REVISION_MANUAL.md
│   └── validacion_revisión_trazas.png
│
├── prompts/                            # Prompts y resultados experimentales
│   ├── registro_resultados.json
│   ├── resultados_metricas.json
│   └── trazas_agent.jsonl
│
├── reportes/                           # Logs y resultados de ejecución
│   ├── registros_latencia_costo.jsonl
│   └── resultados_evaluacion.txt
│
├── pruebas/                            # Recursos auxiliares para pruebas
│
├── src/
│   ├── agents/                         # Agentes y orquestación
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── agent_supervisor.py
│   │
│   ├── core/                           # Configuración y componentes base
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── config.py
│   │   ├── corpus.py
│   │   ├── metrics.py
│   │   ├── prompts.py
│   │   └── try_api.py
│   │
│   ├── pipelines/                      # Flujos y pipelines RAG
│   │   ├── chains/
│   │   │   ├── __init__.py
│   │   │   ├── chain_3_steps.py
│   │   │   └── router_chain.py
│   │   ├── try/
│   │   │   ├── __init__.py
|   |   |   ├── try_búsquedas.py
│   │   |   ├── try_chunking.py
│   │   |   ├── try_embeddings.py
│   │   |   ├── try_index.py
│   │   |   ├── try_indexar_corpus.py
│   │   |   ├── try_rag.py
│   │   |   └── try_recovery.py
|   |   |
│   │   ├── __init__.py
│   │   ├── costs_rag.py
│   │   ├── format_context.py
│   │   ├── indexar_corpus.py
│   │   ├── instrumentacion_rag.py
│   │   ├── metrics_recovery.py
│   │   ├── pipeline_clean_text.py
│   │   ├── preflight.py
│   │   └── trazabilidad_citas.py
|   |   
│   │
│   ├── utils/                          # Utilidades de auditoría y reportes
│   │   ├── __init__.py
│   │   ├── check_trazas.py
│   │   ├── generate_report_md.py
│   │   ├── latency.py
│   │   └── leer_registro_latencia.py
│   │
│   └── main.py                         # Punto de entrada principal
│
├── tests/                              # Pruebas automáticas con pytest
│   ├── test_chain_3_steps.py
│   ├── test_client.py
│   ├── test_pipeline_clean.py
│   └── test_router_chain.py
│
├── vectorstore/                        # Base vectorial persistente (ChromaDB)
│
├── .env.example                        # Variables de entorno de ejemplo
├── .gitignore
├── pyproject.toml
├── pytest.ini
├── requirements.txt
└── README.md
---

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

### 5. Ejecutar la aplicación

Una vez configurado el entorno y las credenciales, ejecuta:

```bash
# Aplicación principal
python src/main.py
```

También puedes ejecutar otros scripts ubicados dentro de la carpeta `src/` según la funcionalidad que quieras probar.

### 6. Ejecutar flujos principales

```bash
# Indexar el corpus oficial en ChromaDB
python src/pipelines/indexar_corpus.py

# Ejecutar consulta RAG con instrumentación y registro de latencia/costes
python src/pipelines/instrumentacion_rag.py

# Auditar el historial de trazas de latencia y costes
python src/utils/leer_registro_latencia.py

# Ejecutar agentes y supervisión
python src/agents/agent_supervisor.py
```

---

# 🏗️ Arquitectura RAG y Agentes

El proyecto implementa una arquitectura moderna basada en LangChain y Google Gemini que combina:

- Recuperación semántica mediante ChromaDB.
- Embeddings con Gemini Embedding.
- Generación aumentada por recuperación (RAG).
- Agentes con selección dinámica de herramientas.
- Supervisión de límites de autonomía.
- Instrumentación de latencia y costes.
- Trazabilidad de citas y auditoría de decisiones.

### Flujo General

```text
Usuario
   │
   ▼
Consulta
   │
   ▼
Retriever (ChromaDB)
   │
   ▼
Contexto Recuperado
   │
   ▼
Pipeline RAG
   │
   ▼
Gemini LLM
   │
   ▼
Respuesta con citas
   │
   ▼
Telemetría + Logs + Auditoría
```

---

## 🛡️ Características Principales Implementadas

### ✅ Resiliencia y Fallback

Sistema inteligente que recorre una lista de modelos de respaldo (`gemini-3.5-flash`, `gemini-3.5-flash-lite`, `gemini-2.5-flash`, etc.) cuando se detectan errores de disponibilidad o límites de uso (`429` o `503`).

### ✅ Resiliencia Nivel Cadena (`with_fallbacks`)

Todas las rutas de respuesta están protegidas mediante `.with_fallbacks()`, asegurando que ante caídas de red o errores del LLM el sistema entregue una respuesta controlada y amigable.

### ✅ Control Global de Excepciones (`procesar_mensaje_seguro`)

Wrapper principal basado en `try/except` que captura errores de ejecución, registra eventos en logs y evita la interrupción del flujo de usuario.

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
- Justificación de decisiones técnicas.
- Evidencias de ejecución y pruebas.
- Capturas solicitadas para la evaluación del proyecto.

---

## 👨‍💻 Autor

Proyecto desarrollado por *Odette Gallo* para la evaluación **Gate 1 - Especialización en Desarrollo con IA Generativa (Accenture)**.