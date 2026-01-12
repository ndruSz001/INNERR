#!/usr/bin/env python3
"""
voz_tars.py - Script de Interacción por Voz para TARS
Versión: Exclusiva para Ndrz (2026)
Funcionalidad: Voz a voz con personalidad Jarvis/Interstellar

Características Actuales:
- TTS básico con pyttsx3
- STT con speech_recognition
- Wake Word básico ("Hey TARS")
- Procesamiento local en laptop RTX 3050

Futuras Expansiones (Comentadas):
- TTS avanzado con Piper/Sherpa-ONNX para voz humana
- Reconocimiento de voz familiar (Ndrz, Papá, etc.)
- Integración con clúster de 35 PCs
- Modo Legal/Privado automático
"""

import time
import random
from core_ia import TarsVision

# Inicializar TARS Vision
vision = TarsVision()

# Configuración de voz
WAKE_WORD = "hey tars"  # Palabra de activación (en minúsculas)
USER_ID = "Ndrz"  # Exclusivo para Ndrz por ahora

def saludar():
    """Saludo inicial de TARS"""
    saludos = [
        "¡Hola Ndrz! TARS activado y listo para servir.",
        "Buenos días, compañero. ¿En qué puedo ayudarte hoy?",
        "Sistema operativo. ¿Qué aventura emprendemos?"
    ]
    saludo = random.choice(saludos)
    print(f"TARS: {saludo}")
    # Si existe vision.hablar, usarlo. Si no, solo print (para modo terminal)
    if hasattr(vision, "hablar") and callable(getattr(vision, "hablar")):
        vision.hablar(saludo)
    # else:
    #     Aquí puedes agregar integración de voz en el futuro

def procesar_comando(texto):
    """Procesa el comando de voz y decide acción"""
    texto_lower = texto.lower()

    # Comandos especiales
    if "apagar" in texto_lower or "desactivar" in texto_lower:
        despedida = "Entendido. TARS desconectándose."
        print(f"TARS: {despedida}")
        vision.hablar(despedida)
        return False  # Salir del loop

    # Procesar consulta normal
    respuesta = vision.responder_consulta(texto, USER_ID)
    print(f"TARS: {respuesta}")
    # TTS ya se ejecuta en responder_consulta

    return True  # Continuar

def escuchar_con_wake_word():
    """[DESACTIVADO] Escucha continuamente hasta detectar wake word"""
    print("[VOZ DESACTIVADA] TARS: Solo modo terminal.")
    return False

def main():
    """Loop principal de TARS en modo terminal interactivo"""
    print("[TERMINAL] TARS: Modo compañero activado. Escribe 'salir' para terminar.")
    saludar()
    while True:
        entrada = input("Tú: ").strip()
        if entrada.lower().startswith("listar conversaciones de "):
            nombre_agente = entrada[24:].strip().replace(" ", "_").upper()
            base_path = f"tars_lifelong/biomed_db/{nombre_agente}"
            try:
                import os
                if not os.path.exists(base_path):
                    print(f"TARS: El agente '{nombre_agente}' no existe.")
                    continue
                archivos = os.listdir(base_path)
                convs = [a for a in archivos if a.endswith('.txt') or a.endswith('.md')]
                if convs:
                    print(f"TARS: Conversaciones/memorias en {nombre_agente}:")
                    for archivo in convs:
                        print(f"- {archivo}")
                else:
                    print(f"TARS: No hay conversaciones guardadas en {nombre_agente}.")
            except Exception as e:
                print(f"TARS: Error al listar conversaciones: {e}")
            continue
        if entrada.lower() in ["salir", "apagar", "desactivar"]:
            print("TARS: Hasta luego, Ndrz. Aquí estaré cuando me necesites.")
            break
        if entrada.lower().startswith("crear agente "):
            nombre_agente = entrada[13:].strip().replace(" ", "_").upper()
            base_path = f"tars_lifelong/biomed_db/{nombre_agente}"
            try:
                import os
                os.makedirs(base_path + "/papers", exist_ok=True)
                os.makedirs(base_path + "/datasets", exist_ok=True)
                os.makedirs(base_path + "/protocols", exist_ok=True)
                os.makedirs(base_path + "/contacts", exist_ok=True)
                os.makedirs(base_path + "/results", exist_ok=True)
                os.makedirs(base_path + "/notes", exist_ok=True)
                with open(base_path + "/README.md", "w", encoding="utf-8") as f:
                    f.write(f"# Agente Inteligente: {nombre_agente}\n\nEstructura base para organizar información, memoria y entrenamiento de este agente temático.\n\n## Carpetas sugeridas\n- `papers/` — Artículos y referencias clave\n- `datasets/` — Datos relevantes\n- `protocols/` — Protocolos y procedimientos\n- `contacts/` — Colaboradores\n- `results/` — Resultados y análisis\n- `notes/` — Notas rápidas y aprendizajes\n\nPuedes usar esta estructura para mantener la información organizada y lista para entrenamiento futuro.\n")
                print(f"TARS: Agente '{nombre_agente}' creado con estructura estándar en {base_path}")
            except Exception as e:
                print(f"TARS: Error creando agente: {e}")
            continue
        # Mejorar detección de saludos: acepta variantes y errores comunes
        saludos_clave = ["hola", "buenos días", "buenas", "hey tars", "qué tal", "saludos"]
        entrada_limpia = entrada.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        if any(s in entrada_limpia for s in saludos_clave) or any(s in entrada_limpia for s in ["hol", "hoila", "ola"]):
            respuestas = [
                "¡Hola! ¿Cómo te encuentras hoy?",
                "Aquí estoy, listo para acompañarte.",
                "¿En qué puedo ayudarte o conversar hoy?"
            ]
            respuesta = random.choice(respuestas)
            print(f"TARS: {respuesta}")
            # vision.hablar(respuesta)  # Descomenta para voz en el futuro
            continue
        # Procesar cualquier otro texto como consulta
        if entrada:
            continuar = procesar_comando(entrada)
            if not continuar:
                break
    print("TARS: Sesión terminada.")

if __name__ == "__main__":
    main()

"""
FUTURAS EXPANSIONES (NO IMPLEMENTADAS AÚN):

1. TTS Avanzado:
   - Reemplazar pyttsx3 con Piper o Sherpa-ONNX
   - Instalar: pip install piper-tts onnxruntime-gpu
   - Código ejemplo:
     from piper.voice import PiperVoice
     voice = PiperVoice.load("path/to/model.onnx")
     voice.speak("Texto", "output.wav")  # Usar GPU

2. Reconocimiento de Voz Familiar:
   - Usar speaker diarization (pyannote.audio)
   - Entrenar con voces de familia
   - Código preparado:
     # if voice_id == "Papa":
     #     USER_ID = "Papá_Abogado"
     #     vision.hablar("Modo Legal activado.")

3. Integración con Clúster:
   - Detectar complejidad de tarea
   - Enviar a clúster si > threshold
   - Código preparado:
     # if "analiza resonancia" in texto and len(texto) > 50:
     #     enviar_a_cluster(datos)
     #     vision.hablar("Procesando en clúster...")

4. Seguridad Mejorada:
   - Verificación biométrica de voz
   - Encriptación de audio local
   - Código preparado:
     # if not verificar_voz(voice_sample, USER_ID):
     #     vision.hablar("Acceso denegado.")
"""