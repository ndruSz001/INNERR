#!/usr/bin/env python3
"""
Prueba simplificada de los sistemas avanzados de personalidad de TARS.
Sin cargar los modelos grandes de IA para enfocarnos en la integración de módulos.
"""

import sys
import os
import json
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sistemas_avanzados():
    """Prueba los sistemas avanzados sin cargar modelos de IA pesados."""
    print("🧪 **PRUEBA SIMPLIFICADA DE SISTEMAS AVANZADOS**")
    print("=" * 60)

    try:
        # Importar solo los módulos avanzados
        from rvc_voice_cloner import RVCVoiceCloner
        from episodic_memory import EpisodicMemory
        from personality_config import PersonalityConfig
        from response_postprocessor import ResponsePostprocessor
        from encrypted_db import EncryptedDatabase

        print("✅ Módulos importados correctamente")

        # Probar EncryptedDatabase
        print("\n🔐 Probando EncryptedDatabase...")
        db = EncryptedDatabase("test_memoria.db")
        print("✅ Base de datos encriptada inicializada")

        # Probar guardar y obtener contexto
        db.guardar_contexto_usuario("test_user", "test_type", "test_key", "test_value")
        context = db.obtener_contexto_usuario("test_user", "test_type")
        print(f"✅ Contexto guardado/obtenido: {len(context)} items")

        # Probar EpisodicMemory
        print("\n🧠 Probando EpisodicMemory...")
        memory = EpisodicMemory("test_user", "test_memoria.db")
        print("✅ Memoria episódica inicializada")

        # Probar guardar conversación
        memory.process_conversation("Hola", "¡Hola! ¿Cómo estás?")
        print("✅ Conversación procesada")

        # Probar obtener contexto
        context = memory.get_context("test_user", "¿Qué tal?")
        print(f"✅ Contexto obtenido: {len(context)} caracteres")

        # Probar PersonalityConfig
        print("\n⚙️ Probando PersonalityConfig...")
        config = PersonalityConfig("test_user")
        settings = config.get_all_settings()  # Usar el método correcto
        print(f"✅ Configuración obtenida: {len(settings)} parámetros")

        # Probar actualizar configuración
        config.set_setting(0.8, "affinity_settings", "emotional_intelligence", "empathy_level")
        config.set_setting(0.7, "affinity_settings", "emotional_intelligence", "humor_level")
        print("✅ Configuración actualizada")

        # Probar ResponsePostprocessor
        print("\n📝 Probando ResponsePostprocessor...")
        processor = ResponsePostprocessor(memory, config, "test_user")
        respuesta = "Hola, soy TARS"
        processed = processor.postprocess_response(respuesta, "Hola TARS")
        print(f"✅ Respuesta procesada: {len(processed)} caracteres")

        # Probar RVCVoiceCloner
        print("\n🎭 Probando RVCVoiceCloner...")
        voice_cloner = RVCVoiceCloner()
        is_trained = voice_cloner.model is not None
        print(f"✅ RVC inicializado (entrenado: {is_trained})")

        # Limpiar archivos de prueba
        if os.path.exists("test_memoria.db"):
            os.remove("test_memoria.db")
        if os.path.exists("db_key.enc"):
            os.remove("db_key.enc")
        print("🧹 Archivos de prueba limpiados")

        return True

    except Exception as e:
        print(f"❌ Error en prueba simplificada: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal de pruebas simplificadas."""
    print("🚀 **PRUEBA SIMPLIFICADA DE SISTEMAS AVANZADOS DE TARS**")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    if test_sistemas_avanzados():
        print("\n" + "=" * 60)
        print("🎉 **PRUEBA SIMPLIFICADA EXITOSA**")
        print("✅ Todos los sistemas avanzados funcionan correctamente")
        print("✅ La integración modular está completa")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ **PRUEBA SIMPLIFICADA FALLIDA**")
        print("Revisa los errores arriba")
        return 1

if __name__ == "__main__":
    sys.exit(main())