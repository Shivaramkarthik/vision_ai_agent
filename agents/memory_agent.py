"""Memory Agent for Offline Visual AI Agent 2.0"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import MEMORY_STORE_PATH, MEMORY_DIR
except ImportError:
    MEMORY_DIR = "memory"
    MEMORY_STORE_PATH = os.path.join(MEMORY_DIR, "memory_store.json")


class MemoryAgent:
    """
    Memory agent responsible for storing and retrieving successful strategies.
    """
    
    def __init__(self, memory_file: str = None):
        self.memory_file = memory_file or MEMORY_STORE_PATH
        self._ensure_memory_file()
        self._memory_cache = None
    
    def _ensure_memory_file(self):
        """Ensure memory directory and file exist."""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        if not os.path.exists(self.memory_file):
            self._save_memory({"tasks": {}, "strategies": [], "metadata": {}})
    
    def _load_memory(self) -> Dict:
        """Load memory from file."""
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure structure
                if "tasks" not in data:
                    data["tasks"] = {}
                if "strategies" not in data:
                    data["strategies"] = []
                if "metadata" not in data:
                    data["metadata"] = {}
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            return {"tasks": {}, "strategies": [], "metadata": {}}
    
    def _save_memory(self, memory: Dict):
        """Save memory to file."""
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
        self._memory_cache = memory
    
    def get_plan(self, goal: str) -> Optional[List[str]]:
        """
        Get a stored plan for a goal.
        
        Args:
            goal: The task goal
            
        Returns:
            List of action commands or None
        """
        memory = self._load_memory()
        
        # Exact match
        if goal in memory["tasks"]:
            task_data = memory["tasks"][goal]
            if isinstance(task_data, dict):
                return task_data.get("plan", [])
            return task_data  # Legacy format
        
        # Fuzzy match
        goal_lower = goal.lower()
        for stored_goal, task_data in memory["tasks"].items():
            if goal_lower in stored_goal.lower() or stored_goal.lower() in goal_lower:
                if isinstance(task_data, dict):
                    return task_data.get("plan", [])
                return task_data
        
        return None
    
    def store_plan(self, goal: str, plan: List[str], 
                   success: bool = True):
        """
        Store a plan for a goal.
        
        Args:
            goal: The task goal
            plan: List of action commands
            success: Whether the plan succeeded
        """
        memory = self._load_memory()
        
        memory["tasks"][goal] = {
            "plan": plan,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "execution_count": memory["tasks"].get(goal, {}).get("execution_count", 0) + 1
        }
        
        self._save_memory(memory)
    
    def get_suggestions(self, goal: str) -> List[str]:
        """
        Get suggestions for a goal based on similar past tasks.
        
        Args:
            goal: The task goal
            
        Returns:
            List of suggestion strings
        """
        memory = self._load_memory()
        suggestions = []
        
        goal_lower = goal.lower()
        goal_words = set(goal_lower.split())
        
        for stored_goal, task_data in memory["tasks"].items():
            stored_words = set(stored_goal.lower().split())
            
            # Check for word overlap
            overlap = goal_words & stored_words
            if len(overlap) >= 1:
                if isinstance(task_data, dict) and task_data.get("success"):
                    plan = task_data.get("plan", [])
                    if plan:
                        suggestions.append(f"For '{stored_goal}': {', '.join(plan[:3])}")
        
        return suggestions[:3]  # Limit suggestions
    
    def add_strategy(self, name: str, description: str, 
                     steps: List[str], tags: List[str] = None):
        """
        Add a reusable strategy.
        
        Args:
            name: Strategy name
            description: Strategy description
            steps: List of action steps
            tags: Optional tags for categorization
        """
        memory = self._load_memory()
        
        strategy = {
            "name": name,
            "description": description,
            "steps": steps,
            "tags": tags or [],
            "created": datetime.now().isoformat()
        }
        
        # Update existing or add new
        existing_idx = None
        for i, s in enumerate(memory["strategies"]):
            if s["name"] == name:
                existing_idx = i
                break
        
        if existing_idx is not None:
            memory["strategies"][existing_idx] = strategy
        else:
            memory["strategies"].append(strategy)
        
        self._save_memory(memory)
    
    def get_strategy(self, name: str) -> Optional[Dict]:
        """
        Get a strategy by name.
        
        Args:
            name: Strategy name
            
        Returns:
            Strategy dict or None
        """
        memory = self._load_memory()
        
        for strategy in memory["strategies"]:
            if strategy["name"].lower() == name.lower():
                return strategy
        
        return None
    
    def search_strategies(self, query: str) -> List[Dict]:
        """
        Search strategies by query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching strategies
        """
        memory = self._load_memory()
        query_lower = query.lower()
        
        matches = []
        for strategy in memory["strategies"]:
            if (query_lower in strategy["name"].lower() or
                query_lower in strategy["description"].lower() or
                any(query_lower in tag.lower() for tag in strategy.get("tags", []))):
                matches.append(strategy)
        
        return matches
    
    def clear_memory(self):
        """Clear all memory."""
        self._save_memory({"tasks": {}, "strategies": [], "metadata": {}})
    
    def get_stats(self) -> Dict:
        """
        Get memory statistics.
        
        Returns:
            Statistics dict
        """
        memory = self._load_memory()
        
        successful_tasks = sum(
            1 for t in memory["tasks"].values()
            if isinstance(t, dict) and t.get("success")
        )
        
        return {
            "total_tasks": len(memory["tasks"]),
            "successful_tasks": successful_tasks,
            "total_strategies": len(memory["strategies"]),
        }
