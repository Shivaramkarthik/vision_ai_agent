"""Screen hashing utilities for Offline Visual AI Agent 2.0"""

import cv2
import numpy as np
from typing import Optional, Tuple
import hashlib

try:
    import imagehash
    from PIL import Image
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False


class ScreenHash:
    """
    Fast screen change detection using perceptual hashing.
    """
    
    def __init__(self, hash_size: int = 8):
        self.hash_size = hash_size
        self._last_hash = None
        self._hash_history = []
        self._max_history = 10
    
    def compute_hash(self, image: np.ndarray) -> str:
        """
        Compute perceptual hash of an image.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Hash string
        """
        if IMAGEHASH_AVAILABLE:
            return self._compute_phash(image)
        else:
            return self._compute_simple_hash(image)
    
    def _compute_phash(self, image: np.ndarray) -> str:
        """
        Compute perceptual hash using imagehash library.
        """
        pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        hash_val = imagehash.phash(pil_img, hash_size=self.hash_size)
        return str(hash_val)
    
    def _compute_simple_hash(self, image: np.ndarray) -> str:
        """
        Compute simple hash when imagehash is not available.
        Uses downscaled grayscale image.
        """
        # Resize to small size
        small = cv2.resize(image, (16, 16))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        
        # Compute mean
        mean = np.mean(gray)
        
        # Create binary hash
        binary = (gray > mean).flatten()
        hash_bytes = np.packbits(binary).tobytes()
        
        return hashlib.md5(hash_bytes).hexdigest()[:16]
    
    def has_changed(self, image: np.ndarray, 
                    threshold: int = 5) -> bool:
        """
        Check if screen has changed from last hash.
        
        Args:
            image: Current screenshot
            threshold: Hash difference threshold
            
        Returns:
            True if screen changed
        """
        current_hash = self.compute_hash(image)
        
        if self._last_hash is None:
            self._last_hash = current_hash
            self._add_to_history(current_hash)
            return True
        
        changed = self._compare_hashes(self._last_hash, current_hash, threshold)
        
        self._last_hash = current_hash
        self._add_to_history(current_hash)
        
        return changed
    
    def _compare_hashes(self, hash1: str, hash2: str, 
                        threshold: int) -> bool:
        """
        Compare two hashes.
        """
        if IMAGEHASH_AVAILABLE:
            # Convert back to imagehash objects for comparison
            h1 = imagehash.hex_to_hash(hash1)
            h2 = imagehash.hex_to_hash(hash2)
            diff = h1 - h2
            return diff > threshold
        else:
            # Simple string comparison
            return hash1 != hash2
    
    def _add_to_history(self, hash_val: str):
        """Add hash to history."""
        self._hash_history.append(hash_val)
        if len(self._hash_history) > self._max_history:
            self._hash_history.pop(0)
    
    def is_in_loop(self, min_repeats: int = 3) -> bool:
        """
        Check if screen is in a loop (same hash repeating).
        
        Args:
            min_repeats: Minimum repeats to consider a loop
            
        Returns:
            True if in a loop
        """
        if len(self._hash_history) < min_repeats:
            return False
        
        recent = self._hash_history[-min_repeats:]
        return len(set(recent)) == 1
    
    def get_last_hash(self) -> Optional[str]:
        """Get the last computed hash."""
        return self._last_hash
    
    def reset(self):
        """Reset hash history."""
        self._last_hash = None
        self._hash_history = []


# Singleton instance
_hasher = None

def get_hasher() -> ScreenHash:
    """Get the singleton ScreenHash instance."""
    global _hasher
    if _hasher is None:
        _hasher = ScreenHash()
    return _hasher


def screen_changed(old_img: np.ndarray, new_img: np.ndarray, 
                   threshold: int = 5) -> bool:
    """
    Convenience function to check if screen changed.
    """
    hasher = ScreenHash()
    hasher._last_hash = hasher.compute_hash(old_img)
    return hasher.has_changed(new_img, threshold)
