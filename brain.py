import ollama


def build_prompt(elements, goal):

    ui_text = ""

    for i, e in enumerate(elements):

        ui_text += f'{i+1}. {e["type"]} "{e["text"]}"\n'

    prompt = f"""
You are a computer control AI.

Goal:
{goal}

UI elements:

{ui_text}

Rules:
- Use element numbers when clicking.
- Format commands exactly like:

click NUMBER
type TEXT
press KEY

Example:
click 1
type youtube
press enter
"""

    return prompt


def generate_plan(elements, goal):

    prompt = build_prompt(elements, goal)

    response = ollama.chat(
        model="llama3:8b",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response["message"]["content"]

    lines = text.split("\n")

    plan = []

    for line in lines:

        line = line.strip()

        if line == "":
            continue

        if line.startswith("click") or line.startswith("type") or line.startswith("press"):
            plan.append(line)

    return plan