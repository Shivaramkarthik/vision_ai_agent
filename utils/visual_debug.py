"""Visual debugging utilities for Offline Visual AI Agent 2.0"""

import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import SCREENSHOTS_DIR
except ImportError:
    SCREENSHOTS_DIR = "screenshots"


class VisualDebugger:
    """
    Visual debugging tools for the AI agent.
    """
    
    def __init__(self):
        self.output_dir = SCREENSHOTS_DIR
        self.window_name = "AI Vision Debug"
        self._colors = {
            "button": (0, 255, 0),      # Green
            "textbox": (255, 0, 0),     # Blue
            "text": (0, 255, 255),      # Yellow
            "checkbox": (255, 0, 255),  # Magenta
            "icon": (0, 165, 255),      # Orange
            "menu": (255, 255, 0),      # Cyan
            "link": (128, 0, 128),      # Purple
            "default": (0, 255, 0)      # Green
        }
        os.makedirs(self.output_dir, exist_ok=True)
    
    def draw_elements(self, image: np.ndarray, 
                      elements: List[Dict],
                      show_numbers: bool = True,
                      show_labels: bool = True,
                      show_centers: bool = True) -> np.ndarray:
        """
        Draw UI elements on image.
        
        Args:
            image: Input image
            elements: List of UI elements
            show_numbers: Show element numbers
            show_labels: Show element type labels
            show_centers: Show center click points
            
        Returns:
            Annotated image
        """
        debug_img = image.copy()
        
        for i, e in enumerate(elements):
            x1 = e.get("x1", 0)
            y1 = e.get("y1", 0)
            x2 = e.get("x2", 0)
            y2 = e.get("y2", 0)
            element_type = e.get("type", "unknown")
            text = e.get("text", "")[:30]  # Truncate long text
            
            # Get color for element type
            color = self._colors.get(element_type, self._colors["default"])
            
            # Draw bounding box
            cv2.rectangle(debug_img, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            if show_labels:
                label = f'{element_type}'
                if text:
                    label += f': "{text}"'
                
                # Background for text
                (text_w, text_h), _ = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1
                )
                cv2.rectangle(
                    debug_img, 
                    (x1, y1 - text_h - 4), 
                    (x1 + text_w, y1), 
                    color, -1
                )
                cv2.putText(
                    debug_img, label, (x1, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1
                )
            
            # Draw element number
            if show_numbers:
                number = str(i + 1)
                cv2.circle(debug_img, (x1 + 10, y1 + 10), 10, color, -1)
                cv2.putText(
                    debug_img, number, (x1 + 5, y1 + 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1
                )
            
            # Draw center point
            if show_centers:
                cx = e.get("x", (x1 + x2) // 2)
                cy = e.get("y", (y1 + y2) // 2)
                cv2.circle(debug_img, (cx, cy), 4, (0, 0, 255), -1)
        
        return debug_img
    
    def show(self, image: np.ndarray, 
             elements: List[Dict] = None,
             wait: bool = True):
        """
        Display debug image in window.
        
        Args:
            image: Image to display
            elements: Optional elements to draw
            wait: Wait for key press
        """
        if elements:
            image = self.draw_elements(image, elements)
        
        cv2.imshow(self.window_name, image)
        
        if wait:
            cv2.waitKey(0)
        else:
            cv2.waitKey(1)
    
    def save(self, image: np.ndarray, 
             filename: str,
             elements: List[Dict] = None) -> str:
        """
        Save debug image to file.
        
        Args:
            image: Image to save
            filename: Output filename
            elements: Optional elements to draw
            
        Returns:
            Path to saved file
        """
        if elements:
            image = self.draw_elements(image, elements)
        
        path = os.path.join(self.output_dir, filename)
        cv2.imwrite(path, image)
        return path
    
    def close(self):
        """Close debug window."""
        cv2.destroyWindow(self.window_name)
    
    def close_all(self):
        """Close all OpenCV windows."""
        cv2.destroyAllWindows()


# Singleton instance
_debugger = None

def get_debugger() -> VisualDebugger:
    """Get the singleton VisualDebugger instance."""
    global _debugger
    if _debugger is None:
        _debugger = VisualDebugger()
    return _debugger


def draw_debug(image: np.ndarray, elements: List[Dict]) -> np.ndarray:
    """
    Convenience function to draw debug visualization.
    """
    debugger = get_debugger()
    debug_img = debugger.draw_elements(image, elements)
    debugger.show(debug_img, wait=False)
    return debug_img
