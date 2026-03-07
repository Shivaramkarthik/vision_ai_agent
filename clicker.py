import pyautogui

pyautogui.FAILSAFE = True


def click(x, y):
    pyautogui.moveTo(x, y, duration=0.3)
    pyautogui.click()


def type_text(text):
    pyautogui.write(text, interval=0.05)


def press_key(key):
    pyautogui.press(key)