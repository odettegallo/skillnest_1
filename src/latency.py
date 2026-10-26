import time
from try_api import enviar_peticion, MODELOS_DISPONIBLES

def medir_latencia_modelo(pregunta, modelo, iteraciones=3):
    """Mide la latencia de un modelo específico de forma aislada."""
    print(f"\n🧪 Midiendo latencias para el modelo: {modelo}")
    latencias = []
    
    for i in range(iteraciones):
        try:
            inicio = time.perf_counter()
            # Llamamos directamente al modelo sin hacer fallback cruzado
            enviar_peticion(pregunta, modelo)
            fin = time.perf_counter()
            
            latencia = fin - inicio
            latencias.append(latencia)
            print(f"   ⏱️ Intento {i + 1}: {latencia:.2f} segundos")
        except Exception as e:
            print(f"   ⚠️ Error en intento {i + 1}: {e}")
            
        time.sleep(1) # Pausa breve para evitar saturación
        
    if latencias:
        promedio = sum(latencias) / len(latencias)
        print(f"   📊 Promedio para {modelo}: {promedio:.2f} s")
        return promedio
    return None

if __name__ == "__main__":
    pregunta_prueba = "Hola, dime una frase corta."
    
    # Probamos dos modelos de la lista de forma limpia y separada
    modelos_a_probar = MODELOS_DISPONIBLES[:2] # Toma los primeros dos modelos
    
    for mod in modelos_a_probar:
        medir_latencia_modelo(pregunta_prueba, mod, iteraciones=3)