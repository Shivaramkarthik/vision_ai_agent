import cv2
import pytesseract
import re

# Path to Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_elements(image_path):

    img = cv2.imread(image_path)

    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    data = pytesseract.image_to_data(img_rgb, output_type=pytesseract.Output.DICT)

    elements = []

    n = len(data["text"])

    for i in range(n):

        text = data["text"][i].strip()

        # Skip empty text
        if text == "":
            continue

        # Remove weird characters
        text = re.sub(r'[^a-zA-Z0-9._:/\\-]', '', text)

        # Skip very short noise
        if len(text) < 3:
            continue

        x = data["left"][i]
        y = data["top"][i]
        w = data["width"][i]
        h = data["height"][i]

        elements.append({
            "text": text,
            "x": x,
            "y": y,
            "width": w,
            "height": h
        })

    return elements


def format_ui(elements):

    ui_description = ""

    for e in elements:

        cx = e["x"] + e["width"] // 2
        cy = e["y"] + e["height"] // 2

        line = f'Text "{e["text"]}" at ({cx},{cy})'

        ui_description += line + "\n"

    return ui_description