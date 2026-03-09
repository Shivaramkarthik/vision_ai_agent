import cv2
import numpy as np


def detect_ui(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(blur, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []

    for cnt in contours:

        x, y, w, h = cv2.boundingRect(cnt)

        if w < 40 or h < 20:
            continue

        aspect = w / float(h)

        label = "unknown"

        # Checkbox detection
        if 0.8 < aspect < 1.2 and 15 < w < 50:
            label = "checkbox"

        # Button detection
        elif w > 80 and h > 30:
            label = "button"

        # Textbox detection
        elif w > 150 and h < 60:
            label = "textbox"

        else:
            continue

        x1 = x
        y1 = y
        x2 = x + w
        y2 = y + h

        boxes.append((x1, y1, x2, y2, label))

    return boxes