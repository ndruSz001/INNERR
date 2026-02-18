"""
ia_simple.py
Versión simplificada de TARS para respuestas inteligentes sin dependencias pesadas.

Ejemplo de uso:
    from core.ia_simple import TarsVisionSimple
    tars = TarsVisionSimple()
    print(tars.generar_respuesta("Hola, ¿qué puedes hacer?"))
"""

import json
import random
from datetime import datetime
from pathlib import Path
from tars_tools import TarsTools

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
        self.tools = TarsTools()
        self.usar_ollama = OLLAMA_DISPONIBLE
        if self.usar_ollama:
            try:
                ollama.list()
                modelo_activo = self._seleccionar_mejor_modelo()
                print(f"✅ TARS con Ollama (modelo: {modelo_activo})")
            except Exception as e:
                self.usar_ollama = False
                print(f"⚠️ Ollama no disponible: {e}")
                print("✅ TARS Simple cargado (modo básico)")
        else:
            print("✅ TARS Simple cargado (modo básico)")
        self.contexto = []
        self.max_contexto = 10

    def generar_respuesta(self, mensaje: str) -> str:
        mensaje_lower = mensaje.lower().strip()
        intencion_herramienta = self.tools.detectar_intencion_herramienta(mensaje)
        if intencion_herramienta:
            herramienta, params = intencion_herramienta
            resultado = self.tools.ejecutar_herramienta(herramienta, **params)
            if resultado['exito']:
                respuesta = self._formatear_respuesta_herramienta(herramienta, resultado['resultado'])
            else:
                respuesta = f"No pude obtener esa información: {resultado.get('error', 'Error desconocido')}"
            self.contexto.append({"rol": "usuario", "contenido": mensaje, "timestamp": datetime.now()})
            self.contexto.append({"rol": "asistente", "contenido": respuesta, "timestamp": datetime.now()})
            if len(self.contexto) > self.max_contexto:
                self.contexto.pop(0)
            return respuesta
        if self.usar_ollama:
            try:
                respuesta = self._generar_con_ollama(mensaje)
                self.contexto.append({"rol": "usuario", "contenido": mensaje, "timestamp": datetime.now()})
                self.contexto.append({"rol": "asistente", "contenido": respuesta, "timestamp": datetime.now()})
                if len(self.contexto) > self.max_contexto:
                    self.contexto.pop(0)
                return respuesta
            except Exception as e:
                print(f"⚠️ Error con Ollama: {e}, usando respuestas por patrón")
                import traceback
                traceback.print_exc()
        respuesta = self._buscar_patron(mensaje_lower)
        if not respuesta:
            respuesta = self._generar_respuesta_contextual(mensaje)
        self.contexto.append({"rol": "usuario", "contenido": mensaje, "timestamp": datetime.now()})
        self.contexto.append({"rol": "asistente", "contenido": respuesta, "timestamp": datetime.now()})
        if len(self.contexto) > self.max_contexto:
            self.contexto.pop(0)
        return respuesta

    def _generar_con_ollama(self, mensaje: str) -> str:
        modelo = self._seleccionar_mejor_modelo()
        mensajes = []
        mensajes.append({
            "role": "system",
            "content": (
                "Eres TARS, un asistente de IA personal. "
                "Respondes de forma útil, clara y amigable. "
                "Puedes usar un poco de humor cuando sea apropiado. "
                "Si no sabes algo, lo admites."
            )
        })
        for ctx in self.contexto[-8:]:
            mensajes.append({
                "role": "user" if ctx["rol"] == "usuario" else "assistant",
                "content": ctx["contenido"]
            })
        mensajes.append({
            "role": "user",
            "content": mensaje
        })
        response = ollama.chat(
            model=modelo,
            messages=mensajes,
            options={
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 200,
            }
        )
        return response['message']['content']

    def _seleccionar_mejor_modelo(self) -> str:
        try:
            modelos_disponibles = ollama.list()
            nombres = [m['name'] for m in modelos_disponibles.get('models', [])]
            preferencias = [
                'llama3.1:8b',
                'llama3.2:3b',
                'llama3:8b',
                'llama3:latest'
            ]
            for modelo in preferencias:
                if modelo in nombres:
                    return modelo
            return 'llama3.2:3b'
        except:
            return 'llama3.2:3b'

    def _formatear_respuesta_herramienta(self, herramienta: str, datos: dict) -> str:
        if herramienta == "clima":
            if "error" in datos:
                return f"No pude obtener el clima: {datos['error']}"
            return (
                f"En {datos['ciudad']}: {datos['temperatura']} "
                f"(sensación de {datos['sensacion']}), {datos['condicion']}. "
                f"Humedad: {datos['humedad']}, viento: {datos['viento']}."
            )
        # ...otros formateadores de herramientas...
        return str(datos)

    def _buscar_patron(self, mensaje_lower: str) -> str:
        patrones = {
            "hola": "¡Hola! ¿En qué puedo ayudarte hoy?",
            "quién eres": "Soy TARS, tu asistente de IA personal.",
            "qué puedes hacer": "Puedo ayudarte con información, cálculos, clima, y más. ¡Pregunta lo que quieras!"
        }
        for patron, respuesta in patrones.items():
            if patron in mensaje_lower:
                return respuesta
        return ""

    def _generar_respuesta_contextual(self, mensaje: str) -> str:
        return f"Recibí tu mensaje: '{mensaje}'. ¿Puedes darme más detalles o contexto?"
