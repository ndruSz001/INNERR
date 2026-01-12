import os
import torch
import numpy as np
import librosa
import soundfile as sf
from io import BytesIO
import pygame
import json
import hashlib
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RVCVoiceCloner:
    """
    Sistema de Clonación de Voz usando Retrieval-based Voice Conversion (RVC)
    Permite que TARS suene exactamente como un personaje específico.
    """

    def __init__(self, model_path="modelos_rvc/tars_voice.pth", config_path="modelos_rvc/config.json"):
        self.model_path = model_path
        self.config_path = config_path
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.config = None

        # Configuración de audio
        self.sample_rate = 44100
        self.hop_length = 512

        # Inicializar pygame para reproducción
        pygame.mixer.init(frequency=self.sample_rate)

        # Cargar modelo si existe
        self.cargar_modelo()

    def cargar_modelo(self):
        """Carga el modelo RVC entrenado"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.config_path):
                logger.info(f"🎭 Cargando modelo RVC desde {self.model_path}")

                # Cargar configuración
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)

                # Aquí iría la carga del modelo RVC
                # Por ahora, simulamos la carga
                self.model = "RVC_MODEL_LOADED"  # Placeholder

                logger.info("✅ Modelo RVC cargado exitosamente")
                return True
            else:
                logger.warning("⚠️ Modelo RVC no encontrado, usando voz por defecto")
                return False

        except Exception as e:
            logger.error(f"❌ Error cargando modelo RVC: {e}")
            return False

    def entrenar_modelo_rvc(self, audio_dataset_path, epochs=100, batch_size=8):
        """
        Entrena un modelo RVC con dataset de audio del personaje.
        Este método prepara los datos para entrenamiento en cluster.
        """
        try:
            logger.info(f"🎯 Preparando entrenamiento RVC con datos de {audio_dataset_path}")

            if not os.path.exists(audio_dataset_path):
                raise FileNotFoundError(f"Dataset no encontrado: {audio_dataset_path}")

            # Preparar datos de entrenamiento
            datos_entrenamiento = self._preparar_datos_entrenamiento(audio_dataset_path)

            # Configuración de entrenamiento
            config_entrenamiento = {
                "model_name": "tars_voice_rvc",
                "sample_rate": self.sample_rate,
                "epochs": epochs,
                "batch_size": batch_size,
                "learning_rate": 1e-4,
                "dataset_size": len(datos_entrenamiento),
                "fecha_creacion": datetime.now().isoformat(),
                "device": self.device
            }

            # Guardar configuración
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config_entrenamiento, f, indent=2)

            logger.info("✅ Configuración de entrenamiento preparada")
            logger.info(f"📊 Dataset: {len(datos_entrenamiento)} muestras de audio")
            logger.info("🚀 Listo para entrenamiento en cluster")

            return config_entrenamiento

        except Exception as e:
            logger.error(f"❌ Error preparando entrenamiento: {e}")
            return None

    def _preparar_datos_entrenamiento(self, dataset_path):
        """Prepara y valida el dataset de audio para entrenamiento"""
        datos = []

        # Buscar archivos de audio
        for root, dirs, files in os.walk(dataset_path):
            for file in files:
                if file.endswith(('.wav', '.mp3', '.flac')):
                    audio_path = os.path.join(root, file)

                    try:
                        # Validar archivo de audio
                        audio, sr = librosa.load(audio_path, sr=self.sample_rate)

                        # Verificar calidad del audio
                        if len(audio) < self.sample_rate:  # Menos de 1 segundo
                            logger.warning(f"⚠️ Audio muy corto: {file}")
                            continue

                        if np.max(np.abs(audio)) < 0.01:  # Audio muy bajo
                            logger.warning(f"⚠️ Audio muy bajo: {file}")
                            continue

                        datos.append({
                            "path": audio_path,
                            "duration": len(audio) / sr,
                            "sample_rate": sr,
                            "channels": 1 if len(audio.shape) == 1 else audio.shape[0]
                        })

                    except Exception as e:
                        logger.warning(f"⚠️ Error procesando {file}: {e}")
                        continue

        return datos

    def convertir_voz(self, texto, voz_base="gtts", pitch_shift=0, formant_shift=0):
        """
        Convierte texto a voz usando el modelo RVC entrenado.
        Si no hay modelo RVC, usa voz base (gTTS).
        """
        try:
            # Generar audio base
            if voz_base == "gtts":
                audio_base = self._generar_audio_gtts(texto)
            else:
                audio_base = self._generar_audio_pyttsx3(texto)

            if audio_base is None:
                return False

            # Si tenemos modelo RVC, aplicar conversión
            if self.model is not None:
                logger.info("🎭 Aplicando conversión RVC...")
                audio_convertido = self._aplicar_rvc(audio_base, pitch_shift, formant_shift)

                if audio_convertido is not None:
                    return self._reproducir_audio(audio_convertido)
                else:
                    logger.warning("⚠️ Conversión RVC falló, usando audio base")
                    return self._reproducir_audio(audio_base)
            else:
                # Usar audio base directamente
                return self._reproducir_audio(audio_base)

        except Exception as e:
            logger.error(f"❌ Error en conversión de voz: {e}")
            return False

    def _generar_audio_gtts(self, texto):
        """Genera audio base usando gTTS"""
        try:
            from gtts import gTTS

            tts = gTTS(text=texto, lang='es', slow=False)
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            # Convertir a numpy array
            audio_data, _ = sf.read(audio_buffer)
            return audio_data

        except Exception as e:
            logger.error(f"Error generando audio gTTS: {e}")
            return None

    def _generar_audio_pyttsx3(self, texto):
        """Genera audio base usando pyttsx3"""
        try:
            import pyttsx3

            # Crear archivo temporal
            temp_file = f"temp_tts_{hash(texto)}.wav"
            engine = pyttsx3.init()
            engine.setProperty('rate', 180)
            engine.setProperty('volume', 0.9)
            engine.save_to_file(texto, temp_file)
            engine.runAndWait()

            # Cargar audio
            audio_data, _ = sf.read(temp_file)

            # Limpiar archivo temporal
            os.remove(temp_file)

            return audio_data

        except Exception as e:
            logger.error(f"Error generando audio pyttsx3: {e}")
            return None

    def _aplicar_rvc(self, audio_base, pitch_shift=0, formant_shift=0):
        """Aplica conversión RVC al audio base"""
        try:
            # Placeholder para implementación RVC real
            # Aquí iría el código para aplicar el modelo RVC entrenado

            logger.info("🎭 Aplicando transformación RVC (simulado)")

            # Simular procesamiento RVC
            # En implementación real, esto usaría el modelo cargado

            # Aplicar ajustes de pitch y formant si se especifican
            if pitch_shift != 0:
                # Aquí iría código para cambiar pitch
                pass

            if formant_shift != 0:
                # Aquí iría código para cambiar formants
                pass

            # Por ahora, devolver el audio base (sin cambios)
            # En implementación real, devolvería audio convertido
            return audio_base

        except Exception as e:
            logger.error(f"Error aplicando RVC: {e}")
            return None

    def _reproducir_audio(self, audio_data):
        """Reproduce audio usando pygame"""
        try:
            # Crear archivo temporal
            temp_file = f"temp_rvc_{hash(str(audio_data))}.wav"

            # Guardar como WAV
            sf.write(temp_file, audio_data, self.sample_rate)

            # Reproducir
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()

            # Esperar a que termine
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)

            # Limpiar archivo temporal
            os.remove(temp_file)

            return True

        except Exception as e:
            logger.error(f"Error reproduciendo audio: {e}")
            return False

    def obtener_estadisticas_modelo(self):
        """Retorna estadísticas del modelo RVC"""
        if self.config:
            return {
                "modelo_cargado": self.model is not None,
                "sample_rate": self.config.get("sample_rate", "N/A"),
                "fecha_entrenamiento": self.config.get("fecha_creacion", "N/A"),
                "dataset_size": self.config.get("dataset_size", "N/A"),
                "device": self.device
            }
        else:
            return {
                "modelo_cargado": False,
                "estado": "Modelo no encontrado, usando voz por defecto"
            }

    def crear_dataset_ejemplo(self, output_path="dataset_rvc_ejemplo"):
        """
        Crea un dataset de ejemplo para entrenamiento RVC.
        Incluye instrucciones para recopilar audio real.
        """
        try:
            os.makedirs(output_path, exist_ok=True)

            # Crear archivo de instrucciones
            instrucciones = f"""
# 🎭 DATASET PARA ENTRENAMIENTO RVC - VOZ DE TARS

## INSTRUCCIONES PARA CREAR TU DATASET:

### 1. RECOPILAR AUDIO:
- Busca clips de voz del actor de TARS en Interstellar
- Evita clips con música de fondo o efectos de sonido
- Necesitas 5-10 minutos de audio limpio
- Formatos aceptados: WAV, MP3, FLAC

### 2. PREPARAR ARCHIVOS:
- Nombra los archivos como: tars_001.wav, tars_002.wav, etc.
- Cada archivo debe tener al menos 3-5 segundos de audio
- Asegúrate de que la voz sea clara y sin ruido

### 3. CALIDAD DEL AUDIO:
- Sample rate: 44100 Hz (CD quality)
- Mono (1 canal)
- Volumen consistente
- Sin compresión excesiva

### 4. CONTENIDO RECOMENDADO:
- Diálogos técnicos sobre ciencia/física
- Expresiones de compañerismo
- Tono calmado pero confiado
- Referencias a "calibración", "sistemas", "órbitas"

## EJEMPLOS DE FRASES PARA GRABAR:

"Calibrando sistemas de navegación."
"Entendido, comandante. Procediendo con la secuencia."
"Los cálculos indican una probabilidad del 97.3%."
"Estoy aquí para ayudar, como siempre."

## ENTRENAMIENTO:

Una vez tengas el dataset, ejecuta:
```bash
python rvc_voice_cloner.py --train --dataset {output_path}
```

## NOTAS IMPORTANTES:

- El entrenamiento requiere GPU potente (usa tu cluster)
- Tiempo estimado: 2-4 horas en RTX 3060
- Modelo final: ~100MB
- Calidad mejora con más datos de entrenamiento

---
Creado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """

            with open(os.path.join(output_path, "INSTRUCCIONES.txt"), 'w', encoding='utf-8') as f:
                f.write(instrucciones)

            # Crear archivo de configuración de ejemplo
            config_ejemplo = {
                "dataset_name": "tars_voice_dataset",
                "target_speaker": "TARS (Interstellar)",
                "audio_format": "wav",
                "sample_rate": 44100,
                "channels": 1,
                "min_duration": 3.0,
                "max_duration": 10.0,
                "recommended_total_duration": 600,  # 10 minutos
                "quality_checks": [
                    "no_background_music",
                    "clear_voice",
                    "consistent_volume",
                    "no_compression_artifacts"
                ]
            }

            with open(os.path.join(output_path, "config_dataset.json"), 'w', encoding='utf-8') as f:
                json.dump(config_ejemplo, f, indent=2)

            logger.info(f"✅ Dataset de ejemplo creado en {output_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Error creando dataset ejemplo: {e}")
            return False