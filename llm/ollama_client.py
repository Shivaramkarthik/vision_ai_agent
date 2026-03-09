"""Centralized Ollama LLM client for Offline Visual AI Agent 2.0"""

import ollama
import time
from typing import Optional, List, Dict, Any
import sys
sys.path.append('..')

try:
    from config import (
        OLLAMA_HOST, PLANNER_MODEL, VISION_MODEL,
        LLM_TEMPERATURE, LLM_MAX_TOKENS, LLM_TIMEOUT
    )
except ImportError:
    # Fallback defaults
    OLLAMA_HOST = "http://localhost:11434"
    PLANNER_MODEL = "llama3:8b"
    VISION_MODEL = "llava:latest"
    LLM_TEMPERATURE = 0.3
    LLM_MAX_TOKENS = 500
    LLM_TIMEOUT = 60


class OllamaClient:
    """Centralized client for Ollama LLM interactions"""
    
    def __init__(self):
        self.planner_model = PLANNER_MODEL
        self.vision_model = VISION_MODEL
        self.temperature = LLM_TEMPERATURE
        self.max_tokens = LLM_MAX_TOKENS
        self.timeout = LLM_TIMEOUT
        self._last_response_time = 0
    
    def chat(self, prompt: str, model: Optional[str] = None, 
             system_prompt: Optional[str] = None) -> str:
        """
        Send a chat message to Ollama and get response.
        
        Args:
            prompt: The user prompt
            model: Model to use (defaults to planner model)
            system_prompt: Optional system prompt
            
        Returns:
            The model's response text
        """
        model = model or self.planner_model
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        start_time = time.time()
        
        try:
            response = ollama.chat(
                model=model,
                messages=messages,
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            )
            
            self._last_response_time = time.time() - start_time
            return response["message"]["content"]
            
        except Exception as e:
            print(f"Ollama error: {e}")
            return ""
    
    def analyze_image(self, image_path: str, prompt: str) -> str:
        """
        Analyze an image using LLaVA vision model.
        
        Args:
            image_path: Path to the image file
            prompt: Question/prompt about the image
            
        Returns:
            The model's analysis
        """
        try:
            response = ollama.chat(
                model=self.vision_model,
                messages=[{
                    "role": "user",
                    "content": prompt,
                    "images": [image_path]
                }],
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            )
            
            return response["message"]["content"]
            
        except Exception as e:
            print(f"LLaVA error: {e}")
            return ""
    
    def plan(self, goal: str, ui_elements: List[Dict], 
             history: Optional[List[str]] = None,
             memory_suggestions: Optional[List[str]] = None) -> str:
        """
        Generate a plan for achieving a goal.
        
        Args:
            goal: The task goal
            ui_elements: List of detected UI elements
            history: Previous action history
            memory_suggestions: Suggestions from memory
            
        Returns:
            The planning response
        """
        from llm.prompt_templates import build_planning_prompt
        
        prompt = build_planning_prompt(
            goal=goal,
            ui_elements=ui_elements,
            history=history,
            memory_suggestions=memory_suggestions
        )
        
        return self.chat(prompt, model=self.planner_model)
    
    def get_last_response_time(self) -> float:
        """Get the time taken for the last response"""
        return self._last_response_time
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            ollama.list()
            return True
        except:
            return False


# Singleton instance
_client = None

def get_client() -> OllamaClient:
    """Get the singleton Ollama client instance"""
    global _client
    if _client is None:
        _client = OllamaClient()
    return _client
