import pytesseract
import cv2

# Set path to Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def read_text(image):
    """
    Extract text and bounding boxes from the image using Tesseract OCR
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

    results = []

    for i in range(len(data["text"])):

        text = data["text"][i].strip()

        if text == "":
            continue

        x = data["left"][i]
        y = data["top"][i]
        w = data["width"][i]
        h = data["height"][i]

        results.append((text, (x, y, w, h)))

    return results