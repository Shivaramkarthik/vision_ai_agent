"""UI semantic classification module for Offline Visual AI Agent 2.0"""

from typing import Optional


# Common button labels
BUTTON_LABELS = {
    "ok", "cancel", "yes", "no", "submit", "send", "save", "apply",
    "login", "sign in", "sign up", "register", "search", "go",
    "next", "back", "previous", "continue", "finish", "done",
    "close", "exit", "quit", "delete", "remove", "add", "create",
    "edit", "update", "refresh", "reload", "download", "upload",
    "browse", "open", "new", "copy", "paste", "cut", "undo", "redo"
}

# Common menu labels
MENU_LABELS = {
    "file", "edit", "view", "tools", "help", "window", "options",
    "settings", "preferences", "format", "insert", "selection"
}

# Common tab labels
TAB_LABELS = {
    "home", "settings", "profile", "dashboard", "account",
    "general", "advanced", "about", "details", "overview"
}

# Common link patterns
LINK_PATTERNS = {
    "http", "www", "click here", "learn more", "read more",
    "see more", "view all", "show more"
}


def classify_ui_element(label: str, text: str, 
                        width: int, height: int) -> str:
    """
    Classify UI element into semantic type.
    
    Args:
        label: Raw detection label
        text: Text content of element
        width: Element width
        height: Element height
        
    Returns:
        Semantic UI type
    """
    text_lower = text.lower().strip()
    label_lower = label.lower()
    
    # Direct label mappings
    if label_lower in ["textbox", "input", "textarea"]:
        return "textbox"
    
    if label_lower == "checkbox":
        return "checkbox"
    
    if label_lower == "radio":
        return "radio"
    
    # Button detection
    if label_lower == "button" or _is_button(text_lower, width, height):
        return "button"
    
    # Menu detection
    if text_lower in MENU_LABELS:
        return "menu"
    
    # Tab detection
    if text_lower in TAB_LABELS:
        return "tab"
    
    # Link detection
    if _is_link(text_lower):
        return "link"
    
    # Icon detection
    if label_lower == "icon" or (0.7 < width/max(height,1) < 1.4 and width < 60):
        return "icon"
    
    # Search box detection
    if "search" in text_lower and width > 100:
        return "search"
    
    # Dropdown detection
    if label_lower in ["dropdown", "select", "combobox"]:
        return "dropdown"
    
    # Default to original label or generic type
    if label_lower != "unknown":
        return label_lower
    
    # Classify by shape as fallback
    return _classify_by_shape(width, height)


def _is_button(text: str, width: int, height: int) -> bool:
    """
    Check if element is likely a button.
    """
    # Check text content
    if text in BUTTON_LABELS:
        return True
    
    # Check for common button text patterns
    for btn_text in BUTTON_LABELS:
        if btn_text in text:
            return True
    
    # Check shape (buttons are typically wider than tall)
    if width > 60 and height > 20 and height < 60:
        aspect = width / max(height, 1)
        if 1.5 < aspect < 8:
            return True
    
    return False


def _is_link(text: str) -> bool:
    """
    Check if element is likely a link.
    """
    for pattern in LINK_PATTERNS:
        if pattern in text:
            return True
    return False


def _classify_by_shape(width: int, height: int) -> str:
    """
    Classify element by shape when other methods fail.
    """
    aspect = width / max(height, 1)
    area = width * height
    
    # Very wide and short = likely text field or menu
    if aspect > 5 and height < 40:
        return "textbox"
    
    # Square-ish and small = likely icon or checkbox
    if 0.8 < aspect < 1.2 and width < 50:
        return "icon"
    
    # Medium rectangle = likely button
    if 1.5 < aspect < 4 and 500 < area < 10000:
        return "button"
    
    return "element"


def get_element_description(element: dict) -> str:
    """
    Get a human-readable description of a UI element.
    
    Args:
        element: UI element dictionary
        
    Returns:
        Description string
    """
    element_type = element.get("type", "element")
    text = element.get("text", "")
    
    if text:
        return f'{element_type} "{text}"'
    else:
        return f'{element_type} at ({element.get("x", 0)}, {element.get("y", 0)})'
