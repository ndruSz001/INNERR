"""
Vision Analyzer Module (Vision Transformer)
FASE 13: Multimodal Processing - Vision Analysis

Provides image classification, description, and visual understanding using
Vision Transformer (ViT) and CLIP models.

Dependencies:
  - transformers (Hugging Face models)
  - torch (PyTorch)
  - pillow (image utilities)
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


class VisionTask(Enum):
    """Supported vision analysis tasks"""
    CLASSIFICATION = "image-classification"
    DETECTION = "object-detection"
    SEGMENTATION = "semantic-segmentation"
    CAPTIONING = "image-captioning"
    VQA = "visual-question-answering"


@dataclass
class ClassificationResult:
    """Image classification result"""
    label: str
    confidence: float
    top_5: List[Dict[str, float]]
    model: str
    timestamp: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict())


@dataclass
class Caption:
    """Image caption"""
    text: str
    confidence: float
    model: str
    timestamp: str


@dataclass
class VQAAnswer:
    """Visual question answering result"""
    question: str
    answer: str
    confidence: float
    model: str
    timestamp: str


class VisionAnalyzer:
    """Vision understanding using ViT and CLIP"""
    
    def __init__(
        self,
        model_name: str = "google/vit-base-patch16-224",
        device: str = "cuda",
        use_quantization: bool = False
    ):
        """
        Initialize vision analyzer
        
        Args:
            model_name: Hugging Face model ID
            device: Device to run on (cuda, cpu)
            use_quantization: Use model quantization for speed
        """
        self.model_name = model_name
        self.device = device
        self.use_quantization = use_quantization
        self.pipeline = None
        self.clip_model = None
        self.clip_processor = None
        
        self._load_models()
        
        logger.info(
            f"VisionAnalyzer initialized: model={model_name}, "
            f"device={device}, quantization={use_quantization}"
        )
    
    def _load_models(self):
        """Load vision models"""
        try:
            from transformers import pipeline, CLIPProcessor, CLIPModel
            
            # Load ViT classification pipeline
            self.pipeline = pipeline(
                "image-classification",
                model=self.model_name,
                device=0 if self.device == "cuda" else -1
            )
            
            # Load CLIP for multimodal understanding
            self.clip_model = CLIPModel.from_pretrained(
                "openai/clip-vit-base-patch32"
            ).to(self.device)
            self.clip_processor = CLIPProcessor.from_pretrained(
                "openai/clip-vit-base-patch32"
            )
            
            logger.info("Vision models loaded successfully")
        
        except ImportError:
            logger.error("transformers/torch not installed. Install with: pip install transformers torch")
            raise
        except Exception as e:
            logger.error(f"Failed to load vision models: {e}")
            raise
    
    def classify_image(
        self,
        image_path: str,
        top_k: int = 5
    ) -> ClassificationResult:
        """
        Classify image using ViT
        
        Args:
            image_path: Path to image file
            top_k: Number of top predictions
        
        Returns:
            ClassificationResult
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            from PIL import Image
            
            # Load and classify
            image = Image.open(image_path)
            results = self.pipeline(image, top_k=top_k)
            
            # Extract top results
            top_result = results[0]
            top_5 = [
                {"label": r["label"], "confidence": r["score"]}
                for r in results[:5]
            ]
            
            return ClassificationResult(
                label=top_result["label"],
                confidence=top_result["score"],
                top_5=top_5,
                model=self.model_name,
                timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            raise
    
    def describe_image(
        self,
        image_path: str,
        candidate_labels: Optional[List[str]] = None
    ) -> Caption:
        """
        Generate image description using CLIP
        
        Args:
            image_path: Path to image file
            candidate_labels: Labels for CLIP classification
        
        Returns:
            Caption
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            from PIL import Image
            import torch
            
            if candidate_labels is None:
                candidate_labels = [
                    "a photo",
                    "a diagram",
                    "a chart",
                    "a logo",
                    "text content"
                ]
            
            # Load image
            image = Image.open(image_path)
            
            # Process with CLIP
            inputs = self.clip_processor(
                text=candidate_labels,
                images=image,
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            # Get CLIP scores
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
            
            # Get probabilities
            probs = logits_per_image.softmax(dim=1)[0]
            best_idx = probs.argmax().item()
            confidence = probs[best_idx].item()
            
            return Caption(
                text=f"This is {candidate_labels[best_idx]}",
                confidence=confidence,
                model="openai/clip-vit-base-patch32",
                timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            logger.error(f"Image description failed: {e}")
            raise
    
    def answer_question(
        self,
        image_path: str,
        question: str
    ) -> VQAAnswer:
        """
        Answer visual question about image using CLIP
        
        Args:
            image_path: Path to image file
            question: Question about the image
        
        Returns:
            VQAAnswer
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            from PIL import Image
            import torch
            
            # Generate candidate answers
            candidates = [
                "yes",
                "no",
                "maybe",
                "unclear",
                "cannot determine"
            ]
            
            # Load image
            image = Image.open(image_path)
            
            # Create text with question and candidates
            text_inputs = [f"{question} {candidate}" for candidate in candidates]
            
            # Process with CLIP
            inputs = self.clip_processor(
                text=text_inputs,
                images=image,
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            # Get CLIP scores
            with torch.no_grad():
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
            
            # Get best answer
            probs = logits_per_image.softmax(dim=1)[0]
            best_idx = probs.argmax().item()
            confidence = probs[best_idx].item()
            
            return VQAAnswer(
                question=question,
                answer=candidates[best_idx],
                confidence=confidence,
                model="openai/clip-vit-base-patch32",
                timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            logger.error(f"VQA failed: {e}")
            raise
    
    def extract_image_embedding(
        self,
        image_path: str
    ) -> np.ndarray:
        """
        Extract image embedding using CLIP
        
        Args:
            image_path: Path to image file
        
        Returns:
            Image embedding vector
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            from PIL import Image
            import torch
            
            # Load image
            image = Image.open(image_path)
            
            # Process with CLIP
            inputs = self.clip_processor(images=image, return_tensors="pt").to(self.device)
            
            # Get image embedding
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
            
            # Normalize and convert to numpy
            embedding = image_features / image_features.norm(dim=-1, keepdim=True)
            return embedding.cpu().numpy()[0]
        
        except Exception as e:
            logger.error(f"Embedding extraction failed: {e}")
            raise
    
    def batch_classify(
        self,
        image_dir: str,
        pattern: str = "*.jpg"
    ) -> Dict[str, ClassificationResult]:
        """
        Classify multiple images
        
        Args:
            image_dir: Directory with images
            pattern: File pattern
        
        Returns:
            Dictionary mapping filename to result
        """
        image_path = Path(image_dir)
        if not image_path.exists():
            raise FileNotFoundError(f"Directory not found: {image_dir}")
        
        results = {}
        files = list(image_path.glob(pattern))
        
        for i, file_path in enumerate(files, 1):
            try:
                result = self.classify_image(str(file_path))
                results[file_path.name] = result
                logger.info(f"Classified {i}/{len(files)}: {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to classify {file_path.name}: {e}")
                results[file_path.name] = None
        
        return results
    
    def similarity_search(
        self,
        query_image: str,
        image_dir: str,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find similar images using CLIP embeddings
        
        Args:
            query_image: Query image path
            image_dir: Directory with candidate images
            top_k: Number of results
        
        Returns:
            List of (filename, similarity) tuples
        """
        try:
            # Get query embedding
            query_emb = self.extract_image_embedding(query_image)
            
            # Get candidate embeddings
            image_path = Path(image_dir)
            files = list(image_path.glob("*.jpg")) + list(image_path.glob("*.png"))
            
            similarities = []
            for file_path in files:
                if str(file_path) == query_image:
                    continue
                
                try:
                    cand_emb = self.extract_image_embedding(str(file_path))
                    # Cosine similarity
                    similarity = np.dot(query_emb, cand_emb)
                    similarities.append((file_path.name, similarity))
                except Exception:
                    continue
            
            # Sort and return top k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
        
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize analyzer
    analyzer = VisionAnalyzer(device="cpu")
    
    # Example: Classify image
    # result = analyzer.classify_image("path/to/image.jpg")
    # print(f"Classification: {result.label} ({result.confidence:.2%})")
    
    # Example: Describe image
    # caption = analyzer.describe_image("path/to/image.jpg")
    # print(f"Description: {caption.text}")
    
    # Example: Answer question
    # answer = analyzer.answer_question("path/to/image.jpg", "Is there a person?")
    # print(f"Answer: {answer.answer} ({answer.confidence:.2%})")
