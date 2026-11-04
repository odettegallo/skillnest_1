from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from pipelines.router_chain import construir_router, construir_cadena_con_enrutamiento

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