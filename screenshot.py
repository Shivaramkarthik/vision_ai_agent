import mss
import cv2
import numpy as np
import time


def capture_screen():

    with mss.mss() as sct:

        screenshot = sct.grab(sct.monitors[1])

        img = np.array(screenshot)

        filename = f"screenshots/screen_{int(time.time())}.png"

        cv2.imwrite(filename, img)

        return filename