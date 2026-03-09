"""Agent Controller for Offline Visual AI Agent 2.0"""

import time
import threading
from typing import Optional, Callable, List, Dict
from enum import Enum
import sys
sys.path.append('..')

from agents.vision_agent import VisionAgent
from agents.planner_agent import PlannerAgent
from agents.executor_agent import ExecutorAgent
from agents.critic_agent import CriticAgent
from agents.memory_agent import MemoryAgent
from vision.screenshot import get_capture
from utils.logger import get_logger

try:
    from config import MAX_RETRIES, MAX_TOTAL_ACTIONS, EXECUTOR_ACTION_DELAY
except ImportError:
    MAX_RETRIES = 3
    MAX_TOTAL_ACTIONS = 50
    EXECUTOR_ACTION_DELAY = 0.5


class AgentState(Enum):
    """Agent state enumeration"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class AgentController:
    """
    Central controller for the AI agent system.
    Coordinates vision, planning, execution, and memory.
    """
    
    def __init__(self):
        # Initialize agents
        self.vision_agent = VisionAgent()
        self.planner_agent = PlannerAgent()
        self.executor_agent = ExecutorAgent()
        self.critic_agent = CriticAgent()
        self.memory_agent = MemoryAgent()
        self.capture = get_capture()
        self.logger = get_logger()
        
        # State
        self.state = AgentState.IDLE
        self.current_task = None
        self.current_plan = []
        self.action_history = []
        self.total_actions = 0
        self.retry_count = 0
        
        # Configuration
        self.max_retries = MAX_RETRIES
        self.max_total_actions = MAX_TOTAL_ACTIONS
        self.action_delay = EXECUTOR_ACTION_DELAY
        
        # Callbacks
        self._on_state_change: Optional[Callable] = None
        self._on_action: Optional[Callable] = None
        self._on_log: Optional[Callable] = None
        
        # Threading
        self._thread: Optional[threading.Thread] = None
        self._stop_flag = False
    
    def set_callbacks(self, 
                      on_state_change: Callable = None,
                      on_action: Callable = None,
                      on_log: Callable = None):
        """
        Set callback functions for UI updates.
        
        Args:
            on_state_change: Called when agent state changes
            on_action: Called when an action is executed
            on_log: Called to log messages
        """
        self._on_state_change = on_state_change
        self._on_action = on_action
        self._on_log = on_log
    
    def _log(self, message: str):
        """Log a message"""
        self.logger.info(message)
        if self._on_log:
            self._on_log(message)
    
    def _set_state(self, state: AgentState):
        """Update agent state"""
        self.state = state
        if self._on_state_change:
            self._on_state_change(state)
    
    def start_task(self, task: str, async_mode: bool = True):
        """
        Start executing a task.
        
        Args:
            task: The task description
            async_mode: Run in background thread
        """
        if self.state == AgentState.RUNNING:
            self._log("Agent is already running")
            return
        
        self.current_task = task
        self.action_history = []
        self.total_actions = 0
        self.retry_count = 0
        self._stop_flag = False
        
        if async_mode:
            self._thread = threading.Thread(target=self._run_task_loop)
            self._thread.daemon = True
            self._thread.start()
        else:
            self._run_task_loop()
    
    def stop(self):
        """Stop the current task"""
        self._stop_flag = True
        self._set_state(AgentState.STOPPED)
        self._log("Agent stopped")
    
    def pause(self):
        """Pause the current task"""
        if self.state == AgentState.RUNNING:
            self._set_state(AgentState.PAUSED)
            self._log("Agent paused")
    
    def resume(self):
        """Resume a paused task"""
        if self.state == AgentState.PAUSED:
            self._set_state(AgentState.RUNNING)
            self._log("Agent resumed")
    
    def _run_task_loop(self):
        """
        Main task execution loop.
        """
        self._set_state(AgentState.RUNNING)
        self._log(f"Starting task: {self.current_task}")
        
        # Check memory for existing plan
        memory_plan = self.memory_agent.get_plan(self.current_task)
        if memory_plan:
            self._log("Found plan in memory")
            self.current_plan = memory_plan
        else:
            self.current_plan = []
        
        previous_screen = None
        
        while not self._stop_flag:
            # Check pause state
            while self.state == AgentState.PAUSED:
                time.sleep(0.1)
                if self._stop_flag:
                    return
            
            # Check action limit
            if self.total_actions >= self.max_total_actions:
                self._log("Maximum actions reached")
                self._set_state(AgentState.FAILED)
                return
            
            try:
                # Capture and process screen
                screen = self.capture.capture(resize=True)
                elements = self.vision_agent.observe(screen)
                
                self._log(f"Detected {len(elements)} UI elements")
                
                # Plan if needed
                if not self.current_plan:
                    self._log("Planning...")
                    
                    # Get memory suggestions
                    suggestions = self.memory_agent.get_suggestions(self.current_task)
                    
                    self.current_plan = self.planner_agent.plan(
                        elements=elements,
                        goal=self.current_task,
                        history=self.action_history,
                        memory_suggestions=suggestions
                    )
                    
                    if not self.current_plan:
                        self._log("No plan generated")
                        self.retry_count += 1
                        if self.retry_count >= self.max_retries:
                            self._set_state(AgentState.FAILED)
                            return
                        continue
                    
                    self._log(f"Plan: {self.current_plan}")
                
                # Check for completion
                if self.current_plan and self.current_plan[0].upper() == "DONE":
                    self._log("Task completed!")
                    self.memory_agent.store_plan(self.current_task, self.action_history)
                    self._set_state(AgentState.COMPLETED)
                    return
                
                # Execute next action
                if self.current_plan:
                    action = self.current_plan.pop(0)
                    self._log(f"Executing: {action}")
                    
                    if self._on_action:
                        self._on_action(action)
                    
                    success = self.executor_agent.execute(action, elements)
                    self.action_history.append(action)
                    self.total_actions += 1
                    
                    time.sleep(self.action_delay)
                    
                    # Verify action
                    new_screen = self.capture.capture(resize=True)
                    result = self.critic_agent.evaluate(screen, new_screen, action)
                    
                    self._log(f"Result: {result}")
                    
                    if result == "FAILED":
                        self.retry_count += 1
                        if self.retry_count >= self.max_retries:
                            self._log("Max retries reached, replanning...")
                            self.current_plan = []
                            self.retry_count = 0
                    else:
                        self.retry_count = 0
                    
                    previous_screen = new_screen
                
            except Exception as e:
                self._log(f"Error: {e}")
                self.retry_count += 1
                if self.retry_count >= self.max_retries:
                    self._set_state(AgentState.FAILED)
                    return
        
        self._set_state(AgentState.STOPPED)
    
    def get_status(self) -> Dict:
        """
        Get current agent status.
        
        Returns:
            Status dictionary
        """
        return {
            "state": self.state.value,
            "current_task": self.current_task,
            "total_actions": self.total_actions,
            "retry_count": self.retry_count,
            "plan_remaining": len(self.current_plan),
            "action_history": self.action_history[-5:]  # Last 5 actions
        }


# Singleton instance
_controller = None

def get_controller() -> AgentController:
    """Get the singleton AgentController instance"""
    global _controller
    if _controller is None:
        _controller = AgentController()
    return _controller
