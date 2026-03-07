import time

from screenshot import capture_screen
from vision_processor import get_screen_state
from brain import generate_plan
from clicker import click, type_text, press_key


goal = "search youtube"


while True:

    # -------- Observe --------
    image_path = capture_screen()

    elements = get_screen_state(image_path)

    print("\nDetected elements:")

    for i, el in enumerate(elements):
        print(i + 1, el["type"], el["text"], el["x"], el["y"])


    # -------- Reason --------
    print("\nSending screen state to LLM...")

    plan = generate_plan(elements, goal)

    print("\nLLM Plan:")
    print(plan)


    # -------- Act --------
    steps = plan.split("\n")

    for step in steps:

        parts = step.strip().split()

        if len(parts) == 0:
            continue

        action = parts[0].lower()

        if action == "click":

            index = int(parts[1]) - 1
            el = elements[index]

            click(el["x"], el["y"])

        elif action == "type":

            text = " ".join(parts[1:])
            type_text(text)

        elif action == "press":

            key = parts[1]
            press_key(key)

        time.sleep(1)


    time.sleep(3)