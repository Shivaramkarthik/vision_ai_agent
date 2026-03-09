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

print("Starting Multi-Agent AI System")

while True:

    screen = capture_screen()

    elements = vision_agent.observe(screen)

    draw_debug(screen, elements)

    if not plan:

        print("Planning...")

        plan = planner_agent.plan(elements, goal)

        for step in plan:
            print(step)

    for command in plan:

        print("Executing:", command)

        executor_agent.execute(command, elements)

        time.sleep(2)

        new_screen = capture_screen()

        if previous_screen is not None:

            result = critic_agent.evaluate(previous_screen, new_screen)

            print("Result:", result)

            if result == "FAILED":

                print("Replanning...")

                plan = None

                break

        previous_screen = new_screen

    else:

        print("Task complete")

        memory_agent.store_plan(goal, plan)

        break