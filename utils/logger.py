"""Logging module for Offline Visual AI Agent 2.0"""

import logging
import os
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import LOG_LEVEL, LOG_TO_FILE, LOG_TO_CONSOLE, LOG_FILE_NAME, LOGS_DIR
except ImportError:
    LOG_LEVEL = "INFO"
    LOG_TO_FILE = True
    LOG_TO_CONSOLE = True
    LOG_FILE_NAME = "agent.log"
    LOGS_DIR = "logs"


class AgentLogger:
    """
    Custom logger for the AI agent.
    """
    
    def __init__(self, name: str = "VisionAIAgent"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup logging handlers."""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        if LOG_TO_CONSOLE:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # File handler
        if LOG_TO_FILE:
            os.makedirs(LOGS_DIR, exist_ok=True)
            log_path = os.path.join(LOGS_DIR, LOG_FILE_NAME)
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)
    
    def action(self, action: str, result: str = ""):
        """Log an agent action."""
        if result:
            self.info(f"ACTION: {action} -> {result}")
        else:
            self.info(f"ACTION: {action}")
    
    def plan(self, plan: list):
        """Log a plan."""
        self.info(f"PLAN: {' | '.join(plan)}")
    
    def vision(self, element_count: int, process_time: float = 0):
        """Log vision processing."""
        if process_time:
            self.debug(f"VISION: {element_count} elements in {process_time:.2f}s")
        else:
            self.debug(f"VISION: {element_count} elements detected")


# Singleton instance
_logger = None

def get_logger() -> AgentLogger:
    """Get the singleton logger instance."""
    global _logger
    if _logger is None:
        _logger = AgentLogger()
    return _logger
