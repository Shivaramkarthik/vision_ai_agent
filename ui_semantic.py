def classify_ui_element(label, text, width, height):
    """
    Convert raw UI detection into semantic UI types
    """

    text_lower = text.lower()

    # Textbox detection
    if label == "textbox":
        return "textbox"

    # Checkbox detection
    if label == "checkbox":
        return "checkbox"

    # Button detection
    if label == "button":

        if text_lower in ["ok", "login", "submit", "search", "send", "apply"]:
            return "button"

        if width > 80 and height > 25:
            return "button"

    # Menu detection
    if text_lower in ["file", "edit", "view", "tools", "help"]:
        return "menu"

    # Tab detection
    if text_lower in ["home", "settings", "profile", "dashboard"]:
        return "tab"

    return label