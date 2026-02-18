
"""
memory.py
Sistema de Memoria Episódica para TARS.
Recuerda experiencias, preferencias y contexto del usuario a largo plazo.

Ejemplo de uso:
    from episodic.memory import EpisodicMemory
    mem = EpisodicMemory(user_id="usuario")
    mem.guardar_evento("inicio_sesion", {"hora": "10:00"})
    print(mem.obtener_contexto_actual())
"""

import re
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import logging
from encrypted_db import EncryptedDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EpisodicMemory:
    """
    Sistema de Memoria Episódica para TARS
    Recuerda experiencias, preferencias y contexto del usuario a largo plazo.
    """
    def __init__(self, user_id="Ndrz", db_path="memoria_episodica.db"):
        self.user_id = user_id
        self.db = EncryptedDatabase(db_path)
        self.current_context = {
            "emotional_state": "neutral",
            "current_topic": None,
            "recent_frustrations": [],
            "recent_successes": [],
            "working_on": None,
            "time_of_day": None,
            "conversation_streak": 0
        }
        self._load_current_context()
    def _load_current_context(self):
        try:
            context_data = self.db.obtener_contexto_usuario(
                self.user_id, "current_session", limit=20
            )
            for item in context_data:
                key = item['key']
                value = item['value']
                if key in self.current_context:
                    if isinstance(self.current_context[key], list):
                        if isinstance(value, str):
                            try:
                                self.current_context[key] = json.loads(value)
                            except:
                                self.current_context[key] = [value]
                        else:
                            self.current_context[key] = value
                    else:
                        self.current_context[key] = value
            logger.debug("✅ Contexto actual cargado")
        except Exception as e:
            logger.error(f"Error cargando contexto: {e}")
    def _save_current_context(self):
        try:
            for key, value in self.current_context.items():
                if isinstance(value, list):
                    value_to_save = json.dumps(value)
                else:
                    value_to_save = str(value)
                self.db.guardar_contexto_usuario(
                    self.user_id, "current_session", key, value_to_save,
                    relevance_score=0.9, expires_days=7
                )
        except Exception as e:
            logger.error(f"Error guardando contexto: {e}")
    def process_conversation(self, user_message, tars_response, conversation_topic=None):
        try:
            user_analysis = self._analyze_message(user_message, "user")
            tars_analysis = self._analyze_message(tars_response, "tars")
            self._update_emotional_context(user_analysis, tars_analysis)
            self._extract_important_info(user_message, user_analysis)
            if self._is_conversation_memorable(user_analysis):
                self._record_memorable_conversation(
                    conversation_topic or user_analysis.get('topic', 'general'),
                    user_message, tars_response, user_analysis
                )
            self._update_user_preferences(user_message, user_analysis)
            self.db.log_interaction(
                self.user_id, "conversation",
                user_message, tars_response
            )
            self._save_current_context()
        except Exception as e:
            logger.error(f"Error procesando conversación: {e}")
    def _analyze_message(self, message, sender):
        analysis = {
            'emotional_state': self._detect_emotion(message),
            'topics': self._extract_topics(message),
            'urgency': self._detect_urgency(message),
            'sentiment': self._analyze_sentiment(message),
            'questions': self._extract_questions(message),
            'commands': self._extract_commands(message),
            'topic': self._identify_main_topic(message)
        }
        return analysis
    def _detect_emotion(self, message):
        message_lower = message.lower()
        emotion_patterns = {
            'frustrated': ['frustrado', 'frustración', 'no funciona', 'problema', 'error', 'odio'],
            'excited': ['genial', 'increíble', 'fantástico', 'emocionado', 'wow', 'impresionante'],
            'tired': ['cansado', 'agotado', 'exhausto', 'no puedo más', 'necesito descansar'],
            'confused': ['confundido', 'no entiendo', 'complicado', 'difícil', 'perdido'],
            'satisfied': ['bien', 'funciona', 'solucionado', 'perfecto', 'excelente'],
            'concerned': ['preocupado', 'inquieto', 'miedo', 'riesgo', 'peligro'],
            'motivated': ['quiero', 'vamos', 'adelante', 'continuar', 'probar']
        }
        for emotion, patterns in emotion_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return emotion
        return 'neutral'
    def _analyze_sentiment(self, message):
        positive_words = ['bueno', 'bien', 'genial', 'excelente', 'perfecto', 'feliz', 'contento']
        negative_words = ['malo', 'terrible', 'horrible', 'frustrado', 'enojado', 'triste']
        message_lower = message.lower()
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    def _extract_questions(self, message):
        questions = []
        sentences = re.split(r'[.!?]+', message)
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence.endswith('?'):
                questions.append(sentence)
        return questions
    def _extract_commands(self, message):
        commands = []
        command_patterns = [
            r'entrenar\s+\w+',
            r'calcular\s+.+',
            r'analizar\s+.+',
            r'mostrar\s+.+',
            r'crear\s+.+',
            r'ejecutar\s+.+'
        ]
        for pattern in command_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            commands.extend(matches)
        return commands
    def _identify_main_topic(self, message):
        topics = self._extract_topics(message)
        if topics:
            return topics[0]
        if '?' in message:
            return 'question'
        elif any(word in message.lower() for word in ['entrenar', 'calcular', 'analizar']):
            return 'technical_request'
        else:
            return 'general_conversation'
    def _extract_topics(self, message):
        # Placeholder: implement NLP topic extraction
        return []
    def _detect_urgency(self, message):
        # Placeholder: implement urgency detection
        return 'normal'
    def _update_emotional_context(self, user_analysis, tars_analysis):
        if user_analysis['emotional_state'] != 'neutral':
            self.current_context['emotional_state'] = user_analysis['emotional_state']
            if user_analysis['emotional_state'] == 'frustrated':
                self.current_context['recent_frustrations'].append({
                    'topic': user_analysis.get('topic', 'unknown'),
                    'timestamp': datetime.now().isoformat()
                })
                self.current_context['recent_frustrations'] = self.current_context['recent_frustrations'][-5:]
            elif user_analysis['emotional_state'] in ['satisfied', 'excited']:
                self.current_context['recent_successes'].append({
                    'topic': user_analysis.get('topic', 'unknown'),
                    'timestamp': datetime.now().isoformat()
                })
                self.current_context['recent_successes'] = self.current_context['recent_successes'][-5:]
    def _extract_important_info(self, message, analysis):
        if 'exoesqueleto' in analysis['topics']:
            self.db.actualizar_preferencia(
                self.user_id, 'technical_focus', 'main_project', 'exoesqueleto', 0.9
            )
        if analysis['topic'] in ['exoesqueleto', 'medicina', 'ingeniería']:
            self.current_context['working_on'] = analysis['topic']
        current_hour = datetime.now().hour
        if 6 <= current_hour < 12:
            self.current_context['time_of_day'] = 'morning'
        elif 12 <= current_hour < 18:
            self.current_context['time_of_day'] = 'afternoon'
        elif 18 <= current_hour < 22:
            self.current_context['time_of_day'] = 'evening'
        else:
            self.current_context['time_of_day'] = 'night'
    def _is_conversation_memorable(self, analysis):
        if analysis['emotional_state'] in ['frustrated', 'excited', 'tired']:
            return True
        if analysis['topic'] in ['exoesqueleto', 'medicina', 'ingeniería'] and analysis['questions']:
            return True
        if analysis['commands']:
            return True
        return False
    def _record_memorable_conversation(self, topic, user_message, tars_response, analysis):
        key_points = f"Usuario expresó: {analysis['emotional_state']} sobre {topic}"
        if analysis['questions']:
            key_points += f". Preguntó: {'; '.join(analysis['questions'][:2])}"
        if analysis['commands']:
            key_points += f". Solicitó: {'; '.join(analysis['commands'][:2])}"
        self.db.recordar_conversacion(
            self.user_id, topic, key_points,
            emotional_context=analysis['emotional_state'],
            user_mood=analysis['sentiment']
        )
    def _update_user_preferences(self, message, analysis):
        if 'formal' in message.lower() or 'usted' in message.lower():
            self.db.actualizar_preferencia(
                self.user_id, 'communication', 'formality', 'formal', 0.7
            )
        elif any(word in message.lower() for word in ['qué onda', 'chevere', 'padre']):
            self.db.actualizar_preferencia(
                self.user_id, 'communication', 'formality', 'casual', 0.8
            )
        if any(word in message.lower() for word in ['detalle', 'explica', 'cómo funciona']):
            self.db.actualizar_preferencia(
                self.user_id, 'response_style', 'detail_level', 'detailed', 0.6
            )
    # ... (rest of EpisodicMemory methods from episodic_memory.py)
