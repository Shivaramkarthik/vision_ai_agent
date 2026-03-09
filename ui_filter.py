def filter_ui_elements(elements):
    """
    Remove very small or useless UI detections
    """

    filtered = []

    for e in elements:

        width = e.get("width", 0)
        height = e.get("height", 0)

        # ignore very small detections (noise)
        if width < 15 or height < 15:
            continue

        # ignore empty text elements that are tiny
        if e["type"] == "text" and e["text"].strip() == "" and width < 40:
            continue

        filtered.append(e)

    return filtered