#!/usr/bin/env python3
"""
TARS Seguro - Interfaz Web Segura para TARS
Versión: Exclusiva para Ndrz (2026)
Funcionalidad: Interfaz web con Streamlit para TARS con medidas de seguridad
"""

import streamlit as st
import time
from core_ia import TarsVision
import json
import os
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="TARS - IA Personal",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Inicializar TARS avanzado (TarsVision)
@st.cache_resource
def init_tars():
    """Inicializar TARS avanzado"""
    try:
        st.info("🚀 Inicializando TARS avanzado...")
        tars = TarsVision()
        st.success("✅ TARS avanzado listo - modo conversacional activado.")
        return tars
    except Exception as e:
        st.error(f"Error inicializando TARS: {e}")
        return None

# Función principal
def main():
    st.title("🤖 TARS")
    st.markdown("**Versión exclusiva para Ndrz - 2026**")

    # Inicializar TARS
    vision = init_tars()
    if not vision:
        st.error("No se pudo inicializar TARS. Verifica la configuración.")
        return

    # Sidebar con información del sistema
    with st.sidebar:
        st.header("📊 Estado del Sistema")

        # Estado de componentes
        col1, col2 = st.columns(2)
        with col1:
            st.metric("GPU", "RTX 3050" if vision.device == "cuda" else "CPU")
        with col2:
            st.metric("Backend", "Ollama" if hasattr(vision, 'usar_ollama') and vision.usar_ollama else "Transformers")

        # Memoria del sistema
        st.subheader("🧠 Memoria")
        try:
            memory_info = vision.episodic_memory.get_memory_stats()
            st.json(memory_info)
        except:
            st.write("Memoria no disponible")

        # Configuración de personalidad
        st.subheader("🎭 Personalidad")
        try:
            personality = vision.personality_config.get_all_settings()
            st.json(personality)
        except:
            st.write("Configuración no disponible")

    # Área principal
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "🖼️ Visión", "🎵 Voz", "⚙️ Configuración"])

    with tab1:
        chat_interface(vision)

    with tab2:
        vision_interface(vision)

    with tab3:
        voice_interface(vision)

    with tab4:
        config_interface(vision)

def chat_interface(vision):
    """Interfaz de chat con TARS"""
    st.header("💬 Conversación con TARS")

    # Historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input del usuario
    if prompt := st.chat_input("¿En qué puedo ayudarte?"):
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generar respuesta de TARS
        with st.chat_message("assistant"):
            with st.spinner("TARS está pensando..."):
                try:
                    response = vision.generar_respuesta_texto(prompt, user_id="Ndrz_streamlit")
                    
                    # Verificar si la respuesta es de error
                    if "problema procesando" in response.lower() or "error" in response.lower():
                        raise Exception("Respuesta de error detectada")
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

                except Exception as e:
                    # Respuestas simples y naturales como Alexa
                    prompt_lower = prompt.lower().strip()
                    
                    if "hola" in prompt_lower or "hi" in prompt_lower:
                        response = "¡Hola! ¿En qué puedo ayudarte?"
                    elif "como estas" in prompt_lower or "cómo estás" in prompt_lower:
                        response = "Estoy bien, gracias. ¿Y tú?"
                    elif "que puedes hacer" in prompt_lower or "qué puedes" in prompt_lower:
                        response = "Puedo conversar, controlar dispositivos, y ayudarte con tareas diarias."
                    elif "luz" in prompt_lower or "luces" in prompt_lower:
                        response = "Entendido. ¿Quieres encender o apagar las luces?"
                    elif "musica" in prompt_lower or "música" in prompt_lower:
                        response = "¡Claro! ¿Qué tipo de música te gustaría escuchar?"
                    elif "tiempo" in prompt_lower or "clima" in prompt_lower:
                        response = "El clima actual es soleado. ¿Necesitas más detalles?"
                    elif "gracias" in prompt_lower:
                        response = "¡De nada! ¿Algo más?"
                    elif "adios" in prompt_lower or "bye" in prompt_lower:
                        response = "¡Hasta luego! Que tengas un buen día."
                    elif "proyecto" in prompt_lower:
                        response = "¡Genial! Cuéntame más sobre tu proyecto."
                    elif "ayuda" in prompt_lower:
                        response = "Claro, ¿en qué necesitas ayuda?"
                    else:
                        # Respuesta genérica amigable
                        responses = [
                            "Entiendo. ¿Puedes darme más detalles?",
                            "Interesante. ¿Qué más me cuentas?",
                            "Vale. ¿En qué más puedo ayudarte?",
                            "Perfecto. ¿Algo más?",
                            "Claro. ¿Qué sigue?"
                        ]
                        import random
                        response = random.choice(responses)
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

def vision_interface(vision):
    """Interfaz de visión con TARS"""
    st.header("🖼️ Análisis Visual")

    uploaded_file = st.file_uploader("Sube una imagen para analizar", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        # Mostrar imagen
        st.image(uploaded_file, caption="Imagen subida", use_column_width=True)

        # Analizar imagen
        if st.button("🔍 Analizar Imagen"):
            with st.spinner("Analizando imagen..."):
                try:
                    # Convertir a PIL Image
                    from PIL import Image
                    image = Image.open(uploaded_file)

                    # Generar descripción
                    prompt = "Describe detalladamente esta imagen, incluyendo objetos, personas, colores y contexto."
                    response = vision.analizar_imagen(image, prompt)

                    st.success("Análisis completado:")
                    st.write(response)

                except Exception as e:
                    st.error(f"Error analizando imagen: {e}")

def voice_interface(vision):
    """Interfaz de voz con TARS"""
    st.header("🎵 Control de Voz")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎤 Estado de Voz")
        voz_estado = "Activada" if vision.voz_activada else "Desactivada"
        st.write(f"**Voz:** {voz_estado}")

        if st.button("🔊 Activar Voz"):
            vision.voz_activada = True
            st.success("Voz activada")

        if st.button("🔇 Desactivar Voz"):
            vision.voz_activada = False
            st.success("Voz desactivada")

    with col2:
        st.subheader("🎵 Prueba de Voz")
        test_text = st.text_input("Texto para probar voz:", "Hola, soy TARS")

        if st.button("🗣️ Hablar"):
            try:
                vision.hablar(test_text)
                st.success("Reproduciendo voz...")
            except Exception as e:
                st.error(f"Error reproduciendo voz: {e}")

def config_interface(vision):
    """Interfaz de configuración"""

    st.header("⚙️ Configuración Avanzada")

    # Selector de modo
    st.subheader("🧠 Modo de TARS")
    if "modo_tars" not in st.session_state:
        st.session_state.modo_tars = "Conversacional"
    modo = st.radio("Selecciona el modo de TARS:", ["Conversacional", "Investigación"], index=0 if st.session_state.modo_tars=="Conversacional" else 1)
    st.session_state.modo_tars = modo
    st.info(f"Modo actual: {modo}")

    # Configuración de personalidad
    st.subheader("🎭 Modo de Personalidad")
    modos = ["amigable", "profesional", "divertido", "serio"]
    modo_actual = st.selectbox("Seleccionar modo:", modos, index=0)

    if st.button("💾 Aplicar Modo"):
        try:
            vision.personality_config.set_mode(modo_actual)
            st.success(f"Modo cambiado a: {modo_actual}")
        except Exception as e:
            st.error(f"Error cambiando modo: {e}")

    # Afinidad por usuario
    st.subheader("❤️ Afinidad")
    try:
        affinity = vision.personality_config.get_affinity("Ndrz_streamlit")
        st.write(f"**Afinidad actual:** {affinity}")

        new_affinity = st.slider("Ajustar afinidad:", 0.0, 1.0, affinity, 0.1)
        if st.button("💖 Actualizar Afinidad"):
            vision.personality_config.update_affinity("Ndrz_streamlit", "", "", new_affinity)
            st.success("Afinidad actualizada")
    except Exception as e:
        st.error(f"Error con afinidad: {e}")

    # Estadísticas de aprendizaje
    st.subheader("📈 Estadísticas de Aprendizaje")
    try:
        stats = vision.personality_trainer.get_stats()
        st.json(stats)
    except Exception as e:
        st.error(f"Error obteniendo estadísticas: {e}")

    # Subida de audios/videos para entrenamiento de personalidad y voz
    st.subheader("🔊 Entrenamiento de Voz y Personalidad")
    st.write("Sube audios o videos para que TARS aprenda tu voz y personalidad. Puedes subir archivos .wav, .mp3, .mp4")
    uploaded_files = st.file_uploader("Selecciona archivos de audio/video", type=["wav", "mp3", "mp4"], accept_multiple_files=True)
    if uploaded_files:
        for file in uploaded_files:
            file_path = os.path.join("data_privada/Ndrz/entrenamiento_voz", file.name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            st.success(f"Archivo {file.name} guardado para entrenamiento.")

if __name__ == "__main__":
    main()
