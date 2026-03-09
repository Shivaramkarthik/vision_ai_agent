"""
clicker.py - Action Execution Module

Executes actions using PyAutoGUI.
Supports click, type, press, and scroll commands.
"""

import pyautogui
import time


pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


class Clicker:
    def __init__(self, action_delay: float = 0.2):
        self.action_delay = action_delay
    
    def execute(self, command: str) -> bool:
        parts = command.strip().split(" ", 1)
        if not parts:
            return False
        action = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        try:
            if action == "click":
                return self._click(args)
            elif action == "type":
                return self._type(args)
            elif action == "press":
                return self._press(args)
            elif action == "scroll":
                return self._scroll(args)
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def _click(self, args: str) -> bool:
        coords = args.strip().split()
        if len(coords) >= 2:
            x, y = int(coords[0]), int(coords[1])
            pyautogui.click(x, y)
            time.sleep(self.action_delay)
            return True
        return False
    
    def _type(self, text: str) -> bool:
        if text:
            pyautogui.typewrite(text, interval=0.02)
            time.sleep(self.action_delay)
            return True
        return False
    
    def _press(self, key: str) -> bool:
        key = key.strip().lower()
        key_map = {"enter": "return", "esc": "escape"}
        pyautogui.press(key_map.get(key, key))
        time.sleep(self.action_delay)
        return True
    
    def _scroll(self, direction: str) -> bool:
        d = direction.strip().lower()
        pyautogui.scroll(3 if d == "up" else -3)
        time.sleep(self.action_delay)
        return True
    
    def get_mouse_position(self):
        return pyautogui.position()


# Legacy - pyautogui.FAILSAFE = True


def execute_command(command, elements):

    parts = command.split()

    action = parts[0]

    if action == "click":

        index = int(parts[1]) - 1

        if index < 0 or index >= len(elements):
            print("Invalid element index")
            return

        e = elements[index]

        x = e["x"]
        y = e["y"]

        print(f"Clicking element {index+1} at {x},{y}")

        pyautogui.moveTo(x, y, duration=0.2)

        time.sleep(0.2)

        pyautogui.click()

    elif action == "type":

        text = " ".join(parts[1:])

        pyautogui.write(text)

    elif action == "press":

        key = parts[1]

        pyautogui.press(key)