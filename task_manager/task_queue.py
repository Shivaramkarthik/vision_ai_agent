"""Task Queue Manager for Offline Visual AI Agent 2.0"""

from typing import List, Optional, Dict, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
import queue


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Task data class."""
    id: int
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error
        }


class TaskQueue:
    """
    Thread-safe task queue manager.
    """
    
    def __init__(self):
        self._queue: List[Task] = []
        self._completed: List[Task] = []
        self._current_task: Optional[Task] = None
        self._task_counter = 0
        self._lock = threading.Lock()
        self._on_task_added: Optional[Callable] = None
        self._on_task_completed: Optional[Callable] = None
    
    def set_callbacks(self, 
                      on_task_added: Callable = None,
                      on_task_completed: Callable = None):
        """
        Set callback functions.
        
        Args:
            on_task_added: Called when task is added
            on_task_completed: Called when task completes
        """
        self._on_task_added = on_task_added
        self._on_task_completed = on_task_completed
    
    def add_task(self, description: str, priority: int = 0) -> Task:
        """
        Add a task to the queue.
        
        Args:
            description: Task description
            priority: Task priority (higher = more important)
            
        Returns:
            The created Task
        """
        with self._lock:
            self._task_counter += 1
            task = Task(
                id=self._task_counter,
                description=description,
                priority=priority
            )
            self._queue.append(task)
            
            # Sort by priority (higher first)
            self._queue.sort(key=lambda t: t.priority, reverse=True)
        
        if self._on_task_added:
            self._on_task_added(task)
        
        return task
    
    def get_next_task(self) -> Optional[Task]:
        """
        Get the next task from the queue.
        
        Returns:
            Next Task or None if queue is empty
        """
        with self._lock:
            if not self._queue:
                return None
            
            task = self._queue.pop(0)
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            self._current_task = task
            
            return task
    
    def complete_task(self, task: Task, result: str = None, 
                      success: bool = True):
        """
        Mark a task as completed.
        
        Args:
            task: The task to complete
            result: Optional result message
            success: Whether task succeeded
        """
        with self._lock:
            task.completed_at = datetime.now()
            task.result = result
            
            if success:
                task.status = TaskStatus.COMPLETED
            else:
                task.status = TaskStatus.FAILED
                task.error = result
            
            self._completed.append(task)
            
            if self._current_task and self._current_task.id == task.id:
                self._current_task = None
        
        if self._on_task_completed:
            self._on_task_completed(task)
    
    def cancel_task(self, task_id: int) -> bool:
        """
        Cancel a pending task.
        
        Args:
            task_id: ID of task to cancel
            
        Returns:
            True if task was cancelled
        """
        with self._lock:
            for i, task in enumerate(self._queue):
                if task.id == task_id:
                    task.status = TaskStatus.CANCELLED
                    self._completed.append(self._queue.pop(i))
                    return True
        return False
    
    def clear_queue(self):
        """Clear all pending tasks."""
        with self._lock:
            for task in self._queue:
                task.status = TaskStatus.CANCELLED
                self._completed.append(task)
            self._queue.clear()
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks."""
        with self._lock:
            return list(self._queue)
    
    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks."""
        with self._lock:
            return list(self._completed)
    
    def get_current_task(self) -> Optional[Task]:
        """Get the currently running task."""
        return self._current_task
    
    def get_queue_size(self) -> int:
        """Get number of pending tasks."""
        return len(self._queue)
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._queue) == 0
    
    def get_stats(self) -> Dict:
        """
        Get queue statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            completed_count = len([t for t in self._completed 
                                   if t.status == TaskStatus.COMPLETED])
            failed_count = len([t for t in self._completed 
                               if t.status == TaskStatus.FAILED])
            
            return {
                "pending": len(self._queue),
                "completed": completed_count,
                "failed": failed_count,
                "total": self._task_counter
            }


# Singleton instance
_queue = None

def get_queue() -> TaskQueue:
    """Get the singleton TaskQueue instance."""
    global _queue
    if _queue is None:
        _queue = TaskQueue()
    return _queue
