"""Configuration settings for Offline Visual AI Agent 2.0"""

import os

# =============================================================================
# PATHS
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
MODELS_DIR = os.path.join(BASE_DIR, "models")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Tesseract path
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# YOLO model path
YOLO_MODEL_PATH = os.path.join(MODELS_DIR, "yolov8n.pt")

# Memory store
MEMORY_STORE_PATH = os.path.join(MEMORY_DIR, "memory_store.json")

# =============================================================================
# SCREEN CAPTURE SETTINGS
# =============================================================================
SCREEN_CAPTURE_MONITOR = 1  # Primary monitor
SCREEN_RESIZE_WIDTH = 960   # Resize for faster processing
SCREEN_RESIZE_HEIGHT = 540
SCREEN_ORIGINAL_WIDTH = 1920
SCREEN_ORIGINAL_HEIGHT = 1080

# =============================================================================
# VISION SETTINGS
# =============================================================================
# OCR settings
OCR_CONFIDENCE_THRESHOLD = 30  # Minimum confidence for OCR text
OCR_MIN_TEXT_LENGTH = 1        # Minimum text length to keep

# YOLO settings
YOLO_CONFIDENCE_THRESHOLD = 0.25
YOLO_IOU_THRESHOLD = 0.45

# UI element filtering
UI_MIN_WIDTH = 15
UI_MIN_HEIGHT = 15
UI_MAX_ELEMENTS = 100  # Maximum elements to process

# =============================================================================
# LLM SETTINGS (OLLAMA)
# =============================================================================
OLLAMA_HOST = "http://localhost:11434"

# Models
PLANNER_MODEL = "llama3:8b"      # For planning/reasoning
VISION_MODEL = "llava:latest"    # For screenshot understanding (local)

# LLM parameters
LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS = 500
LLM_TIMEOUT = 60  # seconds

# =============================================================================
# AGENT SETTINGS
# =============================================================================
# Planner
MAX_PLAN_STEPS = 5              # Maximum steps per plan
MAX_RETRIES = 3                 # Maximum retries before giving up
MAX_TOTAL_ACTIONS = 50          # Maximum total actions per task

# Executor
EXECUTOR_CLICK_DURATION = 0.2   # Mouse move duration
EXECUTOR_TYPE_INTERVAL = 0.02   # Typing interval
EXECUTOR_ACTION_DELAY = 0.5     # Delay after action

# Critic
SCREEN_CHANGE_THRESHOLD = 500000  # Minimum pixel diff for change
SCREEN_HASH_BITS = 64             # Perceptual hash size

# =============================================================================
# DASHBOARD SETTINGS
# =============================================================================
DASHBOARD_WIDTH = 600
DASHBOARD_HEIGHT = 700
DASHBOARD_TITLE = "Offline Visual AI Agent 2.0"

# =============================================================================
# LOGGING SETTINGS
# =============================================================================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True
LOG_TO_CONSOLE = True
LOG_FILE_NAME = "agent.log"

# =============================================================================
# PERFORMANCE SETTINGS
# =============================================================================
ENABLE_VISION_CACHE = True
VISION_CACHE_TTL = 2.0          # Cache validity in seconds
ENABLE_PARALLEL_VISION = False  # Run OCR and YOLO in parallel
USE_LLAVA_FOR_COMPLEX = True    # Use LLaVA only for complex scenes
LLAVA_COMPLEXITY_THRESHOLD = 20 # Elements count to trigger LLaVA

# =============================================================================
# SAFETY SETTINGS
# =============================================================================
PYAUTOGUI_FAILSAFE = True       # Move mouse to corner to abort
PYAUTOGUI_PAUSE = 0.1           # Pause between PyAutoGUI calls

# =============================================================================
# CREATE DIRECTORIES
# =============================================================================
def ensure_directories():
    """Create required directories if they don't exist"""
    for directory in [SCREENSHOTS_DIR, MEMORY_DIR, MODELS_DIR, LOGS_DIR]:
        os.makedirs(directory, exist_ok=True)

# Auto-create directories on import
ensure_directories()
