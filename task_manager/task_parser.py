"""Task Parser for Offline Visual AI Agent 2.0"""

from typing import List, Dict, Optional
import re
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from llm.ollama_client import get_client
    from llm.prompt_templates import build_task_parsing_prompt
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


class TaskParser:
    """
    Parse natural language tasks into executable steps.
    """
    
    def __init__(self):
        if LLM_AVAILABLE:
            self.client = get_client()
        else:
            self.client = None
        
        # Common task patterns
        self._patterns = {
            r"open (\w+)": ["click on {0} icon", "wait for {0} to open"],
            r"search for (.+)": ["click on search box", "type {0}", "press enter"],
            r"go to (.+)": ["click on address bar", "type {0}", "press enter"],
            r"type (.+)": ["type {0}"],
            r"click (.+)": ["click on {0}"],
        }
    
    def parse(self, task_description: str) -> List[str]:
        """
        Parse a task description into steps.
        
        Args:
            task_description: Natural language task
            
        Returns:
            List of step descriptions
        """
        # Try pattern matching first
        steps = self._match_patterns(task_description)
        if steps:
            return steps
        
        # Use LLM for complex tasks
        if self.client:
            return self._parse_with_llm(task_description)
        
        # Fallback: return task as single step
        return [task_description]
    
    def _match_patterns(self, task: str) -> Optional[List[str]]:
        """
        Try to match task against known patterns.
        """
        task_lower = task.lower().strip()
        
        for pattern, steps_template in self._patterns.items():
            match = re.match(pattern, task_lower)
            if match:
                groups = match.groups()
                steps = []
                for step in steps_template:
                    # Replace placeholders with matched groups
                    for i, group in enumerate(groups):
                        step = step.replace(f"{{{i}}}", group)
                    steps.append(step)
                return steps
        
        return None
    
    def _parse_with_llm(self, task: str) -> List[str]:
        """
        Parse task using LLM.
        """
        prompt = build_task_parsing_prompt(task)
        response = self.client.chat(prompt)
        
        # Parse response
        steps = []
        for line in response.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            # Remove step numbering
            match = re.match(r"(?:STEP\s*)?\d+[:.)]?\s*(.+)", line, re.IGNORECASE)
            if match:
                steps.append(match.group(1).strip())
            elif line and not line.startswith("#"):
                steps.append(line)
        
        return steps if steps else [task]
    
    def simplify_task(self, task: str) -> str:
        """
        Simplify a task description.
        
        Args:
            task: Original task description
            
        Returns:
            Simplified task
        """
        # Remove common filler words
        filler_words = [
            "please", "can you", "could you", "i want to",
            "i need to", "help me", "i would like to"
        ]
        
        task_lower = task.lower()
        for filler in filler_words:
            task_lower = task_lower.replace(filler, "")
        
        return task_lower.strip()
    
    def extract_target(self, task: str) -> Optional[str]:
        """
        Extract the main target/object from a task.
        
        Args:
            task: Task description
            
        Returns:
            Target string or None
        """
        # Common patterns for extracting targets
        patterns = [
            r"open (.+)",
            r"click (?:on )?(.+)",
            r"go to (.+)",
            r"search (?:for )?(.+)",
            r"find (.+)",
            r"type (.+)",
        ]
        
        task_lower = task.lower().strip()
        
        for pattern in patterns:
            match = re.match(pattern, task_lower)
            if match:
                return match.group(1).strip()
        
        return None


# Singleton instance
_parser = None

def get_parser() -> TaskParser:
    """Get the singleton TaskParser instance."""
    global _parser
    if _parser is None:
        _parser = TaskParser()
    return _parser
