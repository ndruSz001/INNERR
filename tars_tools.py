"""
Sistema de Herramientas para TARS
Proporciona acceso a información en tiempo real
"""

# Modularized: import TarsTools from tars_tools.tools
from tars_tools.tools import TarsTools
        
        # Ciudades comunes
        ciudades = {
            'santo domingo': 'Santo Domingo',
            'santiago': 'Santiago',
            'nueva york': 'New York',
            'madrid': 'Madrid',
            'barcelona': 'Barcelona',
            'bogota': 'Bogota',
            'bogotá': 'Bogota',
            'buenos aires': 'Buenos Aires',
            'lima': 'Lima',
            'ciudad de mexico': 'Mexico City',
            'méxico': 'Mexico City'
        }
        
        for ciudad_key, ciudad_nombre in ciudades.items():
            if ciudad_key in mensaje_lower:
                return ciudad_nombre
        
        # Si menciona "en [ciudad]", intentar extraer
        if ' en ' in mensaje_lower:
            partes = mensaje_lower.split(' en ')
            if len(partes) > 1:
                posible_ciudad = partes[1].strip().split()[0]
                return posible_ciudad.capitalize()
        
        return None
