"""Main entry point for Offline Visual AI Agent 2.0"""

import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ensure_directories


def run_dashboard():
    """Run the GUI dashboard."""
    from dashboard.agent_dashboard import AgentDashboard
    dashboard = AgentDashboard()
    dashboard.run()


def run_cli(task: str):
    """Run a single task from command line."""
    from agents.agent_controller import get_controller
    
    controller = get_controller()
    
    # Set up simple logging
    def log_callback(message):
        print(f"[Agent] {message}")
    
    controller.set_callbacks(on_log=log_callback)
    
    print(f"Starting task: {task}")
    print("-" * 50)
    
    # Run synchronously
    controller.start_task(task, async_mode=False)
    
    # Print result
    status = controller.get_status()
    print("-" * 50)
    print(f"Final state: {status['state']}")
    print(f"Total actions: {status['total_actions']}")


def run_legacy():
    """Run in legacy mode (compatible with old main.py)."""
    import time
    from screenshot import capture_screen
    from visual_debug import draw_debug
    from agents.vision_agent import VisionAgent
    from agents.planner_agent import PlannerAgent
    from agents.executor_agent import ExecutorAgent
    from agents.critic_agent import CriticAgent
    from agents.memory_agent import MemoryAgent
    
    goal = "open youtube"
    
    vision_agent = VisionAgent()
    planner_agent = PlannerAgent()
    executor_agent = ExecutorAgent()
    critic_agent = CriticAgent()
    memory_agent = MemoryAgent()
    
    previous_screen = None
    plan = memory_agent.get_plan(goal)
    
    print("Starting Multi-Agent AI System (Legacy Mode)")
    print(f"Goal: {goal}")
    print("-" * 50)
    
    while True:
        screen = capture_screen()
        elements = vision_agent.observe(screen)
        
        draw_debug(screen, elements)
        
        if not plan:
            print("Planning...")
            plan = planner_agent.plan(elements, goal)
            for step in plan:
                print(f"  - {step}")
        
        for command in plan:
            print(f"Executing: {command}")
            executor_agent.execute(command, elements)
            
            time.sleep(2)
            
            new_screen = capture_screen()
            
            if previous_screen is not None:
                result = critic_agent.evaluate(previous_screen, new_screen)
                print(f"Result: {result}")
                
                if result == "FAILED":
                    print("Replanning...")
                    plan = None
                    break
            
            previous_screen = new_screen
        else:
            print("Task complete")
            memory_agent.store_plan(goal, plan)
            break


def test_vision():
    """Test the vision pipeline."""
    from vision.screenshot import capture_screen
    from vision.vision_processor import process_screen
    from utils.visual_debug import draw_debug
    
    print("Testing vision pipeline...")
    
    # Capture screen
    screen = capture_screen(resize=True)
    print(f"Captured screen: {screen.shape}")
    
    # Process screen
    elements = process_screen(screen)
    print(f"Detected {len(elements)} UI elements")
    
    # Show first 10 elements
    for i, e in enumerate(elements[:10]):
        print(f"  {i+1}. {e['type']}: \"{e['text'][:30]}\"")
    
    # Draw debug visualization
    draw_debug(screen, elements)
    
    print("\nVision test complete. Press any key to close.")
    import cv2
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def test_llm():
    """Test the LLM connection."""
    from llm.ollama_client import get_client
    
    print("Testing Ollama connection...")
    
    client = get_client()
    
    if client.is_available():
        print("Ollama is available!")
        
        # Test chat
        response = client.chat("Say 'Hello, I am working!' in exactly those words.")
        print(f"Response: {response}")
    else:
        print("ERROR: Ollama is not available. Make sure it's running.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Offline Visual AI Agent 2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run GUI dashboard
  python main.py --task "open chrome"  # Run single task
  python main.py --legacy           # Run in legacy mode
  python main.py --test-vision      # Test vision pipeline
  python main.py --test-llm         # Test LLM connection
"""
    )
    
    parser.add_argument(
        "--task", "-t",
        type=str,
        help="Run a single task from command line"
    )
    
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Run in legacy mode (old main.py behavior)"
    )
    
    parser.add_argument(
        "--test-vision",
        action="store_true",
        help="Test the vision pipeline"
    )
    
    parser.add_argument(
        "--test-llm",
        action="store_true",
        help="Test the LLM connection"
    )
    
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Run without GUI (requires --task)"
    )
    
    args = parser.parse_args()
    
    # Ensure directories exist
    ensure_directories()
    
    # Handle different modes
    if args.test_vision:
        test_vision()
    elif args.test_llm:
        test_llm()
    elif args.legacy:
        run_legacy()
    elif args.task:
        run_cli(args.task)
    else:
        run_dashboard()


if __name__ == "__main__":
    main()
