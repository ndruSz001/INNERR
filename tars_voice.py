"""
Módulo de síntesis de voz para TARS
Permite que TARS hable sus respuestas
"""

import os
import subprocess
from typing import Optional

# Intentar importar pyttsx3 (síntesis offline)
try:
    import pyttsx3
    PYTTSX3_DISPONIBLE = True
except ImportError:
    PYTTSX3_DISPONIBLE = False

# Intentar importar gTTS (síntesis online, mejor calidad)
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
        """
        Inicializa el sistema de voz
        
        Args:
            metodo: "pyttsx3", "gtts", "auto" (detecta el mejor disponible)
        """
        self.activo = False
        self.metodo = None
        self.engine = None
        
        if metodo == "auto":
            # Preferir pyttsx3 (offline, más rápido)
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
        """Verifica si un método está disponible"""
        if metodo == "pyttsx3":
            return PYTTSX3_DISPONIBLE
        elif metodo == "gtts":
            return GTTS_DISPONIBLE
        return False
    
    def _inicializar_pyttsx3(self):
        """Inicializa pyttsx3 (síntesis offline)"""
        try:
            self.engine = pyttsx3.init()
            
            # Configurar voz
            voices = self.engine.getProperty('voices')
            
            # Intentar encontrar voz en español
            voz_espanol = None
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'español' in voice.name.lower():
                    voz_espanol = voice.id
                    break
            
            if voz_espanol:
                self.engine.setProperty('voice', voz_espanol)
            
            # Configurar velocidad y volumen
            self.engine.setProperty('rate', 150)  # Velocidad (palabras por minuto)
            self.engine.setProperty('volume', 0.9)  # Volumen (0.0 a 1.0)
            
            print("✅ Voz TARS activada (pyttsx3 - offline)")
            self.activo = True
        except Exception as e:
            print(f"⚠️ Error al inicializar pyttsx3: {e}")
            self.metodo = None
            self.activo = False
    
    def _inicializar_gtts(self):
        """Inicializa gTTS (síntesis online, mejor calidad)"""
        try:
            # Inicializar pygame para reproducir audio
            pygame.mixer.init()
            print("✅ Voz TARS activada (gTTS - online, mejor calidad)")
            self.activo = True
        except Exception as e:
            print(f"⚠️ Error al inicializar gTTS: {e}")
            self.metodo = None
            self.activo = False
    
    def hablar(self, texto: str):
        """
        Convierte texto a voz y lo reproduce
        
        Args:
            texto: Texto a sintetizar
        """
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
        """Síntesis con pyttsx3 (offline)"""
        self.engine.say(texto)
        self.engine.runAndWait()
    
    def _hablar_gtts(self, texto: str):
        """Síntesis con gTTS (online, mejor calidad)"""
        try:
            # Generar audio con gTTS
            tts = gTTS(text=texto, lang='es', slow=False)
            
            # Guardar en memoria
            audio_fp = BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            
            # Reproducir con pygame
            pygame.mixer.music.load(audio_fp)
            pygame.mixer.music.play()
            
            # Esperar a que termine
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"⚠️ Error con gTTS: {e}")
    
    def activar(self):
        """Activa la síntesis de voz"""
        if self.metodo:
            self.activo = True
            print("🔊 Voz activada")
    
    def desactivar(self):
        """Desactiva la síntesis de voz"""
        self.activo = False
        print("🔇 Voz desactivada")
    
    def alternar(self):
        """Alterna entre activado/desactivado"""
        if self.activo:
            self.desactivar()
        else:
            self.activar()
    
    def esta_disponible(self) -> bool:
        """Retorna True si hay algún método de voz disponible"""
        return self.metodo is not None
    
    def obtener_info(self) -> dict:
        """Retorna información sobre el sistema de voz"""
        return {
            "disponible": self.esta_disponible(),
            "activo": self.activo,
            "metodo": self.metodo,
            "pyttsx3_disponible": PYTTSX3_DISPONIBLE,
            "gtts_disponible": GTTS_DISPONIBLE
        }
