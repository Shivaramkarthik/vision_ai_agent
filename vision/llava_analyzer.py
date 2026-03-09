"""LLaVA vision analysis module for Offline Visual AI Agent 2.0"""

import os
import sys
sys.path.append('..')

try:
    from config import SCREENSHOTS_DIR, USE_LLAVA_FOR_COMPLEX, LLAVA_COMPLEXITY_THRESHOLD
except ImportError:
    SCREENSHOTS_DIR = "screenshots"
    USE_LLAVA_FOR_COMPLEX = True
    LLAVA_COMPLEXITY_THRESHOLD = 20

from llm.ollama_client import get_client
from llm.prompt_templates import build_vision_analysis_prompt


class LLaVAAnalyzer:
    """LLaVA-based visual understanding for complex scenes"""
    
    def __init__(self):
        self.client = get_client()
        self.enabled = USE_LLAVA_FOR_COMPLEX
        self.complexity_threshold = LLAVA_COMPLEXITY_THRESHOLD
        self._last_analysis = None
    
    def should_analyze(self, element_count: int) -> bool:
        """
        Determine if LLaVA analysis is needed based on scene complexity.
        
        Args:
            element_count: Number of detected UI elements
            
        Returns:
            True if LLaVA analysis should be performed
        """
        if not self.enabled:
            return False
        return element_count < self.complexity_threshold
    
    def analyze_screenshot(self, image_path: str, 
                           context: str = "general") -> str:
        """
        Analyze a screenshot using LLaVA.
        
        Args:
            image_path: Path to the screenshot
            context: Analysis context (general, ui_detection, error_check, task_progress)
            
        Returns:
            Analysis result as string
        """
        if not os.path.exists(image_path):
            return "Error: Screenshot not found"
        
        prompt = build_vision_analysis_prompt(context)
        
        try:
            result = self.client.analyze_image(image_path, prompt)
            self._last_analysis = result
            return result
        except Exception as e:
            return f"LLaVA analysis error: {e}"
    
    def describe_screen(self, image_path: str) -> str:
        """
        Get a general description of the screen.
        
        Args:
            image_path: Path to the screenshot
            
        Returns:
            Screen description
        """
        return self.analyze_screenshot(image_path, "general")
    
    def detect_ui_elements(self, image_path: str) -> str:
        """
        Use LLaVA to detect UI elements.
        
        Args:
            image_path: Path to the screenshot
            
        Returns:
            UI element descriptions
        """
        return self.analyze_screenshot(image_path, "ui_detection")
    
    def check_for_errors(self, image_path: str) -> str:
        """
        Check screenshot for error messages or issues.
        
        Args:
            image_path: Path to the screenshot
            
        Returns:
            Error check results
        """
        return self.analyze_screenshot(image_path, "error_check")
    
    def assess_task_progress(self, image_path: str) -> str:
        """
        Assess current task progress from screenshot.
        
        Args:
            image_path: Path to the screenshot
            
        Returns:
            Task progress assessment
        """
        return self.analyze_screenshot(image_path, "task_progress")
    
    def get_last_analysis(self) -> str:
        """Get the last analysis result"""
        return self._last_analysis or ""


# Singleton instance
_analyzer = None

def get_analyzer() -> LLaVAAnalyzer:
    """Get the singleton LLaVAAnalyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = LLaVAAnalyzer()
    return _analyzer
