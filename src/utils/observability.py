import sys
import json
import logging
import hashlib
from contextvars import ContextVar
from typing import Any, Dict, List, Optional

from langchain_core.callbacks import BaseCallbackHandler

trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)


def _a_texto(valor: Any) -> str:
    if isinstance(valor, str):
        return valor
    if isinstance(valor, (dict, list)):
        return json.dumps(valor, ensure_ascii=False)
    return str(valor) if valor is not None else ""


def huella_texto(texto: Any) -> str:
    texto_str = _a_texto(texto)
    return hashlib.sha256(texto_str.encode("utf-8")).hexdigest()[:12]


def resumen_gobernado(texto: Any) -> Dict[str, Any]:
    texto_str = _a_texto(texto)
    return {"chars": len(texto_str), "huella": huella_texto(texto_str)}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "msg": record.getMessage(),
            "trace_id": getattr(record, "trace_id", None) or trace_id_var.get(),
        }
        extra_data = getattr(record, "extra_data", None)
        if isinstance(extra_data, dict):
            payload.update(extra_data)
        return json.dumps(payload, ensure_ascii=False)


def obtener_logger_json(
    nombre: str = "agente_trazas",
    archivo_jsonl: Optional[str] = None,
    consola: bool = True,
) -> logging.Logger:
    logger = logging.getLogger(nombre)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    formatter = JsonFormatter()

    if consola:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    if archivo_jsonl:
        file_handler = logging.FileHandler(archivo_jsonl, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

class CallbackObservabilidad(BaseCallbackHandler):
    def __init__(self, logger: logging.Logger) -> None:
        super().__init__()
        self.logger = logger

    def _trace_id(self, metadata: Optional[Dict[str, Any]]) -> Optional[str]:
        if metadata and metadata.get("trace_id"):
            return str(metadata["trace_id"])
        return trace_id_var.get()

    def on_retriever_start(
        self,
        serialized: Dict[str, Any],
        query: str,
        *,
        run_id: Any,
        parent_run_id: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        self.logger.info(
            "retriever_start",
            extra={
                "trace_id": self._trace_id(metadata),
                "extra_data": {
                    "run_id": str(run_id),
                    "parent_run_id": str(parent_run_id) if parent_run_id else None,
                    "query_resumen": resumen_gobernado(query),
                },
            },
        )

    def on_retriever_end(
        self,
        documents: List[Any],
        *,
        run_id: Any,
        parent_run_id: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        self.logger.info(
            "retriever_end",
            extra={
                "trace_id": self._trace_id(metadata),
                "extra_data": {
                    "run_id": str(run_id),
                    "parent_run_id": str(parent_run_id) if parent_run_id else None,
                    "n_documentos": len(documents),
                },
            },
        )

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: Any,
        parent_run_id: Any = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        herramienta = (serialized or {}).get("name", "herramienta_desconocida")
        self.logger.info(
            "tool_start",
            extra={
                "trace_id": self._trace_id(metadata),
                "extra_data": {
                    "herramienta": herramienta,
                    "run_id": str(run_id),
                    "parent_run_id": str(parent_run_id) if parent_run_id else None,
                    "input_resumen": resumen_gobernado(json.dumps(inputs or input_str, ensure_ascii=False)),
                },
            },
        )

    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: Any,
        parent_run_id: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        salida_str = output if isinstance(output, str) else str(getattr(output, "content", output))
        self.logger.info(
            "tool_end",
            extra={
                "trace_id": self._trace_id(metadata),
                "extra_data": {
                    "run_id": str(run_id),
                    "parent_run_id": str(parent_run_id) if parent_run_id else None,
                    "output_resumen": resumen_gobernado(salida_str),
                },
            },
        )

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: Any,
        parent_run_id: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        self.logger.info(
            "llm_start",
            extra={
                "trace_id": self._trace_id(metadata),
                "extra_data": {
                    "n_prompts": len(prompts),
                    "run_id": str(run_id),
                    "parent_run_id": str(parent_run_id) if parent_run_id else None,
                },
            },
        )

    def on_llm_end(
        self,
        response: Any,
        *,
        run_id: Any,
        parent_run_id: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        texto = ""
        try:
            texto = response.generations[0][0].text
        except Exception:
            texto = str(response)
        self.logger.info(
            "llm_end",
            extra={
                "trace_id": self._trace_id(metadata),
                "extra_data": {
                    "chars_respuesta": len(texto),
                    "huella_respuesta": huella_texto(texto),
                    "run_id": str(run_id),
                    "parent_run_id": str(parent_run_id) if parent_run_id else None,
                },
            },
        )

if __name__ == "__main__":
    from langchain_core.language_models.fake import FakeListLLM

    logger = obtener_logger_json("prueba_obs")
    callback = CallbackObservabilidad(logger)
    llm = FakeListLLM(responses=["Respuesta de prueba desde observability.py"])

    token = trace_id_var.set("trace-demo-01")
    try:
        llm.invoke(
            "¿Funciona el callback?",
            config={"callbacks": [callback], "metadata": {"trace_id": "trace-demo-01"}},
        )
    finally:
        trace_id_var.reset(token)