#!/usr/bin/env python3
"""
Script de integración: Cómo modificar core_ia.py para usar Llama.cpp
Mantiene compatibilidad con el código existente.
"""

import os
import sys

def mostrar_cambios_necesarios():
    """Muestra los cambios necesarios en core_ia.py"""

    print("🔧 CAMBIOS NECESARIOS EN core_ia.py")
    print("=" * 50)
    print()

    print("1️⃣ AGREGAR IMPORTACIÓN:")
    print("   from optimizacion_llama import LlamaCppBackend")
    print()

    print("2️⃣ MODIFICAR CONSTRUCTOR (__init__):")
    print("""
   # Después de inicializar otros sistemas...
   try:
       self.llama_backend = LlamaCppBackend()
       self.usar_backend_optimizado = True
       print("✅ Backend Llama.cpp cargado - ¡modo turbo activado!")
   except Exception as e:
       print(f"⚠️ Backend Llama.cpp no disponible: {e}")
       print("🔄 Usando modo estándar...")
       self.llama_backend = None
       self.usar_backend_optimizado = False
   """)

    print("3️⃣ MODIFICAR generar_respuesta_texto():")
    print("""
   def generar_respuesta_texto(self, consulta, contexto="", user_id="default_user"):
       if self.usar_backend_optimizado and self.llama_backend:
           # 🚀 USAR BACKEND C++ OPTIMIZADO
           return self._generar_con_backend_optimizado(consulta, contexto, user_id)
       else:
           # 🐌 USAR BACKEND PYTHON ESTÁNDAR
           return self._generar_con_backend_estandar(consulta, contexto, user_id)
   """)

    print("4️⃣ AGREGAR MÉTODO OPTIMIZADO:")
    print("""
   def _generar_con_backend_optimizado(self, consulta, contexto, user_id):
       try:
           # Obtener contexto de memoria episódica
           memory_context = self.episodic_memory.get_context(user_id, consulta)

           # Obtener personalidad aprendida
           personalidad_prompt = self.personality_trainer.generar_prompt_personalidad()

           # Obtener configuración de personalidad actual
           personality_settings = self.personality_config.get_all_settings()

           # Prompt optimizado para Llama.cpp
           system_prompt = f'''Eres TARS, una IA inteligente y adaptable.

   Tu personalidad se adapta constantemente aprendiendo de conversaciones.

   {personalidad_prompt}

   {memory_context}

   Configuración actual: {personality_settings}

   Responde de manera natural, como hablarías con un amigo cercano.'''

           prompt = f"{system_prompt}\\n\\nUsuario: {consulta}\\nTARS:"

           # ⚡ GENERACIÓN ULTRA-RÁPIDA CON C++
           respuesta = self.llama_backend.generate_response(
               prompt,
               max_tokens=150,  # Más rápido que 200
               temperature=0.7  # Balanceado
           )

           # Limpiar respuesta
           if "TARS:" in respuesta:
               respuesta = respuesta.split("TARS:")[-1].strip()

           # Aplicar post-procesamiento
           respuesta_procesada = self.response_processor.postprocess_response(respuesta, consulta)

           # Guardar en memoria (solo si es significativa)
           if len(respuesta_procesada) > 10:
               self.episodic_memory.process_conversation(consulta, respuesta_procesada)
               self.personality_trainer._analizar_texto_personalidad(respuesta_procesada)
               self.personality_config.update_affinity(user_id, consulta, respuesta_procesada)

           return respuesta_procesada

       except Exception as e:
           print(f"Error en backend optimizado: {e}")
           # Fallback automático
           return self._generar_con_backend_estandar(consulta, contexto, user_id)
   """)

    print("5️⃣ RENOMBRAR MÉTODO EXISTENTE:")
    print("""
   def _generar_con_backend_estandar(self, consulta, contexto, user_id):
       # [Todo el código actual de generar_respuesta_texto]
       # Simplemente copiar y pegar el código existente aquí
   """)

def crear_version_optimizada():
    """Crea una versión optimizada de core_ia.py"""

    print("\\n🔄 CREANDO VERSIÓN OPTIMIZADA...")
    print("Esto creará core_ia_optimizado.py con backend Llama.cpp")

    # Leer archivo original
    try:
        with open('core_ia.py', 'r', encoding='utf-8') as f:
            contenido_original = f.read()
    except FileNotFoundError:
        print("❌ No se encontró core_ia.py")
        return

    # Crear versión modificada
    contenido_optimizado = contenido_original

    # Agregar importación
    import_line = "from optimizacion_llama import LlamaCppBackend\\n"
    if import_line not in contenido_optimizado:
        # Encontrar la línea de imports existente
        lines = contenido_optimizado.split('\\n')
        for i, line in enumerate(lines):
            if line.startswith("from rvc_voice_cloner"):
                lines.insert(i, import_line)
                break
        contenido_optimizado = '\\n'.join(lines)

    # Agregar inicialización en __init__
    init_code = '''
        # Inicializar backend optimizado Llama.cpp
        try:
            self.llama_backend = LlamaCppBackend()
            self.usar_backend_optimizado = True
            print("✅ Backend Llama.cpp cargado - ¡modo turbo activado!")
        except Exception as e:
            print(f"⚠️ Backend Llama.cpp no disponible: {e}")
            print("🔄 Usando modo estándar...")
            self.llama_backend = None
            self.usar_backend_optimizado = False
'''

    # Buscar el final del __init__
    if "print(\\"Modelo LLaVA, Phi-2 y cerebros expertos cargados.\\")" in contenido_optimizado:
        contenido_optimizado = contenido_optimizado.replace(
            "print(\\"Modelo LLaVA, Phi-2 y cerebros expertos cargados.\\")",
            init_code + '\\n        print("Modelo LLaVA, Phi-2 y cerebros expertos cargados.")'
        )

    # Guardar versión optimizada
    with open('core_ia_optimizado.py', 'w', encoding='utf-8') as f:
        f.write(contenido_optimizado)

    print("✅ core_ia_optimizado.py creado")
    print("🔧 Ahora edítalo manualmente para agregar el método _generar_con_backend_optimizado")

def mostrar_comandos_instalacion():
    """Muestra comandos para instalar y configurar"""

    print("\\n📦 COMANDOS DE INSTALACIÓN:")
    print("=" * 40)

    comandos = [
        "# 1. Instalar Llama.cpp",
        "chmod +x instalar_llama.sh",
        "./instalar_llama.sh",
        "",
        "# 2. Descargar modelo Phi-2",
        "huggingface-cli download microsoft/phi-2 --local-dir modelos/phi-2",
        "",
        "# 3. Convertir a GGUF",
        "cd llama.cpp",
        "python convert-hf-to-gguf.py ../modelos/phi-2/",
        "",
        "# 4. Cuantizar a Q4_K_M",
        "./quantize ../modelos/phi-2.gguf ../modelos/phi-2-q4_k_m.gguf Q4_K_M",
        "",
        "# 5. Probar rendimiento",
        "./main -m ../modelos/phi-2-q4_k_m.gguf --prompt \\"Hola TARS\\" -n 50 --gpu-layers 35",
        "",
        "# 6. Integrar con TARS",
        "python integracion_llama.py crear_optimizado"
    ]

    for cmd in comandos:
        print(f"   {cmd}")

if __name__ == "__main__":
    print("🔧 INTEGRACIÓN DE LLAMA.CPP CON TARS")
    print("=" * 50)

    if len(sys.argv) > 1:
        comando = sys.argv[1]

        if comando == "mostrar":
            mostrar_cambios_necesarios()
        elif comando == "crear_optimizado":
            crear_version_optimizada()
        elif comando == "instalar":
            mostrar_comandos_instalacion()
        else:
            print("Comandos: mostrar, crear_optimizado, instalar")
    else:
        print("Uso: python integracion_llama.py [comando]")
        print()
        mostrar_cambios_necesarios()
        print()
        mostrar_comandos_instalacion()