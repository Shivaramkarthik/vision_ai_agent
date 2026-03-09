import cv2
import numpy as np


class CriticAgent:

    def evaluate(self, prev_screen, new_screen):

        diff = cv2.absdiff(prev_screen, new_screen)

        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        score = np.sum(gray)

        if score > 500000:
            return "SUCCESS"

        return "FAILED"