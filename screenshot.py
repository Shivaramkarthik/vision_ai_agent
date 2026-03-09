"""
screenshot.py - Screen Capture Module

Captures screenshots using mss library.
Saves screenshots to the screenshots/ directory.
"""

import os
import time
from mss import mss
import numpy as np
import cv2


class ScreenCapture:
    """Handles screen capture operations."""
    
    def __init__(self, save_dir: str = "screenshots"):
        self.save_dir = save_dir
        self._ensure_dir_exists()
    
    def _ensure_dir_exists(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def capture(self, filename: str = None) -> tuple:
        if filename is None:
            timestamp = int(time.time() * 1000)
            filename = f"screen_{timestamp}.png"
        
        filepath = os.path.join(self.save_dir, filename)
        
        with mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            cv2.imwrite(filepath, img)
            print(f"Screenshot saved: {filepath}")
        
        return filepath, img
    
    def get_screen_size(self) -> tuple:
        with mss() as sct:
            monitor = sct.monitors[1]
            return (monitor["width"], monitor["height"])


def capture_screen():
    os.makedirs("screenshots", exist_ok=True)
    with mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        cv2.imwrite("screenshots/screen.png", img)
        print("Screenshot saved: screenshots/screen.png")
        return img


if __name__ == "__main__":
    capture = ScreenCapture()
    path, img = capture.capture()
    print(f"Saved to: {path}, Shape: {img.shape}")

# END OF FILE
# import mss
import numpy as np
import cv2
import os


def capture_screen():

    os.makedirs("screenshots", exist_ok=True)

    with mss.mss() as sct:

        monitor = sct.monitors[1]

        screenshot = sct.grab(monitor)

        img = np.array(screenshot)

        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        cv2.imwrite("screenshots/screen.png", img)

        print("Screenshot saved: screenshots/screen.png")

        return img