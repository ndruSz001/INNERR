"""
Text-to-Speech Module (gTTS + TTS Engines)
FASE 12: Multimodal Processing - Speech Output

Provides text-to-speech synthesis with multiple engines:
- Google TTS (free, cloud-based)
- Edge TTS (high quality)
- Pyttsx3 (offline)

Dependencies:
  - gTTS (Google TTS)
  - edge-tts (Microsoft Edge TTS)
  - pyttsx3 (offline TTS)
"""

import os
import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Callable
from enum import Enum
import asyncio
from datetime import datetime

# Initialize logger
logger = logging.getLogger(__name__)


class TTSEngine(Enum):
    """Available TTS engines"""
    GOOGLE = "google"  # gTTS
    EDGE = "edge"      # Microsoft Edge TTS
    OFFLINE = "offline"  # Pyttsx3 (no internet required)


class Voice(Enum):
    """Available voices by language"""
    # English
    EN_US_MALE = "en-US-AriaNeural"
    EN_US_FEMALE = "en-US-SaraNeural"
    EN_GB_MALE = "en-GB-GuyNeural"
    EN_GB_FEMALE = "en-GB-SoniaNeural"
    
    # Spanish
    ES_ES_MALE = "es-ES-AlvaroNeural"
    ES_ES_FEMALE = "es-ES-ElviraNeural"
    ES_MX_MALE = "es-MX-JorgeNeural"
    ES_MX_FEMALE = "es-MX-DaliaNeural"
    
    # Others
    FR_FR_FEMALE = "fr-FR-CelesteNeural"
    DE_DE_MALE = "de-DE-ConradNeural"
    PT_BR_FEMALE = "pt-BR-FranciscaNeural"


@dataclass
class SynthesisResult:
    """TTS synthesis result metadata"""
    audio_path: str
    duration: float
    engine: str
    voice: str
    text_length: int
    sample_rate: int
    timestamp: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict())


class TextToSpeech:
    """Multi-engine text-to-speech synthesis"""
    
    def __init__(
        self,
        engine: str = "google",
        language: str = "en",
        accent: str = "US",
        voice_preference: Optional[str] = None
    ):
        """
        Initialize TTS engine
        
        Args:
            engine: TTS engine to use ('google', 'edge', 'offline')
            language: Language code (e.g., 'en', 'es', 'fr')
            accent: Accent variant (e.g., 'US', 'GB', 'ES')
            voice_preference: Specific voice preference
        """
        self.engine = engine
        self.language = language
        self.accent = accent
        self.voice_preference = voice_preference
        self._engines = {}
        self._load_engines()
        
        logger.info(
            f"TextToSpeech initialized: engine={engine}, "
            f"language={language}, accent={accent}"
        )
    
    def _load_engines(self):
        """Load requested TTS engines"""
        if self.engine in ["google", "all"]:
            try:
                from gtts import gTTS
                self._engines["google"] = gTTS
                logger.info("Google TTS engine loaded")
            except ImportError:
                logger.warning("gTTS not installed. Install with: pip install gtts")
        
        if self.engine in ["edge", "all"]:
            try:
                import edge_tts
                self._engines["edge"] = edge_tts
                logger.info("Edge TTS engine loaded")
            except ImportError:
                logger.warning("edge-tts not installed. Install with: pip install edge-tts")
        
        if self.engine in ["offline", "all"]:
            try:
                import pyttsx3
                self._engines["offline"] = pyttsx3
                logger.info("Offline TTS engine loaded")
            except ImportError:
                logger.warning("pyttsx3 not installed. Install with: pip install pyttsx3")
    
    def synthesize(
        self,
        text: str,
        output_path: str,
        voice: Optional[str] = None,
        slow: bool = False
    ) -> SynthesisResult:
        """
        Synthesize text to speech
        
        Args:
            text: Text to synthesize
            output_path: Output audio file path
            voice: Specific voice (overrides preference)
            slow: Slow down speech (Google TTS only)
        
        Returns:
            SynthesisResult with metadata
        """
        if self.engine == "google":
            return self._synthesize_google(text, output_path, slow)
        elif self.engine == "edge":
            return self._synthesize_edge(text, output_path, voice)
        elif self.engine == "offline":
            return self._synthesize_offline(text, output_path)
        else:
            raise ValueError(f"Unknown TTS engine: {self.engine}")
    
    def _synthesize_google(
        self,
        text: str,
        output_path: str,
        slow: bool = False
    ) -> SynthesisResult:
        """Synthesize using Google TTS"""
        try:
            from gtts import gTTS
            
            # Create gTTS instance
            tts = gTTS(
                text=text,
                lang=self.language,
                slow=slow,
                tld="com"  # Top-level domain
            )
            
            # Create output directory if needed
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            tts.save(output_path)
            
            # Get file info
            duration = self._get_audio_duration(output_path)
            
            return SynthesisResult(
                audio_path=output_path,
                duration=duration,
                engine="google",
                voice=f"{self.language}-{self.accent}",
                text_length=len(text),
                sample_rate=44100,  # Google TTS standard
                timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            logger.error(f"Google TTS synthesis failed: {e}")
            raise
    
    def _synthesize_edge(
        self,
        text: str,
        output_path: str,
        voice: Optional[str] = None
    ) -> SynthesisResult:
        """Synthesize using Edge TTS (async)"""
        try:
            import edge_tts
            
            # Run async synthesis
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context, create new loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self._synthesize_edge_async(
                    text, output_path, voice
                )
            )
            return result
        
        except Exception as e:
            logger.error(f"Edge TTS synthesis failed: {e}")
            raise
    
    async def _synthesize_edge_async(
        self,
        text: str,
        output_path: str,
        voice: Optional[str] = None
    ) -> SynthesisResult:
        """Async Edge TTS synthesis"""
        try:
            import edge_tts
            
            # Select voice
            selected_voice = voice or self.voice_preference or self._get_default_edge_voice()
            
            # Create communicate instance
            communicate = edge_tts.Communicate(text, selected_voice)
            
            # Create output directory
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            await communicate.save(output_path)
            
            # Get duration
            duration = self._get_audio_duration(output_path)
            
            return SynthesisResult(
                audio_path=output_path,
                duration=duration,
                engine="edge",
                voice=selected_voice,
                text_length=len(text),
                sample_rate=48000,  # Edge TTS standard
                timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            logger.error(f"Async Edge TTS synthesis failed: {e}")
            raise
    
    def _synthesize_offline(
        self,
        text: str,
        output_path: str
    ) -> SynthesisResult:
        """Synthesize using offline Pyttsx3"""
        try:
            import pyttsx3
            
            # Initialize engine
            engine = pyttsx3.init()
            
            # Configure engine
            engine.setProperty('rate', 150)  # Speed
            engine.setProperty('volume', 0.9)  # Volume
            
            # Create output directory
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            
            # Get duration (approximation)
            words = len(text.split())
            duration = words / 3.0  # Rough estimate: 3 words per second
            
            return SynthesisResult(
                audio_path=output_path,
                duration=duration,
                engine="offline",
                voice="default",
                text_length=len(text),
                sample_rate=22050,
                timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            logger.error(f"Offline TTS synthesis failed: {e}")
            raise
    
    def stream_synthesis(
        self,
        text: str,
        output_path: str,
        chunk_size: int = 100,
        on_chunk: Optional[Callable] = None
    ) -> SynthesisResult:
        """
        Synthesize text with streaming (for large texts)
        
        Args:
            text: Text to synthesize
            output_path: Output path
            chunk_size: Characters per chunk
            on_chunk: Callback for each processed chunk
        
        Returns:
            SynthesisResult
        """
        # Split text into chunks
        chunks = [
            text[i:i + chunk_size]
            for i in range(0, len(text), chunk_size)
        ]
        
        # Process chunks
        temp_files = []
        for i, chunk in enumerate(chunks):
            temp_path = f"{output_path}.chunk_{i}.mp3"
            result = self.synthesize(chunk, temp_path)
            temp_files.append(temp_path)
            
            if on_chunk:
                on_chunk(i, len(chunks), result)
        
        # Combine chunks (if multiple)
        if len(temp_files) > 1:
            self._combine_audio_files(temp_files, output_path)
            # Clean up temp files
            for temp_file in temp_files:
                if Path(temp_file).exists():
                    os.remove(temp_file)
        elif temp_files:
            import shutil
            shutil.move(temp_files[0], output_path)
        
        # Get final result
        duration = self._get_audio_duration(output_path)
        
        return SynthesisResult(
            audio_path=output_path,
            duration=duration,
            engine=self.engine,
            voice=self.voice_preference or "default",
            text_length=len(text),
            sample_rate=44100,
            timestamp=datetime.now().isoformat()
        )
    
    def get_available_voices(self) -> List[str]:
        """Get list of available voices for current engine"""
        if self.engine == "edge":
            return [v.value for v in Voice]
        else:
            return ["default"]
    
    def _get_default_edge_voice(self) -> str:
        """Get default voice for current language/accent"""
        lang_accent = f"{self.language.upper()}_{self.accent.upper()}"
        
        # Map to voice enum
        voice_map = {
            "EN_US": Voice.EN_US_FEMALE,
            "EN_GB": Voice.EN_GB_FEMALE,
            "ES_ES": Voice.ES_ES_FEMALE,
            "ES_MX": Voice.ES_MX_FEMALE,
            "FR_FR": Voice.FR_FR_FEMALE,
            "DE_DE": Voice.DE_DE_MALE,
            "PT_BR": Voice.PT_BR_FEMALE,
        }
        
        voice = voice_map.get(lang_accent, Voice.EN_US_FEMALE)
        return voice.value
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio file duration"""
        try:
            import librosa
            duration, _ = librosa.load(audio_path, sr=None)
            return float(len(duration) / 22050)  # Default sample rate
        except Exception:
            return 0.0
    
    def _combine_audio_files(self, audio_files: List[str], output_path: str):
        """Combine multiple audio files"""
        try:
            from pydub import AudioSegment
            
            combined = AudioSegment.empty()
            for audio_file in audio_files:
                audio = AudioSegment.from_mp3(audio_file)
                combined += audio
            
            combined.export(output_path, format="mp3")
        except Exception as e:
            logger.error(f"Failed to combine audio files: {e}")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize TTS with Google engine
    tts = TextToSpeech(engine="google", language="en", accent="US")
    
    # Example: Synthesize text
    # result = tts.synthesize(
    #     "Hello, world!",
    #     "/tmp/output.mp3"
    # )
    # print(f"Audio saved to: {result.audio_path}")
    # print(f"Duration: {result.duration:.2f}s")
