def filter_ui_elements(detections, ocr_text):

    useful_classes = [
        "button",
        "text",
        "input",
        "icon",
        "menu"
    ]

    filtered = []

    for d in detections:
        if d["class"] in useful_classes:
            filtered.append(d)

    for t in ocr_text:
        if len(t["text"]) > 2:
            filtered.append(t)

    return filtered