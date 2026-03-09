"""Screenshot capture module for Offline Visual AI Agent 2.0"""

import mss
import numpy as np
import cv2
import os
import time
from typing import Optional, Tuple
import sys
sys.path.append('..')

try:
    from config import (
        SCREENSHOTS_DIR, SCREEN_CAPTURE_MONITOR,
        SCREEN_RESIZE_WIDTH, SCREEN_RESIZE_HEIGHT,
        SCREEN_ORIGINAL_WIDTH, SCREEN_ORIGINAL_HEIGHT
    )
except ImportError:
    SCREENSHOTS_DIR = "screenshots"
    SCREEN_CAPTURE_MONITOR = 1
    SCREEN_RESIZE_WIDTH = 960
    SCREEN_RESIZE_HEIGHT = 540
    SCREEN_ORIGINAL_WIDTH = 1920
    SCREEN_ORIGINAL_HEIGHT = 1080


class ScreenCapture:
    """Optimized screen capture with caching and resizing"""
    
    def __init__(self):
        self.screenshots_dir = SCREENSHOTS_DIR
        self.monitor_index = SCREEN_CAPTURE_MONITOR
        self.resize_width = SCREEN_RESIZE_WIDTH
        self.resize_height = SCREEN_RESIZE_HEIGHT
        self._last_capture = None
        self._last_capture_time = 0
        self._scale_x = SCREEN_ORIGINAL_WIDTH / SCREEN_RESIZE_WIDTH
        self._scale_y = SCREEN_ORIGINAL_HEIGHT / SCREEN_RESIZE_HEIGHT
        
        os.makedirs(self.screenshots_dir, exist_ok=True)
    
    def capture(self, resize: bool = True, save: bool = True) -> np.ndarray:
        """
        Capture the screen.
        
        Args:
            resize: Whether to resize for faster processing
            save: Whether to save to disk
            
        Returns:
            Screenshot as numpy array (BGR format)
        """
        with mss.mss() as sct:
            monitor = sct.monitors[self.monitor_index]
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        # Store original for coordinate mapping
        self._last_full_capture = img.copy()
        self._last_capture_time = time.time()
        
        if resize:
            img = cv2.resize(img, (self.resize_width, self.resize_height))
        
        self._last_capture = img
        
        if save:
            path = os.path.join(self.screenshots_dir, "screen.png")
            cv2.imwrite(path, self._last_full_capture)
        
        return img
    
    def capture_full(self, save: bool = True) -> np.ndarray:
        """
        Capture full resolution screen.
        
        Args:
            save: Whether to save to disk
            
        Returns:
            Full resolution screenshot
        """
        return self.capture(resize=False, save=save)
    
    def get_last_capture(self) -> Optional[np.ndarray]:
        """Get the last captured screenshot"""
        return self._last_capture
    
    def get_last_full_capture(self) -> Optional[np.ndarray]:
        """Get the last full resolution capture"""
        return getattr(self, '_last_full_capture', None)
    
    def scale_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """
        Scale coordinates from resized image to original screen.
        
        Args:
            x: X coordinate in resized image
            y: Y coordinate in resized image
            
        Returns:
            Tuple of (x, y) in original screen coordinates
        """
        return int(x * self._scale_x), int(y * self._scale_y)
    
    def get_screenshot_path(self) -> str:
        """Get path to the saved screenshot"""
        return os.path.join(self.screenshots_dir, "screen.png")


# Singleton instance
_capture = None

def get_capture() -> ScreenCapture:
    """Get the singleton ScreenCapture instance"""
    global _capture
    if _capture is None:
        _capture = ScreenCapture()
    return _capture


def capture_screen(resize: bool = True) -> np.ndarray:
    """Convenience function to capture screen"""
    return get_capture().capture(resize=resize)
