
# Límites de autonomía: Agente de Operaciones y Soporte de Envíos

## Herramientas y nivel de riesgo

- `consultar_estado_envio_con_historial`: bajo (es una herramienta de solo lectura que consulta datos estáticos de envíos).
- `calcular_costo_envio`: bajo (es una herramienta de solo lectura que realiza un cálculo matemático interno sin modificar sistemas externos).
- `generar_reembolso`: alto (es una herramienta de escritura irreversible con impacto económico directo al realizar reembolsos monetarios).

## Herramientas que requieren aprobación humana

- `generar_reembolso`: Requiere aprobación humana obligatoria a través de la función de control interactivo porque maneja transacciones financieras y salidas de dinero irreversibles, evitando acciones no autorizadas por parte del LLM.

## Revisión de trazas

- **Frecuencia:** Cada N interacciones o revisión semanal del archivo de auditoría ubicado en `prompts/trazas_agent.jsonl`.
- **Qué se busca:** Patrones sospechosos basados en la traza, tales como llamadas consecutivas duplicadas a la misma herramienta (ej. reintentos seguidos de `generar_reembolso`) o ejecuciones sin observaciones de respaldo válidas.

## Qué hacer ante un comportamiento inesperado

1. Desactivar temporalmente la herramienta crítica afectada (`generar_reembolso`) removiéndola de la lista de herramientas en el agente.
2. Revisar y ajustar el prompt del sistema (*system prompt*) para acotar las restricciones operativas del modelo.
3. Refinar y aclarar la descripción (*docstring*) de la herramienta para evitar ambigüedades en la interpretación del LLM.


## 🔎 Validación y revisión de trazas

Durante las pruebas del agente se realizaron verificaciones manuales desde PowerShell para validar el correcto funcionamiento del mecanismo de aprobación humana y la generación de registros de auditoría.

### Conteo de registros almacenados

Comando ejecutado:

```powershell
(Get-Content .\prompts\trazas_agent.jsonl).Count
```

**Propósito:**
Cuenta la cantidad total de líneas presentes en el archivo `trazas_agent.jsonl`.

**Interpretación:**
Dado que el formato JSONL almacena un objeto JSON por línea, este comando permite conocer rápidamente cuántos eventos o interacciones han sido registrados por el agente durante las pruebas.

### Verificación del punto de aprobación humana

Comando ejecutado:

```powershell
findstr /S /I /N "esperar_aprobacion" src\pipelines\agent_supervisor.py
```

**Propósito:**
Busca la cadena `esperar_aprobacion` dentro del archivo `agent_supervisor.py`.

**Parámetros utilizados:**

- `/S`: busca en subdirectorios.
- `/I`: ignora diferencias entre mayúsculas y minúsculas.
- `/N`: muestra el número de línea donde se encuentra cada coincidencia.

**Resultados observados:**

- Línea 38: definición de la función `esperar_aprobacion()`.
- Línea 89: invocación de `esperar_aprobacion(mensaje)` antes de ejecutar una acción crítica.

**Interpretación:**
La revisión confirma que el flujo incorpora un mecanismo explícito de supervisión humana antes de permitir la ejecución de operaciones sensibles. Esto garantiza que herramientas de alto riesgo, como `generar_reembolso`, no puedan ser ejecutadas de forma completamente autónoma por el agente.

### Conclusión de la validación

Las evidencias obtenidas mediante el análisis de código y la revisión de trazas permiten verificar que:

- El agente mantiene registros auditables de sus interacciones.
- Existe un punto de control para aprobación humana antes de acciones críticas.
- Las operaciones financieras quedan sujetas a supervisión humana obligatoria.
- La configuración implementada es consistente con los límites de autonomía definidos para el agente.