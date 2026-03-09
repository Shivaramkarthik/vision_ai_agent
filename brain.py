"""
brain.py - LLM Communication Module

Communicates with Ollama (llama3:8b) for reasoning and action planning.
Runs fully offline using local Ollama instance.
"""

import requests
from typing import Optional, List


class Brain:
    """Handles communication with Ollama LLM for reasoning."""
    
    def __init__(self, model: str = "llama3:8b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        
        self.system_prompt = """You are a Visual AI Agent that controls a computer.
You receive descriptions of what is on the screen and must generate actions.

Available commands:
- click x y (click at coordinates)
- type text (type the specified text)
- press key (press a keyboard key like enter, tab, escape)
- scroll up (scroll up)
- scroll down (scroll down)

Rules:
1. Output ONLY commands, one per line
2. Use exact coordinates for clicks
3. Be precise and efficient

Example output:
click 800 450
type hello world
press enter"""
    
    def generate(self, prompt: str, context: Optional[str] = None) -> str:
        full_prompt = prompt
        if context:
            full_prompt = f"Context: {context}\n\n{prompt}"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "system": self.system_prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 256}
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Ollama: {e}")
            return ""
    
    def plan_actions(self, screen_description: str, goal: str) -> List[str]:
        prompt = f"""Current screen state:
{screen_description}

Goal: {goal}

Generate the next actions. Output only commands, one per line."""
        
        response = self.generate(prompt)
        commands = []
        for line in response.split("\n"):
            line = line.strip()
            if line and self._is_valid_command(line):
                commands.append(line)
        return commands
    
    def _is_valid_command(self, command: str) -> bool:
        valid_prefixes = ["click", "type", "press", "scroll"]
        return any(command.lower().startswith(p) for p in valid_prefixes)
    
    def reflect(self, action_taken: str, screen_changed: bool, screen_description: str) -> str:
        prompt = f"""Action taken: {action_taken}
Screen changed: {screen_changed}
Current screen: {screen_description}

If the screen didn't change, suggest a different action.
Output only the next command to try."""
        return self.generate(prompt)
    
    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False


# Legacy functions for backward compatibility
# import ollama


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