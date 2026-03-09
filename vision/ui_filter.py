"""UI element filtering module for Offline Visual AI Agent 2.0"""

from typing import List, Dict
import sys
sys.path.append('..')

try:
    from config import UI_MIN_WIDTH, UI_MIN_HEIGHT
except ImportError:
    UI_MIN_WIDTH = 15
    UI_MIN_HEIGHT = 15


def filter_ui_elements(elements: List[Dict], 
                       min_width: int = None,
                       min_height: int = None,
                       remove_duplicates: bool = True) -> List[Dict]:
    """
    Filter UI elements to remove noise and duplicates.
    
    Args:
        elements: List of UI element dictionaries
        min_width: Minimum element width
        min_height: Minimum element height
        remove_duplicates: Whether to remove duplicate elements
        
    Returns:
        Filtered list of elements
    """
    min_width = min_width or UI_MIN_WIDTH
    min_height = min_height or UI_MIN_HEIGHT
    
    filtered = []
    seen_positions = set()
    
    for e in elements:
        width = e.get("width", 0)
        height = e.get("height", 0)
        
        # Filter by size
        if width < min_width or height < min_height:
            continue
        
        # Filter empty text elements that are tiny
        if e.get("type") == "text":
            text = e.get("text", "").strip()
            if text == "" and width < 40:
                continue
        
        # Filter very large elements (likely background)
        if width > 1800 or height > 1000:
            continue
        
        # Remove duplicates based on position
        if remove_duplicates:
            pos_key = (e.get("x1", 0) // 10, e.get("y1", 0) // 10,
                       e.get("x2", 0) // 10, e.get("y2", 0) // 10)
            if pos_key in seen_positions:
                continue
            seen_positions.add(pos_key)
        
        filtered.append(e)
    
    # Sort by position (top to bottom, left to right)
    filtered.sort(key=lambda e: (e.get("y1", 0), e.get("x1", 0)))
    
    return filtered


def filter_by_type(elements: List[Dict], 
                   element_types: List[str]) -> List[Dict]:
    """
    Filter elements by type.
    
    Args:
        elements: List of UI element dictionaries
        element_types: List of types to keep
        
    Returns:
        Filtered list of elements
    """
    return [e for e in elements if e.get("type") in element_types]


def filter_by_text(elements: List[Dict], 
                   text: str, 
                   partial: bool = True) -> List[Dict]:
    """
    Filter elements by text content.
    
    Args:
        elements: List of UI element dictionaries
        text: Text to search for
        partial: Allow partial matches
        
    Returns:
        Filtered list of elements
    """
    text_lower = text.lower()
    
    if partial:
        return [e for e in elements 
                if text_lower in e.get("text", "").lower()]
    else:
        return [e for e in elements 
                if text_lower == e.get("text", "").lower()]


def filter_clickable(elements: List[Dict]) -> List[Dict]:
    """
    Filter to only clickable elements.
    
    Args:
        elements: List of UI element dictionaries
        
    Returns:
        List of clickable elements
    """
    clickable_types = [
        "button", "link", "checkbox", "radio", "icon",
        "menu", "menu_item", "tab", "clickable"
    ]
    return filter_by_type(elements, clickable_types)


def filter_input_fields(elements: List[Dict]) -> List[Dict]:
    """
    Filter to only input fields.
    
    Args:
        elements: List of UI element dictionaries
        
    Returns:
        List of input field elements
    """
    input_types = ["textbox", "input", "textarea", "search"]
    return filter_by_type(elements, input_types)
