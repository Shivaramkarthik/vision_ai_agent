from ui_detector import detect_ui_elements
from ocr_reader import detect_text_boxes


def get_screen_state(image_path):

    ui_elements = detect_ui_elements(image_path)
    text_elements = detect_text_boxes(image_path)

    elements = []

    # --- keep only useful UI objects ---
    allowed_ui = ["cell phone", "tv", "laptop", "keyboard"]

    for el in ui_elements:

        if el["type"] in allowed_ui:

            elements.append({
                "type": "ui",
                "text": el["type"],
                "x": el["x"],
                "y": el["y"]
            })

    # --- filter OCR text ---
    for el in text_elements:

        text = el["text"].strip()

        # remove tiny garbage text
        if len(text) < 3:
            continue

        # remove symbols
        if text in ["©", "&", "*", ".", "-", "_"]:
            continue

        elements.append({
            "type": "text",
            "text": text,
            "x": el["x"],
            "y": el["y"]
        })

    # limit elements so LLM doesn't get overwhelmed
    return elements[:30]