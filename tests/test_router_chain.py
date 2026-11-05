from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from pipelines.router_chain import (
    construir_router, 
    construir_cadena_con_enrutamiento, 
    construir_paso_clasificacion, 
    respuesta_generica
)

def test_clasificacion_normaliza_antes_de_comparar():
    """
    Verifica que '.strip().lower()' deja la categoría en minúsculas y sin espacios,
    sin importar cómo la devuelva el modelo (ej: ' Queja \n').
    """
    modelo_falso = MagicMock()
    modelo_falso.return_value = AIMessage(content=" Queja \n")
    
    paso = construir_paso_clasificacion(modelo_falso)
    resultado = paso.invoke({"mensaje": "algo salió mal"})
    
    assert resultado == "queja"


def test_enrutamiento_va_a_cadena_queja():
    """
    Verifica que un mensaje clasificado como 'queja' ejecuta 'cadena_queja', 
    y no cualquier otra ruta.
    """
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.return_value = "queja"
    
    cadena_queja_falsa = MagicMock()
    cadena_queja_falsa.return_value = "respuesta de queja ejecutada"
    
    cadena_pregunta_falsa = MagicMock()
    cadena_pregunta_falsa.return_value = "respuesta pregunta"

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_queja=cadena_queja_falsa,
        cadena_pregunta=cadena_pregunta_falsa,
    )

    resultado = cadena.invoke({"mensaje": "tengo un problema"})

    assert cadena_queja_falsa.called
    assert not cadena_pregunta_falsa.called
    assert resultado == "respuesta de queja ejecutada"


def test_cadena_queja_usa_fallback_ante_fallo_del_modelo():
    """
    Si 'cadena_queja' falla, 'with_fallbacks' ejecuta la alternativa configurada,
    en vez de propagar la excepción.
    """
    def fallar_a_proposito(x):
        raise Exception("Error de red simulado")

    cadena_rota = RunnableLambda(fallar_a_proposito)
    cadena_segura = cadena_rota.with_fallbacks([respuesta_generica])
    
    resultado = cadena_segura.invoke({"mensaje": "algo"})
    
    assert "Un miembro de nuestro equipo te va a responder pronto" in resultado


def test_procesar_mensaje_seguro_no_propaga_excepciones():
    """
    Que ningún fallo, sea cual sea, deje sin respuesta a quien llama a 'procesar_mensaje_seguro'.
    """
    from pipelines.router_chain import procesar_mensaje_seguro
    
    # Creamos un router falso cuyo método .invoke lanza una excepción
    router_roto = MagicMock()
    router_roto.invoke.side_effect = Exception("Fallo crítico en el sistema")
    
    resultado = procesar_mensaje_seguro("mensaje de prueba", router_roto)
    
    assert "No pudimos procesar tu mensaje en este momento" in resultado


def test_enrutamiento_usa_default_ante_categoria_desconocida():
    """
    Prueba unitaria para verificar que ante una categoría desconocida 
    o inventada, el router utiliza la ruta por defecto (cadena_pregunta).
    """
    # 1. Creamos mocks independientes para la clasificación y la ruta por defecto
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.return_value = "categoria_inventada"
    
    cadena_pregunta_falsa = MagicMock()
    cadena_pregunta_falsa.return_value = "respuesta por defecto"

    # 2. Construimos la cadena inyectando los mocks
    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_pregunta=cadena_pregunta_falsa,
    )

    # 3. Ejecutamos el flujo con un mensaje ambiguo
    resultado = cadena.invoke({"mensaje": "mensaje ambiguo"})

    # 4. Validamos que se haya ejecutado la ruta por defecto
    assert cadena_pregunta_falsa.called


def test_router_enruta_a_queja():
    """Prueba unitaria para la ruta explícita de 'queja'."""
    modelo_falso = MagicMock()
    modelo_falso.side_effect = [
        AIMessage(content="queja"),
        AIMessage(content="Lamentamos mucho el inconveniente..."),
    ]

    router_chain = construir_router(modelo_falso)
    resultado = router_chain.invoke({"mensaje": "La app se cierra cada vez que subo una foto."})

    assert modelo_falso.call_count == 2
    assert "Lamentamos mucho" in resultado


def test_router_enruta_a_sugerencia():
    """Prueba unitaria para la ruta explícita de 'sugerencia'."""
    modelo_falso = MagicMock()
    modelo_falso.side_effect = [
        AIMessage(content="sugerencia"),
        AIMessage(content="Muchas gracias por tu idea, la evaluaremos..."),
    ]

    router_chain = construir_router(modelo_falso)
    resultado = router_chain.invoke({"mensaje": "Deberían agregar un modo oscuro."})

    assert modelo_falso.call_count == 2
    assert "Muchas gracias" in resultado

def test_router_enruta_a_elogio():
    """Prueba unitaria para la ruta explícita de 'elogio'."""
    modelo_falso = MagicMock()
    modelo_falso.side_effect = [
        AIMessage(content="elogio"),
        AIMessage(content="¡Gracias por tus palabras! Nos alegra que disfrutes..."),
    ]

    router_chain = construir_router(modelo_falso)
    resultado = router_chain.invoke({"mensaje": "¡Me encanta la nueva interfaz, está muy intuitiva!"})

    assert modelo_falso.call_count == 2
    assert "Nos alegra que disfrutes" in resultado

def test_router_enruta_a_por_defecto_pregunta():
    """Prueba unitaria para la ruta por defecto (fallback) o 'pregunta'."""
    modelo_falso = MagicMock()
    modelo_falso.side_effect = [
        AIMessage(content="pregunta"),
        AIMessage(content="Aquí tienes la explicación técnica..."),
    ]

    router_chain = construir_router(modelo_falso)
    resultado = router_chain.invoke({"mensaje": "¿Cómo configuro las credenciales?"})

    assert modelo_falso.call_count == 2
    assert "explicación técnica" in resultado