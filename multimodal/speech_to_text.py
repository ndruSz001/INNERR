"""
Speech-to-Text Module (Whisper Integration)
FASE 12: Multimodal Processing - Speech Input

Provides automatic speech recognition using OpenAI's Whisper model.
Supports real-time streaming and batch audio processing.

Dependencies:
  - openai-whisper (ASR engine)
  - librosa (audio preprocessing)
  - pydub (format conversion)
"""

import os
import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Tuple
from enum import Enum
import tempfile
import subprocess

import numpy as np

# Initialize logger
logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    M4A = "m4a"
    OGG = "ogg"
    FLAC = "flac"


class WhisperModel(Enum):
    """Available Whisper model sizes"""
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


@dataclass
class TranscriptionResult:
    """Transcription result with metadata"""
    text: str
    language: str
    confidence: float
    duration: float
    model: str
    timestamp: str
    segments: List[Dict]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


class SpeechToText:
    """OpenAI Whisper-based speech recognition engine"""
    
    def __init__(
        self,
        model_name: str = "base",
        device: str = "cuda",
        language: Optional[str] = None,
        compute_type: str = "float32"
    ):
        """
        Initialize Whisper STT engine
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            device: Device to run on (cuda, cpu)
            language: Language code (e.g., 'es', 'en'). Auto-detect if None
            compute_type: Precision (float32, float16, int8)
        """
        self.model_name = model_name
        self.device = device
        self.language = language
        self.compute_type = compute_type
        self.model = None
        self._load_model()
        
        logger.info(
            f"SpeechToText initialized: model={model_name}, "
            f"device={device}, language={language}"
        )
    
    def _load_model(self):
        """Load Whisper model"""
        try:
            import whisper
            self.model = whisper.load_model(
                self.model_name,
                device=self.device
            )
            logger.info(f"Whisper model '{self.model_name}' loaded successfully")
        except ImportError:
            logger.error("openai-whisper not installed. Install with: pip install openai-whisper")
            raise
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> TranscriptionResult:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Language code (overrides default)
            task: 'transcribe' or 'translate'
        
        Returns:
            TranscriptionResult with transcription and metadata
        """
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            # Transcribe with Whisper
            result = self.model.transcribe(
                audio_path,
                language=language or self.language,
                task=task,
                verbose=False
            )
            
            # Extract key information
            text = result["text"]
            detected_language = result.get("language", "unknown")
            segments = result.get("segments", [])
            
            # Calculate confidence (average segment probabilities)
            confidences = [
                seg.get("confidence", 0.9) 
                for seg in segments 
                if "confidence" in seg
            ]
            avg_confidence = np.mean(confidences) if confidences else 0.95
            
            # Get audio duration
            duration = self._get_audio_duration(audio_path)
            
            return TranscriptionResult(
                text=text,
                language=detected_language,
                confidence=float(avg_confidence),
                duration=duration,
                model=self.model_name,
                timestamp=self._get_timestamp(),
                segments=segments
            )
        
        except Exception as e:
            logger.error(f"Transcription failed for {audio_path}: {e}")
            raise
    
    def stream_transcribe(
        self,
        audio_path: str,
        chunk_duration: float = 30.0
    ) -> List[TranscriptionResult]:
        """
        Transcribe audio in chunks for streaming results
        
        Args:
            audio_path: Path to audio file
            chunk_duration: Duration of each chunk in seconds
        
        Returns:
            List of TranscriptionResult objects
        """
        # Split audio into chunks
        chunks = self._split_audio_file(audio_path, chunk_duration)
        results = []
        
        for i, chunk_path in enumerate(chunks):
            try:
                result = self.transcribe(chunk_path)
                logger.info(f"Transcribed chunk {i+1}/{len(chunks)}")
                results.append(result)
            finally:
                # Clean up temp chunk
                if Path(chunk_path).exists():
                    os.remove(chunk_path)
        
        return results
    
    def batch_transcribe(
        self,
        audio_dir: str,
        pattern: str = "*.wav"
    ) -> Dict[str, TranscriptionResult]:
        """
        Transcribe all audio files in directory
        
        Args:
            audio_dir: Directory containing audio files
            pattern: File pattern (e.g., '*.wav', '*.mp3')
        
        Returns:
            Dictionary mapping filename to TranscriptionResult
        """
        audio_path = Path(audio_dir)
        if not audio_path.exists():
            raise FileNotFoundError(f"Directory not found: {audio_dir}")
        
        results = {}
        files = list(audio_path.glob(pattern))
        
        for i, file_path in enumerate(files, 1):
            try:
                result = self.transcribe(str(file_path))
                results[file_path.name] = result
                logger.info(f"Transcribed {i}/{len(files)}: {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to transcribe {file_path.name}: {e}")
                results[file_path.name] = None
        
        return results
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats"""
        return [fmt.value for fmt in AudioFormat]
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio file duration in seconds"""
        try:
            import librosa
            duration, _ = librosa.get_samplerate(audio_path)
            return float(duration)
        except Exception:
            return 0.0
    
    def _split_audio_file(
        self,
        audio_path: str,
        chunk_duration: float
    ) -> List[str]:
        """Split audio file into chunks"""
        try:
            from pydub import AudioSegment
            
            # Load audio
            audio = AudioSegment.from_file(audio_path)
            duration_ms = len(audio)
            chunk_ms = int(chunk_duration * 1000)
            
            chunks = []
            temp_dir = tempfile.gettempdir()
            
            for i in range(0, duration_ms, chunk_ms):
                chunk = audio[i:i + chunk_ms]
                chunk_path = os.path.join(
                    temp_dir,
                    f"chunk_{i//chunk_ms}.wav"
                )
                chunk.export(chunk_path, format="wav")
                chunks.append(chunk_path)
            
            return chunks
        except ImportError:
            logger.error("pydub not installed. Install with: pip install pydub")
            raise
    
    def _get_timestamp(self) -> str:
        """Get current ISO timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize STT engine
    stt = SpeechToText(model_name="base", device="cpu")
    
    # Example: Transcribe single file
    # result = stt.transcribe("path/to/audio.wav")
    # print(f"Transcription: {result.text}")
    # print(f"Language: {result.language}")
    # print(f"Confidence: {result.confidence:.2%}")
