"""Planner Agent for Offline Visual AI Agent 2.0"""

import ollama
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from llm.ollama_client import get_client
    from llm.prompt_templates import build_planning_prompt
    NEW_STRUCTURE = True
except ImportError:
    NEW_STRUCTURE = False

try:
    from config import MAX_PLAN_STEPS, PLANNER_MODEL
except ImportError:
    MAX_PLAN_STEPS = 5
    PLANNER_MODEL = "llama3:8b"


class PlannerAgent:
    """
    Planner agent responsible for generating action plans.
    Uses Ollama LLM for reasoning.
    """
    
    def __init__(self):
        if NEW_STRUCTURE:
            self.client = get_client()
        else:
            self.client = None
        self.max_steps = MAX_PLAN_STEPS
        self.model = PLANNER_MODEL
        self._last_plan = []
        self._last_prompt = ""
    
    def build_prompt(self, elements: List[Dict], goal: str,
                     history: Optional[List[str]] = None,
                     memory_suggestions: Optional[List[str]] = None) -> str:
        """
        Build the planning prompt.
        """
        if NEW_STRUCTURE:
            return build_planning_prompt(
                goal=goal,
                ui_elements=elements,
                history=history,
                memory_suggestions=memory_suggestions
            )
        
        # Legacy prompt building
        ui_text = ""
        for i, e in enumerate(elements[:50]):
            ui_text += f'{i+1}. {e.get("type", "unknown")} "{e.get("text", "")}"\n'
        
        history_text = ""
        if history:
            history_text = "\nPrevious actions:\n" + "\n".join(f"- {a}" for a in history[-5:])
        
        prompt = f"""You control a computer.

Goal: {goal}

UI elements:
{ui_text}
{history_text}

Allowed commands:
click NUMBER
type TEXT
press KEY
scroll DIRECTION

Rules:
- Output ONLY commands, one per line
- Maximum {self.max_steps} commands
- Do not repeat failed actions
- If done, output: DONE

Your commands:"""
        
        return prompt
    
    def plan(self, elements: List[Dict], goal: str,
             history: Optional[List[str]] = None,
             memory_suggestions: Optional[List[str]] = None) -> List[str]:
        """
        Generate a plan to achieve the goal.
        
        Args:
            elements: List of UI elements
            goal: The task goal
            history: Previous action history
            memory_suggestions: Suggestions from memory
            
        Returns:
            List of action commands
        """
        prompt = self.build_prompt(elements, goal, history, memory_suggestions)
        self._last_prompt = prompt
        
        # Get LLM response
        if self.client:
            response = self.client.chat(prompt, model=self.model)
        else:
            # Direct Ollama call
            result = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            response = result["message"]["content"]
        
        # Parse response into commands
        plan = self._parse_response(response)
        plan = plan[:self.max_steps]
        
        self._last_plan = plan
        return plan
    
    def _parse_response(self, response: str) -> List[str]:
        """
        Parse LLM response into action commands.
        """
        valid_commands = ["click", "type", "press", "scroll", "drag", "hotkey", "done"]
        plan = []
        
        for line in response.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            # Remove numbering
            if line[0].isdigit():
                parts = line.split(".", 1)
                if len(parts) > 1:
                    line = parts[1].strip()
                else:
                    parts = line.split(" ", 1)
                    if len(parts) > 1:
                        line = parts[1].strip()
            
            # Remove prefixes
            line = line.lstrip("- ").lstrip("* ")
            
            # Check for valid command
            line_lower = line.lower()
            for cmd in valid_commands:
                if line_lower.startswith(cmd):
                    plan.append(line)
                    break
        
        return plan
    
    def get_last_plan(self) -> List[str]:
        """Get the last generated plan"""
        return self._last_plan
    
    def get_last_prompt(self) -> str:
        """Get the last prompt sent to LLM"""
        return self._last_prompt
