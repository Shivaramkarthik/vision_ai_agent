from ocr_reader import read_text
from ui_detector import detect_ui
from ui_filter import filter_ui_elements
from ui_semantic import classify_ui_element


def text_inside_box(text_box, ui_box):

    tx, ty, tw, th = text_box
    ux1, uy1, ux2, uy2 = ui_box

    cx = tx + tw // 2
    cy = ty + th // 2

    if ux1 <= cx <= ux2 and uy1 <= cy <= uy2:
        return True

    return False


def process_screen(image):

    ocr_results = read_text(image)
    ui_boxes = detect_ui(image)

    elements = []

    used_text = set()

    for x1, y1, x2, y2, label in ui_boxes:

        attached_text = ""

        for i, (text, (tx, ty, tw, th)) in enumerate(ocr_results):

            if text_inside_box((tx, ty, tw, th), (x1, y1, x2, y2)):
                attached_text += text + " "
                used_text.add(i)

        attached_text = attached_text.strip()

        width = int(x2 - x1)
        height = int(y2 - y1)

        semantic_type = classify_ui_element(label, attached_text, width, height)

        elements.append({
            "type": semantic_type,
            "text": attached_text,
            "x": int((x1 + x2) / 2),
            "y": int((y1 + y2) / 2),
            "width": width,
            "height": height,
            "x1": int(x1),
            "y1": int(y1),
            "x2": int(x2),
            "y2": int(y2)
        })

    # Add remaining OCR text
    for i, (text, (x, y, w, h)) in enumerate(ocr_results):

        if i in used_text:
            continue

        elements.append({
            "type": "text",
            "text": text,
            "x": x + w // 2,
            "y": y + h // 2,
            "width": w,
            "height": h,
            "x1": x,
            "y1": y,
            "x2": x + w,
            "y2": y + h
        })

    elements = filter_ui_elements(elements)

    return elements