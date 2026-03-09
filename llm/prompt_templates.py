"""
Prompt Templates for Offline Visual AI Agent 2.0
Optimized for local LLMs (llama3:8b, llava)

These prompts are designed to:
1. Be concise to reduce token usage
2. Use clear structure for reliable parsing
3. Provide explicit examples for better accuracy
4. Work well with smaller local models
"""

from typing import List, Dict, Optional


# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

AGENT_SYSTEM_PROMPT = """You are an AI computer control agent. You observe screenshots and execute actions to complete tasks. You work OFFLINE using local models only. Be precise and efficient."""

PLANNER_SYSTEM_PROMPT = """You are a task planner for computer automation. Given a goal and UI elements, output exact commands. Output ONLY valid commands."""


# =============================================================================
# PLANNING PROMPTS
# =============================================================================

def build_planning_prompt(
    goal: str,
    ui_elements: List[Dict],
    history: Optional[List[str]] = None,
    memory_suggestions: Optional[List[str]] = None,
    failed_actions: Optional[List[str]] = None
) -> str:
    """Build optimized planning prompt for local LLMs."""
    
    # Build compact UI elements list
    ui_lines = []
    for i, e in enumerate(ui_elements[:30]):
        etype = e.get("type", "element")[:10]
        etext = e.get("text", "")[:40].replace('"', "'")
        if etext:
            ui_lines.append(f'{i+1}. [{etype}] "{etext}"')
        else:
            ui_lines.append(f'{i+1}. [{etype}]')
    
    ui_text = "\n".join(ui_lines) if ui_lines else "No UI elements detected"
    
    # Build history
    history_text = ""
    if history and len(history) > 0:
        recent = history[-3:]
        history_text = "\nLAST ACTIONS: " + " -> ".join(recent)
    
    # Build failed actions warning
    failed_text = ""
    if failed_actions and len(failed_actions) > 0:
        failed_text = "\nFAILED (do not repeat): " + ", ".join(failed_actions[-3:])
    
    # Build memory hints
    memory_text = ""
    if memory_suggestions and len(memory_suggestions) > 0:
        memory_text = "\nHINT: " + "; ".join(memory_suggestions[:2])
    
    prompt = f"""GOAL: {goal}

UI ELEMENTS:
{ui_text}
{history_text}{failed_text}{memory_text}

COMMANDS:
- click <n>        -> click element number n
- type "<text>"    -> type text (use quotes)
- press <key>      -> press key (enter/tab/escape/backspace)
- scroll <dir>     -> scroll up/down/left/right
- hotkey <keys>    -> key combo (ctrl+c, alt+tab)
- DONE             -> task complete

EXAMPLES:
Goal: search for cats
-> click 3
-> type "cats"
-> press enter

Goal: open calculator
-> hotkey win
-> type "calculator"
-> press enter

Goal: open notepad
-> hotkey win
-> type "notepad"
-> press enter

RULES:
1. Output 1-5 commands only
2. Use exact element numbers
3. Never repeat failed actions
4. Say DONE when complete

OUTPUT:"""
    
    return prompt


def build_simple_planning_prompt(goal: str, screen_text: str) -> str:
    """Simplified planning when UI detection fails."""
    screen_text = screen_text[:800] if screen_text else "Unable to read screen"
    
    prompt = f"""GOAL: {goal}

SCREEN TEXT:
{screen_text}

COMMANDS:
- type "<text>"
- press <key>
- hotkey <keys>
- scroll <dir>

Output 1-3 commands:"""
    
    return prompt


# =============================================================================
# CRITIC PROMPTS
# =============================================================================

def build_critic_prompt(action: str, before_description: str, after_description: str) -> str:
    """Build critic prompt for action verification."""
    prompt = f"""ACTION: {action}

BEFORE: {before_description[:200]}

AFTER: {after_description[:200]}

Did action succeed?
Answer ONLY: SUCCESS or FAILED"""
    
    return prompt


def build_quick_critic_prompt(action: str, screen_changed: bool) -> str:
    """Fast critic using screen change detection."""
    change = "YES" if screen_changed else "NO"
    
    prompt = f"""ACTION: {action}
SCREEN CHANGED: {change}

Expected change for this action?
Answer ONLY: SUCCESS or FAILED"""
    
    return prompt


# =============================================================================
# VISION PROMPTS (for LLaVA)
# =============================================================================

def build_vision_analysis_prompt(context: str = "general") -> str:
    """Build prompts for LLaVA image analysis."""
    prompts = {
        "general": """Describe this screenshot:
1. Application name
2. Main UI elements
3. Current state
Be concise.""",
        
        "ui_detection": """List clickable elements:
Format: TYPE "label" POSITION
Example: BUTTON "Submit" center
List up to 15 elements.""",
        
        "error_check": """Check for:
1. Error messages?
2. Warnings?
3. Popups?
Answer: CLEAR or describe issue.""",
        
        "task_progress": """What's on screen?
1. Application
2. Current state
3. Next action needed"""
    }
    
    return prompts.get(context, prompts["general"])


# =============================================================================
# TASK PARSING
# =============================================================================

def build_task_parsing_prompt(task_description: str) -> str:
    """Parse task into steps."""
    prompt = f"""TASK: {task_description}

Break into simple steps (one action each):

EXAMPLE:
Task: "open chrome and search weather"
1. Open Chrome
2. Click address bar
3. Type "weather"
4. Press Enter

YOUR STEPS:"""
    
    return prompt


# =============================================================================
# RECOVERY PROMPTS
# =============================================================================

def build_recovery_prompt(goal: str, failed_actions: List[str], current_screen: str) -> str:
    """Prompt for recovering from failures."""
    failed = "\n".join(f"- {a}" for a in failed_actions[-5:])
    
    prompt = f"""GOAL: {goal}

FAILED:
{failed}

SCREEN: {current_screen[:300]}

Suggest DIFFERENT approach:"""
    
    return prompt


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def parse_llm_commands(response: str) -> List[str]:
    """Parse LLM response into commands."""
    commands = []
    lines = response.strip().split("\n")
    
    valid_prefixes = ("click", "type", "press", "scroll", "hotkey", "drag", "done")
    
    for line in lines:
        line = line.strip().lower()
        # Remove prefixes
        for prefix in ["-> ", "- ", "* "]:
            if line.startswith(prefix):
                line = line[len(prefix):]
        # Remove numbering
        if len(line) > 2 and line[0].isdigit() and line[1] in ".)":
            line = line[2:].strip()
        
        if any(line.startswith(p) for p in valid_prefixes):
            commands.append(line)
        elif line == "done":
            commands.append("DONE")
    
    return commands[:5]
