import json
import os


class MemoryAgent:

    def __init__(self):

        self.file = "agent_memory.json"

        if not os.path.exists(self.file):
            with open(self.file, "w") as f:
                json.dump({}, f)

    def load_memory(self):

        with open(self.file, "r") as f:
            return json.load(f)

    def save_memory(self, memory):

        with open(self.file, "w") as f:
            json.dump(memory, f, indent=2)

    def get_plan(self, goal):

        memory = self.load_memory()

        return memory.get(goal)

    def store_plan(self, goal, plan):

        memory = self.load_memory()

        memory[goal] = plan

        self.save_memory(memory)