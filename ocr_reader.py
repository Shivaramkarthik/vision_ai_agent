import pytesseract
import cv2

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def detect_text_boxes(image_path):

    img = cv2.imread(image_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

    elements = []

    for i in range(len(data["text"])):

        text = data["text"][i].strip()

        if text != "":

            x = data["left"][i]
            y = data["top"][i]

            elements.append({
                "text": text,
                "x": x,
                "y": y
            })

    return elements