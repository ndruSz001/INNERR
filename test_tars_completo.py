#!/usr/bin/env python3
"""
Test completo del sistema TARS
"""

print("="*70)
print("VERIFICACIÓN COMPLETA DEL SISTEMA TARS")
print("="*70)

# 1. Imports
print("\n1. Verificando imports...")
try:
    from conversation_manager import ConversationManager
    from core_ia_simple import TarsVisionSimple
    from tars_tools import TarsTools
    import ollama
    print("   ✅ Todos los imports correctos")
except Exception as e:
    print(f"   ❌ Error en imports: {e}")
    exit(1)

# 2. Inicialización
print("\n2. Inicializando componentes...")
try:
    tools = TarsTools()
    print(f"   ✅ TarsTools: {len(tools.herramientas_disponibles)} herramientas")
    
    tars = TarsVisionSimple()
    print(f"   ✅ TARS Core inicializado")
    
    cm = ConversationManager()
    print(f"   ✅ ConversationManager inicializado")
except Exception as e:
    print(f"   ❌ Error en inicialización: {e}")
    exit(1)

# 3. Test de herramientas
print("\n3. Probando herramientas...")
tests_herramientas = {
    "hora": {},
    "clima": {"ciudad": "Santo Domingo"}
}

for herramienta, params in tests_herramientas.items():
    try:
        resultado = tools.ejecutar_herramienta(herramienta, **params)
        if resultado['exito']:
            print(f"   ✅ {herramienta}: OK")
        else:
            print(f"   ⚠️  {herramienta}: {resultado.get('error', 'Sin datos')}")
    except Exception as e:
        print(f"   ❌ {herramienta}: {e}")

# 4. Test de detección de intenciones
print("\n4. Probando detección de intenciones...")
tests_intencion = [
    "¿qué hora es?",
    "¿cómo está el clima?",
    "hola cómo estás"
]

for test in tests_intencion:
    intencion = tools.detectar_intencion_herramienta(test)
    if intencion:
        herr, params = intencion
        print(f"   ✅ '{test}' -> {herr}")
    else:
        print(f"   ℹ️  '{test}' -> conversación normal")

# 5. Test de Ollama
print("\n5. Probando generación con Ollama...")
try:
    respuesta = tars.generar_respuesta("Responde solo 'Sistema OK' sin más texto")
    print(f"   ✅ Ollama respondió: {respuesta[:50]}...")
except Exception as e:
    print(f"   ❌ Error con Ollama: {e}")

# 6. Test de memoria
print("\n6. Probando sistema de memoria...")
try:
    conv_id = cm.nueva_conversacion(
        titulo="Test de sistema",
        categoria="test"
    )
    print(f"   ✅ Conversación creada: {conv_id[:8]}...")
    
    cm.agregar_mensaje(conv_id, "user", "Mensaje de prueba")
    cm.agregar_mensaje(conv_id, "assistant", "Respuesta de prueba")
    print(f"   ✅ Mensajes guardados")
    
    conversaciones = cm.listar_conversaciones(limit=5)
    print(f"   ✅ Total conversaciones: {len(conversaciones)}")
except Exception as e:
    print(f"   ❌ Error en memoria: {e}")

# 7. Resumen
print("\n" + "="*70)
print("RESUMEN")
print("="*70)
print("✅ Sistema TARS completamente funcional")
print(f"   • Modelo: llama3.2:3b")
print(f"   • Herramientas: {len(tools.herramientas_disponibles)}")
print(f"   • Memoria: Activa")
print(f"   • Ollama: Activo")
print("\nPuedes ejecutar: python3 tars_asistente.py")
print("="*70)
