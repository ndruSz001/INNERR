"""
Archivo de orquestación para la IA de TARS.
Este archivo solo contiene el punto de entrada y comentarios para futuras modificaciones.
Toda la lógica debe migrarse a core/ia.py y módulos especializados.
"""

from core.ia import TarsIA

if __name__ == "__main__":
    # Punto de entrada para ejecutar la IA modular
    ia = TarsIA()
    # Aquí puedes agregar lógica de inicialización, pruebas o integración
    # Ejemplo:
    # respuesta = ia.generar_respuesta("¿Cuál es el estado del sistema?")
    # print(respuesta)