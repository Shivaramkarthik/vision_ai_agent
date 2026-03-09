"""Vision processing pipeline for Offline Visual AI Agent 2.0"""

import cv2
import numpy as np
from typing import List, Dict, Optional
import time
import sys
sys.path.append('..')

from vision.screenshot import get_capture
from vision.ocr_reader import get_reader
from vision.ui_detector import get_detector
from vision.ui_filter import filter_ui_elements
from vision.ui_semantic import classify_ui_element

try:
    from config import ENABLE_VISION_CACHE, VISION_CACHE_TTL, UI_MAX_ELEMENTS
except ImportError:
    ENABLE_VISION_CACHE = True
    VISION_CACHE_TTL = 2.0
    UI_MAX_ELEMENTS = 100


class VisionProcessor:
    """Optimized vision processing pipeline"""
    
    def __init__(self):
        self.capture = get_capture()
        self.ocr = get_reader()
        self.detector = get_detector()
        
        # Caching
        self._cache_enabled = ENABLE_VISION_CACHE
        self._cache_ttl = VISION_CACHE_TTL
        self._cached_elements = None
        self._cache_time = 0
        
        # Performance tracking
        self._last_process_time = 0
    
    def process(self, image: Optional[np.ndarray] = None, 
                use_cache: bool = True) -> List[Dict]:
        """
        Process screen and extract UI elements.
        
        Args:
            image: Optional image to process (captures new if None)
            use_cache: Whether to use cached results
            
        Returns:
            List of UI element dictionaries
        """
        # Check cache
        if use_cache and self._cache_enabled:
            if self._cached_elements is not None:
                if time.time() - self._cache_time < self._cache_ttl:
                    return self._cached_elements
        
        start_time = time.time()
        
        # Capture screen if not provided
        if image is None:
            image = self.capture.capture(resize=True)
        
        # Run OCR and UI detection
        ocr_results = self.ocr.read_text(image)
        ui_boxes = self.detector.detect(image)
        
        # Combine results
        elements = self._combine_results(ocr_results, ui_boxes)
        
        # Filter and limit
        elements = filter_ui_elements(elements)
        elements = elements[:UI_MAX_ELEMENTS]
        
        # Update cache
        self._cached_elements = elements
        self._cache_time = time.time()
        self._last_process_time = time.time() - start_time
        
        return elements
    
    def _combine_results(self, ocr_results: List, 
                         ui_boxes: List) -> List[Dict]:
        """
        Combine OCR text with UI element detections.
        """
        elements = []
        used_text = set()
        
        # Process UI boxes and attach text
        for x1, y1, x2, y2, label in ui_boxes:
            attached_text = ""
            
            for i, (text, (tx, ty, tw, th)) in enumerate(ocr_results):
                if self._text_inside_box((tx, ty, tw, th), (x1, y1, x2, y2)):
                    attached_text += text + " "
                    used_text.add(i)
            
            attached_text = attached_text.strip()
            width = int(x2 - x1)
            height = int(y2 - y1)
            
            # Get semantic type
            semantic_type = classify_ui_element(label, attached_text, width, height)
            
            elements.append({
                "type": semantic_type,
                "text": attached_text,
                "x": int((x1 + x2) / 2),
                "y": int((y1 + y2) / 2),
                "width": width,
                "height": height,
                "x1": int(x1),
                "y1": int(y1),
                "x2": int(x2),
                "y2": int(y2),
                "confidence": 1.0
            })
        
        # Add remaining OCR text as standalone elements
        for i, (text, (x, y, w, h)) in enumerate(ocr_results):
            if i in used_text:
                continue
            
            elements.append({
                "type": "text",
                "text": text,
                "x": x + w // 2,
                "y": y + h // 2,
                "width": w,
                "height": h,
                "x1": x,
                "y1": y,
                "x2": x + w,
                "y2": y + h,
                "confidence": 0.8
            })
        
        return elements
    
    def _text_inside_box(self, text_box: tuple, ui_box: tuple) -> bool:
        """
        Check if text center is inside UI box.
        """
        tx, ty, tw, th = text_box
        ux1, uy1, ux2, uy2 = ui_box
        
        cx = tx + tw // 2
        cy = ty + th // 2
        
        return ux1 <= cx <= ux2 and uy1 <= cy <= uy2
    
    def get_element_at(self, x: int, y: int) -> Optional[Dict]:
        """
        Get UI element at specific coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Element dict or None
        """
        elements = self.process(use_cache=True)
        
        for element in elements:
            if (element["x1"] <= x <= element["x2"] and
                element["y1"] <= y <= element["y2"]):
                return element
        
        return None
    
    def find_element_by_text(self, text: str, 
                              partial: bool = True) -> Optional[Dict]:
        """
        Find UI element by text content.
        
        Args:
            text: Text to search for
            partial: Allow partial matches
            
        Returns:
            Element dict or None
        """
        elements = self.process(use_cache=True)
        text_lower = text.lower()
        
        for element in elements:
            element_text = element.get("text", "").lower()
            if partial:
                if text_lower in element_text:
                    return element
            else:
                if text_lower == element_text:
                    return element
        
        return None
    
    def get_last_process_time(self) -> float:
        """Get time taken for last processing"""
        return self._last_process_time
    
    def clear_cache(self):
        """Clear the element cache"""
        self._cached_elements = None
        self._cache_time = 0


# Singleton instance
_processor = None

def get_processor() -> VisionProcessor:
    """Get the singleton VisionProcessor instance"""
    global _processor
    if _processor is None:
        _processor = VisionProcessor()
    return _processor


def process_screen(image: Optional[np.ndarray] = None) -> List[Dict]:
    """Convenience function to process screen"""
    return get_processor().process(image)
