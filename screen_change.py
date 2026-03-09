import cv2
import numpy as np


def screen_changed(old_img, new_img, threshold=5000000):

    # convert to grayscale
    old_gray = cv2.cvtColor(old_img, cv2.COLOR_BGR2GRAY)
    new_gray = cv2.cvtColor(new_img, cv2.COLOR_BGR2GRAY)

    # compute difference
    diff = cv2.absdiff(old_gray, new_gray)

    # sum difference
    change = np.sum(diff)

    print("Screen difference:", change)

    return change > threshold
