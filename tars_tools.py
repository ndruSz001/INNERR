"""
Sistema de Herramientas para TARS
Proporciona acceso a información en tiempo real
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
import subprocess


class TarsTools:
    """
    Herramientas que TARS puede usar para obtener información actualizada
    """
    
    def __init__(self):
        self.herramientas_disponibles = {
            "clima": self.obtener_clima,
            "hora": self.obtener_hora,
            "buscar": self.buscar_web,
            "wikipedia": self.buscar_wikipedia,
            "noticias": self.obtener_noticias
        }
    
    def ejecutar_herramienta(self, nombre: str, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta una herramienta específica
        """
        if nombre not in self.herramientas_disponibles:
            return {
                "exito": False,
                "error": f"Herramienta '{nombre}' no disponible",
                "disponibles": list(self.herramientas_disponibles.keys())
            }
        
        try:
            resultado = self.herramientas_disponibles[nombre](**kwargs)
            return {"exito": True, "resultado": resultado}
        except Exception as e:
            return {"exito": False, "error": str(e)}
    
    def obtener_clima(self, ciudad: str = "Santo Domingo", pais: str = "DO") -> Dict[str, Any]:
        """
        Obtiene el clima actual usando wttr.in (no requiere API key)
        """
        try:
            # wttr.in proporciona clima en formato JSON
            url = f"https://wttr.in/{ciudad}?format=j1"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                actual = data['current_condition'][0]
                
                return {
                    "ciudad": ciudad,
                    "temperatura": f"{actual['temp_C']}°C",
                    "sensacion": f"{actual['FeelsLikeC']}°C",
                    "condicion": actual['weatherDesc'][0]['value'],
                    "humedad": f"{actual['humidity']}%",
                    "viento": f"{actual['windspeedKmph']} km/h",
                    "hora_consulta": datetime.now().strftime("%H:%M")
                }
            else:
                return {"error": "No se pudo obtener el clima"}
                
        except Exception as e:
            return {"error": f"Error al consultar clima: {e}"}
    
    def obtener_hora(self, zona: str = "local") -> Dict[str, str]:
        """
        Obtiene la hora actual
        """
        ahora = datetime.now()
        return {
            "hora": ahora.strftime("%H:%M:%S"),
            "fecha": ahora.strftime("%d/%m/%Y"),
            "dia_semana": ahora.strftime("%A"),
            "zona": zona
        }
    
    def buscar_web(self, query: str, num_resultados: int = 3) -> Dict[str, Any]:
        """
        Busca en DuckDuckGo (no requiere API key)
        Usa la API instantanea de DuckDuckGo
        """
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                resultado = {
                    "query": query,
                    "respuesta_directa": data.get('AbstractText', ''),
                    "fuente": data.get('AbstractSource', ''),
                    "url": data.get('AbstractURL', ''),
                }
                
                # Agregar tópicos relacionados si existen
                if data.get('RelatedTopics'):
                    resultado['temas_relacionados'] = [
                        {
                            "texto": t.get('Text', ''),
                            "url": t.get('FirstURL', '')
                        }
                        for t in data['RelatedTopics'][:num_resultados]
                        if isinstance(t, dict) and t.get('Text')
                    ]
                
                return resultado
            else:
                return {"error": "No se pudo realizar la búsqueda"}
                
        except Exception as e:
            return {"error": f"Error en búsqueda: {e}"}
    
    def buscar_wikipedia(self, termino: str, idioma: str = "es") -> Dict[str, Any]:
        """
        Busca información en Wikipedia
        """
        try:
            url = f"https://{idioma}.wikipedia.org/api/rest_v1/page/summary/{termino}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "titulo": data.get('title', ''),
                    "resumen": data.get('extract', ''),
                    "url": data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    "imagen": data.get('thumbnail', {}).get('source', '') if data.get('thumbnail') else None
                }
            else:
                return {"error": f"No se encontró información sobre '{termino}'"}
                
        except Exception as e:
            return {"error": f"Error al consultar Wikipedia: {e}"}
    
    def obtener_noticias(self, tema: str = "tecnologia", num_noticias: int = 3) -> Dict[str, Any]:
        """
        Obtiene noticias recientes (usando RSS de fuentes públicas)
        """
        try:
            # Usar NewsAPI o un feed RSS público
            # Por ahora retornamos un placeholder que indica que la función existe
            return {
                "tema": tema,
                "mensaje": "Para obtener noticias en tiempo real, configura una API key de NewsAPI",
                "sugerencia": "Visita https://newsapi.org/ para obtener una clave gratuita"
            }
        except Exception as e:
            return {"error": f"Error al obtener noticias: {e}"}
    
    def detectar_intencion_herramienta(self, mensaje: str) -> Optional[tuple]:
        """
        Detecta si el usuario quiere usar una herramienta específica
        Returns: (nombre_herramienta, parametros) o None
        """
        mensaje_lower = mensaje.lower()
        
        # Clima
        if any(palabra in mensaje_lower for palabra in ['clima', 'temperatura', 'tiempo', 'pronóstico']):
            # Intentar extraer ciudad
            ciudad = self._extraer_ciudad(mensaje)
            return ("clima", {"ciudad": ciudad} if ciudad else {})
        
        # Hora
        if any(palabra in mensaje_lower for palabra in ['hora', 'qué hora', 'que hora']):
            return ("hora", {})
        
        # Wikipedia
        if 'wikipedia' in mensaje_lower or mensaje_lower.startswith('qué es') or mensaje_lower.startswith('que es'):
            termino = mensaje_lower.replace('wikipedia', '').replace('qué es', '').replace('que es', '').strip()
            if termino:
                return ("wikipedia", {"termino": termino})
        
        # Búsqueda general
        if mensaje_lower.startswith('busca') or mensaje_lower.startswith('buscar'):
            query = mensaje_lower.replace('busca', '').replace('buscar', '').strip()
            if query:
                return ("buscar", {"query": query})
        
        return None
    
    def _extraer_ciudad(self, mensaje: str) -> Optional[str]:
        """
        Intenta extraer nombre de ciudad del mensaje
        """
        mensaje_lower = mensaje.lower()
        
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
