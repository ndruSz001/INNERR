"""
Multimodal Processing Module
SPRINT 5: Multimodal Input Support (Audio, Image, Fusion)

This module provides comprehensive multimodal processing capabilities:

Components:
- SpeechToText (speech_to_text.py):
  * OpenAI Whisper integration for automatic speech recognition
  * Supports streaming and batch processing
  * 30+ languages, confidence scoring

- TextToSpeech (text_to_speech.py):
  * Multiple TTS engines (Google, Microsoft Edge, Offline)
  * Streaming synthesis for large texts
  * Voice selection and customization

- AudioProcessor (audio_processor.py):
  * Format conversion (WAV, MP3, M4A, OGG, FLAC)
  * Normalization and silence detection
  * Chunking and preprocessing

- ImageHandler (image_handler.py):
  * Image loading and preprocessing for ML models
  * Resizing modes (scale, crop, pad, stretch)
  * Feature extraction (color, edges, histograms, SIFT)
  * Object detection via contours

- VisionAnalyzer (vision_analyzer.py):
  * Vision Transformer (ViT) for image classification
  * CLIP for multimodal understanding
  * Visual question answering (VQA)
  * Similarity search over image collections

- MultimodalFusion (multimodal_fusion.py):
  * Unified multimodal input processing
  * Multiple fusion strategies (early, late, hybrid, attention)
  * Cross-modal analysis and insights
  * Integrated embeddings from all modalities

Architecture:
  User Input (text/audio/image) → Modality Processors → Embeddings → Fusion → Unified Representation

Integration Points:
- Connects to processing.embedding_engine for text encoding
- Connects to project_knowledge for storing multimodal documents
- Connects to api.main for HTTP multimodal endpoints
- WebSocket streaming for real-time audio/video processing

Dependencies:
- openai-whisper: Speech recognition
- gtts + edge-tts + pyttsx3: Text-to-speech engines
- librosa: Audio processing
- pydub: Format conversion
- opencv-python: Image processing
- transformers + torch: Vision models (ViT, CLIP)
- pillow: Image utilities

Example Usage:

    from multimodal.multimodal_fusion import MultimodalFusion
    
    # Initialize
    fusion = MultimodalFusion(fusion_strategy="hybrid")
    
    # Process multimodal input
    result = fusion.process_multimodal_input(
        text="Tell me about this image",
        audio_path="speech.wav",
        image_path="photo.jpg"
    )
    
    # Create embedding
    input_obj = MultimodalInput(
        text="Hello world",
        audio_path="hello.wav",
        image_path="world.jpg"
    )
    embedding = fusion.create_embedding(input_obj)

"""

from .speech_to_text import SpeechToText, TranscriptionResult, WhisperModel
from .text_to_speech import TextToSpeech, TTSEngine, Voice, SynthesisResult
from .audio_processor import AudioProcessor, AudioFormat, AudioMetadata, AudioFrame
from .image_handler import ImageHandler, ImageFormat, ResizeMode, ImageMetadata, DetectedObject
from .vision_analyzer import VisionAnalyzer, VisionTask, ClassificationResult, Caption, VQAAnswer
from .multimodal_fusion import (
    MultimodalFusion,
    MultimodalInput,
    MultimodalEmbedding,
    MultimodalAnalysisResult,
    ModalityType,
    FusionStrategy
)

__all__ = [
    # Speech-to-Text
    "SpeechToText",
    "TranscriptionResult",
    "WhisperModel",
    
    # Text-to-Speech
    "TextToSpeech",
    "TTSEngine",
    "Voice",
    "SynthesisResult",
    
    # Audio Processing
    "AudioProcessor",
    "AudioFormat",
    "AudioMetadata",
    "AudioFrame",
    
    # Image Processing
    "ImageHandler",
    "ImageFormat",
    "ResizeMode",
    "ImageMetadata",
    "DetectedObject",
    
    # Vision Analysis
    "VisionAnalyzer",
    "VisionTask",
    "ClassificationResult",
    "Caption",
    "VQAAnswer",
    
    # Multimodal Fusion
    "MultimodalFusion",
    "MultimodalInput",
    "MultimodalEmbedding",
    "MultimodalAnalysisResult",
    "ModalityType",
    "FusionStrategy",
]

__version__ = "1.0.0"
__description__ = "Multimodal processing for TARS: Speech, Text, Vision integration"
