"""OCR text extraction module for Offline Visual AI Agent 2.0"""

import pytesseract
import cv2
import numpy as np
from typing import List, Tuple, Dict
import sys
sys.path.append('..')

try:
    from config import TESSERACT_PATH, OCR_CONFIDENCE_THRESHOLD, OCR_MIN_TEXT_LENGTH
except ImportError:
    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    OCR_CONFIDENCE_THRESHOLD = 30
    OCR_MIN_TEXT_LENGTH = 1

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


class OCRReader:
    """Optimized OCR text extraction"""
    
    def __init__(self):
        self.confidence_threshold = OCR_CONFIDENCE_THRESHOLD
        self.min_text_length = OCR_MIN_TEXT_LENGTH
        self._cache = {}
        self._cache_hash = None
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Preprocessed grayscale image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply slight blur to reduce noise
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Apply adaptive thresholding for better text detection
        # gray = cv2.adaptiveThreshold(
        #     gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        #     cv2.THRESH_BINARY, 11, 2
        # )
        
        return gray
    
    def read_text(self, image: np.ndarray, 
                  use_preprocessing: bool = True) -> List[Tuple[str, Tuple[int, int, int, int]]]:
        """
        Extract text and bounding boxes from image.
        
        Args:
            image: Input image (BGR format)
            use_preprocessing: Whether to preprocess the image
            
        Returns:
            List of (text, (x, y, width, height)) tuples
        """
        if use_preprocessing:
            processed = self.preprocess_image(image)
        else:
            processed = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Get OCR data with confidence scores
        data = pytesseract.image_to_data(
            processed, 
            output_type=pytesseract.Output.DICT,
            config='--psm 11'  # Sparse text mode
        )
        
        results = []
        n_boxes = len(data["text"])
        
        for i in range(n_boxes):
            text = data["text"][i].strip()
            conf = int(data["conf"][i]) if data["conf"][i] != '-1' else 0
            
            # Filter by confidence and text length
            if conf < self.confidence_threshold:
                continue
            if len(text) < self.min_text_length:
                continue
            if text == "":
                continue
            
            x = data["left"][i]
            y = data["top"][i]
            w = data["width"][i]
            h = data["height"][i]
            
            results.append((text, (x, y, w, h)))
        
        return results
    
    def read_text_simple(self, image: np.ndarray) -> str:
        """
        Extract all text from image as a single string.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Extracted text as string
        """
        gray = self.preprocess_image(image)
        text = pytesseract.image_to_string(gray)
        return text.strip()
    
    def get_text_regions(self, image: np.ndarray) -> List[Dict]:
        """
        Get text regions with detailed information.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of dictionaries with text region info
        """
        results = self.read_text(image)
        
        regions = []
        for text, (x, y, w, h) in results:
            regions.append({
                "text": text,
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "center_x": x + w // 2,
                "center_y": y + h // 2,
                "x1": x,
                "y1": y,
                "x2": x + w,
                "y2": y + h
            })
        
        return regions


# Singleton instance
_reader = None

def get_reader() -> OCRReader:
    """Get the singleton OCRReader instance"""
    global _reader
    if _reader is None:
        _reader = OCRReader()
    return _reader


def read_text(image: np.ndarray) -> List[Tuple[str, Tuple[int, int, int, int]]]:
    """Convenience function to read text from image"""
    return get_reader().read_text(image)
