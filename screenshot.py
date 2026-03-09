import mss
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