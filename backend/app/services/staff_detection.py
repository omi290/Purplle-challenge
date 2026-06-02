import cv2
import numpy as np
import logging
from typing import Tuple
from app.config import settings

logger = logging.getLogger(__name__)

# Try to load CLIP requirements
try:
    from PIL import Image
    import torch
    from transformers import CLIPProcessor, CLIPModel
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    logger.warning("CLIP libraries not fully available. Staff detection will default to Color-based HSV heuristic.")

class StaffDetectionEngine:
    def __init__(self):
        self.method = settings.STAFF_DETECTION_METHOD
        self.model = None
        self.processor = None
        
        if self.method == "clip" and CLIP_AVAILABLE:
            try:
                logger.info("Initializing CLIP Model for zero-shot staff uniform classification...")
                # Use a small clip model for fast inference
                self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                logger.info("CLIP Model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load CLIP Model: {e}. Falling back to Color HSV.")
                self.method = "color"

    def detect_staff_crop(self, frame_crop: np.ndarray) -> Tuple[bool, float]:
        """
        Detects if a cropped frame of a person represents a staff member in uniform.
        Returns: (is_staff, confidence)
        """
        if frame_crop is None or frame_crop.size == 0:
            return False, 0.0

        if self.method == "clip" and self.model is not None and self.processor is not None:
            return self._detect_with_clip(frame_crop)
        else:
            return self._detect_with_color(frame_crop)

    def _detect_with_clip(self, frame_crop: np.ndarray) -> Tuple[bool, float]:
        """
        CLIP zero-shot classification: 'store employee in uniform' vs 'customer shopping'
        """
        try:
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(image_rgb)
            
            inputs = self.processor(
                text=["store employee in uniform", "retail customer shopping"],
                images=pil_img,
                return_tensors="pt",
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=-1)
                
            probs_list = probs[0].tolist()
            is_staff = probs_list[0] > probs_list[1]
            confidence = float(probs_list[0]) if is_staff else float(probs_list[1])
            
            return is_staff, confidence
            
        except Exception as e:
            logger.error(f"CLIP staff detection error: {e}. Falling back to Color HSV.")
            return self._detect_with_color(frame_crop)

    def _detect_with_color(self, frame_crop: np.ndarray) -> Tuple[bool, float]:
        """
        Color HSV Heuristic: Purplle store staff wear bright purple/pink/magenta uniforms.
        Check if dominant color matches the defined HSV range.
        Default ranges:
        Purple/Pink HSV: Hue (120-160), Saturation (50-255), Value (50-255)
        """
        try:
            # Parse lower/upper limits from settings
            lower_str = settings.UNIFORM_COLOR_HSV_LOWER.split(",")
            upper_str = settings.UNIFORM_COLOR_HSV_UPPER.split(",")
            
            lower_hsv = np.array([int(lower_str[0]), int(lower_str[1]), int(lower_str[2])])
            upper_hsv = np.array([int(upper_str[0]), int(upper_str[1]), int(upper_str[2])])
            
            # Resize image to speed up color analysis
            small_crop = cv2.resize(frame_crop, (50, 100))
            hsv = cv2.cvtColor(small_crop, cv2.COLOR_BGR2HSV)
            
            # Mask out the uniform color
            mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
            
            # Calculate ratio of uniform color pixels in the center-chest region (rows 30-70)
            chest_region = mask[30:70, :]
            total_pixels = chest_region.size
            if total_pixels == 0:
                return False, 0.0
                
            color_pixels = cv2.countNonZero(chest_region)
            ratio = color_pixels / total_pixels
            
            # If more than 15% of pixels match, it's highly likely staff uniform
            is_staff = ratio > 0.15
            confidence = min(0.99, 0.5 + ratio * 3.0) if is_staff else min(0.99, 1.0 - ratio)
            
            return is_staff, float(confidence)
            
        except Exception as e:
            logger.error(f"Color staff detection error: {e}")
            # Safe fallback: mock check based on typical uniform patterns
            return False, 0.0

staff_detector = StaffDetectionEngine()
