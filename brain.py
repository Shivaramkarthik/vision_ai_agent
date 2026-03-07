import ollama


def generate_plan(elements, goal):

    description = ""

    for i, el in enumerate(elements):

        description += f"{i+1}. {el['type']} {el['text']} at ({el['x']},{el['y']})\n"

    prompt = f"""
You are controlling a computer.

Goal:
{goal}

Visible elements:
{description}

Create an action plan using:

click <number>
type <text>
press <key>
"""

    response = ollama.chat(
        model="llama3:8b",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]