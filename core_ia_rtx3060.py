# 🚀 TARS Optimizado para RTX 3060 (12GB VRAM)
# Versión preparada para cuando tengas la Dell dedicada
# NO REEMPLAZAR core_ia.py actual hasta tener RTX 3060

import torch
from PIL import Image
from transformers import LlavaNextProcessor, LlavaNextForConditionalGeneration, BitsAndBytesConfig, AutoTokenizer, AutoModelForCausalLM
import json
import os
import random
import pyttsx3
from gtts import gTTS
import pygame
from io import BytesIO
import speech_recognition as sr
from brain_conceptual import BrainConceptual
from brain_mechanical import BrainMechanical
from brain_medical import BrainMedical
from database_handler import DatabaseHandler

# Memoria compartida (ahora manejada por DatabaseHandler)
MEMORY_FILE = "tars_memory.json"

class TarsVisionRTX3060:
    """Versión optimizada de TarsVision para RTX 3060 con 12GB VRAM"""

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"TARS RTX 3060: Sistema de visión avanzado iniciado en {self.device}")

        # RTX 3060: 4-bit quantization para modelos más grandes
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )

        # Modelo de visión LLaVA 13B (3x más grande que 7B)
        print("Cargando LLaVA 13B para análisis de imágenes superior...")
        self.processor = LlavaNextProcessor.from_pretrained("llava-hf/llava-1.5-13b-hf")
        self.model = LlavaNextForConditionalGeneration.from_pretrained(
            "llava-hf/llava-1.5-13b-hf",
            quantization_config=quantization_config,
            device_map="auto",
            low_cpu_mem_usage=True,
            torch_dtype=torch.float16,
            max_memory={0: "12GB", "cpu": "32GB"}
        )

        # Modelo de conversación Mistral 7B (superior a Phi-2)
        print("Cargando Mistral 7B para conversaciones inteligentes...")
        self.text_tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
        self.text_tokenizer.pad_token = self.text_tokenizer.eos_token

        self.text_model = AutoModelForCausalLM.from_pretrained(
            "mistralai/Mistral-7B-Instruct-v0.1",
            quantization_config=quantization_config,
            device_map="auto",
            low_cpu_mem_usage=True,
            torch_dtype=torch.float16,
            max_memory={0: "12GB", "cpu": "32GB"}
        )

        # Inicializar cerebros expertos
        self.brain_conceptual = BrainConceptual()
        self.brain_mechanical = BrainMechanical()
        self.brain_medical = BrainMedical()

        # Inicializar base de datos
        self.db = DatabaseHandler()

        # TTS con gTTS y pygame
        pygame.mixer.init()
        self.tts_engine = None
        self.voz_activada = False

        # Historial de conversación expandido
        self.historial_conversacion = []

        print("✅ TARS RTX 3060 listo: LLaVA 13B + Mistral 7B + cerebros especializados")

    def generar_respuesta_texto(self, consulta, contexto=""):
        """Genera respuesta usando Mistral 7B con contexto avanzado"""
        try:
            # Historial expandido (10 intercambios vs 3 actuales)
            historial = ""
            if self.historial_conversacion:
                ultimos = self.historial_conversacion[-20:]  # 10 pares de mensajes
                historial = "\n".join([f"Usuario: {msg['user']}\nTARS: {msg['tars']}" for msg in ultimos])

            # Prompt optimizado para Mistral
            system_prompt = f"""<s>[INST] Eres TARS, una IA avanzada inspirada en Interstellar.
            Eres conversacional, amigable y experto en ciencia, tecnología, medicina y exoesqueletos.
            Responde naturalmente en español coloquial, entiende expresiones como "qué onda", "órale".
            Mantén tono amigable y sarcástico como en películas de ciencia ficción.

            Historial reciente:
            {historial}

            Usuario: {consulta} [/INST]"""

            inputs = self.text_tokenizer(system_prompt, return_tensors="pt", padding=True, truncation=True).to(self.device)

            with torch.no_grad():
                outputs = self.text_model.generate(
                    **inputs,
                    max_new_tokens=400,  # Más tokens con RTX 3060
                    temperature=0.8,
                    top_p=0.9,
                    repetition_penalty=1.1,
                    do_sample=True,
                    pad_token_id=self.text_tokenizer.eos_token_id
                )

            respuesta = self.text_tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Limpiar respuesta
            if "[/INST]" in respuesta:
                respuesta = respuesta.split("[/INST]")[-1].strip()

            # Guardar en historial
            self.historial_conversacion.append({"user": consulta, "tars": respuesta})

            return respuesta

        except Exception as e:
            print(f"Error RTX 3060: {e}")
            return "Lo siento, problema técnico. ¿Repites?"

    # Resto de métodos igual que versión actual pero optimizados...
    # [Aquí irían todos los demás métodos adaptados para RTX 3060]

    def hablar(self, texto):
        """TTS optimizado para RTX 3060"""
        try:
            tts = gTTS(text=texto, lang='es', slow=False)
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            pygame.mixer.music.load(audio_buffer, 'mp3')
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)

        except Exception as e:
            print(f"Error TTS RTX 3060: {e}")
            try:
                if not self.tts_engine:
                    self.tts_engine = pyttsx3.init()
                    self.tts_engine.setProperty('rate', 180)
                    self.tts_engine.setProperty('volume', 0.9)
                self.tts_engine.say(texto)
                self.tts_engine.runAndWait()
            except Exception as e2:
                print(f"Error TTS fallback: {e2}")

    def escuchar(self):
        """STT optimizado con mejor configuración"""
        try:
            r = sr.Recognizer()
            r.energy_threshold = 300
            r.dynamic_energy_threshold = True
            r.pause_threshold = 0.8
            r.phrase_threshold = 0.3
            r.non_speaking_duration = 0.5

            with sr.Microphone() as source:
                print("🎤 RTX 3060: Escuchando...")
                r.adjust_for_ambient_noise(source, duration=1)
                print("🎤 RTX 3060: Listo, habla ahora...")

                audio = r.listen(source, timeout=5, phrase_time_limit=15)

                print("🎤 RTX 3060: Procesando...")
                try:
                    texto = r.recognize_google(audio, language='es-ES')
                    print(f"🎤 RTX 3060: '{texto}'")
                    return texto
                except sr.UnknownValueError:
                    try:
                        texto = r.recognize_google(audio, language='en-US')
                        print(f"🎤 RTX 3060: (inglés) '{texto}'")
                        return texto
                    except sr.UnknownValueError:
                        return "No entendí bien. ¿Puedes repetir más claro?"
                except sr.RequestError as e:
                    return f"Error de conexión: {e}"

        except Exception as e:
            print(f"Error STT RTX 3060: {e}")
            return f"Error de voz: {e}"

    # 🚀 MÉTODOS DE ACTUALIZACIÓN DE ENTRENAMIENTO PARA RTX 3060

    def cargar_checkpoint_personalizado(self, checkpoint_path=None):
        """Cargar modelo desde checkpoint personalizado (entrenado en cluster)"""
        try:
            if checkpoint_path is None:
                checkpoint_path = "modelos_personalizados/tars_rtx3060_checkpoint"

            if os.path.exists(checkpoint_path):
                print(f"🔄 RTX 3060: Cargando checkpoint personalizado desde {checkpoint_path}")

                # Cargar modelo de visión personalizado
                if os.path.exists(f"{checkpoint_path}/vision_model"):
                    self.model = LlavaNextForConditionalGeneration.from_pretrained(
                        f"{checkpoint_path}/vision_model",
                        quantization_config=self.model.config.quantization_config,
                        device_map="auto",
                        torch_dtype=torch.float16
                    )
                    print("✅ Modelo de visión personalizado cargado")

                # Cargar modelo de texto personalizado
                if os.path.exists(f"{checkpoint_path}/text_model"):
                    self.text_model = AutoModelForCausalLM.from_pretrained(
                        f"{checkpoint_path}/text_model",
                        quantization_config=self.text_model.config.quantization_config,
                        device_map="auto",
                        torch_dtype=torch.float16
                    )
                    print("✅ Modelo de texto personalizado cargado")

                return True
            else:
                print(f"⚠️ RTX 3060: No se encontró checkpoint en {checkpoint_path}")
                return False

        except Exception as e:
            print(f"❌ Error cargando checkpoint RTX 3060: {e}")
            return False

    def actualizar_entrenamiento_cluster(self, nuevos_datos_path, epochs=1, batch_size=2):
        """Actualizar entrenamiento con datos nuevos del cluster (fine-tuning ligero)"""
        try:
            print(f"🎯 RTX 3060: Iniciando actualización de entrenamiento con datos de {nuevos_datos_path}")

            if not os.path.exists(nuevos_datos_path):
                print(f"❌ No se encontraron datos en {nuevos_datos_path}")
                return False

            # Configurar optimizador con learning rate bajo (fine-tuning)
            optimizer = torch.optim.AdamW([
                {'params': self.model.parameters(), 'lr': 1e-5},  # LR muy bajo para fine-tuning
                {'params': self.text_model.parameters(), 'lr': 1e-5}
            ], weight_decay=0.01)

            # Cargar datos del cluster
            datos_cluster = self._cargar_datos_cluster(nuevos_datos_path)

            if not datos_cluster:
                print("❌ No se pudieron cargar datos del cluster")
                return False

            print(f"📊 RTX 3060: Actualizando con {len(datos_cluster)} muestras nuevas")

            # Fine-tuning ligero
            self.model.train()
            self.text_model.train()

            for epoch in range(epochs):
                total_loss = 0
                for i, batch in enumerate(datos_cluster):
                    try:
                        # Procesar batch de visión
                        if 'imagen' in batch:
                            inputs_vision = self.processor(
                                text=batch.get('texto', ''),
                                images=batch['imagen'],
                                return_tensors="pt"
                            ).to(self.device)

                            outputs_vision = self.model(**inputs_vision, labels=inputs_vision['input_ids'])
                            loss_vision = outputs_vision.loss

                        # Procesar batch de texto
                        if 'texto' in batch:
                            inputs_text = self.text_tokenizer(
                                batch['texto'],
                                return_tensors="pt",
                                padding=True,
                                truncation=True
                            ).to(self.device)

                            outputs_text = self.text_model(**inputs_text, labels=inputs_text['input_ids'])
                            loss_text = outputs_text.loss

                        # Combinar pérdidas
                        loss = (loss_vision + loss_text) / 2 if 'imagen' in batch else loss_text

                        # Backward pass
                        optimizer.zero_grad()
                        loss.backward()
                        optimizer.step()

                        total_loss += loss.item()

                        if i % 10 == 0:
                            print(f"🎯 Epoch {epoch+1}/{epochs}, Batch {i+1}: Loss = {loss.item():.4f}")

                    except Exception as e:
                        print(f"⚠️ Error en batch {i}: {e}")
                        continue

                avg_loss = total_loss / len(datos_cluster)
                print(f"✅ Epoch {epoch+1} completado. Loss promedio: {avg_loss:.4f}")

            # Guardar modelo actualizado
            self.guardar_modelo_actualizado()
            print("💾 Modelo actualizado guardado")

            return True

        except Exception as e:
            print(f"❌ Error en actualización de entrenamiento RTX 3060: {e}")
            return False

    def _cargar_datos_cluster(self, datos_path):
        """Cargar datos de entrenamiento del cluster"""
        try:
            datos = []
            if datos_path.endswith('.json'):
                with open(datos_path, 'r', encoding='utf-8') as f:
                    datos_raw = json.load(f)

                for item in datos_raw:
                    dato = {}
                    if 'imagen_path' in item:
                        try:
                            dato['imagen'] = Image.open(item['imagen_path']).convert('RGB')
                        except:
                            continue
                    if 'texto' in item:
                        dato['texto'] = item['texto']
                    if dato:
                        datos.append(dato)

            elif os.path.isdir(datos_path):
                # Cargar desde directorio
                for file in os.listdir(datos_path):
                    if file.endswith('.json'):
                        with open(os.path.join(datos_path, file), 'r', encoding='utf-8') as f:
                            item = json.load(f)
                            dato = {}
                            if 'imagen_path' in item:
                                try:
                                    dato['imagen'] = Image.open(item['imagen_path']).convert('RGB')
                                except:
                                    continue
                            if 'texto' in item:
                                dato['texto'] = item['texto']
                            if dato:
                                datos.append(dato)

            return datos

        except Exception as e:
            print(f"❌ Error cargando datos del cluster: {e}")
            return []

    def guardar_modelo_actualizado(self, output_path=None):
        """Guardar modelo actualizado después del fine-tuning"""
        try:
            if output_path is None:
                timestamp = "2026_01_07"  # Fecha actual
                output_path = f"modelos_actualizados/tars_rtx3060_{timestamp}"

            os.makedirs(output_path, exist_ok=True)

            print(f"💾 RTX 3060: Guardando modelo actualizado en {output_path}")

            # Guardar modelo de visión
            vision_path = f"{output_path}/vision_model"
            self.model.save_pretrained(vision_path)
            self.processor.save_pretrained(vision_path)

            # Guardar modelo de texto
            text_path = f"{output_path}/text_model"
            self.text_model.save_pretrained(text_path)
            self.text_tokenizer.save_pretrained(text_path)

            # Guardar configuración
            config = {
                "fecha_actualizacion": "2026-01-07",
                "tipo_modelo": "RTX_3060_fine_tuned",
                "version": "2.0",
                "capacidades": ["vision_medical", "conversacion_avanzada", "especialidades_tecnicas"]
            }

            with open(f"{output_path}/config.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print("✅ Modelo actualizado guardado exitosamente")
            return True

        except Exception as e:
            print(f"❌ Error guardando modelo RTX 3060: {e}")
            return False

    def verificar_actualizaciones_cluster(self):
        """Verificar si hay nuevas actualizaciones disponibles del cluster"""
        try:
            update_path = "cluster_updates/"
            if os.path.exists(update_path):
                archivos = [f for f in os.listdir(update_path) if f.endswith('.json')]
                if archivos:
                    print(f"🔄 RTX 3060: {len(archivos)} actualizaciones disponibles del cluster")
                    return archivos
            return []
        except Exception as e:
            print(f"❌ Error verificando actualizaciones: {e}")
            return []

    def aplicar_actualizacion_automatica(self):
        """Aplicar actualización automática si hay datos nuevos del cluster"""
        try:
            actualizaciones = self.verificar_actualizaciones_cluster()
            if actualizaciones:
                print("🚀 RTX 3060: Aplicando actualización automática...")

                for update_file in actualizaciones:
                    update_path = f"cluster_updates/{update_file}"
                    success = self.actualizar_entrenamiento_cluster(update_path, epochs=1)

                    if success:
                        # Mover archivo procesado
                        processed_path = f"cluster_updates/procesados/{update_file}"
                        os.makedirs(os.path.dirname(processed_path), exist_ok=True)
                        os.rename(update_path, processed_path)
                        print(f"✅ Actualización {update_file} aplicada y archivada")
                    else:
                        print(f"❌ Error aplicando actualización {update_file}")

                return True
            else:
                print("📋 RTX 3060: No hay actualizaciones pendientes")
                return False

        except Exception as e:
            print(f"❌ Error en actualización automática: {e}")
            return False

    # [Resto de métodos adaptados para RTX 3060...]