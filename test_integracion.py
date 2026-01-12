#!/usr/bin/env python3
"""
Script de prueba para verificar la integración de los sistemas avanzados de personalidad de TARS.
"""

import sys
import os
import json
from datetime import datetime

# Agregar el directorio actual al path para importar módulos locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core_ia import TarsVision

def test_integracion_basica():
    """Prueba básica de inicialización de TARS con todos los sistemas."""
    print("🧪 **INICIANDO PRUEBA DE INTEGRACIÓN BÁSICA**")
    print("=" * 60)

    try:
        # Inicializar TARS
        print("🤖 Inicializando TARS con sistemas avanzados...")
        tars = TarsVision()
        print("✅ TARS inicializado correctamente")

        # Verificar que todos los sistemas estén disponibles
        sistemas = [
            ("Voice Cloner (RVC)", tars.voice_cloner),
            ("Episodic Memory", tars.episodic_memory),
            ("Personality Config", tars.personality_config),
            ("Response Processor", tars.response_processor),
        ]

        print("\n🔍 **VERIFICANDO SISTEMAS:**")
        for nombre, sistema in sistemas:
            if sistema is not None:
                print(f"✅ {nombre}: OK")
            else:
                print(f"❌ {nombre}: FALTA")

        return True

    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        return False

def test_generacion_respuesta():
    """Prueba la generación de respuestas con memoria episódica."""
    print("\n🧪 **PRUEBA DE GENERACIÓN DE RESPUESTAS**")
    print("=" * 60)

    try:
        tars = TarsVision()

        # Usuario de prueba
        user_id = "test_user"

        # Primera conversación
        consulta1 = "Hola TARS, ¿cómo estás?"
        print(f"👤 Usuario: {consulta1}")

        respuesta1 = tars.generar_respuesta_texto(consulta1, user_id=user_id)
        print(f"🤖 TARS: {respuesta1}")

        # Segunda conversación (debería recordar la primera)
        consulta2 = "¿Te acuerdas qué te pregunté antes?"
        print(f"\n👤 Usuario: {consulta2}")

        respuesta2 = tars.generar_respuesta_texto(consulta2, user_id=user_id)
        print(f"🤖 TARS: {respuesta2}")

        # Verificar estadísticas de memoria
        stats = tars.obtener_estadisticas_memoria(user_id)
        print(f"\n{stats}")

        return True

    except Exception as e:
        print(f"❌ Error en generación de respuesta: {e}")
        return False

def test_configuracion_personalidad():
    """Prueba la configuración de personalidad."""
    print("\n🧪 **PRUEBA DE CONFIGURACIÓN DE PERSONALIDAD**")
    print("=" * 60)

    try:
        tars = TarsVision()
        user_id = "test_user"

        # Configurar personalidad
        resultado = tars.configurar_personalidad(
            user_id=user_id,
            afinidad=0.8,
            comunicacion="amigable",
            humor=0.7,
            empatia=0.9
        )
        print(f"⚙️ {resultado}")

        # Verificar configuración
        settings = tars.personality_config.get_settings(user_id)
        print(f"📋 Configuración actual: {json.dumps(settings, indent=2)}")

        return True

    except Exception as e:
        print(f"❌ Error en configuración de personalidad: {e}")
        return False

def test_exportacion_datos():
    """Prueba la exportación e importación de datos."""
    print("\n🧪 **PRUEBA DE EXPORTACIÓN/IMPORTACIÓN DE DATOS**")
    print("=" * 60)

    try:
        tars = TarsVision()
        user_id = "test_user"

        # Agregar algunos datos de prueba
        tars.generar_respuesta_texto("Hola, soy un usuario de prueba", user_id=user_id)
        tars.configurar_personalidad(user_id=user_id, afinidad=0.5)

        # Exportar datos
        resultado_export = tars.exportar_datos_usuario(user_id)
        print(f"📤 {resultado_export}")

        # Extraer nombre del archivo del resultado
        lineas = resultado_export.split('\n')
        archivo_export = None
        for linea in lineas:
            if 'Archivo:' in linea:
                archivo_export = linea.split('Archivo:')[1].strip()
                break

        if archivo_export and os.path.exists(archivo_export):
            print(f"✅ Archivo exportado existe: {archivo_export}")

            # Importar datos en nuevo usuario
            new_user_id = "test_user_restaurado"
            resultado_import = tars.importar_datos_usuario(archivo_export, new_user_id)
            print(f"📥 {resultado_import}")

            # Limpiar archivo de prueba
            os.remove(archivo_export)
            print("🧹 Archivo de prueba eliminado")

            return True
        else:
            print("❌ Archivo de exportación no encontrado")
            return False

    except Exception as e:
        print(f"❌ Error en exportación/importación: {e}")
        return False

def main():
    """Función principal de pruebas."""
    print("🚀 **INICIANDO SUITE DE PRUEBAS DE TARS AVANZADO**")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    pruebas = [
        ("Integración Básica", test_integracion_basica),
        ("Generación de Respuestas", test_generacion_respuesta),
        ("Configuración de Personalidad", test_configuracion_personalidad),
        ("Exportación/Importación", test_exportacion_datos),
    ]

    resultados = []
    for nombre, funcion in pruebas:
        try:
            exito = funcion()
            resultados.append((nombre, exito))
        except Exception as e:
            print(f"❌ Error crítico en {nombre}: {e}")
            resultados.append((nombre, False))

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 **RESUMEN DE PRUEBAS**")
    print("=" * 60)

    exitosas = 0
    for nombre, exito in resultados:
        status = "✅ PASÓ" if exito else "❌ FALLÓ"
        print(f"{status} - {nombre}")
        if exito:
            exitosas += 1

    print(f"\n🏆 **RESULTADO FINAL: {exitosas}/{len(resultados)} pruebas pasaron**")

    if exitosas == len(resultados):
        print("🎉 **¡TODAS LAS PRUEBAS PASARON!** Los sistemas avanzados están listos.")
        return 0
    else:
        print("⚠️ **ALGUNAS PRUEBAS FALLARON.** Revisa los errores arriba.")
        return 1

if __name__ == "__main__":
    sys.exit(main())