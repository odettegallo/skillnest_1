
# Proyecto Gate 1 — Especialización en Desarrollo con IA Generativa (Accenture)

Aplicación en Python y LangChain que se conecta a la API de Google Gemini implementando arquitecturas resilientes con múltiples modelos (Fallback), enrutamiento dinámico de mensajes mediante `RunnableBranch`, manejo estricto de errores y una suite completa de pruebas unitarias automatizadas con `pytest`.

---

## 📂 Estructura del Proyecto

```text
plantilla-repositorio-base/
│
├── docs/                      # Documentación técnica y diagramas de arquitectura
│   ├── .gitkeep
│   ├── diagrama_arquitectura_API.png
│   ├── eleccion_arquitectura.md
│   ├── evidencia_petición.png
│   ├── limites_métrica.md
│   └── REVISION_MANUAL.md
│
├── prompts/                   # Banco de prompts estructurados y registros de resultados
│   ├── registro_resultados.json
│   └── resultados_metricas.json
│
├── pruebas/                   # Archivos auxiliares de pruebas y recursos
│
├── src/                       # Código fuente principal de la aplicación
│   ├── core/                  # Núcleo de configuración y cliente base
│   │   ├── __init__.py
│   │   ├── client.py          # Cliente modular y orquestador del modelo
│   │   ├── config.py          # Configuración global, modelos y constantes
│   │   └── try_api.py         # Script base de conexión a la API
│   │
│   ├── pipelines/             # Cadenas de ejecución y orquestación con LangChain
│   │   ├── __init__.py
│   │   ├── chain_3_steps.py   # Cadena secuencial de múltiples pasos
│   │   ├── pipeline_clean_text.py # Limpieza de texto, tokenización y métricas F1
│   │   └── router_chain.py    # Router inteligente con RunnableBranch y Fallbacks
│   │
│   ├── utils/                 # Utilidades de rendimiento, reportes y métricas
│   │   ├── __init__.py
│   │   ├── generate_report_md.py # Generador automatizado de reportes en Markdown
│   │   └── latency.py         # Mediciones y pruebas de rendimiento/latencia
│   │
│   ├── .gitkeep
│   └── main.py                # Punto de entrada principal de la aplicación
│
├── tests/                     # Pruebas unitarias automatizadas con pytest
│   ├── .gitkeep
│   ├── test_chain_3_steps.py  # Pruebas para la cadena secuencial
│   ├── test_client.py         # Pruebas para el cliente modular y resiliencia
│   ├── test_pipeline_clean.py # Pruebas para el pipeline de texto y métricas
│   └── test_router_chain.py   # Pruebas unitarias completas para el router de mensajes
│
├── .env.example               # Plantilla de variables de entorno (requiere API Key)
├── .env                       # Variables de entorno reales (excluido en .gitignore)
├── .gitignore                 # Archivos y carpetas ignorados por Git
├── pyproject.toml             # Configuración del paquete y dependencias de desarrollo
├── pytest.ini                 # Configuración general para la ejecución de pruebas
├── requirements.txt           # Dependencias del proyecto
└── README.md                  # Instrucciones de instalación y ejecución
```

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
python src/main.py
```

También puedes ejecutar otros scripts ubicados dentro de la carpeta `src/` según la funcionalidad que quieras probar.

---

## 🛡️ Características Principales Implementadas

### ✅ Resiliencia y Fallback

Sistema inteligente que recorre una lista de modelos de respaldo (`gemini-2.5-flash`, `gemini-3.5-flash`, etc.) cuando se detectan errores de disponibilidad o límites de uso (códigos 429 o 503).

### ✅ Resiliencia Nivel Cadena (with_fallbacks)
Todas las rutas de respuesta están protegidas con cadenas de respaldo (respuesta_generica) mediante .with_fallbacks(), asegurando que ante caídas de red o errores del LLM el sistema devuelva una respuesta cordial y estructurada al usuario en lugar de propagar una excepción.

### ✅ Control Global de Excepciones (procesar_mensaje_seguro)
Wrapper de entrada con bloque try/except envolviendo la invocación (.invoke()), registrando el error en logs sin interrumpir el flujo ni colapsar la experiencia de usuario.

### ✅ Manejo Robusto de Errores

Implementación de validaciones y excepciones controladas (`ValueError`, `RuntimeError`) para evitar fallos silenciosos y facilitar la depuración.

### ✅ Banco de Prompts y Schemas

Validación estricta de respuestas JSON mediante esquemas predefinidos que garantizan consistencia estructural y facilidad de procesamiento.

### ✅ Pipeline de Texto y Métricas (F1)

Limpieza de texto, tokenización y cálculo automatizado de métricas de Precisión, Cobertura y F1 comparando respuestas generadas por la IA frente a textos de referencia, clasificando el desempeño e identificando los peores casos para su revisión.


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