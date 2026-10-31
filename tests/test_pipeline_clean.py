from pipeline_clean_text import procesar_texto  

def test_procesar_texto_normaliza_mayusculas_y_puntuacion():
    """Verifica que el pipeline convierta a minúsculas, limpie puntuación y tokenice correctamente."""
    resultado = procesar_texto("El Cielo, es AZUL!")
    assert resultado == ["el", "cielo", "es", "azul"]


def test_procesar_texto_solo_puntuacion_devuelve_lista_vacia():
    """Verifica el caso límite: un texto que tras limpiarse queda vacío retorna una lista vacía."""
    resultado = procesar_texto("¡¡¡...!!!")
    assert resultado == []