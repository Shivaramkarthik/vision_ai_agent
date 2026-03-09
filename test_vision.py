from vision import extract_text_elements, format_ui
import os

image_path = "screenshots/screen.png"

if not os.path.exists(image_path):
    print("Screenshot not found.")
    print("Run screenshot.py first.")
    exit()

print("Testing OCR Vision System...\n")

elements = extract_text_elements(image_path)

print("RAW ELEMENTS:")
print(elements)

print("\nFormatted UI Description:\n")

ui_description = format_ui(elements)

print(ui_description)