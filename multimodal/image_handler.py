"""
Image Handler Module (OpenCV-based)
FASE 13: Multimodal Processing - Vision Input

Provides image loading, preprocessing, and feature extraction.
Supports JPEG, PNG, WebP, TIFF formats.

Dependencies:
  - opencv-python (image processing)
  - pillow (image utilities)
  - numpy (array operations)
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


class ImageFormat(Enum):
    """Supported image formats"""
    JPEG = "jpg"
    PNG = "png"
    WEBP = "webp"
    TIFF = "tiff"
    BMP = "bmp"


class ResizeMode(Enum):
    """Image resizing modes"""
    SCALE = "scale"           # Scale with aspect ratio
    CROP = "crop"             # Crop to size
    PAD = "pad"               # Pad with borders
    STRETCH = "stretch"       # Stretch to size


@dataclass
class ImageMetadata:
    """Image file metadata"""
    file_path: str
    width: int
    height: int
    channels: int
    dtype: str
    format: str
    size_mb: float
    aspect_ratio: float
    created_at: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict())


@dataclass
class DetectedObject:
    """Detected object in image"""
    label: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    color: Tuple[int, int, int]
    area: int


class ImageHandler:
    """Image processing and analysis"""
    
    def __init__(
        self,
        target_size: Tuple[int, int] = (224, 224),
        normalize: bool = True
    ):
        """
        Initialize image handler
        
        Args:
            target_size: Default resize target (width, height)
            normalize: Normalize pixel values to [0, 1]
        """
        self.target_size = target_size
        self.normalize = normalize
        
        logger.info(
            f"ImageHandler initialized: target_size={target_size}, "
            f"normalize={normalize}"
        )
    
    def load_image(
        self,
        image_path: str,
        color_mode: str = "rgb"
    ) -> np.ndarray:
        """
        Load image from file
        
        Args:
            image_path: Path to image file
            color_mode: 'rgb', 'bgr', or 'gray'
        
        Returns:
            Image as numpy array
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            import cv2
            
            # Load image (BGR by default)
            img = cv2.imread(image_path)
            
            if img is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            # Convert color space if needed
            if color_mode == "rgb":
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            elif color_mode == "gray":
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            logger.info(
                f"Loaded image: {Path(image_path).name} "
                f"({img.shape[1]}x{img.shape[0]})"
            )
            
            return img
        
        except ImportError:
            raise ImportError("opencv-python not installed. Install with: pip install opencv-python")
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            raise
    
    def save_image(
        self,
        image: np.ndarray,
        file_path: str,
        color_mode: str = "rgb"
    ) -> str:
        """
        Save image to file
        
        Args:
            image: Image as numpy array
            file_path: Output file path
            color_mode: Input color mode ('rgb', 'bgr', 'gray')
        
        Returns:
            Path to saved file
        """
        try:
            import cv2
            
            # Create output directory
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert back to BGR for OpenCV
            if color_mode == "rgb" and len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Save image
            cv2.imwrite(file_path, image)
            
            logger.info(f"Image saved to: {file_path}")
            return file_path
        
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            raise
    
    def resize_image(
        self,
        image: np.ndarray,
        size: Tuple[int, int],
        mode: str = "scale"
    ) -> np.ndarray:
        """
        Resize image
        
        Args:
            image: Image array
            size: Target size (width, height)
            mode: Resize mode (scale, crop, pad, stretch)
        
        Returns:
            Resized image
        """
        try:
            import cv2
            
            h, w = image.shape[:2]
            target_w, target_h = size
            
            if mode == "scale":
                # Scale with aspect ratio preservation
                scale = min(target_w / w, target_h / h)
                new_w = int(w * scale)
                new_h = int(h * scale)
                resized = cv2.resize(image, (new_w, new_h))
                
                # Pad to target size
                if len(resized.shape) == 3:
                    resized = cv2.copyMakeBorder(
                        resized, 
                        (target_h - new_h) // 2,
                        (target_h - new_h + 1) // 2,
                        (target_w - new_w) // 2,
                        (target_w - new_w + 1) // 2,
                        cv2.BORDER_CONSTANT,
                        value=(0, 0, 0)
                    )
                else:
                    resized = cv2.copyMakeBorder(
                        resized,
                        (target_h - new_h) // 2,
                        (target_h - new_h + 1) // 2,
                        (target_w - new_w) // 2,
                        (target_w - new_w + 1) // 2,
                        cv2.BORDER_CONSTANT,
                        value=0
                    )
            
            elif mode == "crop":
                # Crop to target size
                start_y = max(0, (h - target_h) // 2)
                start_x = max(0, (w - target_w) // 2)
                resized = image[start_y:start_y+target_h, start_x:start_x+target_w]
            
            elif mode == "pad":
                # Pad to target size
                resized = cv2.copyMakeBorder(
                    image,
                    (target_h - h) // 2,
                    (target_h - h + 1) // 2,
                    (target_w - w) // 2,
                    (target_w - w + 1) // 2,
                    cv2.BORDER_CONSTANT,
                    value=0
                )
            
            elif mode == "stretch":
                # Stretch to exact size
                resized = cv2.resize(image, (target_w, target_h))
            
            else:
                raise ValueError(f"Unknown resize mode: {mode}")
            
            logger.info(f"Image resized to {size} ({mode})")
            return resized
        
        except Exception as e:
            logger.error(f"Resize failed: {e}")
            raise
    
    def extract_features(
        self,
        image: np.ndarray,
        feature_type: str = "color"
    ) -> Dict[str, np.ndarray]:
        """
        Extract image features
        
        Args:
            image: Image array
            feature_type: 'color', 'edge', 'histogram', 'sift'
        
        Returns:
            Dictionary of extracted features
        """
        try:
            import cv2
            
            features = {}
            
            if feature_type == "color":
                # Color statistics
                features["mean_color"] = np.mean(image, axis=(0, 1))
                features["std_color"] = np.std(image, axis=(0, 1))
            
            elif feature_type == "edge":
                # Edge detection
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
                edges = cv2.Canny(gray, 100, 200)
                features["edges"] = edges
                features["edge_density"] = np.sum(edges > 0) / edges.size
            
            elif feature_type == "histogram":
                # Color histograms
                if len(image.shape) == 3:
                    features["hist_r"] = cv2.calcHist([image], [0], None, [256], [0, 256])
                    features["hist_g"] = cv2.calcHist([image], [1], None, [256], [0, 256])
                    features["hist_b"] = cv2.calcHist([image], [2], None, [256], [0, 256])
            
            elif feature_type == "sift":
                # SIFT keypoints
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
                sift = cv2.SIFT_create()
                kp, des = sift.detectAndCompute(gray, None)
                features["keypoints"] = len(kp)
                features["descriptors"] = des
            
            logger.info(f"Extracted {feature_type} features")
            return features
        
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return {}
    
    def detect_objects(
        self,
        image: np.ndarray,
        min_area: int = 100
    ) -> List[DetectedObject]:
        """
        Detect objects using contours
        
        Args:
            image: Image array
            min_area: Minimum object area
        
        Returns:
            List of DetectedObject
        """
        try:
            import cv2
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
            
            # Threshold
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            objects = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area >= min_area:
                    x, y, w, h = cv2.boundingRect(cnt)
                    
                    obj = DetectedObject(
                        label=f"object_{len(objects)}",
                        confidence=0.9,
                        bbox=(x, y, w, h),
                        color=(0, 255, 0),
                        area=int(area)
                    )
                    objects.append(obj)
            
            logger.info(f"Detected {len(objects)} objects")
            return objects
        
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            return []
    
    def preprocess_for_model(
        self,
        image: np.ndarray,
        target_size: Optional[Tuple[int, int]] = None,
        normalize_range: Tuple[float, float] = (0, 1)
    ) -> np.ndarray:
        """
        Preprocess image for ML model
        
        Args:
            image: Image array
            target_size: Resize to this size (uses default if None)
            normalize_range: Normalize to this range
        
        Returns:
            Preprocessed image
        """
        # Resize
        if target_size:
            image = self.resize_image(image, target_size)
        elif image.shape[:2] != self.target_size[::-1]:
            image = self.resize_image(image, self.target_size)
        
        # Normalize
        if self.normalize:
            min_val, max_val = normalize_range
            image = (image.astype(np.float32) / 255.0) * (max_val - min_val) + min_val
        
        return image
    
    def get_metadata(self, image_path: str) -> ImageMetadata:
        """Get image metadata"""
        try:
            img = self.load_image(image_path)
            
            h, w = img.shape[:2]
            channels = img.shape[2] if len(img.shape) == 3 else 1
            file_size = Path(image_path).stat().st_size / (1024 * 1024)
            aspect_ratio = w / h if h > 0 else 0
            created_at = datetime.fromtimestamp(
                Path(image_path).stat().st_ctime
            ).isoformat()
            
            return ImageMetadata(
                file_path=image_path,
                width=w,
                height=h,
                channels=channels,
                dtype=str(img.dtype),
                format=Path(image_path).suffix.lstrip("."),
                size_mb=file_size,
                aspect_ratio=aspect_ratio,
                created_at=created_at
            )
        
        except Exception as e:
            logger.error(f"Failed to get metadata: {e}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported formats"""
        return [fmt.value for fmt in ImageFormat]


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize handler
    handler = ImageHandler(target_size=(224, 224), normalize=True)
    
    # Example: Load and process image
    # img = handler.load_image("path/to/image.jpg")
    # resized = handler.resize_image(img, (256, 256), mode="scale")
    # features = handler.extract_features(img, feature_type="color")
    # objects = handler.detect_objects(img)
