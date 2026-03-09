"""
critic.py - Screen Change Detection Module

Checks if screen changed using OpenCV image comparison.
Used for reflection loop to prevent infinite loops.
"""

import cv2
import numpy as np
from typing import Tuple, Optional


class Critic:
    """Handles screen change detection using OpenCV."""
    
    def __init__(self, threshold: float = 0.95):
        """
        Initialize the critic module.
        
        Args:
            threshold: Similarity threshold (0-1). Higher = more similar required.
        """
        self.threshold = threshold
        self.last_screenshot = None
    
    def compare_images(self, img1: np.ndarray, img2: np.ndarray) -> Tuple[bool, float]:
        """
        Compare two images and determine if they are different.
        
        Args:
            img1: First image (numpy array)
            img2: Second image (numpy array)
            
        Returns:
            Tuple of (changed: bool, similarity: float)
        """
        # Ensure same size
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        
        # Convert to grayscale for comparison
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # Calculate structural similarity
        similarity = self._calculate_similarity(gray1, gray2)
        
        # Screen changed if similarity is below threshold
        changed = similarity < self.threshold
        
        return changed, similarity
    
    def _calculate_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate similarity between two grayscale images.
        
        Uses normalized cross-correlation for speed.
        
        Args:
            img1: First grayscale image
            img2: Second grayscale image
            
        Returns:
            Similarity score (0-1)
        """
        # Compute absolute difference
        diff = cv2.absdiff(img1, img2)
        
        # Calculate percentage of pixels that are similar
        non_zero = np.count_nonzero(diff > 10)  # Threshold for noise
        total_pixels = diff.size
        
        similarity = 1.0 - (non_zero / total_pixels)
        return similarity
    
    def has_screen_changed(self, current_img: np.ndarray) -> bool:
        """
        Check if screen has changed since last capture.
        
        Args:
            current_img: Current screenshot (numpy array)
            
        Returns:
            True if screen changed, False otherwise
        """
        if self.last_screenshot is None:
            self.last_screenshot = current_img.copy()
            return True  # First capture, consider as changed
        
        changed, similarity = self.compare_images(self.last_screenshot, current_img)
        
        # Update last screenshot
        self.last_screenshot = current_img.copy()
        
        print(f"Screen similarity: {similarity:.2%}, Changed: {changed}")
        return changed
    
    def compare_files(self, path1: str, path2: str) -> Tuple[bool, float]:
        """
        Compare two image files.
        
        Args:
            path1: Path to first image
            path2: Path to second image
            
        Returns:
            Tuple of (changed: bool, similarity: float)
        """
        img1 = cv2.imread(path1)
        img2 = cv2.imread(path2)
        
        if img1 is None or img2 is None:
            print("Error: Could not load images")
            return True, 0.0
        
        return self.compare_images(img1, img2)
    
    def reset(self):
        """Reset the last screenshot reference."""
        self.last_screenshot = None


if __name__ == "__main__":
    # Test the critic module
    critic = Critic(threshold=0.95)
    
    # Create test images
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2[50:60, 50:60] = 255  # Add white square
    
    changed, similarity = critic.compare_images(img1, img2)
    print(f"Test - Changed: {changed}, Similarity: {similarity:.2%}")
