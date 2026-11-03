import sys
import os

# Aseguramos que la carpeta 'src' esté en el path de Python para importar sin problemas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from pipeline_clean_text import ejecutar_pruebas

if __name__ == "__main__":
    print("==================================================")
    print("🚀 EJECUTANDO DEMOSTRACIÓN COMPLETA - GATE 1")
    print("==================================================\n")
    
    try:
        # Ejecuta todo el flujo de 20 casos, métricas y guardado en JSON
        ejecutar_pruebas()
        
        print("\n==================================================")
        print("✅ ¡Demostración completada exitosamente!")
        print("==================================================")
    except Exception as error:
        print(f"\n❌ Error durante la ejecución del flujo: {error}")