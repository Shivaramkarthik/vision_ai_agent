"""Critic Agent for Offline Visual AI Agent 2.0"""

import cv2
import numpy as np
from typing import Optional, Tuple
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import SCREEN_CHANGE_THRESHOLD, SCREEN_HASH_BITS
except ImportError:
    SCREEN_CHANGE_THRESHOLD = 500000
    SCREEN_HASH_BITS = 64

try:
    import imagehash
    from PIL import Image
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False


class CriticAgent:
    """
    Critic agent responsible for evaluating action success.
    Uses screen comparison and perceptual hashing.
    """
    
    def __init__(self):
        self.change_threshold = SCREEN_CHANGE_THRESHOLD
        self.hash_bits = SCREEN_HASH_BITS
        self._last_hash = None
        self._last_result = ""
    
    def evaluate(self, prev_screen: np.ndarray, 
                 new_screen: np.ndarray,
                 action: str = "") -> str:
        """
        Evaluate whether an action succeeded.
        
        Args:
            prev_screen: Screenshot before action
            new_screen: Screenshot after action
            action: The action that was taken
            
        Returns:
            "SUCCESS" or "FAILED"
        """
        # Check if screens are different
        changed = self.screen_changed(prev_screen, new_screen)
        
        # For most actions, screen change indicates success
        if changed:
            self._last_result = "SUCCESS"
        else:
            # Some actions might not change the screen visibly
            # (e.g., typing in a field that's off-screen)
            if action.lower().startswith("type"):
                # Typing might not always show visible change
                self._last_result = "SUCCESS"
            else:
                self._last_result = "FAILED"
        
        return self._last_result
    
    def screen_changed(self, old_img: np.ndarray, 
                       new_img: np.ndarray) -> bool:
        """
        Check if screen has changed significantly.
        
        Args:
            old_img: Previous screenshot
            new_img: New screenshot
            
        Returns:
            True if screen changed significantly
        """
        # Use perceptual hash if available (faster)
        if IMAGEHASH_AVAILABLE:
            return self._hash_changed(old_img, new_img)
        
        # Fall back to pixel difference
        return self._pixel_diff_changed(old_img, new_img)
    
    def _pixel_diff_changed(self, old_img: np.ndarray, 
                            new_img: np.ndarray) -> bool:
        """
        Check change using pixel difference.
        """
        # Ensure same size
        if old_img.shape != new_img.shape:
            new_img = cv2.resize(new_img, (old_img.shape[1], old_img.shape[0]))
        
        # Compute difference
        diff = cv2.absdiff(old_img, new_img)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        score = np.sum(gray)
        
        return score > self.change_threshold
    
    def _hash_changed(self, old_img: np.ndarray, 
                      new_img: np.ndarray) -> bool:
        """
        Check change using perceptual hash.
        """
        # Convert to PIL Images
        old_pil = Image.fromarray(cv2.cvtColor(old_img, cv2.COLOR_BGR2RGB))
        new_pil = Image.fromarray(cv2.cvtColor(new_img, cv2.COLOR_BGR2RGB))
        
        # Compute perceptual hashes
        old_hash = imagehash.phash(old_pil, hash_size=8)
        new_hash = imagehash.phash(new_pil, hash_size=8)
        
        # Compare hashes (lower difference = more similar)
        hash_diff = old_hash - new_hash
        
        # Threshold for considering screens different
        return hash_diff > 5
    
    def compute_hash(self, image: np.ndarray) -> Optional[str]:
        """
        Compute perceptual hash of an image.
        
        Args:
            image: Input image
            
        Returns:
            Hash string or None
        """
        if not IMAGEHASH_AVAILABLE:
            return None
        
        pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        hash_val = imagehash.phash(pil_img, hash_size=8)
        self._last_hash = str(hash_val)
        return self._last_hash
    
    def get_change_score(self, old_img: np.ndarray, 
                         new_img: np.ndarray) -> float:
        """
        Get a numeric score for how much the screen changed.
        
        Args:
            old_img: Previous screenshot
            new_img: New screenshot
            
        Returns:
            Change score (higher = more change)
        """
        if old_img.shape != new_img.shape:
            new_img = cv2.resize(new_img, (old_img.shape[1], old_img.shape[0]))
        
        diff = cv2.absdiff(old_img, new_img)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        return float(np.sum(gray))
    
    def get_last_result(self) -> str:
        """Get the last evaluation result"""
        return self._last_result
    
    def get_last_hash(self) -> Optional[str]:
        """Get the last computed hash"""
        return self._last_hash
