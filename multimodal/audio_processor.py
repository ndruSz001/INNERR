"""
Audio Processing Utilities
FASE 12: Multimodal Processing - Audio Utils

Provides audio file handling, conversion, normalization, and preprocessing.
Supports WAV, MP3, M4A, OGG, FLAC formats.

Dependencies:
  - librosa (audio processing)
  - pydub (format conversion)
  - numpy (signal processing)
  - scipy (audio analysis)
"""

import os
import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Tuple
from enum import Enum
import numpy as np
from datetime import datetime

# Initialize logger
logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    M4A = "m4a"
    OGG = "ogg"
    FLAC = "flac"


@dataclass
class AudioMetadata:
    """Audio file metadata"""
    file_path: str
    format: str
    duration: float
    sample_rate: int
    channels: int
    bit_depth: int
    size_mb: float
    created_at: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict())


@dataclass
class AudioFrame:
    """Audio frame (chunk)"""
    data: np.ndarray
    sample_rate: int
    duration: float
    start_time: float
    end_time: float
    frame_index: int


class AudioProcessor:
    """Audio processing and conversion utilities"""
    
    def __init__(self, sample_rate: int = 16000, mono: bool = True):
        """
        Initialize audio processor
        
        Args:
            sample_rate: Target sample rate (Hz)
            mono: Convert to mono
        """
        self.sample_rate = sample_rate
        self.mono = mono
        
        logger.info(
            f"AudioProcessor initialized: "
            f"sample_rate={sample_rate}, mono={mono}"
        )
    
    def load_audio(
        self,
        file_path: str,
        sr: Optional[int] = None,
        mono: Optional[bool] = None
    ) -> Tuple[np.ndarray, int]:
        """
        Load audio file
        
        Args:
            file_path: Path to audio file
            sr: Sample rate (uses default if None)
            mono: Convert to mono (uses default if None)
        
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        try:
            import librosa
            
            # Use provided values or defaults
            sr = sr or self.sample_rate
            mono = mono if mono is not None else self.mono
            
            # Load audio
            audio, sr = librosa.load(
                file_path,
                sr=sr,
                mono=mono
            )
            
            logger.info(
                f"Loaded audio: {Path(file_path).name} "
                f"({len(audio)/sr:.2f}s @ {sr}Hz)"
            )
            
            return audio, sr
        
        except ImportError:
            raise ImportError("librosa not installed. Install with: pip install librosa")
        except Exception as e:
            logger.error(f"Failed to load audio: {e}")
            raise
    
    def save_audio(
        self,
        audio: np.ndarray,
        file_path: str,
        sr: int,
        format: str = "wav"
    ) -> str:
        """
        Save audio to file
        
        Args:
            audio: Audio data (numpy array)
            file_path: Output file path
            sr: Sample rate
            format: Output format (wav, mp3, etc.)
        
        Returns:
            Path to saved file
        """
        try:
            import librosa
            
            # Create output directory
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save audio
            librosa.output.write_wav(file_path, audio, sr)
            
            logger.info(f"Audio saved to: {file_path}")
            return file_path
        
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            raise
    
    def convert_format(
        self,
        input_path: str,
        output_path: str,
        output_format: str = "wav"
    ) -> str:
        """
        Convert audio file format
        
        Args:
            input_path: Input file path
            output_path: Output file path
            output_format: Target format
        
        Returns:
            Path to converted file
        """
        try:
            from pydub import AudioSegment
            
            # Load and export
            audio = AudioSegment.from_file(input_path)
            
            # Create output directory
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Export in new format
            audio.export(output_path, format=output_format)
            
            logger.info(
                f"Converted {Path(input_path).name} → {Path(output_path).name}"
            )
            return output_path
        
        except ImportError:
            raise ImportError("pydub not installed. Install with: pip install pydub")
        except Exception as e:
            logger.error(f"Format conversion failed: {e}")
            raise
    
    def normalize_audio(
        self,
        audio: np.ndarray,
        target_db: float = -20.0
    ) -> np.ndarray:
        """
        Normalize audio to target loudness (dB)
        
        Args:
            audio: Audio data
            target_db: Target loudness in dB
        
        Returns:
            Normalized audio
        """
        try:
            import librosa
            
            # Calculate RMS
            S = librosa.feature.melspectrogram(y=audio, sr=self.sample_rate)
            rms = librosa.feature.rms(S=S)[0]
            mean_rms = np.mean(rms)
            
            # Calculate scaling factor
            target_rms = 10 ** (target_db / 20)
            if mean_rms > 0:
                scale_factor = target_rms / mean_rms
            else:
                scale_factor = 1.0
            
            # Apply scaling
            normalized = audio * scale_factor
            
            # Prevent clipping
            max_val = np.max(np.abs(normalized))
            if max_val > 1.0:
                normalized = normalized / max_val
            
            logger.info(f"Audio normalized to {target_db}dB")
            return normalized
        
        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            return audio
    
    def detect_silence(
        self,
        audio: np.ndarray,
        threshold_db: float = -40.0,
        min_duration: float = 0.5
    ) -> List[Tuple[float, float]]:
        """
        Detect silent segments
        
        Args:
            audio: Audio data
            threshold_db: Silence threshold in dB
            min_duration: Minimum silence duration in seconds
        
        Returns:
            List of (start_time, end_time) tuples
        """
        try:
            import librosa
            from scipy import signal
            
            # Calculate energy
            S = librosa.feature.melspectrogram(y=audio, sr=self.sample_rate)
            energy = np.sqrt(np.sum(S**2, axis=0))
            
            # Convert to dB
            energy_db = librosa.power_to_db(energy)
            
            # Find silent frames
            silent_frames = energy_db < threshold_db
            
            # Group consecutive silent frames
            min_samples = int(min_duration * self.sample_rate / 512)
            labeled, num_segments = label(silent_frames)
            
            # Extract segments
            segments = []
            for i in range(1, num_segments + 1):
                frames = np.where(labeled == i)[0]
                if len(frames) >= min_samples:
                    start_frame = frames[0]
                    end_frame = frames[-1]
                    start_time = start_frame * 512 / self.sample_rate
                    end_time = end_frame * 512 / self.sample_rate
                    segments.append((start_time, end_time))
            
            logger.info(f"Detected {len(segments)} silent segments")
            return segments
        
        except Exception as e:
            logger.error(f"Silence detection failed: {e}")
            return []
    
    def chunk_audio(
        self,
        audio: np.ndarray,
        chunk_duration: float,
        overlap: float = 0.0
    ) -> List[AudioFrame]:
        """
        Split audio into overlapping chunks
        
        Args:
            audio: Audio data
            chunk_duration: Chunk duration in seconds
            overlap: Overlap ratio (0.0-1.0)
        
        Returns:
            List of AudioFrame objects
        """
        chunk_samples = int(chunk_duration * self.sample_rate)
        overlap_samples = int(chunk_samples * overlap)
        stride = chunk_samples - overlap_samples
        
        frames = []
        
        for i, start in enumerate(range(0, len(audio) - chunk_samples, stride)):
            end = start + chunk_samples
            frame_data = audio[start:end]
            
            frame = AudioFrame(
                data=frame_data,
                sample_rate=self.sample_rate,
                duration=chunk_duration,
                start_time=start / self.sample_rate,
                end_time=end / self.sample_rate,
                frame_index=i
            )
            frames.append(frame)
        
        logger.info(f"Split audio into {len(frames)} frames")
        return frames
    
    def get_metadata(self, file_path: str) -> AudioMetadata:
        """Get audio file metadata"""
        try:
            import librosa
            
            if not Path(file_path).exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Load metadata
            y, sr = librosa.load(file_path)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Get file info
            file_size = Path(file_path).stat().st_size / (1024 * 1024)  # MB
            created_at = datetime.fromtimestamp(
                Path(file_path).stat().st_ctime
            ).isoformat()
            
            # Estimate bit depth and channels
            bit_depth = 16  # Assume 16-bit
            channels = 1 if self.mono else 2
            
            return AudioMetadata(
                file_path=file_path,
                format=Path(file_path).suffix.lstrip("."),
                duration=duration,
                sample_rate=sr,
                channels=channels,
                bit_depth=bit_depth,
                size_mb=file_size,
                created_at=created_at
            )
        
        except Exception as e:
            logger.error(f"Failed to get metadata: {e}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported formats"""
        return [fmt.value for fmt in AudioFormat]


def label(arr):
    """Simple connected component labeling"""
    labeled = np.zeros_like(arr, dtype=int)
    current_label = 0
    
    for i in range(len(arr)):
        if arr[i] and labeled[i] == 0:
            current_label += 1
            labeled[i] = current_label
            
            # Propagate label
            j = i + 1
            while j < len(arr) and arr[j]:
                labeled[j] = current_label
                j += 1
    
    return labeled, current_label


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize processor
    processor = AudioProcessor(sample_rate=16000, mono=True)
    
    # Example: Load and process audio
    # audio, sr = processor.load_audio("path/to/audio.wav")
    # normalized = processor.normalize_audio(audio)
    # chunks = processor.chunk_audio(normalized, chunk_duration=5.0)
    # print(f"Created {len(chunks)} chunks")
