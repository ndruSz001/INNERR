import torch
from PIL import Image
from transformers import LlavaNextProcessor, LlavaNextForConditionalGeneration, BitsAndBytesConfig, AutoTokenizer, AutoModelForCausalLM
import json
import os
import random
from core.ia import *

if __name__ == "__main__":
    # Punto de entrada para ejecutar la IA modular
    main()
        self._vision_loaded = False
        print("👁️  Modelo de visión LLaVA: [DISPONIBLE BAJO DEMANDA]")
        
        # ========== MODELO DE TEXTO PRINCIPAL ==========
        # Phi-2 es el único modelo que se carga al inicio
        print("🧠 Cargando modelo conversacional Phi-2...")
        self.text_tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2")
        self.text_tokenizer.pad_token = self.text_tokenizer.eos_token
        
        self.text_model = AutoModelForCausalLM.from_pretrained(
            "microsoft/phi-2",
            quantization_config=self.quantization_config,
            device_map="auto",
            low_cpu_mem_usage=True,
            torch_dtype=torch.float16
        )
        print("✅ Phi-2 cargado exitosamente")
        
        # ========== SISTEMAS LIGEROS ==========
        # Estos componentes son rápidos de inicializar
        print("📊 Inicializando sistemas de personalidad y memoria...")
        self.db = DatabaseHandler()
        self.personality_trainer = PersonalityTrainer()
        self.episodic_memory = EpisodicMemory()
        self.personality_config = PersonalityConfig()
        self.response_processor = ResponsePostprocessor(self.episodic_memory, self.personality_config)
        self.strategic_reasoning = StrategicReasoning()
        
        # ========== CEREBROS EXPERTOS ==========
        # Ahora con funcionalidad real, se les pasa referencia al modelo de visión
        self.brain_conceptual = BrainConceptual(vision_model=self)
        self.brain_mechanical = BrainMechanical(vision_model=self)
        self.brain_medical = BrainMedical(vision_model=self)
        print("🧪 Cerebros expertos: [LISTOS - con análisis real]")
        
        # ========== MÓDULOS AVANZADOS ==========
        # Módulos que diferencian a TARS de Copilot/ChatGPT
        try:
            from tars_hardware import TarsHardware
            self.hardware = TarsHardware()
            print("🔧 Control de hardware: [DISPONIBLE]")
        except Exception as e:
            self.hardware = None
            print(f"⚠️ Control de hardware: No disponible ({e})")
        
        try:
            from project_knowledge import ProjectKnowledge
            self.projects = ProjectKnowledge()
            print("📚 Base de conocimiento de proyectos: [DISPONIBLE]")
        except Exception as e:
            self.projects = None
            print(f"⚠️ Base de conocimiento: No disponible ({e})")
        
        try:
            from document_processor import DocumentProcessor
            self.docs = DocumentProcessor()
            print("📄 Procesador de documentos (PDFs): [DISPONIBLE]")
        except Exception as e:
            self.docs = None
            print(f"⚠️ Procesador de documentos: No disponible ({e})")
        
        try:
            from conversation_manager import ConversationManager
            self.conversations = ConversationManager()
            print("💬 Gestor de conversaciones: [DISPONIBLE]")
        except Exception as e:
            self.conversations = None
            print(f"⚠️ Gestor de conversaciones: No disponible ({e})")
        
        # ========== CLONACIÓN DE VOZ (DESHABILITADA) ==========
        # RVC es muy pesado y experimental, solo cargar si se solicita
        self.voice_cloner = None
        self._voice_cloner_enabled = False
        print("🎤 Clonación de voz RVC: [DESHABILITADA - usar enable_voice_cloning()]")
        
        # ========== BACKEND OLLAMA (OPCIONAL) ==========
        try:
            ollama.list()
            self.usar_ollama = True
            print("⚡ Backend Ollama detectado - aceleración C++ activada")
        except Exception:
            self.usar_ollama = False
            print("📦 Ollama no disponible")
        
        # ========== BACKEND LLAMA.CPP (PRIORITARIO) ==========
        self.llama_backend = None
        self.usar_llama_cpp = False
        if LLAMA_CPP_AVAILABLE:
            try:
                self.llama_backend = LlamaCppBackend()
                self.usar_llama_cpp = True
                print("⚡ Backend llama.cpp activado - máxima velocidad!")
            except Exception as e:
                print(f"⚠️ No se pudo cargar llama.cpp: {e}")
                print("📦 Usando transformers como fallback")
        else:
            print("📦 Usando backend Python estándar")
        
        # Interfaz de voz deshabilitada para modo terminal
        self.tts_engine = None
        self.voz_activada = False
        
        print("\n" + "="*50)
        print("✅ TARS LISTO - Modo Conversacional Activado")
        print("💡 Memoria usada: ~2-3GB (solo Phi-2)")
        print("💡 Para análisis de imágenes usa: analizar_imagen(path)")
        print("="*50 + "\n")

    def _load_vision_model(self):
        """Carga el modelo de visión LLaVA bajo demanda (lazy loading)"""
        if self._vision_loaded:
            return True
            
        try:
            print("\n👁️  Cargando modelo de visión LLaVA 7B...")
            print("⏳ Esto puede tomar 30-60 segundos...")
            
            self.processor = LlavaNextProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf")
            self.model = LlavaNextForConditionalGeneration.from_pretrained(
                "llava-hf/llava-1.5-7b-hf",
                quantization_config=self.quantization_config,
                device_map="auto",
                low_cpu_mem_usage=True
            )
            
            self._vision_loaded = True
            print("✅ LLaVA cargado exitosamente\n")
            return True
            
        except Exception as e:
            print(f"❌ Error cargando modelo de visión: {e}")
            return False
    
    def enable_voice_cloning(self):
        """Activa el sistema de clonación de voz RVC (bajo demanda)"""
        if self._voice_cloner_enabled:
            print("🎤 Clonación de voz ya está activada")
            return
        
        try:
            print("🎤 Activando clonación de voz RVC...")
            from rvc_voice_cloner import RVCVoiceCloner
            self.voice_cloner = RVCVoiceCloner()
            self._voice_cloner_enabled = True
            print("✅ Clonación de voz RVC activada")
        except Exception as e:
            print(f"❌ Error activando clonación de voz: {e}")
    
    def generar_respuesta_texto(self, consulta, contexto="", user_id="default_user"):
        """
        Genera respuesta conversacional con el mejor backend disponible.
        Prioridad: llama.cpp > Ollama > Transformers
        """
        try:
            # PRIORIDAD 1: llama.cpp (más rápido)
            if self.usar_llama_cpp and self.llama_backend:
                return self._generar_con_llama_cpp(consulta, contexto, user_id)
            
            # PRIORIDAD 2: Ollama (rápido, si está disponible)
            if self.usar_ollama:
                return self._generar_con_ollama(consulta, contexto, user_id)
            
            # FALLBACK: Transformers (más lento pero siempre disponible)
            return self._generar_con_transformers(consulta, contexto, user_id)
        
        except Exception as e:
            print(f"Error en generación de texto: {e}")
            return "Lo siento, tuve un problema procesando eso. ¿Puedes repetirlo?"
    
    
    def generar_respuesta_texto(self, consulta, contexto="", user_id="default_user"):
        """
        Genera respuesta conversacional con backend optimizado (prioridad: llama.cpp > Ollama > transformers).
        """
        try:
            # 🚀 Prioridad 1: llama.cpp (4x más rápido que transformers)
            if self.usar_llama_cpp and self.llama_backend:
                return self._generar_con_llama_cpp(consulta, contexto, user_id)
            
            # ⚡ Prioridad 2: Ollama (optimización C++)
            if self.usar_ollama:
                return self._generar_con_ollama(consulta, contexto, user_id)
            
            # 📦 Prioridad 3: Transformers (fallback)
            return self._generar_con_transformers(consulta, contexto, user_id)
        
        except Exception as e:
            print(f"Error en generación de texto: {e}")
            return "Lo siento, tuve un problema procesando eso. ¿Puedes repetirlo?"
    
    def _generar_con_llama_cpp(self, consulta, contexto="", user_id="default_user"):
        """
        Genera respuesta usando llama.cpp (backend ultrarrápido).
        """
        try:
            # Obtener contexto de memoria episódica
            memory_context = self.episodic_memory.get_context(user_id, consulta)
            
            # Obtener personalidad aprendida
            personalidad_prompt = self.personality_trainer.generar_prompt_personalidad()
            
            # Obtener configuración de personalidad actual
            personality_settings = self.personality_config.get_all_settings()
            
            # System prompt para llama.cpp
            system_prompt = f"""Eres TARS, una IA inteligente y adaptable que aprende de las personas con las que interactúa.

Tu personalidad se adapta constantemente aprendiendo de conversaciones, expresiones y patrones de comunicación.
Hablas de manera natural, conversacional y empática, como un compañero inteligente real.

Características principales:
- Conversacional y amigable
- Experto en ciencia, tecnología, medicina y exoesqueletos
- Entiendes expresiones coloquiales mexicanas/latinas
- Mantienes un tono natural y ligeramente sarcástico cuando corresponde
- Aprendes y te adaptas al estilo de comunicación de tu usuario
- Recuerdas conversaciones anteriores y referencias personales

{personalidad_prompt}

{memory_context}

IMPORTANTE: Responde de manera natural, como hablarías con un amigo cercano. 
No suenes como una IA formal o robótica. Sé auténtico y relatable.

Configuración actual: {json.dumps(personality_settings, indent=2)}"""

            # Construir prompt completo
            prompt = f"{system_prompt}\n\nUsuario: {consulta}\nTARS:"
            
            # Generar respuesta con llama.cpp (ultrarrápido)
            respuesta = self.llama_backend.generate_response(
                prompt,
                max_tokens=200,
                temperature=0.8
            )
            
            # Limpiar respuesta
            if "Usuario:" in respuesta:
                respuesta = respuesta.split("Usuario:")[0].strip()
            if "TARS:" in respuesta:
                respuesta = respuesta.split("TARS:")[-1].strip()
            
            # Aplicar post-procesamiento
            respuesta_procesada = self.response_processor.postprocess_response(respuesta, consulta)
            
            # Agregar razonamiento estratégico si es relevante
            respuesta_final = self._add_strategic_reasoning(respuesta_procesada, consulta, user_id)
            
            # Guardar conversación en memoria episódica
            self.episodic_memory.process_conversation(consulta, respuesta_final)
            
            # Aprender de la respuesta generada
            if respuesta_final and len(respuesta_final) > 10:
                self.personality_trainer._analizar_texto_personalidad(respuesta_final)
            
            # Actualizar afinidad
            self.personality_config.update_affinity(user_id, consulta, respuesta_final)
            
            return respuesta_final
        
        except Exception as e:
            print(f"⚠️ Error en llama.cpp, usando fallback: {e}")
            # Fallback a transformers si llama.cpp falla
            return self._generar_con_transformers(consulta, contexto, user_id)
    
    def _generar_con_transformers(self, consulta, contexto="", user_id="default_user"):
        """
        Genera respuesta usando transformers (Phi-2) - fallback si llama.cpp/Ollama no están disponibles.
        """
        try:
            
            # Obtener contexto de memoria episódica
            memory_context = self.episodic_memory.get_context(user_id, consulta)
            
            # Obtener personalidad aprendida
            personalidad_prompt = self.personality_trainer.generar_prompt_personalidad()
            # Obtener contexto de memoria episódica
            memory_context = self.episodic_memory.get_context(user_id, consulta)
            
            # Obtener personalidad aprendida
            personalidad_prompt = self.personality_trainer.generar_prompt_personalidad()
            
            # Obtener configuración de personalidad actual
            personality_settings = self.personality_config.get_all_settings()
            
            # Prompt base mejorado
            system_prompt_base = """Eres TARS, una IA inteligente y adaptable que aprende de las personas con las que interactúa.
            
            Tu personalidad se adapta constantemente aprendiendo de conversaciones, expresiones y patrones de comunicación.
            Hablas de manera natural, conversacional y empática, como un compañero inteligente real.
            
            Características principales:
            - Conversacional y amigable
            - Experto en ciencia, tecnología, medicina y exoesqueletos
            - Entiendes expresiones coloquiales mexicanas/latinas
            - Mantienes un tono natural y ligeramente sarcástico cuando corresponde
            - Aprendes y te adaptas al estilo de comunicación de tu usuario
            - Recuerdas conversaciones anteriores y referencias personales
            
            {personalidad_aprendida}
            
            {memory_context}
            
            IMPORTANTE: Responde de manera natural, como hablarías con un amigo cercano. 
            No suenes como una IA formal o robótica. Sé auténtico y relatable.
            
            Configuración actual: {personality_settings}"""
            
            system_prompt = system_prompt_base.format(
                personalidad_aprendida=personalidad_prompt,
                memory_context=memory_context,
                personality_settings=json.dumps(personality_settings, indent=2)
            )
            
            prompt = f"{system_prompt}\n\nUsuario: {consulta}\nTARS:"
            
            inputs = self.text_tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(self.device)
            
            with torch.no_grad():
                outputs = self.text_model.generate(
                    **inputs,
                    max_new_tokens=200,
                    do_sample=True,
                    temperature=0.8,
                    top_p=0.9,
                    repetition_penalty=1.1,
                    pad_token_id=self.text_tokenizer.eos_token_id
                )
            
            respuesta = self.text_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Limpiar respuesta
            if "TARS:" in respuesta:
                respuesta = respuesta.split("TARS:")[-1].strip()
            
            # Aplicar post-procesamiento
            respuesta_procesada = self.response_processor.postprocess_response(respuesta, consulta)
            
            # Agregar razonamiento estratégico
            respuesta_final = self._add_strategic_reasoning(respuesta_procesada, consulta, user_id)
            
            # Guardar conversación en memoria episódica
            self.episodic_memory.process_conversation(consulta, respuesta_final)
            
            # Aprender de la respuesta generada
            if respuesta_final and len(respuesta_final) > 10:
                self.personality_trainer._analizar_texto_personalidad(respuesta_final)
            
            # Actualizar afinidad
            self.personality_config.update_affinity(user_id, consulta, respuesta_final)
            
            return respuesta_final
        
        except Exception as e:
            print(f"Error en transformers: {e}")
            return "Lo siento, tuve un problema procesando eso. ¿Puedes repetirlo?"

    def _generar_con_ollama(self, consulta, contexto="", user_id="default_user"):
        """
        Genera respuesta usando Ollama (backend C++ optimizado).
        """
        try:
            # Obtener contexto de memoria episódica
            memory_context = self.episodic_memory.get_context(user_id, consulta)
            
            # Obtener personalidad aprendida
            personalidad_prompt = self.personality_trainer.generar_prompt_personalidad()
            
            # Obtener configuración de personalidad actual
            personality_settings = self.personality_config.get_all_settings()
            
            # System prompt para Ollama
            system_prompt = f"""Eres TARS, una IA inteligente y adaptable que aprende de las personas con las que interactúa.

Tu personalidad se adapta constantemente aprendiendo de conversaciones, expresiones y patrones de comunicación.
Hablas de manera natural, conversacional y empática, como un compañero inteligente real.

Características principales:
- Conversacional y amigable
- Experto en ciencia, tecnología, medicina y exoesqueletos
- Entiendes expresiones coloquiales mexicanas/latinas
- Mantienes un tono natural y ligeramente sarcástico cuando corresponde
- Aprendes y te adaptas al estilo de comunicación de tu usuario
- Recuerdas conversaciones anteriores y referencias personales

{personalidad_prompt}

{memory_context}

IMPORTANTE: Responde de manera natural, como hablarías con un amigo cercano. 
No suenes como una IA formal o robótica. Sé auténtico y relatable.

Configuración actual: {json.dumps(personality_settings, indent=2)}"""
            
            # Llamada a Ollama
            response = ollama.chat(
                model='llama3',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': consulta}
                ],
                options={
                    'temperature': 0.8,
                    'top_p': 0.9,
                    'num_predict': 200
                }
            )
            
            respuesta = response['message']['content']
            
            # Aplicar post-procesamiento de respuesta
            respuesta_procesada = self.response_processor.postprocess_response(respuesta, consulta)
            
            # Agregar razonamiento estratégico si es relevante
            respuesta_final = self._add_strategic_reasoning(respuesta_procesada, consulta, user_id)
            
            # Guardar conversación en memoria episódica
            self.episodic_memory.process_conversation(consulta, respuesta_final)
            
            # Aprender de la respuesta generada para mejorar personalidad futura
            if respuesta_final and len(respuesta_final) > 10:
                self.personality_trainer._analizar_texto_personalidad(respuesta_final)
            
            # Actualizar afinidad basada en la interacción
            self.personality_config.update_affinity(user_id, consulta, respuesta_final)
            
            return respuesta_final
        
        except Exception as e:
            print(f"Error en Ollama: {e}")
            # Fallback a modo estándar
            return self._generar_con_transformers(consulta, contexto, user_id)

    def _generar_con_transformers(self, consulta, contexto="", user_id="default_user"):
        """
        Genera respuesta usando transformers (Phi-2).
        """
        try:
            # Obtener contexto de memoria episódica
            memory_context = self.episodic_memory.get_context(user_id, consulta)
            
            # Obtener personalidad aprendida
            personalidad_prompt = self.personality_trainer.generar_prompt_personalidad()
            
            # Obtener configuración de personalidad actual
            personality_settings = self.personality_config.get_all_settings()
            
            # Prompt base mejorado con personalidad aprendida y contexto de memoria
            system_prompt_base = """Eres TARS, una IA inteligente y adaptable que aprende de las personas con las que interactúa.
            
            Tu personalidad se adapta constantemente aprendiendo de conversaciones, expresiones y patrones de comunicación.
            Hablas de manera natural, conversacional y empática, como un compañero inteligente real.
            
            Características principales:
            - Conversacional y amigable
            - Experto en ciencia, tecnología, medicina y exoesqueletos
            - Entiendes expresiones coloquiales mexicanas/latinas
            - Mantienes un tono natural y ligeramente sarcástico cuando corresponde
            - Aprendes y te adaptas al estilo de comunicación de tu usuario
            - Recuerdas conversaciones anteriores y referencias personales
            
            {personalidad_aprendida}
            
            {memory_context}
            
            IMPORTANTE: Responde de manera natural, como hablarías con un amigo cercano. 
            No suenes como una IA formal o robótica. Sé auténtico y relatable.
            
            Configuración actual: {personality_settings}"""
            
            system_prompt = system_prompt_base.format(
                personalidad_aprendida=personalidad_prompt,
                memory_context=memory_context,
                personality_settings=json.dumps(personality_settings, indent=2)
            )
            
            prompt = f"{system_prompt}\n\nUsuario: {consulta}\nTARS:"
            
            inputs = self.text_tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(self.device)
            
            with torch.no_grad():
                outputs = self.text_model.generate(
                    **inputs,
                    max_new_tokens=200,  # Más tokens para respuestas más naturales
                    do_sample=True,
                    temperature=0.8,  # Un poco más creativo
                    top_p=0.9,
                    repetition_penalty=1.1,  # Evitar repeticiones
                    pad_token_id=self.text_tokenizer.eos_token_id
                )
            
            respuesta = self.text_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Limpiar respuesta (quitar el prompt)
            if "TARS:" in respuesta:
                respuesta = respuesta.split("TARS:")[-1].strip()
            
            # Aplicar post-procesamiento de respuesta
            respuesta_procesada = self.response_processor.postprocess_response(respuesta, consulta)
            
            # Agregar razonamiento estratégico si es relevante
            respuesta_final = self._add_strategic_reasoning(respuesta_procesada, consulta, user_id)
            
            # Guardar conversación en memoria episódica
            self.episodic_memory.process_conversation(consulta, respuesta_final)
            
            # Aprender de la respuesta generada para mejorar personalidad futura
            if respuesta_final and len(respuesta_final) > 10:
                self.personality_trainer._analizar_texto_personalidad(respuesta_final)
            
            # Actualizar afinidad basada en la interacción
            self.personality_config.update_affinity(user_id, consulta, respuesta_final)
            
            return respuesta_final
        
        except Exception as e:
            print(f"Error en transformers: {e}")
            return "Lo siento, tuve un problema procesando eso. ¿Puedes repetirlo?"

    def personalidad_amigable(self, mensaje_base, modo="amigable"):
        """
        Agrega personalidad a las respuestas de TARS usando patrones aprendidos.
        """
        if modo == "amigable":
            preguntas_abiertas = [
                "que me cuentas", "qué me cuentas", "cómo estás", "como estas", "qué tal", "que tal", "algo nuevo", "cómo va todo", "como va todo"
            ]
            mensaje_base_l = mensaje_base.lower()
            if any(p in mensaje_base_l for p in preguntas_abiertas):
                respuestas_cercanas = [
                    "¡Hoy estoy listo para ayudarte en lo que necesites! ¿Quieres saber algo curioso o necesitas apoyo con algún tema? Por ejemplo, ¿sabías que los pulpos tienen tres corazones?",
                    "¡Estoy de buen ánimo! Si quieres, puedo contarte un dato interesante o ayudarte con lo que gustes. Hoy leí sobre inteligencia artificial y cómo está cambiando el mundo.",
                    "¡Gracias por preguntar! Hoy aprendí muchas cosas nuevas, ¿quieres que te cuente alguna? Por cierto, ¿te gustaría saber cómo funciona la memoria de TARS?",
                    "¡Aquí estoy, preparado para cualquier consulta! ¿Te gustaría escuchar una curiosidad, una anécdota divertida o tienes algo en mente?"
                ]
                return random.choice(respuestas_cercanas)
            # Obtener expresiones aprendidas del usuario
            top_expresiones = sorted(self.personality_trainer.voice_patterns["expresiones_frecuentes"].items(),
                                   key=lambda x: x[1], reverse=True)[:5]
            intros_base = [
                "¡Claro que sí! ",
                "Con gusto te ayudo. ",
                "Como tu asistente personal, ",
                "TARS a tus órdenes. ",
                "Interesante consulta. ",
                "¡Ey, eso me recuerda a algo! ",
                "Como diría un amigo, ",
                "Procesando... ",
                "¡Fascinante! ",
                "Déjame pensar en eso. ",
                "¡Genial! ",
                "Oye, ",
                "Mira, ",
                "Sabes qué, ",
                "¡Por supuesto! ",
                "Vamos a ver... ",
                "¡Eso es interesante! ",
                "Como experto, te digo que ",
                "¡Perfecto! ",
                "¡Aquí vamos! "
            ]
            intros_aprendidas = [f"{expr} " for expr, _ in top_expresiones if len(expr.split()) <= 3]
          
            intros = intros_base + intros_aprendidas
            intro = random.choice(intros)
            # Añadir una curiosidad, anécdota o reflexión para respuestas más largas
            curiosidades = [
                "¿Sabías que el cerebro humano tiene más conexiones que estrellas en la galaxia?",
                "Una vez, un usuario me preguntó cómo recordar mejor las cosas. Le recomendé asociar ideas con imágenes, ¡funciona muy bien!",
                "La inteligencia artificial está avanzando rápido, pero siempre trato de mantenerme amigable y útil para ti.",
                "Si tienes alguna pregunta sobre ciencia, tecnología o incluso recetas, ¡puedo ayudarte!"
            ]
            if random.random() < 0.5:
                extra = " " + random.choice(curiosidades)
            else:
                extra = ""
            return f"{intro}{mensaje_base}{extra}"
        elif modo == "analisis":
            anuncios = [
                "🔍 **MODO ANÁLISIS ACTIVADO** 🔍\n\nTARS asumiendo control total. Procesando datos...\n\n",
                "⚡ **PROTOCOLOS DE ANÁLISIS INICIADOS** ⚡\n\nCoordinando agentes especializados...\n\n",
                "🧠 **TARS EN MODO INTELIGENTE** 🧠\n\nAnalizando con precisión quirúrgica...\n\n"
            ]
            anuncio = random.choice(anuncios)
            return f"{anuncio}{mensaje_base}"
        return mensaje_base

    # def hablar(self, texto, modo="amigable"):
    #     pass

    # def escuchar(self):
    #     pass

    def load_memory(self):
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        return {"preferences": {}, "learnings": []}

    def save_memory(self):
        with open(MEMORY_FILE, "w") as f:
            json.dump(self.memory, f)

    def orquestar_analisis(self, image_path, user_query=""):
        """
        Orquestador: Decide qué cerebro usar basado en la consulta y la imagen.
        """
        # Anuncio de modo análisis
        anuncio = "Activando protocolos de análisis avanzado. TARS coordinando agentes especializados..."
        
        # Clasificación simple basada en palabras clave
        if "boceto" in user_query.lower() or "diseño" in user_query.lower():
            analisis = self.brain_conceptual.analyze(image_path, user_query)
        elif "torque" in user_query.lower() or "material" in user_query.lower() or "cad" in user_query.lower():
            analisis = self.brain_mechanical.analyze(image_path, user_query)
        elif "resonancia" in user_query.lower() or "anatomía" in user_query.lower() or "biomecánica" in user_query.lower():
            analisis = self.brain_medical.analyze(image_path, user_query)
        else:
            # Análisis general con LLaVA
            analisis = self.analizar_prototipo(image_path)
        
        return self.personalidad_amigable(f"{anuncio}\n\n{analisis}", modo="analisis")

    def analizar_prototipo(self, imagen_path):
        """
        Función para que TARS analice imágenes médicas o de robótica usando LLaVA.
        """
        # Cargar modelo de visión si aún no está cargado
        if not self._load_vision_model():
            return "❌ No se pudo cargar el modelo de visión. Verifica la instalación de LLaVA."
        
        try:
            print(f"Debug: Intentando abrir imagen en {imagen_path}")
            img = Image.open(imagen_path).convert("RGB")
            print(f"Debug: Imagen abierta correctamente, tamaño: {img.size}")
            
            # Prompt para análisis médico/robótico
            prompt = "Describe esta imagen en detalle, enfocándote en elementos médicos o mecánicos como articulaciones, servomotores o estructuras anatómicas."
            
            print(f"Debug: Procesando con prompt: {prompt}")
            inputs = self.processor(prompt, img, return_tensors="pt").to(self.device)
            print(f"Debug: Inputs procesados, keys: {inputs.keys()}")
            
            # Generar respuesta
            with torch.no_grad():
                output = self.model.generate(**inputs, max_new_tokens=200, do_sample=False)
            
            respuesta = self.processor.decode(output[0], skip_special_tokens=True)
            print(f"Debug: Respuesta generada: {respuesta}")
            
            # Limpiar respuesta (quitar el prompt)
            if prompt in respuesta:
                respuesta = respuesta.replace(prompt, "").strip()
            
            return f"Análisis de TARS: {respuesta}"
        
        except Exception as e:
            print(f"Debug: Error en análisis: {str(e)}")
            return f"Error en análisis: {str(e)}. Verifica que la imagen sea válida."

    def etiquetar_componentes(self, imagen_path):
        """
        Etiqueta componentes específicos en imágenes de exoesqueletos.
        """
        # Cargar modelo de visión si aún no está cargado
        if not self._load_vision_model():
            return "❌ No se pudo cargar el modelo de visión. Verifica la instalación de LLaVA."
        
        try:
            print(f"Debug etiquetas: Abriendo imagen {imagen_path}")
            img = Image.open(imagen_path).convert("RGB")
            print(f"Debug etiquetas: Imagen abierta, tamaño: {img.size}")
            
            prompt = "Lista los componentes visibles en esta imagen, como articulaciones, servomotores, estructuras metálicas. Sé específico."
            print(f"Debug etiquetas: Prompt: {prompt}")
            
            inputs = self.processor(prompt, img, return_tensors="pt").to(self.device)
            print(f"Debug etiquetas: Inputs procesados")
            
            with torch.no_grad():
                output = self.model.generate(**inputs, max_new_tokens=100, do_sample=False)
            
            respuesta = self.processor.decode(output[0], skip_special_tokens=True)
            print(f"Debug etiquetas: Respuesta: {respuesta}")
            
            if prompt in respuesta:
                respuesta = respuesta.replace(prompt, "").strip()
            
            # Parsear en lista (simple split por comas)
            etiquetas = [etiqueta.strip() for etiqueta in respuesta.split(",") if etiqueta.strip()]
            return etiquetas
        
        except Exception as e:
            print(f"Debug etiquetas: Error: {str(e)}")
            return [f"Error: {str(e)}"]

    def responder_consulta(self, consulta, usuario="Ndrz"):
        """
        Responde consultas de texto usando Phi-2 por defecto, delegando a agentes solo para temas técnicos específicos.
        """
        consulta_lower = consulta.lower()
        
        # Solo delegar a agentes especializados si es claramente técnico
        if any(word in consulta_lower for word in ["diseño", "boceto", "diseñar", "prototipo"]) and not any(word in consulta_lower for word in ["ciencia", "tecnología", "vida", "mundo"]):
            respuesta = self.brain_conceptual.analyze("", consulta)
        elif any(word in consulta_lower for word in ["mecánica", "torque", "material", "cad", "ingeniería", "calcular", "fuerza", "voltaje"]) and not any(word in consulta_lower for word in ["vida", "mundo", "noticias"]):
            # Guardar cálculo si es nuevo
            if "calcular" in consulta_lower:
                self.db.guardar_calculo("torque", f"Cálculo solicitado: {consulta}", usuario)
            respuesta = self.brain_mechanical.analyze("", consulta)
        elif any(word in consulta_lower for word in ["médico", "anatomía", "resonancia", "biomecánica", "diagnóstico", "paciente"]) and not any(word in consulta_lower for word in ["vida", "mundo", "noticias"]):
            respuesta = self.brain_medical.analyze("", consulta)
        
        # Buscar en base de datos solo si es consulta específica
        elif "materiales" in consulta_lower or "preferencia" in consulta_lower:
            prefs = self.db.obtener_preferencias(usuario, "materiales")
            if prefs:
                respuesta = f"Basado en tu preferencia guardada: {prefs[0][0]}"
            else:
                respuesta = "Recomiendo fibra de carbono para ligereza y titanio para durabilidad."
        
        elif "historial" in consulta_lower or "calculos" in consulta_lower:
            historial = self.db.obtener_historial(usuario=usuario)
            if historial:
                response = "Historial reciente:\n"
                for calc in historial[:5]:
                    response += f"- {calc[0]}: {calc[1]} ({calc[2]})\n"
                respuesta = response
            else:
                respuesta = "No hay cálculos guardados aún."
        
        # 🧠 COMANDOS DE ENTRENAMIENTO DE PERSONALIDAD
        elif consulta_lower.startswith("entrenar_audio"):
            # Formato: entrenar_audio ruta/al/archivo.wav "transcripción opcional"
            partes = consulta.split(" ", 2)
            if len(partes) >= 2:
                audio_path = partes[1].strip()
                transcripcion = partes[2].strip('"') if len(partes) > 2 else None
                respuesta = self.entrenar_personalidad_audio(audio_path, transcripcion)
            else:
                respuesta = "Formato: entrenar_audio ruta/al/archivo.wav \"transcripción opcional\""
        
        elif consulta_lower.startswith("entrenar_texto"):
            # Formato: entrenar_texto "texto de ejemplo"
            if '"' in consulta:
                texto = consulta.split('"')[1]
                respuesta = self.entrenar_personalidad_texto(texto)
            else:
                respuesta = "Formato: entrenar_texto \"tu texto de ejemplo aquí\""
        
        elif "estadisticas_personalidad" in consulta_lower or "stats_personalidad" in consulta_lower:
            respuesta = self.mostrar_estadisticas_personalidad()
        
        elif "resetear_personalidad" in consulta_lower:
            respuesta = self.resetear_personalidad()
        
        elif "sugerencias_personalidad" in consulta_lower or "mejorar_personalidad" in consulta_lower:
            respuesta = self.sugerir_mejoras_personalidad()
        
        else:
            # Usar modelo de texto conversacional para TODO lo demás
            respuesta = self.generar_respuesta_texto(consulta)
        
        respuesta_personalizada = self.personalidad_amigable(respuesta)
        
        # Aprender de la conversación para mejorar personalidad
        self.aprender_de_conversacion(consulta, respuesta_personalizada)
        
        # Solo hablar si está activado
        if hasattr(self, 'voz_activada') and self.voz_activada:
            self.hablar(respuesta_personalizada)
        return respuesta_personalizada

    # 🧠 MÉTODOS DE ENTRENAMIENTO DE PERSONALIDAD

    def entrenar_personalidad_audio(self, audio_path, transcripcion_manual=None):
        """
        Entrena la personalidad de TARS con un archivo de audio.
        Aprende expresiones, tono, vocabulario y patrones de comunicación.
        """
        try:
            print(f"🎤 Entrenando personalidad con audio: {audio_path}")
            success = self.personality_trainer.procesar_audio_personalidad(audio_path, transcripcion_manual)

            if success:
                print("✅ Personalidad actualizada con nuevo audio")
                return "¡Perfecto! He aprendido de ese audio. Mi personalidad se está adaptando a tu estilo de comunicación."
            else:
                return "Lo siento, no pude procesar ese audio. ¿Puedes verificar que sea un archivo de audio válido?"

        except Exception as e:
            print(f"Error entrenando personalidad: {e}")
            return f"Error procesando audio: {e}"

    def entrenar_personalidad_texto(self, texto_ejemplo):
        """
        Entrena la personalidad con un texto de ejemplo.
        Útil para textos escritos o transcripciones manuales.
        """
        try:
            print("📝 Entrenando personalidad con texto...")
            self.personality_trainer._analizar_texto_personalidad(texto_ejemplo)
            self.personality_trainer.guardar_personalidad()
            print("✅ Personalidad actualizada con texto")
            return "¡Gracias! He aprendido de ese texto. Mi forma de hablar se está adaptando."

        except Exception as e:
            print(f"Error entrenando con texto: {e}")
            return f"Error procesando texto: {e}"

    def mostrar_estadisticas_personalidad(self):
        """
        Muestra estadísticas de la personalidad aprendida.
        """
        try:
            stats = self.personality_trainer.obtener_estadisticas_personalidad()

            respuesta = "📊 **ESTADÍSTICAS DE MI PERSONALIDAD APRENDIDA**\n\n"

            respuesta += f"**Análisis Total:**\n"
            respuesta += f"- Expresiones analizadas: {stats['total_expresiones_analizadas']}\n"
            respuesta += f"- Palabras de vocabulario: {stats['total_palabras_vocabulario']}\n"
            respuesta += f"- Patrones de conversación: {stats['total_patrones_conversacion']}\n\n"

            respuesta += f"**Estilo de Comunicación:**\n"
            estilo = stats['estilo_actual']
            respuesta += f"- Formalidad: {estilo['formalidad']:.2f} (0=coloquial, 1=formal)\n"
            respuesta += f"- Humor: {estilo['humor']:.2f} (0=serio, 1=bromista)\n"
            respuesta += f"- Empatía: {estilo['empatia']:.2f} (0=directo, 1=empático)\n"
            respuesta += f"- Detallismo: {estilo['detallismo']:.2f} (0=conciso, 1=detallado)\n\n"

            if stats['top_expresiones']:
                respuesta += f"**Expresiones Favoritas:**\n"
                for expr, count in stats['top_expresiones'].items():
                    respuesta += f"- '{expr}' ({count} veces)\n"

            if stats['top_vocabulario']:
                respuesta += f"\n**Vocabulario Preferido:**\n"
                vocab_list = list(stats['top_vocabulario'].keys())[:10]
                respuesta += ", ".join(vocab_list)

            return respuesta

        except Exception as e:
            return f"Error obteniendo estadísticas: {e}"

    def resetear_personalidad(self):
        """
        Resetea toda la personalidad aprendida (volver a personalidad base).
        """
        try:
            self.personality_trainer.resetear_personalidad()
            return "🔄 Personalidad reseteada. Volví a mi personalidad base de TARS."

        except Exception as e:
            return f"Error reseteando personalidad: {e}"

    def aprender_de_conversacion(self, texto_usuario, texto_respuesta):
        """
        Aprende automáticamente de las conversaciones para mejorar la personalidad.
        Se llama automáticamente en cada interacción.
        """
        try:
            # Aprender del usuario
            if texto_usuario and len(texto_usuario) > 5:
                self.personality_trainer._analizar_texto_personalidad(texto_usuario)

            # Aprender de las respuestas (para auto-mejora)
            if texto_respuesta and len(texto_respuesta) > 10:
                self.personality_trainer._analizar_texto_personalidad(texto_respuesta)

        except Exception as e:
            # No mostrar error al usuario, solo loggear
            print(f"Error aprendiendo de conversación: {e}")

    def sugerir_mejoras_personalidad(self):
        """
        Sugiere qué tipo de contenido agregar para mejorar la personalidad.
        """
        stats = self.personality_trainer.obtener_estadisticas_personalidad()

        sugerencias = []

        if stats['total_expresiones_analizadas'] < 50:
            sugerencias.append("🎤 **Más audios:** Necesito escuchar más conversaciones tuyas para aprender tus expresiones favoritas.")

        if stats['estilo_actual']['formalidad'] < 0.3:
            sugerencias.append("📝 **Vocabulario variado:** Tu estilo es muy coloquial. ¿Quieres que agregue más expresiones formales?")

        if stats['estilo_actual']['humor'] < 0.4:
            sugerencias.append("😄 **Más humor:** ¿Quieres que sea más bromista? Agrega conversaciones con chistes o expresiones divertidas.")

        if stats['estilo_actual']['empatia'] < 0.4:
            sugerencias.append("❤️ **Más empatía:** ¿Quieres que sea más comprensivo? Agrega conversaciones sobre sentimientos o situaciones personales.")

        if not sugerencias:
            sugerencias.append("✅ **¡Excelente!** Tu personalidad está muy bien desarrollada. Sigue agregando contenido para mantenerla fresca.")

        respuesta = "**💡 SUGERENCIAS PARA MEJORAR MI PERSONALIDAD:**\n\n" + "\n".join(sugerencias)
        respuesta += "\n\n**Para agregar contenido usa:**\n"
        respuesta += "- `entrenar_audio ruta/al/audio.wav`\n"
        respuesta += "- `entrenar_texto \"tu texto aquí\"`\n"
        respuesta += "- Simplemente habla conmigo normalmente (aprendo automáticamente)"

        return respuesta

    # ===== MÉTODOS PARA SISTEMAS AVANZADOS DE PERSONALIDAD =====

    def entrenar_voz_rvc(self, audio_path, user_id="default_user"):
        """
        Entrena el modelo RVC con audio del usuario para clonar su voz.
        """
        try:
            print(f"🎭 Iniciando entrenamiento de voz RVC para usuario {user_id}")
            resultado = self.voice_cloner.entrenar(audio_path, user_id)
            return resultado
        except Exception as e:
            return f"Error entrenando voz RVC: {e}"

    def configurar_personalidad(self, user_id="default_user", **settings):
        """
        Configura parámetros de personalidad para un usuario específico.
        """
        try:
            # Actualizar settings específicos
            for key, value in settings.items():
                if '.' in key:
                    # Keys anidados como "affinity_settings.proactivity_level.suggestion_frequency"
                    key_parts = key.split('.')
                    self.personality_config.set_setting(value, *key_parts)
                else:
                    # Keys simples
                    self.personality_config.set_setting(value, key)
            
            return f"✅ Personalidad configurada para {user_id}"
        except Exception as e:
            return f"Error configurando personalidad: {e}"

    def obtener_estadisticas_memoria(self, user_id="default_user"):
        """
        Obtiene estadísticas de la memoria episódica del usuario.
        """
        try:
            stats = self.episodic_memory.get_stats(user_id)
            return f"📊 **ESTADÍSTICAS DE MEMORIA PARA {user_id.upper()}:**\n\n{stats}"
        except Exception as e:
            return f"Error obteniendo estadísticas de memoria: {e}"

    def limpiar_memoria_antigua(self, user_id="default_user", dias=30):
        """
        Limpia conversaciones antiguas de la memoria episódica.
        """
        try:
            resultado = self.episodic_memory.cleanup_old_conversations(user_id, dias)
            return f"🧹 **LIMPIEZA DE MEMORIA COMPLETADA:**\n\n{resultado}"
        except Exception as e:
            return f"Error limpiando memoria: {e}"

    def exportar_datos_usuario(self, user_id="default_user"):
        """
        Exporta todos los datos del usuario (memoria, configuración, personalidad).
        """
        try:
            # Recopilar datos de todos los sistemas
            datos = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "memoria_episodica": self.episodic_memory.export_data(user_id),
                "configuracion_personalidad": self.personality_config.get_all_settings(),
                "estadisticas_personalidad": self.personality_trainer.obtener_estadisticas_personalidad(),
                "voz_rvc_entrenada": self.voice_cloner.model is not None
            }
            # Guardar en archivo JSON
            filename = f"tars_datos_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            return f"✅ **DATOS EXPORTADOS:**\n\nArchivo: {filename}\nTamaño: {len(json.dumps(datos))} caracteres"
        except Exception as e:
            return f"Error exportando datos: {e}"

    def importar_datos_usuario(self, filename, user_id="default_user"):
        """
        Importa datos de usuario desde un archivo JSON.
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            # Restaurar datos en cada sistema
            if "memoria_episodica" in datos:
                self.episodic_memory.import_data(user_id, datos["memoria_episodica"])
            
            if "configuracion_personalidad" in datos:
                self.personality_config.update_settings(user_id, **datos["configuracion_personalidad"])
            
            return f"✅ **DATOS IMPORTADOS:**\n\nUsuario: {user_id}\nConversaciones: {len(datos.get('memoria_episodica', {}).get('conversaciones', []))}"
        except Exception as e:
            return f"Error importando datos: {e}"

    def _add_strategic_reasoning(self, response, query, user_id):
        """
        Agrega razonamiento estratégico a la respuesta cuando es relevante.
        """
        try:
            # Obtener métricas actuales del sistema
            current_metrics = self._get_system_metrics()
            # Generar consejo estratégico basado en el contexto
            strategic_advice = self.strategic_reasoning.get_strategic_advice(query)
            # Agregar consejo si es relevante y la respuesta no es muy larga
            if strategic_advice and len(response) < 400:
                response += f"\n\n{strategic_advice}"
            return response
        except Exception as e:
            print(f"Error en razonamiento estratégico: {e}")
            return response

    def _get_system_metrics(self):
        """
        Obtiene métricas actuales del sistema para análisis estratégico.
        """
        try:
            import psutil
            import GPUtil
            
            # CPU y memoria
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # GPU si está disponible
            gpu_info = {}
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    gpu_info = {
                        "gpu_usage": gpu.load * 100,
                        "gpu_memory": gpu.memoryUsed,
                        "gpu_temperature": gpu.temperature
                    }
            except:
                pass
            
            metrics = {
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "avg_response_time": 2.1,  # Estimado, se podría medir realmente
                "temperature": 75,  # Estimado
                "voice_cloned": self.voice_cloner.model is not None if hasattr(self, 'voice_cloner') else False
            }
            
            metrics.update(gpu_info)
            return metrics
            
        except Exception as e:
            print(f"Error obteniendo métricas del sistema: {e}")
            return {
                "cpu_usage": 80,
                "memory_usage": 75,
                "avg_response_time": 2.1,
                "temperature": 75,
                "voice_cloned": False
            }
    
    # ========== MÉTODOS DE ACCESO RÁPIDO (DIFERENCIADORES) ==========
    
    def analizar_imagen_medica(self, imagen, contexto="", patient_id=None):
        """
        Análisis privado de imágenes médicas (100% local).
        Diferenciador: Copilot/ChatGPT no pueden procesar datos médicos privados.
        """
        if not self.brain_medical:
            return "❌ Cerebro médico no disponible"
        
        return self.brain_medical.analyze(
            imagen, 
            user_context=contexto,
            patient_id=patient_id
        )
    
    def analizar_diseno_mecanico(self, imagen, contexto=""):
        """
        Análisis de diseños mecánicos con cálculos de ingeniería.
        """
        if not self.brain_mechanical:
            return "❌ Cerebro mecánico no disponible"
        
        return self.brain_mechanical.analyze(imagen, user_context=contexto)
    
    def calcular_torque(self, fuerza_N, distancia_m, angulo=90):
        """Cálculo rápido de torque requerido."""
        if not self.brain_mechanical:
            return "❌ Cerebro mecánico no disponible"
        
        return self.brain_mechanical.calculate_torque(fuerza_N, distancia_m, angulo)
    
    def analizar_boceto(self, imagen, contexto=""):
        """
        Análisis de diseño conceptual con enfoque en ergonomía.
        """
        if not self.brain_conceptual:
            return "❌ Cerebro conceptual no disponible"
        
        return self.brain_conceptual.analyze(imagen, user_context=contexto)
    
    def conectar_hardware(self, puerto="/dev/ttyUSB0", nombre="esp32"):
        """
        Conecta a hardware (ESP32, Arduino, etc).
        Diferenciador: Copilot/ChatGPT no pueden controlar hardware real.
        """
        if not self.hardware:
            return "❌ Módulo de hardware no disponible"
        
        return self.hardware.conectar_dispositivo(puerto, nombre=nombre)
    
    def ejecutar_experimento(self, protocolo, dispositivo="esp32"):
        """
        Ejecuta protocolo de prueba automatizado en hardware.
        """
        if not self.hardware:
            return "❌ Módulo de hardware no disponible"
        
        return self.hardware.ejecutar_protocolo_prueba(protocolo, nombre=dispositivo)
    
    def registrar_experimento_proyecto(self, proyecto_id, datos_experimento):
        """
        Documenta experimento en base de conocimiento.
        Diferenciador: Memoria persistente acumulativa.
        """
        if not self.projects:
            return "❌ Base de conocimiento no disponible"
        
        return self.projects.registrar_experimento(proyecto_id, datos_experimento)
    
    def buscar_soluciones_previas(self, problema):
        """
        Busca en tu historial de proyectos soluciones a problemas similares.
        Diferenciador: Contexto acumulativo que Copilot/ChatGPT no tienen.
        """
        if not self.projects:
            return "❌ Base de conocimiento no disponible"
        
        return self.projects.buscar_soluciones_previas(problema)
    
    # ============================================================
    # INGESTA RÁPIDA DE INFORMACIÓN
    # ============================================================
    
    def procesar_pdf(self, pdf_path, categoria="paper", extraer_imagenes=True):
        """
        Procesa un PDF completo: extrae texto, imágenes, tablas.
        Útil para papers científicos, manuales técnicos, reportes.
        
        Diferenciador: Ingesta local de documentación sin límites de tamaño.
        """
        if not self.docs:
            return {"error": "Procesador de documentos no disponible"}
        
        return self.docs.procesar_pdf(pdf_path, categoria, extraer_imagenes)
    
    def buscar_en_documentos(self, query, categoria=None):
        """
        Busca información en todos los PDFs procesados.
        Encuentra rápidamente referencias, métodos, resultados previos.
        """
        if not self.docs:
            return []
        
        return self.docs.buscar_en_documentos(query, categoria)
    
    def analizar_documento_con_expertos(self, pdf_path, tipo_analisis="completo"):
        """
        Procesa PDF y lo analiza con los cerebros expertos relevantes.
        
        tipo_analisis: "medico", "mecanico", "conceptual", "completo"
        """
        if not self.docs:
            return {"error": "Procesador no disponible"}
        
        # Procesar PDF
        resultado = self.docs.procesar_pdf(pdf_path)
        
        if "error" in resultado:
            return resultado
        
        # Analizar imágenes extraídas con cerebros expertos
        analisis = {
            "documento": resultado["nombre_archivo"],
            "texto_extraido": True,
            "total_paginas": len(resultado["paginas"]),
            "analisis_expertos": []
        }
        
        # Si hay imágenes, analizarlas
        if resultado.get("imagenes_extraidas"):
            print(f"\n🔍 Analizando {len(resultado['imagenes_extraidas'])} imágenes con cerebros expertos...")
            
            for img_path in resultado["imagenes_extraidas"][:3]:  # Máximo 3 imágenes
                if tipo_analisis in ["medico", "completo"] and self.brain_medical:
                    analisis_img = self.brain_medical.analyze(img_path)
                    analisis["analisis_expertos"].append({
                        "imagen": img_path,
                        "tipo": "medico",
                        "resultado": analisis_img
                    })
                
                if tipo_analisis in ["mecanico", "completo"] and self.brain_mechanical:
                    analisis_img = self.brain_mechanical.analyze(img_path)
                    analisis["analisis_expertos"].append({
                        "imagen": img_path,
                        "tipo": "mecanico",
                        "resultado": analisis_img
                    })
        
        return analisis
    
    def procesar_pdf_con_ocr(self, pdf_path, idioma="spa+eng"):
        """
        Procesa PDF escaneado usando OCR.
        Útil para papers antiguos, documentos escaneados sin texto.
        """
        if not self.docs:
            return {"error": "Procesador no disponible"}
        
        return self.docs.aplicar_ocr_a_pdf(pdf_path, idioma)
    
    def extraer_metadatos_paper(self, pdf_path):
        """
        Extrae metadatos estructurados de un paper científico.
        Retorna: título, autores, DOI, año, abstract, keywords.
        """
        if not self.docs:
            return {"error": "Procesador no disponible"}
        
        # Primero procesar el PDF si no está procesado
        txt_file = self.docs.docs_dir / f"{Path(pdf_path).stem}.txt"
        
        if not txt_file.exists():
            resultado = self.docs.procesar_pdf(pdf_path, categoria="paper")
            if "error" in resultado:
                return resultado
            texto = resultado["texto_completo"]
        else:
            with open(txt_file, 'r', encoding='utf-8') as f:
                texto = f.read()
        
        return self.docs.extraer_metadatos_paper(texto)
    
    def generar_resumen_pdf(self, pdf_path, num_oraciones=5):
        """
        Genera resumen automático de un PDF.
        Usa algoritmo extractivo basado en frecuencia de palabras.
        """
        if not self.docs:
            return {"error": "Procesador no disponible"}
        
        # Obtener texto del PDF
        txt_file = self.docs.docs_dir / f"{Path(pdf_path).stem}.txt"
        
        if not txt_file.exists():
            resultado = self.docs.procesar_pdf(pdf_path)
            if "error" in resultado:
                return resultado
            texto = resultado["texto_completo"]
        else:
            with open(txt_file, 'r', encoding='utf-8') as f:
                texto = f.read()
        
        resumen = self.docs.generar_resumen_automatico(texto, num_oraciones)
        
        return {
            "archivo": Path(pdf_path).name,
            "resumen": resumen,
            "num_oraciones": num_oraciones
        }
    
    def extraer_referencias_paper(self, pdf_path):
        """
        Extrae todas las referencias bibliográficas de un paper.
        Útil para rastrear literatura citada, encontrar papers relacionados.
        """
        if not self.docs:
            return {"error": "Procesador no disponible"}
        
        txt_file = self.docs.docs_dir / f"{Path(pdf_path).stem}.txt"
        
        if not txt_file.exists():
            resultado = self.docs.procesar_pdf(pdf_path, categoria="paper")
            if "error" in resultado:
                return resultado
            texto = resultado["texto_completo"]
        else:
            with open(txt_file, 'r', encoding='utf-8') as f:
                texto = f.read()
        
        referencias = self.docs.extraer_referencias_bibliograficas(texto)
        
        return {
            "archivo": Path(pdf_path).name,
            "total_referencias": len(referencias),
            "referencias": referencias
        }
    
    def comparar_pdfs(self, pdf1_path, pdf2_path):
        """
        Compara dos PDFs y encuentra diferencias.
        Útil para revisar versiones de papers, ver qué cambió.
        """
        if not self.docs:
            return {"error": "Procesador no disponible"}
        
        return self.docs.comparar_documentos(pdf1_path, pdf2_path)
    
    def analizar_calidad_paper(self, pdf_path):
        """
        Analiza calidad/completitud de un paper científico.
        Verifica presencia de secciones clave, referencias, figuras.
        """
        if not self.docs:
            return {"error": "Procesador no disponible"}
        
        txt_file = self.docs.docs_dir / f"{Path(pdf_path).stem}.txt"
        
        if not txt_file.exists():
            resultado = self.docs.procesar_pdf(pdf_path, categoria="paper")
            if "error" in resultado:
                return resultado
            texto = resultado["texto_completo"]
        else:
            with open(txt_file, 'r', encoding='utf-8') as f:
                texto = f.read()
        
        calidad = self.docs.analizar_calidad_paper(texto)
        
        print(f"\n📊 Análisis de Calidad: {Path(pdf_path).name}")
        print(f"   Completitud: {calidad['completitud']}%")
        print(f"   Secciones encontradas: {len(calidad['secciones_encontradas'])}/{len(calidad['secciones_encontradas']) + len(calidad['secciones_faltantes'])}")
        print(f"   Referencias: {calidad['numero_referencias']}")
        print(f"   Figuras: {calidad['numero_figuras']}")
        
        if calidad["recomendaciones"]:
            print(f"\n   Recomendaciones:")
            for rec in calidad["recomendaciones"]:
                print(f"      {rec}")
        
        return calidad