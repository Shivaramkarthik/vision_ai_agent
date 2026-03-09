"""Strategy Memory for Offline Visual AI Agent 2.0"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import MEMORY_DIR
except ImportError:
    MEMORY_DIR = os.path.dirname(os.path.abspath(__file__))


class StrategyMemory:
    """
    Manages reusable strategies for common tasks.
    """
    
    def __init__(self):
        self.strategies_file = os.path.join(MEMORY_DIR, "strategies.json")
        self._ensure_file()
    
    def _ensure_file(self):
        """Ensure strategies file exists."""
        if not os.path.exists(self.strategies_file):
            self._save({"strategies": [], "categories": {}})
    
    def _load(self) -> Dict:
        """Load strategies from file."""
        try:
            with open(self.strategies_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"strategies": [], "categories": {}}
    
    def _save(self, data: Dict):
        """Save strategies to file."""
        with open(self.strategies_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_strategy(self, name: str, description: str,
                     steps: List[str], category: str = "general",
                     tags: List[str] = None) -> bool:
        """
        Add a new strategy.
        
        Args:
            name: Strategy name
            description: What the strategy does
            steps: List of action steps
            category: Strategy category
            tags: Optional tags
            
        Returns:
            True if added successfully
        """
        data = self._load()
        
        # Check for duplicate
        for s in data["strategies"]:
            if s["name"].lower() == name.lower():
                return False
        
        strategy = {
            "name": name,
            "description": description,
            "steps": steps,
            "category": category,
            "tags": tags or [],
            "created": datetime.now().isoformat(),
            "use_count": 0,
            "success_rate": 1.0
        }
        
        data["strategies"].append(strategy)
        
        # Update categories
        if category not in data["categories"]:
            data["categories"][category] = []
        data["categories"][category].append(name)
        
        self._save(data)
        return True
    
    def get_strategy(self, name: str) -> Optional[Dict]:
        """
        Get a strategy by name.
        
        Args:
            name: Strategy name
            
        Returns:
            Strategy dict or None
        """
        data = self._load()
        
        for s in data["strategies"]:
            if s["name"].lower() == name.lower():
                return s
        
        return None
    
    def find_strategies(self, query: str = None, 
                        category: str = None,
                        tags: List[str] = None) -> List[Dict]:
        """
        Find strategies matching criteria.
        
        Args:
            query: Search query
            category: Filter by category
            tags: Filter by tags
            
        Returns:
            List of matching strategies
        """
        data = self._load()
        results = []
        
        for s in data["strategies"]:
            # Category filter
            if category and s.get("category") != category:
                continue
            
            # Tags filter
            if tags:
                strategy_tags = set(s.get("tags", []))
                if not set(tags) & strategy_tags:
                    continue
            
            # Query filter
            if query:
                query_lower = query.lower()
                if (query_lower not in s["name"].lower() and
                    query_lower not in s["description"].lower()):
                    continue
            
            results.append(s)
        
        # Sort by use count and success rate
        results.sort(
            key=lambda x: (x.get("use_count", 0), x.get("success_rate", 0)),
            reverse=True
        )
        
        return results
    
    def record_use(self, name: str, success: bool = True):
        """
        Record strategy usage.
        
        Args:
            name: Strategy name
            success: Whether usage was successful
        """
        data = self._load()
        
        for s in data["strategies"]:
            if s["name"].lower() == name.lower():
                s["use_count"] = s.get("use_count", 0) + 1
                
                # Update success rate
                total = s["use_count"]
                current_rate = s.get("success_rate", 1.0)
                if success:
                    s["success_rate"] = ((current_rate * (total - 1)) + 1) / total
                else:
                    s["success_rate"] = (current_rate * (total - 1)) / total
                
                break
        
        self._save(data)
    
    def get_categories(self) -> List[str]:
        """Get all categories."""
        data = self._load()
        return list(data.get("categories", {}).keys())
    
    def delete_strategy(self, name: str) -> bool:
        """
        Delete a strategy.
        
        Args:
            name: Strategy name
            
        Returns:
            True if deleted
        """
        data = self._load()
        
        for i, s in enumerate(data["strategies"]):
            if s["name"].lower() == name.lower():
                category = s.get("category")
                data["strategies"].pop(i)
                
                # Update categories
                if category in data["categories"]:
                    if name in data["categories"][category]:
                        data["categories"][category].remove(name)
                
                self._save(data)
                return True
        
        return False


# Singleton instance
_memory = None

def get_strategy_memory() -> StrategyMemory:
    """Get the singleton StrategyMemory instance."""
    global _memory
    if _memory is None:
        _memory = StrategyMemory()
    return _memory
