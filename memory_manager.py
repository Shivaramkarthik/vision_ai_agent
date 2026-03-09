import json
import os

MEMORY_FILE = "agent_memory.json"


def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(memory):

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


def get_plan_for_goal(goal):

    memory = load_memory()

    if goal in memory:
        return memory[goal]

    return None


def store_plan(goal, plan):

    memory = load_memory()

    memory[goal] = plan

    save_memory(memory)