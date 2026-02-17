"""
TarsVoice: Sistema de síntesis de voz para TARS
"""
import os
import subprocess
from typing import Optional

try:
    import pyttsx3
    PYTTSX3_DISPONIBLE = True
except ImportError:
    PYTTSX3_DISPONIBLE = False

try:
    from gtts import gTTS
    import pygame
    from io import BytesIO
    GTTS_DISPONIBLE = True
except ImportError:
    GTTS_DISPONIBLE = False

class TarsVoice:
    """
    Sistema de síntesis de voz para TARS
    """
    def __init__(self, metodo: str = "auto"):
        self.activo = False
        self.metodo = None
        self.engine = None
        if metodo == "auto":
            if PYTTSX3_DISPONIBLE:
                self.metodo = "pyttsx3"
            elif GTTS_DISPONIBLE:
                self.metodo = "gtts"
            else:
                self.metodo = None
        else:
            self.metodo = metodo if self._verificar_disponibilidad(metodo) else None
        if self.metodo == "pyttsx3":
            self._inicializar_pyttsx3()
        elif self.metodo == "gtts":
            self._inicializar_gtts()
    def _verificar_disponibilidad(self, metodo: str) -> bool:
        if metodo == "pyttsx3":
            return PYTTSX3_DISPONIBLE
        elif metodo == "gtts":
            return GTTS_DISPONIBLE
        return False
    def _inicializar_pyttsx3(self):
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            voz_espanol = None
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'español' in voice.name.lower():
                    voz_espanol = voice.id
                    break
            if voz_espanol:
                self.engine.setProperty('voice', voz_espanol)
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)
            print("✅ Voz TARS activada (pyttsx3 - offline)")
            self.activo = True
        except Exception as e:
            print(f"⚠️ Error al inicializar pyttsx3: {e}")
            self.metodo = None
            self.activo = False
    def _inicializar_gtts(self):
        try:
            pygame.mixer.init()
            print("✅ Voz TARS activada (gTTS - online, mejor calidad)")
            self.activo = True
        except Exception as e:
            print(f"⚠️ Error al inicializar gTTS: {e}")
            self.metodo = None
            self.activo = False
    def hablar(self, texto: str):
        if not self.activo or not texto.strip():
            return
        try:
            if self.metodo == "pyttsx3":
                self._hablar_pyttsx3(texto)
            elif self.metodo == "gtts":
                self._hablar_gtts(texto)
        except Exception as e:
            print(f"⚠️ Error al sintetizar voz: {e}")
    def _hablar_pyttsx3(self, texto: str):
        self.engine.say(texto)
        self.engine.runAndWait()
    def _hablar_gtts(self, texto: str):
        try:
            tts = gTTS(text=texto, lang='es', slow=False)
            audio_fp = BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            pygame.mixer.music.load(audio_fp)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"⚠️ Error con gTTS: {e}")
    def activar(self):
        if self.metodo:
            self.activo = True
            print("🔊 Voz activada")
    def desactivar(self):
        self.activo = False
        print("🔇 Voz desactivada")
    def alternar(self):
        if self.activo:
            self.desactivar()
        else:
            self.activar()
    def esta_disponible(self) -> bool:
        return self.metodo is not None
    def obtener_info(self) -> dict:
        return {
            "disponible": self.esta_disponible(),
            "activo": self.activo,
            "metodo": self.metodo,
            "pyttsx3_disponible": PYTTSX3_DISPONIBLE,
            "gtts_disponible": GTTS_DISPONIBLE
        }
