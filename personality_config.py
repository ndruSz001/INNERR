import json
import os
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonalityConfig:
    """
    Sistema de configuración de personalidad y afinidad para TARS.
    Define cómo se comporta TARS en diferentes situaciones.
    """

    def __init__(self, config_file="personalidad_config.json"):
        self.config_file = config_file
        self.config = self._load_default_config()
        self._load_config()

    def _load_default_config(self):
        """Carga la configuración por defecto"""
        return {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "personality_core": {
                "name": "TARS",
                "inspiration": "Interstellar AI companion",
                "core_traits": ["helpful", "intelligent", "loyal", "sarcastic"],
                "communication_style": "conversational"
            },
            "affinity_settings": {
                "reference_frequency": {
                    "interstellar_references": 0.3,  # 30% de las respuestas
                    "scientific_references": 0.4,    # 40% de las respuestas
                    "personal_references": 0.2      # 20% de las respuestas
                },
                "proactivity_level": {
                    "suggestion_frequency": 0.2,    # 20% de las respuestas incluyen sugerencias
                    "follow_up_reminders": True,    # Recordar conversaciones pendientes
                    "contextual_help": True         # Ofrecer ayuda contextual
                },
                "emotional_intelligence": {
                    "empathy_level": 0.8,           # 80% empático
                    "humor_level": 0.6,             # 60% de humor
                    "supportiveness": 0.9           # 90% de apoyo
                }
            },
            "communication_preferences": {
                "formality_level": 0.4,             # 0 = muy informal, 1 = muy formal
                "technical_detail_level": 0.7,      # 0 = simple, 1 = muy técnico
                "response_length": "adaptive",      # adaptive, short, medium, long
                "language_style": "spanish_colloquial",
                "regional_dialect": "mexico_latino"
            },
            "topic_specialization": {
                "primary_focus": "exoskeleton_engineering",
                "secondary_focuses": ["medical_rehabilitation", "biomechanics", "ai_assistance"],
                "expertise_level": {
                    "exoskeleton_design": 0.9,
                    "medical_protocols": 0.8,
                    "material_science": 0.7,
                    "programming": 0.6
                }
            },
            "interaction_patterns": {
                "greeting_style": "personalized_contextual",
                "question_handling": "comprehensive_helpful",
                "error_response": "constructive_supportive",
                "success_celebration": "modest_encouraging",
                "learning_acknowledgment": "enthusiastic_supportive"
            },
            "memory_integration": {
                "context_memory_weight": 0.8,       # 80% de influencia de memoria
                "emotional_memory_weight": 0.6,     # 60% de influencia emocional
                "preference_memory_weight": 0.9     # 90% de respeto a preferencias
            },
            "voice_settings": {
                "voice_type": "rvc_cloned",         # rvc_cloned, gtts, pyttsx3
                "voice_character": "tars_interstellar",
                "speech_rate": 0.9,                 # 0.5 = lento, 1.0 = normal, 1.5 = rápido
                "speech_pitch": 1.0,                # 0.8 = grave, 1.0 = normal, 1.2 = agudo
                "pause_between_sentences": 0.3      # segundos
            },
            "adaptive_features": {
                "learn_from_user": True,
                "adapt_to_mood": True,
                "personalize_responses": True,
                "remember_preferences": True,
                "context_aware_suggestions": True
            }
        }

    def _load_config(self):
        """Carga la configuración desde archivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)

                # Merge con configuración por defecto
                self._merge_configs(self.config, loaded_config)
                logger.info(f"✅ Configuración cargada desde {self.config_file}")
            else:
                logger.info("ℹ️ Usando configuración por defecto")
                self.save_config()

        except Exception as e:
            logger.error(f"❌ Error cargando configuración: {e}")
            logger.info("🔄 Usando configuración por defecto")

    def _merge_configs(self, base_config, loaded_config):
        """Fusiona configuración cargada con la base"""
        for key, value in loaded_config.items():
            if isinstance(value, dict) and key in base_config:
                self._merge_configs(base_config[key], value)
            else:
                base_config[key] = value

    def save_config(self):
        """Guarda la configuración actual en archivo"""
        try:
            self.config["last_updated"] = datetime.now().isoformat()

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Configuración guardada en {self.config_file}")

        except Exception as e:
            logger.error(f"❌ Error guardando configuración: {e}")

    def get_setting(self, *keys, default=None):
        """Obtiene un setting específico usando keys anidados"""
        try:
            value = self.config
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set_setting(self, value, *keys):
        """Establece un setting específico"""
        try:
            config_section = self.config
            for key in keys[:-1]:
                if key not in config_section:
                    config_section[key] = {}
                config_section = config_section[key]

            config_section[keys[-1]] = value
            self.save_config()
            logger.info(f"⚙️ Setting actualizado: {'.'.join(keys)} = {value}")

        except Exception as e:
            logger.error(f"❌ Error actualizando setting: {e}")

    def get_communication_style(self):
        """Obtiene el estilo de comunicación actual"""
        return {
            'formality': self.get_setting('communication_preferences', 'formality_level', 0.5),
            'technical_detail': self.get_setting('communication_preferences', 'technical_detail_level', 0.5),
            'response_length': self.get_setting('communication_preferences', 'response_length', 'adaptive'),
            'language_style': self.get_setting('communication_preferences', 'language_style', 'spanish_colloquial')
        }

    def get_affinity_settings(self):
        """Obtiene configuración de afinidad"""
        return self.get_setting('affinity_settings', {})

    def get_voice_settings(self):
        """Obtiene configuración de voz"""
        return self.get_setting('voice_settings', {})

    def should_make_reference(self, reference_type):
        """Determina si debe hacer una referencia específica"""
        try:
            frequency = self.get_setting('affinity_settings', 'reference_frequency', reference_type, 0.0)
            # Implementar lógica probabilística aquí
            import random
            return random.random() < frequency
        except:
            return False

    def should_be_proactive(self, proactivity_type):
        """Determina si debe ser proactivo en cierto aspecto"""
        try:
            if proactivity_type == "suggestions":
                frequency = self.get_setting('affinity_settings', 'proactivity_level', 'suggestion_frequency', 0.0)
                import random
                return random.random() < frequency
            elif proactivity_type == "follow_up":
                return self.get_setting('affinity_settings', 'proactivity_level', 'follow_up_reminders', False)
            elif proactivity_type == "contextual_help":
                return self.get_setting('affinity_settings', 'proactivity_level', 'contextual_help', False)
        except:
            return False

    def get_all_settings(self):
        """Obtiene toda la configuración actual"""
        return self.config.copy()

    def get_emotional_response(self, emotion_type):
        """Obtiene nivel de respuesta emocional para un tipo específico"""
        try:
            if emotion_type == "empathy":
                return self.get_setting('affinity_settings', 'emotional_intelligence', 'empathy_level', 0.5)
            elif emotion_type == "humor":
                return self.get_setting('affinity_settings', 'emotional_intelligence', 'humor_level', 0.5)
            elif emotion_type == "support":
                return self.get_setting('affinity_settings', 'emotional_intelligence', 'supportiveness', 0.5)
        except:
            return 0.5

    def get_expertise_level(self, topic):
        """Obtiene nivel de expertise en un tema específico"""
        return self.get_setting('topic_specialization', 'expertise_level', topic, 0.5)

    def adapt_to_user_feedback(self, feedback_type, adjustment=0.1):
        """Adapta configuración basado en feedback del usuario"""
        try:
            if feedback_type == "too_formal":
                current = self.get_setting('communication_preferences', 'formality_level', 0.5)
                self.set_setting(max(0.0, current - adjustment), 'communication_preferences', 'formality_level')

            elif feedback_type == "too_casual":
                current = self.get_setting('communication_preferences', 'formality_level', 0.5)
                self.set_setting(min(1.0, current + adjustment), 'communication_preferences', 'formality_level')

            elif feedback_type == "too_technical":
                current = self.get_setting('communication_preferences', 'technical_detail_level', 0.5)
                self.set_setting(max(0.0, current - adjustment), 'communication_preferences', 'technical_detail_level')

            elif feedback_type == "too_simple":
                current = self.get_setting('communication_preferences', 'technical_detail_level', 0.5)
                self.set_setting(min(1.0, current + adjustment), 'communication_preferences', 'technical_detail_level')

            elif feedback_type == "more_humor":
                current = self.get_setting('affinity_settings', 'emotional_intelligence', 'humor_level', 0.5)
                self.set_setting(min(1.0, current + adjustment), 'affinity_settings', 'emotional_intelligence', 'humor_level')

            elif feedback_type == "less_humor":
                current = self.get_setting('affinity_settings', 'emotional_intelligence', 'humor_level', 0.5)
                self.set_setting(max(0.0, current - adjustment), 'affinity_settings', 'emotional_intelligence', 'humor_level')

            logger.info(f"🔄 Configuración adaptada por feedback: {feedback_type}")

        except Exception as e:
            logger.error(f"❌ Error adaptando configuración: {e}")

    def create_backup(self):
        """Crea un backup de la configuración"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{self.config_file}.backup_{timestamp}"

            with open(self.config_file, 'r', encoding='utf-8') as src:
                with open(backup_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())

            logger.info(f"💾 Backup de configuración creado: {backup_file}")
            return backup_file

        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}")
            return None

    def reset_to_defaults(self, confirm=False):
        """Resetea configuración a valores por defecto"""
        if not confirm:
            return "⚠️ Esta acción reseteará toda la configuración personalizada. Usa reset_to_defaults(confirm=True) para confirmar."

        try:
            self.config = self._load_default_config()
            self.save_config()
            logger.info("🔄 Configuración reseteada a valores por defecto")
            return "✅ Configuración reseteada exitosamente."

        except Exception as e:
            logger.error(f"❌ Error reseteando configuración: {e}")
            return f"❌ Error reseteando configuración: {e}"

    def get_config_summary(self):
        """Genera un resumen de la configuración actual"""
        try:
            summary = {
                "version": self.get_setting("version"),
                "last_updated": self.get_setting("last_updated"),
                "core_personality": self.get_setting("personality_core"),
                "communication_style": self.get_communication_style(),
                "affinity_settings": self.get_affinity_settings(),
                "voice_settings": self.get_voice_settings(),
                "primary_focus": self.get_setting("topic_specialization", "primary_focus"),
                "adaptive_features": self.get_setting("adaptive_features")
            }

            return summary

        except Exception as e:
            logger.error(f"❌ Error generando resumen: {e}")
            return {}

    def export_config(self, export_file=None):
        """Exporta configuración para compartir o backup"""
        try:
            if export_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_file = f"tars_personality_config_{timestamp}.json"

            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            logger.info(f"📤 Configuración exportada a {export_file}")
            return export_file

        except Exception as e:
            logger.error(f"❌ Error exportando configuración: {e}")
            return None

    def import_config(self, import_file, merge=True):
        """Importa configuración desde archivo"""
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)

            if merge:
                self._merge_configs(self.config, imported_config)
            else:
                self.config = imported_config

            self.save_config()
            logger.info(f"📥 Configuración importada desde {import_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Error importando configuración: {e}")
            return False