import os
import json
import re
import speech_recognition as sr
from collections import defaultdict, Counter
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import numpy as np
from datetime import datetime
import pickle

# Descargar recursos de NLTK si no existen
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

class PersonalityTrainer:
    """
    Sistema de aprendizaje de personalidad basado en voz y texto.
    Aprende patrones de habla, expresiones, tono y estilo de comunicación.
    """

    def __init__(self, personality_file="personalidad_aprendida.json"):
        self.personality_file = personality_file
        self.voice_patterns = {
            "expresiones_frecuentes": defaultdict(int),
            "estructura_frases": defaultdict(int),
            "tono_emocional": defaultdict(int),
            "vocabulario_preferido": defaultdict(int),
            "longitud_respuestas": [],
            "patrones_conversacion": [],
            "estilo_comunicacion": {
                "formalidad": 0.5,  # 0 = muy informal, 1 = muy formal
                "humor": 0.5,       # 0 = serio, 1 = muy bromista
                "empatia": 0.5,     # 0 = directo, 1 = muy empático
                "detallismo": 0.5   # 0 = conciso, 1 = muy detallado
            }
        }

        self.stop_words_es = set(stopwords.words('spanish'))
        self.cargar_personalidad()

    def cargar_personalidad(self):
        """Carga personalidad aprendida desde archivo"""
        try:
            if os.path.exists(self.personality_file):
                with open(self.personality_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.voice_patterns.update(data)
                print(f"✅ Personalidad cargada desde {self.personality_file}")
            else:
                print("ℹ️ No se encontró archivo de personalidad, empezando desde cero")
        except Exception as e:
            print(f"⚠️ Error cargando personalidad: {e}")

    def guardar_personalidad(self):
        """Guarda personalidad aprendida en archivo"""
        try:
            with open(self.personality_file, 'w', encoding='utf-8') as f:
                json.dump(self.voice_patterns, f, indent=2, ensure_ascii=False)
            print(f"💾 Personalidad guardada en {self.personality_file}")
        except Exception as e:
            print(f"❌ Error guardando personalidad: {e}")

    def procesar_audio_personalidad(self, audio_path, transcripcion_manual=None):
        """
        Procesa un archivo de audio para aprender patrones de personalidad.
        Puede usar transcripción automática o manual.
        """
        try:
            print(f"🎤 Procesando audio de personalidad: {audio_path}")

            # Transcribir audio si no se proporciona transcripción manual
            if transcripcion_manual:
                texto = transcripcion_manual
            else:
                texto = self._transcribir_audio(audio_path)
                if not texto:
                    print("❌ No se pudo transcribir el audio")
                    return False

            # Analizar el texto para patrones de personalidad
            self._analizar_texto_personalidad(texto)

            # Guardar personalidad actualizada
            self.guardar_personalidad()

            print("✅ Audio procesado y personalidad actualizada")
            return True

        except Exception as e:
            print(f"❌ Error procesando audio: {e}")
            return False

    def _transcribir_audio(self, audio_path):
        """Transcribe audio usando speech recognition"""
        try:
            r = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio = r.record(source)

            # Intentar español primero
            try:
                texto = r.recognize_google(audio, language='es-ES')
                return texto
            except sr.UnknownValueError:
                # Intentar inglés como fallback
                try:
                    texto = r.recognize_google(audio, language='en-US')
                    return texto
                except sr.UnknownValueError:
                    return None

        except Exception as e:
            print(f"Error en transcripción: {e}")
            return None

    def _analizar_texto_personalidad(self, texto):
        """Analiza el texto para extraer patrones de personalidad"""

        # Limpiar y tokenizar
        texto = texto.lower().strip()
        oraciones = sent_tokenize(texto, language='spanish')
        palabras = word_tokenize(texto, language='spanish')

        # Filtrar stop words para análisis de vocabulario
        palabras_filtradas = [p for p in palabras if p not in self.stop_words_es and p.isalpha()]

        # 1. Expresiones frecuentes (frases comunes)
        for oracion in oraciones:
            # Buscar expresiones de 2-4 palabras
            tokens = word_tokenize(oracion, language='spanish')
            for i in range(len(tokens) - 1):
                expr_2 = f"{tokens[i]} {tokens[i+1]}"
                self.voice_patterns["expresiones_frecuentes"][expr_2] += 1

                if i < len(tokens) - 2:
                    expr_3 = f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}"
                    self.voice_patterns["expresiones_frecuentes"][expr_3] += 1

        # 2. Estructura de frases
        for oracion in oraciones:
            oracion = oracion.strip()
            if oracion.endswith('?'):
                self.voice_patterns["estructura_frases"]["pregunta"] += 1
            elif oracion.endswith('!'):
                self.voice_patterns["estructura_frases"]["exclamacion"] += 1
            elif any(palabra in oracion.lower() for palabra in ['claro', 'sí', 'exacto', 'por supuesto']):
                self.voice_patterns["estructura_frases"]["afirmacion_enthusiasta"] += 1
            else:
                self.voice_patterns["estructura_frases"]["afirmacion_normal"] += 1

        # 3. Vocabulario preferido
        for palabra in palabras_filtradas:
            if len(palabra) > 3:  # Solo palabras significativas
                self.voice_patterns["vocabulario_preferido"][palabra] += 1

        # 4. Longitud de respuestas
        self.voice_patterns["longitud_respuestas"].append(len(oraciones))

        # 5. Análisis de tono emocional
        texto_lower = texto.lower()
        if any(palabra in texto_lower for palabra in ['genial', 'fantástico', 'increíble', 'maravilloso']):
            self.voice_patterns["tono_emocional"]["enthusiasta"] += 1
        if any(palabra in texto_lower for palabra in ['claro', 'obvio', 'simple', 'fácil']):
            self.voice_patterns["tono_emocional"]["confiado"] += 1
        if any(palabra in texto_lower for palabra in ['entiendo', 'comprendo', 'imagino', 'siento']):
            self.voice_patterns["tono_emocional"]["empatico"] += 1
        if any(palabra in texto_lower for palabra in ['bueno', 'vale', 'ok', 'bien']):
            self.voice_patterns["tono_emocional"]["relajado"] += 1

        # 6. Patrones de conversación
        patrones = self._extraer_patrones_conversacion(texto)
        self.voice_patterns["patrones_conversacion"].extend(patrones)

        # 7. Actualizar estilo de comunicación basado en análisis
        self._actualizar_estilo_comunicacion()

    def _extraer_patrones_conversacion(self, texto):
        """Extrae patrones de conversación del texto"""
        patrones = []

        # Buscar saludos
        if any(palabra in texto.lower() for palabra in ['hola', 'buenos días', 'buenas tardes', 'qué onda', 'qué tal']):
            patrones.append("saludo_amigable")

        # Buscar despedidas
        if any(palabra in texto.lower() for palabra in ['adiós', 'hasta luego', 'nos vemos', 'chau', 'bye']):
            patrones.append("despedida_relajada")

        # Buscar expresiones de duda
        if any(palabra in texto.lower() for palabra in ['mmm', 'bueno', 'pues', 'verás', 'es que']):
            patrones.append("introduccion_reflexiva")

        # Buscar expresiones de acuerdo
        if any(palabra in texto.lower() for palabra in ['claro', 'por supuesto', 'exactamente', 'totalmente']):
            patrones.append("acuerdo_enthusiasta")

        return patrones

    def _actualizar_estilo_comunicacion(self):
        """Actualiza los parámetros de estilo de comunicación basado en el análisis"""

        # Calcular formalidad (basado en expresiones formales vs coloquiales)
        expresiones_formales = sum(self.voice_patterns["expresiones_frecuentes"].get(expr, 0)
                                 for expr in ['por favor', 'disculpe', 'perdón', 'muchas gracias'])
        expresiones_coloquiales = sum(self.voice_patterns["expresiones_frecuentes"].get(expr, 0)
                                    for expr in ['qué onda', 'qué pedo', 'órale', 'chingón', 'chévere'])

        total_expresiones = expresiones_formales + expresiones_coloquiales
        if total_expresiones > 0:
            self.voice_patterns["estilo_comunicacion"]["formalidad"] = expresiones_formales / total_expresiones

        # Calcular humor (basado en expresiones humorísticas)
        expresiones_humor = sum(self.voice_patterns["tono_emocional"].get(tono, 0)
                              for tono in ['enthusiasta', 'confiado'])
        total_analisis = sum(self.voice_patterns["tono_emocional"].values())
        if total_analisis > 0:
            self.voice_patterns["estilo_comunicacion"]["humor"] = expresiones_humor / total_analisis

        # Calcular empatía (basado en expresiones empáticas)
        expresiones_empatia = self.voice_patterns["tono_emocional"].get("empatico", 0)
        if total_analisis > 0:
            self.voice_patterns["estilo_comunicacion"]["empatia"] = expresiones_empatia / total_analisis

        # Calcular detallismo (basado en longitud promedio de respuestas)
        if self.voice_patterns["longitud_respuestas"]:
            avg_longitud = np.mean(self.voice_patterns["longitud_respuestas"])
            # Normalizar: 1 oración = 0.3, 5+ oraciones = 0.9
            self.voice_patterns["estilo_comunicacion"]["detallismo"] = min(1.0, max(0.0, (avg_longitud - 1) / 4))

    def generar_prompt_personalidad(self):
        """Genera un prompt personalizado basado en la personalidad aprendida"""

        estilo = self.voice_patterns["estilo_comunicacion"]

        # Expresiones más frecuentes
        top_expresiones = sorted(self.voice_patterns["expresiones_frecuentes"].items(),
                               key=lambda x: x[1], reverse=True)[:10]
        expresiones_str = ", ".join([f'"{expr}"' for expr, _ in top_expresiones])

        # Vocabulario preferido
        top_vocab = sorted(self.voice_patterns["vocabulario_preferido"].items(),
                          key=lambda x: x[1], reverse=True)[:15]
        vocab_str = ", ".join([palabra for palabra, _ in top_vocab])

        # Patrones de conversación
        patrones_counter = Counter(self.voice_patterns["patrones_conversacion"])
        top_patrones = patrones_counter.most_common(5)
        patrones_str = ", ".join([patron for patron, _ in top_patrones])

        prompt = f"""
        PERSONALIDAD APRENDIDA DEL USUARIO:

        **Estilo de Comunicación:**
        - Formalidad: {estilo['formalidad']:.2f} (0=coloquial, 1=formal)
        - Humor: {estilo['humor']:.2f} (0=serio, 1=bromista)
        - Empatía: {estilo['empatia']:.2f} (0=directo, 1=empático)
        - Detallismo: {estilo['detallismo']:.2f} (0=conciso, 1=detallado)

        **Expresiones Favoritas:** {expresiones_str}
        **Vocabulario Preferido:** {vocab_str}
        **Patrones de Conversación:** {patrones_str}

        **INSTRUCCIONES PARA RESPONDER:**
        - Adapta tu tono al nivel de formalidad aprendido ({estilo['formalidad']:.2f})
        - Incluye expresiones naturales que uses frecuentemente
        - Mantén el nivel de humor y empatía observado
        - Ajusta la longitud de respuesta al detallismo preferido
        - Usa el vocabulario que te es familiar
        - Sigue los patrones de conversación aprendidos

        Recuerda: Habla como hablarías naturalmente, no como una IA formal.
        """

        return prompt

    def obtener_estadisticas_personalidad(self):
        """Retorna estadísticas de la personalidad aprendida"""
        return {
            "total_expresiones_analizadas": len(self.voice_patterns["expresiones_frecuentes"]),
            "total_palabras_vocabulario": len(self.voice_patterns["vocabulario_preferido"]),
            "total_patrones_conversacion": len(self.voice_patterns["patrones_conversacion"]),
            "estilo_actual": self.voice_patterns["estilo_comunicacion"],
            "top_expresiones": dict(sorted(self.voice_patterns["expresiones_frecuentes"].items(),
                                         key=lambda x: x[1], reverse=True)[:5]),
            "top_vocabulario": dict(sorted(self.voice_patterns["vocabulario_preferido"].items(),
                                         key=lambda x: x[1], reverse=True)[:10])
        }

    def resetear_personalidad(self):
        """Resetea toda la personalidad aprendida (usar con cuidado)"""
        self.voice_patterns = {
            "expresiones_frecuentes": defaultdict(int),
            "estructura_frases": defaultdict(int),
            "tono_emocional": defaultdict(int),
            "vocabulario_preferido": defaultdict(int),
            "longitud_respuestas": [],
            "patrones_conversacion": [],
            "estilo_comunicacion": {
                "formalidad": 0.5,
                "humor": 0.5,
                "empatia": 0.5,
                "detallismo": 0.5
            }
        }
        self.guardar_personalidad()
        print("🔄 Personalidad reseteada")