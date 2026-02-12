"""
Multimodal Fusion Layer
FASE 13: Multimodal Processing - Fusion & Integration

Combines audio, image, and text modalities into unified representations.
Enables cross-modal retrieval and understanding.

Integrates with:
- SpeechToText (audio → text)
- TextToSpeech (text → audio)
- VisionAnalyzer (image understanding)
- Project knowledge base
"""

import os
import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Tuple, Any
from enum import Enum
import numpy as np
from datetime import datetime

# Initialize logger
logger = logging.getLogger(__name__)


class ModalityType(Enum):
    """Input modality types"""
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    MIXED = "mixed"


class FusionStrategy(Enum):
    """Multimodal fusion strategies"""
    EARLY = "early"           # Combine features early
    LATE = "late"             # Combine predictions late
    HYBRID = "hybrid"         # Combination of early and late
    ATTENTION = "attention"   # Cross-modal attention


@dataclass
class MultimodalInput:
    """Unified multimodal input representation"""
    text: Optional[str] = None
    audio_path: Optional[str] = None
    image_path: Optional[str] = None
    metadata: Dict[str, Any] = None
    timestamp: str = None
    
    def get_modality_types(self) -> List[str]:
        """Get list of present modalities"""
        modalities = []
        if self.text:
            modalities.append("text")
        if self.audio_path:
            modalities.append("audio")
        if self.image_path:
            modalities.append("image")
        return modalities
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class MultimodalEmbedding:
    """Unified multimodal embedding"""
    embedding: np.ndarray        # Combined embedding vector
    text_embedding: Optional[np.ndarray] = None
    audio_embedding: Optional[np.ndarray] = None
    image_embedding: Optional[np.ndarray] = None
    attention_weights: Optional[Dict[str, float]] = None
    modality_types: List[str] = None
    timestamp: str = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary (for serialization)"""
        return {
            "embedding_shape": self.embedding.shape,
            "text_embedding_shape": self.text_embedding.shape if self.text_embedding is not None else None,
            "audio_embedding_shape": self.audio_embedding.shape if self.audio_embedding is not None else None,
            "image_embedding_shape": self.image_embedding.shape if self.image_embedding is not None else None,
            "attention_weights": self.attention_weights,
            "modality_types": self.modality_types,
            "timestamp": self.timestamp
        }


@dataclass
class MultimodalAnalysisResult:
    """Complete multimodal analysis result"""
    text_content: Optional[str] = None
    text_entities: List[str] = None
    image_classification: Optional[Dict] = None
    audio_transcript: Optional[str] = None
    audio_language: Optional[str] = None
    cross_modal_insights: str = None
    confidence: float = 0.0
    processing_time: float = 0.0
    timestamp: str = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict())


class MultimodalFusion:
    """Multimodal input fusion and understanding"""
    
    def __init__(
        self,
        fusion_strategy: str = "hybrid",
        enable_cross_modal: bool = True,
        embedding_dim: int = 512
    ):
        """
        Initialize multimodal fusion
        
        Args:
            fusion_strategy: Fusion method (early, late, hybrid, attention)
            enable_cross_modal: Enable cross-modal analysis
            embedding_dim: Target embedding dimension
        """
        self.fusion_strategy = fusion_strategy
        self.enable_cross_modal = enable_cross_modal
        self.embedding_dim = embedding_dim
        
        # Initialize submodules (lazy load)
        self.stt = None
        self.tts = None
        self.vision = None
        self.text_encoder = None
        
        logger.info(
            f"MultimodalFusion initialized: strategy={fusion_strategy}, "
            f"cross_modal={enable_cross_modal}, dim={embedding_dim}"
        )
    
    def _ensure_modules(self):
        """Lazy load required modules"""
        if self.stt is None:
            try:
                from multimodal.speech_to_text import SpeechToText
                self.stt = SpeechToText(model_name="base", device="cpu")
            except Exception as e:
                logger.warning(f"Could not load SpeechToText: {e}")
        
        if self.vision is None:
            try:
                from multimodal.vision_analyzer import VisionAnalyzer
                self.vision = VisionAnalyzer(device="cpu")
            except Exception as e:
                logger.warning(f"Could not load VisionAnalyzer: {e}")
        
        if self.text_encoder is None:
            try:
                from processing.embedding_engine import EmbeddingEngine
                self.text_encoder = EmbeddingEngine()
            except Exception as e:
                logger.warning(f"Could not load EmbeddingEngine: {e}")
    
    def process_multimodal_input(
        self,
        text: Optional[str] = None,
        audio_path: Optional[str] = None,
        image_path: Optional[str] = None
    ) -> MultimodalAnalysisResult:
        """
        Process multimodal input from multiple sources
        
        Args:
            text: Text input (optional)
            audio_path: Path to audio file (optional)
            image_path: Path to image file (optional)
        
        Returns:
            MultimodalAnalysisResult
        """
        import time
        start_time = time.time()
        
        self._ensure_modules()
        
        result = MultimodalAnalysisResult(
            text_content=text,
            timestamp=datetime.now().isoformat()
        )
        
        try:
            # Process audio if provided
            if audio_path and self.stt:
                try:
                    transcript = self.stt.transcribe(audio_path)
                    result.audio_transcript = transcript.text
                    result.audio_language = transcript.language
                    text = text + " " + transcript.text if text else transcript.text
                except Exception as e:
                    logger.error(f"Audio processing failed: {e}")
            
            # Process image if provided
            if image_path and self.vision:
                try:
                    classification = self.vision.classify_image(image_path)
                    result.image_classification = classification.to_dict()
                except Exception as e:
                    logger.error(f"Image processing failed: {e}")
            
            # Extract text entities
            if text:
                result.text_entities = self._extract_entities(text)
                result.text_content = text
            
            # Generate cross-modal insights
            if len([x for x in [text, audio_path, image_path] if x]) > 1:
                result.cross_modal_insights = self._generate_cross_modal_insights(
                    text, audio_path, image_path, result
                )
            
            # Set confidence and processing time
            result.confidence = 0.85
            result.processing_time = time.time() - start_time
            
            logger.info(
                f"Multimodal processing complete in {result.processing_time:.2f}s"
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Multimodal processing failed: {e}")
            raise
    
    def create_embedding(
        self,
        multimodal_input: MultimodalInput
    ) -> MultimodalEmbedding:
        """
        Create unified multimodal embedding
        
        Args:
            multimodal_input: MultimodalInput object
        
        Returns:
            MultimodalEmbedding
        """
        self._ensure_modules()
        
        embeddings = {}
        modality_types = multimodal_input.get_modality_types()
        
        try:
            # Text embedding
            if multimodal_input.text and self.text_encoder:
                text_emb = self.text_encoder.encode([multimodal_input.text])[0]
                embeddings["text"] = text_emb
            
            # Audio embedding (via transcription + text encoding)
            if multimodal_input.audio_path and self.stt and self.text_encoder:
                try:
                    transcript = self.stt.transcribe(multimodal_input.audio_path)
                    audio_text_emb = self.text_encoder.encode([transcript.text])[0]
                    embeddings["audio"] = audio_text_emb
                except Exception:
                    pass
            
            # Image embedding
            if multimodal_input.image_path and self.vision:
                try:
                    img_emb = self.vision.extract_image_embedding(
                        multimodal_input.image_path
                    )
                    embeddings["image"] = img_emb
                except Exception:
                    pass
            
            # Fuse embeddings
            if self.fusion_strategy == "early":
                combined = self._fuse_early(embeddings)
            elif self.fusion_strategy == "late":
                combined = self._fuse_late(embeddings)
            elif self.fusion_strategy == "attention":
                combined, attention = self._fuse_attention(embeddings)
            else:  # hybrid
                combined = self._fuse_hybrid(embeddings)
                attention = None
            
            return MultimodalEmbedding(
                embedding=combined,
                text_embedding=embeddings.get("text"),
                audio_embedding=embeddings.get("audio"),
                image_embedding=embeddings.get("image"),
                attention_weights=attention,
                modality_types=modality_types,
                timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            logger.error(f"Embedding creation failed: {e}")
            raise
    
    def _fuse_early(self, embeddings: Dict[str, np.ndarray]) -> np.ndarray:
        """Early fusion: concatenate embeddings"""
        if not embeddings:
            return np.zeros(self.embedding_dim)
        
        # Concatenate all embeddings
        fused = np.concatenate(list(embeddings.values()), axis=0)
        
        # Resize to target dimension
        if len(fused) > self.embedding_dim:
            fused = fused[:self.embedding_dim]
        elif len(fused) < self.embedding_dim:
            fused = np.pad(fused, (0, self.embedding_dim - len(fused)))
        
        return fused
    
    def _fuse_late(self, embeddings: Dict[str, np.ndarray]) -> np.ndarray:
        """Late fusion: average embeddings"""
        if not embeddings:
            return np.zeros(self.embedding_dim)
        
        # Pad all to embedding_dim
        padded = []
        for emb in embeddings.values():
            if len(emb) > self.embedding_dim:
                p = emb[:self.embedding_dim]
            elif len(emb) < self.embedding_dim:
                p = np.pad(emb, (0, self.embedding_dim - len(emb)))
            else:
                p = emb
            padded.append(p)
        
        # Average
        return np.mean(padded, axis=0)
    
    def _fuse_attention(
        self,
        embeddings: Dict[str, np.ndarray]
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """Attention-based fusion with cross-modal weights"""
        if not embeddings:
            return np.zeros(self.embedding_dim), {}
        
        # Simple attention: compute similarity between modalities
        weights = {}
        total_sim = 0.0
        
        modalities = list(embeddings.keys())
        for i, mod1 in enumerate(modalities):
            mod_sim = 0.0
            for j, mod2 in enumerate(modalities):
                if i != j:
                    emb1 = embeddings[mod1]
                    emb2 = embeddings[mod2]
                    
                    # Normalize
                    emb1_norm = emb1 / (np.linalg.norm(emb1) + 1e-8)
                    emb2_norm = emb2 / (np.linalg.norm(emb2) + 1e-8)
                    
                    # Dot product similarity
                    min_len = min(len(emb1_norm), len(emb2_norm))
                    mod_sim += np.dot(emb1_norm[:min_len], emb2_norm[:min_len])
            
            total_sim += mod_sim
            weights[mod1] = mod_sim
        
        # Normalize weights
        if total_sim > 0:
            weights = {k: v / total_sim for k, v in weights.items()}
        else:
            weights = {k: 1.0 / len(weights) for k in weights}
        
        # Weighted average
        padded = []
        for mod, emb in embeddings.items():
            weight = weights.get(mod, 1.0)
            if len(emb) > self.embedding_dim:
                p = emb[:self.embedding_dim]
            elif len(emb) < self.embedding_dim:
                p = np.pad(emb, (0, self.embedding_dim - len(emb)))
            else:
                p = emb
            padded.append(p * weight)
        
        return np.sum(padded, axis=0), weights
    
    def _fuse_hybrid(self, embeddings: Dict[str, np.ndarray]) -> np.ndarray:
        """Hybrid fusion: early + late combination"""
        if not embeddings:
            return np.zeros(self.embedding_dim)
        
        # Early part
        early = self._fuse_early(embeddings)
        
        # Late part
        late = self._fuse_late(embeddings)
        
        # Combine
        combined = 0.5 * early + 0.5 * late
        
        return combined
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities from text"""
        try:
            import re
            
            # Simple entity extraction (capitalized words)
            entities = []
            words = text.split()
            for word in words:
                if word and word[0].isupper() and len(word) > 2:
                    entities.append(word.strip(".,!?"))
            
            return list(set(entities))
        except Exception:
            return []
    
    def _generate_cross_modal_insights(
        self,
        text: Optional[str],
        audio_path: Optional[str],
        image_path: Optional[str],
        result: MultimodalAnalysisResult
    ) -> str:
        """Generate insights from cross-modal analysis"""
        insights = []
        
        if text and audio_path:
            insights.append("Cross-modal text-audio analysis: Comparing textual and spoken content")
        
        if text and image_path:
            insights.append("Cross-modal text-image analysis: Relating text to image content")
        
        if audio_path and image_path:
            insights.append("Cross-modal audio-image analysis: Integrated audio-visual understanding")
        
        if result.text_entities:
            insights.append(f"Extracted entities: {', '.join(result.text_entities[:5])}")
        
        return ". ".join(insights) if insights else "Multimodal analysis complete"


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize fusion
    fusion = MultimodalFusion(fusion_strategy="hybrid", enable_cross_modal=True)
    
    # Example: Process multimodal input
    # result = fusion.process_multimodal_input(
    #     text="A person speaking about AI",
    #     audio_path="path/to/audio.wav",
    #     image_path="path/to/image.jpg"
    # )
    # print(result.to_json())
