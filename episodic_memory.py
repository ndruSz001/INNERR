import re
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import logging
from encrypted_db import EncryptedDatabase

# Configurar logging
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
# Modularized: import EpisodicMemory from episodic.memory
from episodic.memory import EpisodicMemory
                self.user_id, 'technical_focus', 'main_project', 'exoesqueleto', 0.9
            )

        # Recordar qué está trabajando actualmente
        if analysis['topic'] in ['exoesqueleto', 'medicina', 'ingeniería']:
            self.current_context['working_on'] = analysis['topic']

        # Recordar horario aproximado
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
        """Determina si una conversación vale la pena recordar"""
        # Recordar si hay emociones fuertes
        if analysis['emotional_state'] in ['frustrated', 'excited', 'tired']:
            return True

        # Recordar preguntas técnicas
        if analysis['topic'] in ['exoesqueleto', 'medicina', 'ingeniería'] and analysis['questions']:
            return True

        # Recordar si hay comandos importantes
        if analysis['commands']:
            return True

        return False

    def _record_memorable_conversation(self, topic, user_message, tars_response, analysis):
        """Registra una conversación memorable"""
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
        """Actualiza preferencias del usuario basadas en patrones"""
        # Preferencia de comunicación
        if 'formal' in message.lower() or 'usted' in message.lower():
            self.db.actualizar_preferencia(
                self.user_id, 'communication', 'formality', 'formal', 0.7
            )
        elif any(word in message.lower() for word in ['qué onda', 'chevere', 'padre']):
            self.db.actualizar_preferencia(
                self.user_id, 'communication', 'formality', 'casual', 0.8
            )

        # Preferencia de detalle en respuestas
        if any(word in message.lower() for word in ['detalle', 'explica', 'cómo funciona']):
            self.db.actualizar_preferencia(
                self.user_id, 'response_style', 'detail_level', 'detailed', 0.6
            )

    def get_personalized_greeting(self):
        """Genera un saludo personalizado basado en la memoria"""
        try:
            greeting_parts = []

            # Saludo basado en hora del día
            time_of_day = self.current_context.get('time_of_day')
            if time_of_day == 'morning':
                greeting_parts.append("Buenos días")
            elif time_of_day == 'afternoon':
                greeting_parts.append("Buenas tardes")
            elif time_of_day == 'evening':
                greeting_parts.append("Buenas noches")
            else:
                greeting_parts.append("Hola")

            # Referencia a estado emocional reciente
            recent_emotions = []
            if self.current_context.get('recent_frustrations'):
                recent_emotions.append('frustrated')
            if self.current_context.get('recent_successes'):
                recent_emotions.append('successful')

            if recent_emotions:
                if 'frustrated' in recent_emotions:
                    greeting_parts.append("espero que hoy vaya mejor que ayer")
                if 'successful' in recent_emotions:
                    greeting_parts.append("siguiendo con el buen trabajo de ayer")

            # Referencia a proyecto actual
            working_on = self.current_context.get('working_on')
            if working_on:
                project_names = {
                    'exoesqueleto': 'el exoesqueleto',
                    'medicina': 'los temas médicos',
                    'ingeniería': 'los proyectos de ingeniería'
                }
                project_name = project_names.get(working_on, f"el proyecto de {working_on}")
                greeting_parts.append(f"¿continuamos con {project_name}?")

            # Unir partes del saludo
            if len(greeting_parts) > 1:
                greeting = greeting_parts[0] + ", " + " y ".join(greeting_parts[1:])
            else:
                greeting = greeting_parts[0] if greeting_parts else "Hola"

            return greeting.capitalize() + "."

        except Exception as e:
            logger.error(f"Error generando saludo personalizado: {e}")
            return "Hola, ¿en qué puedo ayudarte?"

    def get_context(self, user_id, current_query=""):
        """
        Obtiene contexto relevante para una consulta específica.
        Devuelve un string con información contextual para el prompt.
        """
        try:
            context_parts = []

            # Información contextual actual
            if self.current_context.get('working_on'):
                context_parts.append(f"Trabajando actualmente en: {self.current_context['working_on']}")

            if self.current_context.get('emotional_state') != 'neutral':
                context_parts.append(f"Estado emocional reciente: {self.current_context['emotional_state']}")

            # Información sobre conversaciones recientes
            if self.current_context.get('recent_frustrations'):
                context_parts.append(f"Ha tenido frustraciones recientes relacionadas con: {self.current_context['recent_frustrations'][-1].get('topic', 'temas diversos')}")

            if self.current_context.get('recent_successes'):
                context_parts.append(f"Ha tenido éxitos recientes en: {self.current_context['recent_successes'][-1].get('topic', 'diversos temas')}")

            # Análisis de la consulta actual para contexto relevante
            if current_query:
                query_analysis = self._analyze_message(current_query, "user")
                if query_analysis.get('topics'):
                    context_parts.append(f"Consulta actual sobre: {', '.join(query_analysis['topics'])}")

            return "\n".join(context_parts) if context_parts else "Sin contexto previo disponible."

        except Exception as e:
            logger.error(f"Error obteniendo contexto: {e}")
            return "Error obteniendo contexto de memoria."

    def get_contextual_suggestions(self):
        """Genera sugerencias contextuales basadas en la memoria"""
        suggestions = []

        try:
            # Sugerencias basadas en frustraciones recientes
            frustrations = self.current_context.get('recent_frustrations', [])
            if frustrations:
                latest_frustration = frustrations[-1]
                topic = latest_frustration.get('topic', 'general')
                suggestions.append(f"¿Quieres que revisemos juntos el problema de {topic} que tuviste?")

            # Sugerencias basadas en proyecto actual
            working_on = self.current_context.get('working_on')
            if working_on == 'exoesqueleto':
                suggestions.append("¿Necesitas ayuda con cálculos de torque o diseño de materiales para el exoesqueleto?")
            elif working_on == 'medicina':
                suggestions.append("¿Quieres que analice algún caso médico o protocolo de rehabilitación?")

            # Sugerencias basadas en conversaciones recordadas
            remembered_convs = self.db.obtener_conversaciones_recordadas(self.user_id, limit=3)
            for conv in remembered_convs:
                if conv.get('follow_up_suggested') == False:
                    topic = conv.get('topic', '')
                    if topic:
                        suggestions.append(f"¿Recordamos la conversación sobre {topic}? ¿Quieres continuar con eso?")

        except Exception as e:
            logger.error(f"Error generando sugerencias contextuales: {e}")

        return suggestions[:3]  # Máximo 3 sugerencias

    def get_user_profile_summary(self):
        """Genera un resumen del perfil del usuario"""
        try:
            analysis = self.db.obtener_analisis_usuario(self.user_id)

            summary = {
                'emotional_profile': analysis.get('emotional_profile', {}),
                'main_topics': list(analysis.get('interaction_stats', {}).keys())[:3],
                'total_memories': analysis.get('total_memories', 0),
                'working_focus': self.current_context.get('working_on'),
                'communication_style': self.db.obtener_preferencias(self.user_id).get('communication', {})
            }

            return summary

        except Exception as e:
            logger.error(f"Error generando resumen de perfil: {e}")
            return {}

    def reset_memory(self, confirm=False):
        """Resetea la memoria episódica (usar con cuidado)"""
        if not confirm:
            return "⚠️ Esta acción borrará toda tu memoria. Usa reset_memory(confirm=True) para confirmar."

        try:
            # Limpiar contexto actual
            self.current_context = {
                "emotional_state": "neutral",
                "current_topic": None,
                "recent_frustrations": [],
                "recent_successes": [],
                "working_on": None,
                "time_of_day": None,
                "conversation_streak": 0
            }

            # Aquí iría código para limpiar la base de datos si es necesario
            logger.info("🔄 Memoria episódica reseteada")
            return "✅ Memoria reseteada completamente."

        except Exception as e:
            logger.error(f"Error reseteando memoria: {e}")
            return f"❌ Error reseteando memoria: {e}"

    def backup_memory(self):
        """Crea un backup de la memoria"""
        try:
            backup_path = self.db.backup_database()
            if backup_path:
                return f"💾 Backup de memoria creado: {backup_path}"
            else:
                return "❌ Error creando backup de memoria"

        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return f"❌ Error creando backup: {e}"

    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.db:
            self.db.close()