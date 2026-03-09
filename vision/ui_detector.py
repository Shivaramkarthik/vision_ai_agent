"""UI element detection module for Offline Visual AI Agent 2.0"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
import os
import sys
sys.path.append('..')

try:
    from config import (
        YOLO_MODEL_PATH, YOLO_CONFIDENCE_THRESHOLD, YOLO_IOU_THRESHOLD
    )
except ImportError:
    YOLO_MODEL_PATH = "models/yolov8n.pt"
    YOLO_CONFIDENCE_THRESHOLD = 0.25
    YOLO_IOU_THRESHOLD = 0.45

# Try to import ultralytics for YOLO
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Warning: ultralytics not installed, using OpenCV fallback")


class UIDetector:
    """UI element detection using YOLO or OpenCV fallback"""
    
    def __init__(self, use_yolo: bool = True):
        self.use_yolo = use_yolo and YOLO_AVAILABLE
        self.yolo_model = None
        self.confidence_threshold = YOLO_CONFIDENCE_THRESHOLD
        self.iou_threshold = YOLO_IOU_THRESHOLD
        
        if self.use_yolo:
            self._load_yolo_model()
    
    def _load_yolo_model(self):
        """Load YOLO model for UI detection"""
        try:
            if os.path.exists(YOLO_MODEL_PATH):
                self.yolo_model = YOLO(YOLO_MODEL_PATH)
            else:
                # Use default YOLOv8 nano model
                self.yolo_model = YOLO("yolov8n.pt")
            print("YOLO model loaded successfully")
        except Exception as e:
            print(f"Failed to load YOLO model: {e}")
            self.use_yolo = False
    
    def detect(self, image: np.ndarray) -> List[Tuple[int, int, int, int, str]]:
        """
        Detect UI elements in image.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of (x1, y1, x2, y2, label) tuples
        """
        if self.use_yolo and self.yolo_model is not None:
            return self._detect_yolo(image)
        else:
            return self._detect_opencv(image)
    
    def _detect_yolo(self, image: np.ndarray) -> List[Tuple[int, int, int, int, str]]:
        """
        Detect UI elements using YOLO.
        
        Note: Standard YOLO models detect general objects.
        For UI-specific detection, a custom trained model would be needed.
        This uses general object detection as a fallback.
        """
        results = self.yolo_model(
            image,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            verbose=False
        )
        
        boxes = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = result.names[cls]
                
                # Map general objects to UI elements
                ui_label = self._map_to_ui_element(label, int(x2-x1), int(y2-y1))
                
                boxes.append((int(x1), int(y1), int(x2), int(y2), ui_label))
        
        return boxes
    
    def _detect_opencv(self, image: np.ndarray) -> List[Tuple[int, int, int, int, str]]:
        """
        Detect UI elements using OpenCV contour detection.
        Fallback when YOLO is not available.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)
        
        # Dilate to connect nearby edges
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        boxes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            
            # Filter small detections
            if w < 30 or h < 15:
                continue
            
            # Filter very large detections (likely background)
            if w > image.shape[1] * 0.9 or h > image.shape[0] * 0.9:
                continue
            
            # Classify based on aspect ratio and size
            label = self._classify_by_shape(w, h)
            
            if label != "unknown":
                boxes.append((x, y, x + w, y + h, label))
        
        # Remove overlapping boxes
        boxes = self._non_max_suppression(boxes)
        
        return boxes
    
    def _classify_by_shape(self, width: int, height: int) -> str:
        """
        Classify UI element type based on shape.
        """
        aspect = width / max(height, 1)
        area = width * height
        
        # Checkbox/radio button (square-ish, small)
        if 0.8 < aspect < 1.2 and 15 < width < 50:
            return "checkbox"
        
        # Icon (square-ish, medium)
        if 0.7 < aspect < 1.4 and 20 < width < 80:
            return "icon"
        
        # Button (wider than tall, medium size)
        if aspect > 1.5 and 60 < width < 300 and 20 < height < 60:
            return "button"
        
        # Text field (wide, short)
        if aspect > 3 and width > 100 and height < 50:
            return "textbox"
        
        # Menu item (wide, short)
        if aspect > 2 and width > 80 and 15 < height < 40:
            return "menu_item"
        
        # Generic clickable area
        if area > 500 and area < 50000:
            return "clickable"
        
        return "unknown"
    
    def _map_to_ui_element(self, yolo_label: str, width: int, height: int) -> str:
        """
        Map YOLO object labels to UI element types.
        """
        # For standard YOLO, most detections won't be UI elements
        # This is a placeholder for custom UI-trained models
        ui_mapping = {
            "cell phone": "icon",
            "laptop": "window",
            "tv": "window",
            "keyboard": "textbox",
            "mouse": "clickable",
            "remote": "button",
            "book": "document",
        }
        
        if yolo_label in ui_mapping:
            return ui_mapping[yolo_label]
        
        # Fall back to shape-based classification
        return self._classify_by_shape(width, height)
    
    def _non_max_suppression(self, boxes: List[Tuple], 
                              iou_threshold: float = 0.5) -> List[Tuple]:
        """
        Remove overlapping boxes using non-maximum suppression.
        """
        if len(boxes) == 0:
            return []
        
        # Sort by area (larger first)
        boxes = sorted(boxes, key=lambda b: (b[2]-b[0]) * (b[3]-b[1]), reverse=True)
        
        keep = []
        while boxes:
            current = boxes.pop(0)
            keep.append(current)
            
            boxes = [
                box for box in boxes
                if self._compute_iou(current, box) < iou_threshold
            ]
        
        return keep
    
    def _compute_iou(self, box1: Tuple, box2: Tuple) -> float:
        """
        Compute Intersection over Union between two boxes.
        """
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        
        union = area1 + area2 - intersection
        
        return intersection / max(union, 1)


# Singleton instance
_detector = None

def get_detector() -> UIDetector:
    """Get the singleton UIDetector instance"""
    global _detector
    if _detector is None:
        _detector = UIDetector()
    return _detector


def detect_ui(image: np.ndarray) -> List[Tuple[int, int, int, int, str]]:
    """Convenience function to detect UI elements"""
    return get_detector().detect(image)
