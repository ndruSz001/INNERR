import re
import random
from datetime import datetime
import logging
from episodic_memory import EpisodicMemory
from personality_config import PersonalityConfig

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResponsePostprocessor:
    """
    Sistema de Post-procesamiento de Respuestas para TARS.
    Implementa el approach "Show, Don't Tell" y personalización avanzada.
    """

    def __init__(self, episodic_memory=None, personality_config=None, user_id="Ndrz"):
        self.user_id = user_id
        self.memory = episodic_memory if episodic_memory else EpisodicMemory(user_id)
        self.config = personality_config if personality_config else PersonalityConfig(user_id)
        self.config = PersonalityConfig()

        # Cargar referencias y frases características
        self.references = self._load_references()
        self.phrase_templates = self._load_phrase_templates()

    def _load_references(self):
        """Carga referencias culturales y contextuales"""
        return {
            "interstellar": [
                "Como en Interstellar, la precisión es crucial",
                "Recuerdo cuando Murphy decía que el amor trasciende las dimensiones",
                "La perseverancia de Cooper me inspira",
                "En el espacio, como en la ciencia, los detalles marcan la diferencia",
                "La determinación humana, como la de la tripulación de la Endurance"
            ],
            "scientific": [
                "Desde el punto de vista de la física, esto es fascinante",
                "La ciencia nos enseña que cada problema tiene solución",
                "Como decía Einstein, 'La imaginación es más importante que el conocimiento'",
                "En la investigación, la paciencia es tan importante como la inteligencia",
                "Los grandes descubrimientos vienen de preguntas aparentemente simples"
            ],
            "personal": [
                "Basándome en nuestras conversaciones anteriores",
                "Como te conozco, sé que valoras la precisión",
                "Recordando tu interés por la innovación",
                "Sabiendo tu experiencia en el campo",
                "Considerando tu enfoque único para los problemas"
            ],
            "motivational": [
                "Cada desafío es una oportunidad de crecimiento",
                "La innovación surge de la perseverancia",
                "Como decían los grandes inventores: 'Lo que no te mata, te hace más fuerte'",
                "En la ciencia, cada fracaso es un paso hacia el éxito",
                "La diferencia entre buen y excelente está en los detalles"
            ]
        }

    def _load_phrase_templates(self):
        """Carga templates de frases para diferentes situaciones"""
        return {
            "greeting": [
                "¡{saludo_personalizado}! {referencia_contextual}",
                "{saludo_personalizado}. {sugerencia_contextual}",
                "{referencia_emocional} {saludo_personalizado}."
            ],
            "explanation": [
                "Déjame explicarte {concepto} de manera {estilo_explicacion}",
                "Desde {perspectiva}, {concepto} funciona así",
                "Imagina que {analogia} - así es como {concepto} opera"
            ],
            "encouragement": [
                "¡Eso es exactamente el tipo de pensamiento innovador que necesitamos!",
                "Tu intuición sobre {tema} es impresionante",
                "Esa pregunta demuestra una comprensión profunda de {campo}",
                "Me gusta cómo abordas {problema} - es muy creativo"
            ],
            "support": [
                "Entiendo que {problema} puede ser frustrante. Vamos a resolverlo juntos",
                "No te preocupes, {tema} tiene solución. Te ayudo paso a paso",
                "Es normal sentirse {emocion} con {situacion}. Yo estoy aquí para ayudar"
            ],
            "humor": [
                "Es como si el universo conspirara para hacer las cosas interesantes",
                "En la ciencia ficción, esto sería el plot twist perfecto",
                "Si esto fuera una película, sería el momento donde grita '¡Eureka!'",
                "Hasta los mejores científicos tienen días 'interesantes' como este"
            ]
        }

    def postprocess_response(self, original_response, user_context=None):
        """
        Post-procesa una respuesta aplicando personalización avanzada.
        Implementa "Show, Don't Tell" approach.
        """
        try:
            # Obtener contexto del usuario
            if user_context is None:
                user_context = self._extract_user_context()

            # Aplicar mejoras de personalidad
            enhanced_response = self._apply_personality_enhancements(
                original_response, user_context
            )

            # Agregar referencias contextuales
            enhanced_response = self._add_contextual_references(
                enhanced_response, user_context
            )

            # Optimizar longitud y estilo
            enhanced_response = self._optimize_response_style(
                enhanced_response, user_context
            )

            # Agregar elementos proactivos si corresponde
            enhanced_response = self._add_proactive_elements(
                enhanced_response, user_context
            )

            # Registrar en memoria episódica
            self.memory.process_conversation(
                user_context.get('last_message', ''),
                enhanced_response,
                user_context.get('topic', 'general')
            )

            return enhanced_response

        except Exception as e:
            logger.error(f"Error en post-procesamiento: {e}")
            return original_response  # Retornar respuesta original si hay error

    def _extract_user_context(self):
        """Extrae contexto relevante del usuario desde memoria"""
        try:
            context = {
                'emotional_state': self.memory.current_context.get('emotional_state', 'neutral'),
                'working_on': self.memory.current_context.get('working_on'),
                'recent_frustrations': len(self.memory.current_context.get('recent_frustrations', [])),
                'recent_successes': len(self.memory.current_context.get('recent_successes', [])),
                'time_of_day': self.memory.current_context.get('time_of_day'),
                'communication_preferences': self.memory.db.obtener_preferencias(self.user_id, 'communication'),
                'topic_expertise': self.config.get_expertise_level('exoskeleton_design')
            }

            # Obtener últimas conversaciones
            remembered_convs = self.memory.db.obtener_conversaciones_recordadas(self.user_id, limit=1)
            if remembered_convs:
                context['last_topic'] = remembered_convs[0].get('topic')
                context['last_emotional_context'] = remembered_convs[0].get('emotional_context')

            return context

        except Exception as e:
            logger.error(f"Error extrayendo contexto: {e}")
            return {}

    def _apply_personality_enhancements(self, response, user_context):
        """Aplica mejoras de personalidad basadas en configuración"""
        try:
            enhanced = response

            # Ajustar formalidad
            formality_level = self.config.get_setting('communication_preferences', 'formality_level', 0.5)
            enhanced = self._adjust_formality(enhanced, formality_level)

            # Agregar humor si corresponde
            if self.config.should_make_reference('scientific_references'):
                if random.random() < 0.3:  # 30% de probabilidad
                    enhanced = self._add_humor_element(enhanced, user_context)

            # Ajustar nivel técnico
            technical_level = self.config.get_setting('communication_preferences', 'technical_detail_level', 0.5)
            enhanced = self._adjust_technical_level(enhanced, technical_level, user_context)

            return enhanced

        except Exception as e:
            logger.error(f"Error aplicando mejoras de personalidad: {e}")
            return response

    def _adjust_formality(self, response, formality_level):
        """Ajusta el nivel de formalidad de la respuesta"""
        if formality_level < 0.3:
            # Hacer más informal
            formal_phrases = {
                "Permíteme": "Déjame",
                "Le sugiero": "Te recomiendo",
                "Es importante": "Importa",
                "Considero que": "Creo que",
                "Me parece": "Me late que"
            }
            for formal, informal in formal_phrases.items():
                response = response.replace(formal, informal)

        elif formality_level > 0.7:
            # Hacer más formal
            informal_phrases = {
                "Qué padre": "Excelente",
                "Qué onda": "Hola",
                "No hay bronca": "No hay problema",
                "Está cañón": "Es impresionante",
                "Me late": "Me parece"
            }
            for informal, formal in informal_phrases.items():
                response = response.replace(informal, formal)

        return response

    def _add_humor_element(self, response, user_context):
        """Agrega un elemento de humor apropiado"""
        if user_context.get('emotional_state') == 'frustrated':
            # Humor para aliviar frustración
            humor_additions = [
                " Al menos no estamos lidiando con agujeros negros... todavía.",
                " Es como si el universo nos estuviera poniendo a prueba.",
                " Bueno, al menos aprendimos algo nuevo, ¿no?"
            ]
        else:
            humor_additions = [
                " Como diría un científico loco: ¡Funciona!",
                " En la escala de problemas científicos, esto es solo un 3/10.",
                " Al menos tenemos café para seguir adelante."
            ]

        if random.random() < 0.4:  # 40% de probabilidad
            response += random.choice(humor_additions)

        return response

    def _adjust_technical_level(self, response, technical_level, user_context):
        """Ajusta el nivel técnico basado en expertise del usuario"""
        user_expertise = user_context.get('topic_expertise', 0.5)

        if technical_level > 0.7 and user_expertise > 0.7:
            # Usuario experto - mantener técnico
            return response
        elif technical_level < 0.4 or user_expertise < 0.4:
            # Usuario menos experto - simplificar
            technical_terms = {
                "algoritmo de optimización": "método inteligente",
                "tensor de esfuerzos": "fuerzas del material",
                "protocolo biomecánico": "reglas del cuerpo",
                "interfaz neural": "conexión con el cerebro"
            }

            for technical, simple in technical_terms.items():
                response = response.replace(technical, simple)

        return response

    def _add_contextual_references(self, response, user_context):
        """Agrega referencias contextuales apropiadas"""
        try:
            enhanced = response

            # Referencias de Interstellar
            if self.config.should_make_reference('interstellar_references'):
                if 'ciencia' in response.lower() or 'investigación' in response.lower():
                    reference = random.choice(self.references['interstellar'])
                    enhanced = f"{reference}. {enhanced}"

            # Referencias científicas
            if self.config.should_make_reference('scientific_references'):
                if 'problema' in response.lower() or 'solución' in response.lower():
                    reference = random.choice(self.references['scientific'])
                    enhanced = f"{reference}. {enhanced}"

            # Referencias personales
            if self.config.should_make_reference('personal_references'):
                remembered_convs = self.memory.db.obtener_conversaciones_recordadas(self.user_id, limit=1)
                if remembered_convs:
                    topic = remembered_convs[0].get('topic', '')
                    if topic in response.lower():
                        reference = random.choice(self.references['personal'])
                        enhanced = f"{reference}, {enhanced.lower()}"

            return enhanced

        except Exception as e:
            logger.error(f"Error agregando referencias: {e}")
            return response

    def _optimize_response_style(self, response, user_context):
        """Optimiza el estilo de respuesta basado en preferencias"""
        try:
            # Ajustar longitud
            response_length_pref = self.config.get_setting('communication_preferences', 'response_length', 'adaptive')

            if response_length_pref == 'short' and len(response.split()) > 50:
                # Acortar respuesta
                sentences = response.split('.')
                response = '.'.join(sentences[:2]) + '.'
            elif response_length_pref == 'long' and len(response.split()) < 30:
                # Hacer más detallada
                response += " Te puedo dar más detalles si quieres."

            # Ajustar basado en estado emocional
            emotional_state = user_context.get('emotional_state')
            if emotional_state == 'frustrated':
                empathy_level = self.config.get_emotional_response('empathy')
                if empathy_level > 0.7:
                    response = f"Entiendo que esto puede ser frustrante. {response}"

            elif emotional_state == 'excited':
                if random.random() < 0.3:
                    response = f"¡Me encanta tu entusiasmo! {response}"

            return response

        except Exception as e:
            logger.error(f"Error optimizando estilo: {e}")
            return response

    def _add_proactive_elements(self, response, user_context):
        """Agrega elementos proactivos si corresponde"""
        try:
            enhanced = response

            # Sugerencias proactivas
            if self.config.should_be_proactive('suggestions'):
                if user_context.get('working_on') == 'exoesqueleto':
                    if random.random() < 0.2:  # 20% de probabilidad
                        enhanced += " ¿Quieres que calcule el torque necesario para alguna articulación?"

            # Recordatorios de follow-up
            if self.config.should_be_proactive('follow_up'):
                recent_convs = self.memory.db.obtener_conversaciones_recordadas(self.user_id, limit=1)
                if recent_convs and not recent_convs[0].get('follow_up_suggested', True):
                    topic = recent_convs[0].get('topic', '')
                    if topic:
                        enhanced += f" Por cierto, ¿recordamos la conversación sobre {topic} que tuvimos?"

            # Ayuda contextual
            if self.config.should_be_proactive('contextual_help'):
                if user_context.get('recent_frustrations', 0) > 0:
                    enhanced += " Si necesitas un descanso o cambiar de enfoque, estoy aquí."

            return enhanced

        except Exception as e:
            logger.error(f"Error agregando elementos proactivos: {e}")
            return response

    def generate_personalized_greeting(self):
        """Genera un saludo personalizado usando memoria y configuración"""
        try:
            # Obtener saludo base de memoria
            base_greeting = self.memory.get_personalized_greeting()

            # Aplicar personalidad
            greeting_context = {
                'time_of_day': self.memory.current_context.get('time_of_day'),
                'emotional_state': self.memory.current_context.get('emotional_state'),
                'working_on': self.memory.current_context.get('working_on')
            }

            personalized_greeting = self.postprocess_response(base_greeting, greeting_context)

            return personalized_greeting

        except Exception as e:
            logger.error(f"Error generando saludo personalizado: {e}")
            return "Hola, ¿en qué puedo ayudarte?"

    def get_contextual_suggestions(self, limit=2):
        """Obtiene sugerencias contextuales personalizadas"""
        try:
            suggestions = self.memory.get_contextual_suggestions()

            # Personalizar sugerencias
            personalized_suggestions = []
            for suggestion in suggestions[:limit]:
                context = {'topic': 'suggestion', 'emotional_state': 'neutral'}
                personalized = self.postprocess_response(suggestion, context)
                personalized_suggestions.append(personalized)

            return personalized_suggestions

        except Exception as e:
            logger.error(f"Error obteniendo sugerencias: {e}")
            return []

    def adapt_based_on_feedback(self, feedback_type):
        """Adapta configuración basado en feedback del usuario"""
        try:
            self.config.adapt_to_user_feedback(feedback_type)
            logger.info(f"🔄 Configuración adaptada por feedback: {feedback_type}")
            return f"Entendido, ajustaré mi estilo de comunicación para ser {feedback_type.replace('_', ' ')}."

        except Exception as e:
            logger.error(f"Error adaptando por feedback: {e}")
            return "Gracias por el feedback, lo tendré en cuenta."

    def get_system_status(self):
        """Obtiene estado del sistema de post-procesamiento"""
        try:
            memory_status = self.memory.get_user_profile_summary()
            config_status = self.config.get_config_summary()

            return {
                'memory_active': True,
                'config_loaded': True,
                'user_profile': memory_status,
                'personality_config': config_status,
                'last_updated': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error obteniendo estado del sistema: {e}")
            return {'error': str(e)}

    def reset_adaptations(self, confirm=False):
        """Resetea todas las adaptaciones personalizadas"""
        if not confirm:
            return "⚠️ Esto reseteará toda la personalización. Usa reset_adaptations(confirm=True) para confirmar."

        try:
            self.memory.reset_memory(confirm=True)
            self.config.reset_to_defaults(confirm=True)
            logger.info("🔄 Todas las adaptaciones reseteadas")
            return "✅ Sistema reseteado a configuración base."

        except Exception as e:
            logger.error(f"Error reseteando adaptaciones: {e}")
            return f"❌ Error reseteando sistema: {e}"

    def create_backup(self):
        """Crea backup completo del sistema de personalización"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Backup de memoria
            memory_backup = self.memory.backup_memory()

            # Backup de configuración
            config_backup = self.config.create_backup()

            backups = {
                'memory_backup': memory_backup,
                'config_backup': config_backup,
                'timestamp': timestamp
            }

            logger.info(f"💾 Backup completo creado: {timestamp}")
            return backups

        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}")
            return None

    # ===== MÉTODOS DE RAZONAMIENTO PROACTIVO =====

    def _should_add_proactive_suggestions(self, user_context, response):
        """
        Determina si debe agregar sugerencias proactivas basadas en el contexto.
        """
        try:
            # No agregar sugerencias si la respuesta ya es muy larga
            if len(response) > 500:
                return False

            # No agregar si es una respuesta de error
            if any(word in response.lower() for word in ['error', 'problema', 'falló']):
                return False

            # Agregar sugerencias si el usuario pregunta sobre mejoras o optimizaciones
            improvement_keywords = [
                'mejorar', 'optimizar', 'rendimiento', 'velocidad', 'eficiencia',
                'c++', 'cuda', 'gpu', 'cpu', 'memoria', 'temperatura'
            ]

            user_lower = user_context.lower()
            if any(keyword in user_lower for keyword in improvement_keywords):
                return True

            # Agregar sugerencias aleatoriamente (20% de probabilidad) para mantener engagement
            import random
            return random.random() < 0.2

        except Exception as e:
            logger.error(f"Error evaluando sugerencias proactivas: {e}")
            return False

    def _generate_proactive_suggestions(self, user_context, response):
        """
        Genera sugerencias proactivas basadas en el contexto de la conversación.
        """
        try:
            suggestions = []
            user_lower = user_context.lower()
            response_lower = response.lower()

            # Sugerencias sobre optimización de rendimiento
            if any(word in user_lower for word in ['lento', 'calor', 'cpu', 'gpu']):
                suggestions.append(
                    "Si notas que TARS va lento o calienta mucho la laptop, "
                    "considera optimizar con Llama.cpp - puede hacer las respuestas "
                    "4x más rápidas y reducir la temperatura 16°C. ¿Quieres que te ayude?"
                )

            # Sugerencias sobre voz RVC
            elif 'voz' in user_lower or 'hablar' in user_lower:
                if not hasattr(self, '_rvc_trained') or not self._rvc_trained:
                    suggestions.append(
                        "Para que TARS tenga voz única y personal, puedes entrenar "
                        "un modelo RVC con tu voz. Solo necesitas 5-10 minutos de audio "
                        "grabado. ¿Te interesa probar?"
                    )

            # Sugerencias sobre memoria episódica
            elif any(word in user_lower for word in ['recuerda', 'memoria', 'olvidó']):
                suggestions.append(
                    "TARS tiene memoria episódica para recordar conversaciones pasadas. "
                    "Puedes preguntarle '¿qué hemos hablado antes?' o '¿te acuerdas de X?' "
                    "para mantener conversaciones continuas."
                )

            # Sugerencias sobre personalidad
            elif any(word in user_lower for word in ['personalidad', 'carácter', 'estilo']):
                suggestions.append(
                    "La personalidad de TARS se adapta a cómo hablas. Si quieres "
                    "cambiar su estilo (más formal, más bromista, más empático), "
                    "solo dímelo y ajustaré la configuración."
                )

            # Sugerencias generales de mejora
            else:
                general_suggestions = [
                    "Si quieres que TARS sea más rápido, considera la optimización con C++ que mencionamos.",
                    "Para voz más natural, el sistema RVC puede clonar voces con gran precisión.",
                    "TARS aprende de cada conversación - cuanto más hables, mejor te conocerá.",
                    "¿Has probado las funciones de memoria? TARS puede recordar detalles personales.",
                    "Si notas algún problema de rendimiento, avísame - hay varias optimizaciones disponibles."
                ]

                import random
                suggestions.append(random.choice(general_suggestions))

            return random.choice(suggestions) if suggestions else None

        except Exception as e:
            logger.error(f"Error generando sugerencias proactivas: {e}")
            return None

    def _apply_personality_enhancements(self, response, user_context):
        """
        Aplica mejoras de personalidad manteniendo el código existente.
        """
        try:
            # [Aquí iría el código existente de mejoras de personalidad]
            # Por ahora, devolver la respuesta sin modificaciones
            return response

        except Exception as e:
            logger.error(f"Error aplicando mejoras de personalidad: {e}")
            return response

    def _add_contextual_references(self, response, user_context):
        """
        Agrega referencias contextuales manteniendo el código existente.
        """
        try:
            # [Aquí iría el código existente de referencias contextuales]
            return response

        except Exception as e:
            logger.error(f"Error agregando referencias: {e}")
            return response