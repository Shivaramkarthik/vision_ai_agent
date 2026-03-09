import pyautogui
import time


pyautogui.FAILSAFE = True


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