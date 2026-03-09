import cv2
import numpy as np


def evaluate_action(prev_screen, new_screen):
    """
    Determine if an action changed the screen
    """

    diff = cv2.absdiff(prev_screen, new_screen)

    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    score = np.sum(gray)

    if score > 500000:
        return "SUCCESS"

    return "FAILED"