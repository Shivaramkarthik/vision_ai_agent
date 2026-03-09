"""Executor Agent for Offline Visual AI Agent 2.0"""

import pyautogui
import time
from typing import List, Dict, Optional, Tuple
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import (
        EXECUTOR_CLICK_DURATION, EXECUTOR_TYPE_INTERVAL,
        PYAUTOGUI_FAILSAFE, PYAUTOGUI_PAUSE,
        SCREEN_RESIZE_WIDTH, SCREEN_RESIZE_HEIGHT,
        SCREEN_ORIGINAL_WIDTH, SCREEN_ORIGINAL_HEIGHT
    )
except ImportError:
    EXECUTOR_CLICK_DURATION = 0.2
    EXECUTOR_TYPE_INTERVAL = 0.02
    PYAUTOGUI_FAILSAFE = True
    PYAUTOGUI_PAUSE = 0.1
    SCREEN_RESIZE_WIDTH = 960
    SCREEN_RESIZE_HEIGHT = 540
    SCREEN_ORIGINAL_WIDTH = 1920
    SCREEN_ORIGINAL_HEIGHT = 1080

# Configure PyAutoGUI
pyautogui.FAILSAFE = PYAUTOGUI_FAILSAFE
pyautogui.PAUSE = PYAUTOGUI_PAUSE


class ExecutorAgent:
    """
    Executor agent responsible for performing mouse/keyboard actions.
    """
    
    def __init__(self):
        self.click_duration = EXECUTOR_CLICK_DURATION
        self.type_interval = EXECUTOR_TYPE_INTERVAL
        
        # Scale factors for coordinate conversion
        self._scale_x = SCREEN_ORIGINAL_WIDTH / SCREEN_RESIZE_WIDTH
        self._scale_y = SCREEN_ORIGINAL_HEIGHT / SCREEN_RESIZE_HEIGHT
        
        self._last_action = ""
        self._last_result = True
    
    def execute(self, command: str, elements: List[Dict]) -> bool:
        """
        Execute a command.
        
        Args:
            command: The command string (e.g., "click 5", "type hello")
            elements: List of UI elements for reference
            
        Returns:
            True if execution succeeded, False otherwise
        """
        self._last_action = command
        
        try:
            parts = command.split(maxsplit=1)
            if not parts:
                return False
            
            action = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            if action == "click":
                return self._execute_click(args, elements)
            elif action == "type":
                return self._execute_type(args)
            elif action == "press":
                return self._execute_press(args)
            elif action == "scroll":
                return self._execute_scroll(args)
            elif action == "drag":
                return self._execute_drag(args, elements)
            elif action == "hotkey":
                return self._execute_hotkey(args)
            elif action == "done":
                return True
            else:
                print(f"Unknown action: {action}")
                return False
                
        except Exception as e:
            print(f"Execution error: {e}")
            self._last_result = False
            return False
    
    def _execute_click(self, args: str, elements: List[Dict]) -> bool:
        """
        Execute a click action.
        
        Args:
            args: Element number or coordinates
            elements: List of UI elements
        """
        try:
            # Parse element number
            index = int(args.strip()) - 1
            
            if index < 0 or index >= len(elements):
                print(f"Invalid element index: {index + 1}")
                return False
            
            element = elements[index]
            
            # Get coordinates and scale to screen
            x, y = self._scale_coordinates(element["x"], element["y"])
            
            # Move and click
            pyautogui.moveTo(x, y, duration=self.click_duration)
            time.sleep(0.1)
            pyautogui.click()
            
            self._last_result = True
            return True
            
        except ValueError:
            # Try parsing as coordinates "x,y"
            try:
                coords = args.split(",")
                x = int(coords[0].strip())
                y = int(coords[1].strip())
                x, y = self._scale_coordinates(x, y)
                pyautogui.moveTo(x, y, duration=self.click_duration)
                pyautogui.click()
                return True
            except:
                print(f"Invalid click argument: {args}")
                return False
    
    def _execute_type(self, text: str) -> bool:
        """
        Execute a type action.
        
        Args:
            text: Text to type
        """
        if not text:
            return False
        
        # Remove quotes if present
        text = text.strip('"').strip("'")
        
        pyautogui.write(text, interval=self.type_interval)
        self._last_result = True
        return True
    
    def _execute_press(self, key: str) -> bool:
        """
        Execute a key press action.
        
        Args:
            key: Key to press
        """
        if not key:
            return False
        
        key = key.strip().lower()
        
        # Map common key names
        key_map = {
            "enter": "return",
            "return": "return",
            "esc": "escape",
            "escape": "escape",
            "tab": "tab",
            "space": "space",
            "backspace": "backspace",
            "delete": "delete",
            "up": "up",
            "down": "down",
            "left": "left",
            "right": "right",
            "home": "home",
            "end": "end",
            "pageup": "pageup",
            "pagedown": "pagedown",
        }
        
        key = key_map.get(key, key)
        
        pyautogui.press(key)
        self._last_result = True
        return True
    
    def _execute_scroll(self, direction: str) -> bool:
        """
        Execute a scroll action.
        
        Args:
            direction: Scroll direction (up/down/left/right)
        """
        direction = direction.strip().lower()
        
        scroll_amount = 3  # Number of scroll units
        
        if direction == "up":
            pyautogui.scroll(scroll_amount)
        elif direction == "down":
            pyautogui.scroll(-scroll_amount)
        elif direction == "left":
            pyautogui.hscroll(-scroll_amount)
        elif direction == "right":
            pyautogui.hscroll(scroll_amount)
        else:
            print(f"Invalid scroll direction: {direction}")
            return False
        
        self._last_result = True
        return True
    
    def _execute_drag(self, args: str, elements: List[Dict]) -> bool:
        """
        Execute a drag action.
        
        Args:
            args: "from_index to_index" or "from_x,from_y to_x,to_y"
            elements: List of UI elements
        """
        try:
            parts = args.split()
            if len(parts) < 2:
                return False
            
            # Parse as element indices
            from_idx = int(parts[0]) - 1
            to_idx = int(parts[1]) - 1
            
            if from_idx < 0 or from_idx >= len(elements):
                return False
            if to_idx < 0 or to_idx >= len(elements):
                return False
            
            from_elem = elements[from_idx]
            to_elem = elements[to_idx]
            
            from_x, from_y = self._scale_coordinates(from_elem["x"], from_elem["y"])
            to_x, to_y = self._scale_coordinates(to_elem["x"], to_elem["y"])
            
            pyautogui.moveTo(from_x, from_y, duration=self.click_duration)
            pyautogui.drag(to_x - from_x, to_y - from_y, duration=0.5)
            
            self._last_result = True
            return True
            
        except Exception as e:
            print(f"Drag error: {e}")
            return False
    
    def _execute_hotkey(self, keys: str) -> bool:
        """
        Execute a hotkey combination.
        
        Args:
            keys: Key combination (e.g., "ctrl+c", "alt+tab", "win")
        """
        if not keys:
            return False
        
        keys = keys.strip().lower()
        
        # Map common key names
        key_map = {
            "win": "win",
            "windows": "win",
            "ctrl": "ctrl",
            "control": "ctrl",
            "alt": "alt",
            "shift": "shift",
        }
        
        # Handle single key (like "win")
        if "+" not in keys:
            mapped_key = key_map.get(keys, keys)
            pyautogui.press(mapped_key)
            self._last_result = True
            return True
        
        # Handle key combinations (like "ctrl+c")
        key_parts = [k.strip() for k in keys.split("+")]
        mapped_keys = [key_map.get(k, k) for k in key_parts]
        
        pyautogui.hotkey(*mapped_keys)
        self._last_result = True
        return True
    
    def _scale_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """
        Scale coordinates from resized image to screen.
        """
        return int(x * self._scale_x), int(y * self._scale_y)
    
    def click_at(self, x: int, y: int, scale: bool = True) -> bool:
        """
        Click at specific coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            scale: Whether to scale coordinates
        """
        if scale:
            x, y = self._scale_coordinates(x, y)
        
        pyautogui.moveTo(x, y, duration=self.click_duration)
        pyautogui.click()
        return True
    
    def get_last_action(self) -> str:
        """Get the last executed action"""
        return self._last_action
    
    def get_last_result(self) -> bool:
        """Get the result of the last action"""
        return self._last_result
