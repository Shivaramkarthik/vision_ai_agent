"""Agent Dashboard for Offline Visual AI Agent 2.0"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import DASHBOARD_WIDTH, DASHBOARD_HEIGHT, DASHBOARD_TITLE
except ImportError:
    DASHBOARD_WIDTH = 600
    DASHBOARD_HEIGHT = 700
    DASHBOARD_TITLE = "Offline Visual AI Agent 2.0"

from agents.agent_controller import get_controller, AgentState
from task_manager.task_queue import get_queue


class AgentDashboard:
    """
    GUI Dashboard for controlling the AI agent.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(DASHBOARD_TITLE)
        self.root.geometry(f"{DASHBOARD_WIDTH}x{DASHBOARD_HEIGHT}")
        self.root.resizable(True, True)
        
        # Get controller and queue
        self.controller = get_controller()
        self.task_queue = get_queue()
        
        # Set up callbacks
        self.controller.set_callbacks(
            on_state_change=self._on_state_change,
            on_action=self._on_action,
            on_log=self._log
        )
        
        # Build UI
        self._build_ui()
        
        # Update loop
        self._update_interval = 500  # ms
        self._schedule_update()
    
    def _build_ui(self):
        """Build the dashboard UI."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text=DASHBOARD_TITLE,
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Task input section
        input_frame = ttk.LabelFrame(main_frame, text="New Task", padding="5")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.task_entry = ttk.Entry(input_frame, width=50)
        self.task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.task_entry.bind("<Return>", lambda e: self._add_task())
        
        add_btn = ttk.Button(input_frame, text="Add Task", command=self._add_task)
        add_btn.pack(side=tk.LEFT)
        
        # Task queue section
        queue_frame = ttk.LabelFrame(main_frame, text="Task Queue", padding="5")
        queue_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.task_listbox = tk.Listbox(queue_frame, height=6)
        self.task_listbox.pack(fill=tk.BOTH, expand=True)
        
        queue_btn_frame = ttk.Frame(queue_frame)
        queue_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        clear_btn = ttk.Button(queue_btn_frame, text="Clear Queue", command=self._clear_queue)
        clear_btn.pack(side=tk.LEFT)
        
        remove_btn = ttk.Button(queue_btn_frame, text="Remove Selected", command=self._remove_selected)
        remove_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="5")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Current task
        task_row = ttk.Frame(status_frame)
        task_row.pack(fill=tk.X)
        ttk.Label(task_row, text="Current Task:").pack(side=tk.LEFT)
        self.current_task_label = ttk.Label(task_row, text="None", foreground="blue")
        self.current_task_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Agent state
        state_row = ttk.Frame(status_frame)
        state_row.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(state_row, text="Agent State:").pack(side=tk.LEFT)
        self.state_label = ttk.Label(state_row, text="IDLE", foreground="gray")
        self.state_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Actions count
        actions_row = ttk.Frame(status_frame)
        actions_row.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(actions_row, text="Actions:").pack(side=tk.LEFT)
        self.actions_label = ttk.Label(actions_row, text="0")
        self.actions_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_btn = ttk.Button(
            control_frame, text="Start Agent", 
            command=self._start_agent, style="Accent.TButton"
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = ttk.Button(
            control_frame, text="Stop Agent", 
            command=self._stop_agent, state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.pause_btn = ttk.Button(
            control_frame, text="Pause", 
            command=self._toggle_pause, state=tk.DISABLED
        )
        self.pause_btn.pack(side=tk.LEFT)
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Logs", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=12, wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Clear log button
        clear_log_btn = ttk.Button(log_frame, text="Clear Logs", command=self._clear_logs)
        clear_log_btn.pack(pady=(5, 0))
    
    def _add_task(self):
        """Add a task to the queue."""
        task = self.task_entry.get().strip()
        if task:
            self.task_queue.add_task(task)
            self.task_entry.delete(0, tk.END)
            self._update_task_list()
            self._log(f"Task added: {task}")
    
    def _clear_queue(self):
        """Clear the task queue."""
        self.task_queue.clear_queue()
        self._update_task_list()
        self._log("Task queue cleared")
    
    def _remove_selected(self):
        """Remove selected task from queue."""
        selection = self.task_listbox.curselection()
        if selection:
            tasks = self.task_queue.get_pending_tasks()
            if selection[0] < len(tasks):
                task = tasks[selection[0]]
                self.task_queue.cancel_task(task.id)
                self._update_task_list()
                self._log(f"Task removed: {task.description}")
    
    def _start_agent(self):
        """Start the agent."""
        # Get next task from queue or use current task
        task = self.task_queue.get_next_task()
        if task:
            self.controller.start_task(task.description)
            self._update_buttons(running=True)
            self._log(f"Agent started with task: {task.description}")
        else:
            messagebox.showwarning("No Task", "Please add a task to the queue first.")
    
    def _stop_agent(self):
        """Stop the agent."""
        self.controller.stop()
        self._update_buttons(running=False)
        self._log("Agent stopped")
    
    def _toggle_pause(self):
        """Toggle pause state."""
        if self.controller.state == AgentState.PAUSED:
            self.controller.resume()
            self.pause_btn.config(text="Pause")
        else:
            self.controller.pause()
            self.pause_btn.config(text="Resume")
    
    def _update_buttons(self, running: bool):
        """Update button states."""
        if running:
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.NORMAL)
        else:
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.DISABLED)
            self.pause_btn.config(text="Pause")
    
    def _update_task_list(self):
        """Update the task listbox."""
        self.task_listbox.delete(0, tk.END)
        for task in self.task_queue.get_pending_tasks():
            self.task_listbox.insert(tk.END, f"[{task.id}] {task.description}")
    
    def _on_state_change(self, state: AgentState):
        """Handle state change callback."""
        self.root.after(0, self._update_state_display, state)
    
    def _update_state_display(self, state: AgentState):
        """Update state display on main thread."""
        state_colors = {
            AgentState.IDLE: "gray",
            AgentState.RUNNING: "green",
            AgentState.PAUSED: "orange",
            AgentState.COMPLETED: "blue",
            AgentState.FAILED: "red",
            AgentState.STOPPED: "gray"
        }
        
        self.state_label.config(
            text=state.value.upper(),
            foreground=state_colors.get(state, "black")
        )
        
        if state in [AgentState.COMPLETED, AgentState.FAILED, AgentState.STOPPED]:
            self._update_buttons(running=False)
            # Complete current task in queue
            current = self.task_queue.get_current_task()
            if current:
                self.task_queue.complete_task(
                    current, 
                    success=(state == AgentState.COMPLETED)
                )
    
    def _on_action(self, action: str):
        """Handle action callback."""
        self.root.after(0, self._log, f"Action: {action}")
    
    def _log(self, message: str):
        """Add message to log."""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _clear_logs(self):
        """Clear the log display."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _schedule_update(self):
        """Schedule periodic UI update."""
        self._update_ui()
        self.root.after(self._update_interval, self._schedule_update)
    
    def _update_ui(self):
        """Update UI with current status."""
        status = self.controller.get_status()
        
        # Update current task
        task = status.get("current_task", "None")
        self.current_task_label.config(text=task[:50] if task else "None")
        
        # Update actions count
        self.actions_label.config(text=str(status.get("total_actions", 0)))
        
        # Update task list
        self._update_task_list()
    
    def run(self):
        """Run the dashboard."""
        self._log("Dashboard started")
        self._log("Add tasks and click 'Start Agent' to begin")
        self.root.mainloop()


def main():
    """Main entry point for dashboard."""
    dashboard = AgentDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
