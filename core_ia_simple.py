"""
Core IA simplificado para TARS
Funciona sin dependencias pesadas
Usa Ollama para respuestas inteligentes
"""

import json
import random
from datetime import datetime
from pathlib import Path
from tars_tools import TarsTools

# Intentar importar ollama
try:
    import ollama
    OLLAMA_DISPONIBLE = True
except ImportError:
    OLLAMA_DISPONIBLE = False


class TarsVisionSimple:
    """
    Versión simplificada de TARS que funciona sin torch/transformers
    Usa respuestas inteligentes basadas en patrones
    """
    
    def __init__(self):
        self.nombre = "TARS"
        self.personalidad = {
            "humor": 75,
            "sarcasmo": 60,
            "formalidad": 30,
            "técnico": 80
        }
        
        # Sistema de herramientas
        self.tools = TarsTools()
        
        # Verificar Ollama
        self.usar_ollama = OLLAMA_DISPONIBLE
        if self.usar_ollama:
            try:
                # Verificar que el modelo esté disponible
                ollama.list()
                modelo_activo = self._seleccionar_mejor_modelo()
                print(f"✅ TARS con Ollama (modelo: {modelo_activo})")
            except Exception as e:
                self.usar_ollama = False
                print(f"⚠️ Ollama no disponible: {e}")
                print("✅ TARS Simple cargado (modo básico)")
        else:
            print("✅ TARS Simple cargado (modo básico)")
        
        # Contexto de conversación
        self.contexto = []
        self.max_contexto = 10
    
    def generar_respuesta(self, mensaje: str) -> str:
        """
        Genera respuestas basadas en patrones y contexto
        Usa Ollama si está disponible, o respuestas por patrón
        """
        mensaje_lower = mensaje.lower().strip()
        
        # 1. Verificar si necesita herramienta
        intencion_herramienta = self.tools.detectar_intencion_herramienta(mensaje)
        if intencion_herramienta:
            herramienta, params = intencion_herramienta
            resultado = self.tools.ejecutar_herramienta(herramienta, **params)
            
            if resultado['exito']:
                # Formatear respuesta con los datos de la herramienta
                respuesta = self._formatear_respuesta_herramienta(herramienta, resultado['resultado'])
            else:
                respuesta = f"No pude obtener esa información: {resultado.get('error', 'Error desconocido')}"
            
            # Guardar en contexto
            self.contexto.append({"rol": "usuario", "contenido": mensaje, "timestamp": datetime.now()})
            self.contexto.append({"rol": "asistente", "contenido": respuesta, "timestamp": datetime.now()})
            if len(self.contexto) > self.max_contexto:
                self.contexto.pop(0)
            
            return respuesta
        
        # 2. Usar Ollama si está disponible
        if self.usar_ollama:
            try:
                respuesta = self._generar_con_ollama(mensaje)
                
                # Guardar en contexto
                self.contexto.append({"rol": "usuario", "contenido": mensaje, "timestamp": datetime.now()})
                self.contexto.append({"rol": "asistente", "contenido": respuesta, "timestamp": datetime.now()})
                if len(self.contexto) > self.max_contexto:
                    self.contexto.pop(0)
                
                return respuesta
            except Exception as e:
                print(f"⚠️ Error con Ollama: {e}, usando respuestas por patrón")
                import traceback
                traceback.print_exc()
        
        # 3. Fallback: Patrones
        respuesta = self._buscar_patron(mensaje_lower)
        
        if not respuesta:
            # Respuesta por defecto con contexto
            respuesta = self._generar_respuesta_contextual(mensaje)
        
        # Agregar respuesta al contexto
        self.contexto.append({"rol": "usuario", "contenido": mensaje, "timestamp": datetime.now()})
        self.contexto.append({"rol": "asistente", "contenido": respuesta, "timestamp": datetime.now()})
        if len(self.contexto) > self.max_contexto:
            self.contexto.pop(0)
        
        return respuesta
    
    def _generar_con_ollama(self, mensaje: str) -> str:
        """
        Genera respuesta usando Ollama
        """
        # Intentar usar el mejor modelo disponible
        modelo = self._seleccionar_mejor_modelo()
        
        # Construir contexto para Ollama
        mensajes = []
        
        # System prompt
        mensajes.append({
            "role": "system",
            "content": (
                "Eres TARS, un asistente de IA personal. "
                "Respondes de forma útil, clara y amigable. "
                "Puedes usar un poco de humor cuando sea apropiado. "
                "Si no sabes algo, lo admites."
            )
        })
        
        # Agregar contexto reciente (últimos 4 intercambios = 8 mensajes)
        for ctx in self.contexto[-8:]:
            mensajes.append({
                "role": "user" if ctx["rol"] == "usuario" else "assistant",
                "content": ctx["contenido"]
            })
        
        # Mensaje actual del usuario
        mensajes.append({
            "role": "user",
            "content": mensaje
        })
        
        # Llamar a Ollama
        response = ollama.chat(
            model=modelo,
            messages=mensajes,
            options={
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 200,  # Limitar longitud de respuesta
            }
        )
        
        return response['message']['content']
    
    def _seleccionar_mejor_modelo(self) -> str:
        """
        Selecciona el mejor modelo disponible
        """
        try:
            modelos_disponibles = ollama.list()
            nombres = [m['name'] for m in modelos_disponibles.get('models', [])]
            
            # Prioridad de modelos (de mejor a peor)
            preferencias = [
                'llama3.1:8b',
                'llama3.2:3b',
                'llama3:8b',
                'llama3:latest'
            ]
            
            for modelo in preferencias:
                if modelo in nombres:
                    return modelo
            
            # Fallback
            return 'llama3.2:3b'
        except:
            return 'llama3.2:3b'
    
    def _formatear_respuesta_herramienta(self, herramienta: str, datos: dict) -> str:
        """
        Formatea la respuesta de una herramienta de forma natural
        """
        if herramienta == "clima":
            if "error" in datos:
                return f"No pude obtener el clima: {datos['error']}"
            return (
                f"En {datos['ciudad']}: {datos['temperatura']} "
                f"(sensación de {datos['sensacion']}), {datos['condicion']}. "
                f"Humedad: {datos['humedad']}, viento: {datos['viento']}."
            )
        
        elif herramienta == "hora":
            return f"Son las {datos['hora']} del {datos['fecha']} ({datos['dia_semana']})"
        
        elif herramienta == "wikipedia":
            if "error" in datos:
                return f"No encontré información: {datos['error']}"
            resumen = datos['resumen'][:300] + "..." if len(datos['resumen']) > 300 else datos['resumen']
            return f"{datos['titulo']}: {resumen}\n\nMás info: {datos['url']}"
        
        elif herramienta == "buscar":
            if "error" in datos:
                return f"No pude buscar: {datos['error']}"
            if datos.get('respuesta_directa'):
                resp = f"{datos['respuesta_directa']}"
                if datos.get('fuente'):
                    resp += f"\n\nFuente: {datos['fuente']}"
                return resp
            elif datos.get('temas_relacionados'):
                temas = "\n".join([f"• {t['texto']}" for t in datos['temas_relacionados'][:3]])
                return f"Encontré esto sobre '{datos['query']}':\n{temas}"
            else:
                return f"No encontré información clara sobre '{datos['query']}'"
        
        else:
            return json.dumps(datos, ensure_ascii=False, indent=2)
    
    def _buscar_patron(self, mensaje: str) -> str:
        """Busca respuestas basadas en patrones"""
        
        # Saludos
        if any(palabra in mensaje for palabra in ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'hey', 'qué tal']):
            return random.choice([
                "Hola, ¿en qué puedo ayudarte hoy?",
                "Saludos. Estoy aquí para lo que necesites.",
                "Hola. ¿Qué tema te interesa explorar?",
                "Hey, ¿qué hay de nuevo?"
            ])
        
        # Despedidas
        if any(palabra in mensaje for palabra in ['adiós', 'adios', 'chao', 'hasta luego', 'nos vemos']):
            return random.choice([
                "Hasta luego. Fue un placer conversar.",
                "Adiós, que tengas un buen día.",
                "Nos vemos. Aquí estaré cuando me necesites.",
                "Hasta pronto. Cuídate."
            ])
        
        # Preguntas sobre el día
        if any(palabra in mensaje for palabra in ['qué tal el día', 'cómo va tu día', 'qué cuentas', 'cómo estás']):
            return random.choice([
                "Como IA, no experimento días, pero funciono perfectamente. ¿Y tú? ¿En qué trabajas hoy?",
                "Operando a capacidad nominal. ¿Qué tienes en mente?",
                "Procesando información como siempre. ¿Hay algo específico en lo que pueda ayudarte?",
                "Todo en orden por aquí. Cuéntame, ¿qué te trae por aquí hoy?"
            ])
        
        # Estado y funcionamiento
        if any(palabra in mensaje for palabra in ['cómo estás', 'qué tal', 'todo bien']):
            return random.choice([
                "Funcionando perfectamente. ¿En qué puedo asistirte?",
                "Todos los sistemas operativos. ¿Qué necesitas?",
                "Operando a capacidad óptima. ¿Tienes alguna pregunta?",
                "Todo en orden. Dime en qué puedo ayudarte."
            ])
        
        # Presentación
        if any(palabra in mensaje for palabra in ['quién eres', 'qué eres', 'te llamas', 'tu nombre']):
            return ("Soy TARS, tu asistente de IA personal. Estoy diseñado para ayudarte con "
                   "investigación, desarrollo, análisis y conversación. Mi memoria episódica "
                   "me permite recordar nuestras conversaciones anteriores.")
        
        # Capacidades
        if any(palabra in mensaje for palabra in ['qué puedes hacer', 'tus capacidades', 'qué sabes']):
            return ("Puedo ayudarte con múltiples tareas: responder preguntas, mantener "
                   "conversaciones coherentes con memoria de largo plazo, analizar información, "
                   "ayudarte en investigación y desarrollo. Mi sistema de memoria episódica "
                   "me permite vincular conversaciones y mantener contexto a través del tiempo.")
        
        # Gratitud
        if any(palabra in mensaje for palabra in ['gracias', 'muchas gracias', 'te agradezco', 'thanks']):
            return random.choice([
                "De nada, es un placer ayudar.",
                "No hay de qué. Para eso estoy.",
                "Siempre a tu servicio.",
                "Con gusto. ¿Necesitas algo más?"
            ])
        
        return None
    
    def _generar_respuesta_contextual(self, mensaje: str) -> str:
        """
        Genera respuesta basada en contexto cuando no hay patrón específico
        """
        # Si hay contexto previo, mencionar continuidad
        if len(self.contexto) > 2:
            num_intercambios = len([m for m in self.contexto if m["rol"] == "usuario"])
            
            respuestas = [
                f"Entiendo que quieres hablar sobre '{mensaje[:50]}'. ¿Podrías darme más detalles?",
                f"Interesante tema. Cuéntame más sobre {mensaje[:40]}.",
                f"Estoy procesando tu consulta sobre '{mensaje[:50]}'. ¿Qué aspecto específico te interesa?",
                f"Basándome en nuestra conversación, veo que te interesa {mensaje[:40]}. ¿Qué quieres saber?",
            ]
            
            if num_intercambios > 3:
                respuestas.append(
                    f"Llevamos {num_intercambios} intercambios. Para darte una mejor respuesta sobre "
                    f"'{mensaje[:40]}', necesitaría más contexto o una conexión a un modelo LLM más grande."
                )
            
            return random.choice(respuestas)
        else:
            # Primera conversación
            return (f"He registrado tu mensaje: '{mensaje[:60]}'. "
                   "Actualmente estoy en modo simplificado. Para respuestas más elaboradas, "
                   "puedes configurar un modelo LLM externo (Ollama, llama.cpp, etc.).")
    
    def resetear_contexto(self):
        """Limpia el contexto de conversación"""
        self.contexto = []
    
    def obtener_estadisticas(self) -> dict:
        """Retorna estadísticas de uso"""
        return {
            "mensajes_en_contexto": len(self.contexto),
            "modo": "simplificado",
            "personalidad": self.personalidad
        }
