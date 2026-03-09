"""Vision Agent for Offline Visual AI Agent 2.0"""

import numpy as np
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from vision.vision_processor import get_processor
    from vision.llava_analyzer import get_analyzer
    from vision.screenshot import get_capture
    NEW_STRUCTURE = True
except ImportError:
    from vision_processor import process_screen as _legacy_process
    NEW_STRUCTURE = False

try:
    from config import USE_LLAVA_FOR_COMPLEX, LLAVA_COMPLEXITY_THRESHOLD
except ImportError:
    USE_LLAVA_FOR_COMPLEX = False
    LLAVA_COMPLEXITY_THRESHOLD = 20


class VisionAgent:
    """
    Vision agent responsible for observing and understanding the screen.
    Combines OCR, UI detection, and optional LLaVA analysis.
    """
    
    def __init__(self):
        if NEW_STRUCTURE:
            self.processor = get_processor()
            self.llava = get_analyzer()
            self.capture = get_capture()
        else:
            self.processor = None
            self.llava = None
            self.capture = None
        
        self.use_llava = USE_LLAVA_FOR_COMPLEX
        self.llava_threshold = LLAVA_COMPLEXITY_THRESHOLD
        self._last_elements = []
        self._last_analysis = ""
    
    def observe(self, image: Optional[np.ndarray] = None) -> List[Dict]:
        """
        Observe the screen and extract UI elements.
        
        Args:
            image: Optional image to process (captures new if None)
            
        Returns:
            List of UI element dictionaries
        """
        if self.processor:
            elements = self.processor.process(image)
        else:
            elements = _legacy_process(image)
        
        self._last_elements = elements
        
        # Use LLaVA for complex scenes if enabled
        if self.use_llava and self.llava and len(elements) < self.llava_threshold:
            if self.capture:
                screenshot_path = self.capture.get_screenshot_path()
                self._last_analysis = self.llava.describe_screen(screenshot_path)
        
        return elements
    
    def get_element_by_index(self, index: int) -> Optional[Dict]:
        """
        Get element by index (1-based for user commands).
        
        Args:
            index: 1-based element index
            
        Returns:
            Element dict or None
        """
        idx = index - 1
        if 0 <= idx < len(self._last_elements):
            return self._last_elements[idx]
        return None
    
    def find_element(self, text: str) -> Optional[Dict]:
        """
        Find element by text content.
        
        Args:
            text: Text to search for
            
        Returns:
            Element dict or None
        """
        if self.processor:
            return self.processor.find_element_by_text(text)
        
        # Fallback search
        text_lower = text.lower()
        for e in self._last_elements:
            if text_lower in e.get("text", "").lower():
                return e
        return None
    
    def get_last_elements(self) -> List[Dict]:
        """Get the last observed elements"""
        return self._last_elements
    
    def get_last_analysis(self) -> str:
        """Get the last LLaVA analysis"""
        return self._last_analysis
    
    def format_elements_for_prompt(self, max_elements: int = 50) -> str:
        """
        Format elements for LLM prompt.
        
        Args:
            max_elements: Maximum elements to include
            
        Returns:
            Formatted string
        """
        lines = []
        for i, e in enumerate(self._last_elements[:max_elements]):
            element_type = e.get("type", "unknown")
            element_text = e.get("text", "")[:50]
            lines.append(f'{i+1}. {element_type} "{element_text}"')
        return "\n".join(lines)
