import ollama


class PlannerAgent:

    def build_prompt(self, elements, goal):

        ui_text = ""

        for i, e in enumerate(elements):
            ui_text += f'{i+1}. {e["type"]} "{e["text"]}"\n'

        prompt = f"""
You control a computer.

Goal:
{goal}

UI elements:
{ui_text}

Allowed commands:

click NUMBER
type TEXT
press KEY

Return one command per line.
"""

        return prompt

    def plan(self, elements, goal):

        prompt = self.build_prompt(elements, goal)

        response = ollama.chat(
            model="llama3:8b",
            messages=[{"role": "user", "content": prompt}]
        )

        text = response["message"]["content"]

        plan = []

        for line in text.split("\n"):

            line = line.strip()

            if line.startswith("click") or line.startswith("type") or line.startswith("press"):
                plan.append(line)

        return plan